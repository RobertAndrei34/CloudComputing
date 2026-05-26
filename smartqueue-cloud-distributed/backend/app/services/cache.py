import json
import os
import redis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

def set_queue_snapshot(service_id: int, entries: list[dict]):
    key = f"queue:snapshot:{service_id}"
    redis_client.set(key, json.dumps(entries), ex=120)

def get_queue_snapshot(service_id: int):
    key = f"queue:snapshot:{service_id}"
    raw = redis_client.get(key)
    if not raw:
        return None
    return json.loads(raw)

def invalidate_queue_snapshot(service_id: int):
    redis_client.delete(f"queue:snapshot:{service_id}")

def redis_ping() -> bool:
    return bool(redis_client.ping())
