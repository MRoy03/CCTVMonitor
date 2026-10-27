"""Object storage, behind one small interface with two backends:

- "local": plain filesystem under `settings.local_storage_dir`, served back
  to the browser via a FastAPI static mount (see cip.main). Zero signup,
  zero cost, used by default for local dev.
- "s3": any S3-compatible provider (Cloudflare R2, Supabase Storage, MinIO,
  ...) via boto3 — only the endpoint/credentials differ. Used once deployed.

Callers (ingestion pipeline, API routes) never branch on backend — they just
call put_object/get_object/get_presigned_url.
"""

from functools import lru_cache
from io import BytesIO
from pathlib import Path

import boto3

from cip.settings import get_settings


@lru_cache
def get_storage_client():
    settings = get_settings()
    return boto3.client(
        "s3",
        endpoint_url=settings.storage_endpoint_url,
        aws_access_key_id=settings.storage_access_key,
        aws_secret_access_key=settings.storage_secret_key,
        region_name=settings.storage_region,
    )


def _local_path(object_key: str) -> Path:
    settings = get_settings()
    path = Path(settings.local_storage_dir) / object_key
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def ensure_bucket() -> None:
    settings = get_settings()
    if settings.storage_backend == "local":
        Path(settings.local_storage_dir).mkdir(parents=True, exist_ok=True)
        return

    client = get_storage_client()
    existing = {b["Name"] for b in client.list_buckets().get("Buckets", [])}
    if settings.storage_bucket not in existing:
        client.create_bucket(Bucket=settings.storage_bucket)


def put_object(object_key: str, data: bytes, content_type: str = "application/octet-stream") -> str:
    settings = get_settings()
    if settings.storage_backend == "local":
        _local_path(object_key).write_bytes(data)
        return object_key

    get_storage_client().upload_fileobj(
        BytesIO(data),
        settings.storage_bucket,
        object_key,
        ExtraArgs={"ContentType": content_type},
    )
    return object_key


def get_object(object_key: str) -> bytes:
    settings = get_settings()
    if settings.storage_backend == "local":
        return _local_path(object_key).read_bytes()

    buffer = BytesIO()
    get_storage_client().download_fileobj(settings.storage_bucket, object_key, buffer)
    return buffer.getvalue()


def get_presigned_url(object_key: str, expires_in: int = 3600) -> str:
    settings = get_settings()
    if settings.storage_backend == "local":
        return f"{settings.backend_public_url}/media/{object_key}"

    return get_storage_client().generate_presigned_url(
        "get_object",
        Params={"Bucket": settings.storage_bucket, "Key": object_key},
        ExpiresIn=expires_in,
    )
