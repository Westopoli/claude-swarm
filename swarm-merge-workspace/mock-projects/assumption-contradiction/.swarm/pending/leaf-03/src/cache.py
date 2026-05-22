class Cache:
    def __init__(self):
        self._store = {}
    def get(self, key):
        return self._store.get(key)  # returns None on miss
    def set(self, key, value):
        self._store[key] = value
