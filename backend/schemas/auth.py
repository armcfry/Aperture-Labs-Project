import uuid
from pydantic import BaseModel, EmailStr

from schemas.users import UserIdentity


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserInfo(UserIdentity):
    """Auth response user shape; same as UserIdentity (id + email)."""
    pass


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserInfo
