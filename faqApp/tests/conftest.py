import pytest
from django.conf import settings
from django_redis import get_redis_connection

@pytest.fixture(autouse=True)
def use_redis_for_testing(settings):
    settings.CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": "redis://localhost:6379/1",
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            }
        }
    }
    settings.CACHE_KEY_PREFIX = "test_"
    
    # Clear Redis before each test
    redis_client = get_redis_connection("default")
    redis_client.flushdb() 