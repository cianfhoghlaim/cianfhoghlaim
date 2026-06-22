"""Stub: x402 pricing helpers (subpackage)."""

from __future__ import annotations

from typing import Any


def get_network(name: str | None = None) -> dict[str, Any]:
    return {"name": name or "cronos", "status": "stub"}


def get_pay_to_address() -> str:
    return "0x0000000000000000000000000000000000000000"


__all__ = ["get_network", "get_pay_to_address"]
