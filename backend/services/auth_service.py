from sqlalchemy.orm import Session

from db.models import User
from schemas.auth import LoginRequest, LoginResponse, UserInfo


def login(db: Session, payload: LoginRequest) -> LoginResponse:
    user = db.query(User).filter(User.email == payload.email).first()
    password_match = (user.password_hash == payload.password)

    # Only checking that the user exists and the password matched what's in the table for MVP time constraint
    if not user or not password_match:
        return LoginResponse(
            success=False,
            message="Invalid email or password",
        )

    return LoginResponse(
        success=True,
        user=UserInfo(id=user.id, email=user.email),
    )


def logout(db: Session) -> None:
    # MVP: no token invalidation needed
    pass
