import io
from minio import Minio
from minio.error import S3Error

MINIO_ENDPOINT = "localhost:9000"
MINIO_ACCESS_KEY = "minioadmin"
MINIO_SECRET_KEY = "minioadmin"
MINIO_SECURE = False

BUCKET_DESIGNS = "fod-designs"
BUCKET_IMAGES = "fod-images"

_client: Minio | None = None


def get_client() -> Minio:
    global _client
    if _client is None:
        _client = Minio(
            MINIO_ENDPOINT,
            access_key=MINIO_ACCESS_KEY,
            secret_key=MINIO_SECRET_KEY,
            secure=MINIO_SECURE,
        )
    return _client


def ensure_bucket(bucket_name: str) -> None:
    client = get_client()
    if not client.bucket_exists(bucket_name):
        client.make_bucket(bucket_name)


def upload_file(
    bucket: str, object_name: str, file_data: bytes, content_type: str
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
