import io
from datetime import timedelta
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
    return object_name  # just the object name, not bucket/object_name


def list_objects(bucket: str, prefix: str) -> list[str]:
    """Return all object names under a given prefix in a bucket."""
    client = get_client()
    objects = client.list_objects(bucket, prefix=prefix, recursive=True)
    return [obj.object_name for obj in objects]


def get_presigned_url(
    bucket: str,
    object_name: str,
    expires_seconds: int = 900,
) -> str:
    client = get_client()
    return client.presigned_get_object(
        bucket,
        object_name,
        expires=timedelta(seconds=expires_seconds),
    )


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


def create_project_bucket(project_id: str) -> None:
    """Create a bucket for a project."""
    ensure_bucket(project_id)


def delete_project_bucket(project_id: str) -> None:
    """Delete a project's bucket and all its contents."""
    client = get_client()
    bucket = project_id
    if not client.bucket_exists(bucket):
        return
    # Remove all objects first
    objects = client.list_objects(bucket, recursive=True)
    for obj in objects:
        client.remove_object(bucket, obj.object_name)
    # Then remove the bucket
    client.remove_bucket(bucket)