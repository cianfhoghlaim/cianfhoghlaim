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
    User,
    extract_user_from_headers,
    get_current_user,
    require_auth,
    require_verified_email,
    AuthMiddleware,
    UserContext,
    AUTH_VALIDATION_ENABLED,
)

__all__ = [
    "User",
    "extract_user_from_headers",
    "get_current_user",
    "require_auth",
    "require_verified_email",
    "AuthMiddleware",
    "UserContext",
    "AUTH_VALIDATION_ENABLED",
]
