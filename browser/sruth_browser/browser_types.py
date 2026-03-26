"""Type definitions for browser agent stack.

These types are shared across all flows that use browser capabilities.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field


class BackendType(str, Enum):
    """Available browser backends."""

    # Self-hosted (priority order, $0 cost)
    CDP_LOCAL = "cdp_local"
    SKYVERN_LOCAL = "skyvern_local"
    CRAWL4AI_LOCAL = "crawl4ai_local"
    STAGEHAND_LOCAL = "stagehand_local"

    # Paid fallback (cost-based order)
    FIRECRAWL_MCP = "firecrawl_mcp"
    BROWSERBASE_MCP = "browserbase_mcp"
    ZAI_VISION = "zai_vision"


class BrowserOperation(str, Enum):
    """Types of browser operations."""

    SCRAPE = "scrape"  # Extract content from page
    INTERACT = "interact"  # Click, type, scroll
    NAVIGATE = "navigate"  # Go to URL, back, forward
    RESEARCH = "research"  # Multi-page deep research
    EXTRACT = "extract"  # Structured data extraction
    EXTRACTION = "extraction"  # Alias for EXTRACT
    SCREENSHOT = "screenshot"  # Capture visual snapshot
    FORM = "form"  # Fill and submit forms


class ExtractionFormat(str, Enum):
    """Output formats for extraction."""

    MARKDOWN = "markdown"
    HTML = "html"
    RAW_HTML = "rawHtml"
    TEXT = "text"
    JSON = "json"
    STRUCTURED = "structured"  # Alias for JSON
    SCREENSHOT = "screenshot"
    LINKS = "links"
    SUMMARY = "summary"


class CircuitState(str, Enum):
    """Circuit breaker states."""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, rejecting requests
    HALF_OPEN = "half_open"  # Testing if recovered


class BackendHealth(BaseModel):
    """Health status of a backend."""

    backend: BackendType
    state: CircuitState = CircuitState.CLOSED
    failure_count: int = 0
    success_count: int = 0
    last_failure: datetime | None = None
    last_success: datetime | None = None
    last_error: str | None = None
    latency_ms: float | None = None

    @property
    def is_available(self) -> bool:
        """Check if backend is available for requests."""
        return self.state != CircuitState.OPEN


class SessionState(BaseModel):
    """Browser session state for migration between backends."""

    session_id: str
    backend: BackendType
    url: str | None = None
    cookies: list[dict[str, Any]] = Field(default_factory=list)
    local_storage: dict[str, str] = Field(default_factory=dict)
    session_storage: dict[str, str] = Field(default_factory=dict)
    viewport: dict[str, int] = Field(default_factory=lambda: {"width": 1920, "height": 1080})
    user_agent: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_activity: datetime = Field(default_factory=datetime.utcnow)


class NavigationResult(BaseModel):
    """Result of a navigation operation."""

    success: bool
    url: str
    title: str | None = None
    status_code: int | None = None
    backend_used: BackendType | None = None
    latency_ms: float = 0
    error: str | None = None


class ExtractionResult(BaseModel):
    """Result of an extraction operation."""

    success: bool
    url: str
    content: dict[str, Any]
    format: ExtractionFormat | str = ExtractionFormat.JSON
    backend_used: BackendType | None = None
    latency_ms: float = 0
    tokens_used: int | None = None
    error: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    data: dict[str, Any] | None = None  # Alias for content


class InteractionResult(BaseModel):
    """Result of a browser interaction."""

    success: bool
    action: str
    selector: str | None = None
    backend_used: BackendType | None = None
    latency_ms: float = 0
    screenshot_after: str | None = None
    error: str | None = None


class ScreenshotResult(BaseModel):
    """Result of a screenshot operation."""

    success: bool
    url: str
    image_data: str  # Base64 encoded
    format: Literal["png", "jpeg", "webp"] = "png"
    width: int
    height: int
    backend_used: BackendType | None = None
    latency_ms: float = 0
    error: str | None = None


class ResearchResult(BaseModel):
    """Result of a deep research operation."""

    success: bool
    query: str
    sources: list[dict[str, Any]]
    content: str
    backend_used: BackendType | None = None
    latency_ms: float = 0
    urls_visited: int = 0
    tokens_used: int | None = None
    error: str | None = None


class VisualGroundingResult(BaseModel):
    """Result of a visual grounding operation (GLM-4.6v)."""

    success: bool
    prompt: str
    coordinates: dict[str, float] | None = None  # {"x": float, "y": float}
    bounding_box: list[float] | None = None  # [xmin, ymin, xmax, ymax]
    confidence: float | None = None
    backend_used: BackendType | None = None
    latency_ms: float = 0
    tokens_used: int | None = None
    error: str | None = None


class VisionAnalysisResult(BaseModel):
    """Result of a vision analysis operation."""

    success: bool
    image_source: str
    analysis_type: str  # ui_to_artifact, ocr, error_diagnosis, diagram, chart, diff
    content: dict[str, Any]
    backend_used: BackendType | None = None
    latency_ms: float = 0
    tokens_used: int | None = None
    error: str | None = None


# Backend priority mapping for each operation type
BACKEND_PRIORITY: dict[BrowserOperation, list[BackendType]] = {
    BrowserOperation.SCRAPE: [
        BackendType.CRAWL4AI_LOCAL,
        BackendType.FIRECRAWL_MCP,
    ],
    BrowserOperation.INTERACT: [
        BackendType.CDP_LOCAL,
        BackendType.STAGEHAND_LOCAL,
        BackendType.BROWSERBASE_MCP,
    ],
    BrowserOperation.NAVIGATE: [
        BackendType.CDP_LOCAL,
        BackendType.SKYVERN_LOCAL,
        BackendType.BROWSERBASE_MCP,
    ],
    BrowserOperation.RESEARCH: [
        BackendType.FIRECRAWL_MCP,  # Firecrawl /agent is best for research
        BackendType.SKYVERN_LOCAL,
    ],
    BrowserOperation.EXTRACT: [
        BackendType.CRAWL4AI_LOCAL,
        BackendType.FIRECRAWL_MCP,
    ],
    BrowserOperation.EXTRACTION: [
        BackendType.STAGEHAND_LOCAL,
        BackendType.CRAWL4AI_LOCAL,
        BackendType.FIRECRAWL_MCP,
    ],
    BrowserOperation.SCREENSHOT: [
        BackendType.CDP_LOCAL,
        BackendType.BROWSERBASE_MCP,
        BackendType.ZAI_VISION,
    ],
    BrowserOperation.FORM: [
        BackendType.SKYVERN_LOCAL,  # Best for complex forms
        BackendType.STAGEHAND_LOCAL,
        BackendType.BROWSERBASE_MCP,
    ],
}

# Cost per operation (relative units, 0 = free)
BACKEND_COST: dict[BackendType, float] = {
    BackendType.CDP_LOCAL: 0.0,
    BackendType.SKYVERN_LOCAL: 0.0,
    BackendType.CRAWL4AI_LOCAL: 0.0,
    BackendType.STAGEHAND_LOCAL: 0.0,
    BackendType.FIRECRAWL_MCP: 1.0,  # Per-page cost
    BackendType.BROWSERBASE_MCP: 0.5,  # Session-based
    BackendType.ZAI_VISION: 0.1,  # Per-image
}
