# Change: Lakehouse extensive hydration (DuckDB/DuckLake-first, real OCR/VLM)

## Why

The platform's "docs-informed extraction, OCR/VLM via litellm/llama-swap,
DuckDB/DuckLake-first investigation notebooks" story is real in its
architecture and mostly broken in its wiring — a correct piece of
underlying code exists for almost every capability, but the path
supposed to use it in production either doesn't call it, calls it
wrong, or was never turned on.

**OCR/VLM**: the entire live LC syllabus/exam-paper/marking-scheme
extraction pipeline was text-only (pymupdf `page.get_text()`, never a
rendered page image). `ExtractSyllabusDiagram` was declared
`client BIEPV3Vision` (a real, correctly-configured vision client
routing through litellm → llama-swap → qwen3-vl-8b) but had no `image`
parameter at all — vision framing with no pixels behind it. The "4-path
OCR/VLM ensemble" (`meaisinfhoghlaim/ocr/ensemble/ensembled_extractor.py`)
had 2 of 4 paths sending a text string containing a local filesystem
path instead of actual image bytes, and was missing `import json`
entirely (every success-path `json.dumps(data)` call would have raised
`NameError`). `llama-swap` was simply missing from
`deployment-choice.yaml`'s `enabled_stacks:` list.

**DuckDB/DuckLake infrastructure**: Garage S3 and the DuckLake
`ATTACH 'ducklake:postgres:...'` pattern were real, but 4+ divergent
client implementations disagreed on catalog backend and env var names,
and the one Dagster resource meant to expose DuckLake
(`orchestration/resources.py::DuckLakeResource`) imported a module
(`storage.ducklake_client`) that didn't exist anywhere in the repo — a
hard `ModuleNotFoundError` for every caller. The Dagster-orchestrated
ingestion asset used `destination="duckdb"` (ephemeral local file), so
running it through Dagster never actually reached the lakehouse. Three
scripts had an identical hardcoded plaintext Postgres password checked
into git.

**Notebook investigation surface**: of the 17 `notebooks/
10_biep_pipeline_lakehouse_*` marimo notebooks — the "recently updated
notebooks" meant to be the DuckDB/DuckLake-first investigation
surface — 7 had hard `SyntaxError`s from a botched refactor (an
unindented `import ibis` line landed inside function bodies), and
re-indenting surfaced 3 further latent `NameError` bugs (a name imported
in one cell, used in another, never round-tripped through the marimo
cell dependency graph) plus a real `ibis.ibis.duckdb.connect()`
double-prefix typo.

**Live infrastructure**, once actually brought up (Garage + Postgres +
litellm), surfaced 2 more real bugs no code review would have found: the
litellm proxy's own `router_settings.fallbacks` config was malformed
(a bare list of model-name strings; litellm's `Router.validate_fallbacks()`
requires each entry to be a dict) and crash-looped the entire litellm
container on every startup attempt — confirmed via live `docker logs`.
And the documented "canonical" DuckLake bucket name
(`ducklake-cianfhoghlaim`) turned out to be wrong against the actual
live catalog (`ducklake`), discovered only by attempting a real `ATTACH`
and reading the resulting error.

This change fixes all of the above and runs the real hydration pass
those fixes unlock: the full 13-subject/139-document local
`leaving_certificate/` corpus scanned and loaded into the live DuckLake
catalog, with real MiniMax-primary/Qwen-secondary cross-check extraction
on each subject's syllabus.

## What Changes

- Fix the broken `DuckLakeResource`, the wrong-destination Dagster
  asset, the 3 hardcoded passwords (moved to the existing Infisical-
  first/`.env.dev`-fallback `POSTGRES_PASSWORD` convention already used
  by `bonneagar/stacks/lakehouse/secrets.env`), the dangling
  `garage_pdf_arrival_sensor` job reference, the wrong package path in
  `pdf_factory.py`'s `CONVERTER_REGISTRY`, and all 10 of the 17
  notebooks with real code bugs (7 syntax errors + 3 latent
  `NameError`s + 1 wrong path + 1 double-prefix typo) — zero live
  services required for any of this.
- Consolidate the 4+ divergent DuckLake client implementations onto
  `dlt_sources/common/destinations_cianfhoghlaim.py` (the only one using
  dlt's native `DuckLakeCredentials` config object), and correct its
  bucket-name default from the never-actually-verified
  `ducklake-cianfhoghlaim` to the live-verified real value `ducklake`.
- Add a real `image: image[]?` parameter to `ExtractSyllabusDiagram`
  (backwards-compatible), a new `pdf_to_image_bridge.py` adapter
  (pymupdf-based page rendering → `baml_py.Image`, self-contained rather
  than importing the separate `sruth/shared/` workspace), and wire it
  into both `fibo_configs_from_syllabus_diagrams` and one un-stubbed
  Dagster asset (`lc5_chemistry_diagrams_extracted`) — both live-verified
  to render real page images and construct correct multimodal BAML
  requests, up to the network boundary.
- Fix the 4-path OCR ensemble's `_call_qwen3_vl`/`_call_gemma4` to send
  real image payloads instead of a filesystem-path string, and fix the
  missing `import json`.
- Fix a real, live-discovered litellm config bug (malformed
  `router_settings.fallbacks`) at its source (the config generator
  script) and in the checked-in generated config — flagged, not
  silently worked around, that the actually-deployed instance is a
  separate Komodo-managed stack outside this repo/worktree that needs a
  manual redeploy to pick up the fix.
- New `scripts/hydrate_lc_full_corpus.py`: the real hydration pass,
  extending `scripts/load_lc_chemistry_pilot.py`'s proven 1-subject
  pattern to all 13 local subjects, against the real local DuckLake
  catalog (not the MotherDuck fallback the pilot script needed, since
  the local stack is confirmed live here).
- Restore the notebook investigation surface as genuinely usable:
  replace silent fabricated-data fallbacks with visible warnings, and
  fix the connection-fallback order now that local DuckLake is
  confirmed live.

## Dependencies

`Blocked by: none`. `Blocked by (soft):
2026-08-08-docs-informed-quest-and-credential-generation-v1` (the
`ExtractSyllabusDiagram` image param builds on that change's earlier
fix of the systemic BAML role-marker bug, and reuses its
`_classify_pdfs`-style PDF classification pattern). `Affected repos:
cianfhoghlaim (single repo)`, plus one live-infra-only fix
(`~/.komodo-stacks/litellm/config/config.yaml`) explicitly flagged as
outside repo scope, requiring a manual operator action to actually take
effect on the running service.

## Impact

- Capabilities: NEW `duckdb-ducklake-lakehouse-hydration`.
- Code: `orchestration/resources.py`, `orchestration/defs/2_materials/
  filesystem_pipelines/generic_filesystem_assets.py`,
  `orchestration/defs/2_materials/lc_extraction/lc5_assets.py`,
  `orchestration/sensors/garage_pdf_arrival_sensor.py`,
  `orchestration/sensors/__init__.py`, `orchestration/storage/
  ducklake_client.py`, `dlt_sources/common/destinations_cianfhoghlaim.py`,
  `meaisinfhoghlaim/document_factory/{pdf_factory.py,
  curriculum_document.py}` (fix), `meaisinfhoghlaim/document_factory/
  pdf_to_image_bridge.py` (new), `meaisinfhoghlaim/ocr/ensemble/
  ensembled_extractor.py`, `tuatha/asset_generation/fibo/assets.py`,
  `baml_src/british_isles/ireland/education/lc_extraction/
  syllabus_diagram.baml`, `scripts/{verify_ducklake_population.py,
  8_jurisdiction_overview.py, export_cohorts_to_lance.py,
  generate_litellm_config.py, hydrate_lc_full_corpus.py}` (new),
  `bonneagar/stacks/litellm/config/config.yaml`, `deployment-choice.yaml`,
  10 of the 17 `notebooks/10_biep_pipeline_lakehouse_*.py` files.
