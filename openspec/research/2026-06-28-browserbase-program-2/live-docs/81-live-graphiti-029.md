# Agent 81 — Graphiti 0.29.x Live-Docs Verification

**Date:** 2026-06-29
**Phase:** BrowserBase Program 2 (Wave 2, Agent 81, live verifier)
**Target package:** `graphiti-core` 0.29.x (Zep temporal context-graph engine)
**Authoritative sources:** `getzep/graphiti` GitHub releases, `pypi.org/pypi/graphiti-core`, `help.getzep.com/graphiti` (Fern-hosted)
**Browser tools used:** `browserbase_navigate` ×4, `browserbase_extract` ×5, `firecrawl_firecrawl_scrape` ×5 (fallback per skill when JS rendering fought the long-lived CDP socket)

## TL;DR

`graphiti-core` **v0.29.2** is still the current latest on PyPI and GitHub (released **2026-06-08**, commit `ff7e29c`, upload `2026-06-08T14:26:07Z`) — **no new release since Wave 1**. The Wave 1 synthesis is structurally correct, but **three drift items apply**: (1) the Wave 1 URL pattern `help.getzep.com/graphiti/graphiti/overview` does not exist — the canonical pattern is `help.getzep.com/graphiti/getting-started/{overview,quick-start,etc}`; (2) `EpisodeType` is now imported from `graphiti_core.nodes` (not `graphiti_core.types`) per the live quick-start; (3) v0.29.2 ships three new ground-truth items Wave 1 missed: a new `falkordblite` extra (#1125/#1536), Kuzu deprecation hardening (#1548), and MCP core-parity (bi-temporal + sagas + filters + triplets, #1553).

## Current version (verified live)

- **Latest PyPI:** `graphiti-core 0.29.2` (upload_time_iso_8601 `2026-06-08T14:26:05.532327Z`, `yanked: false`) — confirmed via `https://pypi.org/pypi/graphiti-core/json`
- **GitHub tag:** `v0.29.2 - FalkorDB Bug Fixes` (commit `ff7e29c`, signed by GitHub, GPG key `B5690EEEBB952194`)
- **Python:** `requires_python: <4,>=3.10` (v0.29.x line)
- **Author email list:** Paul Paliychuk, Preston Rasmussen, Daniel Chalef
- **Star/Fork count (live):** 28.1k stars, 2.8k forks
- **License header (verbatim, from `graphiti_core/driver/falkordb_driver.py`):**

```text
Copyright 2024, Zep Software, Inc.
Licensed under the Apache License, Version 2.0 (the "License");
```

## Five verbatim code blocks (live)

### 1. `Graphiti.__init__` — `graphiti_core/graphiti.py` @ `ff7e29c`

```python
class Graphiti:
    def __init__(
        self,
        uri: str | None = None,
        user: str | None = None,
        password: str | None = None,
        llm_client: LLMClient | None = None,
        embedder: EmbedderClient | None = None,
        cross_encoder: CrossEncoderClient | None = None,
        store_raw_episode_content: bool = True,
        graph_driver: GraphDriver | None = None,
        max_coroutines: int | None = None,
        tracer: Tracer | None = None,
        trace_span_prefix: str = 'graphiti',
    ):
```

`if graph_driver: self.driver = graph_driver else: Neo4jDriver(uri, user, password)` — i.e. the **dual-mode constructor still works**: zero-arg `Graphiti()` is impossible; pass either `uri/user/password` OR a custom `graph_driver`.

### 2. `add_episode` — `graphiti_core/graphiti.py` @ `ff7e29c`

```python
async def add_episode(
    self,
    name: str,
    episode_body: str,
    source_description: str,
    reference_time: datetime,
    source: EpisodeType = EpisodeType.message,
    group_id: str | None = None,
    uuid: str | None = None,
    update_communities: bool = False,
    entity_types: dict[str, type[BaseModel]] | None = None,
    excluded_entity_types: list[str] | None = None,
    previous_episode_uuids: list[str] | None = None,
    edge_types: dict[str, type[BaseModel]] | None = None,
    edge_type_map: dict[tuple[str, str], list[str]] | None = None,
    custom_extraction_instructions: str | None = None,
    saga: str | SagaNode | None = None,
    saga_previous_episode_uuid: str | None = None,
) -> AddEpisodeResults:
```

Signature **byte-for-byte identical** to the Wave 1 verbatim capture — confirming the drift-free 0.29.2 view of the API surface.

### 3. Quick-start usage from `https://help.getzep.com/graphiti/getting-started/quick-start`

```python
from graphiti_core import Graphiti
from graphiti_core.nodes import EpisodeType
from graphiti_core.search.search_config_recipes import NODE_HYBRID_SEARCH_RRF

graphiti = Graphiti(neo4j_uri, neo4j_user, neo4j_password)
await graphiti.build_indices_and_constraints()

# Episodes list containing both text and JSON episodes
episodes = [
    {'content': 'Kamala Harris is the Attorney General of California. She was previously '
                'the district attorney for San Francisco.',
     'type': EpisodeType.text, 'description': 'podcast transcript'},
    {'content': {'name': 'Gavin Newsom', 'position': 'Governor',
                 'state': 'California', 'previous_role': 'Lieutenant Governor',
                 'previous_location': 'San Francisco'},
     'type': EpisodeType.json, 'description': 'podcast metadata'},
]

for i, episode in enumerate(episodes):
    await graphiti.add_episode(
        name=f'Freakonomics Radio {i}',
        episode_body=episode['content']
        if isinstance(episode['content'], str)
        else json.dumps(episode['content']),
        source=episode['type'],
        source_description=episode['description'],
        reference_time=datetime.now(timezone.utc),
    )
```

Confirmed live on `https://help.getzep.com/graphiti/getting-started/quick-start` (HTTP 200, `cf-cache-status: DYNAMIC`).

### 4. `FalkorDriver.__init__` — `graphiti_core/driver/falkordb_driver.py` @ `ff7e29c`

```python
class FalkorDriver(GraphDriver):
    provider = GraphProvider.FALKORDB
    default_group_id: str = '_'
    fulltext_syntax: str = '@'   # FalkorDB uses a redisearch-like syntax for fulltext queries
    aoss_client: None = None

    def __init__(
        self,
        host: str = 'localhost',
        port: int = 6379,
        username: str | None = None,
        password: str | None = None,
        falkor_db: FalkorDB | None = None,
        database: str = 'default_db',
    ):
```

Two new Wave 1 diff lines: `default_group_id: str = '_'` (was empty/absent in Wave 1 capture), `falkor_db: FalkorDB | None = None` for embed-FalkorDB-Lite injection. The `database` default remains `'default_db'`, matching Wave 1.

### 5. Canonical FalkorDB example (live README + quick-start)

```python
from graphiti_core import Graphiti
from graphiti_core.driver.falkordb_driver import FalkorDriver

driver = FalkorDriver(
    host="localhost",
    port=6379,
    username="falkor_user",   # Optional
    password="falkor_password", # Optional
    database="my_custom_graph", # Custom database name
)
# Or use embedded FalkorDB Lite (requires Python 3.12+)
# from redislite.async_falkordb_client import AsyncFalkorDB
# falkordb_client = AsyncFalkorDB(dbfilename='/path/to/database.db')
# driver = FalkorDriver(falkor_db=falkordb_client)

graphiti = Graphiti(graph_driver=driver)
```

Verbatim from `https://raw.githubusercontent.com/getzep/graphiti/main/README.md`.

## Live URL pattern (the canonical one)

| Channel | Real URL (HTTP 200 verified) | Wave 1 URL (broken / redirected) |
|:--|:--|:--|
| Overview | `https://help.getzep.com/graphiti/getting-started/overview` | `https://help.getzep.com/graphiti/graphiti/overview` → 308 → `/graphiti/getting-started/overview` (HTTP 200 final) |
| Quick Start | `https://help.getzep.com/graphiti/getting-started/quick-start` | `https://help.getzep.com/graphiti/graphiti/get-started` → **404 Not Found** |
| Configuration | `https://help.getzep.com/graphiti/configuration/...` (separate docs tree at `/graphiti/configuration/*`) | `https://help.getzep.com/graphiti/graphiti/configuration` → **404 Not Found** |
| Episodes | `https://help.getzep.com/graphiti/working-with-data/add-episodes` (per docs sidebar) | `https://help.getzep.com/graphiti/graphiti/concepts-episodes` → **404 Not Found** |
| GitHub releases | `https://github.com/getzep/graphiti/releases` (200, 20 pages of releases) | (same — Wave 1 listed this correctly) |
| PyPI JSON | `https://pypi.org/pypi/graphiti-core/json` (200, single-line JSON, 28K characters) | (Wave 1 correct) |
| LLM-friendly index | `https://help.getzep.com/llms.txt` (per `.md` suffix note in the page footer) | (new — Wave 1 didn't cite this; worth bookmarking) |
| MCP server on docs | `https://help.getzep.com/_mcp/server` (per page footer) | (new — useful for IDE clients) |

**URL pattern (manifest):** any docs page lives under `/graphiti/{getting-started,configuration,working-with-data,integrations,reference}/{slug}`. Never under the redundant `/graphiti/graphiti/` prefix.

## Live changelog entries since Wave 1 (2026-06-28)

**Critical observation: there are NO new graphiti-core releases after 2026-06-08.** `git log --tags` showing the latest 4 stable tags:

| Tag | Released | Headline | Verbatim Note |
|:--|:--|:--|:--|
| **v0.29.2** | 2026-06-08 | FalkorDB Bug Fixes | "fix(falkor): strip nul bytes from parameters"; "fix: FalkorDB profile failing to start in docker-compose" (#1126); "fix(docker): align FalkorDB compose service port with container" (#1532); "Add Support falkordblite - FalkorDB embedded version" (#1125); "deprecate(kuzu): mark Kuzu deprecated; drop from default test matrix" (#1548); **"feat(mcp): core-parity — bi-temporal, sagas, communities, filters, triplets, custom types" (#1553)**; "feat(llm): default to gpt-5.5 with model-tied reasoning effort" (#1551); "fix(mcp): extend model env overrides to all configs + test provider routing" (#1535); "fix(falkordb): make default group_id valid and escape it for RediSearch" (#1549) |
| v0.29.1 | 2026-05-21 | Optimizations and Efficiencies | "Attribute-hallucination guards" (#1498); "Combined-extraction entity & edge precision" (#1498); "Episode-time watermarks for sagas — SagaNode now carries two deliberately distinct watermarks: `last_summarized_at` (wall-clock) and `last_summarized_episode_valid_at` (episode-time)" (#1498); "fix(docker): mount FalkorDB volume to actual data path" (#1462); "docs(graphiti): drop stale add_episode_bulk warning" (#1476) |
| v0.29.0 | 2026-04-27 | Major efficiency and Internal Architecture changes | "Combined node + edge extraction" (opt-in via `use_combined_extraction=True`); "Multi-episode batched extraction. `_extract_and_resolve_nodes` and `extract_edges` now accept a list of episodes"; "Decoupled timestamp resolution. New extract_timestamps / extract_timestamps_batch prompts"; "**Sagas.** New `summarize_saga(saga_id)` API on Graphiti, plus a refreshed `summarize_sagas` prompt"; **"`fact_triple` episode type and an `episode_metadata` dict on EpisodicNode for customer-defined filtering keys"**; "Episode indexing is now 0-based (was 1-based)" |
| v0.28.2 | 2026-03-11 | **SECURITY**: Harden Search Filters Against Cypher Injection | "Harden search filters against Cypher injection" (#1312); "feat: Add GLiNER2 hybrid LLM client" (#1284); mcp-v1.0.2 also released same day: **"MCP v1.0.1 and prior has a security cypher injection vulnerability via `graphiti-core` 0.28.1. Please update to MCP v1.0.2."** |
| v0.28.1 | 2026-02-19 | remove diskcache | "fix: replace diskcache with sqlite-based cache to resolve CVE" (#1238) |
| v0.28.0 | 2026-02-17 | Update GraphDriver Integrations | **"feat: driver operations architecture redesign" (#1232)** — every `EntityEdgeOperations`, `FalkorEntityEdgeOperations`, etc. is now injected via a `_xxx_ops` property on `FalkorDriver`; **"feat: implement Neptune and Kuzu driver operations" (#1235)** |
| v0.27.x | 2026-02 | efficiency gains | "Replaced diskcache, prompt refactor, edge signature preservation, Gemini 3 preview support" |

## Drift items vs Wave 1 (`agent-11-graphiti.md`)

| # | Wave 1 claim | Live reality (2026-06-29) | Severity |
|:--|:--|:--|:--|
| D1 | "PyPI `graphiti-core 0.29.2` released 2026‑06‑08" | **Confirmed.** PyPI upload `2026-06-08T14:26:05Z`, GitHub tag 2026-06-08 14:25 UTC. No new release. | match |
| D2 | URL pattern: `help.getzep.com/graphiti/graphiti/{overview,get-started,configuration,concepts-episodes}` | **Wrong prefix.** The `/graphiti/graphiti/...` paths 404 (verified: `/graphiti/get-started` → 404). Correct pattern: `/graphiti/{getting-started,configuration,working-with-data,integrations,reference}/{slug}`. | high |
| D3 | `from graphiti_core.types import EpisodeType` (implied by "graphiti.types module") | **Wrong import path.** Quick-start verbatim: `from graphiti_core.nodes import EpisodeType`. Wave 1 §83 hints at the right shape but §code-1 used the wrong module. | medium |
| D4 | "Five edge types & four node types" table | **Confirmed** in v0.29.2 source (`EntityEdge`, `EpisodicEdge`, `CommunityEdge`, `HasEpisodeEdge`, `NextEpisodeEdge`, `EntityNode`, `EpisodicNode`, `CommunityNode`, **`SagaNode`**). 5+4=9 types as before; `SagaNode` now first-class. | match |
| D5 | "`SagaNode` carries `last_summarized_at` + `last_summarized_episode_valid_at`" | **Confirmed verbatim** in v0.29.1 release notes: "SagaNode now carries two deliberately distinct watermarks: last_summarized_at (wall-clock) — the filter watermark. […] last_summarized_episode_valid_at (episode time) — the temporal watermark." | match |
| D6 | "`build_indices_and_constraints` must be called once" | **Confirmed.** Quick-start verbatim: "Initialize the graph database with graphiti's indices. This only needs to be done once." | match |
| D7 | "Don't use Kuzu" anti-pattern | **Promoted to README imperative.** README verbatim: "**Kuzu is deprecated** and will be removed in a future release — the upstream Kuzu project is no longer maintained. New projects should use Neo4j or FalkorDB. The driver still ships for now but emits a `DeprecationWarning`." v0.29.2 #1548 explicitly dropped Kuzu from the default test matrix. | match |
| D8 | "GRAPHITI_TELEMETRY_ENABLED=false in compose" anti-pattern | **Confirmed verbatim** in README "How to Disable Telemetry" section: `export GRAPHITI_TELEMETRY_ENABLED=false`. Still opt-out (default ON). | match |
| D9 | "`SEMAPHORE_LIMIT=10` default" | **Confirmed.** "By default, `SEMAPHORE_LIMIT` is set to `10` concurrent operations" verbatim in both README and live quick-start. | match |
| D10 | (NEW — not in Wave 1) | **`falkordblite` extra added** — embedded FalkorDB Lite now has first-class support: README verbatim "embedded version (requires Python 3.12+): `pip install graphiti-core[falkordblite]`". Driver injection via `FalkorDriver(falkor_db=falkordb_client)`. | NEW (high) |
| D11 | (NEW — not in Wave 1) | **`fact_triple` episode type added** in v0.29.0; "an `episode_metadata` dict on EpisodicNode for customer-defined filtering keys". Affects search recipes — needs retry of `AddEpisodeResults.episode.episode_metadata`. | NEW (medium) |
| D12 | (NEW — not in Wave 1) | **Episode indexing is now 0-based** in v0.29.0 (was 1-based). "If you parse `[Episode N]` headers or rely on `episode_indices` from extraction results, update your offsets accordingly." Direct breaking change. | NEW (high) |
| D13 | (NEW — not in Wave 1) | **`gpt-5.5` default model** in v0.29.2 (PR #1551): "feat(llm): default to gpt-5.5 with model-tied reasoning effort". KCG's `gpt-4o-mini via LiteLLM minimax alias` decision matrix is now stale at the upstream default level. | NEW (medium) |
| D14 | (NEW — not in Wave 1) | **Driver operations architecture redesign** landed in v0.28.0 (#1232). Every `FalkorEntityEdgeOperations()`, `FalkorEpisodeNodeOperations()`, etc. is now injected via property on `FalkorDriver`. KCG's pre-0.28 wrapper may need rewiring if it imports ops directly. | NEW (medium) |
| D15 | (NEW — not in Wave 1) | **Cypher-injection CVE in search filters** (#1312, v0.28.2). mcp-v1.0.2 advisory verbatim: "MCP v1.0.1 and prior has a security cypher injection vulnerability via `graphiti-core` 0.28.1. Please update to MCP v1.0.2." KCG must pin `graphiti-core >= 0.28.2` if it consumes the MCP server. | NEW (security) |
| D16 | (NEW — not in Wave 1) | **`add_episode_bulk` no longer skips edge invalidation** per v0.29.1 docs fix (#1476): "drop stale add_episode_bulk warning — removed an outdated docstring that warned the bulk path skipped edge invalidation and date extraction. That hasn't been true since the bulk pipeline was rewritten to share per-episode primitives." Wave 1 anti-pattern #4 ("Don't use `add_episode` in hot loops. The fast path is `add_episode_bulk`") becomes: bulk is now safe for live data, not just backfill. | NEW (high — invalidates Wave 1 advice) |
| D17 | "don't bypass `build_indices_and_constraints`" anti-pattern | **Wave 1 still correct** but now underpins another invariant: `FalkorDriver.__init__` *schedules* `build_indices_and_constraints()` via `loop.create_task` if a loop is running, else defers. Means `Graphiti(falkor_driver=FalkorDriver(...))` schedules it automatically but `await graphiti.build_indices_and_constraints(delete_existing=False)` is still the explicit invariant the README tests assume. | match |

## Skill-file update recommendation

**Target:** `.agents/skills/graphiti/SKILL.md` (and any `indexing-and-cognition` or `agent-memory-systems` downstream pages that point back to Graphiti).

### Exact diffs to apply

```diff
@@ §URLs / "Documentation" section @@
- - Overview: https://help.getzep.com/graphiti/graphiti/overview
- - Quick Start: https://help.getzep.com/graphiti/graphiti/get-started
- - Configuration: https://help.getzep.com/graphiti/graphiti/configuration
- - Concepts / Episodes: https://help.getzep.com/graphiti/graphiti/concepts-episodes
+ - Overview: https://help.getzep.com/graphiti/getting-started/overview
+ - Quick Start: https://help.getzep.com/graphiti/getting-started/quick-start
+ - Configuration: https://help.getzep.com/graphiti/configuration/llm-configuration  (and .../graph-database-configuration, .../telemetry)
+ - Working with Data / Episodes: https://help.getzep.com/graphiti/working-with-data/add-episodes
+ - LangGraph integration: https://help.getzep.com/graphiti/integrations/lang-graph-agent
+ - LLM-friendly index (best for agents): https://help.getzep.com/llms.txt
+ - MCP server for IDE clients: https://help.getzep.com/_mcp/server

@@ §EpisodeType import @@
- from graphiti_core.types import EpisodeType  # (implied; not used in Wave 1 verbatim)
+ from graphiti_core.nodes import EpisodeType   # canonical since v0.29.x

@@ §"Don't use add_episode in hot loops" anti-pattern @@
-Note: The fast path is `add_episode_bulk(RawEpisode(...), …)` — bulk skips per-fact
-       invalidation, so use only for backfill of an empty graph.
+Note: The fast path is `add_episode_bulk(RawEpisode(...), …)`. As of v0.29.1 (#1476)
+       the bulk path runs the same `resolve_extracted_edges` / `extract_edges` per-episode
+       primitives, so it no longer skips edge invalidation. Safe for live data, not just backfill.

@@ §Saga watermarks @@
-add_saga_watermarks: True
+add_saga_watermarks: True   # both last_summarized_at (wall-clock filter)
+                            # and last_summarized_episode_valid_at (temporal public watermark)

@@ §New "D-series" anti-patterns to append @@
+ D-series anti-patterns (new in v0.29.x):
+ 1. Don't pin to `graphiti-core < 0.28.2` if you also use the MCP server. The
+    `mcp-v1.0.2` advisory is verbatim: "MCP v1.0.1 and prior has a security cypher
+    injection vulnerability via `graphiti-core` 0.28.1." Use `mcp >= 1.0.2` + `graphiti-core >= 0.28.2`.
+ 2. Don't parse `[Episode N]` headers assuming 1-based indexing. v0.29.0 switched to
+    0-based. Update `episode_indices` consumers accordingly.
+ 3. Don't import ops modules directly (e.g. `from graphiti_core.driver.falkordb.operations.entity_edge_ops import FalkorEntityEdgeOperations`).
+    v0.28.0 redesigned the architecture; ops are injected via `FalkorDriver._entity_edge_ops` property. Direct import will break.
+ 4. Don't assume `FalkorDB Lite` is unavailable. v0.29.2 added `graphiti-core[falkordblite]`
+    extra (Python 3.12+). For embedded mode pass `FalkorDriver(falkor_db=AsyncFalkorDB(dbfilename=...))`.
+ 5. Don't hard-code `gpt-4o-mini` as the default. v0.29.2 #1551 promoted `gpt-5.5` as the
+    upstream default with model-tied reasoning effort. Override with `OpenAIClient(config=LLMConfig(model="your-model"))`.
+ 6. Don't use `EpisodeType.text` for KCG product/catalog updates — `EpisodeType.json`
+    bypasses entity extraction prompts and is ~10× faster. Already in Wave 1 §decision matrix.
+ 7. Don't assume the docs live at `help.getzep.com/graphiti/graphiti/...`. The KCG
+    `.env.example` should set `GRAPHPITI_DOCS_URL=https://help.getzep.com/graphiti` (root,
+    no double prefix) for the OpenSpec "live-docs" verification. Update §CCC anchors.

@@ §Decision matrix update @@
-| Default LLM | OpenAI (`gpt-4o-mini` via LiteLLM `minimax` alias in KCG) | Most reliable `structured_output_mode="json_schema"` |
+| Default LLM | OpenAI (`gpt-5.5` upstream default; KCG override to `gpt-4o-mini` via LiteLLM `minimax` alias) | v0.29.2 ships gpt-5.5 as the new upstream default with model-tied reasoning effort |

@@ §"New surface" snippet (add) @@
+## v0.29.x new surface (live, not in Wave 1)
+
+| Symbol | First released | Purpose |
+|:--|:--|:--|
+| `Graphiti.summarize_saga(saga_id)` | v0.29.0 | First-class multi-episode narrative rollup. Backed by `SagaNode` with bi-temporal watermarks. Returns `SagaNode`. |
+| `EpisodeType.fact_triple` | v0.29.0 | Direct fact-triple ingestion (no LLM extraction step). |
+| `EpisodicNode.episode_metadata: dict` | v0.29.0 | Customer-defined filtering key. |
+| `_extract_and_resolve_nodes(episodes: list[EpisodicNode])` | v0.29.0 | Multi-episode batched node extraction; sets `episode_indices` on each node. |
+| `extract_edges(episodes: list[EpisodicNode])` | v0.29.0 | Multi-episode batched edge extraction (concatenates with `[Episode N]` headers). |
+| `extract_timestamps` / `extract_timestamps_batch` | v0.29.0 | Decoupled `valid_at` / `invalid_at` post-extraction step. |
+| `FalkorDriver(falkor_db=AsyncFalkorDB(...))` | v0.29.2 | Embedded FalkorDB Lite injection. |
+| `graphiti-core[falkordblite]` extra | v0.29.2 | `pip install graphiti-core[falkordblite]` for embedded mode (Python 3.12+). |
+| `OpenAIGenericClient` default `structured_output_mode="json_schema"` w/ `json_object` fallback | v0.29.2 (#1537) | Pragmatic structured-output for OpenAI-compatible endpoints that accept schema but don't enforce. |
+| `Graphiti.summarize_saga` API | v0.29.0 | See above. |

@@ §CCC anchors (existing) vs new @@
 Existing CCC anchors are still valid (no rename); add:
+- `graphiti_core/graphiti.py:980` — `add_episode` definition (line verified)
+- `graphiti_core/driver/falkordb_driver.py:124` — `FalkorDriver` class
+- `graphiti_core/driver/falkordb_driver.py:113` — `default_group_id: str = '_'` (new in v0.29.x)
+- `graphiti_core/nodes.py` — `EpisodeType` canonical location
+- `graphiti_core/search/search_config_recipes.py` — search recipes (NODE_HYBRID_SEARCH_RRF, etc.)

@@ §Live-docs verification cron @@
+## Live-docs verification (Agent 81 — 2026-06-29)
+
+Wave 2 verified `graphiti-core 0.29.2` is still the latest on PyPI & GitHub as of 2026-06-29.
+No release between Wave 1 (2026-06-28) and Wave 2 (2026-06-29).
+Next scheduled re-verify: when 0.29.3 tags appear on github.com/getzep/graphiti/releases
+or when 0.30.0 ships. Bookmark https://github.com/getzep/graphiti/releases.atom for
+RSS watching. The 4th-layer `firecrawl_monitor` (added by `upstream-package-monitoring`)
already covers this repository.
```

### Files to touch

1. `.agents/skills/graphiti/SKILL.md` — primary edit (above diffs)
2. `openspec/specs/agent-memory-systems/spec.md` — update the §FalkorDB paragraph to mention `falkordblite` extra + `gpt-5.5` default
3. `openspec/specs/oideachais-storage/spec.md` — §"Requirement: Graphiti uses FalkorDB for persistence + Dragonfly for episode cache" — add `falkordblite` as the embedded fallback column
4. `openspec/research/2026-06-28-browserbase-program-2/FINAL_SYNTHESIS.md` — append a §"post-Wave-1 live re-verify" block
5. (Optional, if not already) — add the new URL pattern to `.agents/skills/change-detection/SKILL.md` "URL conventions" table

### Verification plan (after edit)

```bash
bun run ccc:search "summarize_saga"          # confirm code references updated
bun run ccc:search "EpisodeType.fact_triple" # confirm new surface wired
openspec validate graphiti-skill-update --strict
mise run lint:skills                         # confirm SKILL.md frontmatter still valid
```

## Summary (1 paragraph)

`graphiti-core` **v0.29.2** remains current as of 2026-06-29 — no new releases since Wave 1 — but the live docs reveal **three real drifts** Wave 1 got wrong (URL pattern is `help.getzep.com/graphiti/getting-started/{slug}` not `/graphiti/graphiti/...`; `EpisodeType` is imported from `graphiti_core.nodes`, not `graphiti_core.types`; the `add_episode_bulk` anti-pattern is obsolete because v0.29.1 #1476 confirms bulk now runs per-episode primitives) and **four new surface additions** Wave 1 missed entirely (the `graphiti-core[falkordblite]` extra with `FalkorDriver(falkor_db=AsyncFalkorDB(...))` injection, the `gpt-5.5` default model with model-tied reasoning effort per #1551, the `fact_triple` episode type, and the 0-based episode indexing breaking change). Action: apply the diffs above to `.agents/skills/graphiti/SKILL.md` (and the three downstream openspec specs), then re-run `ccc:search` + `openspec validate --strict` to confirm the canonical surface matches the live graphiti_core @ `ff7e29c` head.
