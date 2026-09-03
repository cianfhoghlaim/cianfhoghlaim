"""TinyAuth middleware for extracting user from Traefik forward auth headers.

TinyAuth (with PocketID OIDC) passes authenticated user information through
headers after successful forward auth:
- Remote-User: Primary user identifier (username or email)
- X-Forwarded-User: Alternate user header
- Remote-Email: User's email address (if available)
- Remote-Groups: Comma-separated group memberships

This middleware extracts these headers and populates request.state.user.
"""

from dataclasses import dataclass, field
from typing import Callable, Optional

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import structlog

logger = structlog.get_logger()


@dataclass
class TinyAuthUser:
    """User information extracted from TinyAuth headers."""

    user_id: str
    email: Optional[str] = None
    groups: list[str] = field(default_factory=list)
    is_authenticated: bool = True

    @classmethod
    def anonymous(cls, ip_address: str = "unknown") -> "TinyAuthUser":
        """Create an anonymous user for unauthenticated requests."""
        return cls(
            user_id=f"anon:{ip_address}",
            is_authenticated=False,
        )

    @property
    def is_admin(self) -> bool:
        """Check if user is in admin group."""
        return "admin" in self.groups or "admins" in self.groups


class TinyAuthMiddleware(BaseHTTPMiddleware):
    """Middleware that extracts TinyAuth user from forward auth headers.

    After Traefik's forward auth with TinyAuth, the following headers are set:
    - Remote-User: authenticated username
    - Remote-Email: user email (if OIDC provides it)
    - Remote-Groups: comma-separated group list

    This middleware:
    1. Extracts user info from these headers
    2. Populates request.state.user with TinyAuthUser
    3. Logs authentication context

    Usage:
        app.add_middleware(TinyAuthMiddleware)

        @app.get("/protected")
        async def protected_route(request: Request):
            user = request.state.user
            if not user.is_authenticated:
                raise HTTPException(401)
            return {"user": user.user_id}
    """

    # Header names used by TinyAuth/Traefik
    USER_HEADERS = ["Remote-User", "X-Forwarded-User", "X-User"]
    EMAIL_HEADER = "Remote-Email"
    GROUPS_HEADER = "Remote-Groups"

    def __init__(
        self,
        app,
        require_auth: bool = False,
        skip_paths: Optional[list[str]] = None,
    ):
        """Initialize TinyAuth middleware.

        Args:
            app: ASGI application
            require_auth: If True, reject unauthenticated requests with 401
            skip_paths: Paths to skip authentication (e.g., health checks)
        """
        super().__init__(app)
        self.require_auth = require_auth
        self.skip_paths = skip_paths or [
            "/health",
            "/healthz",
            "/ready",
            "/metrics",
            "/.well-known",
            "/a2a",  # A2A endpoints handle their own auth
        ]

    def _should_skip(self, path: str) -> bool:
        """Check if path should skip authentication."""
        return any(path.startswith(skip) for skip in self.skip_paths)

    def _extract_user(self, request: Request) -> TinyAuthUser:
        """Extract user from TinyAuth headers."""
        # Try each user header in priority order
        user_id = None
        for header in self.USER_HEADERS:
            user_id = request.headers.get(header)
            if user_id:
                break

        if not user_id:
            # No authenticated user - create anonymous
            client_ip = request.client.host if request.client else "unknown"
            return TinyAuthUser.anonymous(client_ip)

        # Extract email
        email = request.headers.get(self.EMAIL_HEADER)

        # Extract groups (comma-separated)
        groups_header = request.headers.get(self.GROUPS_HEADER, "")
        groups = [g.strip() for g in groups_header.split(",") if g.strip()]

        return TinyAuthUser(
            user_id=user_id,
            email=email,
            groups=groups,
            is_authenticated=True,
        )

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and extract TinyAuth user."""
        path = request.url.path

        # Skip specified paths
        if self._should_skip(path):
            request.state.user = TinyAuthUser.anonymous()
            return await call_next(request)

        # Extract user from headers
        user = self._extract_user(request)
        request.state.user = user

        # Log authentication context
        if user.is_authenticated:
            logger.info(
                "Request authenticated",
                user_id=user.user_id,
                email=user.email,
                groups=user.groups,
                path=path,
                method=request.method,
            )
        else:
            logger.debug(
                "Unauthenticated request",
                path=path,
                method=request.method,
            )

        # Reject if auth required but not authenticated
        if self.require_auth and not user.is_authenticated:
            from fastapi.responses import JSONResponse

            return JSONResponse(
                status_code=401,
                content={
                    "error": "Authentication required",
                    "detail": "This endpoint requires TinyAuth authentication",
                },
            )

        return await call_next(request)


def get_current_user(request: Request) -> TinyAuthUser:
    """Dependency to get current authenticated user.

    Usage:
        from fastapi import Depends

        @app.get("/me")
        async def get_me(user: TinyAuthUser = Depends(get_current_user)):
            return {"user_id": user.user_id}
    """
    if not hasattr(request.state, "user"):
        client_ip = request.client.host if request.client else "unknown"
        return TinyAuthUser.anonymous(client_ip)
    return request.state.user


def require_authenticated(request: Request) -> TinyAuthUser:
    """Dependency that requires authenticated user.

    Usage:
        @app.get("/protected")
        async def protected(user: TinyAuthUser = Depends(require_authenticated)):
            return {"user_id": user.user_id}
    """
    from fastapi import HTTPException

    user = get_current_user(request)
    if not user.is_authenticated:
        raise HTTPException(
            status_code=401,
            detail="Authentication required",
        )
    return user


def require_admin(request: Request) -> TinyAuthUser:
    """Dependency that requires admin user.

    Usage:
        @app.get("/admin")
        async def admin_only(user: TinyAuthUser = Depends(require_admin)):
            return {"admin": user.user_id}
    """
    from fastapi import HTTPException

    user = require_authenticated(request)
    if not user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="Admin access required",
        )
    return user
