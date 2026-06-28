"""
SIWE (Sign-In With Ethereum) Authentication Routes.

Provides Web3 wallet authentication using EIP-4361 standard.
"""

import secrets
from datetime import UTC, datetime, timedelta

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
    player_id: str
    message: str


class SessionInfo(BaseModel):
    """Current session information."""

    address: str
    player_id: str
    authenticated: bool
    expires_at: str
    free_messages_remaining: int
    free_searches_remaining: int


@router.get("/nonce", response_model=NonceResponse)
async def get_nonce():
    """
    Get a nonce for SIWE authentication.

    Returns a unique nonce that must be included in the SIWE message.
    Nonces expire after 10 minutes.
    """
    nonce = secrets.token_urlsafe(32)
    expires_at = datetime.now(UTC) + timedelta(minutes=NONCE_EXPIRY_MINUTES)

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
        if datetime.now(UTC) > nonce_expiry:
            del _nonces[nonce]
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Nonce has expired",
            )

        # Verify the signature
        siwe_message.verify(request.signature)

        # Remove used nonce
        del _nonces[nonce]

        # Create session
        session_id = secrets.token_urlsafe(32)
        expires_at = datetime.now(UTC) + timedelta(hours=SESSION_DURATION_HOURS)
        address = siwe_message.address.lower()

        _sessions[session_id] = {
            "address": address,
            "player_id": f"player_{address[:10]}",
            "created_at": datetime.now(UTC).isoformat(),
            "expires_at": expires_at.isoformat(),
            "free_messages_used": 0,
            "free_searches_used": 0,
        }

        return AuthResponse(
            success=True,
            address=address,
            session_id=session_id,
            expires_at=expires_at.isoformat(),
            player_id=f"player_{address[:10]}",
            message="Fáilte! Welcome to Tuath!",
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

    if datetime.now(UTC) > expires_at:
        del _sessions[session_id]
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session has expired",
        )

    # Calculate remaining free usage
    free_messages = max(0, 5 - session.get("free_messages_used", 0))
    free_searches = max(0, 3 - session.get("free_searches_used", 0))

    return SessionInfo(
        address=session["address"],
        player_id=session["player_id"],
        authenticated=True,
        expires_at=session["expires_at"],
        free_messages_remaining=free_messages,
        free_searches_remaining=free_searches,
    )


@router.post("/logout/{session_id}")
async def logout(session_id: str):
    """End a session."""
    _sessions.pop(session_id, None)

    return {"success": True, "message": "Slán! Goodbye!"}


def _cleanup_expired_nonces():
    """Remove expired nonces."""
    now = datetime.now(UTC)
    expired = [n for n, exp in _nonces.items() if now > exp]
    for nonce in expired:
        del _nonces[nonce]


def get_session_from_header(session_id: str) -> dict | None:
    """Get session from session ID (for dependency injection)."""
    if session_id not in _sessions:
        return None

    session = _sessions[session_id]
    expires_at = datetime.fromisoformat(session["expires_at"])

    if datetime.now(UTC) > expires_at:
        del _sessions[session_id]
        return None

    return session


def increment_usage(session_id: str, usage_type: str):
    """Increment usage counter for a session."""
    if session_id in _sessions:
        key = f"free_{usage_type}_used"
        _sessions[session_id][key] = _sessions[session_id].get(key, 0) + 1


def check_free_usage(session_id: str, usage_type: str, limit: int) -> bool:
    """Check if session has free usage remaining."""
    if session_id not in _sessions:
        return False

    key = f"free_{usage_type}_used"
    used = _sessions[session_id].get(key, 0)
    return used < limit
