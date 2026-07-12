---
name: ccc
description: "Semantic code search via CocoIndex Code (ccc CLI). Use when code search, file/directory summary lookup, or concept-guide lookup is needed, when indexing the codebase after changes, or when the user asks about ccc, cocoindex-code, or the codebase index. RETAINED by user direction past the 2026-07-15 retirement; canonical replacement is the v1 App `codebase_indexing` at cocoindex/codebase_indexing.py."
---

> **DEPRECATION NOTICE (2026-07-06):** This skill was scheduled to retire
> 2026-07-15 but is retained by user direction. The replacement (CocoIndex
> v1 App `codebase_indexing`) lives at
> `cocoindex/codebase_indexing.py`. Use the v1 App for new
> work; this skill is retained for the `bun run ccc:init`,
> `bun run ccc:index`, and `bun run ccc:search` developer shortcuts.

# ccc - Semantic Code Search & Indexing

> **Deprecation banner (2026-06-16, retires 2026-07-15):** The v1-native
> replacement is `cocoindex/codebase_indexing.py` (a
> CocoIndex v1 App + Dagster asset group). It uses the same embedding
> model (`BAAI/bge-m3`) and the same LanceDB HNSW index that the rest of
> the data lakehouse uses, and it is registered in the Dagster UI under
> the `codebase` asset group. The `bun run ccc:index` alias now delegates
> to the v1 App, and `bun run ccc:v1:search "<query>"` replaces
> `ccc search "<query>"`. The original `ccc` CLI is kept on disk for the
> 30-day deprecation window only. Reference:
> `openspec/changes/docs-skills-consolidation-pipeline/`.
>
> **Round 8 phase 1 (2026-06-23):** The v1 App gained a **code-graph
> companion** (`codebase_graph` v1 App + `codebase_code_graph` Dagster
> asset). 7 node types (`File`, `Function`, `Class`, `Method`,
> `Module`, `Interface`, `Variable`) + 7 edge types (`CONTAINS`,
> `IMPORTS`, `CALLS`, `EXTENDS`, `IMPLEMENTS`, `USES`, `DEFINES`).
> 29+ language detection via
> `cocoindex/chunking/languages.py` (ported from
> `libraries/codeolas/chunking/languages.py`). Use the v1 Python API
> `search_code_graph(file_path=..., node_type=...)` to query the
> graph table.
>
> **Round 7 phase 2 (2026-06-24):** Four v1 companions for the
> *infrastructure* surface, all in
> `orchestration/defs/infrastructure_assets.py`:
>
> - `api_endpoints` — FastAPI / Hono / TanStack Start / Convex HTTP
>   routes → `api_endpoints` LanceDB. Query helper:
>   `search_api_endpoints(query, framework=None, method=None, limit=20)`.
> - `filesystem_layout` — every directory up to depth 4 with per-dir
>   file-type histogram → `filesystem_layout` LanceDB. Query helper:
>   `search_filesystem(query, min_depth=None, limit=10)`.
> - `storage_backends` — 9 backend kinds (lancedb / duckdb / ducklake /
>   postgres / garage / r2 / d1 / kv / iceberg) → `storage_backends`
>   LanceDB. Query helper:
>   `search_storage(query, kind=None, limit=20)`.
> - `config_files` — 12 config kinds (compose / mise / package /
>   pyproject / turbo / wrangler / env / k8s / pulumi / dg / github /
>   justfile) → `config_files` LanceDB. Query helper:
>   `search_config(query, kind=None, limit=15)`.
>
> **Round 7 phase 3 (2026-06-24):** Two v1 embedding Apps in
> `orchestration/defs/unified_embedding_assets.py`
> (group `embedding`):
>
> - `unified_embeddings` — v1 port of
>   `agents/tuatha/crypteolas/cocoindex_flows/unified_embedding.py:unified_embedding_flow`.
>   Reads any DuckDB connection (default:
>   `crypteolas_catalog.docs.scraped_documents`), chunks with
>   RecursiveSplitter (markdown) or paragraph+char fallback, embeds
>   with BGE-M3, writes to the `unified_embeddings` LanceDB table.
>   Query helper: `unified_search(query, source_types=None, protocol=None)`.
> - `code_embeddings` — v1 port of the v0 `code_embedding_flow`.
>   Walks `UNIFIED_CODE_ROOT` (default:
>   `agents/tuatha/crypteolas/storage/data/code/`) for `*.py`/`*.ts`/`*.tsx`/
>   `*.js`/`*.jsx`/`*.rs`/`*.go`/`*.sol`, chunks with
>   `RecursiveSplitter(detect_code_language)`, embeds with BGE-M3,
>   writes to the `code_embeddings` LanceDB table. Query helper:
>   `code_search(query, language=None, chunk_type=None)`.

`ccc` is the CLI for CocoIndex Code, providing semantic search over the current codebase and index management.

## Ownership

The agent owns the `ccc` lifecycle for the current project — initialization, indexing, and searching. Do not ask the user to perform these steps; handle them automatically.

- **Initialization**: If `ccc search` or `ccc index` fails with an initialization error (e.g., "Not in an initialized project directory"), run `ccc init` from the project root directory, then `ccc index` to build the index, then retry the original command.
- **Index freshness**: Keep the index up to date by running `ccc index` (or `ccc search --refresh`) when the index may be stale — e.g., at the start of a session, or after making significant code changes (new files, refactors, renamed modules). There is no need to re-index between consecutive searches if no code was changed in between.
- **Installation**: If `ccc` itself is not found (command not found), refer to [management.md](references/management.md) for installation instructions and inform the user.

## Searching the Codebase

To perform a semantic search:

```bash
ccc search <query terms>
```

The query should describe the concept, functionality, or behavior to find, not exact code syntax. For example:

```bash
ccc search database connection pooling
ccc search user authentication flow
ccc search error handling retry logic
```

### Filtering Results

- **By language** (`--lang`, repeatable): restrict results to specific languages.

  ```bash
  ccc search --lang python --lang markdown database schema
  ```

- **By path** (`--path`): restrict results to a glob pattern relative to project root. If omitted, defaults to the current working directory (only results under that subdirectory are returned).

  ```bash
  ccc search --path 'src/api/*' request validation
  ```

### Pagination

Results default to the first page. To retrieve additional results:

```bash
ccc search --offset 5 --limit 5 database schema
```

If all returned results look relevant, use `--offset` to fetch the next page — there are likely more useful matches beyond the first page.

### Working with Search Results

Search results include file paths and line ranges. To explore a result in more detail:

- Use the editor's built-in file reading capabilities (e.g., the `Read` tool) to load the matched file and read lines around the returned range for full context.
- When working in a terminal without a file-reading tool, use `sed -n '<start>,<end>p' <file>` to extract a specific line range.

### Following Hints in Search Output

Search results are a mixed ranking of code chunks, per-file/dir summaries, and (when configured) curated concept guides — all scored against the same query. Two kinds of hit come with a follow-up command embedded in the output:

- `[summary]` — a file or directory summary. Read with `ccc describe <path>`.
- `[guide]` — a curated concept guide. Read with `ccc guide <slug>`.

When a hit carries one of these tags, follow the hint: the synthesised text is usually a faster read than chasing through individual files. Conversely, do **not** run `ccc describe .` or `ccc guide` proactively as a triage step — let search rank what's relevant and act on what it returns.

## Describing Files and Directories

Per-file and per-directory summaries (when configured for the project) condense each file's public API, contracts, and role into a short markdown block. They are typically faster to consult than reading the source.

```bash
ccc describe src/auth/session.py        # one file
ccc describe src/auth/                  # directory: summary + children tree
ccc describe .                          # project root overview
```

Use `describe` when you already know the path you want; let `ccc search` find paths for you when you don't.

## Concept Guides

Some projects configure cross-cutting concept guides in `.cocoindex_code/guides.yml` — synthesised markdown documents for architectural topics that span many files (e.g. memoization, plugin-SDK boundary, channel routing). Each guide names canonical files, end-to-end flow, and contracts/invariants.

```bash
ccc guide                               # list available guides + descriptions
ccc guide <slug>                        # print one guide
```

Discovery is search-driven: a relevant guide will surface in `ccc search` results tagged `[guide]` with a `ccc guide <slug>` hint. Run `ccc guide` (no args) only when first orienting in an unfamiliar codebase or when the user explicitly asks for the guide list — not as a routine first step.

### Authoring `guides.yml` Interactively

When the user wants to add or improve concept guides, collaborate on the slug list rather than dumping a finished YAML. Good guide candidates are **named subsystems the codebase obviously has** — cross-cutting lifecycles, registration/dispatch protocols, end-to-end data paths. Single-file or symbol-specific topics do not warrant a guide; per-file summaries already cover those.

Recommended flow:

1. **Survey the codebase.** Use `ccc describe .` and a few likely subdirectory summaries to enumerate the project's subsystems and inter-edge boundaries.
2. **Propose candidates.** Suggest 5–10 slugs with one-line descriptions, framed to name the canonical starting file or directory for each topic. Show them to the user as a list.
3. **Iterate.** Ask which to keep, drop, rename, or merge. Surface non-obvious dependencies (`deps:`) so a higher-level guide can cite a lower-level one rather than restate it. Cycles are rejected at load time.
4. **Write the YAML.** Add the agreed entries to `.cocoindex_code/guides.yml` (creating the file if absent). Confirm `defaults.enabled: true` and that the project's summary feature is enabled — guides require summaries.
5. **Generate.** Run `ccc index` to drive the per-guide agent loop and produce `<slug>.md` files under `.cocoindex_code/guides/`. Re-run after editing descriptions to refresh.

Schema:

```yaml
defaults:
  enabled: true                     # disables all guides when false
  model: openai/gpt-5.4-nano        # falls back to summary.model when omitted
  session_budget: 200
  max_logical_depth: 3
  max_turns_per_session: 18

guides:
  - slug: memoization                          # [a-z0-9][a-z0-9-]*
    description: |
      What this guide covers, framed for the reader.
      Name the canonical starting files (e.g. "start with src/cache.py").
    deps: [other-slug]                         # optional; must not cycle
    max_turns_per_session: 28                  # optional per-entry overrides
```

A multi-line description is fine and often clearer than one terse sentence — the description seeds the guide-generation agent's question, so concrete file/directory anchors pay off.

## Settings

To view or edit embedding model configuration, include/exclude patterns, or language overrides, see [settings.md](references/settings.md).

## Management & Troubleshooting

For installation, initialization, daemon management, troubleshooting, and cleanup commands, see [management.md](references/management.md).

## KCG integration

CCC is the **primary code discovery tool** for every KCG
agent — per the root `AGENTS.md` instruction, "always use
ccc before grep/find". The polyglot monorepo is indexed
continuously into `.cocoindex_code/target_sqlite.db`
(~35 MB) via `bun run ccc:index` (incremental refresh,
<10s on changed files; full rebuild ~2-5 min via
`bun run ccc:init && bun run ccc:index`).

The CCC MCP server is wired in `opencode.json` as
`cocoindex-code` (`ccc mcp`), exposing
`cocoindex-code_search(query, limit, languages, paths)` to
every agent. The tool returns ranked
`[file_path, line_range, score]` tuples — semantic,
embedding-based, not keyword.

**4 canonical CocoIndex flow examples** for the KCG
workloads:

```python
# 1. Text embedding with LanceDB (curriculum corpus)
flow = Flow("text_embedding")
    .source(TextEmbedding.from_markdown("./docs/**/*.md"))
    .transform(LanceDB("curriculum_embeddings"))

# 2. Document knowledge graph (LLM-extracted → Neo4j)
flow = Flow("docs_kg")
    .source(DocumentSource("./docs/**/*.md"))
    .transform(LLMExtraction(model="deepseek-v4-pro",
                             schema=KnowledgeGraphSchema))
    .sink(Neo4jSink("bolt://localhost:7687"))

# 3. Code embedding (tree-sitter chunker → LanceDB)
flow = Flow("code_index")
    .source(CodeSource("./**/*.py", chunker="tree-sitter"))
    .transform(TextEmbedding("code-embeddings"))
    .sink(LanceDBSink("./.cocoindex_code"))

# 4. Multi-format indexing with ColPali (PDF/PNG/JPG → Qdrant)
flow = Flow("visual_docs")
    .source(MultiFormatSource("./docs/**/*.{pdf,png,jpg}"))
    .transform(ColPaliEmbedding())
    .sink(QdrantSink("http://localhost:6333"))
```

**CCC + Cognee complementarity** is the key architectural
insight: CCC searches code (returns implementation files);
Cognee searches docs (returns architecture + patterns). An
agent asking "find how BAML extraction is implemented" gets
code from CCC and architecture from Cognee, then merges.

**Performance**:

| Operation | Scope | Time |
|:--|:--|:--|
| `ccc:index` (incremental) | Changed files only | <10s |
| `ccc:index` (full rebuild) | Entire monorepo | ~2-5 min |
| `ccc:search` | Semantic query | <1s |
| `ccc mcp` server | Continuous | Background |

See `references/kcg-integration/CCC_INTEGRATION.md` for
the full 187-line reference: the current setup, the MCP
config, the index update policy (incremental + full rebuild
+ scheduled via `bun run turbo ccc:index`), the search
API, the per-agent indexing workflow, the 4 flow examples
(text embedding, docs KG, code embedding, ColPali), the
CCC + Cognee dual-search diagram, the index file structure
(`.cocoindex_code/{cocoindex.db, settings.yml, target_sqlite.db}`),
the performance table, and the cross-references.

## KCG ccc-ready index health

The round-1 `cocoindex_readiness_audit` (327 lines, dated
2026-06-06) confirmed the CCC index is **already
ccc-ready for the docs corpus** and the gap is frontmatter,
not indexing. The index is **1.4 GB**, indexes **1,743
`.md` files** (because `**/*.md` is in `include_patterns`),
and was rebuilt on the audit day — no refresh needed.

**7 sample queries** all returned `docs/` files with strong
relevance (0.66-0.79 score range, frequently in the top
position):

| Query | Top hit | Score |
|:--|:--|--:|
| "BAML extraction patterns for Irish education" | `docs/meaisínfhoghlaim/model-ecosystem.md` | 0.774 |
| "Dagster asset partition definition" | `docs/data_engineering/dagster-comprehensive.md` | 0.701 |
| "Convex schema design" | `openspec/.../convex/schema/spec.md` (spec beats docs) | 0.721 |
| "Firecrawl pipeline configuration" | `docs/old/...firecrawl-openapi-research.md` (dup w/ bonneagar, tuatha) | 0.688 |
| "ADK agent routing" | `docs/context/.../google-adk.md` (docs outrank code) | 0.721 |
| "Celtic educational MMO x402 micropayments" | `docs/legacy/tuatha/celtic_mmo.md` (4 dups across dirs) | 0.787 |
| "Gaeltacht language planning areas geoJSON" | `docs/data_engineering/data-sources.md` (4 dups) | 0.741 |

**3 pass / 2 gap findings**: pass on indexing, search
returns docs/, docs outrank code for concepts,
docs-exclusive content is searchable, index freshness;
gap on YAML frontmatter (0 of 7 sampled files) and
duplicate content (4+ copies of same content across
`docs/`, `docs/old/`, `docs/bonneagar/`, `docs/legacy/tuatha/`,
`docs/legacy/tuatha/agents/tuatha/`).

**The "ccc-clean" frontmatter convention** (the round-1
recommendation that became the `agent-docs-patterns`
skill's 12-field schema): `title` (anchor at position 0),
`description` (dense one-sentence summary), `domain`
(controlled vocabulary), `entities` (class/function
names that match code identifiers), `ccc_query_hints` (the
exact natural-language queries users would type — the
highest-ROI field), `status` (active/draft/archived),
`related_skills`, `related_code` (file paths create
embedding adjacency with actual code chunks), `related_docs`.

**The 9-point summary table** scored: docs/ indexed (Pass),
semantic search returns docs/ (Pass), docs outrank code
for concepts (Pass), docs-only content searchable (Pass),
index freshness (Pass), YAML frontmatter (Gap — 0/7),
duplicate content (Gap — 4+ copies), index size
(Healthy — 1.4 GB), docs/ isolation filterable (Pass).

**5 audit recommendations**: (1) no index refresh needed,
(2) add frontmatter starting with `ccc_query_hints` for
highest ROI, (3) deduplicate before consolidating (remove
`docs/old/` + nested `docs/legacy/tuatha/agents/tuatha/` first), (4) create
a `guides.yml` for cross-cutting concept guides
("BAML extraction end-to-end", "Tuath MMO x402 payment
flow"), (5) standardize on `--path docs/` for agent
queries that need documentation context, (6) run
`ccc index` after each major consolidation batch.

See `references/health/cocoindex_readiness_audit.md` for
the full 327-line audit: the executive summary, the
indexing + search internals, the 7-query test results
(each with top-5 hits + scores + assessment), the index
health check, the frontmatter audit (0/7 sampled files),
the 6-point "ccc-clean" convention, the 9-point summary
table, the 6 recommendations, and the appendix of test
commands.

---

## Appendix A: Alternative engines

The KCG-canonical code search is `ccc` (this skill). Two
alternative engines are tracked:

### ChunkHound (now removed from `.agents/skills/`)

ChunkHound (2024-2025) is an open-source local-first code
search engine. It used to ship as a separate skill
(`.agents/skills/chunkhound/SKILL.md`) but was consolidated
into this skill. Key ChunkHound capabilities the KCG team
liked (and which `ccc` v1 does NOT replicate):

- **Two-layer architecture**: base RAG layer (cAST chunking +
  semantic + regex search) + orchestration layer (multi-hop
  exploration).
- **Multi-hop exploration**: BFS traversal discovering
  architectural relationships across the codebase, with a
  5-second convergence detection to prevent infinite loops.
- **Adaptive token budgets**: 30k-150k token budgets based on
  repository size, so small projects don't get buried in noise
  and large monorepos still get sufficient context.
- **29+ language support** (incl. PDF via PyMuPDF).
- **Dual-store**: DuckDB primary + LanceDB experimental.
- **Performance**: 4.3 point gain in Recall@5 on RepoEval,
  2.67 point gain in Pass@1 on SWE-bench, ~5ms query latency
  with HNSW, 10-100x faster indexing via native git bindings.

**When to consider ChunkHound over ccc**:

- The codebase is a fresh project (no Dagster + CocoIndex v1
  pipeline yet) and you need a code search engine *now*.
- You need the multi-hop exploration pattern (ccc v1 has
  flat semantic search; ChunkHound has iterative BFS).
- You need a self-contained, no-cloud-dependencies
  installation. ChunkHound runs locally; ccc needs the
  Dagster + CocoIndex v1 + LanceDB + (optionally) Lance
  Cloud infrastructure.

**How to install ChunkHound if needed** (KCG teams don't
ship it as a skill anymore):

```bash
uv tool install chunkhound
cd /path/to/project
chunkhound index
chunkhound search "def.*authenticate"
```

The ChunkHound `.chunkhound.json` configuration pattern
(local-first, no cloud) is the right default for any
air-gapped or compliance-constrained project.

### Other engines (not in KCG)

- **Sourcegraph** — enterprise code intelligence, paid.
- **livegrep** — regex-only, no embeddings.
- **Zoekt** — gitlab's regex engine.
- **Code Search (Google internal)** — not available externally.

The KCG stack uses `ccc` (canonical) or `ChunkHound`
(per-project self-hosted) for all production code search.

## See also

- **[`../INDEXING_AND_COGNITION.md`](../INDEXING_AND_COGNITION.md)** — Consolidated setup + MCP reference for both `ccc` and `cognee`. Includes current state (index size, chunk count, container status), first-time setup, daily-use commands, MCP tool inventory for both, dual-search workflow, and troubleshooting matrix. Read this when an agent or team member asks "how do I set up ccc?", "how do I start cognee?", or "what MCP tools are available?".
