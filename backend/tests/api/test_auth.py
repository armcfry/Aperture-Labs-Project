import uuid
from unittest.mock import patch

from core.exceptions import Unauthorized
from schemas.auth import LoginResponse, UserInfo


def _login_response(user_id=None, email="test@example.com"):
    return LoginResponse(
        access_token="test-token",
        user=UserInfo(id=user_id or uuid.uuid4(), email=email),
    )


# -------------------------
# POST /auth/login
# -------------------------

def test_login_success(unauth_client):
    mock_resp = _login_response(email="user@example.com")
    with patch("routers.auth.auth_service.login", return_value=mock_resp):
        response = unauth_client.post(
            "/auth/login",
            json={"email": "user@example.com", "password": "secret123"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["access_token"] == "test-token"
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "user@example.com"


def test_login_invalid_credentials(unauth_client):
    with patch("routers.auth.auth_service.login", side_effect=Unauthorized("Invalid email or password")):
        response = unauth_client.post(
            "/auth/login",
            json={"email": "user@example.com", "password": "wrongpass"},
        )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


def test_login_missing_fields(unauth_client):
    response = unauth_client.post("/auth/login", json={"email": "user@example.com"})
    assert response.status_code == 422


def test_login_invalid_email(unauth_client):
    response = unauth_client.post(
        "/auth/login",
        json={"email": "not-an-email", "password": "secret123"},
    )
    assert response.status_code == 422


# -------------------------
# POST /auth/logout
# -------------------------

def test_logout_authenticated(auth_client):
    with patch("routers.auth.auth_service.logout", return_value=None):
        response = auth_client.post("/auth/logout")

    assert response.status_code == 204


def test_logout_unauthenticated(unauth_client):
    response = unauth_client.post("/auth/logout")
    assert response.status_code in (401, 403)
