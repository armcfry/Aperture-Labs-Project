"""
Tests for core/security.py and core/deps.py.

These tests exercise the JWT and password utilities directly, and also run
requests through the real get_current_user dependency (no bypass) to cover
the authentication middleware code paths.
"""
import uuid
from unittest.mock import MagicMock, patch

import jwt
import pytest

from core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from db.session import get_db
from fastapi.testclient import TestClient
from main import app


# -------------------------
# Fixtures
# -------------------------

def _make_db_returning(user):
    """Return a get_db override whose query chain resolves to `user`."""
    def override():
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = user
        return mock_db
    return override


@pytest.fixture
def real_auth_client():
    """Client where get_current_user runs for real; DB returns a MagicMock user."""
    fake_user = MagicMock()
    fake_user.id = uuid.uuid4()
    fake_user.email = "real@example.com"

    app.dependency_overrides[get_db] = _make_db_returning(fake_user)
    with TestClient(app) as client:
        yield client, fake_user
    app.dependency_overrides.clear()


@pytest.fixture
def real_auth_client_no_user():
    """Client where get_current_user runs for real; DB returns None (user not found)."""
    app.dependency_overrides[get_db] = _make_db_returning(None)
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


# -------------------------
# core/security.py — password hashing
# -------------------------

def test_hash_password_produces_different_hash_each_time():
    h1 = hash_password("secret")
    h2 = hash_password("secret")
    assert h1 != h2  # bcrypt uses a random salt


def test_verify_password_correct():
    plain = "correct-horse-battery-staple"
    assert verify_password(plain, hash_password(plain))


def test_verify_password_wrong():
    assert not verify_password("wrong", hash_password("right"))


# -------------------------
# core/security.py — JWT
# -------------------------

def test_create_access_token_returns_string():
    token = create_access_token(str(uuid.uuid4()))
    assert isinstance(token, str)


def test_decode_access_token_round_trip():
    user_id = str(uuid.uuid4())
    token = create_access_token(user_id)
    payload = decode_access_token(token)
    assert payload["sub"] == user_id


def test_decode_access_token_invalid_raises():
    with pytest.raises(jwt.InvalidTokenError):
        decode_access_token("not-a-valid-jwt")


def test_decode_access_token_tampered_raises():
    token = create_access_token(str(uuid.uuid4()))
    tampered = token[:-4] + "XXXX"
    with pytest.raises(jwt.InvalidTokenError):
        decode_access_token(tampered)


# -------------------------
# core/deps.py — get_current_user
# -------------------------

def test_get_current_user_valid_token(real_auth_client):
    client, fake_user = real_auth_client
    token = create_access_token(str(fake_user.id))

    with patch("routers.users.user_service.list_users", return_value=[]):
        response = client.get("/users", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200


def test_get_current_user_invalid_token(real_auth_client):
    client, _ = real_auth_client
    response = client.get("/users", headers={"Authorization": "Bearer invalid.token.here"})
    assert response.status_code == 401


def test_get_current_user_missing_token(real_auth_client):
    client, _ = real_auth_client
    response = client.get("/users")
    assert response.status_code in (401, 403)


def test_get_current_user_malformed_bearer(real_auth_client):
    client, _ = real_auth_client
    response = client.get("/users", headers={"Authorization": "NotBearer token"})
    assert response.status_code in (401, 403)


def test_get_current_user_user_not_found_in_db(real_auth_client_no_user):
    token = create_access_token(str(uuid.uuid4()))
    response = real_auth_client_no_user.get(
        "/users", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 401
