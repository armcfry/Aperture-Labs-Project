import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, field_validator
from .enums import SubmissionStatus, SubmissionPassFail


class SubmissionBase(BaseModel):
    project_id: uuid.UUID
    image_id: str  # object key e.g. "{project_id}/images/filename.png"

    @field_validator("image_id")
    @classmethod
    def image_id_must_contain_slash(cls, v: str) -> str:
        if "/" not in v:
            raise ValueError("image_id must be in the format 'bucket/object_name'")
        return v


class SubmissionCreate(SubmissionBase):
    submitted_by_user_id: uuid.UUID


class SubmissionUpdate(BaseModel):
    status: SubmissionStatus | None = None
    pass_fail: SubmissionPassFail | None = None
    anomaly_count: int | None = None
    error_message: str | None = None


class SubmissionRead(SubmissionBase):
    id: uuid.UUID
    submitted_by_user_id: uuid.UUID
    submitted_at: datetime
    status: SubmissionStatus
    pass_fail: SubmissionPassFail
    anomaly_count: int | None
    error_message: str | None

    model_config = ConfigDict(from_attributes=True)