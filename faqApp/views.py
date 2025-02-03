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

# Create your views here.

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

    def get_cache_key(self, lang):
        return f'faq_list_{lang}'

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
        """List FAQs with optional language parameter"""
        lang = request.query_params.get('lang', 'en')
        cache_key = self.get_cache_key(lang)

        cached_data = self.redis_client.get(cache_key)
        if cached_data:
            return Response(json.loads(cached_data))

        # Debug Redis connection
        try:
            test_value = self.redis_client.get('test_key')
            print(f"Redis test: {test_value}")
        except Exception as e:
            print(f"Redis error: {e}")

        queryset = self.get_queryset()
        serializer = self.serializer_class(
            queryset, 
            many=True,
            context={'language': lang}
        )
        data = serializer.data
        self.redis_client.set(cache_key, json.dumps(data), ex=3600)
        return Response(data)

    def retrieve(self, request, *args, **kwargs):
        """Get single FAQ with optional language parameter"""
        lang = request.query_params.get('lang', 'en')
        instance = self.get_object()
        cache_key = f'faq_detail_{instance.id}_{lang}'

        cached_data = self.redis_client.get(cache_key)
        if cached_data:
            return Response(json.loads(cached_data))

        serializer = self.serializer_class(
            instance,
            context={'language': lang}
        )
        data = serializer.data
        self.redis_client.set(cache_key, json.dumps(data), ex=3600)
        return Response(data)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        cache.delete_pattern(f"{settings.CACHE_KEY_PREFIX}*")
        return response

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        cache.delete_pattern(f"{settings.CACHE_KEY_PREFIX}*")
        return response

    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        cache.delete_pattern(f"{settings.CACHE_KEY_PREFIX}*")
        return response
