"""
Payment API routes for Crypteolas.

Provides endpoints for:
- Pricing information
- Usage statistics
- Payment verification
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
import structlog

from ..lib.pricing_config import PRICING_CONFIG

# Import x402 payment utilities from local lib
from ..lib.x402 import (
    get_usage_stats,
    check_free_tier_available,
    create_payment_requirements,
)
from ..lib.x402.pricing import get_network, get_pay_to_address
from ..lib.x402.types import PricingTier


logger = structlog.get_logger()

router = APIRouter()


class PricingResponse(BaseModel):
    """Response with pricing information."""

    network: str
    pay_to: str
    endpoints: dict[str, dict]


class UsageResponse(BaseModel):
    """Response with usage statistics."""

    user_id: str
    today_total: int
    today_paid: int
    today_free: int
    total_spent_usd: str
    free_remaining: dict[str, int]


class FreeTierCheckResponse(BaseModel):
    """Response for free tier availability check."""

    endpoint: str
    available: bool
    free_daily_limit: int
    price_usd: str


@router.get("/pricing", response_model=PricingResponse)
async def get_pricing():
    """Get pricing information for all endpoints."""
    endpoints = {}
    for path, tier in PRICING_CONFIG.items():
        endpoints[path] = {
            "price_usd": str(tier.price_usd),
            "free_daily_limit": tier.free_daily_limit,
            "description": tier.description,
        }

    return PricingResponse(
        network=get_network(),
        pay_to=get_pay_to_address(),
        endpoints=endpoints,
    )


@router.get("/pricing/{endpoint:path}")
async def get_endpoint_pricing(endpoint: str):
    """Get pricing for a specific endpoint."""
    path = f"/{endpoint}" if not endpoint.startswith("/") else endpoint

    if path not in PRICING_CONFIG:
        raise HTTPException(status_code=404, detail="Endpoint not found")

    tier = PRICING_CONFIG[path]

    # Generate payment requirements for this endpoint
    requirements = create_payment_requirements(path, PRICING_CONFIG)

    return {
        "endpoint": path,
        "price_usd": str(tier.price_usd),
        "free_daily_limit": tier.free_daily_limit,
        "description": tier.description,
        "payment_requirements": requirements.model_dump(),
    }


@router.get("/usage", response_model=UsageResponse)
async def get_usage(request: Request):
    """Get usage statistics for the current user."""
    # Get user ID from request state or headers
    user_id = None
    if hasattr(request.state, "user") and request.state.user:
        user_id = request.state.user.get("id", request.state.user.get("address"))

    if not user_id:
        user_id = request.headers.get("X-WALLET")

    if not user_id:
        client_ip = request.client.host if request.client else "unknown"
        user_id = f"ip:{client_ip}"

    stats = get_usage_stats(user_id, PRICING_CONFIG)
    return UsageResponse(**stats)


@router.get("/free-tier/{endpoint:path}", response_model=FreeTierCheckResponse)
async def check_free_tier(endpoint: str, request: Request):
    """Check if free tier is available for an endpoint."""
    path = f"/{endpoint}" if not endpoint.startswith("/") else endpoint

    if path not in PRICING_CONFIG:
        raise HTTPException(status_code=404, detail="Endpoint not found")

    # Get user ID
    user_id = None
    if hasattr(request.state, "user") and request.state.user:
        user_id = request.state.user.get("id")

    if not user_id:
        user_id = request.headers.get("X-WALLET")

    if not user_id:
        client_ip = request.client.host if request.client else "unknown"
        user_id = f"ip:{client_ip}"

    tier = PRICING_CONFIG[path]
    available = check_free_tier_available(user_id, path, PRICING_CONFIG)

    return FreeTierCheckResponse(
        endpoint=path,
        available=available,
        free_daily_limit=tier.free_daily_limit,
        price_usd=str(tier.price_usd),
    )


@router.post("/verify")
async def verify_payment(request: Request):
    """Verify a payment for debugging/testing.

    Note: This endpoint is for development purposes.
    In production, payment verification happens in the middleware.
    """
    try:
        body = await request.json()
        payment_header = body.get("payment")

        if not payment_header:
            raise HTTPException(status_code=400, detail="Missing payment field")

        from ..lib.x402.middleware import decode_payment_header

        payment = decode_payment_header(payment_header)
        if not payment:
            raise HTTPException(status_code=400, detail="Invalid payment format")

        return {
            "valid": True,
            "network": payment.network.value,
            "scheme": payment.scheme,
            "from": payment.payload.authorization.from_,
            "value": payment.payload.authorization.value,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Payment verification error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
