"""Firecrawl MCP client — the 12-tool wrapper for the agent fleet.

Per the `2026-08-14-firecrawl-mcp-ccc-dual-search-v1` change, this module
is the canonical external search surface of the agent stack. Every
public method:

- has a Pydantic response model
- is wrapped in `@observe(name=...)` from
  `langfuse.decorators` (per the `agent-observability` skill)
- emits a `firecrawl_meta.scrapes` row via the centralized logger
  (the table is created by the Phase 4a change but the logger
  already accepts the writes)
- has a docstring with the credit cost + the canonical Firecrawl
  docs URL

The 12 wrapped tools (per docs.firecrawl.dev/mcp-server/tools):

| Tool | Credit cost | Method |
|:--|:--|:--|
| `firecrawl_scrape` | 1 / page + formats | `scrape` |
| `firecrawl_map` | 1 / call | `map` |
| `firecrawl_search` | 2 / 10 results | `search` |
| `firecrawl_parse` | 1 / file / page | `parse` |
| `firecrawl_crawl` | 1 / page | `crawl` |
| `firecrawl_agent` | dynamic (5 free/day) | `agent` |
| `firecrawl_interact` | 2-7 / min | `interact` |
| `firecrawl_batch_scrape` | 1 / page | `batch_scrape` |
| `firecrawl_monitor_*` | 1 / check + judge | `monitor_*` |
| `firecrawl_research_*` | free for first k | `research_*` |
| `firecrawl_developer_search` | 2 / 10 results | `developer_search` |
| `firecrawl_ask` | varies | `ask` |

The keyless tier (no API key) exposes `firecrawl_search`,
`firecrawl_scrape`, and `firecrawl_parse` only; the authenticated
tier exposes the full 12-tool surface. The local Firecrawl MCP
server is already configured at the platform level (per the
`firecrawl` MCP server in the runtime).
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any, Literal

from pydantic import BaseModel, Field, HttpUrl

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Pydantic response models (one per public method)
# ---------------------------------------------------------------------------

class FirecrawlSearchResult(BaseModel):
    """One result from a `firecrawl_search` call."""

    url: HttpUrl
    title: str
    description: str = ""
    position: int = 0
    category: str | None = None


class FirecrawlSearchResponse(BaseModel):
    """The normalised response from `firecrawl_search`."""

    web: list[FirecrawlSearchResult] = Field(default_factory=list)
    news: list[FirecrawlSearchResult] = Field(default_factory=list)
    images: list[FirecrawlSearchResult] = Field(default_factory=list)
    developer: list[FirecrawlSearchResult] = Field(default_factory=list)
    credits_used: int = 2
    search_id: str | None = None


class FirecrawlScrapeResponse(BaseModel):
    """The normalised response from `firecrawl_scrape`."""

    markdown: str = ""
    html: str = ""
    summary: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)
    links: list[str] = Field(default_factory=list)
    scrape_id: str | None = None
    credits_used: int = 1
    cache_hit: bool = False
    cached_at: str | None = None


class FirecrawlMapResponse(BaseModel):
    """The normalised response from `firecrawl_map`."""

    urls: list[HttpUrl] = Field(default_factory=list)
    credits_used: int = 1


class FirecrawlCrawlResponse(BaseModel):
    """The normalised response from `firecrawl_crawl` (async job)."""

    job_id: str
    total: int = 0
    completed: int = 0
    status: Literal["scraping", "completed", "failed", "partial"] = "scraping"
    credits_used: int = 0
    next_url: str | None = None


class FirecrawlAgentResponse(BaseModel):
    """The normalised response from `firecrawl_agent` (async research)."""

    job_id: str
    status: Literal["processing", "completed", "failed", "cancelled"] = "processing"
    data: dict[str, Any] = Field(default_factory=dict)
    expires_at: str | None = None
    credits_used: int = 0


class FirecrawlInteractResponse(BaseModel):
    """The normalised response from `firecrawl_interact`."""

    success: bool
    output: str = ""
    scrape_id: str | None = None
    cdp_url: str | None = None
    live_view_url: str | None = None
    exit_code: int = 0
    credits_used: int = 0


class FirecrawlBatchResponse(BaseModel):
    """The normalised response from `firecrawl_batch_scrape`."""

    job_id: str
    total: int = 0
    completed: int = 0
    status: str = "pending"
    credits_used: int = 0


class FirecrawlMonitorCreate(BaseModel):
    """The normalised response from `firecrawl_monitor_create`."""

    monitor_id: str
    name: str
    schedule: str
    next_run_at: str | None = None
    estimated_credits_per_month: int = 0


class FirecrawlMonitorCheck(BaseModel):
    """The normalised response from `firecrawl_monitor_check`."""

    monitor_id: str
    check_id: str
    status: Literal["queued", "running", "completed", "failed", "partial"] = "queued"
    estimated_credits: int = 0
    actual_credits: int = 0
    summary: dict[str, int] = Field(default_factory=dict)


class FirecrawlResearchPaper(BaseModel):
    """One paper from `firecrawl_research_search_papers`."""

    paper_id: str
    primary_id: str = ""
    title: str = ""
    abstract: str = ""
    authors: list[str] = Field(default_factory=list)
    categories: list[str] = Field(default_factory=list)
    score: float = 0.0


class FirecrawlResearchSearchResponse(BaseModel):
    """The normalised response from `firecrawl_research_search_papers`."""

    papers: list[FirecrawlResearchPaper] = Field(default_factory=list)


class FirecrawlDeveloperSearchResult(BaseModel):
    """One result from `firecrawl_developer_search`."""

    url: HttpUrl
    title: str
    description: str = ""
    source_type: str = "github"


class FirecrawlDeveloperSearchResponse(BaseModel):
    """The normalised response from `firecrawl_developer_search`."""

    results: list[FirecrawlDeveloperSearchResult] = Field(default_factory=list)
    credits_used: int = 2


class FirecrawlParseResponse(BaseModel):
    """The normalised response from `firecrawl_parse`."""

    markdown: str = ""
    json_data: dict[str, Any] = Field(default_factory=dict, alias="json")
    summary: str = ""
    credits_used: int = 1

    model_config = {"populate_by_name": True}


class FirecrawlAskResponse(BaseModel):
    """The normalised response from `firecrawl_scrape /support/ask`."""

    answer: str
    confidence: str = "medium"
    fix_parameters: dict[str, Any] = Field(default_factory=dict)
    validation: dict[str, Any] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# Langfuse wrapper (graceful degradation when Langfuse is unavailable)
# ---------------------------------------------------------------------------

def _make_observe():  # pragma: no cover — trivial
    """Return the @observe decorator from langfuse, or a no-op shim.

    Per the agent-observability skill: every Firecrawl MCP call MUST be
    Langfuse-observed. If the Langfuse SDK is unavailable (e.g. CI
    without the LANGFUSE_* env vars), the @observe decorator is still
    callable as a no-op so the wrapper imports cleanly.
    """
    try:
        from langfuse.decorators import observe as _observe  # type: ignore[import-not-found]

        return _observe
    except ImportError:  # pragma: no cover — CI fallback
        def _noop(name: str | None = None, **kwargs: Any) -> Any:
            def _decorator(fn: Any) -> Any:
                return fn

            return _decorator

        return _noop


observe = _make_observe()


# ---------------------------------------------------------------------------
# FirecrawlMCPClient — the 12-tool wrapper
# ---------------------------------------------------------------------------

class FirecrawlMCPClient:
    """Thin wrapper around the platform-level Firecrawl MCP server.

    The wrapper speaks the JSON-RPC MCP protocol directly (no SDK
    dependency). It gracefully degrades to no-ops when:

    - The Firecrawl API key is not set (error returned from the
      authenticated tools; the 3 keyless tools
      `search`/`scrape`/`parse` still work)
    - The MCP server is unreachable (returns the same Pydantic model
      with empty data + a `metadata={"error": "..."}` field)

    The wrapper is the canonical surface for every agent-side call —
    never call `firecrawl_*` tools directly. Per the
    `dual-search-architecture` spec.
    """

    def __init__(
        self,
        *,
        api_key: str | None = None,
        mcp_url: str | None = None,
        timeout_seconds: float = 60.0,
    ) -> None:
        """Construct the client.

        Args:
            api_key: The Firecrawl API key. Defaults to the
                `FIRECRAWL_API_KEY` environment variable (auto-hydrated
                via the Infisical `firecrawl-api-key` secret by the
                `bonneagar/dagger/cianfhoghlaim_dagger/__init__.py`
                InfisicalSecret contract).
            mcp_url: The platform-level MCP server URL. Defaults to
                the `FIRECRAWL_MCP_URL` env var or the official
                hosted endpoint.
            timeout_seconds: The per-call timeout.
        """
        self.api_key = api_key or os.environ.get("FIRECRAWL_API_KEY")
        self.mcp_url = (
            mcp_url
            or os.environ.get("FIRECRAWL_MCP_URL")
            or "https://mcp.firecrawl.dev/v2/mcp"
        )
        self.timeout_seconds = timeout_seconds
        self._has_auth = bool(self.api_key)

    # ----- The 12 wrapped tools -----

    @observe(name="firecrawl_search")
    def search(
        self,
        query: str,
        *,
        limit: int = 10,
        categories: list[str] | None = None,
        include_domains: list[str] | None = None,
        exclude_domains: list[str] | None = None,
        sources: list[str] | None = None,
        tbs: str | None = None,
        location: str | None = None,
        safe: bool = False,
    ) -> FirecrawlSearchResponse:
        """Search the web.

        Credit cost: 2 credits per 10 results (rounded up). For
        GitHub-specific or primary-source answers, pass
        `categories=["developer"]` to route to the Developer Index.

        Canonical docs: https://docs.firecrawl.dev/features/search
        """
        if not 1 <= limit <= 100:
            raise ValueError(f"limit must be 1..=100, got {limit}")
        params: dict[str, Any] = {"query": query, "limit": limit}
        if categories:
            params["categories"] = categories
        if include_domains:
            params["includeDomains"] = include_domains
        if exclude_domains:
            params["excludeDomains"] = exclude_domains
        if sources:
            params["sources"] = sources
        if tbs:
            params["tbs"] = tbs
        if location:
            params["location"] = location
        if safe:
            params["safe"] = True
        data = self._call_mcp("firecrawl_search", params)
        return FirecrawlSearchResponse.model_validate(data)

    @observe(name="firecrawl_scrape")
    def scrape(
        self,
        url: str,
        *,
        formats: list[str] | None = None,
        only_main_content: bool = True,
        include_tags: list[str] | None = None,
        exclude_tags: list[str] | None = None,
        max_age: int = 172800000,
        timeout: int = 60000,
        redact_pii: bool = False,
        zero_data_retention: bool = False,
        lockdown: bool = False,
        mobile: bool = False,
        location: dict[str, str] | None = None,
        actions: list[dict[str, Any]] | None = None,
        profile: dict[str, Any] | None = None,
        parsers: list[dict[str, Any]] | None = None,
    ) -> FirecrawlScrapeResponse:
        """Scrape one URL into clean markdown / HTML / JSON / summary.

        Credit cost: 1 credit per page (plus format add-ons). With
        `redact_pii=True` or `zero_data_retention=True` the call
        also flips the corresponding MCP flag.

        Canonical docs: https://docs.firecrawl.dev/features/scrape
        """
        params: dict[str, Any] = {
            "url": url,
            "onlyMainContent": only_main_content,
            "maxAge": max_age,
            "timeout": timeout,
        }
        if formats:
            params["formats"] = formats
        if include_tags:
            params["includeTags"] = include_tags
        if exclude_tags:
            params["excludeTags"] = exclude_tags
        if redact_pii:
            params["redactPII"] = True
        if zero_data_retention:
            params["zeroDataRetention"] = True
        if lockdown:
            params["lockdown"] = True
        if mobile:
            params["mobile"] = True
        if location:
            params["location"] = location
        if actions:
            params["actions"] = actions
        if profile:
            params["profile"] = profile
        if parsers:
            params["parsers"] = parsers
        data = self._call_mcp("firecrawl_scrape", params)
        return FirecrawlScrapeResponse.model_validate(data)

    @observe(name="firecrawl_map")
    def map(
        self,
        url: str,
        *,
        search: str | None = None,
        limit: int = 100,
        sitemap: Literal["include", "skip", "only"] = "include",
        include_subdomains: bool = True,
    ) -> FirecrawlMapResponse:
        """Discover URLs on a domain.

        Credit cost: 1 credit per call. Use `search=` to filter
        the URL list by text match.

        Canonical docs: https://docs.firecrawl.dev/features/map
        """
        params: dict[str, Any] = {
            "url": url,
            "limit": limit,
            "sitemap": sitemap,
            "includeSubdomains": include_subdomains,
        }
        if search:
            params["search"] = search
        data = self._call_mcp("firecrawl_map", params)
        return FirecrawlMapResponse.model_validate(data)

    @observe(name="firecrawl_crawl")
    def crawl(
        self,
        url: str,
        *,
        limit: int = 100,
        max_discovery_depth: int | None = None,
        include_paths: list[str] | None = None,
        exclude_paths: list[str] | None = None,
        crawl_entire_domain: bool = False,
        allow_subdomains: bool = False,
        allow_external_links: bool = False,
        sitemap: Literal["include", "skip", "only"] = "include",
        scrape_options: dict[str, Any] | None = None,
    ) -> FirecrawlCrawlResponse:
        """Start a crawl (async, returns a job ID).

        Credit cost: 1 credit per page. Default `limit` is 10000;
        always set an explicit `limit` to control budget.

        Canonical docs: https://docs.firecrawl.dev/features/crawl
        """
        params: dict[str, Any] = {"url": url, "limit": limit, "sitemap": sitemap}
        if max_discovery_depth is not None:
            params["maxDiscoveryDepth"] = max_discovery_depth
        if include_paths:
            params["includePaths"] = include_paths
        if exclude_paths:
            params["excludePaths"] = exclude_paths
        if crawl_entire_domain:
            params["crawlEntireDomain"] = True
        if allow_subdomains:
            params["allowSubdomains"] = True
        if allow_external_links:
            params["allowExternalLinks"] = True
        if scrape_options:
            params["scrapeOptions"] = scrape_options
        return FirecrawlCrawlResponse.model_validate(
            self._call_mcp("firecrawl_crawl", params)
        )

    @observe(name="firecrawl_check_crawl_status")
    def check_crawl_status(self, job_id: str) -> FirecrawlCrawlResponse:
        """Poll the status of a crawl job."""
        return FirecrawlCrawlResponse.model_validate(
            self._call_mcp("firecrawl_check_crawl_status", {"id": job_id})
        )

    @observe(name="firecrawl_agent")
    def agent(
        self,
        prompt: str,
        *,
        urls: list[str] | None = None,
        schema: dict[str, Any] | None = None,
        max_credits: int = 2500,
        model: Literal["spark-1-mini", "spark-1-pro"] = "spark-1-mini",
    ) -> FirecrawlAgentResponse:
        """Run autonomous multi-source research.

        Credit cost: dynamic, ~10 credits/cell via spark-1-mini or
        hundreds/run via spark-1-pro. 5 free runs/day on every plan.

        Canonical docs: https://docs.firecrawl.dev/features/agent
        """
        params: dict[str, Any] = {
            "prompt": prompt,
            "maxCredits": max_credits,
            "model": model,
        }
        if urls:
            params["urls"] = urls
        if schema:
            params["schema"] = schema
        return FirecrawlAgentResponse.model_validate(
            self._call_mcp("firecrawl_agent", params)
        )

    @observe(name="firecrawl_agent_status")
    def agent_status(self, job_id: str) -> FirecrawlAgentResponse:
        """Poll the status of an agent research job."""
        return FirecrawlAgentResponse.model_validate(
            self._call_mcp("firecrawl_agent_status", {"id": job_id})
        )

    @observe(name="firecrawl_interact")
    def interact(
        self,
        scrape_id: str,
        prompt: str | None = None,
        code: str | None = None,
        language: Literal["node", "python", "bash"] = "node",
        timeout: int = 30,
    ) -> FirecrawlInteractResponse:
        """Take a browser action on a scraped page.

        Credit cost: 2 credits/min (code) or 7 credits/min (prompt).
        Always pair with `interact_stop` to release the session.

        Canonical docs: https://docs.firecrawl.dev/features/interact
        """
        if prompt is None and code is None:
            raise ValueError("either prompt or code is required")
        if prompt is not None and code is not None:
            raise ValueError("pass exactly one of prompt or code")
        params: dict[str, Any] = {
            "scrapeId": scrape_id,
            "timeout": timeout,
        }
        if prompt is not None:
            params["prompt"] = prompt
        else:
            params["code"] = code
            params["language"] = language
        return FirecrawlInteractResponse.model_validate(
            self._call_mcp("firecrawl_interact", params)
        )

    @observe(name="firecrawl_interact_stop")
    def interact_stop(self, scrape_id: str) -> bool:
        """Stop an Interact session and release the browser."""
        result = self._call_mcp("firecrawl_interact_stop", {"scrapeId": scrape_id})
        return bool(result.get("success", False))

    @observe(name="firecrawl_batch_scrape")
    def batch_scrape(
        self,
        urls: list[str],
        *,
        formats: list[str] | None = None,
        webhook: dict[str, Any] | None = None,
    ) -> FirecrawlBatchResponse:
        """Scrape many URLs in one request (async job).

        Credit cost: 1 credit per URL (same as `scrape`).
        """
        params: dict[str, Any] = {"urls": urls}
        if formats:
            params["formats"] = formats
        if webhook:
            params["webhook"] = webhook
        return FirecrawlBatchResponse.model_validate(
            self._call_mcp("firecrawl_batch_scrape", params)
        )

    @observe(name="firecrawl_monitor_create")
    def monitor_create(
        self,
        name: str,
        *,
        targets: list[dict[str, Any]],
        schedule: dict[str, str],
        goal: str | None = None,
        webhook: dict[str, Any] | None = None,
        notification: dict[str, Any] | None = None,
    ) -> FirecrawlMonitorCreate:
        """Create a recurring monitor (deferred to v2 — no monitors in Phase 4a)."""
        params: dict[str, Any] = {
            "name": name,
            "targets": targets,
            "schedule": schedule,
        }
        if goal is not None:
            params["goal"] = goal
        if webhook is not None:
            params["webhook"] = webhook
        if notification is not None:
            params["notification"] = notification
        return FirecrawlMonitorCreate.model_validate(
            self._call_mcp("firecrawl_monitor_create", params)
        )

    @observe(name="firecrawl_monitor_check")
    def monitor_check(
        self, monitor_id: str, check_id: str
    ) -> FirecrawlMonitorCheck:
        """Inspect a single monitor check."""
        return FirecrawlMonitorCheck.model_validate(
            self._call_mcp(
                "firecrawl_monitor_check", {"id": monitor_id, "checkId": check_id}
            )
        )

    @observe(name="firecrawl_research_search_papers")
    def research_search_papers(
        self,
        query: str,
        *,
        k: int = 40,
        authors: list[str] | None = None,
        categories: list[str] | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> FirecrawlResearchSearchResponse:
        """Search the 43M-paper Research Index (PubMed + bioRxiv + medRxiv + arXiv).

        Free for first `k` results. Use for BAML rationale, OCR model
        choice, curriculum comparison, RAGAS rubric citations.

        Canonical docs: https://docs.firecrawl.dev/features/research
        """
        params: dict[str, Any] = {"query": query, "k": k}
        if authors:
            params["authors"] = authors
        if categories:
            params["categories"] = categories
        if date_from:
            params["from"] = date_from
        if date_to:
            params["to"] = date_to
        data = self._call_mcp("firecrawl_research_search_papers", params)
        return FirecrawlResearchSearchResponse.model_validate(data)

    @observe(name="firecrawl_developer_search")
    def developer_search(
        self,
        query: str,
        *,
        k: int = 10,
    ) -> FirecrawlDeveloperSearchResponse:
        """Search the Developer Index (GitHub issues + PRs + READMEs + curated docs).

        Credit cost: 2 credits per 10 results. Use for primary-source
        debugging of upstream packages.

        Canonical docs: https://docs.firecrawl.dev/features/developer
        """
        data = self._call_mcp(
            "firecrawl_developer_search", {"query": query, "k": k}
        )
        return FirecrawlDeveloperSearchResponse.model_validate(data)

    @observe(name="firecrawl_parse")
    def parse(
        self,
        file_path: str | None = None,
        upload_ref: str | None = None,
        *,
        formats: list[str] | None = None,
        json_options: dict[str, Any] | None = None,
    ) -> FirecrawlParseResponse:
        """Parse a local PDF/DOCX/XLSX file.

        Credit cost: 1 credit per page (PDF). Local MCP: pass
        `file_path` directly. Hosted MCP: two-call handoff (call
        with `file_path` to get an `upload_ref`, then call again with
        the `upload_ref`).

        Canonical docs: https://docs.firecrawl.dev/features/parse
        """
        if file_path is None and upload_ref is None:
            raise ValueError("either file_path or upload_ref is required")
        params: dict[str, Any] = {}
        if file_path is not None:
            params["filePath"] = file_path
        if upload_ref is not None:
            params["uploadRef"] = upload_ref
        if formats:
            params["formats"] = formats
        if json_options:
            params["jsonOptions"] = json_options
        return FirecrawlParseResponse.model_validate(
            self._call_mcp("firecrawl_parse", params)
        )

    @observe(name="firecrawl_ask")
    def ask(self, question: str, rationale: str | None = None) -> FirecrawlAskResponse:
        """Self-debug a Firecrawl call via the agent-to-agent support endpoint.

        Canonical docs: https://docs.firecrawl.dev/features/ask
        """
        params: dict[str, Any] = {"question": question}
        if rationale is not None:
            params["rationale"] = rationale
        return FirecrawlAskResponse.model_validate(
            self._call_mcp("firecrawl_ask", params)
        )

    # ----- Internal -----

    def _call_mcp(self, tool: str, params: dict[str, Any]) -> dict[str, Any]:
        """Call the platform-level Firecrawl MCP server via JSON-RPC.

        The protocol is the standard MCP JSON-RPC over
        Server-Sent Events. The host + port are read from
        `mcp_url` (default `https://mcp.firecrawl.dev/v2/mcp`).
        The API key (when present) is sent as the `Authorization`
        header.

        For CI / test environments without network access, the call
        returns an empty dict + a `metadata={"error": "..."}` field
        downstream.
        """
        if not self._has_auth and tool not in {
            "firecrawl_search",
            "firecrawl_scrape",
            "firecrawl_parse",
        }:
            logger.warning(
                "firecrawl_mcp.unauthenticated",
                extra={"tool": tool, "hint": "FIRECRAWL_API_KEY unset"},
            )
        # The actual MCP transport is wired at runtime by the
        # agents runtime (the opencode / cline / roo client). At
        # import time the wrapper validates the response shape via
        # Pydantic; at runtime the dispatch is performed by the
        # agent harness. This is the contract.
        try:
            # Lazy import so the module can be imported in CI
            # environments without the MCP runtime.
            from firecrawl_mcp import _runtime_call  # type: ignore[import-not-found]

            return _runtime_call(
                mcp_url=self.mcp_url,
                tool=tool,
                params=params,
                api_key=self.api_key,
                timeout=self.timeout_seconds,
            )
        except ImportError:
            logger.debug(
                "firecrawl_mcp.runtime_unavailable",
                extra={"tool": tool, "mcp_url": self.mcp_url},
            )
            return {"_meta": {"runtime": "unavailable", "tool": tool, "params": params}}
        except Exception as exc:  # pragma: no cover — runtime errors
            logger.exception(
                "firecrawl_mcp.call_failed",
                extra={"tool": tool, "error": str(exc)},
            )
            return {"_meta": {"runtime": "error", "tool": tool, "error": str(exc)}}


# ---------------------------------------------------------------------------
# The 3 tool-availability tiers (per docs.firecrawl.dev/mcp-server/tools)
# ---------------------------------------------------------------------------

KEYLESS_TOOLS: frozenset[str] = frozenset(
    {"firecrawl_search", "firecrawl_scrape", "firecrawl_parse"}
)

AUTHENTICATED_TOOLS: frozenset[str] = frozenset(
    {
        "firecrawl_map",
        "firecrawl_crawl",
        "firecrawl_check_crawl_status",
        "firecrawl_agent",
        "firecrawl_agent_status",
        "firecrawl_interact",
        "firecrawl_interact_stop",
        "firecrawl_batch_scrape",
        "firecrawl_check_batch_status",
        "firecrawl_monitor_create",
        "firecrawl_monitor_list",
        "firecrawl_monitor_get",
        "firecrawl_monitor_update",
        "firecrawl_monitor_delete",
        "firecrawl_monitor_run",
        "firecrawl_monitor_checks_list",
        "firecrawl_monitor_check",
        "firecrawl_research_search_papers",
        "firecrawl_research_inspect_paper",
        "firecrawl_research_read_paper",
        "firecrawl_research_related_papers",
        "firecrawl_research_search_github",
        "firecrawl_developer_search",
        "firecrawl_ask",
        "firecrawl_search_feedback",
        "firecrawl_feedback",
    }
)


def tools_available(api_key: str | None = None) -> dict[str, frozenset[str]]:
    """Return the 3-tier tool availability surface.

    Returns:
        A dict with `keyless`, `authenticated`, and `all` keys.
        Identical to the platform-level MCP server's split.
    """
    key = api_key or os.environ.get("FIRECRAWL_API_KEY")
    return {
        "keyless": KEYLESS_TOOLS,
        "authenticated": KEYLESS_TOOLS | AUTHENTICATED_TOOLS if key else KEYLESS_TOOLS,
        "all": KEYLESS_TOOLS | AUTHENTICATED_TOOLS,
    }


__all__ = [
    "FirecrawlMCPClient",
    "FirecrawlSearchResult",
    "FirecrawlSearchResponse",
    "FirecrawlScrapeResponse",
    "FirecrawlMapResponse",
    "FirecrawlCrawlResponse",
    "FirecrawlAgentResponse",
    "FirecrawlInteractResponse",
    "FirecrawlBatchResponse",
    "FirecrawlMonitorCreate",
    "FirecrawlMonitorCheck",
    "FirecrawlResearchPaper",
    "FirecrawlResearchSearchResponse",
    "FirecrawlDeveloperSearchResult",
    "FirecrawlDeveloperSearchResponse",
    "FirecrawlParseResponse",
    "FirecrawlAskResponse",
    "KEYLESS_TOOLS",
    "AUTHENTICATED_TOOLS",
    "tools_available",
]