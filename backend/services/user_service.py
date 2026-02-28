import uuid
from datetime import datetime

from sqlalchemy.orm import Session
from passlib.context import CryptContext

from db.models import User
from schemas.users import UserCreate, UserUpdate
from core import exceptions

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_user(db: Session, payload: UserCreate) -> User:
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise exceptions.ConflictError("A user with this email already exists")

    user = User(
        id=uuid.uuid4(),
        email=payload.email,
        password_hash=pwd_context.hash(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user(db: Session, user_id: uuid.UUID) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise exceptions.UserNotFound()
    return user


def update_user(db: Session, user_id: uuid.UUID, payload: UserUpdate) -> User:
    user = get_user(db, user_id)

    if payload.email is not None:
        existing = db.query(User).filter(
            User.email == payload.email,
            User.id != user_id,
        ).first()
        if existing:
            raise exceptions.ConflictError("A user with this email already exists")
        user.email = payload.email

    if payload.password is not None:
        user.password_hash = pwd_context.hash(payload.password)

    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user_id: uuid.UUID) -> None:
    user = get_user(db, user_id)
    db.delete(user)
    db.commit()
