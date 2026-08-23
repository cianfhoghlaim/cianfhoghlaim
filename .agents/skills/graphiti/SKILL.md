---
name: graphiti
description: Temporal knowledge graph memory for agents. Use when building persistent agent memory with bi-temporal model (event time + ingestion time), episodic memory, entity resolution, contradiction detection, or the Graphiti + FalkorDB + LiteLLM triad. Covers `Graphiti(uri="falkor://...")`, `add_episode`, `add_episode_bulk`, `search_`, `summarize_saga` (v0.29.0), `EpisodeType.{text,json,fact_triple,message}`, and the `FalkorDB Lite` embedded mode (`graphiti-core[falkordblite]`, Python 3.12+). Pin `graphiti-core >= 0.28.2` (Cypher-injection CVE #1312 in 0.28.1). v0.29.0 switched episode indexing to 0-based.

## What's new in 2026-08/09

This skill was refreshed as part of the 2026-08-23 omnibus skill refresh
(per the  change). Key
updates:

- **2026-08 tooling**: aligned with the latest versions of upstream
  libraries (per the dev-tooling version-pinning change)
- **2026-08 patterns**: documented new features surfaced via the
  Phase 3 (surfaces round) refactor
- **Cross-references**: linked to adjacent skills (per the AGENTS.md
  dispatch matrix)

See the linked spec changes for full details.

---

# Graphiti - Temporal Knowledge Graph Memory

**Version:** graphiti-core 0.29.2 (PyPI, 2026-06-25) | **Last Updated:** 2026-06-29
**Verified upstream:** `https://github.com/getzep/graphiti/releases` v0.29.2 (`ff7e29c`)
**Docs:** https://help.getzep.com/graphiti (root URL — no double `/graphiti/graphiti/` prefix)
**llms.txt:** https://help.getzep.com/llms.txt (best for agents)

## URLs (verified 2026-06-29)

- Overview: https://help.getzep.com/graphiti/getting-started/overview
- Quick Start: https://help.getzep.com/graphiti/getting-started/quick-start
- Configuration: https://help.getzep.com/graphiti/configuration/llm-configuration  (and .../graph-database-configuration, .../telemetry)
- Working with Data / Episodes: https://help.getzep.com/graphiti/working-with-data/add-episodes
- LangGraph integration: https://help.getzep.com/graphiti/integrations/lang-graph-agent
- LLM-friendly index (best for agents): https://help.getzep.com/llms.txt
- MCP server for IDE clients: https://help.getzep.com/_mcp/server

## Quick start

```python
from graphiti_core import Graphiti
from graphiti_core.nodes import EpisodeType   # canonical since v0.29.x

# Canonical URI: falkor://host:port  (Cloud: falkor://your-instance.falkordb.cloud:6379)
graphiti = Graphiti(uri="falkor://falkordb:6379")
await graphiti.build_indices_and_constraints()  # one-time

# Add an episode (event-time + ingestion-time tracked)
await graphiti.add_episode(
    name="meeting-2026-06-29",
    episode_body="Cian met with the Bunchloch team to plan a new FalkorDB-backed curriculum graph.",
    source=EpisodeType.text,
    source_description="calendar entry",
    reference_time=datetime(2026, 6, 29, 10, 0),
)

# Search (bi-temporal + hybrid)
results = await graphiti.search_("FalkorDB curriculum", num_results=10)
```

## v0.29.x new surface (live, not in Wave 1)

| Symbol | First released | Purpose |
|:--|:--|:--|
| `Graphiti.summarize_saga(saga_id)` | v0.29.0 | First-class multi-episode narrative rollup. Backed by `SagaNode` with bi-temporal watermarks. Returns `SagaNode`. |
| `EpisodeType.fact_triple` | v0.29.0 | Direct fact-triple ingestion (no LLM extraction step). |
| `EpisodicNode.episode_metadata: dict` | v0.29.0 | Customer-defined filtering key. |
| `_extract_and_resolve_nodes(episodes: list[EpisodicNode])` | v0.29.0 | Multi-episode batched node extraction; sets `episode_indices` on each node. |
| `extract_edges(episodes: list[EpisodicNode])` | v0.29.0 | Multi-episode batched edge extraction (concatenates with `[Episode N]` headers). |
| `extract_timestamps` / `extract_timestamps_batch` | v0.29.0 | Decoupled `valid_at` / `invalid_at` post-extraction step. |
| `FalkorDriver(falkor_db=AsyncFalkorDB(...))` | v0.29.2 | Embedded FalkorDB Lite injection. |
| `graphiti-core[falkordblite]` extra | v0.29.2 | `pip install graphiti-core[falkordblite]` for embedded mode (Python 3.12+). |
| `OpenAIGenericClient` default `structured_output_mode="json_schema"` w/ `json_object` fallback | v0.29.2 (#1537) | Pragmatic structured-output for OpenAI-compatible endpoints. |

## Anti-patterns (D-series, new in v0.29.x)

1. **Don't pin to `graphiti-core < 0.28.2`** if you also use the MCP server. The
   `mcp-v1.0.2` advisory is verbatim: "MCP v1.0.1 and prior has a security cypher
   injection vulnerability via `graphiti-core` 0.28.1." Use `mcp >= 1.0.2` + `graphiti-core >= 0.28.2`.
2. **Don't parse `[Episode N]` headers assuming 1-based indexing.** v0.29.0 switched to
   0-based. Update `episode_indices` consumers accordingly.
3. **Don't import ops modules directly** (e.g. `from graphiti_core.driver.falkordb.operations.entity_edge_ops import FalkorEntityEdgeOperations`).
   v0.28.0 redesigned the architecture; ops are injected via `FalkorDriver._entity_edge_ops` property. Direct import will break.
4. **Don't assume `FalkorDB Lite` is unavailable.** v0.29.2 added `graphiti-core[falkordblite]`
   extra (Python 3.12+). For embedded mode pass `FalkorDriver(falkor_db=AsyncFalkorDB(dbfilename=...))`.
5. **Don't hard-code `gpt-4o-mini` as the default.** v0.29.2 #1551 promoted `gpt-5.5` as the
   upstream default with model-tied reasoning effort. Override with `OpenAIClient(config=LLMConfig(model="your-model"))`.
6. **Don't use `EpisodeType.text` for KCG product/catalog updates** — `EpisodeType.json`
   bypasses entity extraction prompts and is ~10× faster.
7. **Don't assume the docs live at `help.getzep.com/graphiti/graphiti/...`.** The KCG
   `.env.example` should set `GRAPHPITI_DOCS_URL=https://help.getzep.com/graphiti` (root,
   no double prefix) for the OpenSpec "live-docs" verification.

## Saga watermarks

```python
# Both last_summarized_at (wall-clock filter) and
# last_summarized_episode_valid_at (temporal public watermark)
add_saga_watermarks: True
```

## Live-docs verification (Agent 81 — 2026-06-29)

Wave 2 verified `graphiti-core 0.29.2` is still the latest on PyPI & GitHub as of 2026-06-29.
No release between Wave 1 (2026-06-28) and Wave 2 (2026-06-29).
Next scheduled re-verify: when 0.29.3 tags appear on github.com/getzep/graphiti/releases
or when 0.30.0 ships. Bookmark https://github.com/getzep/graphiti/releases.atom for
RSS watching.

## CCC anchors (existing + new)

- `graphiti_core/graphiti.py:980` — `add_episode` definition (line verified)
- `graphiti_core/driver/falkordb_driver.py:124` — `FalkorDriver` class
- `graphiti_core/driver/falkordb_driver.py:113` — `default_group_id: str = '_'` (new in v0.29.x)
- `graphiti_core/nodes.py` — `EpisodeType` canonical location
- `graphiti_core/search/search_config_recipes.py` — search recipes (NODE_HYBRID_SEARCH_RRF, etc.)
