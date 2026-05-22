"""Custom exceptions for browser agent stack."""

from .browser_types import BackendType


class BrowserAgentError(Exception):
    """Base exception for browser agent stack."""

    pass


class BackendError(BrowserAgentError):
    """Error from a browser backend."""

    def __init__(
        self,
        message: str,
        backend: BackendType,
        *,
        retryable: bool = True,
        status_code: int | None = None,
    ):
        super().__init__(message)
        self.backend = backend
        self.retryable = retryable
        self.status_code = status_code


class BackendTimeoutError(BackendError):
    """Timeout waiting for backend response."""

    def __init__(self, backend: BackendType, timeout_seconds: float):
        super().__init__(
            f"Backend {backend.value} timed out after {timeout_seconds}s",
            backend,
            retryable=True,
        )
        self.timeout_seconds = timeout_seconds


class CircuitOpenError(BrowserAgentError):
    """Circuit breaker is open, backend unavailable."""

    def __init__(self, backend: BackendType, recovery_in_seconds: float):
        super().__init__(
            f"Circuit open for {backend.value}, recovery in {recovery_in_seconds:.1f}s"
        )
        self.backend = backend
        self.recovery_in_seconds = recovery_in_seconds


class NavigationError(BrowserAgentError):
    """Failed to navigate to URL."""

    def __init__(self, url: str, reason: str, status_code: int | None = None):
        super().__init__(f"Navigation to {url} failed: {reason}")
        self.url = url
        self.reason = reason
        self.status_code = status_code


class ExtractionError(BrowserAgentError):
    """Failed to extract content from page."""

    def __init__(self, url: str, reason: str):
        super().__init__(f"Extraction from {url} failed: {reason}")
        self.url = url
        self.reason = reason


class SessionError(BrowserAgentError):
    """Error managing browser session."""

    def __init__(self, session_id: str, reason: str):
        super().__init__(f"Session {session_id} error: {reason}")
        self.session_id = session_id
        self.reason = reason


class SchemaValidationError(BrowserAgentError):
    """BAML schema validation failed."""

    def __init__(self, schema_name: str, errors: list[str]):
        super().__init__(f"Schema {schema_name} validation failed: {'; '.join(errors)}")
        self.schema_name = schema_name
        self.errors = errors


class FallbackExhaustedError(BrowserAgentError):
    """All backends (including fallbacks) have failed."""

    def __init__(self, operation: str, backends_tried: list[BackendType]):
        backend_names = [b.value for b in backends_tried]
        super().__init__(
            f"All backends exhausted for {operation}: tried {', '.join(backend_names)}"
        )
        self.operation = operation
        self.backends_tried = backends_tried
