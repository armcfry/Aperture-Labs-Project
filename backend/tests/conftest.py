import os
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add backend directory to path for imports
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Set test environment variables BEFORE importing the app
os.environ.setdefault("DATABASE_URL", "postgresql://test:test@localhost:5432/test_db")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-testing-only")  # noqa: S105
os.environ.setdefault("MINIO_ENDPOINT", "localhost:9000")
os.environ.setdefault("MINIO_ACCESS_KEY", "test-access-key")  # noqa: S105
os.environ.setdefault("MINIO_SECRET_KEY", "test-secret-key")  # noqa: S105
os.environ.setdefault("MINIO_BUCKET_DESIGNS", "test-designs")
os.environ.setdefault("MINIO_BUCKET_IMAGES", "test-images")
os.environ.setdefault("DETECTION_WEBHOOK_SECRET", "test-webhook-secret")  # noqa: S105

from main import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def sample_image_bytes():
    """Create a simple valid PNG image in bytes."""
    from PIL import Image
    import io

    img = Image.new("RGB", (100, 100), color="red")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer.getvalue()
