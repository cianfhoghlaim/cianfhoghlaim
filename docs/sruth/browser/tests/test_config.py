"""Tests for BrowserConfig configuration."""

import os
from unittest.mock import patch

import pytest


class TestBrowserConfigDefaults:
    """Test BrowserConfig default values."""

    def test_default_cdp_url(self, monkeypatch):
        """Test default CDP URL is set correctly."""
        # Clear any env vars
        monkeypatch.delenv("BROWSER_CDP_URL", raising=False)

        from browser.core.config import BrowserConfig

        config = BrowserConfig()
        assert config.cdp_url == "ws://browser-grid:9222"

    def test_default_crawl4ai_url(self, monkeypatch):
        """Test default Crawl4AI URL is set correctly."""
        monkeypatch.delenv("BROWSER_CRAWL4AI_URL", raising=False)

        from browser.core.config import BrowserConfig

        config = BrowserConfig()
        assert config.crawl4ai_url == "http://crawl4ai:11235"

    def test_default_skyvern_url(self, monkeypatch):
        """Test default Skyvern URL is set correctly."""
        monkeypatch.delenv("BROWSER_SKYVERN_API_URL", raising=False)

        from browser.core.config import BrowserConfig

        config = BrowserConfig()
        assert config.skyvern_api_url == "http://skyvern:8000/api/v1"

    def test_default_circuit_breaker_settings(self, monkeypatch):
        """Test default circuit breaker configuration."""
        from browser.core.config import BrowserConfig

        config = BrowserConfig()
        assert config.circuit_failure_threshold == 3
        assert config.circuit_recovery_timeout == 30.0
        assert config.circuit_half_open_requests == 1

    def test_default_timeouts(self, monkeypatch):
        """Test default timeout values."""
        from browser.core.config import BrowserConfig

        config = BrowserConfig()
        assert config.navigation_timeout == 30.0
        assert config.extraction_timeout == 60.0
        assert config.interaction_timeout == 10.0

    def test_default_fallback_settings(self, monkeypatch):
        """Test default fallback configuration."""
        from browser.core.config import BrowserConfig

        config = BrowserConfig()
        assert config.fallback_enabled is True
        assert config.fallback_strategy == "cost"

    def test_default_feature_flags(self, monkeypatch):
        """Test default feature flags."""
        from browser.core.config import BrowserConfig

        config = BrowserConfig()
        assert config.enable_screenshot_cache is True
        assert config.enable_selector_cache is True
        assert config.enable_session_persistence is True

    def test_default_server_settings(self, monkeypatch):
        """Test default server configuration."""
        from browser.core.config import BrowserConfig

        config = BrowserConfig()
        assert config.server_host == "0.0.0.0"
        assert config.server_port == 3001


class TestBrowserConfigEnvOverrides:
    """Test BrowserConfig environment variable overrides."""

    def test_override_cdp_url(self, monkeypatch):
        """Test CDP URL can be overridden via env var."""
        monkeypatch.setenv("BROWSER_CDP_URL", "ws://custom-grid:9223")

        from browser.core.config import BrowserConfig

        config = BrowserConfig()
        assert config.cdp_url == "ws://custom-grid:9223"

    def test_override_crawl4ai_url(self, monkeypatch):
        """Test Crawl4AI URL can be overridden."""
        monkeypatch.setenv("BROWSER_CRAWL4AI_URL", "http://custom-crawl4ai:11236")

        from browser.core.config import BrowserConfig

        config = BrowserConfig()
        assert config.crawl4ai_url == "http://custom-crawl4ai:11236"

    def test_override_circuit_breaker_threshold(self, monkeypatch):
        """Test circuit breaker threshold can be overridden."""
        monkeypatch.setenv("BROWSER_CIRCUIT_FAILURE_THRESHOLD", "5")

        from browser.core.config import BrowserConfig

        config = BrowserConfig()
        assert config.circuit_failure_threshold == 5

    def test_override_recovery_timeout(self, monkeypatch):
        """Test circuit recovery timeout can be overridden."""
        monkeypatch.setenv("BROWSER_CIRCUIT_RECOVERY_TIMEOUT", "60.0")

        from browser.core.config import BrowserConfig

        config = BrowserConfig()
        assert config.circuit_recovery_timeout == 60.0

    def test_override_server_port(self, monkeypatch):
        """Test server port can be overridden."""
        monkeypatch.setenv("BROWSER_SERVER_PORT", "8080")

        from browser.core.config import BrowserConfig

        config = BrowserConfig()
        assert config.server_port == 8080

    def test_override_fallback_strategy(self, monkeypatch):
        """Test fallback strategy can be overridden."""
        monkeypatch.setenv("BROWSER_FALLBACK_STRATEGY", "speed")

        from browser.core.config import BrowserConfig

        config = BrowserConfig()
        assert config.fallback_strategy == "speed"

    def test_disable_fallback(self, monkeypatch):
        """Test fallback can be disabled."""
        monkeypatch.setenv("BROWSER_FALLBACK_ENABLED", "false")

        from browser.core.config import BrowserConfig

        config = BrowserConfig()
        assert config.fallback_enabled is False


class TestBrowserConfigPaidServices:
    """Test BrowserConfig paid service detection."""

    def test_has_browserbase_with_both_keys(self, monkeypatch):
        """Test Browserbase detection with both API key and project ID."""
        monkeypatch.setenv("BROWSER_BROWSERBASE_API_KEY", "test-key")
        monkeypatch.setenv("BROWSER_BROWSERBASE_PROJECT_ID", "test-project")

        from browser.core.config import BrowserConfig

        config = BrowserConfig()
        assert config.has_browserbase is True

    def test_has_browserbase_without_key(self, monkeypatch):
        """Test Browserbase detection without API key."""
        monkeypatch.delenv("BROWSER_BROWSERBASE_API_KEY", raising=False)
        monkeypatch.setenv("BROWSER_BROWSERBASE_PROJECT_ID", "test-project")

        from browser.core.config import BrowserConfig

        config = BrowserConfig()
        assert config.has_browserbase is False

    def test_has_browserbase_without_project(self, monkeypatch):
        """Test Browserbase detection without project ID."""
        monkeypatch.setenv("BROWSER_BROWSERBASE_API_KEY", "test-key")
        monkeypatch.delenv("BROWSER_BROWSERBASE_PROJECT_ID", raising=False)

        from browser.core.config import BrowserConfig

        config = BrowserConfig()
        assert config.has_browserbase is False

    def test_has_firecrawl_with_key(self, monkeypatch):
        """Test Firecrawl detection with API key."""
        monkeypatch.setenv("BROWSER_FIRECRAWL_API_KEY", "test-fc-key")

        from browser.core.config import BrowserConfig

        config = BrowserConfig()
        assert config.has_firecrawl is True

    def test_has_firecrawl_without_key(self, monkeypatch):
        """Test Firecrawl detection without API key."""
        monkeypatch.delenv("BROWSER_FIRECRAWL_API_KEY", raising=False)

        from browser.core.config import BrowserConfig

        config = BrowserConfig()
        assert config.has_firecrawl is False

    def test_has_zai_with_key(self, monkeypatch):
        """Test Z.AI detection with API key."""
        monkeypatch.setenv("BROWSER_ZAI_API_KEY", "test-zai-key")

        from browser.core.config import BrowserConfig

        config = BrowserConfig()
        assert config.has_zai is True

    def test_has_zai_without_key(self, monkeypatch):
        """Test Z.AI detection without API key."""
        monkeypatch.delenv("BROWSER_ZAI_API_KEY", raising=False)

        from browser.core.config import BrowserConfig

        config = BrowserConfig()
        assert config.has_zai is False

    def test_has_gemini_with_key(self, monkeypatch):
        """Test Gemini detection with API key."""
        monkeypatch.setenv("BROWSER_GEMINI_API_KEY", "test-gemini-key")

        from browser.core.config import BrowserConfig

        config = BrowserConfig()
        assert config.has_gemini is True

    def test_has_gemini_without_key(self, monkeypatch):
        """Test Gemini detection without API key."""
        monkeypatch.delenv("BROWSER_GEMINI_API_KEY", raising=False)

        from browser.core.config import BrowserConfig

        config = BrowserConfig()
        assert config.has_gemini is False

    def test_has_paid_fallback_with_browserbase(self, monkeypatch):
        """Test paid fallback detection with Browserbase only."""
        monkeypatch.setenv("BROWSER_BROWSERBASE_API_KEY", "test-key")
        monkeypatch.setenv("BROWSER_BROWSERBASE_PROJECT_ID", "test-project")
        monkeypatch.delenv("BROWSER_FIRECRAWL_API_KEY", raising=False)
        monkeypatch.delenv("BROWSER_ZAI_API_KEY", raising=False)

        from browser.core.config import BrowserConfig

        config = BrowserConfig()
        assert config.has_paid_fallback is True

    def test_has_paid_fallback_with_firecrawl(self, monkeypatch):
        """Test paid fallback detection with Firecrawl only."""
        monkeypatch.delenv("BROWSER_BROWSERBASE_API_KEY", raising=False)
        monkeypatch.setenv("BROWSER_FIRECRAWL_API_KEY", "test-fc-key")
        monkeypatch.delenv("BROWSER_ZAI_API_KEY", raising=False)

        from browser.core.config import BrowserConfig

        config = BrowserConfig()
        assert config.has_paid_fallback is True

    def test_has_paid_fallback_with_zai(self, monkeypatch):
        """Test paid fallback detection with Z.AI only."""
        monkeypatch.delenv("BROWSER_BROWSERBASE_API_KEY", raising=False)
        monkeypatch.delenv("BROWSER_FIRECRAWL_API_KEY", raising=False)
        monkeypatch.setenv("BROWSER_ZAI_API_KEY", "test-zai-key")

        from browser.core.config import BrowserConfig

        config = BrowserConfig()
        assert config.has_paid_fallback is True

    def test_no_paid_fallback(self, monkeypatch):
        """Test no paid fallback when no services configured."""
        monkeypatch.delenv("BROWSER_BROWSERBASE_API_KEY", raising=False)
        monkeypatch.delenv("BROWSER_BROWSERBASE_PROJECT_ID", raising=False)
        monkeypatch.delenv("BROWSER_FIRECRAWL_API_KEY", raising=False)
        monkeypatch.delenv("BROWSER_ZAI_API_KEY", raising=False)

        from browser.core.config import BrowserConfig

        config = BrowserConfig()
        assert config.has_paid_fallback is False


class TestBrowserConfigZAI:
    """Test Z.AI specific configuration."""

    def test_zai_mode_default(self, monkeypatch):
        """Test default Z.AI mode."""
        from browser.core.config import BrowserConfig

        config = BrowserConfig()
        assert config.zai_mode == "ZAI"

    def test_zai_mode_zhipu(self, monkeypatch):
        """Test Z.AI mode can be set to ZHIPU."""
        monkeypatch.setenv("BROWSER_ZAI_MODE", "ZHIPU")

        from browser.core.config import BrowserConfig

        config = BrowserConfig()
        assert config.zai_mode == "ZHIPU"

    def test_zai_base_url_zai_mode(self, monkeypatch):
        """Test Z.AI base URL in ZAI mode."""
        monkeypatch.setenv("BROWSER_ZAI_MODE", "ZAI")

        from browser.core.config import BrowserConfig

        config = BrowserConfig()
        assert config.zai_base_url == "https://api.z.ai/v1"

    def test_zai_base_url_zhipu_mode(self, monkeypatch):
        """Test Z.AI base URL in ZHIPU mode."""
        monkeypatch.setenv("BROWSER_ZAI_MODE", "ZHIPU")

        from browser.core.config import BrowserConfig

        config = BrowserConfig()
        assert config.zai_base_url == "https://open.bigmodel.cn/api/paas/v4"

    def test_zai_default_model(self, monkeypatch):
        """Test default GLM model."""
        from browser.core.config import BrowserConfig

        config = BrowserConfig()
        assert config.zai_glm_model == "glm-4.6v"


class TestBrowserConfigRestate:
    """Test Restate durable execution configuration."""

    def test_restate_default_urls(self, monkeypatch):
        """Test default Restate URLs."""
        from browser.core.config import BrowserConfig

        config = BrowserConfig()
        assert config.restate_url == "http://restate:8080"
        assert config.restate_admin_url == "http://restate:9070"

    def test_has_restate_enabled(self, monkeypatch):
        """Test Restate detection when enabled."""
        monkeypatch.setenv("BROWSER_ENABLE_DURABLE_EXECUTION", "true")
        monkeypatch.setenv("BROWSER_RESTATE_URL", "http://restate:8080")

        from browser.core.config import BrowserConfig

        config = BrowserConfig()
        assert config.has_restate is True

    def test_has_restate_disabled(self, monkeypatch):
        """Test Restate detection when disabled."""
        monkeypatch.setenv("BROWSER_ENABLE_DURABLE_EXECUTION", "false")

        from browser.core.config import BrowserConfig

        config = BrowserConfig()
        assert config.has_restate is False

    def test_human_approval_default(self, monkeypatch):
        """Test human approval default settings."""
        from browser.core.config import BrowserConfig

        config = BrowserConfig()
        assert config.enable_human_approval is False
        assert config.approval_timeout_minutes == 5


class TestBrowserConfigConvex:
    """Test Convex real-time UI state configuration."""

    def test_convex_default_url(self, monkeypatch):
        """Test default Convex URL."""
        from browser.core.config import BrowserConfig

        config = BrowserConfig()
        assert config.convex_url == "http://convex-backend:3210"

    def test_has_convex_enabled(self, monkeypatch):
        """Test Convex detection when enabled."""
        monkeypatch.setenv("BROWSER_ENABLE_CONVEX_THREADS", "true")
        monkeypatch.setenv("BROWSER_CONVEX_URL", "http://convex:3210")

        from browser.core.config import BrowserConfig

        config = BrowserConfig()
        assert config.has_convex is True

    def test_has_convex_disabled(self, monkeypatch):
        """Test Convex detection when disabled."""
        monkeypatch.setenv("BROWSER_ENABLE_CONVEX_THREADS", "false")

        from browser.core.config import BrowserConfig

        config = BrowserConfig()
        assert config.has_convex is False

    def test_convex_max_parallelism(self, monkeypatch):
        """Test Convex max parallelism setting."""
        monkeypatch.setenv("BROWSER_CONVEX_MAX_PARALLELISM", "10")

        from browser.core.config import BrowserConfig

        config = BrowserConfig()
        assert config.convex_max_parallelism == 10


class TestBrowserConfigLLM:
    """Test LLM provider configuration."""

    def test_default_llm_provider(self, monkeypatch):
        """Test default LLM provider."""
        from browser.core.config import BrowserConfig

        config = BrowserConfig()
        assert config.llm_provider == "openai/gpt-4o"

    def test_default_llm_fallback_order(self, monkeypatch):
        """Test default LLM fallback order."""
        from browser.core.config import BrowserConfig

        config = BrowserConfig()
        assert config.llm_fallback_order == ["glm-4.6v", "gemini-2.0-flash", "openai/gpt-4o"]

    def test_visual_healing_enabled(self, monkeypatch):
        """Test visual healing is enabled by default."""
        from browser.core.config import BrowserConfig

        config = BrowserConfig()
        assert config.enable_visual_healing is True
        assert config.visual_healing_model == "glm-4.6v"


class TestGetConfigCaching:
    """Test get_config caching behavior."""

    def test_get_config_returns_instance(self):
        """Test get_config returns a BrowserConfig instance."""
        from browser.core.config import get_config

        # Clear cache first
        get_config.cache_clear()

        config = get_config()
        from browser.core.config import BrowserConfig

        assert isinstance(config, BrowserConfig)

    def test_get_config_cached(self):
        """Test get_config returns cached instance."""
        from browser.core.config import get_config

        # Clear cache first
        get_config.cache_clear()

        config1 = get_config()
        config2 = get_config()

        # Should be the exact same object (cached)
        assert config1 is config2
