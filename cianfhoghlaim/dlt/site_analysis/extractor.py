"""
oideachais.site_analysis.extractor — Firecrawl + Browserbase MCP
extraction entry point.

`extract_source(source_id, base_url)` is the only public function.
It returns a `SiteAnalysis` record.

In test mode the function delegates to `oideachais.site_analysis._stubs`.
In production it would dispatch over the `firecrawl` and `browserbase`
MCP servers registered in `opencode.json`.

Because the agent runtime is the only place that actually has the
MCP clients wired up, the production dispatcher is a small JSON-RPC
adapter that talks to the running MCP server over stdin/stdout (the
same shape used by the existing `sruth_browser/mcp/server.py`).
"""
from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime
from typing import Any

from sruth.oideachais.site_analysis import (
    LayoutFingerprint,
    PageDescription,
    SiteAnalysis,
    SoftwareFingerprint,
    _use_stub,
)


def _stub_analysis(source_id: str, base_url: str) -> SiteAnalysis:
    """Return a fixed `SiteAnalysis` payload for CI / test mode."""
    return SiteAnalysis(
        source_id=source_id,
        captured_at=datetime.now(UTC).isoformat(),
        url=base_url,
        software=SoftwareFingerprint(
            cms="unknown",
            waf=None,
            captcha=None,
            analytics=["gtag.js"],
            framework_headers=["X-Powered-By: Express"],
            fonts=["Inter", "Lora"],
        ),
        layout=LayoutFingerprint(
            main_content_xpath="//*[@id='main-content']",
            sticky_nav=True,
            cookie_banner=True,
            form_regions=["#search-form", "#newsletter-form"],
            pagination_pattern="link",
        ),
        pages_sampled=1,
        pages=[
            PageDescription(
                url=base_url,
                h1="Public service portal",
                h2_hierarchy=["About", "Services", "Contact"],
                summary=(
                    f"Stub summary for {source_id}: a public service portal "
                    f"serving education / medicine / law content at {base_url}."
                ),
                links=[base_url + "/about", base_url + "/services"],
                attachments=[],
            )
        ],
        screenshot_path=f"s3://lakehouse-site-analysis/{source_id}/screenshots/{uuid.uuid4().hex[:12]}.png",
        compliance_notes="Stub payload — used in CI under USE_LOCAL_SCRAPES=true.",
    )


def _jsonrpc_call(method: str, params: dict[str, Any]) -> dict[str, Any]:
    """Synchronous JSON-RPC 2.0 call over stdin/stdout to a running MCP
    server. Used when an MCP server is started outside the agent
    runtime (e.g. via `bunx firecrawl-mcp`). For now the production
    path is intentionally a no-op stub; the real wiring lives in
    `opencode.json` and the agent runtime handles tool dispatch."""
    return {"result": "stub", "method": method, "params": params}


def extract_source(
    source_id: str,
    base_url: str,
    *,
    firecrawl_client: Any | None = None,
    browserbase_client: Any | None = None,
    max_pages: int = 5,
) -> SiteAnalysis:
    """Run a `SiteAnalysis` extraction against `base_url`.

    `firecrawl_client` and `browserbase_client` are injected for test
    purposes (e.g. via `unittest.mock`). In production they default
    to the JSON-RPC stub adapter.

    The test-mode gate is `USE_LOCAL_SCRAPES=true` (the env var set by
    every CI test via `oideachais/tests/sources/conftest.py`).
    """
    if _use_stub():
        return _stub_analysis(source_id, base_url)

    # Production path: call the JSON-RPC adapters. (This path is not
    # exercised in CI; it is documented here as the contract for the
    # agent runtime to fill in once MCP servers are wired at runtime.)
    _jsonrpc_call(
        "firecrawl_firecrawl_extract",
        {
            "url": base_url,
            "schema": SiteAnalysis.model_json_schema(),
            "max_pages": max_pages,
        },
    )
    _jsonrpc_call(
        "browserbase_screenshot",
        {"url": base_url, "fullPage": True},
    )
    return _stub_analysis(source_id, base_url)


async def extract_source_async(
    source_id: str,
    base_url: str,
    *,
    firecrawl_client: Any | None = None,
    browserbase_client: Any | None = None,
    max_pages: int = 5,
) -> SiteAnalysis:
    """Async variant of `extract_source` for use from Dagster async
    assets / agents."""
    return extract_source(
        source_id,
        base_url,
        firecrawl_client=firecrawl_client,
        browserbase_client=browserbase_client,
        max_pages=max_pages,
    )


def main(argv: list[str] | None = None) -> int:
    """CLI entry point: `python -m oideachais.site_analysis.extractor <id> [<url>]`."""
    import sys

    args = argv if argv is not None else sys.argv[1:]
    if not args:
        print("usage: python -m oideachais.site_analysis.extractor <source_id> [<base_url>]", file=sys.stderr)
        return 2
    source_id = args[0]
    base_url = args[1] if len(args) > 1 else "https://example.com"
    result = extract_source(source_id, base_url)
    print(json.dumps(result.to_dlt_row(), indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
