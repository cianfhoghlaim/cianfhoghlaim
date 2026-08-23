# `media-intel-acquisition-plan` — Agent Routing

> The 5-class source acquisition plan (refactored 2026-08-23):
> Hickman comics, Wheel of Time prose, ATLA + Korra + Aang
> animation, Hades+WoW+Golden Sun+Pokémon games, and the
> expanded Class E official surface (6 educational body
> sources + 3 government sub-buckets + 5 departments
> sub-buckets = 36 official records). Feeds the
> medium-agnostic `MediaDescriptor` schema (per
> `media-intel-corpus`).

## Routing

Load this AGENTS.md when:

- You add or modify a `source.yaml` in
  `dlt_sources/media/<class>/<work>/`
- You modify the per-class BAML extractor function
- You modify the per-class VLM routing
- You change the licence summary or `legal_notes` for any
  source
- You add a new official source to the Class E
  (educational body + government + departments) sub-buckets
- You activate a Celtic-history stub source (gated downstream)

For platform-wide context, load
[`../../../AGENTS.md`](../../../AGENTS.md).

## Quick start

```bash
# Validate the spec
openspec validate 2026-08-23-tuatha-media-intel-gameplay-capture-research-v1 --strict

# Run a single source (e.g. UK government)
USE_LOCAL_SCRAPES=true uv run python -c "from dlt_sources.media.official.government.uk.scrape import uk_government_source; src = uk_government_source(); rows = list(src); print(f'uk_government: {len(rows)} rows across the 3 resources')"

# Run the educational body sub-bucket
USE_LOCAL_SCRAPES=true uv run python -c "from dlt_sources.media.official.ncca_sec_celt_duchas_wikipedia.scrape import ncca_sec_dfe_sqa_wjec_desc_source; src = ncca_sec_dfe_sqa_wjec_desc_source(); rows = list(src); print(f'ncca_sec_dfe_sqa_wjec_desc: {len(rows)} rows across the 2 resources')"

# Verify the per-class row count
PYTHONPATH="$PWD/notebooks/_shared:$PWD" uv run python -c "
import duckdb
con = duckdb.connect('md:cianfhoghlaim', read_only=True)
print(con.execute('SELECT medium, COUNT(*) FROM cianfhoghlaim.media.media_descriptors GROUP BY 1').fetchall())
"
```

## Key sources

- `openspec/specs/media-intel-acquisition-plan/spec.md` — the
  canonical spec
- `dlt_sources/media/comics/hickman_marvel/{source.yaml,scrape.py}`
  — Class A
- `dlt_sources/media/prose/wheel_of_time/{source.yaml,scrape.py}`
  — Class B
- `dlt_sources/media/animation/atla_korra_aang_film/{source.yaml,scrape.py}`
  — Class C
- `dlt_sources/media/games/hades_wow_golden_sun_pokemon/{source.yaml,capture.py}`
  — Class D
- `dlt_sources/media/official/ncca_sec_celt_duchas_wikipedia/{source.yaml,scrape.py}`
  — Class E (educational body sub-bucket)
- `dlt_sources/media/official/government/{uk,ie,crown_dependencies}/{source.yaml,scrape.py}`
  — Class E (government sub-buckets)
- `dlt_sources/media/official/departments/{uk,ie,sct,wls,ni}/{source.yaml,scrape.py}`
  — Class E (departments sub-buckets)
- `dlt_sources/media/celtic_history_research/{9 topics}/{source.yaml,scrape.py}`
  — the 9 Celtic-history stub sources (gated)
- `baml_src/media/{comic,prose,animation,gameplay,official_document}_descriptor.baml`
  — the 5 per-medium BAML extractor functions
- `agents/meaisinfhoghlaim/media_intel/media_descriptor_agent.py`
  — the 10-tool ADK agent

## Adjacent specs

- [`../media-intel-corpus/spec.md`](../media-intel-corpus/spec.md)
  — the 7-axis `MediaDescriptor` schema (consumed by every
  source)
- [`../celtic-history-research/spec.md`](../celtic-history-research/spec.md)
  — the 9 Celtic-history stub sources (gated for the
  downstream theming change)
- [`../retro-game-design-catalogue/spec.md`](../retro-game-design-catalogue/spec.md)
  — the existing libretro + BAML `ExtractGameplayPattern`
  surface (extended; the 4 NEW stacks land as part of the
  6-file GOLD_STANDARD pattern)
- [`../celtic-asset-generation/spec.md`](../celtic-asset-generation/spec.md)
  — the 4-pipeline Celtic asset generation (extended with
  the `media_descriptors` input flowing from
  `media-intel-corpus`)
- [`../multimodal-code-and-media-intel/spec.md`](../multimodal-code-and-media-intel/spec.md)
  — the 5 CocoIndex v1 Apps + `MediaLocalEmbedding`
  (extended to accept typed descriptors as the primary
  input)
- [`../firecrawl-corpus-and-portals/spec.md`](../firecrawl-corpus-and-portals/spec.md)
  — the 6 Firecrawl invariants (extended with the 3-plan
  ladder + the per-source `firecrawl_plan` declaration)
- [`../infrastructure-stacks/spec.md`](../infrastructure-stacks/spec.md)
  — the 6-file GOLD_STANDARD pattern (extended with the 4
  NEW stacks)

## DO NOT

- **Never** add a Celtic-history topic to the Class E (official)
  surface — they live exclusively in
  `dlt_sources/media/celtic_history_research/`
- **Never** commit a copyrighted comic panel image, animation
  frame still, or game screenshot to the repo (the
  `shippable: false` invariant — the descriptor is
  description-only)
- **Never** hardcode a model string in any extractor — route
  through `MODEL_REGISTRY`
- **Never** declare `shippable_default: true` without
  explicit operator override
- **Never** use a Plan B or Plan C Firecrawl tool when the
  keyless tier is active (Plan A is the v1 default)
- **Never** add a new source without a `source.yaml` manifest
- **Never** skip the `legal_notes` field in any `source.yaml`
  (the legal capture boundary is enforced at materialisation
  time)
- **Never** use "Wikipedia Foundation" as `rights_holder` —
  use the original publisher of the official document
  (e.g., "Ministry of Defence", "Crown copyright", "An
  Garda Síochána")

## Skill pointers

| Skill | When to load |
|:--|:--|
| [`centralized-registry`](../.agents/skills/centralized-registry/SKILL.md) | MODEL_REGISTRY + schema + codegen patterns |
| [`dlt`](../.agents/skills/dlt/SKILL.md) | DLT source patterns + the `source.yaml` manifest |
| [`baml`](../.agents/skills/baml/SKILL.md) | BAML extraction patterns + the 8-stage BAML lifecycle |
| [`cocoindex`](../.agents/skills/cocoindex/SKILL.md) | CocoIndex v1 App patterns + the `mount_table_target` |
| [`lancedb`](../.agents/skills/lancedb/SKILL.md) | LanceDB HNSW patterns + the shared `BAAI/bge-m3` embedder |
| [`firecrawl`](../.agents/skills/firecrawl/SKILL.md) | Firecrawl tool patterns + the 3-plan ladder |
| [`cognee`](../.agents/skills/cognee/SKILL.md) | Cognee cognify patterns for the cross-doc graph |
| [`dignified-python`](../.agents/skills/dignified-python/SKILL.md) | Production Python standards |
| [`motherduck`](../.agents/skills/motherduck/SKILL.md) | The lakehouse / DuckDB / MotherDuck query surface |

<!-- generated: 2026-08-23 by 2026-08-23-tuatha-media-intel-gameplay-capture-research-v1; do not hand-edit -->
