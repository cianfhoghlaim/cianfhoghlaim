"""Cianfhoghlaim — consolidated Celtic education + multi-nation + multi-language data platform.

Plan 1 (active): Ireland (early childhood / primary / junior cycle / senior cycle / Leaving Cert)
in EN + GA, plus the leabharlann corpus (6 subdirs, 216 documents).

Plan 2 (preserved as stubs): UK 4-nation + Isle of Man — full education sources.

Plan 3 (preserved as stubs): UK 4-nation + IoM — 7 domains (law, medicine, culture,
government, intelligence, statistics, geospatial).

Legacy (preserved as stubs): Jersey + Guernsey (Crown Dependencies).

The package is the single workspace root after the v4 consolidation
(see openspec/changes/2026-06-28-consolidate-sruth-into-cianfhoghlaim-v4/).
The 5 former quadrants (oideachais, meaisinfhoghlaim, tuatha, croilar, crypteolas)
are now sub-trees under cianfhoghlaim/{core,pipelines,sources,assets,agents,notebooks,
stacks,web,ocr,embeddings,cognify,leabharlann,libraries,docs/legacy}/.

Layout
------

* ``core/``          — 16 first-class stack packages (dlt, duckdb, ducklake, lancedb,
  motherduck, cocoindex, baml, marimo, browser, cognee, obs, rag, search,
  curriculum, config, memory).
* ``pipelines/``     — 5-stage pipeline spine (browser → ingest → distribute → process
  → expose + sensors/).
* ``sources/``       — language-first + nation-only source files (7 languages × 6 active
  nations × 8 domains).
* ``assets/``        — Dagster assets, ConfigurableResources, and 4 successive
  independent asset gen pipelines.
* ``agents/``        — 12-agent fleet + ADK + MCP + API + image pipeline + language.
* ``notebooks/``     — marimo reactive notebooks.
* ``stacks/``        — 33 user-pre-selected selfhosted Docker stacks.
* ``web/``           — TanStack Start + Hono + Bun frontends.
* ``ocr/``           — 11 vision models + 4 classical Docker OCR + evaluation harness.
* ``embeddings/``    — embedding pipelines (legacy + v1).
* ``cognify/``       — Cognee cognitive graph rules.
* ``leabharlann/``   — Personal archive corpus (6 subdirs × 216 docs).
* ``libraries/``     — Publishable sub-packages (codelas).
* ``docs/legacy/``   — Frozen snapshots (crypteolas, WoW, Hades II, _game).
* ``tests/``         — Test suites.
* ``scripts/``       — Build / lint / utility scripts.

NOTE: Source schema layout is provisional — refactor after Plan 1 informs best
CocoIndex + DLT + DuckDB + DuckLake + Lance patterns.
"""

__version__ = "0.1.0"
__plan__ = "v4-consolidation (Plan 1: Ireland + leabharlann active)"
__openspec_change__ = "2026-06-28-consolidate-sruth-into-cianfhoghlaim-v4"
__active_nations__ = ("ie", "en", "ni", "wls", "sct", "iom")  # 6 active; +2 legacy (jey, ggy)
__active_languages__ = ("english", "gaeilge")  # Plan 1 active; +5 Celtic (cymraeg, gaidhlig, gaelg, kernewek, brezhoneg)
__active_surfaces__ = ("ireland_education", "leabharlann")  # Plan 1; +Plan 2 UK nations + Plan 3 domains (preserved as stubs)
__status__ = "in-progress (consolidation complete, Plan 1 not yet launched)"
