import psycopg

from apps.api.core.config import settings


async def check_postgres() -> bool:
    try:
        async with await psycopg.AsyncConnection.connect(
            host=settings.postgres_host,
            port=settings.postgres_port,
            dbname=settings.postgres_db,
            user=settings.postgres_user,
            password=settings.postgres_password,
        ) as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT 1")
                result = await cur.fetchone()
                return result == (1,)
    except Exception:
        return False