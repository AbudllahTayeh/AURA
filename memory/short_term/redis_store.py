import json
import os
import redis

class ShortTermMemoryManager:
    def __init__(self):
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.client = redis.Redis.from_url(redis_url, decode_responses=True)

    def save_session_state(self, session_id: str, state_data: dict, ttl_seconds: int = 3600):
        """Cache active research state into Redis."""
        self.client.setex(f"state:{session_id}", ttl_seconds, json.dumps(state_data))

    def get_session_state(self, session_id: str) -> dict:
        """Retrieve active state for a running research task."""
        data = self.client.get(f"state:{session_id}")
        return json.loads(data) if data else {}
