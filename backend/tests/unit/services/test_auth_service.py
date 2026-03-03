"""Tests for auth_service."""
import uuid
import pytest
from unittest.mock import MagicMock

from core import exceptions
from schemas.auth import LoginRequest
from services import auth_service

pytestmark = pytest.mark.unit


class TestAuthService:

    def test_login_success(self):
        """Test successful login returns user info."""
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
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None

        payload = LoginRequest(email="notfound@example.com", password="fake-test-pw-123")  # noqa: S105
        result = auth_service.login(mock_db, payload)

        assert result.success is False
        assert "Invalid" in result.message

    def test_login_wrong_password(self):
        """Test login fails with wrong password."""
        mock_user = MagicMock()
        mock_user.id = uuid.uuid4()
        mock_user.email = "test@example.com"
        mock_user.password_hash = "correct-fake-pw"  # noqa: S105

        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        payload = LoginRequest(email="test@example.com", password="wrong-fake-pw")  # noqa: S105
        result = auth_service.login(mock_db, payload)

        assert result.success is False

    def test_logout(self):
        """Test logout completes without error."""
        mock_db = MagicMock()
        auth_service.logout(mock_db)