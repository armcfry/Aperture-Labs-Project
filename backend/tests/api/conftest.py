import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from core.deps import get_current_user
from db.models import User
from db.session import get_db
from main import app


def _make_fake_user(user_id=None, email="test@example.com"):
    user = MagicMock(spec=User)
    user.id = user_id or uuid.uuid4()
    user.email = email
    user.password_hash = "hashed"
    user.created_at = datetime.now(timezone.utc)
    user.updated_at = datetime.now(timezone.utc)
    return user


@pytest.fixture
def fake_user():
    return _make_fake_user()


@pytest.fixture
def auth_client(fake_user):
    """TestClient with authentication bypassed (get_current_user returns a fake user)."""

    def override_get_current_user():
        return fake_user

    def override_get_db():
        return MagicMock()

    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def unauth_client():
    """Unauthenticated TestClient with DB mocked out."""

    def override_get_db():
        return MagicMock()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()
