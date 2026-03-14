import os
import pytest

# Set env vars before any app imports so pydantic-settings
# can load them when config.py is first imported
os.environ.setdefault("DATABASE_URL", "postgresql://user:pass@localhost:5433/appdb_test")
os.environ.setdefault("MINIO_ENDPOINT", "localhost:9000")
os.environ.setdefault("MINIO_ACCESS_KEY", "minioadmin")
os.environ.setdefault("MINIO_SECRET_KEY", "minioadmin")
os.environ.setdefault("MINIO_USE_SSL", "false")
os.environ.setdefault("MINIO_BUCKET_DESIGNS", "designs")
os.environ.setdefault("MINIO_BUCKET_IMAGES", "images")
os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "60")

from fastapi.testclient import TestClient

from main import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)
