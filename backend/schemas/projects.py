from pydantic import BaseModel
from datetime import datetime


class DesignSpec(BaseModel):
    filename: str
    object_key: str
    uploaded_at: datetime


class ProjectCreate(BaseModel):
    name: str


class Project(BaseModel):
    id: str
    name: str
    created_at: datetime
    design_specs: list[DesignSpec] = []


class ProjectListResponse(BaseModel):
    projects: list[Project]


class UploadResponse(BaseModel):
    filename: str
    project_id: str
    object_key: str
