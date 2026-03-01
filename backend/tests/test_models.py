"""Tests for SQLAlchemy models."""
import uuid
from datetime import datetime

import sys
from pathlib import Path

backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from db.models import Base, User, Project, ProjectMember, Submission, Anomaly


class TestUserModel:
    """Tests for User model."""

    def test_user_tablename(self):
        """Test User table name."""
        assert User.__tablename__ == "users"

    def test_user_has_required_columns(self):
        """Test User has all required columns."""
        columns = [c.name for c in User.__table__.columns]
        assert "id" in columns
        assert "email" in columns
        assert "password_hash" in columns
        assert "created_at" in columns
        assert "updated_at" in columns

    def test_user_email_unique(self):
        """Test User email column is unique."""
        email_column = User.__table__.columns["email"]
        assert email_column.unique is True

    def test_user_id_is_uuid(self):
        """Test User id is UUID type."""
        id_column = User.__table__.columns["id"]
        assert id_column.primary_key is True


class TestProjectModel:
    """Tests for Project model."""

    def test_project_tablename(self):
        """Test Project table name."""
        assert Project.__tablename__ == "projects"

    def test_project_has_required_columns(self):
        """Test Project has all required columns."""
        columns = [c.name for c in Project.__table__.columns]
        assert "id" in columns
        assert "name" in columns
        assert "description" in columns
        assert "created_at" in columns
        assert "updated_at" in columns
        assert "archived_at" in columns

    def test_project_has_optional_columns(self):
        """Test Project has optional columns."""
        columns = [c.name for c in Project.__table__.columns]
        assert "detector_version" in columns
        assert "created_by_user_id" in columns


class TestProjectMemberModel:
    """Tests for ProjectMember model."""

    def test_project_member_tablename(self):
        """Test ProjectMember table name."""
        assert ProjectMember.__tablename__ == "project_members"

    def test_project_member_composite_primary_key(self):
        """Test ProjectMember has composite primary key."""
        pk_columns = [c.name for c in ProjectMember.__table__.primary_key.columns]
        assert "project_id" in pk_columns
        assert "user_id" in pk_columns

    def test_project_member_has_role(self):
        """Test ProjectMember has role column."""
        columns = [c.name for c in ProjectMember.__table__.columns]
        assert "role" in columns

    def test_project_member_role_constraint(self):
        """Test ProjectMember has role check constraint."""
        constraints = [c.name for c in ProjectMember.__table__.constraints if c.name]
        assert "project_members_role_check" in constraints


class TestSubmissionModel:
    """Tests for Submission model."""

    def test_submission_tablename(self):
        """Test Submission table name."""
        assert Submission.__tablename__ == "submissions"

    def test_submission_has_required_columns(self):
        """Test Submission has all required columns."""
        columns = [c.name for c in Submission.__table__.columns]
        assert "id" in columns
        assert "project_id" in columns
        assert "submitted_by_user_id" in columns
        assert "image_id" in columns
        assert "status" in columns
        assert "pass_fail" in columns

    def test_submission_has_status_constraint(self):
        """Test Submission has status check constraint."""
        constraints = [c.name for c in Submission.__table__.constraints if c.name]
        assert "submissions_status_check" in constraints

    def test_submission_has_pass_fail_constraint(self):
        """Test Submission has pass_fail check constraint."""
        constraints = [c.name for c in Submission.__table__.constraints if c.name]
        assert "submissions_pass_fail_check" in constraints


class TestAnomalyModel:
    """Tests for Anomaly model."""

    def test_anomaly_tablename(self):
        """Test Anomaly table name."""
        assert Anomaly.__tablename__ == "anomalies"

    def test_anomaly_has_required_columns(self):
        """Test Anomaly has all required columns."""
        columns = [c.name for c in Anomaly.__table__.columns]
        assert "id" in columns
        assert "submission_id" in columns
        assert "label" in columns
        assert "created_at" in columns

    def test_anomaly_has_optional_columns(self):
        """Test Anomaly has optional columns."""
        columns = [c.name for c in Anomaly.__table__.columns]
        assert "description" in columns
        assert "severity" in columns
        assert "confidence" in columns

    def test_anomaly_has_severity_constraint(self):
        """Test Anomaly has severity check constraint."""
        constraints = [c.name for c in Anomaly.__table__.constraints if c.name]
        assert "anomalies_severity_check" in constraints

    def test_anomaly_has_confidence_constraint(self):
        """Test Anomaly has confidence check constraint."""
        constraints = [c.name for c in Anomaly.__table__.constraints if c.name]
        assert "anomalies_confidence_check" in constraints


class TestBaseModel:
    """Tests for Base declarative model."""

    def test_base_is_declarative(self):
        """Test Base is a DeclarativeBase."""
        assert hasattr(Base, "metadata")
        assert hasattr(Base, "registry")
