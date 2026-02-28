import uuid

from fastapi import UploadFile, HTTPException, status
from sqlalchemy.orm import Session

from db.models import Project
from schemas.projects import UploadResponse
from services import minio_client
from core import exceptions
from core.config import settings


async def upload_design(
    db: Session,
    project_id: uuid.UUID,
    file: UploadFile,
    allowed_types: list[str],
) -> UploadResponse:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise exceptions.ProjectNotFound()

    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No filename provided")

    content_type = file.content_type or ""
    if content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: PDF, TXT. Got: {content_type}",
        )

    contents = await file.read()
    object_name = f"{project_id}/{file.filename}"

    object_key = minio_client.upload_file(
        settings.MINIO_BUCKET_DESIGNS,
        object_name,
        contents,
        content_type,
    )

    return UploadResponse(
        filename=file.filename,
        project_id=project_id,
        object_key=object_key,
    )


async def upload_image(
    db: Session,
    project_id: uuid.UUID,
    file: UploadFile,
    allowed_types: list[str],
) -> UploadResponse:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise exceptions.ProjectNotFound()

    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No filename provided")

    content_type = file.content_type or ""
    if content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: PNG, JPEG. Got: {content_type}",
        )

    contents = await file.read()
    object_name = f"{project_id}/{file.filename}"

    object_key = minio_client.upload_file(
        settings.MINIO_BUCKET_IMAGES,
        object_name,
        contents,
        content_type,
    )

    return UploadResponse(
        filename=file.filename,
        project_id=project_id,
        object_key=object_key,
    )
