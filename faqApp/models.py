from django.db import models
from django_ckeditor_5.fields import CKEditor5Field
from googletrans import Translator, LANGUAGES
from django_redis import get_redis_connection
from django.utils.html import strip_tags
import json

class FAQ(models.Model):
    question = models.TextField(
        help_text="Enter the question in your primary language (English)"
    )
    answer = CKEditor5Field(
        help_text="Enter the answer in your primary language (English)",
        config_name='extends'
    )
    translations = models.JSONField(
        default=dict,
        blank=True,
        help_text="Translations are automatically generated and stored here"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @staticmethod
    def get_supported_languages():
        return LANGUAGES  # Returns dict of language codes and names from googletrans

    def translate_content(self, text, dest_lang):
        if dest_lang not in LANGUAGES:
            return None
        try:
            translator = Translator()
            translation = translator.translate(text, dest=dest_lang)
            return translation.text
        except Exception as e:
            print(f"Translation error: {e}")
            return None

    def get_translation(self, field, lang='en'):
        if lang == 'en':
            return getattr(self, field)
        
        redis_client = get_redis_connection("default")
        cache_key = f'faq_{self.id}_{field}_{lang}'
        
        # Try Redis first
        cached = redis_client.get(cache_key)
        if cached:
            return cached.decode('utf-8')
        
        # If not in Redis, translate and cache
        translations = self.translations or {}
        lang_translations = translations.get(lang, {})
        
        if not lang_translations.get(field):
            try:
                original = getattr(self, field)
                translated = self.translate_content(original, lang)
                if translated:
                    # Cache in Redis
                    redis_client.set(cache_key, translated, ex=3600)
                    
                    # Update translations field
                    if lang not in translations:
                        translations[lang] = {}
                    translations[lang][field] = translated
                    self.translations = translations
                    self.save(update_fields=['translations'])
                    return translated
            except Exception as e:
                print(f"Translation error: {e}")
        
        return lang_translations.get(field, getattr(self, field))

    def get_question(self, lang='en'):
        return self.get_translation('question', lang)

    def get_answer(self, lang='en'):
        return self.get_translation('answer', lang)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
