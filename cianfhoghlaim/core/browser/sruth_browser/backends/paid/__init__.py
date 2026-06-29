"""Paid browser backend implementations.

Post-D.1: Z.AI Vision + Z.AI MCP are deprecated (not in the
5-backend final state per openspec/changes/2026-06-29-browser-stack-crawl4ai-refactor).
The zai_backend.py + zai_mcp_client.py files are kept for
backwards compat but are no longer re-exported from this module.
"""

from .firecrawl import FirecrawlBackend

# Z.AI Vision + Z.AI MCP are deprecated. Use the zai_backend module
# directly if you need them: `from cianfhoghlaim.core.browser.sruth_browser.backends.paid.zai_backend import ZAIVisionBackend`
# They will be removed in a follow-up commit.

__all__ = [
    "FirecrawlBackend",
]
