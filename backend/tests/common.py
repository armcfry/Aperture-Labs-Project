import uuid
from core.security import hash_password
from db.models import User


def make_user(
    db,
    email: str = "test@example.com",
    password: str = "password123",  # noqa: S107
) -> User:
    user = User(
        id=uuid.uuid4(),
        email=email,
        password_hash=hash_password(password),
    )
    db.add(user)
    db.flush()  # ← flush instead of commit
    db.refresh(user)
    return user
