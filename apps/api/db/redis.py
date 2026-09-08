from redis.asyncio import Redis

from apps.api.core.config import settings


async def check_redis() -> bool:
    settings = settings.database_url

    client = Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        decode_responses=True,
    )

    try:
        return await client.ping()

    except Exception:
        return False

    finally:
        await client.aclose()



# Persistent client for the app to use
redis_client = Redis(
    host=settings.redis_host, 
    port=settings.redis_port, 
    decode_responses=True
)

def check_redis_health() -> bool:
    try:
        return redis_client.ping()
    except Exception:
        return False