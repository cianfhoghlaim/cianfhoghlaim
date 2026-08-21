"""
SIWE (Sign-In With Ethereum) Authentication Routes for Crypteolas.

Provides Web3 wallet authentication using EIP-4361 standard.
Supports multi-chain authentication for DeFi analytics.
"""

import secrets
from datetime import datetime, timedelta, timezone
from typing import Literal

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from siwe import SiweMessage, ValidationError

router = APIRouter()

# In-memory session storage (use Redis in production)
_nonces: dict[str, datetime] = {}
_sessions: dict[str, dict] = {}

# Configuration
SESSION_DURATION_HOURS = 24
NONCE_EXPIRY_MINUTES = 10

# Supported chains for Crypteolas
SUPPORTED_CHAINS = {
    1: "Ethereum",
    42161: "Arbitrum",
    10: "Optimism",
    137: "Polygon",
    8453: "Base",
    43114: "Avalanche",
    56: "BNB Chain",
}

# Tier limits
TIER_LIMITS = {
    "free": {"api_calls": 100, "analyses": 5, "protocols": 10},
    "pro": {"api_calls": 10000, "analyses": 100, "protocols": -1},  # -1 = unlimited
    "enterprise": {"api_calls": -1, "analyses": -1, "protocols": -1},
}


class NonceResponse(BaseModel):
    """Response containing authentication nonce."""

    nonce: str
    expires_at: str


class SIWERequest(BaseModel):
    """SIWE authentication request."""

    message: str
    signature: str


class AuthResponse(BaseModel):
    """Authentication response."""

    success: bool
    address: str
    session_id: str
    expires_at: str
    chain_id: int
    chain_name: str
    tier: Literal["free", "pro", "enterprise"]
    api_calls_remaining: int
    analyses_remaining: int
    message: str


class SessionInfo(BaseModel):
    """Current session information."""

    address: str
    chain_id: int
    chain_name: str
    authenticated: bool
    expires_at: str
    tier: Literal["free", "pro", "enterprise"]
    api_calls_remaining: int
    analyses_remaining: int
    protocols_tracked: int


@router.get("/nonce", response_model=NonceResponse)
async def get_nonce():
    """
    Get a nonce for SIWE authentication.

    Returns a unique nonce that must be included in the SIWE message.
    Nonces expire after 10 minutes.
    """
    nonce = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=NONCE_EXPIRY_MINUTES)

    _nonces[nonce] = expires_at

    # Clean up expired nonces
    _cleanup_expired_nonces()

    return NonceResponse(
        nonce=nonce,
        expires_at=expires_at.isoformat(),
    )


@router.post("/verify", response_model=AuthResponse)
async def verify_siwe(request: SIWERequest):
    """
    Verify a SIWE message and signature.

    Creates an authenticated session on success.
    Supports multi-chain authentication.
    """
    try:
        # Parse the SIWE message
        siwe_message = SiweMessage.from_message(request.message)

        # Verify the nonce exists and hasn't expired
        nonce = siwe_message.nonce
        if nonce not in _nonces:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired nonce",
            )

        nonce_expiry = _nonces[nonce]
        if datetime.now(timezone.utc) > nonce_expiry:
            del _nonces[nonce]
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Nonce has expired",
            )

        # Verify the signature
        siwe_message.verify(request.signature)

        # Remove used nonce
        del _nonces[nonce]

        # Extract chain ID
        chain_id = siwe_message.chain_id
        chain_name = SUPPORTED_CHAINS.get(chain_id, f"Chain {chain_id}")

        # Determine user tier (would check on-chain holdings in production)
        tier = _determine_user_tier(siwe_message.address)

        # Create session
        session_id = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=SESSION_DURATION_HOURS)
        address = siwe_message.address.lower()

        limits = TIER_LIMITS[tier]

        _sessions[session_id] = {
            "address": address,
            "chain_id": chain_id,
            "chain_name": chain_name,
            "tier": tier,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "expires_at": expires_at.isoformat(),
            "api_calls_used": 0,
            "analyses_used": 0,
            "protocols_tracked": [],
        }

        return AuthResponse(
            success=True,
            address=address,
            session_id=session_id,
            expires_at=expires_at.isoformat(),
            chain_id=chain_id,
            chain_name=chain_name,
            tier=tier,
            api_calls_remaining=limits["api_calls"],
            analyses_remaining=limits["analyses"],
            message=f"Connected to Crypteolas via {chain_name}",
        )

    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid SIWE message: {e!s}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication failed: {e!s}",
        )


@router.get("/session/{session_id}", response_model=SessionInfo)
async def get_session(session_id: str):
    """Get current session information."""
    if session_id not in _sessions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    session = _sessions[session_id]
    expires_at = datetime.fromisoformat(session["expires_at"])

    if datetime.now(timezone.utc) > expires_at:
        del _sessions[session_id]
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session has expired",
        )

    tier = session.get("tier", "free")
    limits = TIER_LIMITS[tier]

    # Calculate remaining usage
    api_remaining = _calculate_remaining(limits["api_calls"], session.get("api_calls_used", 0))
    analyses_remaining = _calculate_remaining(limits["analyses"], session.get("analyses_used", 0))

    return SessionInfo(
        address=session["address"],
        chain_id=session.get("chain_id", 1),
        chain_name=session.get("chain_name", "Ethereum"),
        authenticated=True,
        expires_at=session["expires_at"],
        tier=tier,
        api_calls_remaining=api_remaining,
        analyses_remaining=analyses_remaining,
        protocols_tracked=len(session.get("protocols_tracked", [])),
    )


@router.post("/logout/{session_id}")
async def logout(session_id: str):
    """End a session."""
    if session_id in _sessions:
        del _sessions[session_id]

    return {"success": True, "message": "Disconnected from Crypteolas"}


@router.get("/chains")
async def get_supported_chains():
    """Get list of supported chains."""
    return {
        "chains": [{"id": chain_id, "name": name} for chain_id, name in SUPPORTED_CHAINS.items()]
    }


def _cleanup_expired_nonces():
    """Remove expired nonces."""
    now = datetime.now(timezone.utc)
    expired = [n for n, exp in _nonces.items() if now > exp]
    for nonce in expired:
        del _nonces[nonce]


def _determine_user_tier(address: str) -> Literal["free", "pro", "enterprise"]:
    """
    Determine user tier based on on-chain data.

    In production, this would check:
    - Token holdings (e.g., governance tokens)
    - NFT ownership
    - Subscription smart contract
    """
    # For now, return free tier
    # TODO: Implement actual on-chain checks
    return "free"


def _calculate_remaining(limit: int, used: int) -> int:
    """Calculate remaining usage."""
    if limit == -1:  # Unlimited
        return -1
    return max(0, limit - used)


def get_session_from_header(session_id: str) -> dict | None:
    """Get session from session ID (for dependency injection)."""
    if session_id not in _sessions:
        return None

    session = _sessions[session_id]
    expires_at = datetime.fromisoformat(session["expires_at"])

    if datetime.now(timezone.utc) > expires_at:
        del _sessions[session_id]
        return None

    return session


def increment_usage(session_id: str, usage_type: str) -> bool:
    """
    Increment usage counter for a session.

    Returns True if within limits, False if limit exceeded.
    """
    if session_id not in _sessions:
        return False

    session = _sessions[session_id]
    tier = session.get("tier", "free")
    limits = TIER_LIMITS[tier]

    key = f"{usage_type}_used"
    limit_key = usage_type.replace("_used", "")

    current = session.get(key, 0)
    limit = limits.get(limit_key, 0)

    if limit != -1 and current >= limit:
        return False

    session[key] = current + 1
    return True


def check_usage_limit(session_id: str, usage_type: str) -> bool:
    """Check if session has usage remaining for given type."""
    if session_id not in _sessions:
        return False

    session = _sessions[session_id]
    tier = session.get("tier", "free")
    limits = TIER_LIMITS[tier]

    key = f"{usage_type}_used"
    limit = limits.get(usage_type, 0)

    if limit == -1:  # Unlimited
        return True

    used = session.get(key, 0)
    return used < limit


def track_protocol(session_id: str, protocol_id: str) -> bool:
    """
    Track a protocol for a session.

    Returns True if successful, False if limit exceeded.
    """
    if session_id not in _sessions:
        return False

    session = _sessions[session_id]
    tier = session.get("tier", "free")
    limits = TIER_LIMITS[tier]

    tracked = session.get("protocols_tracked", [])
    protocol_limit = limits.get("protocols", 0)

    if protocol_id in tracked:
        return True  # Already tracked

    if protocol_limit != -1 and len(tracked) >= protocol_limit:
        return False

    tracked.append(protocol_id)
    session["protocols_tracked"] = tracked
    return True
