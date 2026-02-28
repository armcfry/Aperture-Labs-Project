from sqlalchemy.orm import Session
from passlib.context import CryptContext

from db.models import User
from schemas.auth import LoginRequest, LoginResponse, UserInfo

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def login(db: Session, payload: LoginRequest) -> LoginResponse:
    user = db.query(User).filter(User.email == payload.email).first()

    if not user or not pwd_context.verify(payload.password, user.password_hash):
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
