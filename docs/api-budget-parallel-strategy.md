# Parallel API Budget Strategy — MiniMax-M3 × 3 keys × OpenChamber

> **TL;DR.** Three `OPENCODE_GO_API_KEY_<n>` slots in `.env` each get their own
> 5-hour rolling cap. By configuring three opencode providers and three hidden
> subagents, the orchestrator fans work out to all three slots concurrently
> — tripling per-window throughput inside one openchamber session. Then we
> use the leabharlann/, docs/, openspec/ and .agents/skills/ CocoIndex v1
> Apps (already implemented at `oideachais/cocoindex_flows/`) to spend
> the budget on useful indexing rather than ad-hoc LLM chatter.

## 1. What's already in place

| Asset | Path | Status |
|:--|:--|:--|
| `opencode.json` with 4 MiniMax-M3 providers | `opencode.json` | **Rewritten this session** |
| 3 parallel subagents (indexer-a/b/c) | `opencode.json::agent` | **Added this session** |
| Orchestrator primary agent | `opencode.json::agent.orchestrator` | **Added this session** |
| CocoIndex v1 codebase App (replaces `ccc`) | `oideachais/cocoindex_flows/codebase_indexing.py` | Already exists |
| CocoIndex v1 docs+skills App | `oideachais/cocoindex_flows/docs_skills_consolidation.py` | Already exists |
| CocoIndex v1 leabharlann App | `oideachais/cocoindex_flows/leabharlann_embedding.py` | Already exists |
| CocoIndex v1 PDF App | `oideachais/cocoindex_flows/pdf_embedding.py` | Already exists |
| CocoIndex v1 OCR App | `oideachais/cocoindex_flows/ocr_embedding.py` | Already exists |
| CocoIndex v1 research App | `oideachais/cocoindex_flows/research_embedding.py` | Already exists |
| 4 leabharlann dlt sources | `oideachais/dlt_sources/author_archive/{leabharlann_books,zotero,university_of_galway,google_takeout,gemini_deep_research}.py` | Already exists |
| OpenSpec change drafting the consolidation | `openspec/changes/docs-skills-consolidation-pipeline/` | Already drafted |
| OpenSpec change for ChunkHound deprecation | `openspec/specs/chunkhound-code-search/spec.md` | Existing spec (to be modified) |
| BAML extraction client | `baml_src/` + `baml_client/` | Already exists |

The user's mental model of "rebuild from scratch" is partially incorrect —
**most of the indexing pipeline already exists**. The remaining work is:
(1) run it, (2) add the missing pieces (LEABHARLANN→OpenSpec linking,
schema-mask + data-type deduplication, ChunkHound removal).

## 2. The 3-slot fan-out

```
                 ┌─────────────────────────────┐
                 │  openchamber session (you)  │
                 │  default_agent = orchestrator │
                 │  model = minimax-coding-plan/MiniMax-M3 │
                 └──────────────┬──────────────┘
                                │ task()
        ┌───────────────────────┼───────────────────────┐
        ▼                       ▼                       ▼
 ┌──────────────┐       ┌──────────────┐       ┌──────────────┐
 │  indexer-a   │       │  indexer-b   │       │  indexer-c   │
 │ slot 0 key   │       │ slot 1 key   │       │ slot 2 key   │
 │ LEABHARLANN  │       │ DOCS+SKILLS  │       │ OPENSPEC     │
 │ VLM/OCR/PDF  │       │ consolidat. │       │ code self-idx│
 │ leabharlann  │       │ schema/type  │       │ chunkhound   │
 │ _embedding   │       │ standardis.  │       │ deprecation  │
 └──────────────┘       └──────────────┘       └──────────────┘
        │                       │                       │
        ▼                       ▼                       ▼
   CocoIndex v1            CocoIndex v1            CocoIndex v1
   leabharlann_embedding   docs_skills_consolid.   codebase_indexing
   pdf_embedding           (+new schema/type App)  (already exists)
   ocr_embedding
```

Each subagent binds to a different provider:
- `indexer-a` → `minimax-coding-plan-0/MiniMax-M3` (uses `OPENCODE_GO_API_0`)
- `indexer-b` → `minimax-coding-plan-1/MiniMax-M3` (uses `OPENCODE_GO_API_1`)
- `indexer-c` → `minimax-coding-plan-2/MiniMax-M3` (uses `OPENCODE_GO_API_2`)

Because each provider holds a different `apiKey`, each subagent hits a
different 5-hour rolling cap window. The orchestrator can dispatch all
three in parallel and burn 3× the per-window budget.

## 3. Roll-out (do in this order)

### Phase A — 0–30 min: enable v1 indexing (low LLM cost)

```bash
# Initialise and index the codebase (codebase_indexing.py is LLM-free;
# it uses BAAI/bge-m3 sentence-transformers for embeddings, no chat calls)
mise run ccc:v1:index

# Index docs + skills (also LLM-free for embedding; BAML extraction is the
# expensive step but only fires per changed file)
mise run docs:consolidate
```

This populates `codebase_chunks`, `docs_skills_chunks`, and the FalkorDB
`docs_skills_graph`. Runs entirely locally. **No API calls against the
MiniMax-M3 budget.**

### Phase B — 30 min–5 h: index leabharlann/ via dlt (mostly LLM-free)

```bash
# Walk leabharlann/zotero/ + leabharlann/ollscoil_na_gaillimhe/ + leabharlann/mata/
# The 4 leabharlann dlt sources do the heavy lifting with no LLM calls
uv run python -m oideachais.dlt_sources.author_archive.leabharlann_books run
uv run python -m oideachais.dlt_sources.author_archive.zotero run
uv run python -m oideachais.dlt_sources.author_archive.university_of_galway run
uv run python -m oideachais.dlt_sources.author_archive.gemini_deep_research run

# Then run the leabharlann_embedding v1 App (LLM-free for the embedding step;
# BAML extraction for ~1,500 PDFs will cost budget — see Phase C)
mise run leabharlann:embed
```

### Phase C — 5 h–30 h: spend MiniMax-M3 budget on the 4-directory sweep

Open 1 openchamber session. The orchestrator fans out:

```
@orchestrator
  index leabharlann/, docs/, openspec/, .agents/skills/
  → dispatch to indexer-a, indexer-b, indexer-c in parallel
```

Each subagent will:
1. Walk its assigned directory using `localfs.walk_dir` (already wired in the v1 Apps)
2. Call BAML `ExtractDocSkillTag` / `ExtractTriples` / `ProposeConsolidation` per file
3. Write to the relevant LanceDB + FalkorDB targets
4. Emit a structured report for the orchestrator

Each BAML call is a small, well-bounded MiniMax-M3 call — exactly the
shape that fits inside the 5-hour rolling cap.

### Phase D — week 1 (6 days remaining): implement the existing OpenSpec change

The change `openspec/changes/docs-skills-consolidation-pipeline/` is fully
drafted. The implementation tasks are:

1. `baml_src/docs_skills_consolidation.baml` — new extraction schema
2. `oideachais/cocoindex_flows/docs_skills_consolidation.py` — already
   exists, needs the BAML function calls wired in (Phase 2 graph-build)
3. `oideachais/cocoindex_flows/codebase_indexing.py` — already exists, just
   needs `mise run ccc:v1:index` to be run on a schedule
4. `oideachais/dagster_defs/assets/docs_skills_assets.py` — 6 new assets
5. `mise.toml` + `package.json` — task aliases (already partially done)

This is the work the budget should pay for.

### Phase E — week 1 (overlapping): new OpenSpec change

The new change `openspec/changes/four-directory-indexing-and-standards/`
(this session) adds:
- LEABHARLANN → OpenSpec linking (a new v1 App that joins the
  leabharlann_embedding chunks to the openspec GraphConcept nodes)
- OPENSPEC self-indexing (a new v1 App)
- Schema-mask + data-type deduplication (a new capability spec)

## 4. Manual rotation across 5-hour windows

If the gateway groups the 3 keys into the same 5-hour rolling window
(some gateways do), fall back to manual rotation:

```bash
# Terminal 1 (slot 0 dominates for 5h)
export OPENCODE_GO_API_KEY=$OPENCODE_GO_API_0
opencode --model minimax-coding-plan/MiniMax-M3

# Terminal 2 (slot 1 dominates the next 5h)
export OPENCODE_GO_API_KEY=$OPENCODE_GO_API_1
opencode --model minimax-coding-plan/MiniMax-M3

# Terminal 3 (slot 2)
export OPENCODE_GO_API_KEY=$OPENCODE_GO_API_2
opencode --model minimax-coding-plan/MiniMax-M3
```

If the keys really are independent slots, skip this and use the 3-subagent
fan-out exclusively.

## 5. Cap-recovery posture

If a slot's 5-hour cap hits mid-task:
1. The orchestrator gets a 429 from that slot's provider
2. It re-dispatches the in-flight task to a different indexer
3. The retry uses the next available slot's 5-hour window

To enable this, the orchestrator prompt must include a `MAX_RETRIES=3` and
fallback slot ordering. (Add this in a follow-up.)

## 6. Verification checklist before month-end

```bash
# 1. codebase index populated
uv run python -c 'import asyncio; from oideachais.cocoindex_flows.codebase_indexing import search_codebase; rows = asyncio.run(search_codebase("CocoIndex v1 App")); print(len(rows), "hits")'
# Expect: >= 3 hits

# 2. docs+skills graph populated
uv run python -c 'from falkordb import FalkorDB; db = FalkorDB(); g = db.select_graph("docs_skills_graph"); print(g.query("MATCH (n) RETURN count(n)").result_set)'

# 3. leabharlann LanceDB table populated
uv run python -c 'import lancedb; db = lancedb.connect("rest://lance-api.cianfhoghlaim.ie"); print(db.open_table("leabharlann_chunks").count_rows())'

# 4. openspec/ change inventory
uv run python -c 'import os, glob; from pathlib import Path; chgs = sorted(glob.glob("openspec/changes/*/proposal.md")); print(len(chgs), "active changes")'

# 5. OpenSpec validates
openspec validate docs-skills-consolidation-pipeline --strict
openspec validate four-directory-indexing-and-standards --strict
```

## 7. Files added or modified this session

| Path | Change |
|:--|:--|
| `opencode.json` | Rewrote with 4 MiniMax-M3 providers + 3 parallel subagents + orchestrator |
| `docs/agent-orchestration/api-budget-parallel-strategy.md` | This runbook |
| `openspec/changes/four-directory-indexing-and-standards/` | New change (LEABHARLANN linking + OPENSPEC indexing + schema/type standardisation) |

## 8. Restart openchamber

After saving `opencode.json`, **restart openchamber** (quit + relaunch) so
the new providers and agents are loaded. The running session keeps using
the old config until you restart.
