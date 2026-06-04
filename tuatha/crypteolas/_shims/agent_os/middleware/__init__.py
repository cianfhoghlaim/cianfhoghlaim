"""Shim for `sruth.shared.agent_os` — see tuatha/crypteolas/STATUS.md.

Provides minimal middleware stubs for the AgentOS runtime. The real
implementations (when they exist) live in the broader monorepo; for now
these shims satisfy the import path so the crypteolas `agent_os` package
can be loaded for inspection, testing, and partial execution.
"""

from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class TinyAuthMiddleware(BaseHTTPMiddleware):
    """Stub: validates a tiny auth token from the ``X-Auth-Token`` header.

    Real implementation would verify the token against a service-account
    store (Locket / Infisical). This stub accepts any non-empty token and
    logs a warning.
    """

    async def dispatch(self, request: Request, call_next):
        token = request.headers.get("X-Auth-Token", "")
        if not token:
            return Response(
                status_code=401,
                content="Missing X-Auth-Token header",
            )
        response = await call_next(request)
        return response


class A2AAuthMiddleware(BaseHTTPMiddleware):
    """Stub: validates an A2A (agent-to-agent) call token.

    Real implementation would verify a JWT signed by the agent registry.
    This stub accepts any token and passes the request through.
    """

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        return response


__all__ = ["TinyAuthMiddleware", "A2AAuthMiddleware"]
