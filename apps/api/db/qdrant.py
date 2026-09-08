from qdrant_client import AsyncQdrantClient

from apps.api.core.config import get_settings


async def check_qdrant() -> bool:
    settings = get_settings()

    client = AsyncQdrantClient(
        host=settings.qdrant_host,
        port=settings.qdrant_port,
    )

    try:
        await client.get_collections()
        return True

    except Exception:
        return False

    finally:
        await client.close()