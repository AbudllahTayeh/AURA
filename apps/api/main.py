from contextlib import asynccontextmanager

from fastapi import FastAPI
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from agents.workflow import build_master_graph
from apps.api.core.config import settings
from apps.api.db.postgres import check_postgres
from apps.api.db.qdrant import check_qdrant
from apps.api.db.redis import check_redis
from apps.api.routes.research import router as research_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Open the async Postgres connection pool for LangGraph
    async with AsyncPostgresSaver.from_conn_string(
        settings.database_url
    ) as checkpointer:
        await checkpointer.setup()
        
        # 2. Compile and attach the graph to the app state
        app.state.graph = build_master_graph(checkpointer=checkpointer)
        print("🚀 AURA Master Workflow compiled and ready!")
        
        # 3. Yield to start accepting API requests
        yield
        
    # 4. The pool automatically closes on server shutdown

app = FastAPI(
    title="AURA API",
    version="0.1.0",
    description="Autonomous Research & Decision Intelligence Platform",
    lifespan=lifespan,
)

# Register the new endpoint
app.include_router(research_router)

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