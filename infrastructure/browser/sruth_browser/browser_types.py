"""Type definitions for browser agent stack."""

from datetime import datetime
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field


class BackendType(str, Enum):
    CDP_LOCAL = "cdp_local"
    SKYVERN_LOCAL = "skyvern_local"
    CRAWL4AI_LOCAL = "crawl4ai_local"
    STAGEHAND_LOCAL = "stagehand_local"
    FIRECRAWL_MCP = "firecrawl_mcp"
    BROWSERBASE_MCP = "browserbase_mcp"
    ZAI_VISION = "zai_vision"


class BrowserOperation(str, Enum):
    SCRAPE = "scrape"
    INTERACT = "interact"
    NAVIGATE = "navigate"
    RESEARCH = "research"
    EXTRACT = "extract"
    EXTRACTION = "extraction"
    SCREENSHOT = "screenshot"
    FORM = "form"
    MAP_SITE = "map_site"
    VISUAL_GROUNDING = "visual_grounding"


class ExtractionFormat(str, Enum):
    MARKDOWN = "markdown"
    HTML = "html"
    RAW_HTML = "rawHtml"
    TEXT = "text"
    JSON = "json"
    STRUCTURED = "structured"
    SCREENSHOT = "screenshot"
    LINKS = "links"
    SUMMARY = "summary"


class CircuitState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class BackendHealth(BaseModel):
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
        return self.state != CircuitState.OPEN


class SessionState(BaseModel):
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
    success: bool
    url: str
    title: str | None = None
    status_code: int | None = None
    backend_used: BackendType | None = None
    latency_ms: float = 0
    error: str | None = None


class ExtractionResult(BaseModel):
    success: bool
    url: str
    content: dict[str, Any]
    format: ExtractionFormat | str = ExtractionFormat.JSON
    backend_used: BackendType | None = None
    latency_ms: float = 0
    tokens_used: int | None = None
    error: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    data: dict[str, Any] | None = None


class InteractionResult(BaseModel):
    success: bool
    action: str
    selector: str | None = None
    backend_used: BackendType | None = None
    latency_ms: float = 0
    screenshot_after: str | None = None
    error: str | None = None


class ScreenshotResult(BaseModel):
    success: bool
    url: str
    image_data: str
    format: Literal["png", "jpeg", "webp"] = "png"
    width: int
    height: int
    backend_used: BackendType | None = None
    latency_ms: float = 0
    error: str | None = None


class ResearchResult(BaseModel):
    success: bool
    query: str
    sources: list[dict[str, Any]]
    content: str
    backend_used: BackendType | None = None
    latency_ms: float = 0
    urls_visited: int = 0
    tokens_used: int | None = None
    error: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class VisualGroundingResult(BaseModel):
    success: bool
    prompt: str
    coordinates: dict[str, float] | None = None
    bounding_box: list[float] | None = None
    confidence: float | None = None
    backend_used: BackendType | None = None
    latency_ms: float = 0
    tokens_used: int | None = None
    error: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class VisionAnalysisResult(BaseModel):
    success: bool
    image_source: str
    analysis_type: str
    content: dict[str, Any]
    backend_used: BackendType | None = None
    latency_ms: float = 0
    tokens_used: int | None = None
    error: str | None = None


BACKEND_PRIORITY: dict[BrowserOperation, list[BackendType]] = {
    BrowserOperation.SCRAPE: [BackendType.CRAWL4AI_LOCAL, BackendType.FIRECRAWL_MCP],
    BrowserOperation.INTERACT: [BackendType.CDP_LOCAL, BackendType.STAGEHAND_LOCAL, BackendType.BROWSERBASE_MCP],
    BrowserOperation.NAVIGATE: [BackendType.CDP_LOCAL, BackendType.SKYVERN_LOCAL, BackendType.BROWSERBASE_MCP],
    BrowserOperation.RESEARCH: [BackendType.FIRECRAWL_MCP, BackendType.SKYVERN_LOCAL],
    BrowserOperation.EXTRACT: [BackendType.CRAWL4AI_LOCAL, BackendType.FIRECRAWL_MCP],
    BrowserOperation.EXTRACTION: [BackendType.STAGEHAND_LOCAL, BackendType.CRAWL4AI_LOCAL, BackendType.FIRECRAWL_MCP],
    BrowserOperation.SCREENSHOT: [BackendType.STAGEHAND_LOCAL, BackendType.CDP_LOCAL, BackendType.BROWSERBASE_MCP, BackendType.ZAI_VISION],
    BrowserOperation.FORM: [BackendType.SKYVERN_LOCAL, BackendType.STAGEHAND_LOCAL, BackendType.BROWSERBASE_MCP],
    BrowserOperation.MAP_SITE: [BackendType.CRAWL4AI_LOCAL, BackendType.FIRECRAWL_MCP],
    BrowserOperation.VISUAL_GROUNDING: [BackendType.STAGEHAND_LOCAL, BackendType.CDP_LOCAL, BackendType.BROWSERBASE_MCP, BackendType.ZAI_VISION],
}

BACKEND_COST: dict[BackendType, float] = {
    BackendType.CDP_LOCAL: 0.0,
    BackendType.SKYVERN_LOCAL: 0.0,
    BackendType.CRAWL4AI_LOCAL: 0.0,
    BackendType.STAGEHAND_LOCAL: 0.0,
    BackendType.FIRECRAWL_MCP: 1.0,
    BackendType.BROWSERBASE_MCP: 0.5,
    BackendType.ZAI_VISION: 0.1,
}
