"""oideachais.dlt_sources.official_media.source_resolver — 4-lookup parallel resolver.

For each surviving official-media profile, resolve the canonical
official source through 4 parallel lookups (off the main thread):

  1. Wikipedia REST summary endpoint
  2. Companies House (UK) / CRO (ROI)
  3. Mastodon webfinger
  4. Bluesky xrpc

Plus an optional ``official_media_overrides.yaml`` short-circuit for
the 4 seed intelligence agencies (mi5, mi6, gchq, hmgcc).

When ``USE_LIVE_LOOKUPS`` is unset / false (the CI default), the 4
network lookups are all skipped and the resolver returns a stub
``{"resolver_notes": "offline_stub"}`` row. The override short-circuit
works regardless of the env var.
"""
from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import structlog
import yaml

logger = structlog.get_logger(__name__)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

USE_LIVE_LOOKUPS = os.environ.get("USE_LIVE_LOOKUPS", "").lower() in (
    "1",
    "true",
    "yes",
)


# ---------------------------------------------------------------------------
# SourceResolver
# ---------------------------------------------------------------------------


@dataclass
class ResolvedSource:
    """One row of the ``resolved_sources`` resource."""

    candidate_id: str
    ig_username: str
    category: str | None
    official_website: str | None = None
    wikipedia_url: str | None = None
    wikipedia_extract: str | None = None
    companies_house_id: str | None = None
    companies_house_name: str | None = None
    cro_number: str | None = None
    mastodon_handle: str | None = None
    mastodon_url: str | None = None
    bluesky_handle: str | None = None
    bluesky_did: str | None = None
    bluesky_url: str | None = None
    resolved_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    resolver_notes: str = ""

    def to_dlt_row(self) -> dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "ig_username": self.ig_username,
            "category": self.category,
            "official_website": self.official_website,
            "wikipedia_url": self.wikipedia_url,
            "wikipedia_extract": self.wikipedia_extract,
            "companies_house_id": self.companies_house_id,
            "companies_house_name": self.companies_house_name,
            "cro_number": self.cro_number,
            "mastodon_handle": self.mastodon_handle,
            "mastodon_url": self.mastodon_url,
            "bluesky_handle": self.bluesky_handle,
            "bluesky_did": self.bluesky_did,
            "bluesky_url": self.bluesky_url,
            "resolved_at": self.resolved_at,
            "resolver_notes": self.resolver_notes,
        }


class SourceResolver:
    """4-lookup parallel resolver with override short-circuit.

    Args:
        fixtures_dir: Directory containing ``official_media_overrides.yaml``.
        live_lookups: When ``False`` (the default), the 4 network
            lookups are skipped and the resolver returns a stub. The
            override short-circuit still works.
    """

    def __init__(
        self,
        fixtures_dir: Path | None = None,
        live_lookups: bool | None = None,
    ) -> None:
        self.fixtures_dir = (
            Path(fixtures_dir)
            if fixtures_dir is not None
            else Path(__file__).parent / "fixtures"
        )
        self.live_lookups = (
            USE_LIVE_LOOKUPS if live_lookups is None else live_lookups
        )
        self._overrides: dict[str, dict[str, Any]] = self._load_overrides()

    def _load_overrides(self) -> dict[str, dict[str, Any]]:
        path = self.fixtures_dir / "official_media_overrides.yaml"
        if not path.exists():
            logger.warning("overrides_missing", path=str(path))
            return {}
        with path.open(encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
        entries = data.get("overrides", [])
        return {
            entry["ig_username"].lower(): entry
            for entry in entries
            if isinstance(entry, dict) and "ig_username" in entry
        }

    # -- 4 lookups ------------------------------------------------------

    async def _lookup_wikipedia(self, title: str) -> dict[str, Any] | None:
        if not self.live_lookups:
            logger.debug("lookup_skipped_offline", authority="wikipedia", title=title)
            return None
        # The real implementation lives in source_resolver.live; this
        # signature is what `source_resolver.live` implements.
        from dlt_sources.official_media._resolver_live import lookup_wikipedia

        return await lookup_wikipedia(title)

    async def _lookup_companies_house(self, name: str) -> dict[str, Any] | None:
        if not self.live_lookups:
            logger.debug(
                "lookup_skipped_offline", authority="companies_house", name=name
            )
            return None
        from dlt_sources.official_media._resolver_live import lookup_companies_house

        return await lookup_companies_house(name)

    async def _lookup_cro(self, name: str) -> dict[str, Any] | None:
        if not self.live_lookups:
            logger.debug("lookup_skipped_offline", authority="cro_ireland", name=name)
            return None
        from dlt_sources.official_media._resolver_live import lookup_cro

        return await lookup_cro(name)

    async def _lookup_mastodon(
        self, ig_username: str
    ) -> dict[str, Any] | None:
        if not self.live_lookups:
            logger.debug(
                "lookup_skipped_offline", authority="mastodon", ig_username=ig_username
            )
            return None
        from dlt_sources.official_media._resolver_live import lookup_mastodon

        return await lookup_mastodon(ig_username)

    async def _lookup_bluesky(self, ig_username: str) -> dict[str, Any] | None:
        if not self.live_lookups:
            logger.debug(
                "lookup_skipped_offline", authority="bluesky", ig_username=ig_username
            )
            return None
        from dlt_sources.official_media._resolver_live import lookup_bluesky

        return await lookup_bluesky(ig_username)

    # -- Public API -----------------------------------------------------

    async def resolve_async(
        self,
        ig_username: str,
        category: str | None = None,
        candidate_id: str | None = None,
    ) -> ResolvedSource:
        """Async resolution. The 4 non-override lookups are awaited
        in parallel via ``asyncio.gather``."""
        username = ig_username.lower().lstrip("@")
        cid = candidate_id or f"{username}@{datetime.now(UTC).strftime('%Y%m%d')}"

        # Override short-circuit
        override = self._overrides.get(username)
        if override is not None:
            return ResolvedSource(
                candidate_id=cid,
                ig_username=username,
                category=category or override.get("category"),
                official_website=override.get("official_website"),
                wikipedia_url=override.get("wikipedia_url"),
                wikipedia_extract=override.get("wikipedia_extract"),
                companies_house_id=override.get("companies_house_id"),
                companies_house_name=override.get("companies_house_name"),
                cro_number=override.get("cro_number"),
                mastodon_handle=override.get("mastodon_handle"),
                mastodon_url=override.get("mastodon_url"),
                bluesky_handle=override.get("bluesky_handle"),
                bluesky_did=override.get("bluesky_did"),
                bluesky_url=override.get("bluesky_url"),
                resolver_notes="override",
            )

        # Fan out 5 lookups in parallel (Wikipedia + Companies House
        # + CRO + Mastodon + Bluesky). In offline mode each returns
        # None and we just record the stub.
        wiki, ch, cro, masto, blue = await asyncio.gather(
            self._lookup_wikipedia(override_title_for(username)),
            self._lookup_companies_house(ig_username),
            self._lookup_cro(ig_username),
            self._lookup_mastodon(ig_username),
            self._lookup_bluesky(ig_username),
        )
        return ResolvedSource(
            candidate_id=cid,
            ig_username=username,
            category=category,
            wikipedia_url=(wiki or {}).get("wikipedia_url"),
            wikipedia_extract=(wiki or {}).get("extract"),
            companies_house_id=(ch or {}).get("companies_house_id"),
            companies_house_name=(ch or {}).get("company_name"),
            cro_number=(cro or {}).get("cro_number"),
            mastodon_handle=(masto or {}).get("handle"),
            mastodon_url=(masto or {}).get("url"),
            bluesky_handle=(blue or {}).get("handle"),
            bluesky_did=(blue or {}).get("did"),
            bluesky_url=(blue or {}).get("url"),
            resolver_notes="offline_stub" if not self.live_lookups else "live",
        )

    def resolve(
        self,
        ig_username: str,
        category: str | None = None,
        candidate_id: str | None = None,
    ) -> ResolvedSource:
        """Sync wrapper around ``resolve_async``. Safe to call from
        non-async contexts (Dagster assets, marimo cells)."""
        return asyncio.run(
            self.resolve_async(ig_username, category, candidate_id)
        )


# Module-level singleton — the canonical entry point.
source_resolver = SourceResolver()


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def override_title_for(username: str) -> str:
    """Map an Instagram handle to the Wikipedia page title to look up.

    Best-effort heuristic: drop the unambiguous ``.official`` /
    ``_official`` suffix (used by the verified-account convention) and
    title-case the result. ``_uk`` / ``_ie`` are intentionally **not**
    stripped — they're too ambiguous (could be a handle's identity
    suffix or a "United Kingdom" reference).
    """
    cleaned = username.lower()
    for suffix in (".official", "_official"):
        if cleaned.endswith(suffix):
            cleaned = cleaned[: -len(suffix)]
            break
    return cleaned.replace("_", " ").replace(".", " ").title().strip()
