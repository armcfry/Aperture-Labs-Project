import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from db.models import Project
from schemas.projects import ProjectCreate, ProjectUpdate
from core import exceptions
from services import minio_client


def create_project(db: Session, payload: ProjectCreate) -> Project:
    project_id = uuid.uuid4()

    project = Project(
        id=project_id,
        name=payload.name,
        description=payload.description,
        detector_version=payload.detector_version,
    )
    db.add(project)
    db.commit()
    db.refresh(project)

    # Create the MinIO bucket for this project
    minio_client.create_project_bucket(str(project_id))

    return project


def get_project(db: Session, project_id: uuid.UUID) -> Project:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise exceptions.ProjectNotFound()
    return project


def list_projects_for_user(
    db: Session,
    include_archived: bool = False,
) -> list[Project]:
    query = db.query(Project)
    if not include_archived:
        query = query.filter(Project.archived_at.is_(None))
    return query.order_by(Project.created_at.desc()).all()


def update_project(
    db: Session,
    project_id: uuid.UUID,
    payload: ProjectUpdate,
) -> Project:
    project = get_project(db, project_id)

    if payload.name is not None:
        project.name = payload.name
    if payload.description is not None:
        project.description = payload.description
    if payload.detector_version is not None:
        project.detector_version = payload.detector_version
    if payload.archived_at is not None:
        project.archived_at = payload.archived_at

    project.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(project)
    return project


def delete_project(db: Session, project_id: uuid.UUID) -> None:
    project = get_project(db, project_id)
    db.delete(project)
    db.commit()

    # Clean up the MinIO bucket and all its contents
    try:
        minio_client.delete_project_bucket(str(project_id))
    except Exception:
        # Don't fail the delete if MinIO cleanup fails
        pass


def archive_project(db: Session, project_id: uuid.UUID) -> Project:
    project = get_project(db, project_id)

    if project.archived_at is not None:
        raise exceptions.InvalidStateTransition("Project is already archived")

    project.archived_at = datetime.utcnow()
    project.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(project)
    return project


def unarchive_project(db: Session, project_id: uuid.UUID) -> Project:
    project = get_project(db, project_id)

    if project.archived_at is None:
        raise exceptions.InvalidStateTransition("Project is not archived")

    project.archived_at = None
    project.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(project)
    return project