"""x402 Payment Middleware for Crypteolas AgentOS.

Implements the x402 payment protocol for premium agent access.
Agents can be configured as free or paid, with optional free tier limits.

Reference: https://www.x402.org/
"""

from __future__ import annotations

import os
from collections import defaultdict
from datetime import datetime, timezone
from typing import Dict, Optional

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse


# Agent pricing configuration
# Paths relative to /a2a/agents/ or /v1/agents/
PROTECTED_AGENTS: Dict[str, dict] = {
    "code-analysis-agent": {
        "price_usd": 0.02,
        "description": "Smart contract and code analysis (Claude)",
        "free_tier": 3,  # 3 free calls per day
    },
    "graph-agent": {
        "price_usd": 0.005,
        "description": "Knowledge graph queries",
        "free_tier": 20,
    },
    "analytics-agent": {
        "price_usd": 0.01,
        "description": "DeFi analytics and metrics",
        "free_tier": 5,
    },
    "protocol-team": {
        "price_usd": 0.05,
        "description": "Full team analysis (all agents)",
        "free_tier": 2,
    },
}

FREE_AGENTS = [
    "documentation-agent",  # Unlimited free access
]


# Simple in-memory rate limiting (replace with Redis in production)
_usage_counts: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
_usage_dates: Dict[str, str] = {}


def _get_today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _get_user_id(request: Request) -> str:
    """Extract user ID from request headers or wallet."""
    # Check TinyAuth headers
    if user_id := request.headers.get("Remote-User"):
        return user_id
    # Check wallet header
    if wallet := request.headers.get("X-Wallet"):
        return wallet
    # Check service token
    if service := request.headers.get("X-Service-Name"):
        return f"service:{service}"
    # Default to IP
    return request.client.host if request.client else "anonymous"


def _get_free_usage(user_id: str, agent_name: str) -> int:
    """Get current free tier usage for user and agent."""
    today = _get_today()
    # Reset counts on new day
    if _usage_dates.get(user_id) != today:
        _usage_counts[user_id] = defaultdict(int)
        _usage_dates[user_id] = today
    return _usage_counts[user_id][agent_name]


def _increment_usage(user_id: str, agent_name: str) -> None:
    """Increment usage count."""
    _usage_counts[user_id][agent_name] += 1


def _extract_agent_name(path: str) -> Optional[str]:
    """Extract agent name from request path."""
    # /a2a/agents/<agent-name>/runs
    # /v1/agents/<agent-name>/runs
    parts = path.strip("/").split("/")
    if len(parts) >= 3 and parts[1] == "agents":
        return parts[2]
    # /a2a with agent in body - handled separately
    return None


class X402AgentMiddleware(BaseHTTPMiddleware):
    """Middleware for x402 payment protocol.

    Checks if agent requires payment and validates payment headers.
    Implements free tier with daily limits.

    Headers:
        X-PAYMENT: Signed payment authorization (EIP-3009)
        X-Wallet: User's wallet address for free tier tracking

    Responses:
        402 Payment Required: When free tier exhausted and no payment
        200: When free tier available or payment verified
    """

    def __init__(self, app, skip_verification: bool = False):
        super().__init__(app)
        self.skip_verification = skip_verification
        self.enabled = os.environ.get("X402_ENABLED", "true").lower() == "true"
        self.pay_to_address = os.environ.get("X402_PAY_TO_ADDRESS", "")
        self.network = os.environ.get("X402_NETWORK", "base")

    async def dispatch(self, request: Request, call_next):
        # Skip if disabled
        if not self.enabled:
            return await call_next(request)

        # Only check POST requests to agent endpoints
        if request.method != "POST":
            return await call_next(request)

        path = request.url.path

        # Skip non-agent paths
        if "/agents/" not in path and path != "/a2a":
            return await call_next(request)

        # Extract agent name
        agent_name = _extract_agent_name(path)
        if not agent_name:
            # For /a2a endpoint, would need to peek at body
            # For simplicity, allow through and check in handler
            return await call_next(request)

        # Check if agent is free
        if agent_name in FREE_AGENTS:
            return await call_next(request)

        # Check if agent requires payment
        agent_config = PROTECTED_AGENTS.get(agent_name)
        if not agent_config:
            # Unknown agent - allow through
            return await call_next(request)

        # Get user and check free tier
        user_id = _get_user_id(request)
        current_usage = _get_free_usage(user_id, agent_name)
        free_tier = agent_config.get("free_tier", 0)

        # Check free tier
        if current_usage < free_tier:
            # Free tier available
            _increment_usage(user_id, agent_name)
            response = await call_next(request)
            response.headers["X-Free-Tier-Remaining"] = str(free_tier - current_usage - 1)
            return response

        # Free tier exhausted - check for payment
        payment_header = request.headers.get("X-PAYMENT")

        if not payment_header:
            # Return 402 with payment requirements
            return JSONResponse(
                status_code=402,
                content={
                    "error": "Payment Required",
                    "message": f"Free tier exhausted ({free_tier} calls/day)",
                    "agent": agent_name,
                    "price_usd": agent_config["price_usd"],
                    "payment_requirements": {
                        "network": self.network,
                        "asset": "USDC",
                        "amount_usd": agent_config["price_usd"],
                        "pay_to": self.pay_to_address,
                        "protocol": "x402",
                    },
                },
                headers={
                    "X-Payment-Required": "true",
                    "X-Price-USD": str(agent_config["price_usd"]),
                },
            )

        # Verify payment
        if self.skip_verification:
            # Development mode - accept any payment header
            return await call_next(request)

        # TODO: Implement actual payment verification
        # This would verify the EIP-3009 signed authorization
        # and check that payment was made on-chain
        is_valid = await self._verify_payment(
            payment_header,
            agent_config["price_usd"],
            user_id,
        )

        if not is_valid:
            return JSONResponse(
                status_code=402,
                content={
                    "error": "Invalid Payment",
                    "message": "Payment verification failed",
                },
            )

        return await call_next(request)

    async def _verify_payment(
        self,
        payment_header: str,
        expected_amount: float,
        user_id: str,
    ) -> bool:
        """Verify x402 payment.

        TODO: Implement actual verification:
        1. Decode payment header (EIP-3009 authorization)
        2. Verify signature
        3. Check on-chain that transfer occurred
        4. Verify amount matches expected_amount
        """
        # Placeholder - always return True for now
        return True
