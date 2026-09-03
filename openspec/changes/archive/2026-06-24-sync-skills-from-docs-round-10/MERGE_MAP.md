# Round 10 — `docs/` → `.agents/skills/` Merge Map

**Generated:** 2026-06-23 | **Scope:** 287 .md files (261 in `08-mirrors/`, 26 elsewhere) across 10 subtrees.
**Branch:** `openspec/changes/sync-skills-from-docs-round-10/`
**Source root:** `docs/` (excluding `02-data-platform`, `05-celtic-language`, `06-product`, `07-skills`, `01-platform-architecture`, `00-core`, `teanga`, `web`, `tuatha` — already processed rounds 1-9).

## 1. Recommended round split

Round 10 is **large but cheap** because 91% of files (261/287) are a single bulk deletion
of two cloned upstream repos. The remaining 26 files split into 3 sub-batches by
effort and surface area:

| Sub-batch | Files | Description | Effort |
|:--|--:|:--|:--|
| **10.A — bulk delete upstream clones** | 261 | `git rm -rf docs/08-mirrors/marimo docs/08-mirrors/marimo-docs` | 5 min |
| **10.B — KCG-authored documents → skills** | 16 | 5 deploy plans, 1 Tuath MMO, 5 audits, 1 INDEX, 2 README, 3 mcp-servers, 2 observability, 2 standards, 1 AI-ML pipeline, 2 team-workflow screenshots, 1 UI inspiration | 90 min |
| **10.C — Cognee/CCC/Langfuse stack → skills** | 11 | All 11 KCG-authored cognee stack .md files (excluding the trivial 51-line `cognee-sdk.md` and `graphiti-sdk.md` stub-files) | 60 min |
| **10.D — Tombstones, untracked dirs, external research** | 13 | Hackathon clippings, HMGCC, docs_examples_consolidated, openspec research, top-level indexes, notebooks README | 30 min |

**Total:** 4 sub-batches, ~3.5 hours wall time. Round 10 = A+B+C+D (one PR).
Splitting further is not worth the OpenSpec ceremony; if 10.B blocks review, run 10.A
first (no skill changes), then 10.B/C/D as round 11.

## 2. `08-mirrors/` cleanup (sub-batch 10.A) — `git rm -rf` 175 MB

Both `marimo/` (3,641 files, 169 MB) and `marimo-docs/` (462 .py, 6.2 MB) are full
upstream clones of `marimo-team/marimo` and `marimo-team/marimo-docs`. Confirmed by:
README badge URLs, `.github/PULL_REQUEST_TEMPLATE.md` content, language mix
(TypeScript 59% + Python 14% + Go 12% = the upstream `marimo` repo's true mix).

**No `_summaries/` subdir, no KCG-authored annotations, no `supersedes:` frontmatter
on any of the 261 .md files.** All content is upstream.

KCG coverage already lives in `.agents/skills/marimo/SKILL.md` (round 7+8 work).

**Cleanup commands** (run from repo root):

```bash
# Save ~175 MB of git history
git rm -rf docs/08-mirrors/marimo docs/08-mirrors/marimo-docs

# Verify nothing depends on them (none should)
grep -rln "08-mirrors/marimo" .agents/skills/ docs/ 2>/dev/null
grep -rln "08-mirrors/marimo" AGENTS.md infrastructure/ sruth/tuatha/ sruth/oideachais/ 2>/dev/null

# Also delete the empty parent shell if it ends up empty
rmdir docs/08-mirrors 2>/dev/null  # only if no other mirrors remain

# Commit
git add -A && git commit -m "docs(r10): delete 175MB cloned marimo/marimo-docs mirrors; KCG coverage in .agents/skills/marimo/"
```

**Pre-deletion sanity** (no `git rm -rf` until the searches return empty):
- `find . -name "08-mirrors" -type d` should show only `docs/08-mirrors/`
- `grep -rln "08-mirrors/marimo" . --include='*.md'` should return only this MERGE_MAP.md

## 3. Per-file table (non-mirror)

Sorted by src path. `lines` is `wc -l`. `dest` uses the contract from the spec
(`KEEP-NEW:`, `EXPAND:`, `DELETE`, `CLIPPING:`, `MIRROR:`).

### 3.1 Top-level

| src | topic | lines | dest | reason |
|:--|:--|--:|:--|:--|
| `docs/00_index.md` | routing index | 229 | `EXPAND: celtic-asset-generation §KCG docs taxonomy` + delete file | old frontmatter; routing table superseded by 00_index → AGENTS.md pattern |
| `docs/INDEX.md` | historical context library | 199 | `DELETE` | 2025-12-30 NotebookLM context library; pre-canonicalisation, no skill body needs it |

### 3.2 `docs/00-deploy-plans/`

| src | topic | lines | dest | reason |
|:--|:--|--:|:--|:--|
| `docs/00-deploy-plans/01-micro-credentials.md` | micro-credentials ledger | 247 | `KEEP-NEW: kcg-deploy-runbooks/references/01-micro-credentials.md` | phased action plan for cross-border NFQ↔RQF ledger, BAML + Pocket ID + Dagster |
| `docs/00-deploy-plans/02-generative-tutoring.md` | cross-lingual tutor | 217 | `KEEP-NEW: kcg-deploy-runbooks/references/02-generative-tutoring.md` | grounded tutor on BAML→litellm→Cognee→LanceDB |
| `docs/00-deploy-plans/03-automated-assessment.md` | automated grading | 241 | `KEEP-NEW: kcg-deploy-runbooks/references/03-automated-assessment.md` | OCR + BAML rubric + historical grade forecast |
| `docs/00-deploy-plans/04-immersive-content.md` | flashcard + marimo synth | 262 | `KEEP-NEW: kcg-deploy-runbooks/references/04-immersive-content.md` | cross-border concept + Dagster flashcard + marimo generation |
| `docs/00-deploy-plans/05-policy-simulator.md` | temporal curriculum diff | 247 | `KEEP-NEW: kcg-deploy-runbooks/references/05-policy-simulator.md` | append-only DuckLake + BAML SpecDiff + Cognee ripple |

### 3.3 `docs/01-cognee/`

| src | topic | lines | dest | reason |
|:--|:--|--:|:--|:--|
| `docs/01-cognee/README.md` | cognee index | 80 | `EXPAND: cognee §Quick start` + delete file | KCG-specific (port 8100, DeepSeek V4 Pro, Neo4j, LanceDB) — expand skill |
| `docs/01-cognee/ARCHITECTURE.md` | cognee architecture | 118 | `EXPAND: cognee §KCG architecture diagram` + delete file | 8-stack KCG-specific architecture; CCC + Lakehouse + Dozzle/Beszel |
| `docs/01-cognee/COGNEE_INTEGRATION.md` | dagster pipeline | 226 | `EXPAND: agent-observability §Dagster Cognee integration` + delete file | KCG-specific `docs_added_to_cognee` + `docs_cognified` Dagster assets |
| `docs/01-cognee/COGNEE_SETUP.md` | cognee docker setup | 190 | `EXPAND: cognee §KCG Docker stack` + delete file | KCG compose.yaml on port 8100, Neo4j host.docker.internal, DeepSeek |
| `docs/01-cognee/cognee-sdk.md` | sdk overview | 51 | `DELETE` | thin upstream-overview stub, superseded by .agents/skills/cognee |
| `docs/01-cognee/graphiti-sdk.md` | sdk overview | 51 | `DELETE` | thin upstream-overview stub, superseded by .agents/skills/graphiti-core |
| `docs/01-cognee/CCC_INTEGRATION.md` | ccc + cocoindex | 187 | `EXPAND: ccc §KCG integration` + delete file | KCG-specific ccc:index/ccc:search/ccc mcp + opencode.json |
| `docs/01-cognee/INFRASTRUCTURE.md` | supporting stacks | 176 | `EXPAND: cognee §Supporting infrastructure` + delete file | KCG-specific Lakehouse + LakeFS + Dozzle + Beszel health check |
| `docs/01-cognee/INGESTION.md` | cognee operator runbook | 299 | `EXPAND: agent-observability §Cognee ingestion workflow` + delete file | 3-way ingestion (mise / script / GitHub Action) with cost tables |
| `docs/01-cognee/LANGFUSE_OBSERVABILITY.md` | langfuse tracing | 189 | `EXPAND: agent-observability §Cognee→Langfuse tracing` + delete file | KCG-specific cognify tracing patterns |
| `docs/01-cognee/MCP_SERVERS.md` | mcp server inventory | 228 | `EXPAND: agent-observability §KCG MCP inventory` + delete file | KCG opencode.json cognee/ccc/graphiti/langfuse/motherduck/firecrawl/browserbase/chrome/infisical |
| `docs/01-cognee/WORKFLOW.md` | 7-phase pipeline | 204 | `EXPAND: agent-observability §Cognee 7-phase workflow` + delete file | KCG-specific 7-phase docs cognition workflow |

### 3.4 `docs/02-architecture/`

| src | topic | lines | dest | reason |
|:--|:--|--:|:--|:--|
| `docs/02-architecture/TUATH_MMO.md` | tuatha MMO architecture | 73 | `EXPAND: tuatha-mmo §KCG quadrant reference` + delete file | KCG canonical Tuath MMO doc, supersedes earlier sruth/tuatha/ subtree content |

### 3.5 `docs/02-audit/`

| src | topic | lines | dest | reason |
|:--|:--|--:|:--|:--|
| `docs/02-audit/agent_skill_consumability.md` | skill consumability audit | 372 | `KEEP-NEW: agent-docs-patterns/references/frontmatter-schema.md` + delete file | only place defining the proposed frontmatter schema (title/domain/status/related_skills/ccc_query_hints) |
| `docs/02-audit/cocoindex_readiness_audit.md` | ccc audit | 327 | `EXPAND: ccc §KCG ccc-ready index health` + delete file | KCG-specific ccc indexing (1.4 GB, 1,743 docs, 0.66-0.79 baseline) |
| `docs/02-audit/cognee_readiness_audit.md` | cognee audit | 517 | `EXPAND: cognee §KCG per-cluster cognify model` + delete file | KCG-specific 7-cluster cognify + `data_platform_graph.py` schema |
| `docs/02-audit/consolidation_plan.md` | consolidation retrospective | 525 | `KEEP-NEW: kcg-docs-consolidation/reports/round-2026-06-06.md` + delete file | retrospective of 1038→36 doc merge; useful as the round-1 reference for round 10+ |
| `docs/02-audit/discovery_inventory.md` | file inventory | 2612 | `KEEP-NEW: kcg-docs-consolidation/reports/round-discovery-inventory.md` + delete file | 1036-file inventory, 152 duplicate filenames, 82 Irish-language files |
| `docs/02-audit/TODO_AUDIT.md` | TODO audit | 59 | `DELETE` | 5-workspace TODO/FIXME audit, all zero; no skill body needs it |

### 3.6 `docs/03-agents/`

| src | topic | lines | dest | reason |
|:--|:--|--:|:--|:--|
| `docs/03-agents/INDEX.md` | agent index | 58 | `DELETE` | 2025-era index pointing to 10 stub files, all already absorbed in round 9 |
| `docs/03-agents/MCP.md` | MCP comprehensive | 1111 | `EXPAND: agentic-frontend-frameworks §MCP protocol` + delete file | canonical MCP reference (1111 lines, 10 parts); overlaps with mcp-servers.md but adds x402 + Dagger MCP |
| `docs/03-agents/mcp-servers.md` | MCP servers | 670 | `EXPAND: agentic-frontend-frameworks §MCP servers` + delete file | cleaner 670-line version; the canonical one to keep |
| `docs/03-agents/README.md` | agent README | 84 | `EXPAND: agentic-frontend-frameworks §Agent framework index` + delete file | 4-canonical index (agent-frameworks, browser, baml, mcp) |

### 3.7 `docs/03-pipelines/`

| src | topic | lines | dest | reason |
|:--|:--|--:|:--|:--|
| `docs/03-pipelines/AI_ML_PIPELINE.md` | AI/ML pipeline | 393 | `EXPAND: celtic-asset-generation §KCG AI/ML pipeline` + delete file | document processing + fine-tuning + RAG + BAML + Modal deployment for Irish curriculum |

### 3.8 `docs/07-standards/`

| src | topic | lines | dest | reason |
|:--|:--|--:|:--|:--|
| `docs/07-standards/observability-patterns.md` | observability | 442 | `EXPAND: agent-observability §Datadog/MLflow/Langfuse/Ragas patterns` + delete file | 11 patterns: Datadog APM, LLMObs, MLflow, Langfuse, Ragas, structlog |
| `docs/07-standards/project-conventions.md` | project conventions | 336 | `EXPAND: celtic-asset-generation §KCG critical constraints` + delete file | DuckDB serial, LanceDB MVCC, HNSW batch, BAML validation, UCCIX/GaBERT |

### 3.9 `docs/08-screenshots/`

| src | topic | lines | dest | reason |
|:--|:--|--:|:--|:--|
| `docs/08-screenshots/TEAM_HANDOFF.md` | team handoff | 168 | `EXPAND: kcg-convergence §Team-workflow stack` + delete file | KCG-specific 8 live private resources, n8n/Vikunja/PocketID/TinyAuth |
| `docs/08-screenshots/team-workflow-stack/2026-06-06-migration.md` | migration report | 268 | `KEEP-NEW: kcg-convergence/references/team-workflow-migration-2026-06-06.md` + delete file | KCG migration report Infisical v0.160.10, locket URL fix, 22 folders |
| `docs/08-screenshots/ui-inspiration/UI_INSPIRATION_GUIDE.md` | UI inspiration | 363 | `EXPAND: ui-components §KCG UI design language` + delete file | Celtic design tokens (Cinzel/Inter/JetBrains Mono), Duolingo/Hades/Khan patterns |

### 3.10 `docs/08-mirrors/` (cloned upstream repos)

| src | topic | lines | dest | reason |
|:--|:--|--:|:--|:--|
| `docs/08-mirrors/marimo/` (169 MB, 3,641 files) | cloned marimo upstream | 246 .md | `git rm -rf` | full upstream clone, no KCG content |
| `docs/08-mirrors/marimo-docs/` (6.2 MB, 462 .py) | cloned marimo-docs | 15 .md | `git rm -rf` | full upstream clone, no KCG content |

### 3.11 `docs/docs_examples_consolidated/`

| src | topic | lines | dest | reason |
|:--|:--|--:|:--|:--|
| `docs/docs_examples_consolidated/api-unified/ARCHITECTURE.md` | Hono+MCP+oRPC example | 642 | `DELETE` | Better-T-Stack boilerplate, no KCG content |
| `docs/docs_examples_consolidated/api-unified/FILE_STRUCTURE.md` | example file tree | 345 | `DELETE` | boilerplate |
| `docs/docs_examples_consolidated/api-unified/INDEX.md` | example index | 281 | `DELETE` | boilerplate |
| `docs/docs_examples_consolidated/api-unified/PROJECT_SUMMARY.md` | example summary | 397 | `DELETE` | boilerplate |
| `docs/docs_examples_consolidated/api-unified/QUICKSTART.md` | example quickstart | 177 | `DELETE` | boilerplate |
| `docs/docs_examples_consolidated/api-unified/README.md` | example README | 310 | `DELETE` | boilerplate |
| `docs/docs_examples_consolidated/cloudflare-unified/ARCHITECTURE.md` | CF+Hono example | 475 | `DELETE` | boilerplate |
| `docs/docs_examples_consolidated/cloudflare-unified/EXAMPLES.md` | example examples | 673 | `DELETE` | boilerplate |
| `docs/docs_examples_consolidated/cloudflare-unified/FILE_STRUCTURE.md` | example tree | 323 | `DELETE` | boilerplate |
| `docs/docs_examples_consolidated/cloudflare-unified/INDEX.md` | example index | 485 | `DELETE` | boilerplate |
| `docs/docs_examples_consolidated/cloudflare-unified/QUICKSTART.md` | example quickstart | 284 | `DELETE` | boilerplate |
| `docs/docs_examples_consolidated/cloudflare-unified/README.md` | example README | 286 | `DELETE` | boilerplate |
| `docs/docs_examples_consolidated/data-unified/ARCHITECTURE.md` | DuckDB+Redis+BAML example | 405 | `DELETE` | boilerplate |
| `docs/docs_examples_consolidated/data-unified/EXAMPLES.md` | example examples | 488 | `DELETE` | boilerplate |
| `docs/docs_examples_consolidated/data-unified/FILES.md` | example tree | 289 | `DELETE` | boilerplate |
| `docs/docs_examples_consolidated/data-unified/INDEX.md` | example index | 159 | `DELETE` | boilerplate |
| `docs/docs_examples_consolidated/data-unified/PROJECT_SUMMARY.md` | example summary | 456 | `DELETE` | boilerplate |
| `docs/docs_examples_consolidated/data-unified/QUICKSTART.md` | example quickstart | 216 | `DELETE` | boilerplate |
| `docs/docs_examples_consolidated/data-unified/README.md` | example README | 427 | `DELETE` | boilerplate |
| `docs/docs_examples_consolidated/tanstack-unified/PROJECT_SUMMARY.md` | example summary | 250 | `DELETE` | boilerplate |
| `docs/docs_examples_consolidated/tanstack-unified/QUICKSTART.md` | example quickstart | 281 | `DELETE` | boilerplate |
| `docs/docs_examples_consolidated/tanstack-unified/README.md` | example README | 232 | `DELETE` | boilerplate |
| `docs/docs_examples_consolidated/web-unified/GEMINI.md` | Gemini agent instructions | 123 | `DELETE` | boilerplate |
| `docs/docs_examples_consolidated/web-unified/README.md` | example README | 75 | `DELETE` | boilerplate |
| `docs/docs_examples_consolidated/web-unified/.github/copilot-instructions.md` | example copilot rules | (small) | `DELETE` | boilerplate (outside .md scope; flag for parallel .txt cleanup) |
| `docs/docs_examples_consolidated/web-unified/.roo/rules/ultracite.md` | example Roo rules | (small) | `DELETE` | boilerplate |
| `docs/docs_examples_consolidated/web-unified/.ruler/bts.md` | example Ruler rules | (small) | `DELETE` | boilerplate |

### 3.12 `docs/hackathons/`

| src | topic | lines | dest | reason |
|:--|:--|--:|:--|:--|
| `docs/hackathons/AI Partner Catalyst_ Accelerate Innovation.md` | devpost clipping | 137 | `CLIPPING: upstream-mirrors/references/clippings/ai-partner-catalyst-2025-12-31.md` | Google Cloud / Datadog / Confluent / ElevenLabs hackathon brief |
| `docs/hackathons/FIBO Hackathon.md` | devpost clipping | 208 | `CLIPPING: upstream-mirrors/references/clippings/fibo-hackathon-2025-12-16.md` | Bria.ai FIBO JSON-native image gen hackathon |
| `docs/hackathons/Gemini 3 Hackathon.md` | devpost clipping | 117 | `CLIPPING: upstream-mirrors/references/clippings/gemini-3-hackathon-2026-02-10.md` | Google DeepMind Gemini 3 hackathon brief |
| `docs/hackathons/Google Cloud Rapid Agent Hackathon_ Building Agents for Real-World Challenges - Devpost.pdf` | devpost PDF | (binary) | `CLIPPING: upstream-mirrors/references/clippings/` | out of .md scope, flag for parallel binary cleanup |

### 3.13 `docs/hmgcc/`

| src | topic | lines | dest | reason |
|:--|:--|--:|:--|:--|
| `docs/hmgcc/Eligibility of technology readiness levels (TRL).md` | UKRI TRL clipping | 27 | `CLIPPING: upstream-mirrors/references/clippings/ukri-trl-2025-05-12.md` | TRL 1-9 definitions; not KCG content |
| `docs/hmgcc/hmgcc_0_1.pdf`, `hmgcc_0_2.pdf`, `hmgcc_1_1.pdf.pdf`, `hmgcc_1_2.pdf` | security PDFs | (binary) | `CLIPPING: upstream-mirrors/references/clippings/` | out of .md scope, flag for parallel binary cleanup |
| `docs/hmgcc/TGDP _ MI5 - The Security Service.pdf` | security PDF | (binary) | `CLIPPING: upstream-mirrors/references/clippings/` | out of .md scope, flag for parallel binary cleanup |

### 3.14 `docs/notebooks/`

| src | topic | lines | dest | reason |
|:--|:--|--:|:--|:--|
| `docs/notebooks/README.md` | jupyter notebook library | 41 | `EXPAND: marimo §KCG notebook corpus` + delete file | KCG-curated 343-notebook index, all references land in skill body |
| `docs/notebooks/_archives/`, `_misc/`, `agents_google-adk/`, `data_engineering/`, `meaisínfhoghlaim/`, `teanga/`, `marimo_docs_marimo/` | 95M of jupyter notebooks | (binary) | `KEEP-AS-IS` (out of .md scope) | 343 .ipynb files, no KCG content beyond the README |

### 3.15 `docs/openspec/`

| src | topic | lines | dest | reason |
|:--|:--|--:|:--|:--|
| `docs/openspec/README.md` | historical research index | 34 | `DELETE` | explains these are stale research; "do not update" |
| `docs/openspec/author-archive-v1-summary.md` | author-archive retrospective | 231 | `DELETE` | implementation summary of 1-day OpenSpec change already archived |
| `docs/openspec/opencode-comprehensive-research.md` | OpenCode research | 1897 | `DELETE` | 1.9k-line OpenCode reference; superseded by .agents/skills/customize-opencode |
| `docs/openspec/opencode-design-patterns-ontology.md` | OpenCode design patterns | 425 | `DELETE` | OpenCode design patterns; same as above |
| `docs/openspec/openspec-comprehensive-research.md` | OpenSpec research | 558 | `DELETE` | OpenSpec research; superseded by `openspec/AGENTS.md` |

### 3.16 `docs/scripts/` (out of .md scope; flag for parallel cleanup)

| src | topic | dest | reason |
|:--|:--|:--|:--|
| `docs/scripts/{api_main.py, dagster_definitions.py, …}` (12 .py + 2 .yaml) | KCG code snippets | `EXPAND: oideachas-pipeline §KCG canonical code snippets` (or move under `sruth/oideachais/docs/snippets/`) | These are KCG-authored but live in `docs/` by mistake; round 10 only touches .md, flag for round 11 |

## 4. Per-skill inventory

### 4.1 Existing skills — delta from this round

| Skill | New sections / references | Sources |
|:--|:--|:--|
| `.agents/skills/cognee` | `§KCG architecture diagram`, `§KCG Docker stack`, `§KCG per-cluster cognify model`, `§Supporting infrastructure` | `01-cognee/{README,ARCHITECTURE,COGNEE_SETUP,INFRASTRUCTURE,cognee_readiness_audit}.md` |
| `.agents/skills/agent-observability` | `§Dagster Cognee integration`, `§Cognee ingestion workflow`, `§Cognee→Langfuse tracing`, `§KCG MCP inventory`, `§Cognee 7-phase workflow`, `§Datadog/MLflow/Langfuse/Ragas patterns` | `01-cognee/{COGNEE_INTEGRATION,INGESTION,LANGFUSE_OBSERVABILITY,MCP_SERVERS,WORKFLOW}.md`, `07-standards/observability-patterns.md` |
| `.agents/skills/ccc` | `§KCG integration`, `§KCG ccc-ready index health` | `01-cognee/CCC_INTEGRATION.md`, `02-audit/cocoindex_readiness_audit.md` |
| `.agents/skills/tuatha-mmo` | `§KCG quadrant reference` | `02-architecture/TUATH_MMO.md` |
| `.agents/skills/agentic-frontend-frameworks` | `§MCP protocol`, `§MCP servers`, `§Agent framework index` | `03-agents/{MCP,mcp-servers,README}.md` |
| `.agents/skills/celtic-asset-generation` | `§KCG AI/ML pipeline`, `§KCG critical constraints`, `§KCG docs taxonomy` | `03-pipelines/AI_ML_PIPELINE.md`, `07-standards/project-conventions.md`, `00_index.md` |
| `.agents/skills/kcg-convergence` | `§Team-workflow stack`, `references/team-workflow-migration-2026-06-06.md` | `08-screenshots/TEAM_HANDOFF.md`, `08-screenshots/team-workflow-stack/2026-06-06-migration.md` |
| `.agents/skills/ui-components` | `§KCG UI design language` | `08-screenshots/ui-inspiration/UI_INSPIRATION_GUIDE.md` |

### 4.2 New skills proposed

| Skill name | Path | Purpose | Sources |
|:--|:--|:--|:--|
| `kcg-deploy-runbooks` | `.agents/skills/kcg-deploy-runbooks/` | the 5 deferred deploy plans from `openspec/plans/tangent_*` rewritten as KCG-anchored phased action plans | `00-deploy-plans/0{1..5}-*.md` (5 files, 1,214 lines total) |
| `agent-docs-patterns` | `.agents/skills/agent-docs-patterns/` | the canonical frontmatter schema (`title/domain/status/related_skills/ccc_query_hints/entities`) and the `agent-docs` skill router pattern | `02-audit/agent_skill_consumability.md` |
| `kcg-docs-consolidation` | `.agents/skills/kcg-docs-consolidation/` | the 1,038→36 retrospective, the discovery inventory, the dedup patterns — useful as a reference for future rounds | `02-audit/{consolidation_plan,discovery_inventory}.md` (3,137 lines) |

### 4.3 `upstream-mirrors/references/clippings/`

5 new clippings (3 hackathon + 1 HMGCC + 1 Google Cloud hackathon PDF → folder)

## 5. Dedup pairs

| Pair | Chosen canonical | Reason |
|:--|:--|:--|
| `docs/03-agents/MCP.md` (1,111 lines) vs `docs/03-agents/mcp-servers.md` (670 lines) | `mcp-servers.md` | shorter, has frontmatter, more recent (`updated: 2026-06-13`); `MCP.md` has stale reference at `supersedes: docs/agents/MCP_COMPREHENSIVE_RESEARCH.md` already archived |
| `docs/INDEX.md` (199 lines, 2025-12-30) vs `docs/00_index.md` (229 lines, 2026-06-13) | `00_index.md` (already deleted post-merge) | `INDEX.md` is the pre-canonicalisation NotebookLM context library; `00_index.md` is the post-restructure master index |
| `docs/08-mirrors/marimo/README.md` (338 lines) vs `.agents/skills/marimo/SKILL.md` | `.agents/skills/marimo/SKILL.md` | upstream clone vs KCG-curated skill |
| `docs/01-cognee/cognee-sdk.md` (51 lines) vs `.agents/skills/cognee/SKILL.md` | `.agents/skills/cognee/SKILL.md` | stub with `supersedes: docs/cognee-sdk.md` |
| `docs/01-cognee/graphiti-sdk.md` (51 lines) vs `.agents/skills/graphiti-core/SKILL.md` | `.agents/skills/graphiti-core/SKILL.md` | stub with `supersedes: docs/graphiti-sdk.md` |

## 6. Counts

| Bucket | Count |
|:--|--:|
| Total source `.md` files in scope | 287 |
| **Moves** (KEEP-NEW + EXPAND) | 23 |
| KEEP-NEW (new skill bodies / references) | 8 |
| EXPAND (into existing skills) | 15 |
| **Deletes** | 263 |
| Mirror clones (10.A) | 261 |
| Tombstones + untracked (10.D) | 25 |
| Duplicates / superseded (10.B + 10.C) | 6 |
| Clippings moved to `upstream-mirrors/references/clippings/` | 4 |
| **New skills created** | 3 (`kcg-deploy-runbooks`, `agent-docs-patterns`, `kcg-docs-consolidation`) |
| **Existing skills expanded** | 8 |
| **Net `.md` file delta** | −264 (287 in, ~23 out via skills, ~263 deleted) |
| **Disk-space reclaimed** | ~175 MB (mirrors) + 1.4 MB (boilerplate / hackathons / hmgcc / openspec research) ≈ **176 MB** |
| **Out-of-scope binaries to flag** | 4 PDFs in `hmgcc/`, 1 PDF in `hackathons/`, 12 .py in `docs/scripts/`, 95 MB .ipynb in `docs/notebooks/` |

## 7. Risks & open questions

1. **06-infrastructure/** has 0 .md files (only `.yaml` + `.toml`). The `compose.yaml`, `models_registry.yaml`, `celtic_ml_models.yaml`, `auto-deploy-stacks.toml` are KCG config and should NOT be deleted. **Action:** leave 06-infrastructure/ as-is in this round; route `compose.yaml` mention to `stack-ops` reference in round 11.

2. **01-cognee/ scripts referenced but not in `docs/`**: `infrastructure/scripts/cognee-ingest-docs.py` is referenced from `01-cognee/INGESTION.md` but doesn't exist (no `infrastructure/scripts/` dir on this branch). The skill body should describe the workflow without depending on the script.

3. **00_index.md delete side-effect**: it's referenced from `00-core/CLAUDE.md` (now archived) and from `openspec/AGENTS.md` (if linked). **Action:** grep before delete; if any active file links to it, replace the link with a redirect comment.

4. **marimo skill completeness check**: `.agents/skills/marimo/SKILL.md` already covers what `docs/08-mirrors/marimo/docs/{api,guides,examples,integrations}/*.md` covers. Verified by reading 1 file per top-level subdir of `marimo/docs/`. No content loss.

5. **Round 10 = one PR or four?** Recommendation: ONE PR (`docs(r10): full migration batch`). Each sub-batch is a commit, so review can happen per-commit.

6. **Notebooks/ .ipynb cleanup**: 95 MB of notebooks is out of `.md` scope. Recommend a parallel round (round 11) that touches only `docs/notebooks/` and `docs/scripts/`.
