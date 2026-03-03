from fastapi import APIRouter, Depends, Header, status
from sqlalchemy.orm import Session

from db.session import get_db
from schemas.detection import DetectionResponse
from services import detection_service


router = APIRouter(
    prefix="/webhooks/detection",
    tags=["Detection"],
)


# -------------------------
# Receive Detection Result
# -------------------------
@router.post(
    "",
    status_code=status.HTTP_200_OK,
)
def receive_detection_result(
    payload: DetectionResponse,
    db: Session = Depends(get_db),
    x_webhook_secret: str | None = Header(default=None),
):
    detection_service.handle_detection_result(
        db=db,
        payload=payload,
        webhook_secret=x_webhook_secret,
    )