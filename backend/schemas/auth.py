import uuid
from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserInfo(BaseModel):
    id: uuid.UUID
    email: EmailStr


class LoginResponse(BaseModel):
    success: bool
    user: UserInfo | None = None
    message: str | None = None