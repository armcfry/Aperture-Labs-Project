import uuid
from datetime import datetime, timezone
from unittest.mock import patch

from core.exceptions import AlreadyMember, MemberNotFound, ProjectNotFound, UserNotFound


def _fake_member(project_id=None, user_id=None, role="editor"):
    class _FakeMember:
        pass

    m = _FakeMember()
    m.project_id = project_id or uuid.uuid4()
    m.user_id = user_id or uuid.uuid4()
    m.role = role
    m.joined_at = datetime.now(timezone.utc)
    return m


# -------------------------
# POST /projects/{project_id}/members
# -------------------------

def test_add_member_success(auth_client):
    project_id = uuid.uuid4()
    user_id = uuid.uuid4()
    fake = _fake_member(project_id=project_id, user_id=user_id, role="editor")

    with patch("routers.project_members.project_member_service.add_member", return_value=fake):
        response = auth_client.post(
            f"/projects/{project_id}/members",
            json={"project_id": str(project_id), "user_id": str(user_id), "role": "editor"},
        )

    assert response.status_code == 201
    data = response.json()
    assert data["role"] == "editor"
    assert data["user_id"] == str(user_id)
    assert data["project_id"] == str(project_id)


def test_add_member_project_not_found(auth_client):
    project_id = uuid.uuid4()
    user_id = uuid.uuid4()

    with patch(
        "routers.project_members.project_member_service.add_member",
        side_effect=ProjectNotFound(),
    ):
        response = auth_client.post(
            f"/projects/{project_id}/members",
            json={"project_id": str(project_id), "user_id": str(user_id), "role": "viewer"},
        )

    assert response.status_code == 404


def test_add_member_user_not_found(auth_client):
    project_id = uuid.uuid4()
    user_id = uuid.uuid4()

    with patch(
        "routers.project_members.project_member_service.add_member",
        side_effect=UserNotFound(),
    ):
        response = auth_client.post(
            f"/projects/{project_id}/members",
            json={"project_id": str(project_id), "user_id": str(user_id), "role": "editor"},
        )

    assert response.status_code == 404


def test_add_member_already_member(auth_client):
    project_id = uuid.uuid4()
    user_id = uuid.uuid4()

    with patch(
        "routers.project_members.project_member_service.add_member",
        side_effect=AlreadyMember(),
    ):
        response = auth_client.post(
            f"/projects/{project_id}/members",
            json={"project_id": str(project_id), "user_id": str(user_id), "role": "editor"},
        )

    assert response.status_code == 409


def test_add_member_invalid_role(auth_client):
    project_id = uuid.uuid4()
    user_id = uuid.uuid4()

    response = auth_client.post(
        f"/projects/{project_id}/members",
        json={"project_id": str(project_id), "user_id": str(user_id), "role": "superadmin"},
    )
    assert response.status_code == 422


def test_add_member_unauthenticated(unauth_client):
    project_id = uuid.uuid4()
    response = unauth_client.post(
        f"/projects/{project_id}/members",
        json={"project_id": str(project_id), "user_id": str(uuid.uuid4()), "role": "editor"},
    )
    assert response.status_code in (401, 403)


# -------------------------
# GET /projects/{project_id}/members
# -------------------------

def test_list_members(auth_client):
    project_id = uuid.uuid4()
    fakes = [_fake_member(project_id=project_id, role=r) for r in ("owner", "editor")]

    with patch(
        "routers.project_members.project_member_service.list_members", return_value=fakes
    ):
        response = auth_client.get(f"/projects/{project_id}/members")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert {m["role"] for m in data} == {"owner", "editor"}


def test_list_members_empty(auth_client):
    project_id = uuid.uuid4()

    with patch(
        "routers.project_members.project_member_service.list_members", return_value=[]
    ):
        response = auth_client.get(f"/projects/{project_id}/members")

    assert response.status_code == 200
    assert response.json() == []


def test_list_members_project_not_found(auth_client):
    project_id = uuid.uuid4()

    with patch(
        "routers.project_members.project_member_service.list_members",
        side_effect=ProjectNotFound(),
    ):
        response = auth_client.get(f"/projects/{project_id}/members")

    assert response.status_code == 404


# -------------------------
# GET /projects/{project_id}/members/{user_id}
# -------------------------

def test_get_member_success(auth_client):
    project_id = uuid.uuid4()
    user_id = uuid.uuid4()
    fake = _fake_member(project_id=project_id, user_id=user_id, role="owner")

    with patch(
        "routers.project_members.project_member_service.get_member", return_value=fake
    ):
        response = auth_client.get(f"/projects/{project_id}/members/{user_id}")

    assert response.status_code == 200
    assert response.json()["role"] == "owner"


def test_get_member_not_found(auth_client):
    project_id = uuid.uuid4()
    user_id = uuid.uuid4()

    with patch(
        "routers.project_members.project_member_service.get_member",
        side_effect=MemberNotFound(),
    ):
        response = auth_client.get(f"/projects/{project_id}/members/{user_id}")

    assert response.status_code == 404


# -------------------------
# PATCH /projects/{project_id}/members/{user_id}
# -------------------------

def test_update_member_role_success(auth_client):
    project_id = uuid.uuid4()
    user_id = uuid.uuid4()
    fake = _fake_member(project_id=project_id, user_id=user_id, role="viewer")

    with patch(
        "routers.project_members.project_member_service.update_member_role", return_value=fake
    ):
        response = auth_client.patch(
            f"/projects/{project_id}/members/{user_id}",
            json={"project_id": str(project_id), "user_id": str(user_id), "role": "viewer"},
        )

    assert response.status_code == 200
    assert response.json()["role"] == "viewer"


def test_update_member_role_not_found(auth_client):
    project_id = uuid.uuid4()
    user_id = uuid.uuid4()

    with patch(
        "routers.project_members.project_member_service.update_member_role",
        side_effect=MemberNotFound(),
    ):
        response = auth_client.patch(
            f"/projects/{project_id}/members/{user_id}",
            json={"project_id": str(project_id), "user_id": str(user_id), "role": "editor"},
        )

    assert response.status_code == 404


# -------------------------
# DELETE /projects/{project_id}/members/{user_id}
# -------------------------

def test_remove_member_success(auth_client):
    project_id = uuid.uuid4()
    user_id = uuid.uuid4()

    with patch(
        "routers.project_members.project_member_service.remove_member", return_value=None
    ):
        response = auth_client.delete(f"/projects/{project_id}/members/{user_id}")

    assert response.status_code == 204


def test_remove_member_not_found(auth_client):
    project_id = uuid.uuid4()
    user_id = uuid.uuid4()

    with patch(
        "routers.project_members.project_member_service.remove_member",
        side_effect=MemberNotFound(),
    ):
        response = auth_client.delete(f"/projects/{project_id}/members/{user_id}")

    assert response.status_code == 404
