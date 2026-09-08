
from fastapi import FastAPI

from apps.api.db.postgres import check_postgres_health
from apps.api.db.qdrant import check_qdrant_health
from apps.api.db.redis import check_redis_health

app = FastAPI(
    title="AURA API",
    version="0.1.0",
    description="Autonomous Research & Decision Intelligence Platform",
)


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "name": "AURA",
        "version": "0.1.0",
        "status": "running",
    }


@app.get("/health")
async def health() -> dict:
    services = {
        "postgres": "ok" if check_postgres_health() else "unavailable",
        "redis": "ok" if check_redis_health() else "unavailable",
        "qdrant": "ok" if check_qdrant_health() else "unavailable",
    }
    
    status = "ok" if all(v == "ok" for v in services.values()) else "degraded"
    
    return {
        "status": status,
        "services": services
    }