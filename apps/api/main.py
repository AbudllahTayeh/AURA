from fastapi import FastAPI

from apps.api.db.postgres import check_postgres
from apps.api.db.qdrant import check_qdrant
from apps.api.db.redis import check_redis

app = FastAPI(
    title="AURA API",
    version="0.1.0",
    description="Autonomous Research & Decision Intelligence Platform",
)

@app.get("/health")
async def health() -> dict:
    services = {
        "postgres": "ok" if await check_postgres() else "unavailable",
        "redis": "ok" if await check_redis() else "unavailable",
        "qdrant": "ok" if await check_qdrant() else "unavailable",
    }
    
    status = "ok" if all(v == "ok" for v in services.values()) else "degraded"
    
    return {
        "status": status,
        "services": services
    }