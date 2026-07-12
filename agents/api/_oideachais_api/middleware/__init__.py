"""
FastAPI Middleware for Celtic Education Platform.

Available middleware:
- AuthMiddleware: BetterAuth session validation

Available dependencies:
- get_current_user: Get authenticated user (may be None)
- require_auth: Require authenticated user (raises 401)
- require_verified_email: Require verified email (raises 403)
"""
from .auth import (
    AUTH_VALIDATION_ENABLED,
    AuthMiddleware,
    User,
    UserContext,
    extract_user_from_headers,
    get_current_user,
    require_auth,
    require_verified_email,
)

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
