from sqlalchemy.orm import Session

from schemas.detection import DetectionResponse
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
