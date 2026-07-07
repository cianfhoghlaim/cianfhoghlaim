"""Configuration for browser agent stack.

Extends FlowSettings from sruth.shared.config for consistency.
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class BrowserConfig(BaseSettings):
    """Browser agent configuration from environment variables."""

    model_config = SettingsConfigDict(
        env_prefix="BROWSER_",
        env_file=".env",
        extra="ignore",
    )

    # Self-hosted backend URLs
    cdp_url: str = Field(
        default="ws://browser-grid:9222",
        description="Chrome DevTools Protocol WebSocket URL",
    )
    skyvern_api_url: str = Field(
        default="http://skyvern:8000/api/v1",
        description="Skyvern API endpoint",
    )
    crawl4ai_url: str = Field(
        default="http://crawl4ai:11235",
        description="Crawl4AI API endpoint",
    )
    stagehand_url: str = Field(
        default="http://stagehand-mcp:3000",
        description="Stagehand MCP endpoint (legacy)",
    )
    stagehand_local_url: str = Field(
        default="http://localhost:3100",
        description="Stagehand local server URL",
    )
    stagehand_model: str = Field(
        default="openai/deepseek-v4-pro",
        description="Default model for Stagehand (routed through stagehand-proxy)",
    )
    stagehand_vision_model: str = Field(
        default="openai/deepseek-v4-pro",
        description="Vision model for Stagehand (routed through stagehand-proxy)",
    )
    stagehand_agent_model: str = Field(
        default="openai/deepseek-v4-pro",
        description="Model for Stagehand agent mode (routed through stagehand-proxy)",
    )
    stagehand_auto_fallback: bool = Field(
        default=True,
        description="Automatically fallback to Browserbase when anti-bot detected",
    )
    stagehand_headless: bool = Field(
        default=True,
        description="Run local browser in headless mode",
    )
    solver_url: str = Field(
        default="http://solver-service:5000/turnstile",
        description="Turnstile solver endpoint",
    )

    # Paid service API keys (fallback)
    browserbase_api_key: str | None = Field(
        default=None,
        description="Browserbase API key for fallback",
    )
    browserbase_project_id: str | None = Field(
        default=None,
        description="Browserbase project ID",
    )
    firecrawl_api_key: str | None = Field(
        default=None,
        description="Firecrawl API key for fallback",
    )

    # Z.AI Configuration
    zai_api_key: str | None = Field(
        default=None,
        description="Z.AI API key for GLM-4.6v and MCP services",
    )
    zai_mode: Literal["ZAI", "ZHIPU"] = Field(
        default="ZAI",
        description="Z.AI API mode (ZAI for z.ai, ZHIPU for zhipuai.com)",
    )
    zai_glm_model: str = Field(
        default="glm-4.6v",
        description="GLM vision model for visual grounding",
    )
    zai_vision_mcp_url: str = Field(
        default="https://api.z.ai/api/mcp/vision/mcp",
        description="Z.AI Vision MCP server URL",
    )
    zai_search_mcp_url: str = Field(
        default="https://api.z.ai/api/mcp/web_search_prime/mcp",
        description="Z.AI Search MCP server URL",
    )
    zai_reader_mcp_url: str = Field(
        default="https://api.z.ai/api/mcp/web_reader/mcp",
        description="Z.AI Reader MCP server URL",
    )
    zai_zread_mcp_url: str = Field(
        default="https://api.z.ai/api/mcp/zread/mcp",
        description="Z.AI Zread MCP server URL (GitHub docs)",
    )

    # Gemini Configuration
    gemini_api_key: str | None = Field(
        default=None,
        description="Google Gemini API key",
    )
    gemini_flash_model: str = Field(
        default="gemini-2.0-flash",
        description="Gemini Flash model for fast browsing",
    )
    gemini_pro_model: str = Field(
        default="gemini-2.0-pro",
        description="Gemini Pro model for planning",
    )

    # LLM configuration (routed through stagehand-proxy for OpenCode Go)
    openai_api_key: str | None = Field(default=None)
    anthropic_api_key: str | None = Field(default=None)
    opencode_go_api: str | None = Field(
        default=None,
        description="OpenCode Go API key for LLM calls through proxy",
    )
    llm_provider: str = Field(
        default="openai/deepseek-v4-pro",
        description="Default LLM provider for extraction (routed through stagehand-proxy)",
    )
    llm_fallback_order: list[str] = Field(
        default=["openai/deepseek-v4-pro", "openai/gpt-4o"],
        description="LLM fallback order for provider failures",
    )

    # Visual Healing Configuration
    enable_visual_healing: bool = Field(
        default=True,
        description="Enable visual healing for selector failures",
    )
    visual_healing_model: str = Field(
        default="glm-4.6v",
        description="Vision model for visual grounding in healing workflow",
    )

    # Circuit breaker settings
    circuit_failure_threshold: int = Field(
        default=3,
        description="Failures before opening circuit",
    )
    circuit_recovery_timeout: float = Field(
        default=30.0,
        description="Seconds before attempting recovery",
    )
    circuit_half_open_requests: int = Field(
        default=1,
        description="Requests to try in half-open state",
    )

    # Timeouts
    navigation_timeout: float = Field(
        default=30.0,
        description="Navigation timeout in seconds",
    )
    extraction_timeout: float = Field(
        default=60.0,
        description="Extraction timeout in seconds",
    )
    interaction_timeout: float = Field(
        default=10.0,
        description="UI interaction timeout in seconds",
    )

    # Fallback behavior
    fallback_enabled: bool = Field(
        default=True,
        description="Enable automatic fallback to paid services",
    )
    fallback_strategy: Literal["cost", "speed", "reliability"] = Field(
        default="cost",
        description="Fallback strategy: cost (cheapest), speed (fastest), reliability (most stable)",
    )

    # Server settings
    server_host: str = Field(default="0.0.0.0")
    server_port: int = Field(default=3001)

    # Feature flags
    enable_screenshot_cache: bool = Field(default=True)
    enable_selector_cache: bool = Field(default=True)
    enable_session_persistence: bool = Field(default=True)

    # Restate Configuration (Durable Execution)
    restate_url: str = Field(
        default="http://restate:8080",
        description="Restate ingress endpoint for durable execution",
    )
    restate_admin_url: str = Field(
        default="http://restate:9070",
        description="Restate admin API for health checks and deployments",
    )
    enable_durable_execution: bool = Field(
        default=True,
        description="Enable Restate durable execution for agent pipeline",
    )
    enable_human_approval: bool = Field(
        default=False,
        description="Enable human-in-the-loop approval gates via Restate awakeables",
    )
    approval_timeout_minutes: int = Field(
        default=5,
        description="Timeout in minutes for human approval requests",
    )

    # Convex Configuration (Real-Time UI State)
    convex_url: str = Field(
        default="http://convex-backend:3210",
        description="Convex backend API URL",
    )
    convex_deployment: str | None = Field(
        default=None,
        description="Convex deployment name (for cloud deployments)",
    )
    enable_convex_threads: bool = Field(
        default=True,
        description="Enable Convex for persistent thread/message history",
    )
    convex_max_parallelism: int = Field(
        default=5,
        description="Maximum parallel browser operations via Convex workpool",
    )

    @property
    def has_browserbase(self) -> bool:
        """Check if Browserbase is configured."""
        return bool(self.browserbase_api_key and self.browserbase_project_id)

    @property
    def has_firecrawl(self) -> bool:
        """Check if Firecrawl is configured."""
        return bool(self.firecrawl_api_key)

    @property
    def has_zai(self) -> bool:
        """Check if Z.AI is configured."""
        return bool(self.zai_api_key)

    @property
    def has_gemini(self) -> bool:
        """Check if Gemini is configured."""
        return bool(self.gemini_api_key)

    @property
    def has_paid_fallback(self) -> bool:
        """Check if any paid fallback is available."""
        return self.has_browserbase or self.has_firecrawl or self.has_zai

    @property
    def zai_base_url(self) -> str:
        """Get Z.AI API base URL based on mode."""
        if self.zai_mode == "ZHIPU":
            return "https://open.bigmodel.cn/api/paas/v4"
        return "https://api.z.ai/v1"

    @property
    def has_restate(self) -> bool:
        """Check if Restate is configured and enabled."""
        return self.enable_durable_execution and bool(self.restate_url)

    @property
    def has_convex(self) -> bool:
        """Check if Convex is configured and enabled."""
        return self.enable_convex_threads and bool(self.convex_url)


@lru_cache
def get_config() -> BrowserConfig:
    """Get cached configuration instance."""
    return BrowserConfig()
