import uuid
from datetime import datetime
from fastapi import APIRouter

from schemas.projects import (
    Project,
    ProjectCreate,
    ProjectListResponse,
    DesignSpec,
)

router = APIRouter(prefix="/api", tags=["projects"])

# In-memory project storage
_projects: dict[str, Project] = {}


def get_project(project_id: str) -> Project | None:
    return _projects.get(project_id)


def add_design_spec(project_id: str, spec: DesignSpec) -> None:
    if project_id in _projects:
        _projects[project_id].design_specs.append(spec)


@router.get("/projects/list", response_model=ProjectListResponse)
async def list_projects() -> ProjectListResponse:
    return ProjectListResponse(projects=list(_projects.values()))


@router.post("/projects/create", response_model=Project)
async def create_project(request: ProjectCreate) -> Project:
    project_id = str(uuid.uuid4())
    project = Project(
        id=project_id,
        name=request.name,
        created_at=datetime.now(),
        design_specs=[],
    )
    _projects[project_id] = project
    return project
