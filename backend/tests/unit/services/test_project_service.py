"""Tests for project_service."""
import uuid
import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch

from core import exceptions
from schemas.projects import ProjectCreate, ProjectUpdate
from services import project_service

pytestmark = pytest.mark.unit


class TestProjectService:

    def test_create_project(self):
        """Test creating a new project."""
        mock_db = MagicMock()
        payload = ProjectCreate(name="Test Project", description="A test")

        with patch("services.project_service.minio_client") as mock_minio:
            project_service.create_project(mock_db, payload)

        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()
        mock_minio.create_project_bucket.assert_called_once()

    def test_get_project_found(self):
        """Test getting an existing project."""
        project_id = uuid.uuid4()
        mock_project = MagicMock()
        mock_project.id = project_id

        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_project

        result = project_service.get_project(mock_db, project_id)
        assert result.id == project_id

    def test_get_project_not_found(self):
        """Test getting non-existent project raises ProjectNotFound."""
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(exceptions.ProjectNotFound):
            project_service.get_project(mock_db, uuid.uuid4())

    def test_list_projects_excludes_archived(self):
        """Test listing projects excludes archived by default."""
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
        mock_projects = [MagicMock(), MagicMock()]
        mock_db = MagicMock()
        mock_db.query.return_value.order_by.return_value.all.return_value = mock_projects

        result = project_service.list_projects_for_user(mock_db, include_archived=True)
        assert len(result) == 2

    def test_update_project(self):
        """Test updating a project."""
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
        mock_project = MagicMock()
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_project

        project_service.delete_project(mock_db, uuid.uuid4())

        mock_db.delete.assert_called_once_with(mock_project)
        mock_db.commit.assert_called_once()

    def test_archive_project(self):
        """Test archiving a project."""
        mock_project = MagicMock()
        mock_project.archived_at = None
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_project

        project_service.archive_project(mock_db, uuid.uuid4())

        assert mock_project.archived_at is not None
        mock_db.commit.assert_called_once()

    def test_archive_project_already_archived(self):
        """Test archiving already archived project raises InvalidStateTransition."""
        mock_project = MagicMock()
        mock_project.archived_at = datetime.utcnow()
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_project

        with pytest.raises(exceptions.InvalidStateTransition):
            project_service.archive_project(mock_db, uuid.uuid4())

    def test_unarchive_project(self):
        """Test unarchiving a project."""
        mock_project = MagicMock()
        mock_project.archived_at = datetime.utcnow()
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_project

        project_service.unarchive_project(mock_db, uuid.uuid4())

        assert mock_project.archived_at is None
        mock_db.commit.assert_called_once()

    def test_unarchive_project_not_archived(self):
        """Test unarchiving non-archived project raises InvalidStateTransition."""
        mock_project = MagicMock()
        mock_project.archived_at = None
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_project

        with pytest.raises(exceptions.InvalidStateTransition):
            project_service.unarchive_project(mock_db, uuid.uuid4())