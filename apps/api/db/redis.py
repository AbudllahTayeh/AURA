from redis.asyncio import Redis

from apps.api.core.config import get_settings


async def check_redis() -> bool:
    settings = get_settings()

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