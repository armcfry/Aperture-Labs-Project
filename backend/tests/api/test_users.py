import uuid
from datetime import datetime, timezone
from unittest.mock import patch

from core.exceptions import ConflictError, UserNotFound


def _fake_user_obj(user_id=None, email="test@example.com"):
    """Return a plain object with User attributes for Pydantic serialization."""

    class _FakeUser:
        pass

    u = _FakeUser()
    u.id = user_id or uuid.uuid4()
    u.email = email
    u.created_at = datetime.now(timezone.utc)
    u.updated_at = datetime.now(timezone.utc)
    return u


# -------------------------
# POST /users  (no auth required)
# -------------------------

def test_create_user_success(unauth_client):
    fake = _fake_user_obj(email="new@example.com")
    with patch("routers.users.user_service.create_user", return_value=fake):
        response = unauth_client.post(
            "/users",
            json={"email": "new@example.com", "password": "pass1234"},
        )

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "new@example.com"
    assert "id" in data


def test_create_user_duplicate_email(unauth_client):
    with patch(
        "routers.users.user_service.create_user",
        side_effect=ConflictError("A user with this email already exists"),
    ):
        response = unauth_client.post(
            "/users",
            json={"email": "existing@example.com", "password": "pass1234"},
        )

    assert response.status_code == 409
    assert "already exists" in response.json()["detail"]


def test_create_user_missing_password(unauth_client):
    response = unauth_client.post("/users", json={"email": "a@example.com"})
    assert response.status_code == 422


def test_create_user_invalid_email(unauth_client):
    response = unauth_client.post(
        "/users", json={"email": "not-an-email", "password": "pass1234"}
    )
    assert response.status_code == 422


# -------------------------
# GET /users  (auth required)
# -------------------------

def test_list_users(auth_client):
    fake1 = _fake_user_obj(email="a@example.com")
    fake2 = _fake_user_obj(email="b@example.com")
    with patch("routers.users.user_service.list_users", return_value=[fake1, fake2]):
        response = auth_client.get("/users")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert {d["email"] for d in data} == {"a@example.com", "b@example.com"}


def test_list_users_unauthenticated(unauth_client):
    response = unauth_client.get("/users")
    assert response.status_code in (401, 403)


def test_list_users_empty(auth_client):
    with patch("routers.users.user_service.list_users", return_value=[]):
        response = auth_client.get("/users")

    assert response.status_code == 200
    assert response.json() == []


# -------------------------
# GET /users/{user_id}  (auth required)
# -------------------------

def test_get_user_success(auth_client):
    user_id = uuid.uuid4()
    fake = _fake_user_obj(user_id=user_id, email="found@example.com")
    with patch("routers.users.user_service.get_user", return_value=fake):
        response = auth_client.get(f"/users/{user_id}")

    assert response.status_code == 200
    assert response.json()["email"] == "found@example.com"


def test_get_user_not_found(auth_client):
    user_id = uuid.uuid4()
    with patch("routers.users.user_service.get_user", side_effect=UserNotFound()):
        response = auth_client.get(f"/users/{user_id}")

    assert response.status_code == 404


def test_get_user_invalid_uuid(auth_client):
    response = auth_client.get("/users/not-a-uuid")
    assert response.status_code == 422


# -------------------------
# PATCH /users/{user_id}  (auth required)
# -------------------------

def test_update_user_success(auth_client):
    user_id = uuid.uuid4()
    fake = _fake_user_obj(user_id=user_id, email="updated@example.com")
    with patch("routers.users.user_service.update_user", return_value=fake):
        response = auth_client.patch(
            f"/users/{user_id}",
            json={"email": "updated@example.com"},
        )

    assert response.status_code == 200
    assert response.json()["email"] == "updated@example.com"


def test_update_user_not_found(auth_client):
    user_id = uuid.uuid4()
    with patch("routers.users.user_service.update_user", side_effect=UserNotFound()):
        response = auth_client.patch(f"/users/{user_id}", json={"email": "x@example.com"})

    assert response.status_code == 404


def test_update_user_email_conflict(auth_client):
    user_id = uuid.uuid4()
    with patch(
        "routers.users.user_service.update_user",
        side_effect=ConflictError("A user with this email already exists"),
    ):
        response = auth_client.patch(
            f"/users/{user_id}", json={"email": "taken@example.com"}
        )

    assert response.status_code == 409


# -------------------------
# DELETE /users/{user_id}  (auth required)
# -------------------------

def test_delete_user_success(auth_client):
    user_id = uuid.uuid4()
    with patch("routers.users.user_service.delete_user", return_value=None):
        response = auth_client.delete(f"/users/{user_id}")

    assert response.status_code == 204


def test_delete_user_not_found(auth_client):
    user_id = uuid.uuid4()
    with patch("routers.users.user_service.delete_user", side_effect=UserNotFound()):
        response = auth_client.delete(f"/users/{user_id}")

    assert response.status_code == 404
