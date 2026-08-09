---
name: centralized-registry
description: The single source of truth for models, schemas, pipelines, and stacks. Load when adding/changing/toggling any model, schema, pipeline, or stack. Covers MODEL_REGISTRY (52 entries / 7 families), notebooks/_shared/schema.py (5 introspection helpers), deployment-choice.yaml (the enablement file), notebooks/00_control_panel.py (the 5-tab marimo control panel), and the central registry audit via mise run lint:registry. Per the centralized-model-registry + centralized-schema-registry + deployment-control-panel openspec capabilities (post-2026-08-15).
---

# Centralized Registries — Models, Schemas, Pipelines, Stacks

**Version**: 2026-08-15 | **Last Updated**: 2026-08-15

The Cianfhoghlaim platform now has **one canonical source of truth** for
every model, schema, pipeline, and stack. This replaces the ~70
hardcoded model strings + 96 hand-written Pydantic duplicates + 54
nearly-identical CocoIndex Apps + 619 empty placeholder YAMLs that
the 2026-08-15 audit found.

## 1. The 4 canonical artifacts

| Artifact | Path | Purpose |
|:--|:--|:--|
| **`MODEL_REGISTRY`** | `meaisinfhoghlaim/models/model_registry.py` | 52 entries across 7 families (ocr_vision / text_llm / embedder / rerank / image_gen / voice / translation). |
| **`schema` introspection** | `notebooks/_shared/schema.py` | 5 helpers: `schema_introspect`, `schema_introspect_table`, `schema_introspect_full`, `list_dlt_sources`, `list_cocoindex_apps`, `list_baml_classes`. |
| **`deployment-choice.yaml`** | repo root | The canonical enablement file. Read/written by the marimo notebook + web UI + CLI. |
| **00_control_panel notebook** | `notebooks/00_control_panel.py` | The 5-tab marimo control panel (Models / Pipelines / Datasets / Stacks / Registry). |

## 2. MODEL_REGISTRY — the single source for models

### The 7 families

| Family | Count | Examples |
|:--|--:|:--|
| `ocr_vision` | 20 | `qwen3-vl-8b`, `molmo2-8b`, `gemma-4-26B-A4B`, `dots-ocr`, `unstract-api` |
| `text_llm` | 13 | `minimax-m3`, `qwen3.6-27b-mtp`, `uccix-mistral-24b`, `claude-sonnet-4-20250514` |
| `embedder` | 3 | `BAAI/bge-m3`, `BAAI/bge-large-en-v1.5`, `all-MiniLM-L6-v2` |
| `rerank` | 3 | `jina-reranker-v2-base-multilingual`, `rerank-v3.5`, `gte-rerank-v2` |
| `image_gen` | 5 | `local/image/flux2-dev`, `local/image/z-image-turbo`, `local/image/qwen-image`, `local/image/sdxl`, `local/image/fibo` |
| `voice` | 5 | `whisper-large`, `wav2vec2-irish`, `chatterbox`, `aba-tts`, `ResembleAI/chatterbox` |
| `translation` | 3 | `opus-mt`, `m2m100`, `nllb` |

### The 2-axis key API

```python
from meaisinfhoghlaim.models import (
    MODEL_REGISTRY,            # the registry object
    model_for,                 # resolve a single model key
    filter_models,             # filter by family (returns list[ModelRegistryEntry])
)

# Resolve a single model
default = model_for("text_llm", "default")              # → "minimax-m3"
irish  = model_for("text_llm", "irish", language="ga")  # → "uccix-mistral-24b"
embed  = model_for("embedder", "default")               # → "BAAI/bge-m3"
voice  = model_for("voice", "tts")                      # → "chatterbox"

# Filter by family
embedders = filter_models("embedder")  # → [3 ModelRegistryEntry entries]
for e in embedders:
    print(f"{e.key} ({e.upstream_id}) — {e.role}")

# Direct registry access
entry = MODEL_REGISTRY["minimax-m3"]
print(f"family={entry.family}, role={entry.role}, upstream={entry.upstream_id}")
```

### Adding a new model

To add a new model to the registry, append a `ModelRegistryEntry`
to the relevant family section in
`meaisinfhoghlaim/models/model_registry.py` (one of the 7
`_xxx_entries()` functions):

```python
def _text_llm_entries() -> dict[str, ModelRegistryEntry]:
    entries = {
        # ... existing entries ...
        "my-new-model-v1": ModelRegistryEntry(
            key="my-new-model-v1",
            family="text_llm",
            role="default",  # or any free-form role string
            display_name="My New Model v1",
            unsloth_id=None,  # or "unsloth/my-new-model-GGUF" if local
            mlx_id=None,
            upstream_id="myorg/my-new-model",  # canonical HF ID
            backend="hf",  # or "openai", "google", "anthropic", etc.
            available=True,
            litellm_alias="my-new-model-alias",  # None if not via LiteLLM
            env_var="MY_NEW_MODEL_API_KEY",
            notes="Used by the X agent (per the audit 2026-08-15).",
        ),
    }
    return entries
```

Then run `mise run lint:registry` to verify no drift was introduced.

### Audit drift

```bash
mise run lint:registry            # reports 0 hardcoded model strings
mise run lint:registry --strict   # exits non-zero if drift detected
```

The lint walks `agents/`, `baml_src/`, `notebooks/`, `web/`,
`orchestration/`, `spaces/` and uses AST-aware regex against a tight
family-prefix whitelist. New strings (not in the canonical
`MODEL_REGISTRY` key set) trip the linter.

### List all models

```bash
mise run models:list            # 52 entries grouped by family
mise run models:count           # just the counts (informational)
```

## 3. Schema introspection — discover the lakehouse

5 helpers in `notebooks/_shared/schema.py`:

```python
from notebooks._shared.schema import (
    schema_introspect,               # every BIEP DuckDB table + column metadata
    schema_introspect_table,         # the canonical column metadata for any table
    schema_introspect_full,          # DuckDB + LanceDB + BAML union (control panel Tab 3)
    list_dlt_sources,                # all 920 @dlt.source + 4900 @dlt.resource functions
    list_cocoindex_apps,             # all CocoIndex Apps + their LanceDB mount targets
    list_baml_classes,               # all 838 BAML classes + their parent files
    read_deployment_choice,          # read deployment-choice.yaml (atomic + fcntl.flock)
    write_deployment_choice,         # write deployment-choice.yaml (atomic + fcntl.flock)
    deployment_choice_path,          # canonical path to deployment-choice.yaml
)
```

### Usage

```python
from notebooks._shared.db import connect_md
conn = connect_md()

# 1. Discover the lakehouse schema
rows = schema_introspect_full(conn)  # DuckDB + Lance + BAML
print(f"Found {len(rows)} columns across all tables")

# 2. Check what DLT sources are wired
sources = list_dlt_sources()
print(f"Found {len(sources)} DLT sources/resources")

# 3. Check what CocoIndex Apps are loaded
apps = list_cocoindex_apps()
print(f"Found {len(apps)} CocoIndex Apps")

# 4. Check what BAML classes are extracted
classes = list_baml_classes()
print(f"Found {len(classes)} BAML classes")

# 5. Read/write deployment-choice.yaml
state = read_deployment_choice()
state["enabled_models"]["my-new-model-v1"] = True
write_deployment_choice(state)
```

## 4. Deployment control panel

### Open the 5-tab marimo notebook

```bash
mise run notebook:control-panel
# or: marimo edit notebooks/00_control_panel.py
```

The 5 tabs:
1. **Models** — every MODEL_REGISTRY entry grouped by family. Toggle on/off.
2. **Pipelines** — every DLT source + every CocoIndex App. Toggle on/off.
3. **Datasets** — read-only view of every BIEP DuckDB table + LanceDB mount + BAML class (via `schema_introspect_full`).
4. **Stacks** — every Docker Compose stack. Toggle on/off.
5. **Registry** — full MODEL_REGISTRY view + drift count.

### The deployment-choice.yaml file

The notebook reads/writes `deployment-choice.yaml` at the repo root:

```yaml
version: 1

enabled_models:
  minimax-m3: true
  uccix-mistral-24b: true
  qwen3-vl-8b: true
  # ... 50+ entries ...

enabled_pipelines:
  ireland_jurisdiction_pipeline: true
  european_nations_embedding_factory: true
  # ... 28 entries ...

enabled_stacks:
  litellm: true
  langfuse: true
  # ... 8 high-priority stacks ...

monitoring:
  registry_audit: true
  baml_ts_codegen: true
```

The same file is read/written by the web UI control panel (deferred to
issue #143) and the CLI (deferred to issue #146).

## 5. ADK agent construction (LiteLlm migration)

After the 2026-08-15 drift fix, every ADK agent routes through the
LiteLLM gateway via the canonical `litellm_model("minimax")` helper:

```python
from agents.adk.litellm_agent import make_litellm_agent, litellm_model

# Option A: Use the make_litellm_agent helper
agent = make_litellm_agent(
    name="my_agent",
    description="Routes through the KCG minimax LiteLLM gateway.",
    model_alias="minimax",
    tools=[my_tool],
    instruction="...",
)

# Option B: Use litellm_model with LlmAgent directly
from google.adk.agents import LlmAgent
agent = LlmAgent(
    name="my_agent",
    model=litellm_model("minimax"),
    description="...",
)
```

The 32 hardcoded `LlmAgent(model=config.model_name)` sites that were
bypassing the registry are now all routed through `MODEL_REGISTRY`.

## 6. Dagster JurisdictionAssetsBase

The base class for the 10 per-jurisdiction Dagster asset wrappers.
Lives at `orchestration/defs/2_materials/_base/jurisdiction_assets_base.py`:

```python
from orchestration.defs.2_materials._base.jurisdiction_assets_base import (
    JurisdictionAssetsBase,
    IrelandAssets,                # the reference implementation
    make_jurisdiction_assets,     # dynamic factory for one-line rollouts
    all_jurisdiction_assets,      # list of all 10 AssetsDefinition
)
```

Each per-jurisdiction file becomes a ~30-LOC subclass instead of the
current ~378-LOC. Full rollout saves ~3,300 LOC across 10 files
(issue #146).

## 7. CocoIndex factory pattern

The canonical example: `cocoindex/european_nations/_factory.py`
collapses 40 nation CocoIndex Apps into one factory. See
`cocoindex/AGENTS.md` "The factory pattern" section.

## 7. CocoIndex factory pattern

The canonical example: `cocoindex/european_nations/_factory.py`
collapses 40 nation CocoIndex Apps into one factory. See
`cocoindex/AGENTS.md` "The factory pattern" section.

## Marimo v14 Helper Modules

The canonical shared notebook helpers are:

- `notebooks/_shared/marimo_patterns.py` — reusable v14 dashboard patterns
  and CLI/interactive execution helpers.
- `notebooks/_shared/area_shims/biiep_v3_dashboard.py` — BIEP v3 dashboard
  surface and area-specific shims.
- `notebooks/_shared/ragas_gauge.py` — RAGAS evaluation gauge rendering.

Use `LITELLM_BASE_URL` for LLM routing in notebooks and helper modules; do not
introduce hardcoded gateway URLs. The helpers support the 17 BIEP v3 dashboards,
the 7 grouped dashboards, and the consolidated `notebooks/sync_health.py`
sync-health dashboard.

## 8. The 3 openspec capabilities

| Spec | One-liner |
|:--|:--|
| [`centralized-model-registry`](../../openspec/specs/centralized-model-registry/spec.md) | The 4 canonical artifacts + the 4 Requirements (registry family coverage, no-hardcode-consumption, model_for() API, lint:registry audit). |
| [`centralized-schema-registry`](../../openspec/specs/centralized-schema-registry/spec.md) | BAML is the source of truth + Pydantic + Zod are codegen + 96 Pydantic dupes removed + `schema_introspect_full()`. |
| [`deployment-control-panel`](../../openspec/specs/deployment-control-panel/spec.md) | The marimo notebook + web UI + CLI for picking models/pipelines/datasets/stacks. |

## 9. Reference

- `openspec/changes/archive/2026-08-15-centralized-model-schema-registry-and-deployment-control-panel-v1/`
  (the archived change record)

## Pre-commit hook

A pre-commit hook blocks commits that introduce hardcoded model strings:

```bash
mise run pre-commit-install  # install the hook
mise run pre-commit-run      # run on all files manually
git commit --no-verify       # skip (rare)
```

The hook runs `mise run lint:registry` (which invokes
scripts/registry_audit.py) and fails the commit if any hardcoded
model name/ID is found in `agents/`, `baml_src/`, `notebooks/`,
`web/`, `orchestration/`, `spaces/`, or `meaisinfhoghlaim/` that
isn't routed through `MODEL_REGISTRY`.
- `openspec/specs/centralized-model-registry/spec.md` (4 Requirements)
- `openspec/specs/centralized-schema-registry/spec.md` (4 Requirements)
- `openspec/specs/deployment-control-panel/spec.md` (5 Requirements)
- `meaisinfhoghlaim/models/model_registry.py:MODEL_REGISTRY`
- `notebooks/_shared/schema.py` (5 helpers)
- `notebooks/00_control_panel.py` (the 5-tab notebook)
- `scripts/registry_audit.py` (the drift detector)
- `agents/adk/litellm_agent.py` (the LiteLlm helper)
- `orchestration/defs/2_materials/_base/jurisdiction_assets_base.py`
- `cocoindex/european_nations/_factory.py` (the factory pattern)
- `deployment-choice.yaml` (the canonical enablement file)

## 10. The 6 follow-up issues

| # | Title | Work |
|--:|:--|:--|
| [#141](https://github.com/cianfhoghlaim/cianfhoghlaim/issues/141) | Complete remaining MODEL_REGISTRY migrations (Phase 1.3-1.10 + 1.12-1.19) | 15 remaining model hardcodes |
| [#142](https://github.com/cianfhoghlaim/cianfhoghlaim/issues/142) | Activate BAML TypeScript codegen (baml_client_ts/) | TS codegen via Node @baml/cli |
| [#143](https://github.com/cianfhoghlaim/cianfhoghlaim/issues/143) | Build web UI control panel | 5 TanStack Start routes |
| [#144](https://github.com/cianfhoghlaim/cianfhoghlaim/issues/144) | Pydantic dedup rollout (7 remaining subjects) | ~1320 LOC reduction |
| [#145](https://github.com/cianfhoghlaim/cianfhoghlaim/issues/145) | CocoIndex factory rollout (Irish LC + BI parity) | 14 files → 2 factories |
| [#146](https://github.com/cianfhoghlaim/cianfhoghlaim/issues/146) | Dagster JurisdictionAssetsBase rollout | ~3300 LOC reduction |