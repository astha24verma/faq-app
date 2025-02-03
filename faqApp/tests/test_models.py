import pytest
from faqApp.models import FAQ

@pytest.mark.django_db
class TestFAQModel:
    def test_faq_creation(self):
        faq = FAQ.objects.create(
            question="Test Question?",
            answer="Test Answer"
        )
        assert FAQ.objects.count() == 1
        assert faq.question == "Test Question?"
        assert faq.answer == "Test Answer"
        
    def test_translations(self):
        faq = FAQ.objects.create(
            question="Test Question?",
            answer="Test Answer",
            translations={
                'fr': {
                    'question': 'Question de test?',
                    'answer': 'Réponse de test'
                }
            }
        )
        assert faq.translations['fr']['question'] == 'Question de test?' 