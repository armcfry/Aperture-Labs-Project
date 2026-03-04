import uuid
from datetime import datetime, timezone
from unittest.mock import patch

from core.exceptions import InvalidStateTransition, ProjectNotFound, SubmissionNotFound


def _fake_submission(
    submission_id=None,
    project_id=None,
    user_id=None,
    status="queued",
    pass_fail="unknown",
    image_id="proj/images/test.png",
    anomaly_count=None,
    error_message=None,
):
    class _FakeSub:
        pass

    s = _FakeSub()
    s.id = submission_id or uuid.uuid4()
    s.project_id = project_id or uuid.uuid4()
    s.submitted_by_user_id = user_id or uuid.uuid4()
    s.image_id = image_id
    s.status = status
    s.pass_fail = pass_fail
    s.anomaly_count = anomaly_count
    s.error_message = error_message
    s.submitted_at = datetime.now(timezone.utc)
    return s


# -------------------------
# POST /projects/{project_id}/submissions
# -------------------------

def test_create_submission_success(auth_client):
    project_id = uuid.uuid4()
    user_id = uuid.uuid4()
    fake = _fake_submission(project_id=project_id, user_id=user_id)

    with patch("routers.submissions.submission_service.create_submission", return_value=fake):
        response = auth_client.post(
            f"/projects/{project_id}/submissions",
            json={
                "project_id": str(project_id),
                "image_id": "proj/images/test.png",
                "submitted_by_user_id": str(user_id),
            },
        )

    assert response.status_code == 201
    data = response.json()
    assert data["image_id"] == "proj/images/test.png"
    assert data["status"] == "queued"
    assert data["pass_fail"] == "unknown"


def test_create_submission_project_not_found(auth_client):
    project_id = uuid.uuid4()
    user_id = uuid.uuid4()

    with patch(
        "routers.submissions.submission_service.create_submission",
        side_effect=ProjectNotFound(),
    ):
        response = auth_client.post(
            f"/projects/{project_id}/submissions",
            json={
                "project_id": str(project_id),
                "image_id": "proj/images/test.png",
                "submitted_by_user_id": str(user_id),
            },
        )

    assert response.status_code == 404


def test_create_submission_missing_fields(auth_client):
    project_id = uuid.uuid4()
    response = auth_client.post(
        f"/projects/{project_id}/submissions",
        json={"project_id": str(project_id)},
    )
    assert response.status_code == 422


def test_create_submission_unauthenticated(unauth_client):
    project_id = uuid.uuid4()
    response = unauth_client.post(
        f"/projects/{project_id}/submissions",
        json={
            "project_id": str(project_id),
            "image_id": "proj/images/test.png",
            "submitted_by_user_id": str(uuid.uuid4()),
        },
    )
    assert response.status_code in (401, 403)


# -------------------------
# GET /projects/{project_id}/submissions
# -------------------------

def test_list_submissions(auth_client):
    project_id = uuid.uuid4()
    fakes = [_fake_submission(project_id=project_id) for _ in range(2)]

    with patch(
        "routers.submissions.submission_service.list_submissions_for_project",
        return_value=fakes,
    ):
        response = auth_client.get(f"/projects/{project_id}/submissions")

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_list_submissions_with_status_filter(auth_client):
    project_id = uuid.uuid4()
    fake = _fake_submission(project_id=project_id, status="complete")

    with patch(
        "routers.submissions.submission_service.list_submissions_for_project",
        return_value=[fake],
    ) as mock_list:
        response = auth_client.get(f"/projects/{project_id}/submissions?status=complete")

    assert response.status_code == 200
    mock_list.assert_called_once_with(
        db=mock_list.call_args.kwargs["db"],
        project_id=project_id,
        status="complete",
        pass_fail=None,
    )


def test_list_submissions_empty(auth_client):
    project_id = uuid.uuid4()
    with patch(
        "routers.submissions.submission_service.list_submissions_for_project",
        return_value=[],
    ):
        response = auth_client.get(f"/projects/{project_id}/submissions")

    assert response.status_code == 200
    assert response.json() == []


# -------------------------
# GET /projects/{project_id}/submissions/{submission_id}
# -------------------------

def test_get_submission_success(auth_client):
    project_id = uuid.uuid4()
    submission_id = uuid.uuid4()
    fake = _fake_submission(project_id=project_id, submission_id=submission_id)

    with patch("routers.submissions.submission_service.get_submission", return_value=fake):
        response = auth_client.get(f"/projects/{project_id}/submissions/{submission_id}")

    assert response.status_code == 200
    assert response.json()["id"] == str(submission_id)


def test_get_submission_not_found(auth_client):
    project_id = uuid.uuid4()
    submission_id = uuid.uuid4()

    with patch(
        "routers.submissions.submission_service.get_submission",
        side_effect=SubmissionNotFound(),
    ):
        response = auth_client.get(f"/projects/{project_id}/submissions/{submission_id}")

    assert response.status_code == 404


# -------------------------
# PATCH /projects/{project_id}/submissions/{submission_id}
# -------------------------

def test_update_submission_success(auth_client):
    project_id = uuid.uuid4()
    submission_id = uuid.uuid4()
    fake = _fake_submission(
        project_id=project_id,
        submission_id=submission_id,
        status="complete",
        pass_fail="pass",
        anomaly_count=0,
    )

    with patch("routers.submissions.submission_service.update_submission", return_value=fake):
        response = auth_client.patch(
            f"/projects/{project_id}/submissions/{submission_id}",
            json={"status": "complete", "pass_fail": "pass", "anomaly_count": 0},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "complete"
    assert data["pass_fail"] == "pass"
    assert data["anomaly_count"] == 0


def test_update_submission_not_found(auth_client):
    project_id = uuid.uuid4()
    submission_id = uuid.uuid4()

    with patch(
        "routers.submissions.submission_service.update_submission",
        side_effect=SubmissionNotFound(),
    ):
        response = auth_client.patch(
            f"/projects/{project_id}/submissions/{submission_id}",
            json={"status": "failed"},
        )

    assert response.status_code == 404


# -------------------------
# DELETE /projects/{project_id}/submissions/{submission_id}
# -------------------------

def test_delete_submission_success(auth_client):
    project_id = uuid.uuid4()
    submission_id = uuid.uuid4()

    with patch("routers.submissions.submission_service.delete_submission", return_value=None):
        response = auth_client.delete(f"/projects/{project_id}/submissions/{submission_id}")

    assert response.status_code == 204


def test_delete_submission_not_found(auth_client):
    project_id = uuid.uuid4()
    submission_id = uuid.uuid4()

    with patch(
        "routers.submissions.submission_service.delete_submission",
        side_effect=SubmissionNotFound(),
    ):
        response = auth_client.delete(f"/projects/{project_id}/submissions/{submission_id}")

    assert response.status_code == 404


# -------------------------
# POST /projects/{project_id}/submissions/{submission_id}/retry
# -------------------------

def test_retry_submission_success(auth_client):
    project_id = uuid.uuid4()
    submission_id = uuid.uuid4()
    fake = _fake_submission(
        project_id=project_id,
        submission_id=submission_id,
        status="queued",
        pass_fail="unknown",
    )

    with patch("routers.submissions.submission_service.retry_submission", return_value=fake):
        response = auth_client.post(
            f"/projects/{project_id}/submissions/{submission_id}/retry"
        )

    assert response.status_code == 200
    assert response.json()["status"] == "queued"


def test_retry_submission_invalid_state(auth_client):
    project_id = uuid.uuid4()
    submission_id = uuid.uuid4()

    with patch(
        "routers.submissions.submission_service.retry_submission",
        side_effect=InvalidStateTransition(
            "Only failed or complete_with_errors submissions can be retried"
        ),
    ):
        response = auth_client.post(
            f"/projects/{project_id}/submissions/{submission_id}/retry"
        )

    assert response.status_code == 400
    assert "retried" in response.json()["detail"]


def test_retry_submission_not_found(auth_client):
    project_id = uuid.uuid4()
    submission_id = uuid.uuid4()

    with patch(
        "routers.submissions.submission_service.retry_submission",
        side_effect=SubmissionNotFound(),
    ):
        response = auth_client.post(
            f"/projects/{project_id}/submissions/{submission_id}/retry"
        )

    assert response.status_code == 404
