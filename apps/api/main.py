import asyncio

from fastapi import FastAPI

from apps.api.db.postgres import check_postgres
from apps.api.db.qdrant import check_qdrant
from apps.api.db.redis import check_redis


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
    postgres_ok, redis_ok, qdrant_ok = await asyncio.gather(
        check_postgres(),
        check_redis(),
        check_qdrant(),
    )

    services = {
        "postgres": "ok" if postgres_ok else "unavailable",
        "redis": "ok" if redis_ok else "unavailable",
        "qdrant": "ok" if qdrant_ok else "unavailable",
    }

    all_services_ok = all(
        [postgres_ok, redis_ok, qdrant_ok]
    )

    return {
        "status": "ok" if all_services_ok else "degraded",
        "services": services,
    }