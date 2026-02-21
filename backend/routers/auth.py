from fastapi import APIRouter
from schemas.auth import LoginRequest, LoginResponse, UserInfo

router = APIRouter(prefix="/api", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest) -> LoginResponse:
    return LoginResponse(
        success=True,
        user=UserInfo(username=request.username),
        message="Login successful",
    )
