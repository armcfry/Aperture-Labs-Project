"""Tests for detection_service."""
import uuid
import pytest
from unittest.mock import MagicMock, patch

from services import detection_service

pytestmark = pytest.mark.unit


class TestTriggerDetection:

    @patch("services.detection_service.minio_client")
    def test_trigger_detection_lists_designs(self, mock_minio):
        mock_minio.list_objects.return_value = ["designs/spec.pdf"]
        mock_db = MagicMock()
        project_id = uuid.uuid4()
        submission_id = uuid.uuid4()

        detection_service.trigger_detection(
            db=mock_db,
            submission_id=submission_id,
            project_id=project_id,
            image_object_key=f"{project_id}/images/test.png",
        )

        mock_minio.list_objects.assert_called_once_with(
            bucket=str(project_id),
            prefix="designs/",
        )

    @patch("services.detection_service.minio_client")
    def test_trigger_detection_no_designs(self, mock_minio):
        mock_minio.list_objects.return_value = []
        mock_db = MagicMock()
        project_id = uuid.uuid4()

        # Should not raise even with no design docs
        detection_service.trigger_detection(
            db=mock_db,
            submission_id=uuid.uuid4(),
            project_id=project_id,
            image_object_key=f"{project_id}/images/test.png",
        )

        mock_minio.list_objects.assert_called_once()
