import io
from minio import Minio

from core.config import settings

_client: Minio | None = None


def get_client() -> Minio:
    global _client
    if _client is None:
        _client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_USE_SSL,
        )
    return _client


def ensure_bucket(bucket_name: str) -> None:
    client = get_client()
    if not client.bucket_exists(bucket_name):
        client.make_bucket(bucket_name)


def upload_file(
    bucket: str,
    object_name: str,
    file_data: bytes,
    content_type: str,
) -> str:
    client = get_client()
    ensure_bucket(bucket)
    client.put_object(
        bucket,
        object_name,
        io.BytesIO(file_data),
        length=len(file_data),
        content_type=content_type,
    )
    return f"{bucket}/{object_name}"


def get_file(bucket: str, object_name: str) -> bytes:
    client = get_client()
    response = client.get_object(bucket, object_name)
    try:
        return response.read()
    finally:
        response.close()
        response.release_conn()


def delete_file(bucket: str, object_name: str) -> None:
    client = get_client()
    client.remove_object(bucket, object_name)