# Oideachais Cognify Knowledge Graph v1

## Why

The `oideachais-cognify-knowledge-graph` capability spec (9
requirements: R1 5-stage cross-stage KG, R2 site-analysis cognify,
R3 leabharlann cognify, R4 cross-archive edges, R5 graph query
API, R6 daily cron, R7 BAML TypeBuilder dynamic schema, R8 DLT
fan-out, R9 runtime evals + auto-retry) describes the canonical
Cognee knowledge-graph stack for the British-Isles Education
pipeline + leabharlann corpora.

The infrastructure is largely in place per the 5-tangent change
`1d94711c1` (the cognify rules) + the prior
`2026-07-09-agent-fleet-and-observability-facade-v1` change
(production-ised the `storage/memf.py` MemoryBackend Protocol):

- The 7 cognify adapters live at
  `storage/cognify/cognee_integration/`:
  `cross_stage_cognify.py`, `site_analysis_cognify.py`,
  `leabharlann_cognify.py`, `author_archive_cognify.py`,
  `official_media_cognify.py`, `culture_cognify.py`,
  `leabharlann_inbox_cognify.py`.
- The 4 cross-archive rules live at
  `storage/cognify/rules/`:
  `leabharlann_cross_archive.py` (3 leabharlann-internal edges:
  CITES-arxiv, TEACHES-title, CITES-URL),
  `university_cross_archive.py` (UoGArtifact-MATCHES-CourseDescriptor),
  `leabharlann_inbox_cross_archive.py`,
  `author_archive_cross_corpus.py`.
- The cross-archive graph query API route lives at
  `agents/api/_oideachais_api/routes/cross_archive_graph.py`.

But the **5 per-stage cognify adapters** (Aistear, Primary, JC,
SC, University) and the **3 BIEP cross-archive edges**
(BIEP → leabharlann, BIEP → official-media, leabharlann ↔
culture-heritage) are NOT yet explicit. The spec's 9
requirements are functionally covered by the existing
infrastructure, but the 9 explicit deliverables are not
on-disk.

This change ships the 9 deliverables end-to-end:

  5 stage-specific cognify adapters (per stage)
  ─────────────────────────────────────────────
  - `aistear_cognify.py` — Stage 1 (Early Childhood, 0-6)
  - `primary_cognify.py` — Stage 2 (Primary, 5-12)
  - `junior_cycle_cognify.py` — Stage 3 (JC, 12-15)
  - `senior_cycle_cognify.py` — Stage 4 (SC/LC, 15-18)
  - `university_cognify.py` — Stage 5 (University/Tertiary, 18+)

  3 leabharlann-aware cognify orchestrators
  ─────────────────────────────────────────
  - `leabharlann_official_media.py` — wraps the official-media
    adapter + adds 2 leabharlann-aware edge types
    (OfficialMediaSource-ANNOTATES-LeabharlannDoc +
    OfficialMediaSource-REFERENCED_IN-CurriculumStage)
  - `leabharlann_authors_archive.py` — wraps the author-archive
    adapter + dispatches across the 6 corpora (official_media,
    uog_coursework, personal_records, gemini_deep_research,
    zotero, google_takeout) + adds 2 leabharlann-aware edge types
  - `leabharlann_culture_heritage.py` — wraps the culture cognify
    adapter + adds place/person slug normalisation + stage
    correlation + 2 leabharlann-aware edge types

  3 BIEP cross-archive FalkorDB edge rules (single file)
  ────────────────────────────────────────────────────────
  - `cross_archive_biep_edges.py` — 3 edge types:
    - BIEP → leabharlann (`SCLearningOutcome-REFERENCED_IN-LeabharlannDoc`)
    - BIEP → official-media (`LCSubject-ANNOUNCED_BY-OfficialMediaSource`)
    - leabharlann → culture-heritage (`LeabharlannAuthor-COREFERS_WITH-CultureHeritagePerson` +
      `LeabharlannDoc-ABOUT-CultureHeritagePlace`)

  1 marimo notebook for the cognify visualisation
  ──────────────────────────────────────────────
  - `notebooks/10_cognify/01_knowledge_graph.py` — 429 LOC,
    9-panel visualizer of all 9 requirements with 60-node
    synthetic KG fallback

## What changes

| File | Action | LOC delta |
|:--|:--|--:|
| `storage/cognify/cognee_integration/aistear_cognify.py` | NEW (Stage 1) | +~150 |
| `storage/cognify/cognee_integration/primary_cognify.py` | NEW (Stage 2) | +~166 |
| `storage/cognify/cognee_integration/junior_cycle_cognify.py` | NEW (Stage 3) | +~160 |
| `storage/cognify/cognee_integration/senior_cycle_cognify.py` | NEW (Stage 4) | +~162 |
| `storage/cognify/cognee_integration/university_cognify.py` | NEW (Stage 5) | +~176 |
| `storage/cognify/rules/leabharlann_official_media.py` | NEW (leabharlann-1) | +~171 |
| `storage/cognify/rules/leabharlann_authors_archive.py` | NEW (leabharlann-2) | +~163 |
| `storage/cognify/rules/leabharlann_culture_heritage.py` | NEW (leabharlann-3) | +~168 |
| `storage/cognify/rules/cross_archive_biep_edges.py` | NEW (3 BIEP cross-archive edges) | +~496 |
| `notebooks/10_cognify/01_knowledge_graph.py` | NEW (cognify visualisation) | +~429 |
| `notebooks/cli.py` | MODIFIED (add `10_cognify` to GROUPS) | +~7 |
| `openspec/changes/2026-07-14-oideachais-cognify-knowledge-graph-v1/proposal.md` | NEW (this file) | +~110 |
| `openspec/changes/2026-07-14-oideachais-cognify-knowledge-graph-v1/tasks.md` | NEW | +~90 |
| `openspec/changes/2026-07-14-oideachais-cognify-knowledge-graph-v1/specs/oideachais-cognify-knowledge-graph/spec.md` | NEW (1 ADDED requirement) | +~50 |

Total: 10 NEW Python files (~2,100 LOC) + 1 MODIFIED file (cli.py, +7 LOC)
+ 3 NEW openspec change artifacts (~250 LOC).

## Out of scope

- The 7 existing cognify adapters at
  `storage/cognify/cognee_integration/` are NOT
  modified (they are the templates that the new per-stage +
  leabharlann-aware adapters wrap).
- The 4 existing cross-archive rules at
  `storage/cognify/rules/` are NOT modified.
- The 7 `baml/education/lc_extraction/*.baml` files (owned by
  the BIEP v1 change) are NOT modified.
- The `storage/memf.py` MemoryBackend Protocol (production-ised
  in commit `4d2fe8a2`) is NOT modified.
- The 50+ archived openspec changes under
  `openspec/changes/archive/*` are NOT modified.
- The 15 existing notebooks are NOT modified (verified to still
  AST-parse OK).

## Dependencies

```yaml
Blocked by: none
Blocked by (soft):
  - 2026-07-09-v6-drift-remediation-and-repo-boundary-lockdown-v1
    (the spec already exists; this change fills in the
    deliverables)
Affected repos: cianfhoghlaim (single-repo change)
```

No cross-repo sync required. The 88 Docker Compose stacks
under `bonneagar/stacks/*` (cognee + graphiti + lancedb +
falkordb backends) are untouched.

## Cross-archive impact

This change ONLY touches:
- `storage/cognify/cognee_integration/*_cognify.py` (5 NEW files)
- `storage/cognify/rules/leabharlann_*.py` (3 NEW files)
- `storage/cognify/rules/cross_archive_biep_edges.py` (1 NEW file)
- `notebooks/10_cognify/01_knowledge_graph.py` (1 NEW file)
- `notebooks/cli.py` (MODIFIED, +7 LOC)
- `openspec/changes/2026-07-14-oideachais-cognify-knowledge-graph-v1/` (3 NEW files)

No cross-repo sync required.

## Acceptance gates

- `openspec validate 2026-07-14-oideachais-cognify-knowledge-graph-v1 --strict` passes
- 9 requirements of `oideachais-cognify-knowledge-graph` all functional
- 5 cognify stages (aistear + primary + junior_cycle + senior_cycle + university) all exist at `cognify/cognee_integration/`
- 3 leabharlann cognify all exist at `cognify/rules/`
- 3 FalkorDB edges all exist in `cognify/rules/cross_archive_biep_edges.py`
- 1 marimo notebook at `notebooks/10_cognify/01_knowledge_graph.py` exists + AST-parses cleanly
- `uv run cianfhoghlaim-marimo list 10_cognify` discovers 1 entry
- `mise run baml:generate` exits 0 (verified clean-state; parallel-agent dirty state on `baml/processing/_shared/video_kg.baml` blocks the verification but is not caused by this change)
- The 15 existing notebooks still AST-parse OK
- 1 MODIFIED spec delta is well-formed
- Pushed to `origin/pick-4-biep-v1` (NOT `main`)