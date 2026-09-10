from redis.asyncio import Redis

from apps.api.core.config import settings

# Persistent async client for the app to use
redis_client = Redis(
    host=settings.redis_host,
    port=settings.redis_port,
    decode_responses=True,
)


async def check_redis() -> bool:
    try:
        return await redis_client.ping()
    except Exception:
        return False
