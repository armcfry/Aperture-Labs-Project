"""
GLaDOS - Aperture Labs FOD Detection API
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers.auth import router as auth_router
from routers.projects import router as projects_router
from routers.uploads import router as uploads_router
from routers.detection import router as detection_router
from routers.users import router as users_router
from routers.submissions import router as submissions_router
from routers.anomalies import router as anomalies_router
from routers.project_members import router as project_members_router

from core import exceptions
from core.exception_handlers import (
    project_not_found_handler,
    anomaly_not_found_handler,
    user_not_found_handler,
    member_not_found_handler,
    submission_not_found_handler,
    permission_denied_handler,
    conflict_error_handler,
    invalid_state_transition_handler,
)


app = FastAPI(
    title="GLaDOS - FOD Detection API",
    description="AI Anomaly Detection System for Foreign Object Debris",
    version="1.0.0",
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js default dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(projects_router)
app.include_router(project_members_router)
app.include_router(submissions_router)
app.include_router(anomalies_router)
app.include_router(uploads_router)
app.include_router(detection_router)

# Register global exception handlers
app.add_exception_handler(exceptions.ProjectNotFound, project_not_found_handler)
app.add_exception_handler(exceptions.AnomalyNotFound, anomaly_not_found_handler)
app.add_exception_handler(exceptions.UserNotFound, user_not_found_handler)
app.add_exception_handler(exceptions.MemberNotFound, member_not_found_handler)
app.add_exception_handler(exceptions.SubmissionNotFound, submission_not_found_handler)
app.add_exception_handler(exceptions.PermissionDenied, permission_denied_handler)
app.add_exception_handler(exceptions.ConflictError, conflict_error_handler)
app.add_exception_handler(exceptions.InvalidStateTransition, invalid_state_transition_handler)


@app.get("/")
async def root():
    return {
        "message": "Welcome to GLaDOS - FOD Detection API",
        "version": "1.0.0",
        "docs": "/docs",
    }