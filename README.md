# RAG Data Platform

A small Docker Compose RAG stack with FastAPI, Postgres + pgvector, MinIO, Ollama, and a plain HTML client.

## Services

- FastAPI REST API: upload documents, create embeddings, search chunks, generate answers.
- Postgres + pgvector: stores documents, chunks, and vectors.
- MinIO: stores original uploaded files.
- Ollama: serves the embedding model and LLM.
- Static HTML page: browser client for upload and search.

## Run

```bash
docker compose up --build
```

The `ollama-pull` service downloads `nomic-embed-text` and `llama3.2` during startup. The first run can take a while.

Open:

- App: http://localhost:8000
- API docs: http://localhost:8000/docs
- MinIO console: http://localhost:9001
- Ollama API: http://localhost:11435

MinIO credentials are `minioadmin` / `minioadmin`.

## Calling Host Services From The API Container

Use `host.docker.internal` from Python inside Docker when calling a service running on the host machine:

```python
import httpx

response = httpx.get("http://host.docker.internal:11434/api/tags")
print(response.json())
```

On Linux, `docker-compose.yml` includes:

```yaml
extra_hosts:
  - "host.docker.internal:host-gateway"
```

If the host service is Ollama, make sure Ollama listens on more than localhost. Start it with:

```bash
OLLAMA_HOST=0.0.0.0:11434 ollama serve
```

If Ollama is managed by systemd, set `OLLAMA_HOST=0.0.0.0:11434` in the service environment and restart Ollama.

## API

Upload a document:

```bash
curl -F "file=@sample.pdf" http://localhost:8000/documents/upload
```

Search:

```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query":"What is this document about?","limit":5,"generate_answer":true}'
```

## Notes

The default embedding model is `nomic-embed-text`, which returns 768-dimensional vectors. If you change `OLLAMA_EMBED_MODEL`, update the `VECTOR(768)` size in `db/init.sql` and `api/db/database.py` if the new model has a different dimension.
