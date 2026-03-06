from sqlalchemy.orm import Session

from core import exceptions, security
from db.models import User
from schemas.auth import LoginRequest, LoginResponse, UserInfo

_INVALID_CREDENTIALS = "Invalid email or password"


def login(db: Session, payload: LoginRequest) -> LoginResponse:
    user = db.query(User).filter(User.email == payload.email).first()

    if not user:
        raise exceptions.Unauthorized(_INVALID_CREDENTIALS)

    try:
        valid = security.verify_password(payload.password, user.password_hash)
    except Exception:
        return LoginResponse(success=False, message=_INVALID_CREDENTIALS)

    if not valid:
        raise exceptions.Unauthorized(_INVALID_CREDENTIALS)

    token = security.create_access_token(str(user.id))
    return LoginResponse(
        access_token=token,
        token_type="bearer",
        user=UserInfo(id=user.id, email=user.email),
    )


def logout() -> None:
    # Stateless JWTs: nothing to invalidate server-side.
    # Clients should discard the token on logout.
    pass
