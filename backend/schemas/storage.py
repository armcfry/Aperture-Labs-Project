import uuid
from pydantic import BaseModel


class ImageUploadResponse(BaseModel):
    filename: str
    project_id: uuid.UUID
    object_key: str
    submission_id: uuid.UUID