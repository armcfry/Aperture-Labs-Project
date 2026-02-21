from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class UserInfo(BaseModel):
    username: str


class LoginResponse(BaseModel):
    success: bool
    user: UserInfo | None = None
    message: str | None = None
