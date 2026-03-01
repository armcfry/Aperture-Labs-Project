from fastapi import Request, status
from fastapi.responses import JSONResponse

from core import exceptions


def project_not_found_handler(request: Request, exc: exceptions.ProjectNotFound):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": exc.detail},
    )


def anomaly_not_found_handler(request: Request, exc: exceptions.AnomalyNotFound):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": exc.detail},
    )


def user_not_found_handler(request: Request, exc: exceptions.UserNotFound):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": exc.detail},
    )


def member_not_found_handler(request: Request, exc: exceptions.MemberNotFound):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": exc.detail},
    )


def submission_not_found_handler(request: Request, exc: exceptions.SubmissionNotFound):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": exc.detail},
    )


def permission_denied_handler(request: Request, exc: exceptions.PermissionDenied):
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={"detail": exc.detail},
    )


def conflict_error_handler(request: Request, exc: exceptions.ConflictError):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": exc.detail},
    )


def invalid_state_transition_handler(
    request: Request,
    exc: exceptions.InvalidStateTransition,
):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": exc.detail},
    )