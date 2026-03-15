"""Tests for detection_service."""
import uuid
import pytest
from unittest.mock import MagicMock, patch

from services import detection_service

pytestmark = pytest.mark.unit


SUBMISSION_ID = uuid.uuid4()
PROJECT_ID = uuid.uuid4()
IMAGE_KEY = f"{PROJECT_ID}/images/test.png"


def _make_submission(status="queued", pass_fail="unknown"):
    sub = MagicMock()
    sub.id = SUBMISSION_ID
    sub.status = status
    sub.pass_fail = pass_fail
    return sub


def _make_result(pass_fail="pass", defects=None, response="RESULT: PASS"):
    result = MagicMock()
    result.pass_fail = pass_fail
    result.defects = defects or []
    result.response = response
    return result


class TestTriggerDetection:

    @patch("services.detection_service.threading.Thread")
    def test_starts_background_thread(self, mock_thread_cls):
        mock_thread = MagicMock()
        mock_thread_cls.return_value = mock_thread

        detection_service.trigger_detection(
            submission_id=SUBMISSION_ID,
            project_id=PROJECT_ID,
            image_object_key=IMAGE_KEY,
        )

        mock_thread_cls.assert_called_once_with(
            target=detection_service._run_detection,
            args=(SUBMISSION_ID, PROJECT_ID, IMAGE_KEY),
            daemon=True,
        )
        mock_thread.start.assert_called_once()


class TestRunDetection:

    def _call(self, submission=None, result=None, list_objects_return=None):
        """Helper: run _run_detection with all external dependencies mocked."""
        submission = submission or _make_submission()
        result = result or _make_result()
        list_objects_return = list_objects_return if list_objects_return is not None else []

        mock_db = MagicMock()
        mock_db.get.return_value = submission

        with (
            patch("services.detection_service.SessionLocal", return_value=mock_db),
            patch("services.detection_service.minio_client") as mock_minio,
            patch("services.detection_service._load_image_from_minio") as mock_load_img,
            patch("services.detection_service.get_model") as mock_get_model,
        ):
            mock_minio.list_objects.return_value = list_objects_return
            mock_load_img.return_value = MagicMock()
            mock_get_model.return_value.detect_fod.return_value = result

            detection_service._run_detection(SUBMISSION_ID, PROJECT_ID, IMAGE_KEY)

            return mock_db, mock_minio, mock_get_model

    def test_sets_status_running_then_complete_on_pass(self):
        submission = _make_submission()
        self._call(submission=submission, result=_make_result(pass_fail="pass"))

        assert submission.status == "complete"
        assert submission.pass_fail == "pass"
        assert submission.anomaly_count == 0

    def test_sets_pass_fail_and_anomaly_count_on_fail_with_defects(self):
        defect = MagicMock()
        defect.id = "DEF-001"
        defect.description = "bolt on runway"
        defect.severity = "critical"

        submission = _make_submission()
        result = _make_result(pass_fail="fail", defects=[defect], response="RESULT: FAIL")
        self._call(submission=submission, result=result)

        assert submission.status == "complete"
        assert submission.pass_fail == "fail"
        assert submission.anomaly_count == 1

    def test_lists_design_objects_with_correct_bucket_and_prefix(self):
        _, mock_minio, _ = self._call()

        mock_minio.list_objects.assert_called_once_with(
            bucket=str(PROJECT_ID),
            prefix="designs/",
        )

    def test_no_designs_does_not_raise(self):
        # Should complete without error even when there are no design PDFs
        self._call(list_objects_return=[])

    def test_submission_not_found_returns_early(self):
        mock_db = MagicMock()
        mock_db.get.return_value = None

        with (
            patch("services.detection_service.SessionLocal", return_value=mock_db),
            patch("services.detection_service._load_image_from_minio") as mock_load_img,
            patch("services.detection_service.get_model") as mock_get_model,
        ):
            detection_service._run_detection(SUBMISSION_ID, PROJECT_ID, IMAGE_KEY)

            mock_load_img.assert_not_called()
            mock_get_model.assert_not_called()

    def test_exception_marks_submission_failed(self):
        submission = _make_submission()
        mock_db = MagicMock()
        mock_db.get.return_value = submission

        with (
            patch("services.detection_service.SessionLocal", return_value=mock_db),
            patch("services.detection_service._load_image_from_minio", side_effect=RuntimeError("minio down")),
            patch("services.detection_service.minio_client"),
        ):
            detection_service._run_detection(SUBMISSION_ID, PROJECT_ID, IMAGE_KEY)

        assert submission.status == "failed"
        assert "minio down" in submission.error_message

    def test_db_session_always_closed(self):
        mock_db = MagicMock()
        mock_db.get.return_value = None  # early return path

        with patch("services.detection_service.SessionLocal", return_value=mock_db):
            detection_service._run_detection(SUBMISSION_ID, PROJECT_ID, IMAGE_KEY)

        mock_db.close.assert_called_once()
