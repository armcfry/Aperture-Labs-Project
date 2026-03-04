import io
import uuid
from unittest.mock import patch

from schemas.storage import ImageUploadResponse
from schemas.projects import UploadResponse


def _image_upload_response(project_id=None, submission_id=None):
    pid = project_id or uuid.uuid4()
    return ImageUploadResponse(
        filename="test.png",
        project_id=pid,
        object_key=f"{pid}/images/test.png",
        submission_id=submission_id or uuid.uuid4(),
    )


def _design_upload_response(project_id=None):
    pid = project_id or uuid.uuid4()
    return UploadResponse(
        filename="design.pdf",
        project_id=pid,
        object_key=f"{pid}/designs/design.pdf",
    )


# -------------------------
# POST /storage/image
# -------------------------

def test_upload_image_success(auth_client):
    project_id = uuid.uuid4()
    user_id = uuid.uuid4()
    mock_resp = _image_upload_response(project_id=project_id)

    with patch(
        "routers.storage.storage_service.upload_image", return_value=mock_resp
    ):
        response = auth_client.post(
            f"/storage/image?project_id={project_id}&user_id={user_id}",
            files={"file": ("test.png", io.BytesIO(b"fake-image-data"), "image/png")},
        )

    assert response.status_code == 201
    data = response.json()
    assert data["filename"] == "test.png"
    assert data["project_id"] == str(project_id)
    assert "submission_id" in data
    assert "object_key" in data


def test_upload_image_unauthenticated(unauth_client):
    project_id = uuid.uuid4()
    user_id = uuid.uuid4()
    response = unauth_client.post(
        f"/storage/image?project_id={project_id}&user_id={user_id}",
        files={"file": ("test.png", io.BytesIO(b"fake-image-data"), "image/png")},
    )
    assert response.status_code in (401, 403)


def test_upload_image_missing_project_id(auth_client):
    user_id = uuid.uuid4()
    response = auth_client.post(
        f"/storage/image?user_id={user_id}",
        files={"file": ("test.png", io.BytesIO(b"data"), "image/png")},
    )
    assert response.status_code == 422


def test_upload_image_missing_user_id(auth_client):
    project_id = uuid.uuid4()
    response = auth_client.post(
        f"/storage/image?project_id={project_id}",
        files={"file": ("test.png", io.BytesIO(b"data"), "image/png")},
    )
    assert response.status_code == 422


def test_upload_image_missing_file(auth_client):
    project_id = uuid.uuid4()
    user_id = uuid.uuid4()
    response = auth_client.post(
        f"/storage/image?project_id={project_id}&user_id={user_id}"
    )
    assert response.status_code == 422


# -------------------------
# POST /storage/design
# -------------------------

def test_upload_design_success(auth_client):
    project_id = uuid.uuid4()
    mock_resp = _design_upload_response(project_id=project_id)

    with patch(
        "routers.storage.storage_service.upload_design", return_value=mock_resp
    ):
        response = auth_client.post(
            f"/storage/design?project_id={project_id}",
            files={"file": ("design.pdf", io.BytesIO(b"fake-pdf-data"), "application/pdf")},
        )

    assert response.status_code == 201
    data = response.json()
    assert data["filename"] == "design.pdf"
    assert data["project_id"] == str(project_id)
    assert "object_key" in data


def test_upload_design_missing_project_id(auth_client):
    response = auth_client.post(
        "/storage/design",
        files={"file": ("design.pdf", io.BytesIO(b"data"), "application/pdf")},
    )
    assert response.status_code == 422


def test_upload_design_unauthenticated(unauth_client):
    project_id = uuid.uuid4()
    response = unauth_client.post(
        f"/storage/design?project_id={project_id}",
        files={"file": ("design.pdf", io.BytesIO(b"data"), "application/pdf")},
    )
    assert response.status_code in (401, 403)


# -------------------------
# GET /storage/image/{object_key}
# -------------------------

def test_get_image_url_success(auth_client):
    project_id = uuid.uuid4()
    object_key = f"{project_id}/images/test.png"
    mock_url = "https://minio.example.com/presigned-url"

    with patch(
        "routers.storage.storage_service.get_image_url",
        return_value={"url": mock_url, "expires_in": 900},
    ):
        response = auth_client.get(f"/storage/image/{object_key}")

    assert response.status_code == 200
    data = response.json()
    assert data["url"] == mock_url
    assert data["expires_in"] == 900


def test_get_image_url_with_custom_expiry(auth_client):
    project_id = uuid.uuid4()
    object_key = f"{project_id}/images/test.png"

    with patch(
        "routers.storage.storage_service.get_image_url",
        return_value={"url": "https://example.com/url", "expires_in": 3600},
    ) as mock_get:
        response = auth_client.get(f"/storage/image/{object_key}?expires=3600")

    assert response.status_code == 200
    mock_get.assert_called_once_with(object_key=object_key, expires=3600, download=False)


def test_get_image_url_unauthenticated(unauth_client):
    response = unauth_client.get("/storage/image/some-project/images/test.png")
    assert response.status_code in (401, 403)


# -------------------------
# GET /storage/design/{object_key}
# -------------------------

def test_get_design_url_success(auth_client):
    project_id = uuid.uuid4()
    object_key = f"{project_id}/designs/blueprint.pdf"
    mock_url = "https://minio.example.com/design-presigned"

    with patch(
        "routers.storage.storage_service.get_design_url",
        return_value={"url": mock_url, "expires_in": 900},
    ):
        response = auth_client.get(f"/storage/design/{object_key}")

    assert response.status_code == 200
    data = response.json()
    assert data["url"] == mock_url


def test_get_design_url_download_flag(auth_client):
    project_id = uuid.uuid4()
    object_key = f"{project_id}/designs/blueprint.pdf"

    with patch(
        "routers.storage.storage_service.get_design_url",
        return_value={"url": "https://example.com/dl", "expires_in": 900},
    ) as mock_get:
        response = auth_client.get(f"/storage/design/{object_key}?download=true")

    assert response.status_code == 200
    mock_get.assert_called_once_with(object_key=object_key, expires=900, download=True)
