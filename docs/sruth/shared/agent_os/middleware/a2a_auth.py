"""A2A service-to-service authentication middleware.

For internal A2A calls between AgentOS instances, we use signed JWTs
to authenticate services. This prevents unauthorized access to agents
from outside the mesh.

The authentication flow:
1. Calling service signs JWT with shared secret
2. JWT includes: service_name, timestamp, optional user_id (passthrough)
3. Receiving service validates signature and expiry
4. If valid, request proceeds with service identity attached
"""

import time
from dataclasses import dataclass
from typing import Callable, Optional

import jwt
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import structlog

from ..config import get_config

logger = structlog.get_logger()


@dataclass
class ServiceIdentity:
    """Identity of a calling service in A2A communication."""

    service_name: str
    timestamp: float
    user_id: Optional[str] = None  # Passthrough user from original request

    @property
    def age_seconds(self) -> float:
        """How old is this token in seconds."""
        return time.time() - self.timestamp


# Header for service-to-service auth
SERVICE_TOKEN_HEADER = "X-Service-Token"
# Header for user passthrough
USER_PASSTHROUGH_HEADER = "X-User-ID"


def create_service_token(
    service_name: str,
    user_id: Optional[str] = None,
    secret_key: Optional[str] = None,
    expiry_seconds: int = 3600,
) -> str:
    """Create a signed JWT for service-to-service authentication.

    Args:
        service_name: Name of the calling service
        user_id: Optional user ID to pass through to the target service
        secret_key: Secret for signing (defaults to config)
        expiry_seconds: Token validity period

    Returns:
        Signed JWT string
    """
    if secret_key is None:
        secret_key = get_config().secret_key

    now = time.time()
    payload = {
        "service": service_name,
        "iat": now,
        "exp": now + expiry_seconds,
    }

    if user_id:
        payload["user_id"] = user_id

    return jwt.encode(
        payload,
        secret_key,
        algorithm="HS256",
    )


def verify_service_token(
    token: str,
    secret_key: Optional[str] = None,
) -> Optional[ServiceIdentity]:
    """Verify a service token and extract identity.

    Args:
        token: JWT token to verify
        secret_key: Secret for verification (defaults to config)

    Returns:
        ServiceIdentity if valid, None otherwise
    """
    if secret_key is None:
        secret_key = get_config().secret_key

    try:
        payload = jwt.decode(
            token,
            secret_key,
            algorithms=["HS256"],
        )

        return ServiceIdentity(
            service_name=payload["service"],
            timestamp=payload.get("iat", time.time()),
            user_id=payload.get("user_id"),
        )

    except jwt.ExpiredSignatureError:
        logger.warning("Service token expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning("Invalid service token", error=str(e))
        return None


class A2AAuthMiddleware(BaseHTTPMiddleware):
    """Middleware for A2A service-to-service authentication.

    This middleware:
    1. Checks for X-Service-Token header on A2A paths
    2. Validates the service JWT
    3. Populates request.state.service_identity
    4. Optionally requires service auth for all A2A paths

    A2A paths are identified by:
    - /a2a/agents/*
    - /a2a/teams/*
    - /a2a/workflows/*

    Usage:
        app.add_middleware(A2AAuthMiddleware)

        @app.post("/a2a/agents/{id}/v1/message:send")
        async def handle_a2a(request: Request):
            service = request.state.service_identity
            if service:
                logger.info(f"Call from {service.service_name}")
    """

    A2A_PATH_PREFIXES = [
        "/a2a/agents/",
        "/a2a/teams/",
        "/a2a/workflows/",
    ]

    def __init__(
        self,
        app,
        require_service_auth: bool = False,
        allowed_services: Optional[list[str]] = None,
    ):
        """Initialize A2A auth middleware.

        Args:
            app: ASGI application
            require_service_auth: If True, reject A2A calls without valid service token
            allowed_services: If set, only allow calls from these services
        """
        super().__init__(app)
        self.require_service_auth = require_service_auth
        self.allowed_services = allowed_services

    def _is_a2a_path(self, path: str) -> bool:
        """Check if path is an A2A endpoint."""
        return any(path.startswith(prefix) for prefix in self.A2A_PATH_PREFIXES)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and validate A2A service token."""
        path = request.url.path

        # Only process A2A paths
        if not self._is_a2a_path(path):
            return await call_next(request)

        # Check for service token
        token = request.headers.get(SERVICE_TOKEN_HEADER)
        service_identity = None

        if token:
            service_identity = verify_service_token(token)

            if service_identity:
                logger.info(
                    "A2A request authenticated",
                    calling_service=service_identity.service_name,
                    user_passthrough=service_identity.user_id,
                    token_age=f"{service_identity.age_seconds:.1f}s",
                    path=path,
                )

                # Check allowed services
                if self.allowed_services:
                    if service_identity.service_name not in self.allowed_services:
                        from fastapi.responses import JSONResponse

                        logger.warning(
                            "Service not in allowed list",
                            service=service_identity.service_name,
                            allowed=self.allowed_services,
                        )
                        return JSONResponse(
                            status_code=403,
                            content={
                                "error": "Service not authorized",
                                "detail": f"Service {service_identity.service_name} not in allowed list",
                            },
                        )
            else:
                logger.warning(
                    "Invalid A2A service token",
                    path=path,
                )

        # Attach service identity to request
        request.state.service_identity = service_identity

        # Also check for user passthrough header (for user context propagation)
        user_passthrough = request.headers.get(USER_PASSTHROUGH_HEADER)
        if user_passthrough and not service_identity:
            # User passthrough without service token - log but allow
            request.state.passthrough_user = user_passthrough
        elif service_identity and service_identity.user_id:
            request.state.passthrough_user = service_identity.user_id

        # Require service auth if configured
        if self.require_service_auth and not service_identity:
            from fastapi.responses import JSONResponse

            return JSONResponse(
                status_code=401,
                content={
                    "error": "Service authentication required",
                    "detail": "A2A endpoints require X-Service-Token header",
                },
            )

        return await call_next(request)


def get_service_identity(request: Request) -> Optional[ServiceIdentity]:
    """Dependency to get calling service identity.

    Usage:
        @app.post("/a2a/agents/{id}/v1/message:send")
        async def handle(service: Optional[ServiceIdentity] = Depends(get_service_identity)):
            if service:
                logger.info(f"Call from {service.service_name}")
    """
    return getattr(request.state, "service_identity", None)


def require_service_auth(request: Request) -> ServiceIdentity:
    """Dependency that requires A2A service authentication.

    Usage:
        @app.post("/internal/sync")
        async def sync(service: ServiceIdentity = Depends(require_service_auth)):
            return {"caller": service.service_name}
    """
    from fastapi import HTTPException

    service = get_service_identity(request)
    if not service:
        raise HTTPException(
            status_code=401,
            detail="A2A service authentication required",
        )
    return service
