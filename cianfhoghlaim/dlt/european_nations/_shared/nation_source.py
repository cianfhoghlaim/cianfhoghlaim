"""Shared helpers + registries for the EU nations + Ukraine pipeline.

Defines the canonical per-nation source contract — every per-nation
source subclasses ``NationSource`` and emits rows tagged with
``country_code``, ``language``, ``domain``, and the canonical DuckLake
namespace.

Honours ``USE_LOCAL_SCRAPES=true`` by reading from
``stedding/ingest_queue/european_nations/<country_code>/<domain>/<lang>/``
(matching the AGENTS.md "Respect the Ingestion Cache" rule).
"""
from __future__ import annotations

import os
from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


EU_NATIONS_CACHE_ROOT: Path = Path(
    os.environ.get(
        "EU_NATIONS_SCRAPE_CACHE_ROOT",
        str(
            Path(__file__).resolve().parents[3]
            / "stedding"
            / "ingest_queue"
            / "european_nations"
        ),
    )
)
"""Canonical local scrape cache root for the EU nations pipeline."""


@dataclass
class NationSource:
    """Canonical base class for a per-nation DLT source.

    Every per-nation source MUST subclass this contract. The
    ``supported_languages`` list is the set of official language(s)
    the jurisdiction publishes in.
    """

    country_code: str
    """ISO 3166-1 alpha-3 code in lowercase (e.g. ``"ukr"``, ``"fra"``,
    ``"deu"``, ``"pol"``, ``"esp"``, ``"ita"``)."""

    domain: str
    """One of ``education | law | medicine | statistics | government``."""

    source_slug: str
    """Snake_case slug of the source (e.g. ``"legifrance"``)."""

    supported_languages: tuple[str, ...] = ("en",)
    """Official language(s) the jurisdiction publishes in.

    For example, ``"ukr"`` uses ``("uk",)``, ``"fra"`` uses
    ``("fr",)``, ``"deu"`` uses ``("de",)``, ``"pol"`` uses
    ``("pl",)``, ``"esp"`` uses ``("es", "ca", "gl", "eu", "va")``
    (Castilian + Catalan + Galician + Basque + Aranese), ``"ita"``
    uses ``("it",)``.
    """

    default_language: str | None = None
    """Canonical first-edition language, e.g. ``"uk"`` for Ukraine."""

    document_type: str = "official_document"
    """``document_type`` tag every emitted row carries."""

    extra_metadata: dict[str, Any] = field(default_factory=dict)
    """Per-source metadata surfaced on the ``Metadata`` column."""

    def __post_init__(self) -> None:
        if not self.default_language:
            self.default_language = self.supported_languages[0]

    @property
    def source_id(self) -> str:
        """Canonical ``source_id`` for the per-nation source."""
        return (
            f"european_nations.{self.country_code}.{self.domain}"
            f".{self.source_slug}"
        )

    @property
    def ducklake_table(self) -> str:
        """Canonical DuckLake namespace for the per-nation source."""
        return (
            f"oideachais.{self.domain}.european_nations"
            f".{self.country_code}"
        )

    def cache_path(self, language: str | None = None) -> Path:
        """Return the canonical cache directory."""
        lang = language or self.default_language
        return (
            EU_NATIONS_CACHE_ROOT
            / self.country_code
            / self.domain
            / lang
        )

    def iter_local_cache(
        self,
        language: str | None = None,
    ) -> Iterator[Path]:
        """Yield every cached JSON snapshot under the canonical cache."""
        lang = language or self.default_language
        lang_dir = self.cache_path(lang)
        if not lang_dir.exists():
            return
        for json_path in sorted(lang_dir.glob("*.json")):
            yield json_path


def use_local_scrapes() -> bool:
    """True when the AGENTS.md cache rule is active for the EU nations pipeline."""
    return os.environ.get("USE_LOCAL_SCRAPES", "").lower().strip() in {
        "1",
        "true",
        "yes",
        "on",
    }


def row_from_cache(
    cache_path: Path,
    nation: NationSource,
    *,
    document_id_key: str = "document_id",
    default_status: str = "in_force",
) -> dict[str, Any]:
    """Parse a per-nation cache JSON snapshot into a DLT row.

    The canonical schema is the Firecrawl shape (``markdown`` +
    ``metadata`` + ``sourceURL``) with a per-domain ``document_id``
    field.
    """
    import json
    from datetime import UTC, datetime

    try:
        payload = json.loads(cache_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}

    metadata = payload.get("metadata", {}) if isinstance(payload, dict) else {}
    if not isinstance(metadata, dict):
        metadata = {}

    source_url = metadata.get("sourceURL") or metadata.get("url") or ""
    title = payload.get("title") or metadata.get("title") or ""
    markdown = payload.get("markdown") or ""

    document_id = (
        metadata.get(document_id_key)
        or metadata.get("id")
        or cache_path.stem
    )
    content_hash = (
        f"sha256:{hash(markdown) & 0xFFFFFFFFFFFFFFFF:016x}"
        if markdown
        else ""
    )

    return {
        "country_code": nation.country_code,
        "language": cache_path.parent.name,
        "domain": nation.domain,
        document_id_key: document_id,
        "title": title,
        "source_url": source_url,
        "content_hash": content_hash,
        "document_type": nation.document_type,
        "region": "european_nations",
        "official_status": metadata.get("official_status", default_status),
        "extracted_at": datetime.now(UTC).isoformat(),
        "source": nation.source_slug,
        "source_file": str(cache_path),
    }


__all__ = [
    "EU_NATIONS_CACHE_ROOT",
    "NationSource",
    "row_from_cache",
    "use_local_scrapes",
]
