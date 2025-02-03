from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from django.core.cache import cache
from django.conf import settings
from .models import FAQ
from .serializers import FAQSerializer
import json
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from googletrans import LANGUAGES
from django_redis import get_redis_connection
import logging

# Create your views here.

logger = logging.getLogger(__name__)

class FAQViewSet(viewsets.ModelViewSet):
    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer
    redis_client = get_redis_connection("default")
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        lang = self.request.query_params.get('lang', 'en')
        queryset = FAQ.objects.all()
        
        if lang != 'en':
            for faq in queryset:
                cache_key = f'faq_{faq.id}_question_{lang}'
                cached_question = self.redis_client.get(cache_key)
                if not cached_question:
                    translated = faq.get_translation('question', lang)
                    self.redis_client.set(cache_key, translated, ex=3600)
        
        return queryset

    def get_cache_key(self, key_type, **kwargs):
        if key_type == 'list':
            return f"{settings.CACHE_KEY_PREFIX}list_{kwargs.get('lang', 'en')}"
        elif key_type == 'detail':
            return f"{settings.CACHE_KEY_PREFIX}detail_{kwargs['pk']}_{kwargs.get('lang', 'en')}"
        return None

    def invalidate_cache(self):
        keys = cache.keys(f"{settings.CACHE_KEY_PREFIX}*")
        if keys:
            cache.delete_many(keys)

    @action(detail=False, methods=['get'])
    def available_languages(self, request):
        """Return list of available languages"""
        return Response({
            'languages': [
                {'code': code, 'name': name.capitalize()} 
                for code, name in LANGUAGES.items()
            ]
        })

    @action(detail=True, methods=['get'])
    def translations(self, request, pk=None):
        """Get all translations for a specific FAQ"""
        instance = self.get_object()
        cache_key = f'faq_translations_{instance.id}'
        
        cached_data = self.redis_client.get(cache_key)
        if cached_data:
            return Response(json.loads(cached_data))

        data = {
            'id': instance.id,
            'translations': {
                'en': {
                    'question': instance.question,
                    'answer': instance.answer
                }
            }
        }
        
        # Add translations from JSONField
        if instance.translations:
            data['translations'].update(instance.translations)
        
        self.redis_client.set(cache_key, json.dumps(data), ex=3600)
        return Response(data)

    def list(self, request, *args, **kwargs):
        lang = request.query_params.get('lang', 'en')
        cache_key = self.get_cache_key('list', lang=lang)
        
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)
        
        queryset = self.get_queryset()
        serializer = self.serializer_class(
            queryset, 
            many=True,
            context={'language': lang}
        )
        data = serializer.data
        
        cache.set(cache_key, data, timeout=settings.CACHE_TTL)
        return Response(data)

    def retrieve(self, request, *args, **kwargs):
        """Get single FAQ with optional language parameter"""
        lang = request.query_params.get('lang', 'en')
        instance = self.get_object()
        cache_key = self.get_cache_key('detail', pk=instance.id, lang=lang)

        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)

        serializer = self.serializer_class(
            instance,
            context={'language': lang}
        )
        data = serializer.data
        cache.set(cache_key, data, timeout=settings.CACHE_TTL)
        return Response(data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        self.invalidate_cache()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        self.invalidate_cache()
        return response

    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        self.invalidate_cache()
        return response

    @action(detail=False, methods=['get'])
    def test_redis(self, request):
        """Test Redis connection and caching"""
        test_key = 'test_redis_connection'
        test_value = 'test_value'
        
        try:
            # Test basic connection
            self.redis_client.ping()
            
            # Test setting value
            self.redis_client.set(test_key, test_value)
            
            # Test getting value
            retrieved_value = self.redis_client.get(test_key)
            
            # Get all keys for debugging
            all_keys = self.redis_client.keys('*')
            
            return Response({
                'status': 'success',
                'connection': 'active',
                'test_value_retrieved': retrieved_value,
                'all_keys': all_keys
            })
        except Exception as e:
            return Response({
                'status': 'error',
                'error': str(e)
            }, status=500)
