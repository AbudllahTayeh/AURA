import os

from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

# Fallback to local Docker credentials if environment variable is missing
DB_URI = os.getenv("DATABASE_URL", "postgresql://aura:pass@localhost:5432/aura")

# Connection pool for efficient database connections in FastAPI
pool = ConnectionPool(DB_URI)


def init_postgres():
    """Initializes the database tables."""
    with pool.connection() as conn:
        with conn.cursor() as cur:
            # Create documents table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id SERIAL PRIMARY KEY,
                    filename TEXT NOT NULL,
                    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            # Create chunks table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS chunks (
                    qdrant_id INTEGER PRIMARY KEY,
                    document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
                    chunk_index INTEGER NOT NULL,
                    text TEXT NOT NULL
                );
            """)
        conn.commit()
        print("Postgres tables initialized.")


def get_next_qdrant_id() -> int:
    """Calculates the next available ID for Qdrant and Postgres."""
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COALESCE(MAX(qdrant_id) + 1, 0) FROM chunks;")
            return cur.fetchone()[0]


def insert_document(filename: str) -> int:
    """Inserts a new document and returns its Postgres ID."""
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO documents (filename) VALUES (%s) RETURNING id;",
                (filename,),
            )
            doc_id = cur.fetchone()[0]
        conn.commit()
        return doc_id


def insert_chunks(document_id: int, start_qdrant_id: int, chunks: list[str]):
    """Inserts chunks mapped to their corresponding Qdrant IDs."""
    with pool.connection() as conn:
        with conn.cursor() as cur:
            for i, text in enumerate(chunks):
                cur.execute(
                    """
                    INSERT INTO chunks (qdrant_id, document_id, chunk_index, text)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (start_qdrant_id + i, document_id, i, text),
                )
        conn.commit()


def get_all_chunks() -> list[str]:
    """Retrieves all chunks ordered by ID to rebuild the BM25 corpus."""
    with pool.connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("SELECT text FROM chunks ORDER BY qdrant_id ASC;")
            rows = cur.fetchall()
            return [row["text"] for row in rows]
