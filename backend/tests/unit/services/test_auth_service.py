"""Tests for auth_service."""
import uuid
import pytest
from unittest.mock import MagicMock, patch

from core import exceptions
from schemas.auth import LoginRequest
from services import auth_service

pytestmark = pytest.mark.unit


class TestAuthService:

    def test_login_success(self):
        """Test successful login returns access token and user info."""
        mock_user = MagicMock()
        mock_user.id = uuid.uuid4()
        mock_user.email = "test@example.com"
        mock_user.password_hash = "hashed-pw"  # noqa: S2068

        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        payload = LoginRequest(email="test@example.com", password="fake-test-pw-123")  # noqa: S105, S2068

        with patch("services.auth_service.security.verify_password", return_value=True), \
             patch("services.auth_service.security.create_access_token", return_value="test-token"):
            result = auth_service.login(mock_db, payload)

        assert result.access_token == "test-token"
        assert result.token_type == "bearer"
        assert result.user.email == "test@example.com"

    def test_login_user_not_found(self):
        """Test login raises Unauthorized when user not found."""
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None

        payload = LoginRequest(email="notfound@example.com", password="fake-test-pw-123")  # noqa: S105

        with pytest.raises(exceptions.Unauthorized):
            auth_service.login(mock_db, payload)

    def test_login_wrong_password(self):
        """Test login raises Unauthorized with wrong password."""
        mock_user = MagicMock()
        mock_user.id = uuid.uuid4()
        mock_user.email = "test@example.com"
        mock_user.password_hash = "hashed-correct-pw"  # noqa: S2068

        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        payload = LoginRequest(email="test@example.com", password="wrong-fake-pw")  # noqa: S105

        with patch("services.auth_service.security.verify_password", return_value=False), \
             pytest.raises(exceptions.Unauthorized):
            auth_service.login(mock_db, payload)

    def test_logout(self):
        """Test logout completes without error."""
        auth_service.logout()
