# `media-intel-corpus` — Agent Routing

> The 5-class source registry + the medium-agnostic
> `MediaDescriptor` schema + the Firecrawl 3-plan ladder +
> the legal capture boundary. The content spine for the
> Celtic-Elemental MMO.

## Routing

Load this AGENTS.md when:

- You add or modify a source in the 5-class source registry
- You write or modify a BAML function in `baml_src/media/`
- You modify the Firecrawl plan ladder or the per-source
  `firecrawl_plan` declaration
- You ingest a new external work (comic, prose, animation,
  game, official document) into the descriptor pipeline

For platform-wide context, load
[`../../../AGENTS.md`](../../../AGENTS.md).

## Quick start

```bash
# Validate the spec
openspec validate 2026-08-23-tuatha-media-intel-and-celtic-elemental-mmo-foundation-v1 --strict

# Run the BAML tests
mise run baml:test

# Run the ccc code search
bun run ccc:search "media descriptor schema"

# Check the per-medium extractor health
python -m media_intel.health_check
```

## Key sources

- `openspec/specs/media-intel-corpus/spec.md` — the canonical spec
- `baml_src/media/media_descriptor.baml` — the medium-agnostic
  schema (BAML-as-SSOT)
- `dlt_sources/media/<class>/<work>/source.yaml` — the
  source-type plugin manifest
- `agents/meaisinfhoghlaim/firecrawl_mcp/client.py` — the
  12-tool Firecrawl wrapper with the
  `KEYLESS_TOOLS` set definition
- `meaisinfhoghlaim/models/registry.py:VISION_MODELS` — the
  24-entry VLM fleet

## Adjacent specs

- [`../celtic-elemental-mmo-canon/spec.md`](../celtic-elemental-mmo-canon/spec.md)
  — the 4+1 world canon that consumes the descriptors
- [`../tuatha-anam-economy/spec.md`](../tuatha-anam-economy/spec.md)
  — the anam economy that consumes the descriptor transferability
  field
- [`../retro-game-design-catalogue/spec.md`](../retro-game-design-catalogue/spec.md)
  — extended with the 4 new work-class sources
- [`../celtic-asset-generation/spec.md`](../celtic-asset-generation/spec.md)
  — extended with the `media_descriptors` input
- [`../multimodal-code-and-media-intel/spec.md`](../multimodal-code-and-media-intel/spec.md)
  — extended to accept typed descriptors
- [`../firecrawl-corpus-and-portals/spec.md`](../firecrawl-corpus-and-portals/spec.md)
  — extended with the 3-plan ladder

## DO NOT

- **Never** commit a copyrighted comic panel image, animation
  frame still, or game screenshot to the repo (the
  `shippable: false` invariant)
- **Never** hardcode a model string in any extractor — route
  through `MODEL_REGISTRY`
- **Never** declare `shippable_default: true` without
  explicit operator override
- **Never** use a Plan B or Plan C Firecrawl tool when the
  keyless tier is active
- **Never** add a new source without a `source.yaml` manifest

## Skill pointers

| Skill | When to load |
|:--|:--|
| [`centralized-registry`](../.agents/skills/centralized-registry/SKILL.md) | MODEL_REGISTRY + schema + codegen patterns |
| [`baml`](../.agents/skills/baml/SKILL.md) | BAML extraction patterns + the 8-stage BAML lifecycle |
| [`dlt`](../.agents/skills/dlt/SKILL.md) | DLT source patterns + the `source.yaml` manifest |
| [`cocoindex`](../.agents/skills/cocoindex/SKILL.md) | CocoIndex v1 App patterns + the `mount_table_target` |
| [`lancedb`](../.agents/skills/lancedb/SKILL.md) | LanceDB HNSW patterns + the shared `BAAI/bge-m3` embedder |
| [`firecrawl`](../.agents/skills/firecrawl/SKILL.md) | Firecrawl tool patterns + the 3-plan ladder |
| [`cognee`](../.agents/skills/cognee/SKILL.md) | Cognee cognify patterns for the cross-doc graph |
| [`unsloth`](../.agents/skills/unsloth/SKILL.md) | Unsloth v5 + the model provider convergence |
| [`agent-fleet-orchestration`](../.agents/skills/agent-fleet-orchestration/SKILL.md) | The 12-agent fleet + the ADK framework |

<!-- generated: 2026-08-23 by 2026-08-23-tuatha-media-intel-and-celtic-elemental-mmo-foundation-v1; do not hand-edit -->
