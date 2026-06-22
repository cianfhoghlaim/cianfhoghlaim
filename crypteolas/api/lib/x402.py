"""Stub: x402 payment middleware for FastAPI."""

from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class X402Middleware(BaseHTTPMiddleware):
    """Stub x402 payment middleware. See tuatha/crypteolas/STATUS.md."""

    def __init__(self, app, **kwargs):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        return await call_next(request)


async def decode_payment_header(_header: str | None) -> dict:
    """Stub: decode a payment header. Returns an empty dict."""
    return {}


__all__ = ["X402Middleware", "decode_payment_header"]
