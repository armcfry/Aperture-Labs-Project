"""Tests for service layer with mocked database."""
import uuid
from datetime import datetime
from unittest.mock import MagicMock, patch
import pytest

import sys
from pathlib import Path

backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from core import exceptions
from schemas.auth import LoginRequest
from schemas.users import UserCreate, UserUpdate
from schemas.projects import ProjectCreate, ProjectUpdate


class TestAuthService:
    """Tests for auth_service."""

    def test_login_success(self):
        """Test successful login returns user info."""
        from services import auth_service

        test_pw = "fake-test-pw-123"  # noqa: S105
        mock_user = MagicMock()
        mock_user.id = uuid.uuid4()
        mock_user.email = "test@example.com"
        mock_user.password_hash = test_pw

        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        payload = LoginRequest(email="test@example.com", password=test_pw)
        result = auth_service.login(mock_db, payload)

        assert result.success is True
        assert result.user.email == "test@example.com"

    def test_login_user_not_found(self):
        """Test login fails when user not found."""
        from services import auth_service

        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None

        payload = LoginRequest(email="notfound@example.com", password="fake-test-pw-123")  # noqa: S105  # NOSONAR
        result = auth_service.login(mock_db, payload)

        assert result.success is False
        assert "Invalid" in result.message

    def test_login_wrong_password(self):
        """Test login fails with wrong password."""
        from services import auth_service

        mock_user = MagicMock()
        mock_user.id = uuid.uuid4()
        mock_user.email = "test@example.com"
        mock_user.password_hash = "correct-fake-pw"  # noqa: S105  # NOSONAR

        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        payload = LoginRequest(email="test@example.com", password="wrong-fake-pw")  # noqa: S105  # NOSONAR
        result = auth_service.login(mock_db, payload)

        assert result.success is False

    def test_logout(self):
        """Test logout completes without error."""
        from services import auth_service

        mock_db = MagicMock()
        # Should not raise
        auth_service.logout(mock_db)


class TestUserService:
    """Tests for user_service."""

    @patch("services.user_service.hash_password")
    def test_create_user_success(self, mock_hash):
        """Test creating a new user."""
        from services import user_service

        mock_hash.return_value = "hashed_fake_pw"  # noqa: S105  # NOSONAR

        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None

        payload = UserCreate(email="new@example.com", password="fake-test-pw-789")  # noqa: S105  # NOSONAR
        result = user_service.create_user(mock_db, payload)

        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    def test_create_user_email_exists(self):
        """Test creating user with existing email raises ConflictError."""
        from services import user_service

        mock_existing = MagicMock()
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_existing

        payload = UserCreate(email="existing@example.com", password="fake-test-pw-789")  # noqa: S105  # NOSONAR

        with pytest.raises(exceptions.ConflictError):
            user_service.create_user(mock_db, payload)

    def test_get_user_found(self):
        """Test getting an existing user."""
        from services import user_service

        user_id = uuid.uuid4()
        mock_user = MagicMock()
        mock_user.id = user_id

        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        result = user_service.get_user(mock_db, user_id)
        assert result.id == user_id

    def test_get_user_not_found(self):
        """Test getting non-existent user raises UserNotFound."""
        from services import user_service

        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(exceptions.UserNotFound):
            user_service.get_user(mock_db, uuid.uuid4())

    def test_list_users(self):
        """Test listing all users."""
        from services import user_service

        mock_users = [MagicMock(), MagicMock()]
        mock_db = MagicMock()
        mock_db.query.return_value.order_by.return_value.all.return_value = mock_users

        result = user_service.list_users(mock_db)
        assert len(result) == 2

    def test_delete_user(self):
        """Test deleting a user."""
        from services import user_service

        mock_user = MagicMock()
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        user_service.delete_user(mock_db, uuid.uuid4())

        mock_db.delete.assert_called_once_with(mock_user)
        mock_db.commit.assert_called_once()


class TestProjectService:
    """Tests for project_service."""

    def test_create_project(self):
        """Test creating a new project."""
        from services import project_service

        mock_db = MagicMock()
        payload = ProjectCreate(name="Test Project", description="A test")

        result = project_service.create_project(mock_db, payload)

        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    def test_get_project_found(self):
        """Test getting an existing project."""
        from services import project_service

        project_id = uuid.uuid4()
        mock_project = MagicMock()
        mock_project.id = project_id

        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_project

        result = project_service.get_project(mock_db, project_id)
        assert result.id == project_id

    def test_get_project_not_found(self):
        """Test getting non-existent project raises ProjectNotFound."""
        from services import project_service

        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(exceptions.ProjectNotFound):
            project_service.get_project(mock_db, uuid.uuid4())

    def test_list_projects_excludes_archived(self):
        """Test listing projects excludes archived by default."""
        from services import project_service

        mock_projects = [MagicMock()]
        mock_db = MagicMock()
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value.order_by.return_value.all.return_value = mock_projects

        result = project_service.list_projects_for_user(mock_db, include_archived=False)

        mock_query.filter.assert_called_once()
        assert len(result) == 1

    def test_list_projects_includes_archived(self):
        """Test listing projects includes archived when requested."""
        from services import project_service

        mock_projects = [MagicMock(), MagicMock()]
        mock_db = MagicMock()
        mock_db.query.return_value.order_by.return_value.all.return_value = mock_projects

        result = project_service.list_projects_for_user(mock_db, include_archived=True)
        assert len(result) == 2

    def test_update_project(self):
        """Test updating a project."""
        from services import project_service

        mock_project = MagicMock()
        mock_project.archived_at = None
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_project

        payload = ProjectUpdate(name="Updated Name")
        project_service.update_project(mock_db, uuid.uuid4(), payload)

        assert mock_project.name == "Updated Name"
        mock_db.commit.assert_called_once()

    def test_delete_project(self):
        """Test deleting a project."""
        from services import project_service

        mock_project = MagicMock()
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_project

        project_service.delete_project(mock_db, uuid.uuid4())

        mock_db.delete.assert_called_once_with(mock_project)
        mock_db.commit.assert_called_once()

    def test_archive_project(self):
        """Test archiving a project."""
        from services import project_service

        mock_project = MagicMock()
        mock_project.archived_at = None
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_project

        project_service.archive_project(mock_db, uuid.uuid4())

        assert mock_project.archived_at is not None
        mock_db.commit.assert_called_once()

    def test_archive_project_already_archived(self):
        """Test archiving already archived project raises InvalidStateTransition."""
        from services import project_service

        mock_project = MagicMock()
        mock_project.archived_at = datetime.utcnow()
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_project

        with pytest.raises(exceptions.InvalidStateTransition):
            project_service.archive_project(mock_db, uuid.uuid4())

    def test_unarchive_project(self):
        """Test unarchiving a project."""
        from services import project_service

        mock_project = MagicMock()
        mock_project.archived_at = datetime.utcnow()
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_project

        project_service.unarchive_project(mock_db, uuid.uuid4())

        assert mock_project.archived_at is None
        mock_db.commit.assert_called_once()

    def test_unarchive_project_not_archived(self):
        """Test unarchiving non-archived project raises InvalidStateTransition."""
        from services import project_service

        mock_project = MagicMock()
        mock_project.archived_at = None
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_project

        with pytest.raises(exceptions.InvalidStateTransition):
            project_service.unarchive_project(mock_db, uuid.uuid4())
