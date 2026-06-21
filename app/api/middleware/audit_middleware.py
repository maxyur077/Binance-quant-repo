from __future__ import annotations

import asyncio

from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.repositories.audit_repository import AuditRepository


class AuditMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI) -> None:
        super().__init__(app)
        self._repo = AuditRepository()

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        if request.method in ("POST", "PATCH", "PUT", "DELETE"):
            user_id = None
            if hasattr(request.state, "user") and request.state.user:
                user_id = request.state.user.get("id")

            asyncio.create_task(
                self._repo.log(
                    user_id=user_id,
                    action=f"{request.method} {request.url.path}",
                    resource=request.url.path.split("/")[-1] if "/" in request.url.path else "",
                    resource_id="",
                    details={"status_code": response.status_code},
                    ip_address=request.client.host if request.client else "",
                    user_agent=request.headers.get("user-agent", ""),
                )
            )

        return response


def setup_audit_middleware(app: FastAPI) -> None:
    app.add_middleware(AuditMiddleware)
