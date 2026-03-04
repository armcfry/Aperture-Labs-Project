import uuid
from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserInfo(BaseModel):
    id: uuid.UUID
    email: EmailStr


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserInfo
