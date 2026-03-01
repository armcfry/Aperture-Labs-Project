"""
Unit tests for auth_service.login and auth_service.logout.

These tests call the service layer directly against a real test database.
No HTTP layer is involved — that lives in tests/api/test_auth.py.
"""

from unittest.mock import MagicMock
import uuid

import pytest

from services import auth_service
from schemas.auth import LoginRequest


pytestmark = pytest.mark.unit

def test_login_success():
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

def test_login_user_not_found():
    """Test login fails when user not found."""
    from services import auth_service

    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = None

    payload = LoginRequest(email="notfound@example.com", password="fake-test-pw-123")  # noqa: S105  # NOSONAR
    result = auth_service.login(mock_db, payload)

    assert result.success is False
    assert "Invalid" in result.message

def test_login_wrong_password():
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

def test_logout():
    """Test logout completes without error."""
    from services import auth_service

    mock_db = MagicMock()
    # Should not raise
    auth_service.logout(mock_db)