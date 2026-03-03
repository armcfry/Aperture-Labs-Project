import uuid
from db.models import User


def make_user(
    db,
    email: str = "test@example.com",
    password: str = "password123",
) -> User:
    user = User(
        id=uuid.uuid4(),
        email=email,
        password_hash=password, # no actual hashing happening, we know that the auth is a hoax for the MVP
    )
    db.add(user)
    db.flush()  # ← flush instead of commit
    db.refresh(user)
    return user