# Orchestration — Dagster layer

> The canonical Dagster layer for the Cianfhoghlaim platform: a
> component-based pipeline that walks a corpus from raw disk to an
> agent-consumable, semantically-indexed artifact.

## What this is

`orchestration/` is a single Dagster code-location (`dg.toml` →
`orchestration.definitions`) that loads a mix of hand-written
`@asset`/`@sensor`/`@asset_check` Python decorators and YAML-declared
Dagster Components. Post-v7 flattening this module IS the Dagster
layer — there is no nested `cianfhoghlaim/dagster/` package.

## Architecture

Assets are organised into 7 numbered stage directories under
`orchestration/defs/`, plus a top-level `sensors/` directory:

```
1_ingestion/      DLT sources → DuckLake raw
2_materials/       BAML/Docling extraction → typed structures
3_model_lifecycle/ CocoIndex v1 embedding + Cognee cognify
4_asset_generation/ marimo dashboards + TanStack pages + oRPC routes
4_budget/           Firecrawl budget tracking
4_memory/           docs-index memory job
5_agent_ops/        the agent fleet (adk/agno/custom/meaisinfhoghlaim)
sensors/            change-detection + registry sensors (16 files)
```

`4_budget/` and `4_memory/` sit alongside `4_asset_generation/` as
siblings, not sub-stages — the numbering is "stage 4-ish", not
strictly sequential.

Each stage has a matching `Component` class in `orchestration/components/`
that `dg`-style YAML `defs.yaml` files instantiate:

| Component | File |
|:--|:--|
| `CelticIngestionComponent` | `components/layer1_ingestion.py` |
| `CelticMaterialsComponent` | `components/layer2_materials.py` |
| `CelticModelLifecycleComponent`, `CelticFederatedOcrComponent` | `components/layer3_model_lifecycle.py` |
| `CelticAssetGenerationComponent` | `components/layer4_asset_generation.py` |
| `CelticAgentOpsComponent` | `components/layer5_agent_ops.py` |
| `BIEPSubjectComponent` (base) | `components/biep_subject_component.py` |
| `EnglandBoardSubjectComponent` | `components/england_board_subject_component.py` |
| `EnglandCrossBoardComparatorComponent` | `components/england_cross_board_comparator_component.py` |
| `JuniorCycleSubjectComponent`, `JuniorCycleShortCourseComponent`, `JuniorCycleCBAComponent` | `components/junior_cycle_subject_component.py` |
| `KCGCognifyComponent`, `CognifyIngestSensorsComponent`, `KCGSubjectPilotFactoryComponent` | `components/kcg_cognify_component.py` |
| `BIEPOCREnsembleComponent` | `components/biiep_ocr_ensemble_component.py` |

`orchestration/components/__init__.py` is the registry surface —
every class instantiated from `defs.yaml` via `type:` must be
re-exported there, or Dagster raises `DagsterUnresolvableSymbolError`
at load time. Its own comments document three past rounds of exactly
that bug.

## Implementation decisions

- **Components over hand-written `@asset` per pipeline** — one
  `dg.Component` subclass per stage means a new per-jurisdiction or
  per-subject pipeline is a YAML `defs.yaml` entry, not a new Python
  file. `JurisdictionAssetsBase` (`defs/2_materials/_base/
  jurisdiction_assets_base.py`) takes this further: each of the 10
  British Isles jurisdictions becomes a ~30-line subclass instead of
  a ~380-line hand-written asset file.
- **R1–R4 static conformance checks at scaffold time** — before
  `CelticModelLifecycleComponent` emits a CocoIndex v1 App asset, it
  statically inspects the target module's source text for 4 required
  patterns (shared lifespan import, canonical ContextKeys, module-scope
  `coco.App(...)`, at least one `@coco.fn`) and raises
  `ConformanceViolation` with the exact rule + fix instructions if any
  are missing — catching a broken CocoIndex flow before Dagster ever
  tries to run it, not after.
- **Two sensor homes, not one** — `orchestration/defs/sensors/` (3
  files, auto-discovered by `dg.load_defs()`) and `orchestration/sensors/`
  (16 files: per-registry change-detection sensors, `ocr_completion_sensor.py`,
  `garage_pdf_arrival_sensor.py`, `upstream_breaking_change_sensor.py`).
  This split is a known rough edge, not a deliberate design — see
  Known gaps.

## Layout

| Path | Purpose |
|:--|:--|
| `orchestration/definitions.py` | The `Definitions` entry point (`dg.load_defs()` with a walker fallback) |
| `orchestration/components/` | The 11 Component classes |
| `orchestration/defs/<stage>/` | Per-stage YAML `defs.yaml` + Python assets |
| `orchestration/resources.py` | Shared Dagster resources (DuckLake, LanceDB, secrets) |
| `orchestration/sensors/` | 16 standalone sensor files |
| `orchestration/cli.py` | The real dev CLI: `dev`, `list-assets`, `materialise-leabharlann` |

## Run it

```bash
mise run dagster:dev          # http://localhost:3000 — the real entry point
uv run python -m orchestration.cli list-assets
uv run python -m orchestration.cli materialise-leabharlann
```

**Note on `dg`**: earlier docs (and this file, before 2026-08) described
a `dg list components` / `dg scaffold defs` workflow. `dagster-dg-cli`
is not an installed dependency — `dg` is not available as a command in
this environment. The real, working entry points are `orchestration/cli.py`
and `uv run dagster dev -m orchestration.definitions` (what
`mise run dagster:dev` calls). `dg.toml` still declares the workspace
shape Dagster's own tooling reads, even without the `dg` CLI installed.

## Take it independently

`JurisdictionAssetsBase` + `make_jurisdiction_assets()` is the
cleanest piece to lift: point `pipeline_factory` at your own dlt
pipeline and you get an `AssetsDefinition` with the right group name
and partitioning for free. See
[`docs/CHOP_AND_CHANGE_GUIDE.md`](../docs/CHOP_AND_CHANGE_GUIDE.md)
for the fuller per-area breakdown.

## Known gaps

- The `dg` CLI workflow this README used to document isn't installed
  — see "Run it" above.
- Two sensor homes (`defs/sensors/` and `sensors/`) rather than one.
- `defs.yaml` files under `defs/3_model_lifecycle/cocoindex_v1/*/`
  still reference pre-v7 `cianfhoghlaim.cocoindex.<nation>_education_embedding`
  module paths — doubly stale after the 2026-08-19 `cocoindex/` →
  `cocoindex_flows/` rename. Not yet fixed; needs a live Dagster smoke
  test before repointing, since several adjacent modules turned out to
  have deeper bugs once their imports actually resolved this session.
- `orchestration/defs/1_ingestion/` has empty placeholder YAMLs under
  paths that don't correspond to any currently-loaded pipeline
  (nations already absorbed into the v3 generic jurisdiction pattern);
  not audited for deletion as part of this pass.

## Cross-references

- `.agents/skills/dagster/SKILL.md` — Dagster 1.13+ patterns
- `.agents/skills/dlt/SKILL.md` — DLT integration
- `.agents/skills/agent-fleet-orchestration/SKILL.md` — the agent fleet
- `openspec/specs/dagster-5-layer-component-architecture/spec.md`
