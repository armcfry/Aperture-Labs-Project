from uuid import UUID

from fastapi import APIRouter, Depends, UploadFile, File, Query, status
from sqlalchemy.orm import Session

from db.session import get_db
from schemas.projects import UploadResponse
from services import upload_service


router = APIRouter(
    prefix="/uploads",
    tags=["Uploads"],
)

ALLOWED_DESIGN_TYPES = ["application/pdf", "text/plain"]
ALLOWED_IMAGE_TYPES = ["image/png", "image/jpeg", "image/jpg"]


# -------------------------
# Upload Design File
# -------------------------
@router.post("/design", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_design(
    project_id: UUID = Query(..., description="Project to associate the design with"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    return await upload_service.upload_design(
        db=db,
        project_id=project_id,
        file=file,
        allowed_types=ALLOWED_DESIGN_TYPES,
    )


# -------------------------
# Upload Image File
# -------------------------
@router.post("/image", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_image(
    project_id: UUID = Query(..., description="Project to associate the image with"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    return await upload_service.upload_image(
        db=db,
        project_id=project_id,
        file=file,
        allowed_types=ALLOWED_IMAGE_TYPES,
    )