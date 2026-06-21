from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.v1.deps.auth_deps import get_current_active_user
from app.schemas.auth_schemas import (
    LoginRequest,
    PasswordChangeRequest,
    RefreshRequest,
    SignupRequest,
    TokenResponse,
)
from app.schemas.base_schemas import SuccessResponse
from app.services.auth_service import AuthService
from app.dependencies import get_auth_service

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


@router.post("/signup", response_model=TokenResponse)
async def signup(
    request: SignupRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    return await auth_service.signup(request)


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    return await auth_service.login(request)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    request: RefreshRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    return await auth_service.refresh_token(request.refresh_token)


@router.post("/logout", response_model=SuccessResponse)
async def logout() -> SuccessResponse:
    return SuccessResponse(message="Logged out successfully")


@router.patch("/password", response_model=SuccessResponse)
async def change_password(
    request: PasswordChangeRequest,
    user: dict = Depends(get_current_active_user),
    auth_service: AuthService = Depends(get_auth_service),
) -> SuccessResponse:
    await auth_service.change_password(user["id"], request.current_password, request.new_password)
    return SuccessResponse(message="Password changed successfully")
