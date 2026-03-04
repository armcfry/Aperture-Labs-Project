import uuid

import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from core import exceptions, security
from db.models import User
from db.session import get_db

_bearer = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
    db: Session = Depends(get_db),
) -> User:
    try:
        payload = security.decode_access_token(credentials.credentials)
        user_id = uuid.UUID(payload["sub"])
    except (jwt.InvalidTokenError, KeyError, ValueError):
        raise exceptions.Unauthorized()

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise exceptions.Unauthorized()

    return user
