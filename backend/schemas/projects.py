import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ProjectBase(BaseModel):
    name: str
    description: str | None = None
    bucket_name: str | None = None
    object_key: uuid.UUID | None = None
    detector_version: str | None = None


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    bucket_name: str | None = None
    object_key: uuid.UUID | None = None
    detector_version: str | None = None
    archived_at: datetime | None = None


class ProjectRead(ProjectBase):
    id: uuid.UUID
    created_by_user_id: uuid.UUID | None
    created_at: datetime
    updated_at: datetime
    archived_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


# -------------------------
# Upload-related schemas
# -------------------------
class UploadResponse(BaseModel):
    filename: str
    project_id: uuid.UUID
    object_key: str