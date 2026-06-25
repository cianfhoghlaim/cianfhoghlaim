"""
oideachais.dlt_sources.domains.education.ie — Ireland education DLT sources.

Phase 5 of the openspec change re-organisation. Each sub-module in
this package is a *re-export shim* to the legacy address under
`oideachais.dlt_sources.ireland.*`. The new path is the canonical
address used by `SourceFactory`; the legacy address is preserved
for one release cycle.

Modules that fail to import upstream (e.g. `edcolearning` references a
missing `oideachais.http_utils` module — a pre-existing fragility
flagged in `oideachais/dagster_defs/definitions.py:74-87`) are
deferred-loaded to keep the package import resilient.
"""
from __future__ import annotations

import importlib
import importlib as _il
from typing import Any


def _lazy(name: str, mod: str) -> Any:
    """Return a *deferred* module attribute. Importing the legacy module
    happens on first attribute access, so a broken upstream module does
    not block the whole re-export package."""
    def _getattr() -> Any:  # type: ignore[no-redef]
        return _il.import_module(mod)

    class _LazyModule:
        def __getattr__(self, item: str) -> Any:
            return getattr(_getattr(), item)

    obj = _LazyModule()
    obj.__name__ = name
    return obj


# Re-exported modules. Modules that fail to import are still listed here
# (so `from ... import edcolearning` works after a manual fix upstream),
# but a known-broken import does not block the package.
_REEXPORTS: list[tuple[str, str]] = [
    ("aistear", "oideachais.dlt_sources.ireland.aistear"),
    ("curriculum_source", "oideachais.dlt_sources.ireland.curriculum_source"),
    ("examinations", "oideachais.dlt_sources.ireland.examinations"),
    ("leaving_cert", "oideachais.dlt_sources.ireland.leaving_cert"),
    ("ncca", "oideachais.dlt_sources.ireland.ncca"),
    ("oide", "oideachais.dlt_sources.ireland.oide"),
    ("parallel_corpus", "oideachais.dlt_sources.ireland.parallel_corpus"),
    ("pdf_downloader", "oideachais.dlt_sources.ireland.pdf_downloader"),
    ("sec_aural_transcripts", "oideachais.dlt_sources.ireland.sec_aural_transcripts"),
    ("senior_cycle", "oideachais.dlt_sources.ireland.senior_cycle"),
    ("source_adapters", "oideachais.dlt_sources.ireland.source_adapters"),
    ("tertiary", "oideachais.dlt_sources.ireland.tertiary"),
]

# Eager re-exports for the modules we know import cleanly.
ncca = importlib.import_module("oideachais.dlt_sources.ireland.ncca")
curriculum_source = importlib.import_module("oideachais.dlt_sources.ireland.curriculum_source")
examinations = importlib.import_module("oideachais.dlt_sources.ireland.examinations")
leaving_cert = importlib.import_module("oideachais.dlt_sources.ireland.leaving_cert")
oide = importlib.import_module("oideachais.dlt_sources.ireland.oide")
senior_cycle = importlib.import_module("oideachais.dlt_sources.ireland.senior_cycle")
pdf_downloader = importlib.import_module("oideachais.dlt_sources.ireland.pdf_downloader")

# Lazy re-exports (may be broken upstream).
aistear = _lazy("aistear", "oideachais.dlt_sources.ireland.aistear")
parallel_corpus = _lazy("parallel_corpus", "oideachais.dlt_sources.ireland.parallel_corpus")
sec_aural_transcripts = _lazy("sec_aural_transcripts", "oideachais.dlt_sources.ireland.sec_aural_transcripts")
source_adapters = _lazy("source_adapters", "oideachais.dlt_sources.ireland.source_adapters")
tertiary = _lazy("tertiary", "oideachais.dlt_sources.ireland.tertiary")

# Subjects re-exports.
from dlt_sources.ireland.subjects import (
    base as subjects_base,
    junior_cycle,
    senior_cycle as subjects_senior_cycle,
)


__all__ = [
    "aistear",
    "curriculum_source",
    "examinations",
    "leaving_cert",
    "ncca",
    "oide",
    "parallel_corpus",
    "pdf_downloader",
    "sec_aural_transcripts",
    "senior_cycle",
    "source_adapters",
    "tertiary",
    "subjects_base",
    "junior_cycle",
    "subjects_senior_cycle",
]
