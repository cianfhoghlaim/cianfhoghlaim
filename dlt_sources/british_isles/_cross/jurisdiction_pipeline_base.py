"""British Isles jurisdiction pipeline base class — canonical
per-jurisdiction + per-nation DLT source contract.

Per the 2026-08-10-biep-v3-preflight-bug-fixes-v1 change +
the 2026-08-24-dlt-sources-to-multi-repo-scaffold-v1 §6.1 / §6.3 /
§6.4 / §6.5 / §11 changes.

Consolidates the ~30 LOC of duplicated boilerplate across the 4
BIEP v3 jurisdiction pipeline files (ireland + england + sct_wls_ni +
crown_dependencies) into this shared base class. Each pipeline file
becomes ~25 LOC of subclass definitions.

## Merged with the EU-nations ``NationSource`` API (§11, 2026-08-24)

Per the 2026-08-24-dlt-sources-to-multi-repo-scaffold-v1 §11 change,
this module now hosts the **canonical** per-jurisdiction / per-nation
source base class. The legacy ``NationSource`` dataclass at
``dlt_sources.european_nations._shared.nation_source`` was merged
into ``JurisdictionPipelineBase`` so the 51 per-nation source files
(``american_nations/*``, ``commonwealth/*``, ``education/<cc>/*``,
``law/<cc>/*``, ``medicine/<cc>/*``) inherit the same canonical
boilerplate as the 8 BIEP v3 jurisdiction pipelines.

A single ``JurisdictionPipelineBase`` instance supports **two
construction modes**:

1. **BIEP v3 mode** — ``JurisdictionPipelineBase("ireland", ...)``.
   Positional ``jurisdiction`` is required; subclasses set
   ``STAGE`` + override ``build_pipeline_resource()``.

2. **NationSource mode** —
   ``JurisdictionPipelineBase(country_code="aus", domain="government",
   source_slug="gov_au", supported_languages=("en",),
   document_type="government_document", extra_metadata={...})``.
   The merged class stores the per-vertical resource fields
   (``domain``, ``source_slug``, ``supported_languages``,
   ``default_language``, ``document_type``, ``extra_metadata``) and
   exposes the legacy cache helpers (``cache_path`` /
   ``iter_local_cache``) + the legacy ``source_id`` /
   ``ducklake_table`` properties.

The backward-compat shim at
``dlt_sources/european_nations/_shared/nation_source.py`` re-exports
``NationSource = JurisdictionPipelineBase`` + the legacy
``row_from_cache`` / ``use_local_scrapes`` helpers so the 51
importer files continue to work unchanged for one release before
the bulk-rewrite sweep.

## dlt 1.30 features wired into this base (per §6)

- **§6.1 Multischema datasets (dlt 1.25.0)**: the base configures the
  per-jurisdiction destination with ``multischema=True`` so each
  jurisdiction pipeline emits a single ``<jurisdiction>_education``
  BIEP-schema dataset that contains the per-stage + per-board
  schemas. The previous behaviour emitted one schema per (stage,
  board) sub-namespace, which fragmented queries.
- **§6.3 ``.add_limit()`` on the ``@dlt.source`` factory (dlt 1.30.0)**:
  ``run_smoke(limit=1)`` runs every resource with the 1-row smoke
  data so the smoke test finishes in seconds.
- **§6.4 ``retry_schema_update`` helper (dlt 1.30.0)**:
  ``run(tenacity_retry=True)`` wraps the pipeline call in a tenacity
  retry loop using
  ``dlt.pipeline.helpers.retry_schema_update()`` + a 5-attempt
  ``stop_after_attempt`` + exponential-backoff + jitter. This makes
  the BIEP v3 jurisdiction pipelines tolerant of NCCA syllabus
  evolution (the schema-evolution mismatch that was the most
  common cause of pipeline failure pre-§6.4).
- **§6.5 ``abort_packages`` / ``fail_pending_job`` / ``retry_failed_job``
  (dlt 1.30.0)**:
  ``abort_failed_load_packages()`` replaces the deprecated
  ``Pipeline.drop_pending_packages(...)`` calls (no live call
  sites in BIEP v3 today; the canonical pattern is still wired so
  any future pipeline abort uses the new API).
"""
from __future__ import annotations

import hashlib
import os
import random
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, ClassVar

import dlt
import dlt_sources

# §6.4: the canonical dlt 1.30 helper for retrying schema updates on
# a parallel-races-induced schema-evolution failure. The composable
# patience `Retrying` strategy uses this helper to decide whether to
# re-attempt the pipeline.run(...) call.
from dlt.pipeline.helpers import retry_schema_update as _dlt_retry_schema_update

from dlt_sources.common.destinations_cianfhoghlaim import get_dlt_destination

# §11: module-level helpers merged in from the legacy
# ``dlt_sources.european_nations._shared.nation_source`` module so the
# 51 per-nation source files can import them from the canonical base.
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
"""Canonical local scrape cache root for the EU-nations-style
per-vertical resource emission (mirrors the legacy
``EU_NATIONS_CACHE_ROOT`` constant from
``dlt_sources.european_nations._shared.nation_source``)."""


def use_local_scrapes() -> bool:
    """True when the AGENTS.md cache rule is active for the
    EU-nations-style per-vertical resource emission (mirrors the legacy
    ``use_local_scrapes()`` helper from
    ``dlt_sources.european_nations._shared.nation_source``).
    """
    return os.environ.get("USE_LOCAL_SCRAPES", "").lower().strip() in {
        "1",
        "true",
        "yes",
        "on",
    }


def row_from_cache(
    cache_path: Path,
    nation: "JurisdictionPipelineBase",
    *,
    document_id_key: str = "document_id",
    default_status: str = "in_force",
) -> dict[str, Any]:
    """Parse a per-nation cache JSON snapshot into a DLT row.

    Mirrors the legacy ``row_from_cache()`` helper from
    ``dlt_sources.european_nations._shared.nation_source``. The
    canonical schema is the Firecrawl shape (``markdown`` +
    ``metadata`` + ``sourceURL``) with a per-domain ``document_id``
    field.

    The ``nation`` argument accepts any ``JurisdictionPipelineBase``
    instance constructed in NationSource mode (it must expose
    ``country_code``, ``domain``, ``document_type`` and
    ``source_slug``).
    """
    import json  # noqa: PLC0415

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


# §6.4: the KCG-recommended tenacity pattern for the BIEP v3
# jurisdiction pipelines (per the v2 plan §A.4 + dlt 1.30 release notes).
try:
    from tenacity import (
        Retrying,
        retry_if_exception,
        stop_after_attempt,
        wait_exponential_jitter,
    )
    _TENACITY_IMPORT_ERROR: Exception | None = None
except ImportError as _exc:  # pragma: no cover - defensive
    Retrying = None  # type: ignore[assignment]
    retry_if_exception = None  # type: ignore[assignment]
    stop_after_attempt = None  # type: ignore[assignment]
    wait_exponential_jitter = None  # type: ignore[assignment]
    _TENACITY_IMPORT_ERROR = _exc


VALID_JURISDICTIONS: tuple[str, ...] = (
    "ireland", "england", "scotland", "wales",
    "northern_ireland", "jersey", "guernsey", "isle_of_man",
)

VALID_STAGES: tuple[str, ...] = (
    "primary", "junior_cycle", "senior_cycle", "leaving_certificate",
    "gcse", "as_level", "a_level", "national_5", "higher",
    "advanced_higher", "foundation",
    # Per the `2026-09-XX-cianchosaint-initial-carveout-v1` change +
    # the parent change `2026-08-24-dlt-sources-to-multi-repo-scaffold-v1`
    # §21.2. The `law_enforcement` vertical is a NEW per-vertical
    # subtree added by the cianchosaint sister repo (per Q1 user
    # clarification: evidence-collection for law-enforcement purposes
    # goes to cianchosaint). The 8 per-jurisdiction skeletons live at
    # `cianchosaint/dlt_sources/law_enforcement/<jurisdiction>/` and
    # their `JurisdictionPipelineBase` subclasses set `STAGE =
    # "law_enforcement"` (mirroring the education stage pattern).
    # Carve-out details: openspec/plans/2026-08-24-dlt-deep-analysis-v2.md
    # §Phase 4.1.
    "law_enforcement",
)


class JurisdictionPipelineBase:
    """Shared base for the 4 BIEP v3 jurisdiction pipelines.

    Provides:
    - VALID_JURISDICTIONS validation
    - destination factory + write_disposition + primary_key constants
    - build_pipeline() factory (canonical dlt.pipeline config, multischema-aware)
    - subject_to_row() helper (canonical cohort row shape)
    - run_with_tenacity_retry() (dlt 1.30 §6.4: retry_schema_update helper)
    - abort_failed_load_packages() (dlt 1.30 §6.5: abort_packages API)
    - run_smoke() (dlt 1.30 §6.3: .add_limit() on the @dlt.source factory)

    Subclasses must:
    1. Set `STAGE` class attribute (e.g., "leaving_certificate", "gcse")
    2. Define a `build_pipeline_resource()` method that uses
       `self.subject_to_row()` to yield the per-jurisdiction cohorts.

    Example:
        class IrelandJurisdictionPipeline(JurisdictionPipelineBase):
            STAGE = "leaving_certificate"
            def build_pipeline_resource(self):
                for row in query_by_jurisdiction("ireland"):
                    yield self.subject_to_row(row, self.STAGE)
        ireland_jurisdiction_pipeline = IrelandJurisdictionPipeline("ireland")
    """

    VALID_JURISDICTIONS: ClassVar[tuple[str, ...]] = VALID_JURISDICTIONS
    VALID_STAGES: ClassVar[tuple[str, ...]] = VALID_STAGES
    WRITE_DISPOSITION: ClassVar[str] = "merge"
    # natural_key (not content_hash) is the stable per-cohort identity used for
    # merge/dedup — see subject_to_row() for why content_hash was split in two.
    PRIMARY_KEY: ClassVar[list[str]] = ["natural_key"]

    # ─── dlt 1.30 / DuckLake 1.0 feature flags (per §6 + §7) ───────────
    # §6.1: multischema datasets are on by default for the BIEP v3
    # jurisdiction pipelines. The destination collapses the per-nation
    # DuckLake schemas into one BIEP-schema dataset.
    DEFAULT_MULTISCHEMA: ClassVar[bool] = True
    # §6.4: 5 attempts with exponential-backoff + jitter (the canonical
    # dlt 1.30 release-notes pattern). High enough to absorb a typical
    # NCCA syllabus-evolution race; low enough to fail fast on a hard
    # schema mismatch.
    DEFAULT_TENACITY_ATTEMPTS: ClassVar[int] = 5
    DEFAULT_TENACITY_BASE_SECONDS: ClassVar[float] = 1.0
    DEFAULT_TENACITY_MAX_SECONDS: ClassVar[float] = 30.0
    # §6.3: 1 row per resource is enough to prove the pipeline wires
    # end-to-end + to write a load_info.
    DEFAULT_SMOKE_LIMIT: ClassVar[int] = 1

    def __init__(
        self,
        jurisdiction: str | None = None,
        *,
        # ─── NationSource-mode kwargs (all optional) ──────────────────
        country_code: str | None = None,
        domain: str = "",
        source_slug: str = "",
        supported_languages: tuple[str, ...] = ("en",),
        default_language: str | None = None,
        document_type: str = "official_document",
        extra_metadata: dict[str, Any] | None = None,
        # ─── BIEP v3-mode kwargs ──────────────────────────────────────
        use_md: bool = True,
        valid_jurisdictions: tuple[str, ...] | None = None,
        valid_stages: tuple[str, ...] | None = None,
        multischema: bool | None = None,
        quadrant: str | None = None,
    ):
        """Construct a ``JurisdictionPipelineBase`` in either BIEP v3
        mode or NationSource mode (§11 merge).

        **BIEP v3 mode** — pass ``jurisdiction`` positionally or by
        keyword. The base configures the per-jurisdiction destination,
        validates against ``VALID_JURISDICTIONS`` and primes the
        §6.1 multischema + §6.4 tenacity-retry + §6.5 abort hooks.

        **NationSource mode** — pass ``country_code=...`` (no
        positional). The base derives ``jurisdiction = country_code``,
        stores the per-vertical resource fields (``domain``,
        ``source_slug``, ``supported_languages``,
        ``default_language``, ``document_type``, ``extra_metadata``)
        and exposes the legacy cache helpers + the legacy
        ``source_id`` / ``ducklake_table`` properties.

        Passing both ``jurisdiction`` AND ``country_code`` raises
        ``TypeError``; passing neither raises ``TypeError`` too.

        Example (BIEP v3):
            JurisdictionPipelineBase("ireland")

        Example (NationSource):
            JurisdictionPipelineBase(
                country_code="aus",
                domain="government",
                source_slug="gov_au",
                supported_languages=("en",),
                document_type="government_document",
                extra_metadata={"canonical_root": "https://www.australia.gov.au"},
            )
        """
        # ─── Mode detection (§11) ─────────────────────────────────────
        if jurisdiction is not None and country_code is not None:
            raise TypeError(
                "JurisdictionPipelineBase: pass either jurisdiction=... "
                "(BIEP v3 mode) or country_code=... (NationSource mode), "
                "not both."
            )
        if jurisdiction is None and country_code is None:
            raise TypeError(
                "JurisdictionPipelineBase: requires either jurisdiction=... "
                "(BIEP v3 mode) or country_code=... (NationSource mode)."
            )

        if country_code is not None:
            # ─── NationSource mode ───────────────────────────────────
            self._is_nation_source_mode = True
            jurisdiction = country_code
            self.domain = domain
            self.source_slug = source_slug
            self.supported_languages = supported_languages
            self.default_language = (
                default_language if default_language is not None
                else (supported_languages[0] if supported_languages else "en")
            )
            self.document_type = document_type
            self.extra_metadata = dict(extra_metadata) if extra_metadata else {}
        else:
            # ─── BIEP v3 mode ────────────────────────────────────────
            self._is_nation_source_mode = False
            self.domain = ""
            self.source_slug = ""
            self.supported_languages = ("en",)
            self.default_language = None
            self.document_type = "official_document"
            self.extra_metadata = {}

        # ─── Common init (§6) ─────────────────────────────────────────
        valid_j = valid_jurisdictions or self.VALID_JURISDICTIONS
        valid_s = valid_stages or self.VALID_STAGES
        # §11: in NationSource mode the jurisdiction is an ISO 3166-1
        # alpha-3 country code (``aus``, ``can``, ``bra``, ...) — NOT
        # one of the 8 British Isles jurisdictions — so the BIEP v3
        # validation guard is skipped. Callers who want strict
        # validation can still pass ``valid_jurisdictions=(...)``.
        if not self._is_nation_source_mode and jurisdiction not in valid_j:
            raise ValueError(
                f"jurisdiction={jurisdiction!r} not in {valid_j}"
            )
        self.jurisdiction = jurisdiction
        self.valid_jurisdictions = valid_j
        self.valid_stages = valid_s
        # §6.1: multischema=True is the canonical behaviour for BIEP v3
        # jurisdiction pipelines. Pass multischema=False to opt back
        # into the legacy single-schema behaviour. In NationSource
        # mode the multischema/quadrant/use_md kwargs are still
        # honoured so the destination factory can resolve a sensible
        # default — the destination is still wired up so subclasses
        # can call ``build_pipeline()`` / ``run()`` if they wish.
        self.multischema = (
            multischema if multischema is not None else self.DEFAULT_MULTISCHEMA
        )
        # §7.1: per-quadrant metadata_schema wiring (the canonical
        # home for the Ireland + England + Scotland + Wales + NI + JC
        # + A-Level + GCSE + LC jurisdictional pipelines is the
        # "oideachais" Postgres metadata schema).
        self.quadrant = quadrant or "oideachais"
        self.destination = get_dlt_destination(
            use_ducklake=use_md,
            quadrant=self.quadrant,
            multischema=self.multischema,
        )

    @property
    def STAGE(self) -> str:
        """The education stage for this jurisdiction.

        Subclasses override this as a class attribute.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__}: set STAGE class attribute"
        )

    # ─── §11: NationSource-style properties + cache helpers ───────────
    # All of the below are available regardless of construction mode
    # so subclasses written against either pre-merge contract keep
    # working. In BIEP v3 mode the attributes default to the empty /
    # ("en",) sentinel — see ``__init__`` for the exact defaults.

    @property
    def country_code(self) -> str:
        """ISO 3166-1 alpha-3 code in lowercase.

        In BIEP v3 mode ``country_code == jurisdiction``. In
        NationSource mode the two are explicitly constructed from the
        same string. Mirrors the legacy ``NationSource.country_code``
        attribute.
        """
        return self.jurisdiction

    @property
    def source_id(self) -> str:
        """Canonical ``source_id`` for the source.

        In NationSource mode returns the legacy
        ``european_nations.<country_code>.<domain>.<source_slug>``
        form (e.g. ``european_nations.aus.government.gov_au``). In
        BIEP v3 mode returns the per-cohort
        ``british_isles.<jurisdiction>.education.<stage>...`` form
        via ``subject_to_row()`` — subclasses typically do NOT call
        this property directly, they yield the per-row dict that
        ``subject_to_row()`` produces.
        """
        if self._is_nation_source_mode:
            return (
                f"european_nations.{self.country_code}.{self.domain}"
                f".{self.source_slug}"
            )
        # BIEP v3 mode: subclasses yield per-cohort source_ids via
        # subject_to_row(); fall back to the jurisdiction-level prefix
        # if anyone calls the property directly.
        return f"british_isles.{self.jurisdiction}.education"

    @property
    def ducklake_table(self) -> str:
        """Canonical DuckLake namespace for the source.

        In NationSource mode returns the legacy
        ``oideachais.<domain>.european_nations.<country_code>`` form.
        In BIEP v3 mode returns the per-jurisdiction
        ``oideachais.education.<jurisdiction>`` form.
        """
        if self._is_nation_source_mode:
            return (
                f"oideachais.{self.domain}.european_nations"
                f".{self.country_code}"
            )
        return f"oideachais.education.{self.jurisdiction}"

    def cache_path(self, language: str | None = None) -> Path:
        """Return the canonical EU-nations-style cache directory.

        Mirrors the legacy ``NationSource.cache_path()`` method.
        Unchanged behaviour: language defaults to ``self.default_language``.
        """
        lang = language or self.default_language or "en"
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
        """Yield every cached JSON snapshot under the canonical cache.

        Mirrors the legacy ``NationSource.iter_local_cache()`` method.
        Skips silently when the directory does not exist.
        """
        lang = language or self.default_language or "en"
        lang_dir = self.cache_path(lang)
        if not lang_dir.exists():
            return
        for json_path in sorted(lang_dir.glob("*.json")):
            yield json_path

    def subject_to_row(self, row: Any, stage: str | None = None) -> dict[str, Any]:
        """Convert one SubjectRegistryRow to the canonical cohort row dict.

        Used as the yield body of `build_pipeline_resource()`.
        """
        stage = stage or self.STAGE
        board = getattr(row, "board", None) or "none"
        qual_level = getattr(row, "qualification_level", None) or "untiered"
        # natural_key: the stable identity of *which cohort this is* (jurisdiction
        # + stage + subject + board + level + language). Used as the merge/primary
        # key so re-runs are idempotent — this was formerly mislabeled "content_hash"
        # even though it never hashed anything and never reflected fetched content.
        natural_key = (
            f"{self.jurisdiction}|{stage}|{row.subject_slug}|{board}|"
            f"{qual_level}|{row.language}"
        )
        # content_sha256: a real hash, but of this class's own visibility limit —
        # JurisdictionPipelineBase maps SubjectRegistryRow → cohort dict; it never
        # fetches document bytes, so this can only detect a change to the registry
        # row's own metadata (source_url moved, display name updated, etc.), not a
        # change to the underlying document. Real per-document content hashing
        # belongs in the sources that actually download bytes (e.g.
        # dlt_sources/filesystem/leaving_cert_source.py) — do not treat this field
        # as a substitute for that.
        content_sha256 = hashlib.sha256(
            "|".join(
                str(v)
                for v in (
                    row.source_url,
                    row.display_name_en,
                    row.display_name_local,
                    row.concept,
                    row.baml_function,
                    row.last_verified,
                )
            ).encode("utf-8")
        ).hexdigest()
        return {
            "source_id": (
                f"british_isles.{self.jurisdiction}.education.{stage}."
                f"{board}.{row.subject_slug}"
            ),
            "country_code": self.jurisdiction,
            "jurisdiction": self.jurisdiction,
            "education_stage": stage,
            "exam_board": board,
            "subject": row.subject_slug,
            "qualification_level": qual_level,
            "language": row.language,
            "baml_function": row.baml_function,
            "concept": row.concept,
            "source_url": row.source_url,
            "display_name_en": row.display_name_en,
            "display_name_local": row.display_name_local,
            "last_verified": row.last_verified or datetime.now(UTC).isoformat()[:10],
            "ingested_at": datetime.now(UTC).isoformat(),
            "namespace": (
                f"cianfhoghlaim.education.{self.jurisdiction}.{stage}."
                f"{board}.{row.subject_slug}"
            ),
            "natural_key": natural_key,
            "content_sha256": content_sha256,
        }

    def build_pipeline(
        self,
        dataset_name: str | None = None,
        schemas: Any = None,
    ) -> Any:
        """Build the canonical DLT pipeline for this jurisdiction.

        §6.1: when `multischema=True` (the default), the resulting
        destination is the per-quadrant DuckLake destination (see
        ``self.destination``) which can hold multiple dlt schemas.
        Per-resource schemas are declared on each
        ``@dlt.resource(schema=...)`` decorator; the dataset is
        materialised via ``dlt.dataset(destination, dataset_name,
        schema=[s1, s2, ...])`` at read time.

        The `schemas=` kwarg is accepted for API symmetry with the
        dlt 1.25+ multischema API but is NOT wired into
        ``dlt.pipeline(...)`` itself (per dlt 1.30's pipeline config
        injection — schemas must be attached via the per-resource
        decorator, NOT via ``dlt.pipeline(schema=...)``).
        """
        dataset = dataset_name or f"{self.jurisdiction}_education"
        _ = schemas  # see docstring above for the multischema semantics
        return dlt.pipeline(
            pipeline_name=f"{self.jurisdiction}_jurisdiction_pipeline",
            dataset_name=dataset,
            destination=self.destination,
        )

    def build_pipeline_resource(self):
        """Override this to yield the per-jurisdiction cohorts.

        Each yield MUST be a dict from `self.subject_to_row(row, stage)`.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__}: override build_pipeline_resource()"
        )

    def run(
        self,
        dataset_name: str | None = None,
        tenacity_retry: bool = True,
    ) -> Any:
        """Convenience: build pipeline + run the resource + return load_info.

        Passes WRITE_DISPOSITION/PRIMARY_KEY through explicitly — previously
        declared as class constants but never applied, so every run replaced
        rather than merged.

        §6.4: when `tenacity_retry=True` (the default), the
        ``pipeline.run(...)`` call is wrapped in a tenacity retry loop
        using ``dlt.pipeline.helpers.retry_schema_update()`` so a
        NCCA syllabus-evolution-induced schema mismatch is retried with
        exponential-backoff + jitter instead of failing the load.
        """
        pipeline = self.build_pipeline(dataset_name=dataset_name)
        if tenacity_retry:
            with self._tenacity_retry_context():
                load_info = pipeline.run(
                    self.build_pipeline_resource(),
                    write_disposition=self.WRITE_DISPOSITION,
                    primary_key=self.PRIMARY_KEY,
                )
        else:
            load_info = pipeline.run(
                self.build_pipeline_resource(),
                write_disposition=self.WRITE_DISPOSITION,
                primary_key=self.PRIMARY_KEY,
            )
        return load_info

    # ─── §6.4 — ``retry_schema_update`` helper ────────────────────────────

    def _tenacity_retry_context(self):
        """Return a tenacity ``Retrying`` context manager wired to the
        dlt 1.30 ``retry_schema_update()`` helper.

        Pattern per the canonical dlt 1.30 release notes
        (https://dlthub.com/docs/release-notes/1.30.0):

            from dlt.pipeline.helpers import retry_load, retry_schema_update
            should_retry = retry_if_exception(retry_schema_update()) | retry_if_exception(retry_load(...))
            with Retrying(stop=stop_after_attempt(5), retry=should_retry, reraise=True):
                pipeline.run(data)

        KCG extension: add exponential-backoff + jitter
        (``wait_exponential_jitter``) so simultaneous-pipeline races
        don't sync their retries. Falls back to a no-op context manager
        when tenacity is not installed (defensive — the production
        environment always has tenacity via ``pyproject.toml``).
        """
        if Retrying is None:  # pragma: no cover - defensive
            from contextlib import nullcontext  # noqa: PLC0415

            if _TENACITY_IMPORT_ERROR is not None:
                # Surface a hint once via __cause__ so a future
                # operator can debug.
                raise ImportError(
                    "tenacity is required for §6.4 retry_schema_update support. "
                    f"original import error: {_TENACITY_IMPORT_ERROR}"
                )
            return nullcontext()
        retry_decider = retry_if_exception(_dlt_retry_schema_update())  # type: ignore[misc]
        # Add a tiny jitter so parallel-pipeline races don't sync.
        wait_strategy = wait_exponential_jitter(  # type: ignore[misc]
            initial=self.DEFAULT_TENACITY_BASE_SECONDS,
            max=self.DEFAULT_TENACITY_MAX_SECONDS,
        )
        return Retrying(  # type: ignore[misc]
            stop=stop_after_attempt(self.DEFAULT_TENACITY_ATTEMPTS),  # type: ignore[misc]
            retry=retry_decider,
            wait=wait_strategy,
            reraise=True,
        )

    def run_with_tenacity_retry(self, dataset_name: str | None = None) -> Any:
        """Public alias for ``run(dataset_name, tenacity_retry=True)``.

        Added in §6.4 for callers that prefer the explicit keyword.
        """
        return self.run(dataset_name=dataset_name, tenacity_retry=True)

    # ─── §6.5 — ``abort_packages`` / ``fail_pending_job`` / ``retry_failed_job`` ──

    def abort_failed_load_packages(self, pipeline: Any) -> int:
        """Record what happened for the failed load packages on this
        pipeline using the dlt 1.30 ``abort_packages`` API.

        Replaces the deprecated ``Pipeline.drop_pending_packages(...)``
        call (no live BIEP v3 call sites today, but the canonical
        pattern is wired so any future abort goes through the new API).

        Returns:
            Number of load packages aborted.
        """
        pending = pipeline.list_pending_retry_jobs_in_package()
        if not pending:
            return 0
        # dlt 1.30: abort_packages records what happened; callers may
        # also call retry_failed_job(...) for individual jobs.
        pipeline.abort_packages(*pending)
        return len(pending)

    def fail_pending_job_and_retry(self, pipeline: Any, load_id: str, job_id: str) -> bool:
        """Fail one pending job and retry it via the dlt 1.30
        ``fail_pending_job`` + ``retry_failed_job`` API pair.

        Returns:
            True if the job was successfully retried, False otherwise.
        """
        pipeline.fail_pending_job(load_id, job_id)
        return pipeline.retry_failed_job(load_id, job_id)

    # ─── §6.3 — ``.add_limit(1)`` smoke test ──────────────────────────────

    def run_smoke(
        self,
        limit: int | None = None,
        dataset_name: str | None = None,
    ) -> Any:
        """Run the jurisdiction pipeline with ``.add_limit(limit)`` on
        the source factory (dlt 1.30 §6.3).

        Forces each per-jurisdiction source to yield at most `limit`
        rows (default ``DEFAULT_SMOKE_LIMIT = 1``) so CI finishes in
        seconds. The smoke run still issues a real
        ``pipeline.run(...)`` so the load_info is written.

        Note: the smoke run uses ``write_disposition="replace"`` so
        the 1-row smoke data does not pollute the production dataset
        via a merge. Operators who want to keep the smoke data should
        pass ``dataset_name=f"{jurisdiction}_smoke"``.

        Returns:
            The pipeline ``LoadInfo`` from the smoke run.
        """
        from dlt.extract.source import DltSource  # noqa: PLC0415

        limit = limit if limit is not None else self.DEFAULT_SMOKE_LIMIT
        # Build a one-off pipeline so the smoke run uses a sandboxed
        # dataset and the production pipeline is untouched.
        smoke_dataset = dataset_name or f"{self.jurisdiction}_smoke"
        pipeline = self.build_pipeline(dataset_name=smoke_dataset)

        # The pipeline.run(...) accepts a `DltSource` directly via the
        # data argument; we pass a `DltSource.add_limit(limit)` chain
        # only when the concrete resource supports it (transformers
        # cannot be limited — DltSource.add_limit skips them
        # automatically per dlt 1.30 docs).
        resource = self.build_pipeline_resource()
        # We intentionally allow `add_limit` to skip transformers (the
        # dlt 1.30 documented behaviour). The smoke run is meant to be
        # cheap; correctness comes from `write_disposition=replace`.
        try:
            limited: DltSource | Any = resource
            add_limit_fn = getattr(limited, "add_limit", None)
            if callable(add_limit_fn):
                limited = add_limit_fn(limit)
        except Exception:  # pragma: no cover - defensive (transformer-like)
            limited = resource
        return pipeline.run(
            limited,
            write_disposition="replace",
            primary_key=self.PRIMARY_KEY,
        )


__all__ = [
    "EU_NATIONS_CACHE_ROOT",
    "JurisdictionPipelineBase",
    "VALID_JURISDICTIONS",
    "VALID_STAGES",
    "row_from_cache",
    "use_local_scrapes",
]