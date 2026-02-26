from fastapi import Request, status
from fastapi.responses import JSONResponse

from core import exceptions


def project_not_found_handler(request: Request, exc: exceptions.ProjectNotFound):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": "Project not found"},
    )


def permission_denied_handler(request: Request, exc: exceptions.PermissionDenied):
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={"detail": "You do not have permission to perform this action"},
    )


def conflict_error_handler(request: Request, exc: exceptions.ConflictError):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": "Conflict error"},
    )


def invalid_state_transition_handler(
    request: Request,
    exc: exceptions.InvalidStateTransition,
):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": "Invalid state transition"},
    )