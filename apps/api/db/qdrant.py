from qdrant_client import AsyncQdrantClient
from qdrant_client import QdrantClient
from apps.api.core.config import settings


async def check_qdrant() -> bool:
    settings = settings.database_url

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



# Persistent client for the RAG agent to use later
qdrant_client = QdrantClient(
    host=settings.qdrant_host, 
    port=settings.qdrant_port
)

def check_qdrant_health() -> bool:
    try:
        qdrant_client.get_collections()
        return True
    except Exception:
        return False