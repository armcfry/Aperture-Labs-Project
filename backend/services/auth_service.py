from sqlalchemy.orm import Session

from db.models import User
from schemas.auth import LoginRequest, LoginResponse, UserInfo


def login(db: Session, payload: LoginRequest) -> LoginResponse:
    user = db.query(User).filter(User.email == payload.email).first()

    # Check user exists first, then verify password
    if not user or user.password_hash != payload.password:
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
