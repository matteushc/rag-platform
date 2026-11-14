from io import BytesIO

from pypdf import PdfReader


def extract_text(filename: str, data: bytes, content_type: str | None) -> str:
    lower_name = filename.lower()
    if content_type == "application/pdf" or lower_name.endswith(".pdf"):
        reader = PdfReader(BytesIO(data))
        return "\n".join(page.extract_text() or "" for page in reader.pages)

    return data.decode("utf-8", errors="ignore")


def chunk_text(text: str, chunk_size: int = 1200, overlap: int = 200) -> list[str]:
    normalized = " ".join(text.split())
    if not normalized:
        return []

    chunks = []
    start = 0
    while start < len(normalized):
        end = min(start + chunk_size, len(normalized))
        chunks.append(normalized[start:end])
        if end == len(normalized):
            break
        start = max(end - overlap, start + 1)

    return chunks
