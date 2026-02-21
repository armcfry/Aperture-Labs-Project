from datetime import datetime
from fastapi import APIRouter, HTTPException, UploadFile, File, Query

from schemas.projects import DesignSpec, UploadResponse
from services import minio_client
from routers.projects import get_project, add_design_spec

router = APIRouter(prefix="/api/upload", tags=["uploads"])

ALLOWED_DESIGN_TYPES = ["application/pdf", "text/plain"]
ALLOWED_IMAGE_TYPES = ["image/png", "image/jpeg", "image/jpg"]


@router.post("/design", response_model=UploadResponse)
async def upload_design(
    file: UploadFile = File(...),
    project_id: str = Query(..., description="Project ID to associate the design with"),
) -> UploadResponse:
    project = get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    content_type = file.content_type or ""
    if content_type not in ALLOWED_DESIGN_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: PDF, TXT. Current type: {content_type}",
        )

    contents = await file.read()
    object_name = f"{project_id}/{file.filename}"

    try:
        object_key = minio_client.upload_file(
            minio_client.BUCKET_DESIGNS,
            object_name,
            contents,
            content_type,
        )

        spec = DesignSpec(
            filename=file.filename,
            object_key=object_key,
            uploaded_at=datetime.now(),
        )
        add_design_spec(project_id, spec)

        return UploadResponse(
            filename=file.filename,
            project_id=project_id,
            object_key=object_key,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.post("/image", response_model=UploadResponse)
async def upload_image(
    file: UploadFile = File(...),
    project_id: str = Query(..., description="Project ID to associate the image with"),
) -> UploadResponse:
    project = get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    content_type = file.content_type or ""
    if content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: PNG, JPEG. Current type:{content_type}",
        )

    contents = await file.read()
    object_name = f"{project_id}/{file.filename}"

    try:
        object_key = minio_client.upload_file(
            minio_client.BUCKET_IMAGES,
            object_name,
            contents,
            content_type,
        )

        return UploadResponse(
            filename=file.filename,
            project_id=project_id,
            object_key=object_key,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
