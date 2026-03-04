from unittest.mock import patch

from core.exceptions import PermissionDenied

VALID_SECRET = "test-webhook-secret"  # matches DETECTION_WEBHOOK_SECRET in conftest.py

VALID_PAYLOAD = {
    "response": "no_anomaly",
    "model": "fod-detector-v1",
    "inference_time_ms": 123.4,
}


# -------------------------
# POST /webhooks/detection
# -------------------------

def test_receive_detection_result_success(unauth_client):
    with patch(
        "routers.detection.detection_service.handle_detection_result", return_value=None
    ):
        response = unauth_client.post(
            "/webhooks/detection",
            json=VALID_PAYLOAD,
            headers={"x-webhook-secret": VALID_SECRET},
        )

    assert response.status_code == 200


def test_receive_detection_result_invalid_secret(unauth_client):
    with patch(
        "routers.detection.detection_service.handle_detection_result",
        side_effect=PermissionDenied("Invalid webhook secret"),
    ):
        response = unauth_client.post(
            "/webhooks/detection",
            json=VALID_PAYLOAD,
            headers={"x-webhook-secret": "wrong-secret"},
        )

    assert response.status_code == 403
    assert "Invalid webhook secret" in response.json()["detail"]


def test_receive_detection_result_missing_secret(unauth_client):
    with patch(
        "routers.detection.detection_service.handle_detection_result",
        side_effect=PermissionDenied("Invalid webhook secret"),
    ):
        response = unauth_client.post("/webhooks/detection", json=VALID_PAYLOAD)

    assert response.status_code == 403


def test_receive_detection_result_missing_response_field(unauth_client):
    response = unauth_client.post(
        "/webhooks/detection",
        json={"model": "fod-detector-v1", "inference_time_ms": 100.0},
        headers={"x-webhook-secret": VALID_SECRET},
    )
    assert response.status_code == 422


def test_receive_detection_result_missing_model_field(unauth_client):
    response = unauth_client.post(
        "/webhooks/detection",
        json={"response": "ok", "inference_time_ms": 100.0},
        headers={"x-webhook-secret": VALID_SECRET},
    )
    assert response.status_code == 422


def test_receive_detection_result_missing_inference_time(unauth_client):
    response = unauth_client.post(
        "/webhooks/detection",
        json={"response": "ok", "model": "fod-detector-v1"},
        headers={"x-webhook-secret": VALID_SECRET},
    )
    assert response.status_code == 422


def test_receive_detection_result_empty_body(unauth_client):
    response = unauth_client.post(
        "/webhooks/detection",
        json={},
        headers={"x-webhook-secret": VALID_SECRET},
    )
    assert response.status_code == 422


def test_receive_detection_result_no_auth_required(unauth_client):
    """Webhook uses its own secret header, not bearer auth."""
    with patch(
        "routers.detection.detection_service.handle_detection_result", return_value=None
    ):
        response = unauth_client.post(
            "/webhooks/detection",
            json=VALID_PAYLOAD,
            headers={"x-webhook-secret": VALID_SECRET},
        )

    # Should succeed without a bearer token
    assert response.status_code == 200
