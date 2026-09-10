from qdrant_client import AsyncQdrantClient

from apps.api.core.config import settings

# Persistent async client for the RAG agent to use later
qdrant_client = AsyncQdrantClient(
    host=settings.qdrant_host,
    port=settings.qdrant_port,
)


async def check_qdrant() -> bool:
    try:
        await qdrant_client.get_collections()
        return True
    except Exception:
        return False
