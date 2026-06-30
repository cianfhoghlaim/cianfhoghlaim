"""
oideachais.site_analysis — Firecrawl + Browserbase MCP-driven site analysis.

Phase 8 of the openspec change. For every public source in
`oideachais/sources.yaml`, the `extract` command produces a
`SiteAnalysis` record (defined in `baml/processing/site_analysis.baml`)
that captures the site's software fingerprint, layout fingerprint,
sampled page descriptions, and a full‑page screenshot.

The record is then:
  1. Written as a DLT source to `oideachais.site_analysis` (DuckLake).
  2. Embedded in LanceDB (`oideachais.site_analysis.descriptions`).
  3. Cognified in Cognee (`oideachais_site_analysis`).

In test mode (`USE_LOCAL_SCRAPES=true`) every MCP call is replaced by
a stub from `oideachais/site_analysis/_stubs/`. The stubs return
fixed payloads so the asset graph can be exercised without a live
browser or firecrawl subscription.
"""
from __future__ import annotations

import os
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class SoftwareFingerprint(BaseModel):
    model_config = ConfigDict(extra="forbid")
    cms: str | None = None
    waf: str | None = None
    captcha: str | None = None
    analytics: list[str] = Field(default_factory=list)
    framework_headers: list[str] = Field(default_factory=list)
    fonts: list[str] = Field(default_factory=list)


class LayoutFingerprint(BaseModel):
    model_config = ConfigDict(extra="forbid")
    main_content_xpath: str | None = None
    sticky_nav: bool = False
    cookie_banner: bool = False
    form_regions: list[str] = Field(default_factory=list)
    pagination_pattern: str | None = None


class PageDescription(BaseModel):
    model_config = ConfigDict(extra="forbid")
    url: str
    h1: str | None = None
    h2_hierarchy: list[str] = Field(default_factory=list)
    summary: str = ""
    links: list[str] = Field(default_factory=list)
    attachments: list[str] = Field(default_factory=list)


class SiteAnalysis(BaseModel):
    model_config = ConfigDict(extra="forbid")
    source_id: str
    captured_at: str
    url: str
    software: SoftwareFingerprint = Field(default_factory=SoftwareFingerprint)
    layout: LayoutFingerprint = Field(default_factory=LayoutFingerprint)
    pages_sampled: int = 0
    pages: list[PageDescription] = Field(default_factory=list)
    screenshot_path: str | None = None
    compliance_notes: str | None = None

    def to_dlt_row(self) -> dict[str, Any]:
        """Return a flat dict suitable for DLT `merge` write."""
        return self.model_dump(mode="json")


def _use_stub() -> bool:
    """Test-mode gate: under `USE_LOCAL_SCRAPES=true` we never call
    a live MCP server; the stub fixtures are used instead."""
    return os.environ.get("USE_LOCAL_SCRAPES", "true").lower() == "true"
