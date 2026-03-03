import uuid

from sqlalchemy.orm import Session

from db.models import Submission, Project
from schemas.submissions import SubmissionCreate, SubmissionUpdate
from schemas.enums import SubmissionStatus, SubmissionPassFail
from core import exceptions


def create_submission(
    db: Session,
    project_id: uuid.UUID,
    payload: SubmissionCreate,
) -> Submission:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise exceptions.ProjectNotFound()

    submission = Submission(
        id=uuid.uuid4(),
        project_id=project_id,
        submitted_by_user_id=payload.submitted_by_user_id,
        image_id=payload.image_id,
        status=SubmissionStatus.queued,
        pass_fail=SubmissionPassFail.unknown,
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)
    return submission


def get_submission(
    db: Session,
    project_id: uuid.UUID,
    submission_id: uuid.UUID,
) -> Submission:
    submission = db.query(Submission).filter(
        Submission.id == submission_id,
        Submission.project_id == project_id,
    ).first()
    if not submission:
        raise exceptions.SubmissionNotFound()
    return submission


def list_submissions_for_project(
    db: Session,
    project_id: uuid.UUID,
    status: str | None = None,
    pass_fail: str | None = None,
) -> list[Submission]:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise exceptions.ProjectNotFound()

    query = db.query(Submission).filter(Submission.project_id == project_id)

    if status is not None:
        query = query.filter(Submission.status == status)
    if pass_fail is not None:
        query = query.filter(Submission.pass_fail == pass_fail)

    return query.order_by(Submission.submitted_at.desc()).all()


def update_submission(
    db: Session,
    project_id: uuid.UUID,
    submission_id: uuid.UUID,
    payload: SubmissionUpdate,
) -> Submission:
    submission = get_submission(db, project_id, submission_id)

    if payload.status is not None:
        submission.status = payload.status
    if payload.pass_fail is not None:
        submission.pass_fail = payload.pass_fail
    if payload.anomaly_count is not None:
        submission.anomaly_count = payload.anomaly_count
    if payload.error_message is not None:
        submission.error_message = payload.error_message

    db.commit()
    db.refresh(submission)
    return submission


def delete_submission(
    db: Session,
    project_id: uuid.UUID,
    submission_id: uuid.UUID,
) -> None:
    submission = get_submission(db, project_id, submission_id)
    db.delete(submission)
    db.commit()


def retry_submission(
    db: Session,
    project_id: uuid.UUID,
    submission_id: uuid.UUID,
) -> Submission:
    submission = get_submission(db, project_id, submission_id)

    if submission.status not in (SubmissionStatus.failed, SubmissionStatus.complete_with_errors):
        raise exceptions.InvalidStateTransition(
            "Only failed or complete_with_errors submissions can be retried"
        )

    submission.status = SubmissionStatus.queued
    submission.pass_fail = SubmissionPassFail.unknown
    submission.anomaly_count = None
    submission.error_message = None
    db.commit()
    db.refresh(submission)
    return submission
