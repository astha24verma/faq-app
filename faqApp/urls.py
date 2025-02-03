from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FAQViewSet
from django.conf import settings
from django.conf.urls.static import static

router = DefaultRouter()
router.register(r'faqs', FAQViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
