# `meaisinfhoghlaim/models/` — the model registry

> **The single source of truth for every AI/agentic/LLM/VLM/OCR/embedder/reranker/image-gen/voice/translation model choice in the Cianfhoghlaim platform.**
>
> Post-2026-08-15 (`centralized-model-registry` capability) this directory exposes a unified `MODEL_REGISTRY` with 52 entries across 7 families, replacing the historical ~70 hardcoded model strings scattered across `agents/`, `baml_src/`, `notebooks/`, `web/`, `orchestration/`, and `spaces/`.

## What's in here

```
meaisinfhoghlaim/models/
├── __init__.py           # Re-exports: MODEL_REGISTRY, model_for, filter_models, ModelFamily, ModelRegistryEntry
├── registry.py           # The 22-entry VISION_MODELS + CLASSICAL_OCR + TEXT_MODELS (the historical OCR/VLM home)
├── model_registry.py     # The new 52-entry MODEL_REGISTRY (ocr_vision + 6 new families) — post-2026-08-15
├── routing.py            # The (source_group, language) → model router (the agent fleet's primary entry)
├── llama_swap_config.yaml  # llama-swap GGUF server config (the local OCR/VLM inference path)
└── ci/                  # CI helpers (model registry audit + HF liveness check)
```

## Quick start

### Resolve a model

```python
from meaisinfhoghlaim.models import MODEL_REGISTRY, model_for, filter_models

# Single-model resolve (the canonical API)
default = model_for("text_llm", "default")              # → "minimax-m3"
irish  = model_for("text_llm", "irish", language="ga")  # → "uccix-mistral-24b"
embed  = model_for("embedder", "default")               # → "BAAI/bge-m3"

# Filter by family (returns list[ModelRegistryEntry])
embedders = filter_models("embedder")  # → 3 entries
for e in embedders:
    print(f"{e.key} ({e.upstream_id}) — {e.role}")

# Direct registry access
entry = MODEL_REGISTRY["minimax-m3"]
print(f"family={entry.family}, role={entry.role}, upstream={entry.upstream_id}, "
      f"backend={entry.backend}, available={entry.available}")
```

### Use in agent code

```python
from agents.adk.litellm_agent import make_litellm_agent
from agents.adk.config import AgentConfig

# Option A: Lazy default_factory (config.py uses this)
config = AgentConfig()                # all model fields resolve via MODEL_REGISTRY
config.model_name                     # → "minimax-m3"
config.irish_model                     # → "uccix-mistral-24b"
config.embedding_model                 # → "BAAI/bge-m3"

# Option B: Explicit LiteLlm wrapper
agent = make_litellm_agent(
    name="my_agent",
    description="Routes through the KCG minimax LiteLLM gateway.",
    model_alias="minimax",  # the canonical 7-tier fallback
)
```

### Use in notebook code

```python
from notebooks._shared.schema import schema_introspect_full, list_dlt_sources
from notebooks._shared.db import connect_md

# Discover what's in the lakehouse (DuckDB + LanceDB + BAML union)
conn = connect_md()
rows = schema_introspect_full(conn)
print(f"Found {len(rows)} columns across all tables")
```

## Adding a new model

Append a `ModelRegistryEntry` to the relevant family section in
`model_registry.py` (one of the 7 `_xxx_entries()` functions):

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

Then run:

```bash
mise run lint:registry            # verify no drift was introduced
mise run models:list               # see the new entry
```

## The 7 families

| Family | Count | Role keys (examples) | Used by |
|:--|--:|:--|:--|
| `ocr_vision` | 20 | `default`, `diagram`, `tier1_heavy`, `specialist`, `legacy` | `baml_src/clients*.baml`, BAML extraction pipeline |
| `text_llm` | 13 | `default`, `strong`, `fast`, `irish`, `irish_fast`, `kimi`, `glm`, `m2`, `mimo`, `deepseek`, `hackathon_primary`, `hackathon_fallback_1`, `hackathon_fallback_2`, `long_context` | The 12-agent fleet, `spaces/_common/baml_client.py` |
| `embedder` | 3 | `default`, `english_only`, `lightweight` | All CocoIndex Apps (BGE-M3 is canonical) |
| `rerank` | 3 | `default`, `cohere`, `aliyun` | `cocoindex_flows/_shared/reranker.py` |
| `image_gen` | 5 | `flux`, `z_image`, `qwen`, `sdxl`, `fibo` | `agents/image_generation.py` |
| `voice` | 5 | `asr`, `asr_irish`, `tts`, `tts_irish`, `tts_legacy` | `agents/adk/voice_agent.py`, `chatterbox.py` |
| `translation` | 3 | `default`, `multilingual`, `strong_multilingual` | `agents/translation.py`, `agents/adk/config.py` |

**Total**: 52 entries (51 available + 1 deprecated — `uccix-llama2-13b`).

## Audit + drift detection

```bash
mise run lint:registry            # 0 drift expected
mise run lint:registry --strict   # exits non-zero on drift
```

The lint walks `agents/`, `baml_src/`, `notebooks/`, `web/`,
`orchestration/`, `spaces/` and uses AST-aware regex against a tight
family-prefix whitelist. New model strings (not in the canonical
`MODEL_REGISTRY` key set) trip the linter.

## Cross-references

- `.agents/skills/centralized-registry/SKILL.md` — the canonical skill for the centralized registries
- `openspec/specs/centralized-model-registry/spec.md` — the 4 Requirements that govern the registry
- `openspec/changes/archive/2026-08-15-centralized-model-schema-registry-and-deployment-control-panel-v1/` — the change record
- `notebooks/_shared/schema.py` — the schema introspection helpers
- `notebooks/00_control_panel.py` — the 5-tab control panel marimo notebook
- `deployment-choice.yaml` — the canonical enablement file
- `meaisinfhoghlaim/models/registry.py` — the legacy 22-entry `VISION_MODELS` (kept as a subset view)

## Maintenance notes

- **Don't bypass the registry.** The audit found 32+ sites in
  `agents/adk/*` that hardcoded `"gemini-2.0-flash"` via
  `config.model_name`. They are now resolved through the registry via
  lazy `default_factory`. New code should use
  `model_for(family, role)` directly.
- **Don't add new model strings without registering them.** The
  `mise run lint:registry` audit catches new strings; CI runs the
  audit on every commit.
- **Deprecate, don't delete.** When a model is no longer available,
  set `available=False` + update the `notes` field. Don't remove the
  entry — historical deployments may still depend on it.

---

**Last updated**: 2026-08-15 (created — post-`centralized-model-registry` capability).
**Owner**: Build agent.