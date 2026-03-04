import uuid
from datetime import datetime, timezone
from unittest.mock import patch

from core.exceptions import AnomalyNotFound


def _fake_anomaly(
    anomaly_id=None,
    submission_id=None,
    label="scratch",
    description=None,
    severity="low",
    confidence=0.95,
):
    class _FakeAnomaly:
        pass

    a = _FakeAnomaly()
    a.id = anomaly_id or uuid.uuid4()
    a.submission_id = submission_id or uuid.uuid4()
    a.label = label
    a.description = description
    a.severity = severity
    a.confidence = confidence
    a.created_at = datetime.now(timezone.utc)
    return a


# -------------------------
# POST /anomalies
# -------------------------

def test_create_anomaly_success(auth_client):
    submission_id = uuid.uuid4()
    fake = _fake_anomaly(submission_id=submission_id, label="dent")

    with patch("routers.anomalies.anomaly_service.create_anomaly", return_value=fake):
        response = auth_client.post(
            "/anomalies",
            json={
                "submission_id": str(submission_id),
                "label": "dent",
                "severity": "low",
                "confidence": 0.95,
            },
        )

    assert response.status_code == 201
    data = response.json()
    assert data["label"] == "dent"
    assert data["severity"] == "low"
    assert data["confidence"] == 0.95


def test_create_anomaly_minimal_fields(auth_client):
    submission_id = uuid.uuid4()
    fake = _fake_anomaly(submission_id=submission_id, label="crack", severity=None, confidence=None)

    with patch("routers.anomalies.anomaly_service.create_anomaly", return_value=fake):
        response = auth_client.post(
            "/anomalies",
            json={"submission_id": str(submission_id), "label": "crack"},
        )

    assert response.status_code == 201
    assert response.json()["label"] == "crack"


def test_create_anomaly_invalid_confidence(auth_client):
    submission_id = uuid.uuid4()
    response = auth_client.post(
        "/anomalies",
        json={
            "submission_id": str(submission_id),
            "label": "scratch",
            "confidence": 1.5,
        },
    )
    assert response.status_code == 422


def test_create_anomaly_missing_label(auth_client):
    submission_id = uuid.uuid4()
    response = auth_client.post(
        "/anomalies",
        json={"submission_id": str(submission_id)},
    )
    assert response.status_code == 422


def test_create_anomaly_unauthenticated(unauth_client):
    response = unauth_client.post(
        "/anomalies",
        json={"submission_id": str(uuid.uuid4()), "label": "scratch"},
    )
    assert response.status_code in (401, 403)


# -------------------------
# GET /anomalies?submission_id=...
# -------------------------

def test_list_anomalies(auth_client):
    submission_id = uuid.uuid4()
    fakes = [_fake_anomaly(submission_id=submission_id) for _ in range(3)]

    with patch(
        "routers.anomalies.anomaly_service.list_anomalies_for_submission",
        return_value=fakes,
    ):
        response = auth_client.get(f"/anomalies?submission_id={submission_id}")

    assert response.status_code == 200
    assert len(response.json()) == 3


def test_list_anomalies_with_severity_filter(auth_client):
    submission_id = uuid.uuid4()
    fake = _fake_anomaly(submission_id=submission_id, severity="high")

    with patch(
        "routers.anomalies.anomaly_service.list_anomalies_for_submission",
        return_value=[fake],
    ) as mock_list:
        response = auth_client.get(f"/anomalies?submission_id={submission_id}&severity=high")

    assert response.status_code == 200
    mock_list.assert_called_once_with(
        db=mock_list.call_args.kwargs["db"],
        submission_id=submission_id,
        severity="high",
    )


def test_list_anomalies_empty(auth_client):
    submission_id = uuid.uuid4()
    with patch(
        "routers.anomalies.anomaly_service.list_anomalies_for_submission",
        return_value=[],
    ):
        response = auth_client.get(f"/anomalies?submission_id={submission_id}")

    assert response.status_code == 200
    assert response.json() == []


# -------------------------
# GET /anomalies/{anomaly_id}
# -------------------------

def test_get_anomaly_success(auth_client):
    anomaly_id = uuid.uuid4()
    fake = _fake_anomaly(anomaly_id=anomaly_id, label="fracture")

    with patch("routers.anomalies.anomaly_service.get_anomaly", return_value=fake):
        response = auth_client.get(f"/anomalies/{anomaly_id}")

    assert response.status_code == 200
    assert response.json()["label"] == "fracture"
    assert response.json()["id"] == str(anomaly_id)


def test_get_anomaly_not_found(auth_client):
    anomaly_id = uuid.uuid4()

    with patch(
        "routers.anomalies.anomaly_service.get_anomaly",
        side_effect=AnomalyNotFound(),
    ):
        response = auth_client.get(f"/anomalies/{anomaly_id}")

    assert response.status_code == 404


def test_get_anomaly_invalid_uuid(auth_client):
    response = auth_client.get("/anomalies/not-a-uuid")
    assert response.status_code == 422


# -------------------------
# PATCH /anomalies/{anomaly_id}
# -------------------------

def test_update_anomaly_success(auth_client):
    anomaly_id = uuid.uuid4()
    fake = _fake_anomaly(anomaly_id=anomaly_id, label="updated-label", severity="high")

    with patch("routers.anomalies.anomaly_service.update_anomaly", return_value=fake):
        response = auth_client.patch(
            f"/anomalies/{anomaly_id}",
            json={"label": "updated-label", "severity": "high"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["label"] == "updated-label"
    assert data["severity"] == "high"


def test_update_anomaly_not_found(auth_client):
    anomaly_id = uuid.uuid4()

    with patch(
        "routers.anomalies.anomaly_service.update_anomaly",
        side_effect=AnomalyNotFound(),
    ):
        response = auth_client.patch(f"/anomalies/{anomaly_id}", json={"label": "x"})

    assert response.status_code == 404


# -------------------------
# DELETE /anomalies/{anomaly_id}
# -------------------------

def test_delete_anomaly_success(auth_client):
    anomaly_id = uuid.uuid4()

    with patch("routers.anomalies.anomaly_service.delete_anomaly", return_value=None):
        response = auth_client.delete(f"/anomalies/{anomaly_id}")

    assert response.status_code == 204


def test_delete_anomaly_not_found(auth_client):
    anomaly_id = uuid.uuid4()

    with patch(
        "routers.anomalies.anomaly_service.delete_anomaly",
        side_effect=AnomalyNotFound(),
    ):
        response = auth_client.delete(f"/anomalies/{anomaly_id}")

    assert response.status_code == 404
