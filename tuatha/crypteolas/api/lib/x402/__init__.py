"""Stub: x402 payment middleware + helpers."""

from __future__ import annotations

from typing import Any

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


class X402Middleware(BaseHTTPMiddleware):
    """Stub x402 payment middleware. See tuatha/crypteolas/STATUS.md."""

    def __init__(self, app, **kwargs):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        return await call_next(request)


def get_network(name: str | None = None) -> dict[str, Any]:
    return {"name": name or "cronos", "status": "stub"}


def get_pay_to_address() -> str:
    return "0x0000000000000000000000000000000000000000"


def get_usage_stats(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return {}


async def decode_payment_header(_header: str | None) -> dict:
    return {}


def check_free_tier_available(*args: Any, **kwargs: Any) -> bool:
    return True


def create_payment_requirements(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return {}


__all__ = [
    "X402Middleware",
    "get_network",
    "get_pay_to_address",
    "get_usage_stats",
    "check_free_tier_available",
    "create_payment_requirements",
    "decode_payment_header",
]
