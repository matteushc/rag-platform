import httpx
from fastapi import HTTPException

from api.config import settings


def embed_text(text: str) -> list[float]:
    try:
        response = httpx.post(
            f"{settings.ollama_base_url}/api/embeddings",
            json={"model": settings.ollama_embed_model, "prompt": text},
            timeout=120,
        )
        response.raise_for_status()
    except httpx.HTTPError as exc:
        
        raise HTTPException(
            status_code=503,
            detail=(
                "Could not create embedding with Ollama. "
                f"Make sure the model is pulled: ollama pull {settings.ollama_embed_model}"
            ),
        ) from exc

    embedding = response.json().get("embedding")
    if not embedding:
        raise HTTPException(status_code=502, detail="Ollama returned no embedding")

    return embedding
