from typing import Any
import time

class SimpleCache:
    def __init__(self):
        self.store = {}

    def set(self, key: str, value: Any, ttl: int = 60):  # <-- ovdje
        self.store[key] = {
            "value": value,
            "expires": time.time() + ttl
        }

    def get(self, key: str) -> Any:
        data = self.store.get(key)
        if not data:
            return None
        if time.time() > data["expires"]:
            del self.store[key]
            return None
        return data["value"]
