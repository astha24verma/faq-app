from django.core.cache.backends.base import BaseCache

class TestCache(BaseCache):
    def __init__(self, name, params):
        super().__init__(params)
        self._cache = {}
        self._name = name

    def add(self, key, value, timeout=None, version=None):
        if key in self._cache:
            return False
        self.set(key, value, timeout, version)
        return True

    def get(self, key, default=None, version=None):
        return self._cache.get(key, default)

    def set(self, key, value, timeout=None, version=None):
        self._cache[key] = value

    def delete(self, key, version=None):
        self._cache.pop(key, None)

    def clear(self):
        self._cache.clear()

    def get_many(self, keys, version=None):
        return {k: self._cache[k] for k in keys if k in self._cache}

    def delete_many(self, keys, version=None):
        for key in keys:
            self.delete(key) 