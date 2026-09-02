# Change: Sister-Repo Lift v1 — Lifting v6 era learnings to the 6 sister repos as actual code

> **Status:** AUTHORED (NOT YET ACTIVATED).
>
> **Phase 12 of 12** in the
> [`openspec/plans/2026-09-01-cianfhoghlaim-nua-v6-era-v1.md`](../../plans/2026-09-01-cianfhoghlaim-nua-v6-era-v1.md)
> 10-phase integration of `gemini_hackathon/` learnings back into
> `cianfhoghlaim/`. Phase 12 is the inverse-direction leg: lift the
> cianfhoghlaim-side v6 era learnings OUT to the 6 sister repos.
>
> **Scope discipline:** the lift patches are the *planning docs*.
> The actual code transfer happens in the sister-repo PRs
> (deferred to the sister repo maintainers per the operator's
> earlier directive that each sister has valuable content to lift
> FROM cianfhoghlaim — not wholesale copy of the substrate).

## Why

Phase 8 (the `2026-09-01-sister-side-mirrors-v1/`
sister-side mirrors + the 6 sister-side umbrella-mirror changes)
shipped **awareness** of the cianfhoghlaim v6 era learnings into
the 6 sister repos. None of those changes shipped *code*. The 6
sister repos therefore still operate without the canonical
cianfhoghlaim substrate that the v6 era validated:

- `bonneagar` (IaC substrate) — still has the 6 GCP mirror stack
  READMEs at `bonneagar/stacks/gcp-*/README.md`, but the BAML +
  Convex + A2UI + certificate-pipeline surface is not lifted.
- `tuatha` (British Isles Formative Assessment MMO) — still has
  the legacy Babylon.js 3D + SpacetimeDB theming per the 2026-08-25
  consolidation; the Pipecat + TTS + LC planner + 4-step
  per-subject pattern is not lifted.
- `ciancheiltis` (Celtic-language corpus) — has the 6 Celtic
  languages covered, but the canonical 8-entry `CelticLanguage`
  enum + 7-vernacular BAML extractors + morphology + grammar +
  Duchas source BAML are not lifted.
- `ciandlithe` (OSINT legal-data platform) — has the Courts.ie
  + BAILII awareness, but the 5 core legal BAML schemas (courts +
  judgements + shared_legal_enums + PIAB + court_rules) are not
  lifted.
- `cianchosaint` (OSINT defence platform) — has the same legal
  BAML dependency (3 of the 5 files overlap with ciandlithe), and
  is missing the `eiraic_treasures` canonical + the `_docling_grid_segmenter`
  row × column detector.
- `gemini_hackathon` (GCP-first hackathon repo) — has the OSS-first
  substrate *consumed*, but the substrate itself (study_plan +
  NCCE learning_graph + equivalencies + certificate pipeline +
  CocoIndex v1 learning_graphs_app) is not lifted as the canonical
  reference implementation.

This change authors the **lift patches** — per-sister-repo
planning documents that name the source files in cianfhoghlaim,
the destination files in the sister repo, the transformation
rules (rename / restructure / drop), and the per-PR checklist.

## What is shipped

### §1 — Six lift-patch planning docs (6 files)

The lift patches live in a new directory
`openspec/sister-lifts/` (NOT in `openspec/changes/` — the sister
repo PRs are separate codebases and each gets its own openspec
change in its own repo). The 6 patches:

- **§1.1** `openspec/sister-lifts/bonneagar-iac-gcp-mirror-lift-v1.md`
- **§1.2** `openspec/sister-lifts/tuatha-adk-pipecat-lift-v1.md`
- **§1.3** `openspec/sister-lifts/ciancheiltis-celtic-baml-lift-v1.md`
- **§1.4** `openspec/sister-lifts/ciandlithe-legal-baml-lift-v1.md`
- **§1.5** `openspec/sister-lifts/cianchosaint-defence-baml-lift-v1.md`
- **§1.6** `openspec/sister-lifts/gemini-hackathon-oss-substrate-lift-v1.md`

Each lift patch is a markdown file with:

1. A clear 1-line summary of what's being lifted
2. The list of source files (paths in cianfhoghlaim)
3. The list of destination files (paths in the sister repo)
4. The transformation rules (rename / restructure / drop)
5. A per-PR step-by-step checklist (≥ 3 items per PR, ≥ 3 PRs per
   sister)

### §2 — The customisation matrix

The per-sister customisation matrix (the heart of this change) is
the inverse of the Phase 8 sister-side umbrella-mirror
"per-sister customisation summary" table. Where Phase 8 said
"what ships FROM cianfhoghlaim INTO the sister", Phase 12 (this
change) lays out the per-file customisation plan.

#### §2.1 — bonneagar (IaC substrate)

| # | Source (cianfhoghlaim) | Destination (sister repo) | Transformation |
|--:|---|---|---|
| B.1 | `baml_src/british_isles/_shared/study_plan.baml` | `~/dev/bonneagar/baml_src/_study_plan.baml` | **Rewrite the package + class names** to drop the `british_isles._shared` namespace (bonneagar is the IaC substrate, not the BIEP substrate). Strip the per-jurisdiction SubjectSpec references; keep the canonical `StudyPlan + ExtractStudyPlan + GenerateStudyPlanAssets` shape. |
| B.2 | `bonneagar/stacks/gcp-{bigquery-mirror,cloud-run,gcs-bucket,gemini-vertex,gemma-unsloth,secret-manager}/README.md` | already in bonneagar — **no lift needed**; this is the home repo. | The README content is canonical here; the sister repos `ciandlithe` + `cianchosaint` + `gemini_hackathon` reference these stacks via Pangolin resources. |
| B.3 | `web/packages/db/convex/schema.ts` | `~/dev/bonneagar/web/packages/db/convex/schema.ts` | **Drop the 16 LC tables** (per-subject + per-jurisdiction); the IaC substrate doesn't need Convex tables for BIEP. Keep `users + workspaces + stacks + pipelines + runs + audit_log` (the 6 IaC tables). |
| B.4 | `meaisinfhoghlaim/certificate/` (7-stage pipeline) | `~/dev/bonneagar/meaisinfhoghlaim/certificate/` | **Keep the 7-stage shape** but rewrite `Stage3_ArtifactBuilder` to emit Terraform plan JSON (not PDF); `Stage4_RubricValidator` is dropped (no rubric for IaC artifacts). |
| B.5 | `web/packages/a2ui/` (11-component catalog) | **Drop entirely** — bonneagar doesn't need A2UI; IaC ops happen via Pangolin UI. | This is an explicit "what stays behind" entry. The IaC substrate uses Pangolin resource pages, not A2UI chat surfaces. |

#### §2.2 — tuatha (British Isles Formative Assessment MMO)

| # | Source (cianfhoghlaim) | Destination (sister repo) | Transformation |
|--:|---|---|---|
| T.1 | `agents/adk/voice_agent.py` | `~/dev/tuatha/agents/adk/voice_agent.py` | **Drop the Lingala + French (CA) voice_profile additions** (those came from the BIEP-JC subject extension; tuatha is LC + JC only). Keep the wired Pipecat + ChatterboxTTS dispatch + the 5 voice_profile overrides. |
| T.2 | `agents/api/_oideachais_api/services/pipecat_client.py` | `~/dev/tuatha/agents/api/_oideachais_api/services/pipecat_client.py` | **Lift as-is** — the Pipecat client is identical for both repos (Hono + ws bridge). |
| T.3 | `agents/api/_oideachais_api/services/tts_router.py` | `~/dev/tuatha/agents/api/_oideachais_api/services/tts_router.py` | **Rewrite the voice_id mapping** to use tuatha's 5 voice profiles (LC + JC); drop the BIEP voice_id overrides. |
| T.4 | `agents/adk/subjects/lc/planner.py` | `~/dev/tuatha/agents/adk/subjects/lc/planner.py` | **Lift as-is** — the planner is the canonical study-plan surface per Phase 1. |
| T.5 | `agents/adk/subjects/lc/chemistry.py` | `~/dev/tuatha/agents/adk/subjects/lc/chemistry.py` | **Lift as-is** — the 4-step per-subject pattern is identical across repos. tuatha adds the same pattern to its 14 subjects (per `2026-08-26-extend-educational-mmo-to-14-subjects-v1/`). |

#### §2.3 — ciancheiltis (Celtic-language corpus)

| # | Source (cianfhoghlaim) | Destination (sister repo) | Transformation |
|--:|---|---|---|
| C.1 | `baml_src/celtic/sources.baml` | `~/dev/ciancheiltis/baml_src/celtic/sources.baml` | **Lift as-is** — the 8-entry `CelticLanguage` enum (ga + cy + gd + br + kw + gv + sga + non_celtic_indo_european) is the canonical taxonomy. |
| C.2 | `baml_src/british_isles/_cross/vernacular_languages.baml` | `~/dev/ciancheiltis/baml_src/_cross/vernacular_languages.baml` | **Lift as-is** — the 7-vernacular BAML extractors (CY + GD + BR + KW + GV + FR_JE + FR_GG + SCO) are the canonical cross-vernacular extraction surface. |
| C.3 | `baml_src/celtic/morphology.baml` | `~/dev/ciancheiltis/baml_src/celtic/morphology.baml` | **Lift as-is** — morphology schemas are corpus-specific to ciancheiltis (cianfhoghlaim doesn't have a morphology BAML consumer). |
| C.4 | `baml_src/celtic/grammar_patterns.baml` | `~/dev/ciancheiltis/baml_src/celtic/grammar_patterns.baml` | **Lift as-is** — grammar pattern extraction is corpus-specific. |
| C.5 | `baml_src/celtic/gaois/duchas.baml` | `~/dev/ciancheiltis/baml_src/celtic/gaois/duchas.baml` | **Lift as-is** — the Duchas (Irish folklore + place-name) source BAML is corpus-specific to ciancheiltis (gaois.ie is the canonical source). |

#### §2.4 — ciandlithe (OSINT legal-data platform)

| # | Source (cianfhoghlaim) | Destination (sister repo) | Transformation |
|--:|---|---|---|
| L.1 | `baml_src/british_isles/ireland/education/law/courts.baml` | `~/dev/ciandlithe/baml_src/education/law/courts.baml` | **Drop the `_ireland_education_law_` prefix**; rename to `CourtsBAML` for the ciandlithe package namespace. Strip the LC marking-mode refs (CI1/CI2/CI3/H1/H2/H3 etc.); ciandlithe uses Court-level (SCCD/HC/SC/SupCt) only. |
| L.2 | `baml_src/british_isles/ireland/education/law/judgements.baml` | `~/dev/ciandlithe/baml_src/education/law/judgements.baml` | **Lift as-is** for the schema shape; **rename** the function names from `ExtractJudgement` to `ExtractOSINTJudgement` (to disambiguate from cianfhoghlaim's LC exam judgement surface). |
| L.3 | `baml_src/british_isles/ireland/education/law/shared_legal_enums.baml` | `~/dev/ciandlithe/baml_src/education/law/shared_legal_enums.baml` | **Lift as-is** — the shared enums (CourtLevel, JudgeLevel, CaseStatus, etc.) are the canonical cross-platform taxonomy. |
| L.4 | `baml_src/british_isles/ireland/education/law/piab.baml` | `~/dev/ciandlithe/baml_src/education/law/piab.baml` | **Lift as-is** — Personal Injuries Assessment Board is CI-specific and ciandlithe consumes it directly. |
| L.5 | `baml_src/british_isles/ireland/education/law/court_rules.baml` | `~/dev/ciandlithe/baml_src/education/law/court_rules.baml` | **Lift as-is** — court rules (the Civil Procedure Rules + Rules of the Superior Courts + District Court Rules) are the canonical cross-platform reference. |

#### §2.5 — cianchosaint (OSINT defence platform)

| # | Source (cianfhoghlaim) | Destination (sister repo) | Transformation |
|--:|---|---|---|
| D.1 | `baml_src/british_isles/ireland/education/law/courts.baml` | `~/dev/cianchosaint/baml_src/defence/law/courts.baml` | **Drop the marking-mode refs** (same as ciandlithe L.1); rename to `DefenceCourtsBAML` (defence platform, not education platform). |
| D.2 | `baml_src/british_isles/ireland/education/law/judgements.baml` | `~/dev/cianchosaint/baml_src/defence/law/judgements.baml` | **Drop the marking_mode field**; rename to `DefenceJudgementsBAML`; add the `clearance_level` field (OFFICIAL / OFFICIAL-SENSITIVE / SECRET) which is cianchosaint-specific. |
| D.3 | `baml_src/british_isles/ireland/education/law/legal_aid.baml` | `~/dev/cianchosaint/baml_src/defence/law/legal_aid.baml` | **Lift as-is** — legal_aid is a dependency for both ciandlithe (civil claims) and cianchosaint (military + veterans). |
| D.4 | `baml_src/british_isles/ireland/education/_shared/eiraic_treasures.baml` | `~/dev/cianchosaint/baml_src/defence/_shared/eiraic_treasures.baml` | **Lift as-is** — the Eiraic Treasures canonical BAML (the bilingual artefact-extraction surface) is identical for both platforms. **NOTE:** the path in the task brief was `agents/meaisinfhoghlaim/alignment/eiraic_treasures.py`; the canonical file is the `.baml` file at `baml_src/british_isles/ireland/education/_shared/eiraic_treasures.baml`. The Python module wrapper (if any) is in `agents/meaisinfhoghlaim/firecrawl_mcp/`. |
| D.5 | `cocoindex_flows/_shared/_docling_grid_segmenter.py` | `~/dev/cianchosaint/cocoindex_flows/_shared/_docling_grid_segmenter.py` | **Lift as-is** — the row × column detector is the canonical reference implementation for table extraction in cocoindex. cianchosaint uses it for the MoD corporate report + Public Inquiry extraction pipelines. |

#### §2.6 — gemini_hackathon (GCP-first hackathon repo)

| # | Source (cianfhoghlaim) | Destination (sister repo) | Transformation |
|--:|---|---|---|
| G.1 | `baml_src/british_isles/uk_ncce/learning_graph.baml` | `~/dev/gemini_hackathon/baml_src/education/learning_graph.baml` | **Drop the 14 LC subject extensions**; keep only the 5 NCCE subjects (Computing + Maths + Science + English + Geography). Rename the package to `_education_` (the canonical gemini_hackathon namespace). |
| G.2 | `baml_src/british_isles/uk_ncce/equivalencies.baml` | `~/dev/gemini_hackathon/baml_src/education/equivalencies.baml` | **Drop the jurisdiction-specific equivalencies** (the en/wl/ni/sc/im jurisdiction pairs); keep the canonical 5-jurisdiction equivalence (ENG + WAL + NIR + SCO + IoM → NCCE). |
| G.3 | `baml_src/british_isles/ireland/education/certification.baml` | `~/dev/gemini_hackathon/baml_src/education/certification.baml` | **Lift as-is** — the LC + JC certificate schema is the canonical certification shape; gemini_hackathon reuses it for the OSS-first substrate. |
| G.4 | `meaisinfhoghlaim/certificate/` (7-stage pipeline) | `~/dev/gemini_hackathon/meaisinfhoghlaim/certificate/` | **Lift as-is, with a `GEMINI_HACKATHON_PROFILE` flag** that drops the NCCA-specific stages (Stage4_RubricValidator) for the GCP-first path. |
| G.5 | `cocoindex_flows/uk_ncce/learning_graphs_app.py` | `~/dev/gemini_hackathon/cocoindex_flows/education/learning_graphs_app.py` | **Drop the CocoIndex LanceDB target**; switch to the BigQuery + GCS path (per the 6 GCP mirror stacks that gemini_hackathon already consumes). |

### §3 — Per-PR step-by-step checklists (6 sisters × ≥ 3 PRs × ≥ 3 items per PR)

Each lift patch in `openspec/sister-lifts/` ends with a per-PR
step-by-step checklist. The checklist shape is fixed across all 6
lift patches:

- `[ ]` step 1: copy the source file to the destination path
- `[ ]` step 2: apply the per-file transformation rules
- `[ ]` step 3: regenerate the baml_client (where applicable)
- `[ ]` step 4: add a CI gate that prevents the lifted file from drifting
- `[ ]` step 5: per-sister repo openspec change + PR

### §4 — Spec delta to `sister-repo-customisation` (1 file)

- **§4.1** `specs/sister-repo-customisation/spec.md` — adds 1 new
  Requirement: "Each sister repo MUST receive a per-file lift
  patch (transformation rules + per-PR checklist) before the
  cianfhoghlaim v6 era learnings can be activated in the sister
  repo."

## What stays behind

The Phase 12 lift is *explicitly* NOT a wholesale copy. The
following are excluded from the lift:

1. The 6 GCP mirror stack READMEs (B.2) — these are already in
   `bonneagar/` (the home repo); the sister repos reference them
   via Pangolin resources, not by copying the stack files.
2. The 11-component A2UI catalog (B.5) — bonneagar uses Pangolin
   UI, not A2UI.
3. The 16 LC Convex tables (B.3 partial) — the IaC substrate
   doesn't need BIEP tables.
4. The Lingala + French (CA) voice_profile additions (T.1) —
   tuatha is LC + JC only.
5. The 14 LC subject extensions to the NCCE learning_graph (G.1)
   — gemini_hackathon is the 5-subject OSS-first subset.
6. The CocoIndex LanceDB target (G.5) — gemini_hackathon uses
   BigQuery + GCS.

The "what stays behind" decisions are documented per-row in the
customisation matrix (§2 above) and per-file in each lift patch.

## Impact

- **Audience:** every sister repo maintainer (bonneagar +
  tuatha + ciancheiltis + ciandlithe + cianchosaint +
  gemini_hackathon).
- **Scope:** 6 lift patches (1 per sister) + 1 spec delta + 1
  test file.
- **LOC delta (this change):** ~1,200 LOC of markdown + ~120 LOC
  of test code in `tests/test_phase12_sister_repo_lift.py`.
- **LOC delta (deferred to sister repos):** ~3,500 LOC of code
  lifted across 6 sister repos (~580 LOC per sister on average).
- **Risk:** LOW — the lift patches are planning docs; the actual
  code transfer is per-sister-repo PRs reviewed by the sister repo
  maintainers.
- **Reversibility:** full — the lift patches can be revised
  before any sister-repo PR is opened.

## Dependencies

`Blocked by (hard):` none.

`Blocked by (soft):`

- `2026-09-01-sister-side-mirrors-v1/` (Phase 8 — the awareness
  scaffolding this change turns into actual code plans)
- All 23 openspec changes shipped in the v6 era (the lift
  patches reference the canonical surfaces they were written in)

`Enables:`

- Sister-side PRs can be created for each of the 6 sister repos
  (the actual code transfer work). Each sister repo gets its own
  openspec change in its own repo, scoped to the lift patches
  authored here.

`Affected repos:` `bonneagar` + `tuatha` + `ciancheiltis` +
`ciandlithe` + `cianchosaint` + `gemini_hackathon` (sister
repos).

## Out of scope

- The actual per-sister-repo PRs (the sister repo openspec
  changes propose their own PRs with the per-sister
  customisation).
- Wholesale copy of the cianfhoghlaim substrate into the sister
  repos — the operator's earlier directive forbids this.
- Phase 10 v7 rewrite — handled in
  `2026-09-01-v7-from-the-ground-up-v1/` (deferred per operator
  direction).
- Updating the v7 architecture doc.

## Quality gates (must pass before `openspec archive`)

```bash
uv run openspec validate 2026-09-XX-sister-repo-lift-v1 --strict  ✅
uv run pytest tests/test_phase12_sister_repo_lift.py -v  ✅ all 6 lift-patch assertions pass
```

---

*Last updated by build subagent at 2026-09-01.*
