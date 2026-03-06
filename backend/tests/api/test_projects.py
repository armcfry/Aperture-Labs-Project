import uuid
from datetime import datetime, timezone
from unittest.mock import patch

from core.exceptions import InvalidStateTransition, PermissionDenied, ProjectNotFound


def _fake_project_obj(
    project_id=None,
    name="Test Project",
    description=None,
    detector_version=None,
    created_by_user_id=None,
    archived_at=None,
):
    """Return a plain object with Project attributes for Pydantic serialization."""

    class _FakeProject:
        pass

    p = _FakeProject()
    p.id = project_id or uuid.uuid4()
    p.name = name
    p.description = description
    p.detector_version = detector_version
    p.created_by_user_id = created_by_user_id or uuid.uuid4()
    p.created_at = datetime.now(timezone.utc)
    p.updated_at = datetime.now(timezone.utc)
    p.archived_at = archived_at
    return p


# -------------------------
# POST /projects  (auth required)
# -------------------------

def test_create_project_success(auth_client):
    fake = _fake_project_obj(name="Runway Alpha")
    with patch("routers.projects.project_service.create_project", return_value=fake):
        response = auth_client.post("/projects", json={"name": "Runway Alpha"})

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Runway Alpha"
    assert "id" in data


def test_create_project_unauthenticated(unauth_client):
    response = unauth_client.post("/projects", json={"name": "Runway Alpha"})
    assert response.status_code in (401, 403)


def test_create_project_missing_name(auth_client):
    response = auth_client.post("/projects", json={"description": "no name"})
    assert response.status_code == 422


def test_create_project_with_all_fields(auth_client):
    fake = _fake_project_obj(
        name="Full Project",
        description="Desc",
        detector_version="v2",
    )
    with patch("routers.projects.project_service.create_project", return_value=fake):
        response = auth_client.post(
            "/projects",
            json={"name": "Full Project", "description": "Desc", "detector_version": "v2"},
        )

    assert response.status_code == 201
    data = response.json()
    assert data["description"] == "Desc"
    assert data["detector_version"] == "v2"


# -------------------------
# GET /projects  (auth required)
# -------------------------

def test_list_projects(auth_client):
    fakes = [_fake_project_obj(name=f"Project {i}") for i in range(3)]
    with patch("routers.projects.project_service.list_projects_for_user", return_value=fakes):
        response = auth_client.get("/projects")

    assert response.status_code == 200
    assert len(response.json()) == 3


def test_list_projects_empty(auth_client):
    with patch("routers.projects.project_service.list_projects_for_user", return_value=[]):
        response = auth_client.get("/projects")

    assert response.status_code == 200
    assert response.json() == []


def test_list_projects_include_archived(auth_client):
    archived = _fake_project_obj(name="Old", archived_at=datetime.now(timezone.utc))
    active = _fake_project_obj(name="Active")
    with patch(
        "routers.projects.project_service.list_projects_for_user",
        return_value=[archived, active],
    ) as mock_list:
        response = auth_client.get("/projects?include_archived=true")

    assert response.status_code == 200
    mock_list.assert_called_once_with(db=mock_list.call_args.kwargs["db"], include_archived=True)


def test_list_projects_unauthenticated(unauth_client):
    response = unauth_client.get("/projects")
    assert response.status_code in (401, 403)


# -------------------------
# GET /projects/{project_id}  (auth required)
# -------------------------

def test_get_project_success(auth_client):
    project_id = uuid.uuid4()
    fake = _fake_project_obj(project_id=project_id, name="Found Project")
    with patch("routers.projects.project_service.get_project", return_value=fake):
        response = auth_client.get(f"/projects/{project_id}")

    assert response.status_code == 200
    assert response.json()["name"] == "Found Project"


def test_get_project_not_found(auth_client):
    project_id = uuid.uuid4()
    with patch("routers.projects.project_service.get_project", side_effect=ProjectNotFound()):
        response = auth_client.get(f"/projects/{project_id}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Project not found"


def test_get_project_invalid_uuid(auth_client):
    response = auth_client.get("/projects/not-a-uuid")
    assert response.status_code == 422


# -------------------------
# PATCH /projects/{project_id}  (auth required)
# -------------------------

def test_update_project_success(auth_client):
    project_id = uuid.uuid4()
    fake = _fake_project_obj(project_id=project_id, name="Updated Name")
    with patch("routers.projects.project_service.update_project", return_value=fake):
        response = auth_client.patch(
            f"/projects/{project_id}", json={"name": "Updated Name"}
        )

    assert response.status_code == 200
    assert response.json()["name"] == "Updated Name"


def test_update_project_not_found(auth_client):
    project_id = uuid.uuid4()
    with patch(
        "routers.projects.project_service.update_project", side_effect=ProjectNotFound()
    ):
        response = auth_client.patch(f"/projects/{project_id}", json={"name": "X"})

    assert response.status_code == 404


def test_update_project_permission_denied(auth_client):
    project_id = uuid.uuid4()
    with patch(
        "routers.projects.project_service.update_project",
        side_effect=PermissionDenied("Not enough permissions to update this project"),
    ):
        response = auth_client.patch(f"/projects/{project_id}", json={"name": "X"})

    assert response.status_code == 403
    assert "permissions" in response.json()["detail"]


# -------------------------
# DELETE /projects/{project_id}  (auth required)
# -------------------------

def test_delete_project_success(auth_client):
    project_id = uuid.uuid4()
    with patch("routers.projects.project_service.delete_project", return_value=None):
        response = auth_client.delete(f"/projects/{project_id}")

    assert response.status_code == 204


def test_delete_project_not_found(auth_client):
    project_id = uuid.uuid4()
    with patch(
        "routers.projects.project_service.delete_project", side_effect=ProjectNotFound()
    ):
        response = auth_client.delete(f"/projects/{project_id}")

    assert response.status_code == 404


def test_delete_project_permission_denied(auth_client):
    project_id = uuid.uuid4()
    with patch(
        "routers.projects.project_service.delete_project",
        side_effect=PermissionDenied("Only the owner can delete this project"),
    ):
        response = auth_client.delete(f"/projects/{project_id}")

    assert response.status_code == 403
    assert "owner" in response.json()["detail"]


# -------------------------
# POST /projects/{project_id}/archive  (auth required)
# -------------------------

def test_archive_project_success(auth_client):
    project_id = uuid.uuid4()
    fake = _fake_project_obj(
        project_id=project_id,
        name="Archived Project",
        archived_at=datetime.now(timezone.utc),
    )
    with patch("routers.projects.project_service.archive_project", return_value=fake):
        response = auth_client.post(f"/projects/{project_id}/archive")

    assert response.status_code == 200
    data = response.json()
    assert data["archived_at"] is not None


def test_archive_project_not_found(auth_client):
    project_id = uuid.uuid4()
    with patch(
        "routers.projects.project_service.archive_project", side_effect=ProjectNotFound()
    ):
        response = auth_client.post(f"/projects/{project_id}/archive")

    assert response.status_code == 404


def test_archive_project_permission_denied(auth_client):
    project_id = uuid.uuid4()
    with patch(
        "routers.projects.project_service.archive_project",
        side_effect=PermissionDenied("Only the owner can archive this project"),
    ):
        response = auth_client.post(f"/projects/{project_id}/archive")

    assert response.status_code == 403
    assert "owner" in response.json()["detail"]


def test_archive_already_archived_project(auth_client):
    project_id = uuid.uuid4()
    with patch(
        "routers.projects.project_service.archive_project",
        side_effect=InvalidStateTransition("Project is already archived"),
    ):
        response = auth_client.post(f"/projects/{project_id}/archive")

    assert response.status_code == 400
    assert "already archived" in response.json()["detail"]
