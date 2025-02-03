from rest_framework import serializers
from .models import FAQ
from googletrans import LANGUAGES

class FAQSerializer(serializers.ModelSerializer):
    question = serializers.SerializerMethodField(read_only=True)
    answer = serializers.SerializerMethodField(read_only=True)
    translated_language = serializers.SerializerMethodField(read_only=True)
    question_en = serializers.CharField(write_only=True, source='question')
    answer_en = serializers.CharField(write_only=True, source='answer')

    class Meta:
        model = FAQ
        fields = ['id', 'question', 'answer', 'created_at', 'updated_at', 
                 'translated_language', 'question_en', 'answer_en', 'is_active']
        read_only_fields = ['created_at', 'updated_at', 'translated_language']

    def get_question(self, obj):
        lang = self.context.get('language', 'en')
        return obj.get_question(lang)

    def get_answer(self, obj):
        lang = self.context.get('language', 'en')
        return obj.get_answer(lang)
    
    def get_translated_language(self, obj):
        lang = self.context.get('language', 'en')
        return {
            'code': lang,
            'name': LANGUAGES.get(lang, lang.upper()).capitalize()
        }

    def create(self, validated_data):
        # Create FAQ without translations first
        instance = super().create(validated_data)
        return instance 