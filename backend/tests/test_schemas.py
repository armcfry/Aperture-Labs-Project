"""Tests for Pydantic schemas."""
import pytest
import uuid
from datetime import datetime

import sys
from pathlib import Path

backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from schemas.auth import LoginRequest, LoginResponse, UserInfo
from schemas.projects import ProjectBase, ProjectCreate, ProjectUpdate, ProjectRead, UploadResponse
from schemas.users import UserBase, UserCreate, UserUpdate, UserRead
from schemas.submissions import SubmissionBase, SubmissionCreate, SubmissionUpdate, SubmissionRead
from schemas.detection import DetectionResponse
from schemas.enums import SubmissionStatus, SubmissionPassFail


class TestAuthSchemas:
    """Tests for authentication schemas."""

    def test_login_request_valid(self):
        """Test LoginRequest with valid data."""
        test_pw = "fake-test-pw-123"  # noqa: S105
        request = LoginRequest(email="test@example.com", password=test_pw)
        assert request.email == "test@example.com"
        assert request.password == test_pw

    def test_login_request_invalid_email(self):
        """Test LoginRequest raises error with invalid email."""
        with pytest.raises(Exception):
            LoginRequest(email="invalid-email", password="fake-test-pw-123")  # noqa: S105

    def test_login_request_missing_fields(self):
        """Test LoginRequest raises error with missing fields."""
        with pytest.raises(Exception):
            LoginRequest(email="test@example.com")

    def test_user_info(self):
        """Test UserInfo schema."""
        user_id = uuid.uuid4()
        user = UserInfo(id=user_id, email="test@example.com")
        assert user.id == user_id
        assert user.email == "test@example.com"

    def test_login_response_success(self):
        """Test LoginResponse for successful login."""
        user_id = uuid.uuid4()
        user = UserInfo(id=user_id, email="test@example.com")
        response = LoginResponse(success=True, user=user, message="Login successful")
        assert response.success is True
        assert response.user.email == "test@example.com"
        assert response.message == "Login successful"

    def test_login_response_failure(self):
        """Test LoginResponse for failed login."""
        response = LoginResponse(success=False, user=None, message="Invalid credentials")
        assert response.success is False
        assert response.user is None


class TestProjectSchemas:
    """Tests for project schemas."""

    def test_project_base(self):
        """Test ProjectBase schema."""
        project = ProjectBase(name="Test Project")
        assert project.name == "Test Project"
        assert project.description is None

    def test_project_base_with_all_fields(self):
        """Test ProjectBase with all fields."""
        obj_key = uuid.uuid4()
        project = ProjectBase(
            name="Test Project",
            description="A test project",
            bucket_name="test-bucket",
            object_key=obj_key,
            detector_version="1.0.0",
        )
        assert project.name == "Test Project"
        assert project.description == "A test project"
        assert project.bucket_name == "test-bucket"
        assert project.object_key == obj_key

    def test_project_create(self):
        """Test ProjectCreate schema."""
        project = ProjectCreate(name="New Project")
        assert project.name == "New Project"

    def test_project_update(self):
        """Test ProjectUpdate schema with partial update."""
        update = ProjectUpdate(name="Updated Name")
        assert update.name == "Updated Name"
        assert update.description is None

    def test_project_read(self):
        """Test ProjectRead schema."""
        now = datetime.now()
        project_id = uuid.uuid4()
        user_id = uuid.uuid4()
        project = ProjectRead(
            id=project_id,
            name="Test Project",
            created_by_user_id=user_id,
            created_at=now,
            updated_at=now,
        )
        assert project.id == project_id
        assert project.name == "Test Project"
        assert project.archived_at is None

    def test_upload_response(self):
        """Test UploadResponse schema."""
        project_id = uuid.uuid4()
        response = UploadResponse(
            filename="test.png", project_id=project_id, object_key="projects/123/test.png"
        )
        assert response.filename == "test.png"
        assert response.project_id == project_id


class TestUserSchemas:
    """Tests for user schemas."""

    def test_user_base(self):
        """Test UserBase schema."""
        user = UserBase(email="test@example.com")
        assert user.email == "test@example.com"

    def test_user_create(self):
        """Test UserCreate schema."""
        test_pw = "fake-test-pw-456"  # noqa: S105
        user = UserCreate(email="test@example.com", password=test_pw)
        assert user.email == "test@example.com"
        assert user.password == test_pw

    def test_user_update(self):
        """Test UserUpdate schema with partial update."""
        update = UserUpdate(email="new@example.com")
        assert update.email == "new@example.com"
        assert update.password is None

    def test_user_read(self):
        """Test UserRead schema."""
        now = datetime.now()
        user_id = uuid.uuid4()
        user = UserRead(id=user_id, email="test@example.com", created_at=now, updated_at=now)
        assert user.id == user_id
        assert user.email == "test@example.com"


class TestSubmissionSchemas:
    """Tests for submission schemas."""

    def test_submission_base(self):
        """Test SubmissionBase schema."""
        project_id = uuid.uuid4()
        image_id = uuid.uuid4()
        submission = SubmissionBase(project_id=project_id, image_id=image_id)
        assert submission.project_id == project_id
        assert submission.image_id == image_id

    def test_submission_create(self):
        """Test SubmissionCreate schema."""
        project_id = uuid.uuid4()
        image_id = uuid.uuid4()
        user_id = uuid.uuid4()
        submission = SubmissionCreate(
            project_id=project_id, image_id=image_id, submitted_by_user_id=user_id
        )
        assert submission.submitted_by_user_id == user_id

    def test_submission_update(self):
        """Test SubmissionUpdate schema."""
        update = SubmissionUpdate(status=SubmissionStatus.complete, anomaly_count=3)
        assert update.status == SubmissionStatus.complete
        assert update.anomaly_count == 3

    def test_submission_read(self):
        """Test SubmissionRead schema."""
        now = datetime.now()
        submission = SubmissionRead(
            id=uuid.uuid4(),
            project_id=uuid.uuid4(),
            image_id=uuid.uuid4(),
            submitted_by_user_id=uuid.uuid4(),
            submitted_at=now,
            status=SubmissionStatus.queued,
            pass_fail=SubmissionPassFail.unknown,
            anomaly_count=None,
            error_message=None,
        )
        assert submission.status == SubmissionStatus.queued
        assert submission.pass_fail == SubmissionPassFail.unknown


class TestDetectionSchemas:
    """Tests for detection schemas."""

    def test_detection_response(self):
        """Test DetectionResponse schema."""
        response = DetectionResponse(
            response="No defects found", model="qwen2.5vl:7b", inference_time_ms=1234.56
        )
        assert response.response == "No defects found"
        assert response.model == "qwen2.5vl:7b"
        assert response.inference_time_ms == pytest.approx(1234.56)
