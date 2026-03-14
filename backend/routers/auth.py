from fastapi import APIRouter, Depends, status

from core.deps import get_current_user
from db.session import get_db
from schemas.auth import LoginRequest, LoginResponse
from services import auth_service
from sqlalchemy.orm import Session


router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


# -------------------------
# Login
# -------------------------
@router.post("/login", response_model=LoginResponse)
def login(
    payload: LoginRequest,
    db: Session = Depends(get_db),
):
    return auth_service.login(
        db=db,
        payload=payload,
    )


# -------------------------
# Logout
# -------------------------
@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(get_current_user)])
def logout():
    auth_service.logout()
