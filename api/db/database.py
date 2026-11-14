from contextlib import contextmanager
from typing import Iterator

from pgvector.psycopg import register_vector
from psycopg import Connection, connect
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from api.config import settings

pool = ConnectionPool(
    settings.database_url,
    min_size=1,
    max_size=10,
    kwargs={"row_factory": dict_row},
    open=False,
)


def initialize_database() -> None:
    pool.open(wait=True)
    with get_connection() as conn:
        conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS documents (
                id BIGSERIAL PRIMARY KEY,
                filename TEXT NOT NULL,
                object_name TEXT NOT NULL UNIQUE,
                content_type TEXT,
                size_bytes BIGINT NOT NULL DEFAULT 0,
                created_at TIMESTAMPTZ NOT NULL DEFAULT now()
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS chunks (
                id BIGSERIAL PRIMARY KEY,
                document_id BIGINT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
                chunk_index INTEGER NOT NULL,
                content TEXT NOT NULL,
                embedding VECTOR(768) NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                UNIQUE (document_id, chunk_index)
            )
            """
        )
        conn.execute("DROP INDEX IF EXISTS chunks_embedding_idx")
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS chunks_embedding_hnsw_idx
            ON chunks USING hnsw (embedding vector_cosine_ops)
            """
        )
        conn.commit()


@contextmanager
def get_connection() -> Iterator[Connection]:
    with pool.connection() as conn:
        register_vector(conn)
        yield conn
