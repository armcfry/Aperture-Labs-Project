from pydantic import BaseModel, EmailStr

from schemas.users import UserIdentity


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserInfo(UserIdentity):
    """Auth response user shape; same as UserIdentity (id + email)."""
    pass


class LoginResponse(BaseModel):
    success: bool = True
    message: str | None = None
    access_token: str | None = None
    token_type: str = "bearer"
    user: UserInfo | None = None
