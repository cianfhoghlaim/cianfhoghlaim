"""Shared helpers + registries for the EU institutional pipeline.

Three registries live here:

- :data:`EU_LANGUAGES` — the 24 EU official languages as ISO 639-1
  codes (alphabetical).
- :data:`EU_INSTITUTIONS` — the 10 EU institutions + agencies that the
  pipeline ingests.
- :data:`EU_CACHE_ROOT` — the local scrape cache root
  (``stedding/ingest_queue/eu/<institution>/``) that every EU
  institutional source honours when ``USE_LOCAL_SCRAPES=true``.

Per the :class:`EUInstitutionalSource` contract every source MUST
declare its :attr:`institution_slug` + :attr:`supported_languages` +
:attr:`default_language` so the Dagster partition factory can compose
the canonical ``MultiPartitionsDefinition`` (institution × language)
without per-source wiring.
"""
from __future__ import annotations

import os
from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# The 24 EU official languages (alphabetical by ISO 639-1 code).
# `ga` (Irish / Gaeilge) was added as the 24th official language on
# 2022-01-01.
EU_LANGUAGES: tuple[str, ...] = (
    "bg",  # Bulgarian
    "hr",  # Croatian
    "cs",  # Czech
    "da",  # Danish
    "nl",  # Dutch
    "en",  # English
    "et",  # Estonian
    "fi",  # Finnish
    "fr",  # French
    "de",  # German
    "el",  # Greek
    "hu",  # Hungarian
    "ga",  # Irish (Gaeilge)
    "it",  # Italian
    "lv",  # Latvian
    "lt",  # Lithuanian
    "mt",  # Maltese
    "pl",  # Polish
    "pt",  # Portuguese
    "ro",  # Romanian
    "sk",  # Slovak
    "sl",  # Slovenian
    "es",  # Spanish
    "sv",  # Swedish
)
"""The 24 EU official language codes (ISO 639-1, alphabetical).

Per :class:`EUInstitutionalSource` every EU institutional source MUST
restrict its ``language`` partition to this set.
"""

EU_INSTITUTIONS: tuple[str, ...] = (
    "eur_lex",
    "publications_office",
    "eurydice",
    "cedefop",
    "school_education_gateway",
    "ema",
    "ecdc",
    "european_health_data_space",
    "eurostat",
    "council_of_europe",
    "coe_echr",
    "europa_portal",
    "commission_press",
    "parliament_documents",
    "council_documents",
)
"""The 15 EU institutional sub-trees that the pipeline ingests."""


# Default English edition for sources that publish in a single
# canonical language first.
EU_DEFAULT_LANGUAGE: str = "en"


EU_CACHE_ROOT: Path = Path(
    os.environ.get(
        "EU_SCRAPE_CACHE_ROOT",
        str(Path(__file__).resolve().parents[3] / "stedding" / "ingest_queue" / "eu"),
    )
)
"""Canonical local scrape cache root for the EU institutional pipeline."""


@dataclass
class EUInstitutionalSource:
    """Canonical base class for an EU institutional DLT source.

    Every EU institutional source MUST subclass this contract. The
    :meth:`cache_path` + :meth:`iter_local_cache` helpers route every
    read through the canonical ``stedding/ingest_queue/eu/<institution>/<lang>/``
    cache directory (per the AGENTS.md "Respect the Ingestion Cache"
    rule).
    """

    institution_slug: str
    """The institutional sub-tree slug, e.g. ``"eur_lex"`` or ``"ema"``."""

    supported_languages: tuple[str, ...] = EU_LANGUAGES
    """The languages the source can emit. Defaults to all 24 EU official
    languages; override per source when an institution publishes in
    fewer (e.g. ECHR publishes primarily in English + French)."""

    default_language: str = EU_DEFAULT_LANGUAGE
    """The canonical first-edition language, e.g. ``"en"`` or ``"fr"``."""

    document_type: str = "institutional_document"
    """The ``document_type`` tag every emitted row carries."""

    extra_metadata: dict[str, Any] = field(default_factory=dict)
    """Per-source metadata surfaced on the ``Metadata`` column."""

    def cache_path(self, language: str) -> Path:
        """Return the canonical cache directory for ``language``.

        The convention is ``stedding/ingest_queue/eu/<institution>/<lang>/``
        where ``<lang>`` is the 2-letter ISO 639-1 code.
        """
        if language not in self.supported_languages:
            raise ValueError(
                f"language must be one of {self.supported_languages}, "
                f"got {language!r}"
            )
        return EU_CACHE_ROOT / self.institution_slug / language

    def iter_local_cache(
        self,
        language: str | None = None,
    ) -> Iterator[Path]:
        """Yield every cached JSON snapshot under
        ``stedding/ingest_queue/eu/<institution>/<lang>/``.

        Graceful no-op when the cache is absent (matches the project
        convention).
        """
        languages = (
            (language,)
            if language is not None
            else self.supported_languages
        )
        for lang in languages:
            lang_dir = self.cache_path(lang)
            if not lang_dir.exists():
                continue
            for json_path in sorted(lang_dir.glob("*.json")):
                yield json_path


def use_local_scrapes() -> bool:
    """True when the AGENTS.md cache rule is active for the EU pipeline."""
    return os.environ.get("USE_LOCAL_SCRAPES", "").lower().strip() in {
        "1",
        "true",
        "yes",
        "on",
    }


__all__ = [
    "EU_CACHE_ROOT",
    "EU_DEFAULT_LANGUAGE",
    "EU_INSTITUTIONS",
    "EU_LANGUAGES",
    "EUInstitutionalSource",
    "use_local_scrapes",
]
