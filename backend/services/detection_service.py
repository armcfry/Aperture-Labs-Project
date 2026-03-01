import uuid

from sqlalchemy.orm import Session

from schemas.detection import DetectionResponse
from services import minio_client
from core import exceptions
from core.config import settings


def handle_detection_result(
    db: Session,
    payload: DetectionResponse,
    webhook_secret: str | None,
) -> None:
    if webhook_secret != settings.DETECTION_WEBHOOK_SECRET:
        raise exceptions.PermissionDenied("Invalid webhook secret")

    # TODO: parse payload.response and update the relevant submission
    # This will depend on the structure of the detection service's response
    pass

def trigger_detection(
    db: Session,
    submission_id: uuid.UUID,
    project_id: uuid.UUID,
    image_object_key: str,
) -> None:
    """
    Entry point for the FOD detection pipeline.
    Called automatically when a new image is uploaded.

    TODO: Implement detection logic here. This function receives:
      - submission_id: the submission to update with results
      - project_id: the project the submission belongs to
      - image_object_key: "{project_id}/images/{filename}" — the image to run detection on
      - design_object_keys: list of "{project_id}/designs/{filename}" — reference design docs

    Expected implementation steps:
      1. Fetch image from MinIO using image_object_key
      2. Fetch design docs from MinIO using design_object_keys
      3. Run detection model against image + designs
      4. Update submission status, pass_fail, anomaly_count
      5. Create Anomaly records for each detected anomaly
    """
    bucket = str(project_id)

    # List all design docs under {project_id}/designs/
    design_object_names = minio_client.list_objects(
        bucket=bucket,
        prefix="designs/",
    )
    design_object_keys = [
        f"{bucket}/{object_name}" for object_name in design_object_names
    ]

    # Stub — replace with real detection logic
    print(f"[detection] triggered for submission {submission_id}")
    print(f"[detection] image: {image_object_key}")
    print(f"[detection] designs: {design_object_keys}")


def handle_detection_result(
    db: Session,
    payload: DetectionResponse,
    webhook_secret: str | None,
) -> None:
    if webhook_secret != settings.DETECTION_WEBHOOK_SECRET:
        raise exceptions.PermissionDenied("Invalid webhook secret")

    # TODO: parse payload.response and update the relevant submission
    pass
