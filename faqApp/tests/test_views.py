import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from faqApp.models import FAQ
from django.contrib.auth.models import User
from django_redis import get_redis_connection

@pytest.mark.django_db
class TestFAQViewSet:
    @pytest.fixture
    def api_client(self):
        user = User.objects.create_user(username='testuser', password='testpass')
        client = APIClient()
        client.force_authenticate(user=user)
        return client
    
    @pytest.fixture
    def faq_instance(self):
        return FAQ.objects.create(
            question="Test Question?",
            answer="Test Answer",
            translations={
                'fr': {
                    'question': 'Question de test?',
                    'answer': 'Réponse de test'
                }
            }
        )
    
    @pytest.fixture(autouse=True)
    def setup_redis(self):
        redis_client = get_redis_connection("default")
        redis_client.flushdb()  # Clear before each test
        yield redis_client
        redis_client.flushdb()  # Clear after each test

    def test_list_faqs(self, api_client, faq_instance):
        url = reverse('faq-list')
        response = api_client.get(url)
        assert response.status_code == 200
        assert len(response.data) == 1
        
    def test_list_faqs_with_language(self, api_client, faq_instance):
        url = reverse('faq-list')
        response = api_client.get(f"{url}?lang=fr")
        assert response.status_code == 200
        assert response.data[0]['question'] == 'Question de test?'

    def test_create_faq(self, api_client):
        url = reverse('faq-list')
        data = {
            'question_en': 'New Question?',
            'answer_en': 'New Answer',
            'is_active': True
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == 201

    def test_cache_working(self, api_client, faq_instance):
        url = reverse('faq-list')
        response1 = api_client.get(url)
        assert response1.status_code == 200
        
        # Delete from DB but should still get from cache
        faq_instance.delete()
        response2 = api_client.get(url)
        assert response2.status_code == 200
        assert response2.data == response1.data

    def test_available_languages(self, api_client):
        url = reverse('faq-available-languages')
        response = api_client.get(url)
        assert response.status_code == 200
        assert 'languages' in response.data
        assert len(response.data['languages']) > 0

    def test_translations_endpoint(self, api_client, faq_instance):
        url = reverse('faq-translations', kwargs={'pk': faq_instance.id})
        response = api_client.get(url)
        assert response.status_code == 200
        assert response.data['translations']['fr']['question'] == 'Question de test?'

    def test_retrieve_with_language(self, api_client, faq_instance):
        url = reverse('faq-detail', kwargs={'pk': faq_instance.id})
        response = api_client.get(f"{url}?lang=fr")
        assert response.status_code == 200
        assert response.data['question'] == 'Question de test?'

    def test_create_invalidates_cache(self, api_client):
        url = reverse('faq-list')
        data = {
            'question': 'New Question?',
            'answer': 'New Answer',
            'translations': {
                'fr': {
                    'question': 'Nouvelle Question?',
                    'answer': 'Nouvelle Réponse'
                }
            }
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == 201

        # Verify cache was invalidated
        redis_client = get_redis_connection("default")
        assert len(redis_client.keys('faq_*')) == 0 