from uuid import UUID
from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from db.session import get_db
from schemas.projects import (
    ProjectCreate,
    ProjectUpdate,
    ProjectRead,
)
from services import project_service


router = APIRouter(
    prefix="/projects",
    tags=["Projects"],
)


# -------------------------
# Create Project
# -------------------------
@router.post(
    "",
    response_model=ProjectRead,
    status_code=status.HTTP_201_CREATED,
)
def create_project(
    payload: ProjectCreate,
    db: Session = Depends(get_db),
):
    return project_service.create_project(
        db=db,
        payload=payload,
    )


# -------------------------
# List Projects (Scoped)
# -------------------------
@router.get("", response_model=List[ProjectRead])
def list_projects(
    include_archived: bool = False,
    db: Session = Depends(get_db),
):
    return project_service.list_projects_for_user(
        db=db,
        include_archived=include_archived,
    )


# -------------------------
# Get Single Project
# -------------------------
@router.get("/{project_id}", response_model=ProjectRead)
def get_project(
    project_id: UUID,
    db: Session = Depends(get_db),
):
    return project_service.get_project(
        db=db,
        project_id=project_id,
    )


# -------------------------
# Update Project
# -------------------------
@router.patch("/{project_id}", response_model=ProjectRead)
def update_project(
    project_id: UUID,
    payload: ProjectUpdate,
    db: Session = Depends(get_db),
):
    return project_service.update_project(
        db=db,
        project_id=project_id,
        payload=payload,
    )


# -------------------------
# Delete Project
# -------------------------
@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: UUID,
    db: Session = Depends(get_db),
):
    project_service.delete_project(
        db=db,
        project_id=project_id,
    )


# -------------------------
# Archive Project
# -------------------------
@router.post("/{project_id}/archive", response_model=ProjectRead)
def archive_project(
    project_id: UUID,
    db: Session = Depends(get_db),
):
    return project_service.archive_project(
        db=db,
        project_id=project_id,
    )


# # -------------------------
# # Unarchive Project
# # -------------------------
# @router.post("/{project_id}/unarchive", response_model=ProjectRead)
# def unarchive_project(
#     project_id: UUID,
#     db: Session = Depends(get_db),
    
# ):
#     try:
#         return project_service.unarchive_project(
#             db=db,
#             project_id=project_id,
#         )
#     except exceptions.ProjectNotFound:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Project not found",
#         )
#     except exceptions.PermissionDenied:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Only the owner can unarchive this project",
#         )