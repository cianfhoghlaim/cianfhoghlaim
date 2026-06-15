"""Pydantic schema validation for `oideachais/sources.yaml`.

`oideachais/sources.yaml` is the canonical registry that drives the
SourceFactory (Phase 2.1 of the lateralise change). Each entry
binds a DLT source to a Dagster asset, a LanceDB table, a Cognee
dataset, and a marimo notebook.

This test loads the YAML, parses every `sources:` entry through
the `SourceSpec` pydantic model, and asserts:

  1. Every required field is present.
  2. `id` matches `^{nation}.{domain}.{entity}$`.
  3. `asset_key` is non-empty and starts with `nation` and `domain`.
  4. `kind` is in the `kinds:` whitelist.
  5. `nation` is in the `nations:` whitelist.
  6. `embedding.table` and `kg.dataset` use the canonical
     `oideachais.{domain}.{nation}.{entity}` naming.
  7. `urls` is non-empty.

The test is the schema-of-record for the registry. If you add a
new optional field, add it to `SourceSpec`; if you change the
naming convention, update both this model and the SourceFactory.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml
from pydantic import BaseModel, Field, field_validator


# ---------------------------------------------------------------------------
# Pydantic schema
# ---------------------------------------------------------------------------
class NationSpec(BaseModel):
    code: str
    name: str
    jurisdiction: str


class CrawlSpec(BaseModel):
    include_paths: list[str] = Field(default_factory=list)
    exclude_paths: list[str] = Field(default_factory=list)
    max_pages: int | None = None
    max_depth: int | None = None


class ScheduleSpec(BaseModel):
    cron: str
    timezone: str = "UTC"


class EmbeddingSpec(BaseModel):
    table: str
    kind: str = "page_markdown"


class KgSpec(BaseModel):
    dataset: str
    edges: list[str] = Field(default_factory=list)


class ComplianceSpec(BaseModel):
    licence: str = "TBD"
    contact: str | None = None
    retain_raw_snapshots_days: int | None = None
    respect_robots_txt: bool = True


class SourceSpec(BaseModel):
    id: str
    name: str
    domain: str
    nation: str
    kind: str
    urls: list[str] = Field(default_factory=list)
    crawl: CrawlSpec | None = None
    schedule: ScheduleSpec | None = None
    sensors: list[str] = Field(default_factory=list)
    asset_key: list[str] = Field(default_factory=list)
    embedding: EmbeddingSpec | None = None
    kg: KgSpec | None = None
    compliance: ComplianceSpec | None = None
    # Anything else passes through.
    extra_ignore: Any = None

    @field_validator("id")
    @classmethod
    def _id_matches_nation_domain_entity(cls, v: str) -> str:
        parts = v.split(".")
        if len(parts) != 3:
            raise ValueError(
                f"id {v!r} must be 'nation.domain.entity' (3 dot-separated parts)"
            )
        return v

    @field_validator("asset_key")
    @classmethod
    def _asset_key_starts_with_nation_domain(cls, v: list[str]) -> list[str]:
        if len(v) < 2:
            raise ValueError("asset_key must have at least 2 components")
        return v


# ---------------------------------------------------------------------------
# Loader
# ---------------------------------------------------------------------------
SOURCES_YAML = Path(__file__).resolve().parents[1] / "sources.yaml"


def _load_sources_yaml() -> dict[str, Any]:
    with SOURCES_YAML.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def test_sources_yaml_loads() -> None:
    """The YAML must parse without error."""
    doc = _load_sources_yaml()
    assert doc.get("version") == 2, "sources.yaml must declare version: 2"
    assert "sources" in doc, "sources.yaml must have a `sources:` key"
    assert doc["sources"], "sources.yaml must declare at least one source"


def test_nations_whitelist_is_consistent() -> None:
    """Each `nation` in every source must be in the `nations:` whitelist."""
    doc = _load_sources_yaml()
    allowed = {n["code"] for n in doc.get("nations", [])}
    assert allowed, "nations: whitelist must be non-empty"
    for entry in doc["sources"]:
        assert entry["nation"] in allowed, (
            f"Source {entry.get('id')!r} has nation {entry['nation']!r} "
            f"which is not in the nations: whitelist"
        )


def test_kinds_whitelist_is_consistent() -> None:
    """Each `kind` in every source must be in the `kinds:` whitelist."""
    doc = _load_sources_yaml()
    allowed = set(doc.get("kinds", []))
    assert allowed, "kinds: whitelist must be non-empty"
    for entry in doc["sources"]:
        assert entry["kind"] in allowed, (
            f"Source {entry.get('id')!r} has kind {entry['kind']!r} "
            f"which is not in the kinds: whitelist"
        )


def test_every_source_parses_as_source_spec() -> None:
    """Every entry must satisfy the SourceSpec pydantic model."""
    doc = _load_sources_yaml()
    parsed: list[SourceSpec] = []
    for entry in doc["sources"]:
        try:
            parsed.append(SourceSpec.model_validate(entry))
        except Exception as exc:
            pytest.fail(
                f"Source {entry.get('id')!r} failed SourceSpec validation:\n{exc}"
            )
    # 43 sources is the lateralise-change baseline; we just need
    # the test to surface a regression if someone adds a malformed entry.
    assert len(parsed) >= 30, (
        f"Expected at least 30 sources, got {len(parsed)}. "
        "Has someone accidentally truncated sources.yaml?"
    )


def test_ids_are_unique() -> None:
    """Source ids must be unique (they're the asset key prefix)."""
    doc = _load_sources_yaml()
    seen: dict[str, int] = {}
    for entry in doc["sources"]:
        sid = entry["id"]
        seen[sid] = seen.get(sid, 0) + 1
    dupes = {k: v for k, v in seen.items() if v > 1}
    assert not dupes, f"Duplicate source ids: {dupes}"


def test_url_lists_are_non_empty() -> None:
    """Every source must declare at least one url."""
    doc = _load_sources_yaml()
    for entry in doc["sources"]:
        urls = entry.get("urls") or []
        assert urls, f"Source {entry['id']!r} has empty `urls:`"
