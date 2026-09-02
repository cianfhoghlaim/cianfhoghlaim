# Sister-Repo Lift: `cianchosaint-defence-baml-lift-v1`

> **One-line summary:** Lift the legal BAML subset (courts +
> judgements + legal_aid) + the canonical Eiraic Treasures BAML +
> the Docling row × column detector from cianfhoghlaim into
> cianchosaint (the British-Isles OSINT defence platform sister
> repo). The legal BAML is renamed to DefenceBAML with a
> `clearance_level` field that is cianchosaint-specific.

## Source files (cianfhoghlaim)

| # | Source path | Bytes | Description |
|--:|---|--:|---|
| D.1 | `baml_src/british_isles/ireland/education/law/courts.baml` | ~8 KB | The courts BAML (CourtLevel + CourtType + Judge + court hierarchy). |
| D.2 | `baml_src/british_isles/ireland/education/law/judgements.baml` | ~10 KB | The judgements BAML (case ID + parties + ratio + obiter dicta + counsel). |
| D.3 | `baml_src/british_isles/ireland/education/law/legal_aid.baml` | ~5 KB | The legal aid BAML (Civil Legal Aid + Criminal Legal Aid + Legal Aid Board). |
| D.4 | `baml_src/british_isles/ireland/education/_shared/eiraic_treasures.baml` | ~10 KB | The Eiraic Treasures canonical BAML — the bilingual (Irish + English) artefact-extraction surface. **NOTE:** the path in the task brief was `agents/meaisinfhoghlaim/alignment/eiraic_treasures.py`; the canonical file is the `.baml` file at `baml_src/british_isles/ireland/education/_shared/eiraic_treasures.baml`. |
| D.5 | `cocoindex_flows/_shared/_docling_grid_segmenter.py` | ~12 KB | The row × column detector for table extraction in CocoIndex flows. |

## Destination files (cianchosaint)

| # | Destination path | Bytes | Source |
|--:|---|--:|---|
| D.1.dest | `~/dev/cianchosaint/baml_src/defence/law/courts.baml` | ~7 KB | D.1 (rename to `DefenceCourtsBAML`; drop LC marking-mode refs) |
| D.2.dest | `~/dev/cianchosaint/baml_src/defence/law/judgements.baml` | ~10 KB | D.2 (drop `marking_mode` field; add `clearance_level` field; rename to `DefenceJudgementsBAML`) |
| D.3.dest | `~/dev/cianchosaint/baml_src/defence/law/legal_aid.baml` | ~5 KB | D.3 (lift as-is — shared between ciandlithe + cianchosaint) |
| D.4.dest | `~/dev/cianchosaint/baml_src/defence/_shared/eiraic_treasures.baml` | ~10 KB | D.4 (lift as-is — canonical bilingual artefact extraction) |
| D.5.dest | `~/dev/cianchosaint/cocoindex_flows/_shared/_docling_grid_segmenter.py` | ~12 KB | D.5 (lift as-is — canonical reference implementation) |

## Transformation rules

### D.1 — courts.baml

| Rule | Before | After |
|---|---|---|
| **Package namespace** | `package ireland_education_law` | `package defence_law` (drop `ireland` and `education`; the defence platform is jurisdiction-agnostic) |
| **LC marking-mode refs** | The schema references `enum MarkingMode { CI1, CI2, CI3, H1, H2, H3 }` | **Drop** — cianchosaint uses court-level (SCCD/HC/SC/SupCt/Martial) marking |
| **Class names** | `class Court { ... }` | `class DefenceCourt { ... }` |
| **Function names** | `function ExtractCourt(case_text: string) -> Court` | `function ExtractDefenceCourt(case_text: string) -> DefenceCourt` |

### D.2 — judgements.baml

| Rule | Before | After |
|---|---|---|
| **Package namespace** | `package ireland_education_law` | `package defence_law` |
| **marking_mode field** | `class Judgement { ..., marking_mode: MarkingMode }` | **Drop** |
| **NEW clearance_level field** | n/a | `class DefenceJudgement { ..., clearance_level: ClearanceLevel }` — where `enum ClearanceLevel { OFFICIAL, OFFICIAL_SENSITIVE, SECRET, TOP_SECRET }` is the canonical cianchosaint classification |
| **Class names** | `class Judgement { ... }` | `class DefenceJudgement { ... }` |
| **Function names** | `function ExtractJudgement(...)` + `function ExtractJudgements(...)` | `function ExtractDefenceJudgement(...)` + `function ExtractDefenceJudgements(...)` |

### D.3, D.4, D.5 — No transformation

- D.3 — The legal aid BAML is shared between ciandlithe (civil claims) and cianchosaint (military + veterans). The schema shape is identical.
- D.4 — The Eiraic Treasures canonical BAML is the bilingual (Irish + English) artefact-extraction surface. cianchosaint uses it for the bilingual MoD corporate report + Public Inquiry extraction pipelines.
- D.5 — The row × column detector is the canonical reference implementation for table extraction in cocoindex. cianchosaint uses it for the MoD corporate report + Public Inquiry extraction pipelines.

## Per-PR step-by-step checklist

### PR #1 — Lift the courts + judgements BAML (with the rename transformation) (3 items)

- [ ] **1.1** Copy `baml_src/british_isles/ireland/education/law/courts.baml` → `~/dev/cianchosaint/baml_src/defence/law/courts.baml`; apply the 4 transformation rules
- [ ] **1.2** Copy `baml_src/british_isles/ireland/education/law/judgements.baml` → `~/dev/cianchosaint/baml_src/defence/law/judgements.baml`; apply the 5 transformation rules (including the new `clearance_level` field)
- [ ] **1.3** Regenerate the cianchosaint baml_client: `cd ~/dev/cianchosaint && uv run baml-cli generate`

### PR #2 — Lift the legal_aid BAML + the Eiraic Treasures canonical (4 items)

- [ ] **2.1** Copy `baml_src/british_isles/ireland/education/law/legal_aid.baml` → `~/dev/cianchosaint/baml_src/defence/law/legal_aid.baml` (no transformation)
- [ ] **2.2** Copy `baml_src/british_isles/ireland/education/_shared/eiraic_treasures.baml` → `~/dev/cianchosaint/baml_src/defence/_shared/eiraic_treasures.baml` (no transformation)
- [ ] **2.3** Wire the legal_aid + eiraic_treasures BAML consumers into `~/dev/cianchosaint/sources/{legalaid_ie,mod_corporate_reports,public_inquiries}.py`
- [ ] **2.4** Run `cd ~/dev/cianchosaint && uv run pytest sources/tests/test_legal_aid.py sources/tests/test_mod_corporate_reports.py -v`

### PR #3 — Lift the Docling grid segmenter + wire to MoD + Public Inquiry pipelines (5 items)

- [ ] **3.1** Copy `cocoindex_flows/_shared/_docling_grid_segmenter.py` → `~/dev/cianchosaint/cocoindex_flows/_shared/_docling_grid_segmenter.py` (no transformation)
- [ ] **3.2** Wire the grid segmenter into `~/dev/cianchosaint/cocoindex_flows/mod_corporate_reports_app.py`
- [ ] **3.3** Wire the grid segmenter into `~/dev/cianchosaint/cocoindex_flows/public_inquiries_app.py`
- [ ] **3.4** Author `~/dev/cianchosaint/cocoindex_flows/tests/test_docling_grid_segmenter.py` with the canonical row × column regression tests
- [ ] **3.5** Run `cd ~/dev/cianchosaint && uv run pytest cocoindex_flows/tests/test_docling_grid_segmenter.py -v`

## What stays behind (explicit)

- **The LC marking-mode refs (CI1/CI2/CI3/H1/H2/H3)** — these are
  LC exam-specific and stay in cianfhoghlaim. cianchosaint uses
  court-level (SCCD/HC/SC/SupCt/Martial) marking.
- **The `marking_mode` field on the `Judgement` class** — same
  reason.
- **The 7-vernacular BAML extractors** — these are BIEP-specific
  and stay in cianfhoghlaim + ciancheiltis.
- **The CocoIndex LanceDB target** — cianchosaint uses a separate
  cloud-native storage target (per the cianchosaint CI configs).

## Sister-repo hand-off

- Cianchosaint maintainer receives this lift patch + openspec
  change `2026-09-XX-cianchosaint-lift-v1.md` (authored in
  `~/dev/cianchosaint/openspec/changes/`).
- Approximate LOC delta: 530 LOC (~7 KB courts + ~10 KB
  judgements + ~5 KB legal_aid + ~10 KB eiraic_treasures + ~12 KB
  _docling_grid_segmenter + ~25 KB of CI/test scaffolding).

## NOTE: path correction in the task brief

The task brief listed
`/Users/cianmacandeisigh/dev/cianfhoghlaim/agents/meaisinfhoghlaim/alignment/eiraic_treasures.py`
as the source path. The actual canonical file is the BAML file at
`/Users/cianmacandeisigh/dev/cianfhoghlaim/baml_src/british_isles/ireland/education/_shared/eiraic_treasures.baml`.
This lift patch uses the canonical BAML source path (the
Python wrapper module if any lives at
`agents/meaisinfhoghlaim/firecrawl_mcp/`).
