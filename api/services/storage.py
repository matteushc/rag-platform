from datetime import UTC, datetime
from uuid import uuid4

from minio import Minio

from api.config import settings


def client() -> Minio:
    return Minio(
        settings.minio_endpoint,
        access_key=settings.minio_access_key,
        secret_key=settings.minio_secret_key,
        secure=settings.minio_secure,
    )


def ensure_bucket() -> None:
    minio = client()
    if not minio.bucket_exists(settings.minio_bucket):
        minio.make_bucket(settings.minio_bucket)


def upload_file(filename: str, data: bytes, content_type: str | None) -> str:
    from io import BytesIO

    object_name = (
        f"{datetime.now(UTC).strftime('%Y/%m/%d')}/"
        f"{uuid4().hex}-{filename.replace('/', '_')}"
    )
    client().put_object(
        settings.minio_bucket,
        object_name,
        BytesIO(data),
        length=len(data),
        content_type=content_type or "application/octet-stream",
    )
    return object_name
