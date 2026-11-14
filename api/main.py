from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api.db.database import initialize_database
from api.routes import documents, health, search
from api.services.storage import ensure_bucket

app = FastAPI(title="RAG Data Platform", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(documents.router, prefix="/documents", tags=["documents"])
app.include_router(search.router, prefix="/search", tags=["search"])
app.mount("/", StaticFiles(directory="static", html=True), name="static")


@app.on_event("startup")
def startup() -> None:
    initialize_database()
    ensure_bucket()
