from fastapi import APIRouter, File, HTTPException, UploadFile

from api.db.database import get_connection
from api.services.embeddings import embed_text
from api.services.storage import upload_file
from api.services.text import chunk_text, extract_text

router = APIRouter()


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)) -> dict:
    raw = await file.read()
    if not raw:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    text = extract_text(file.filename or "document", raw, file.content_type)
    chunks = chunk_text(text)
    if not chunks:
        raise HTTPException(status_code=400, detail="No readable text found in file")

    object_name = upload_file(file.filename or "document", raw, file.content_type)

    with get_connection() as conn:
        document = conn.execute(
            """
            INSERT INTO documents (filename, object_name, content_type, size_bytes)
            VALUES (%s, %s, %s, %s)
            RETURNING id, filename, object_name, content_type, size_bytes, created_at
            """,
            (file.filename, object_name, file.content_type, len(raw)),
        ).fetchone()

        for index, chunk in enumerate(chunks):
            embedding = embed_text(chunk)
            conn.execute(
                """
                INSERT INTO chunks (document_id, chunk_index, content, embedding)
                VALUES (%s, %s, %s, %s)
                """,
                (document["id"], index, chunk, embedding),
            )

        conn.commit()

    return {"document": document, "chunks_indexed": len(chunks)}


@router.get("")
def list_documents() -> dict[str, list[dict]]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT d.id, d.filename, d.object_name, d.content_type, d.size_bytes,
                   d.created_at, COUNT(c.id) AS chunk_count
            FROM documents d
            LEFT JOIN chunks c ON c.document_id = d.id
            GROUP BY d.id
            ORDER BY d.created_at DESC
            """
        ).fetchall()

    return {"documents": rows}
