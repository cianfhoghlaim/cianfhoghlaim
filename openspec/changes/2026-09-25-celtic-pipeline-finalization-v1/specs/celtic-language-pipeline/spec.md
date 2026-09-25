## ADDED Requirements

### Requirement: clp-1 — Unified BAML extraction for the 6 Celtic languages + EN

The cianfhoghlaim `baml_src/celtic/` + `baml_src/british_isles/` trees MUST provide at least one BAML extraction function per Celtic language: Irish (ga), Scottish Gaelic (gd), Welsh (cy), Manx (gv), Breton (br), Cornish (kw), plus English (en).

#### Scenario: 7 extractors reachable at runtime

- **WHEN** an operator runs `uv run python -c "from baml_client.sync_client import b; print([n for n in dir(b) if 'Syllabus' in n or 'Curriculum' in n or 'Grammar' in n])"`
- **THEN** the output MUST include at least 7 functions (one per language)

### Requirement: clp-2 — Per-language surface coverage (BAML + DLT + CocoIndex + Dagster + MotherDuck)

Each Celtic language MUST have at least: 1 BAML extractor, 1 DLT source, 1 CocoIndex App, 1 Dagster asset group, 1 MotherDuck Dive.

#### Scenario: 7 surfaces × 5 components

- **WHEN** an operator runs `find baml_src dlt_sources cocoindex_flows orchestration/defs motherduck/dives -name "*gael*"` (for Irish) + same for each language
- **THEN** each language MUST show ≥5 matching files

### Requirement: clp-3 — HuggingFace dataset integration per Celtic language

Each Celtic language MUST have at least 1 HuggingFace dataset integrated into the DLT pipeline (per the Phase 2 + Phase 4 HF inventory in `stedding/sister-lifts/WHOLESALE_COPY_INDEX.md`).

#### Scenario: 7 languages × ≥1 HF dataset

- **WHEN** an operator runs `grep -rl "huggingface\|load_dataset\|HfApi" dlt_sources/ | wc -l`
- **THEN** the output MUST be ≥7

### Requirement: clp-4 — CLARIN-UK VLO integration for Celtic languages

The CLARIN VLO HTTP client (wholesale-copied from ciancheiltis's `dlt_sources/language/clarin.py`) MUST be queryable from cianfhoghlaim for at least the 4 Celtic languages with public CLARIN VLO coverage (Irish, Welsh, Scottish Gaelic, Breton).

#### Scenario: 4 Celtic languages queryable via CLARIN VLO

- **WHEN** an operator runs `uv run python -c "from dlt_sources.language.clarin import ClarinVLOClient; c = ClarinVLOClient(); print(c.search('gaeilge', limit=5))"`
- **THEN** the output MUST include ≥1 result for each of the 4 Celtic languages

### Requirement: clp-5 — Wholesale-copy invariants from sister repos pass

Per `openspec/specs/sister-shared/spec.md` Shared-1..5, every wholesale-copied file MUST carry the `SisterLift:` provenance header, the wholesale-copy ledger MUST be in sync, and the per-sister `MODIFICATIONS.md` files MUST record local modifications.

#### Scenario: ledger-tracked files all have provenance

- **WHEN** an operator runs `uv run python scripts/sister_lifts.py verify`
- **THEN** the output MUST be `OK: all N ledger-tracked wholesale-copied files have SisterLift headers` with N ≥ the number of wholesale-copies recorded

### Requirement: clp-6 — End-to-end Celtic pipeline smoke test passes

The `tests/integration/test_full_celtic_pipeline.py` smoke test MUST pass on every CI run, exercising the full chain: BAML extraction → DLT write → CocoIndex embed → Dagster asset → MotherDuck Dive → marimo notebook.

#### Scenario: smoke test exits 0

- **WHEN** an operator runs `uv run pytest tests/integration/test_full_celtic_pipeline.py -v`
- **THEN** the output MUST be `passed` and the exit code MUST be 0
