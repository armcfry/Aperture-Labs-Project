"""Tests for storage_service."""
import uuid
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from fastapi import HTTPException

from services import storage_service

pytestmark = pytest.mark.unit


class TestStorageServiceUploadImage:

    @pytest.mark.asyncio
    @patch("services.storage_service.detection_service")
    @patch("services.storage_service.minio_client")
    async def test_upload_image_success(self, mock_minio, mock_detection):
        """Test successful image upload creates submission and triggers detection."""
        project_id = uuid.uuid4()
        user_id = uuid.uuid4()

        mock_project = MagicMock()
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_project
        mock_minio.upload_file.return_value = f"images/test.png"

        mock_file = AsyncMock()
        mock_file.filename = "test.png"
        mock_file.content_type = "image/png"
        mock_file.read = AsyncMock(return_value=b"fake image bytes")

        result = await storage_service.upload_image(
            db=mock_db,
            project_id=project_id,
            user_id=user_id,
            file=mock_file,
            allowed_types=["image/png", "image/jpeg"],
        )

        mock_minio.upload_file.assert_called_once()
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_detection.trigger_detection.assert_called_once()
        assert result.filename == "test.png"
        assert result.project_id == project_id
        assert f"{project_id}/images/test.png" == result.object_key

    @pytest.mark.asyncio
    async def test_upload_image_project_not_found(self):
        """Test upload fails when project does not exist."""
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None

        mock_file = AsyncMock()
        mock_file.filename = "test.png"
        mock_file.content_type = "image/png"

        from core import exceptions
        with pytest.raises(exceptions.ProjectNotFound):
            await storage_service.upload_image(
                db=mock_db,
                project_id=uuid.uuid4(),
                user_id=uuid.uuid4(),
                file=mock_file,
                allowed_types=["image/png"],
            )

    @pytest.mark.asyncio
    async def test_upload_image_invalid_file_type(self):
        """Test upload fails for disallowed file type."""
        mock_project = MagicMock()
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_project

        mock_file = AsyncMock()
        mock_file.filename = "test.pdf"
        mock_file.content_type = "application/pdf"

        with pytest.raises(HTTPException) as exc:
            await storage_service.upload_image(
                db=mock_db,
                project_id=uuid.uuid4(),
                user_id=uuid.uuid4(),
                file=mock_file,
                allowed_types=["image/png", "image/jpeg"],
            )
        assert exc.value.status_code == 400

    @pytest.mark.asyncio
    async def test_upload_image_no_filename(self):
        """Test upload fails when file has no filename."""
        mock_project = MagicMock()
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_project

        mock_file = AsyncMock()
        mock_file.filename = None
        mock_file.content_type = "image/png"

        with pytest.raises(HTTPException) as exc:
            await storage_service.upload_image(
                db=mock_db,
                project_id=uuid.uuid4(),
                user_id=uuid.uuid4(),
                file=mock_file,
                allowed_types=["image/png"],
            )
        assert exc.value.status_code == 400


class TestStorageServiceUploadDesign:

    @pytest.mark.asyncio
    @patch("services.storage_service.minio_client")
    async def test_upload_design_success(self, mock_minio):
        """Test successful design upload."""
        project_id = uuid.uuid4()

        mock_project = MagicMock()
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_project
        mock_minio.upload_file.return_value = "designs/spec.pdf"

        mock_file = AsyncMock()
        mock_file.filename = "spec.pdf"
        mock_file.content_type = "application/pdf"
        mock_file.read = AsyncMock(return_value=b"fake pdf bytes")

        result = await storage_service.upload_design(
            db=mock_db,
            project_id=project_id,
            file=mock_file,
            allowed_types=["application/pdf", "text/plain"],
        )

        mock_minio.upload_file.assert_called_once()
        assert result.filename == "spec.pdf"
        assert result.project_id == project_id
        assert f"{project_id}/designs/spec.pdf" == result.object_key

    @pytest.mark.asyncio
    async def test_upload_design_invalid_file_type(self):
        """Test design upload fails for disallowed file type."""
        mock_project = MagicMock()
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_project

        mock_file = AsyncMock()
        mock_file.filename = "image.png"
        mock_file.content_type = "image/png"

        with pytest.raises(HTTPException) as exc:
            await storage_service.upload_design(
                db=mock_db,
                project_id=uuid.uuid4(),
                file=mock_file,
                allowed_types=["application/pdf", "text/plain"],
            )
        assert exc.value.status_code == 400


class TestStorageServicePresignedUrls:

    @patch("services.storage_service.minio_client")
    def test_get_image_url(self, mock_minio):
        """Test get_image_url splits key and calls minio correctly."""
        project_id = uuid.uuid4()
        object_key = f"{project_id}/images/test.png"
        mock_minio.get_presigned_url.return_value = "http://minio/signed-url"

        result = storage_service.get_image_url(object_key=object_key)

        mock_minio.get_presigned_url.assert_called_once_with(
            bucket=str(project_id),
            object_name="images/test.png",
            expires_seconds=900,
            download=False,
        )
        assert result["url"] == "http://minio/signed-url"
        assert result["expires_in"] == 900

    @patch("services.storage_service.minio_client")
    def test_get_image_url_with_download_flag(self, mock_minio):
        """Test get_image_url passes download=True to minio."""
        project_id = uuid.uuid4()
        object_key = f"{project_id}/images/test.png"
        mock_minio.get_presigned_url.return_value = "http://minio/signed-url"

        storage_service.get_image_url(object_key=object_key, download=True)

        mock_minio.get_presigned_url.assert_called_once_with(
            bucket=str(project_id),
            object_name="images/test.png",
            expires_seconds=900,
            download=True,
        )

    @patch("services.storage_service.minio_client")
    def test_get_design_url(self, mock_minio):
        """Test get_design_url splits key and calls minio correctly."""
        project_id = uuid.uuid4()
        object_key = f"{project_id}/designs/spec.pdf"
        mock_minio.get_presigned_url.return_value = "http://minio/signed-url"

        result = storage_service.get_design_url(object_key=object_key)

        mock_minio.get_presigned_url.assert_called_once_with(
            bucket=str(project_id),
            object_name="designs/spec.pdf",
            expires_seconds=900,
            download=False,
        )
        assert result["url"] == "http://minio/signed-url"
        assert result["expires_in"] == 900

    @patch("services.storage_service.minio_client")
    def test_get_image_url_custom_expiry(self, mock_minio):
        """Test custom expiry is passed through correctly."""
        project_id = uuid.uuid4()
        object_key = f"{project_id}/images/test.png"
        mock_minio.get_presigned_url.return_value = "http://minio/signed-url"

        result = storage_service.get_image_url(object_key=object_key, expires=3600)

        mock_minio.get_presigned_url.assert_called_once_with(
            bucket=str(project_id),
            object_name="images/test.png",
            expires_seconds=3600,
            download=False,
        )
        assert result["expires_in"] == 3600