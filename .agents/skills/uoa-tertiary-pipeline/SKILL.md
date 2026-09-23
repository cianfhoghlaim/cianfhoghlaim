---
name: uoa-tertiary-pipeline
description: Router for the University of Galway (Ollscoil na Gaillimhe) tertiary pipeline — 4-tier College → School → Programme → Module DLT sources + BAML schemas + CocoIndex flows + authenticated regexam.nuigalway.ie + Canvas pipelines + the Students' Union ADK agents. Use when adding a new UoG public surface, extending the per-module pipeline, debugging the M365/Canvas auth flow, or asking "where do I add X for the UoG case study?". Triggers: 'UoG', 'University of Galway', 'Ollscoil na Gaillimhe', 'tertiary pipeline', 'regexam', 'Canvas', 'module handbook', 'reading list', 'past paper', 'students union', 'SU case study'.
---

# UoG Tertiary Pipeline — Router (post the 2026-09-23 consolidation)

The University of Galway / Ollscoil na Gaillimhe (UoG) tertiary
pipeline is a single-repo extension of the BIEP v3 umbrella, scoped
to the UoG case study. It systematises the **4-tier College →
School → Programme → Module** academic hierarchy + the authenticated
regexam.nuigalway.ie + Canvas pipelines + the 5 Students' Union
case-study ADK agents (moved from ciandlithe).

## The 14 DLT sources

Located at `dlt_sources/british_isles/ireland/tertiary/uog/`:

| # | Source | Purpose |
|:--|:--|:--|
| 1 | `academic_calendar.py` | UoG academic calendar events |
| 2 | `governance_minutes.py` | University Council + Academic Council minutes |
| 3 | `press_releases.py` | UoG news + press releases |
| 4 | `programme_catalog.py` | Public programme catalog (UG + PG) |
| 5 | `research_outputs.py` | Research publications + theses |
| 6 | `colleges.py` | The 4 UoG colleges |
| 7 | `schools.py` | The ~10 UoG schools |
| 8 | `programmes.py` | The ~200 UoG programmes |
| 9 | `modules.py` | The ~1,500 UoG modules |
| 10 | `module_handbooks.py` | Per-module PDF handbook + OCR |
| 11 | `reading_lists.py` | Per-module reading list extraction |
| 12 | `past_papers.py` | Per-module past papers (regexam.nuigalway.ie) |
| 13 | `regexam_papers.py` | **Authenticated** regexam scraper (M365 OAuth + AppProxy cookies) |
| 14 | `canvas_materials.py` | **Authenticated** Canvas REST primary + M365 OAuth fallback |

Every DLT resource honours `USE_LOCAL_SCRAPES=true` (default).

## The 8 BAML files

Located at `baml_src/british_isles/ireland/tertiary/`:

- `university_extraction.baml` — the 4-tier College + School +
  Programme + Module schema with 5 extraction functions
  (`ExtractCollege`, `ExtractSchool`, `ExtractProgramme`,
  `ExtractModule`, `ExtractModuleHandbook`) + the `PastPaper` and
  `UoAPortalContent` classes + the `ExtractPastPapers` and
  `ExtractUoAPortalContent` functions
- `academic_calendar.baml` — `AcademicCalendarEvent` (migrated from
  KCG)
- `governance_minute.baml` — `GovernanceMinute` (migrated from KCG)
- `press_release.baml` — `PressRelease` (migrated from KCG)
- `research_output.baml` — `ResearchOutput` (new)
- `module_handbook.baml` — `ModuleHandbook` (new)
- `reading_list.baml` — `ReadingList` (new)
- `past_paper.baml` — `PastPaper` (new)

All 8 BAML files route through the canonical `ExtractEn` LiteLLM
client.

## The 10 CocoIndex flows

Located at `cocoindex_flows/british_isles/ireland/tertiary/uog/`:

- `_shared.py` — the per-module factory
  `create_uog_module_flow(config: ModuleSpec)` + the
  `UoGTertiaryConfig` dataclass
- `programme_flow.py` — programme-level embedding
- `governance_flow.py` — governance minute embedding
- (Plus 8 more Phase 1 stubs for the remaining tiers)

Embedder: **BAAI/bge-m3 (1024-d, multilingual)** per
`cocoindex_flows/_shared/_lifespan.py:108`.

## The 5 Students' Union case-study ADK agents

Located at `agents/meaisinfhoghlaim/educational/students_union/`
(moved from `ciandlithe/agents/adk/students_union/`):

- `clubs_socs_agent.py` — Clubs & Societies Registration review
- `grants_funding_agent.py` — Grants & Funding triage
- `class_rep_aggregator_agent.py` — Class Rep Feedback aggregation
- `complaints_welfare_agent.py` — Complaints & Welfare triage
- `elections_agent.py` — Election & Referendum workflow

Plus 1 root orchestrator `students_union_root_agent` at
`root_agent.py` + 5 pure-Python tools at `tools/`. The root is the
**13th specialist in the 12-agent fleet** (registered in
`agents/agent_registry.py`).

## The authenticated UoA portal pipeline

Located at `agents/uoa_portal/`:

- `portal_agent.py` — the 5-stage SequentialAgent
  (`auth → browse → vision → download → embed`)
- `tools/uoa_browse.py` — the Patchright browser tool
- `tools/uoa_vision.py` — the Gemini 2.5 Pro vision tool
- `tools/stream_to_lakehouse.py` — the MotherDuck + local-disk
  uploader
- `tools/baml_extract_uoa_portal.py` — the BAML extraction wiring
- `tools/cocoindex_upsert.py` — the LanceDB embedder

The per-user credential vault at
`bonneagar/stacks/uo-portal-vault/` provisions per-user M365
AppProxy cookies via the 1-time
`komodo run unlock-uo-portal --user <u> --service {regexam,canvas}`
procedure. Canvas uses PAT (self-service) primary + M365 OAuth
fallback — no IT involvement for either path.

## Routing table — "where do I do X in UoG tertiary?"

| I want to... | Look at... |
|:--|:--|
| Add a new UoG public surface DLT source | `dlt_sources/british_isles/ireland/tertiary/uog/<surface>.py` — mirror the existing patterns |
| Add a new BAML extraction function | `baml_src/british_isles/ireland/tertiary/<domain>.baml` |
| Add a new CocoIndex flow | `cocoindex_flows/british_isles/ireland/tertiary/uog/<flow>.py` — import `shared_lifespan` from `...._shared._lifespan` |
| Add a new per-tier module to `_modules.yaml` | `cocoindex_flows/british_isles/ireland/tertiary/uog/_modules.yaml` |
| Unlock the per-user credential vault | `komodo run unlock-uo-portal --user <u> --service regexam` (or `canvas`) |
| Run the 5-stage ADK pipeline | `python -m agents.uoa_portal.portal_agent` |
| Add a new SU case study agent | `agents/meaisinfhoghlaim/educational/students_union/` — mirror the 5 existing specialists |
| View the SU smoke test | `python agents/meaisinfhoghlaim/educational/students_union/_smoke_test.py` |

## Cross-references

- `openspec/changes/2026-09-23-consolidate-uog-tertiary-pipeline-v1/` —
  the umbrella openspec change
- `openspec/specs/cianfhoghlaim-tertiary-pipeline/spec.md` — the
  umbrella spec (the 9 Requirements: 4-tier schema, per-tier DLT,
  per-tier CocoIndex, SU case studies, authenticated UoG portal,
  retirement of KCG, extraction of SU from ciandlithe, firecrawl
  budget, Dagster orchestration)
- `openspec/specs/british-isles-education-pipeline-v3/spec.md:698` —
  the BIEP v3 stage taxonomy (now `'tertiary'` not `'university'`)
- `agents/agent_registry.py` — the 14-agent fleet (13th =
  students_union_root_agent; 14th = students_union_root_agent after
  the umbrella archives)
- `.agents/skills/bie-p/v3` — the parent BIEP v3 router
- `.agents/skills/baml-schema-sync` — the BAML codegen skill
- `.agents/skills/dlt-sync` — the DLT source registry sync skill
- `.agents/skills/secrets-management` — the Infisical + Locket +
  mise three-way contract

## Sister-repo retirement (per the umbrella change)

The KCG/ollscoil-na-gaillimhe sister-repo at
`github.com/cianfhoghlaim/ollscoil-na-gaillimhe` (local mirror at
`~/dev/kings_college_galway/`) is retired by the umbrella change.
The Students' Union package is removed from ciandlithe by the
parallel removal change. After both archive:
- `git grep kings_college_galway` returns 0
- `git grep ollscoil-na-gaillimhe` returns 0
- `git grep students_union` returns 0 in ciandlithe (only in
  updated README/AGENTS/LICENSE pointers)
- `gh repo delete cianfhoghlaim/ollscoil-na-gaillimhe` returns 204
- `rm -rf ~/dev/kings_college_galway` succeeds
