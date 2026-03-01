"""Tests for enum types."""
import sys
from pathlib import Path

backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from schemas.enums import ProjectRole, SubmissionStatus, SubmissionPassFail, AnomalySeverity


class TestProjectRole:
    """Tests for ProjectRole enum."""

    def test_owner_value(self):
        assert ProjectRole.owner.value == "owner"

    def test_editor_value(self):
        assert ProjectRole.editor.value == "editor"

    def test_viewer_value(self):
        assert ProjectRole.viewer.value == "viewer"

    def test_is_string_enum(self):
        assert isinstance(ProjectRole.owner, str)
        assert ProjectRole.owner == "owner"


class TestSubmissionStatus:
    """Tests for SubmissionStatus enum."""

    def test_queued_value(self):
        assert SubmissionStatus.queued.value == "queued"

    def test_running_value(self):
        assert SubmissionStatus.running.value == "running"

    def test_complete_value(self):
        assert SubmissionStatus.complete.value == "complete"

    def test_complete_with_errors_value(self):
        assert SubmissionStatus.complete_with_errors.value == "complete_with_errors"

    def test_failed_value(self):
        assert SubmissionStatus.failed.value == "failed"


class TestSubmissionPassFail:
    """Tests for SubmissionPassFail enum."""

    def test_pass_value(self):
        assert SubmissionPassFail.pass_.value == "pass"

    def test_fail_value(self):
        assert SubmissionPassFail.fail.value == "fail"

    def test_unknown_value(self):
        assert SubmissionPassFail.unknown.value == "unknown"

    def test_db_value_for_pass(self):
        """Test db_value property returns 'pass' for pass_ enum."""
        assert SubmissionPassFail.pass_.db_value == "pass"

    def test_db_value_for_fail(self):
        """Test db_value property returns value for non-pass enums."""
        assert SubmissionPassFail.fail.db_value == "fail"

    def test_db_value_for_unknown(self):
        """Test db_value property returns value for unknown."""
        assert SubmissionPassFail.unknown.db_value == "unknown"


class TestAnomalySeverity:
    """Tests for AnomalySeverity enum."""

    def test_low_value(self):
        assert AnomalySeverity.low.value == "low"

    def test_med_value(self):
        assert AnomalySeverity.med.value == "med"

    def test_high_value(self):
        assert AnomalySeverity.high.value == "high"
