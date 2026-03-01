"""Tests for custom exceptions and exception handlers."""
import pytest
from unittest.mock import MagicMock

import sys
from pathlib import Path

backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from core.exceptions import (
    AppException,
    ProjectNotFound,
    AnomalyNotFound,
    UserNotFound,
    MemberNotFound,
    SubmissionNotFound,
    PermissionDenied,
    ConflictError,
    AlreadyMember,
    InvalidStateTransition,
)
from core.exception_handlers import (
    project_not_found_handler,
    anomaly_not_found_handler,
    user_not_found_handler,
    member_not_found_handler,
    submission_not_found_handler,
    permission_denied_handler,
    conflict_error_handler,
    invalid_state_transition_handler,
)


class TestExceptions:
    """Tests for custom exception classes."""

    def test_app_exception_default_detail(self):
        """Test AppException uses default detail."""
        exc = AppException()
        assert exc.detail == "An unexpected error occurred"

    def test_app_exception_custom_detail(self):
        """Test AppException accepts custom detail."""
        exc = AppException("Custom error message")
        assert exc.detail == "Custom error message"

    def test_project_not_found_default(self):
        """Test ProjectNotFound default message."""
        exc = ProjectNotFound()
        assert exc.detail == "Project not found"

    def test_project_not_found_custom(self):
        """Test ProjectNotFound with custom message."""
        exc = ProjectNotFound("Project 123 not found")
        assert exc.detail == "Project 123 not found"

    def test_anomaly_not_found(self):
        """Test AnomalyNotFound exception."""
        exc = AnomalyNotFound()
        assert exc.detail == "Anomaly not found"

    def test_user_not_found(self):
        """Test UserNotFound exception."""
        exc = UserNotFound()
        assert exc.detail == "User not found"

    def test_member_not_found(self):
        """Test MemberNotFound exception."""
        exc = MemberNotFound()
        assert exc.detail == "Member not found"

    def test_submission_not_found(self):
        """Test SubmissionNotFound exception."""
        exc = SubmissionNotFound()
        assert exc.detail == "Submission not found"

    def test_permission_denied(self):
        """Test PermissionDenied exception."""
        exc = PermissionDenied()
        assert exc.detail == "You do not have permission to perform this action"

    def test_conflict_error(self):
        """Test ConflictError exception."""
        exc = ConflictError()
        assert exc.detail == "A conflict occurred"

    def test_already_member(self):
        """Test AlreadyMember exception inherits from ConflictError."""
        exc = AlreadyMember()
        assert exc.detail == "User is already a member of this project"
        assert isinstance(exc, ConflictError)

    def test_invalid_state_transition(self):
        """Test InvalidStateTransition exception."""
        exc = InvalidStateTransition()
        assert exc.detail == "Invalid state transition"

    def test_exception_is_raisable(self):
        """Test exceptions can be raised and caught."""
        with pytest.raises(ProjectNotFound):
            raise ProjectNotFound()


class TestExceptionHandlers:
    """Tests for exception handlers."""

    def test_project_not_found_handler(self):
        """Test ProjectNotFound handler returns 404."""
        request = MagicMock()
        exc = ProjectNotFound()
        response = project_not_found_handler(request, exc)
        assert response.status_code == 404
        assert b"Project not found" in response.body

    def test_anomaly_not_found_handler(self):
        """Test AnomalyNotFound handler returns 404."""
        request = MagicMock()
        exc = AnomalyNotFound()
        response = anomaly_not_found_handler(request, exc)
        assert response.status_code == 404
        assert b"Anomaly not found" in response.body

    def test_user_not_found_handler(self):
        """Test UserNotFound handler returns 404."""
        request = MagicMock()
        exc = UserNotFound()
        response = user_not_found_handler(request, exc)
        assert response.status_code == 404
        assert b"User not found" in response.body

    def test_member_not_found_handler(self):
        """Test MemberNotFound handler returns 404."""
        request = MagicMock()
        exc = MemberNotFound()
        response = member_not_found_handler(request, exc)
        assert response.status_code == 404
        assert b"Member not found" in response.body

    def test_submission_not_found_handler(self):
        """Test SubmissionNotFound handler returns 404."""
        request = MagicMock()
        exc = SubmissionNotFound()
        response = submission_not_found_handler(request, exc)
        assert response.status_code == 404
        assert b"Submission not found" in response.body

    def test_permission_denied_handler(self):
        """Test PermissionDenied handler returns 403."""
        request = MagicMock()
        exc = PermissionDenied()
        response = permission_denied_handler(request, exc)
        assert response.status_code == 403
        assert b"permission" in response.body.lower()

    def test_conflict_error_handler(self):
        """Test ConflictError handler returns 409."""
        request = MagicMock()
        exc = ConflictError()
        response = conflict_error_handler(request, exc)
        assert response.status_code == 409
        assert b"conflict" in response.body.lower()

    def test_invalid_state_transition_handler(self):
        """Test InvalidStateTransition handler returns 400."""
        request = MagicMock()
        exc = InvalidStateTransition()
        response = invalid_state_transition_handler(request, exc)
        assert response.status_code == 400
        assert b"Invalid state" in response.body
