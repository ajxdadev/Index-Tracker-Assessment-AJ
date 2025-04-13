import redis
import os
import json

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

def get_cache(key: str):
    value = r.get(key)
    if value:
        return json.loads(value)
    return None

def set_cache(key: str, value, ttl: int = 86400):  # 24 hours
    r.set(key, json.dumps(value), ex=ttl)