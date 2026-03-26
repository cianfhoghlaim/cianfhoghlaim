"""Self-hosted browser backends ($0 cost).

Backends:
- CDPBackend: Direct Chrome DevTools Protocol via Playwright
- StagehandBackend: AI-powered browser interactions with natural language
- Crawl4AIBackend: High-throughput bulk extraction with LLM strategies
- SkyvernBackend: Vision-based navigation and form automation
"""

from .cdp_backend import CDPBackend
from .crawl4ai_backend import Crawl4AIBackend
from .skyvern_backend import SkyvernBackend
from .stagehand_backend import StagehandBackend

__all__ = [
    "CDPBackend",
    "SkyvernBackend",
    "Crawl4AIBackend",
    "StagehandBackend",
]
