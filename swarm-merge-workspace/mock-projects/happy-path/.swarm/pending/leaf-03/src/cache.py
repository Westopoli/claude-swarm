class Cache:
    def __init__(self):
        self._store = {}

    def get(self, key):
        entry = self._store.get(key)
        if entry is None:
            return None
        return entry.get('value')

    def set(self, key, value, ttl=None):
        self._store[key] = {'value': value, 'ttl': ttl}
