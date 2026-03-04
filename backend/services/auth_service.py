from sqlalchemy.orm import Session

from core import exceptions, security
from db.models import User
from schemas.auth import LoginRequest, LoginResponse, UserInfo


def login(db: Session, payload: LoginRequest) -> LoginResponse:
    user = db.query(User).filter(User.email == payload.email).first()

    if not user or not security.verify_password(payload.password, user.password_hash):
        raise exceptions.Unauthorized("Invalid email or password")

    token = security.create_access_token(str(user.id))
    return LoginResponse(
        access_token=token,
        user=UserInfo(id=user.id, email=user.email),
    )


def logout() -> None:
    # Stateless JWTs: nothing to invalidate server-side.
    # Clients should discard the token on logout.
    pass
