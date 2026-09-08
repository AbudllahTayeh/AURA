from apps.api.core.config import settings

import psycopg


async def check_postgres() -> bool:
    settings = settings.database_url

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

from apps.api.core.config import settings

def check_postgres_health() -> bool:
    try:
        # Connects using the URL from your config and executes a simple ping
        with psycopg.connect(settings.database_url) as conn:
            conn.execute("SELECT 1")
        return True
    except Exception:
        return False