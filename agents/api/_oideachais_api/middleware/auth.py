"""
BetterAuth Session Middleware for FastAPI.

Validates session tokens from the TanStack Start web app via:
1. Header-based user identity (X-User-ID, X-User-Email)
2. Optional PostgreSQL session validation against BetterAuth tables

The web app (TanStack Start with BetterAuth) forwards user info in headers
after validating the session cookie. This middleware extracts that info
and makes it available to route handlers.

Usage:
    from middleware.auth import get_current_user, require_auth

    @router.get("/protected")
    async def protected_route(user: User = Depends(get_current_user)):
        return {"user_id": user.id}

    @router.get("/admin")
    async def admin_route(user: User = Depends(require_auth)):
        # Raises 401 if not authenticated
        return {"message": f"Hello {user.name}"}
"""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass

from fastapi import Depends, HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

logger = logging.getLogger(__name__)

# Environment configuration
DATABASE_URL = os.getenv("DATABASE_URL")
AUTH_VALIDATION_ENABLED = os.getenv("AUTH_VALIDATION_ENABLED", "false").lower() == "true"


# =============================================================================
# User Model
# =============================================================================


@dataclass
class User:
    """Authenticated user from BetterAuth session."""

    id: str
    email: str
    name: str | None = None
    image: str | None = None
    email_verified: bool = False
    created_at: str | None = None

    @property
    def is_authenticated(self) -> bool:
        """Check if user is authenticated."""
        return bool(self.id and self.email)


# =============================================================================
# Header-Based Authentication
# =============================================================================


def extract_user_from_headers(request: Request) -> User | None:
    """
    Extract user info from request headers.

    The TanStack Start web app forwards these headers after validating
    the session cookie via BetterAuth:
        - X-User-ID: User's unique identifier
        - X-User-Email: User's email address
        - X-User-Name: User's display name (optional)
        - X-User-Image: User's avatar URL (optional)

    Returns:
        User object if headers present, None otherwise
    """
    user_id = request.headers.get("X-User-ID")
    user_email = request.headers.get("X-User-Email")

    if not user_id or not user_email:
        return None

    return User(
        id=user_id,
        email=user_email,
        name=request.headers.get("X-User-Name"),
        image=request.headers.get("X-User-Image"),
    )


# =============================================================================
# Database Session Validation (Optional)
# =============================================================================


async def validate_session_in_database(user: User) -> bool:
    """
    Validate user exists in BetterAuth database tables.

    This is an optional additional validation step. By default, we trust
    the headers from the web app since it has already validated the session.

    Enable this for higher security by setting AUTH_VALIDATION_ENABLED=true
    and providing DATABASE_URL.

    Returns:
        True if user exists in database, False otherwise
    """
    if not AUTH_VALIDATION_ENABLED or not DATABASE_URL:
        return True  # Skip validation if not enabled

    try:
        import asyncpg

        # BetterAuth stores users in the 'user' table
        conn = await asyncpg.connect(DATABASE_URL)
        try:
            result = await conn.fetchrow(
                """
                SELECT id, email, "emailVerified"
                FROM "user"
                WHERE id = $1 AND email = $2
                """,
                user.id,
                user.email,
            )

            if result:
                user.email_verified = result["emailVerified"] is not None
                return True

            return False
        finally:
            await conn.close()

    except ImportError:
        logger.warning("asyncpg not installed, skipping database validation")
        return True
    except Exception as e:
        logger.warning(f"Database validation failed: {e}")
        return True  # Fail open to avoid blocking requests


# =============================================================================
# FastAPI Dependencies
# =============================================================================


async def get_current_user(request: Request) -> User | None:
    """
    FastAPI dependency to get the current authenticated user.

    Returns None if not authenticated.

    Usage:
        @router.get("/profile")
        async def profile(user: Optional[User] = Depends(get_current_user)):
            if user:
                return {"email": user.email}
            return {"anonymous": True}
    """
    # Check if user is already in request state (set by middleware)
    if hasattr(request.state, "user"):
        return request.state.user

    # Extract from headers
    user = extract_user_from_headers(request)

    if user and AUTH_VALIDATION_ENABLED:
        is_valid = await validate_session_in_database(user)
        if not is_valid:
            return None

    return user


async def require_auth(user: User | None = Depends(get_current_user)) -> User:
    """
    FastAPI dependency that requires authentication.

    Raises 401 if not authenticated.

    Usage:
        @router.get("/protected")
        async def protected(user: User = Depends(require_auth)):
            return {"user_id": user.id}
    """
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def require_verified_email(user: User = Depends(require_auth)) -> User:
    """
    FastAPI dependency that requires verified email.

    Raises 403 if email not verified.

    Usage:
        @router.get("/verified-only")
        async def verified_only(user: User = Depends(require_verified_email)):
            return {"verified_email": user.email}
    """
    if not user.email_verified:
        # Only check if database validation is enabled
        if AUTH_VALIDATION_ENABLED:
            raise HTTPException(
                status_code=403,
                detail="Email verification required",
            )
    return user


# =============================================================================
# Middleware (Optional - for setting request.state.user)
# =============================================================================


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware to extract user from headers and set on request.state.

    This is optional - you can use the dependencies directly without this.
    Adding this middleware makes the user available in request.state.user.

    Usage:
        from middleware.auth import AuthMiddleware

        app.add_middleware(AuthMiddleware)

        @router.get("/info")
        async def info(request: Request):
            user = request.state.user  # May be None
            return {"user": user.email if user else "anonymous"}
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Extract user from headers
        user = extract_user_from_headers(request)

        # Validate if enabled
        if user and AUTH_VALIDATION_ENABLED:
            is_valid = await validate_session_in_database(user)
            if not is_valid:
                user = None

        # Set user on request state
        request.state.user = user

        # Log request with user context
        if user:
            logger.debug(f"Request from user {user.email} ({user.id})")
        else:
            logger.debug("Anonymous request")

        return await call_next(request)


# =============================================================================
# Context Manager for User Context
# =============================================================================


class UserContext:
    """
    Context manager for accessing current user in non-request contexts.

    Useful for background tasks or callbacks where request is not available.

    Usage:
        with UserContext(user) as ctx:
            # Do something with ctx.user
            pass
    """

    _current: User | None = None

    def __init__(self, user: User | None):
        self._user = user
        self._previous = None

    def __enter__(self) -> UserContext:
        self._previous = UserContext._current
        UserContext._current = self._user
        return self

    def __exit__(self, *args):
        UserContext._current = self._previous

    @property
    def user(self) -> User | None:
        return self._user

    @classmethod
    def get_current(cls) -> User | None:
        """Get current user from context."""
        return cls._current


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "AUTH_VALIDATION_ENABLED",
    "AuthMiddleware",
    "User",
    "UserContext",
    "extract_user_from_headers",
    "get_current_user",
    "require_auth",
    "require_verified_email",
]
