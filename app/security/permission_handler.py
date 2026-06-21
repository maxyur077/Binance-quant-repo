from __future__ import annotations

from enum import Enum
from typing import Callable

from fastapi import Depends, HTTPException, Request, status


class Role(str, Enum):
    USER = "user"
    ADMIN = "admin"


def require_role(required: Role) -> Callable:
    async def _role_checker(request: Request) -> dict:
        user: dict | None = getattr(request.state, "user", None)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
            )
        user_role = user.get("role", Role.USER.value)
        if required == Role.ADMIN and user_role != Role.ADMIN.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin privileges required",
            )
        return user

    return _role_checker
