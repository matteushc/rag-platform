from fastapi import APIRouter
from pydantic import BaseModel, Field

from api.db.database import get_connection
from api.services.embeddings import embed_text
from api.services.llm import answer_question

router = APIRouter()


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    limit: int = Field(default=5, ge=1, le=20)
    generate_answer: bool = True


@router.post("")
def search_documents(payload: SearchRequest) -> dict:
    query_embedding = embed_text(payload.query)

    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT c.id, c.content, c.chunk_index, d.id AS document_id, d.filename,
                   1 - (c.embedding <=> %s::vector) AS score
            FROM chunks c
            JOIN documents d ON d.id = c.document_id
            ORDER BY c.embedding <=> %s::vector
            LIMIT %s
            """,
            (query_embedding, query_embedding, payload.limit),
        ).fetchall()

    answer = None
    if payload.generate_answer and rows:
        answer = answer_question(payload.query, [row["content"] for row in rows])

    return {"query": payload.query, "answer": answer, "results": rows}
