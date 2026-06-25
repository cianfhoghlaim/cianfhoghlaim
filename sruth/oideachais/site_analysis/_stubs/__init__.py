"""
oideachais.site_analysis._stubs — Test-only payloads for the
firecrawl + browserbase MCP calls.

Used in CI under `USE_LOCAL_SCRAPES=true`. The payloads are
intentionally tiny and deterministic; their only job is to let
the asset graph be exercised end-to-end.
"""
from __future__ import annotations

from typing import Any

SAMPLE_FIRECRAWL_RESPONSE: dict[str, Any] = {
    "url": "https://example.com",
    "markdown": "# Example\n\nStub markdown from firecrawl stub.",
    "html": "<h1>Example</h1>",
    "links": ["https://example.com/about", "https://example.com/services"],
    "metadata": {
        "title": "Example site",
        "description": "Stub description",
        "language": "en",
    },
}

SAMPLE_BROWSERBASE_SCREENSHOT: dict[str, Any] = {
    "url": "https://example.com",
    "screenshot_path": "s3://lakehouse-site-analysis/stub/screenshots/example.png",
    "width": 1280,
    "height": 800,
    "full_page": True,
}
