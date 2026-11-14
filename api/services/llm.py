import httpx
from fastapi import HTTPException

from api.config import settings


def answer_question(question: str, contexts: list[str]) -> str:
    context_block = "\n\n---\n\n".join(contexts)
    prompt = (
        "Answer the question using only the context below. "
        "If the answer is not present, say you do not know.\n\n"
        f"Context:\n{context_block}\n\nQuestion: {question}"
    )

    try:
        response = httpx.post(
            f"{settings.ollama_base_url}/api/generate",
            json={
                "model": settings.ollama_chat_model,
                "prompt": prompt,
                "stream": False,
            },
            timeout=180,
        )
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=503,
            detail=(
                "Could not generate an answer with Ollama. "
                f"Make sure the model is pulled: ollama pull {settings.ollama_chat_model}"
            ),
        ) from exc

    return response.json().get("response", "").strip()
