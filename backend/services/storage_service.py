import uuid

from fastapi import UploadFile, HTTPException, status
from sqlalchemy.orm import Session

from db.models import Project, Submission
from schemas.storage import ImageUploadResponse
from schemas.projects import UploadResponse
from schemas.enums import SubmissionStatus, SubmissionPassFail
from services import minio_client
from services import detection_service
from core import exceptions


# -------------------------
# Uploads
# -------------------------

async def upload_image(
    db: Session,
    project_id: uuid.UUID,
    user_id: uuid.UUID,
    file: UploadFile,
    allowed_types: list[str],
) -> ImageUploadResponse:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise exceptions.ProjectNotFound()

    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No filename provided",
        )

    content_type = file.content_type or ""
    if content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: PNG, JPEG. Got: {content_type}",
        )

    # Upload image to MinIO
    contents = await file.read()
    bucket = str(project_id)
    object_name = f"images/{file.filename}"

    minio_client.upload_file(
        bucket=bucket,
        object_name=object_name,
        file_data=contents,
        content_type=content_type,
    )

    object_key = f"{bucket}/{object_name}"

    # Create submission
    submission = Submission(
        id=uuid.uuid4(),
        project_id=project_id,
        submitted_by_user_id=user_id,
        image_id=object_key,
        status=SubmissionStatus.queued,
        pass_fail=SubmissionPassFail.unknown,
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)

    # Trigger detection pipeline
    detection_service.trigger_detection(
        db=db,
        submission_id=submission.id,
        project_id=project_id,
        image_object_key=object_key,
    )

    return ImageUploadResponse(
        filename=file.filename,
        project_id=project_id,
        object_key=object_key,
        submission_id=submission.id,
    )


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
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No filename provided",
        )

    content_type = file.content_type or ""
    if content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: PDF, TXT. Got: {content_type}",
        )

    contents = await file.read()
    bucket = str(project_id)
    object_name = f"designs/{file.filename}"

    minio_client.upload_file(
        bucket=bucket,
        object_name=object_name,
        file_data=contents,
        content_type=content_type,
    )

    return UploadResponse(
        filename=file.filename,
        project_id=project_id,
        object_key=f"{bucket}/{object_name}",
    )


# -------------------------
# Downloads (Presigned URLs)
# -------------------------

def get_design_url(object_key: str, expires: int = 900) -> dict:
    # object_key format: "{project_id}/designs/{filename}"
    bucket, object_name = object_key.split("/", 1)
    url = minio_client.get_presigned_url(
        bucket=bucket,
        object_name=object_name,
        expires_seconds=expires,
    )
    return {"url": url, "expires_in": expires}


def get_image_url(object_key: str, expires: int = 900) -> dict:
    # object_key format: "{project_id}/images/{filename}"
    bucket, object_name = object_key.split("/", 1)
    url = minio_client.get_presigned_url(
        bucket=bucket,
        object_name=object_name,
        expires_seconds=expires,
    )
    return {"url": url, "expires_in": expires}