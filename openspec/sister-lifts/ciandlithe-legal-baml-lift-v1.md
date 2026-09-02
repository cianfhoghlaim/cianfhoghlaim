# Sister-Repo Lift: `ciandlithe-legal-baml-lift-v1`

> **One-line summary:** Lift the 5 core legal BAML schemas
> (courts + judgements + shared_legal_enums + PIAB + court_rules)
> from cianfhoghlaim into ciandlithe (the British-Isles OSINT
> legal-data platform sister repo). The function names are
> renamed to disambiguate from cianfhoghlaim's LC exam judgement
> surface; the marking-mode refs are stripped.

## Source files (cianfhoghlaim)

| # | Source path | Bytes | Description |
|--:|---|--:|---|
| L.1 | `baml_src/british_isles/ireland/education/law/courts.baml` | ~8 KB | The courts BAML (CourtLevel + CourtType + Judge + court hierarchy). |
| L.2 | `baml_src/british_isles/ireland/education/law/judgements.baml` | ~10 KB | The judgements BAML (case ID + parties + ratio + obiter dicta + counsel). |
| L.3 | `baml_src/british_isles/ireland/education/law/shared_legal_enums.baml` | ~5 KB | The shared legal enums (CourtLevel, JudgeLevel, CaseStatus, DamagesTier, OffenceClass, etc.) — the canonical cross-platform taxonomy. |
| L.4 | `baml_src/british_isles/ireland/education/law/piab.baml` | ~6 KB | The Personal Injuries Assessment Board BAML (PIAB assessments + consent + award). |
| L.5 | `baml_src/british_isles/ireland/education/law/court_rules.baml` | ~9 KB | The court rules BAML (Civil Procedure Rules + Rules of the Superior Courts + District Court Rules). |

## Destination files (ciandlithe)

| # | Destination path | Bytes | Source |
|--:|---|--:|---|
| L.1.dest | `~/dev/ciandlithe/baml_src/education/law/courts.baml` | ~7 KB | L.1 (rename to `CourtsBAML`; strip LC marking-mode refs CI1/CI2/CI3/H1/H2/H3) |
| L.2.dest | `~/dev/ciandlithe/baml_src/education/law/judgements.baml` | ~9 KB | L.2 (rename functions to `ExtractOSINTJudgement` + `ExtractOSINTJudgements`) |
| L.3.dest | `~/dev/ciandlithe/baml_src/education/law/shared_legal_enums.baml` | ~5 KB | L.3 (lift as-is — canonical cross-platform taxonomy) |
| L.4.dest | `~/dev/ciandlithe/baml_src/education/law/piab.baml` | ~6 KB | L.4 (lift as-is — CI-specific) |
| L.5.dest | `~/dev/ciandlithe/baml_src/education/law/court_rules.baml` | ~9 KB | L.5 (lift as-is — canonical cross-platform reference) |

## Transformation rules

### L.1 — courts.baml

| Rule | Before | After |
|---|---|---|
| **Package namespace** | `package ireland_education_law` (BAML package directive) | `package education_law` (drop `ireland`; the package is jurisdiction-agnostic) |
| **LC marking-mode refs** | The schema references `enum MarkingMode { CI1, CI2, CI3, H1, H2, H3 }` | **Drop** — ciandlithe uses court-level (SCCD/HC/SC/SupCt) marking, not LC exam marking |
| **Class names** | `class Court { ... }` | `class OSINTCourt { ... }` (prefix to disambiguate) |
| **Function names** | `function ExtractCourt(case_text: string) -> Court` | `function ExtractOSINTCourt(case_text: string) -> OSINTCourt` |

### L.2 — judgements.baml

| Rule | Before | After |
|---|---|---|
| **Package namespace** | `package ireland_education_law` | `package education_law` |
| **marking_mode field** | `class Judgement { ..., marking_mode: MarkingMode }` | **Drop** the `marking_mode` field — ciandlithe doesn't do LC exam marking |
| **Class names** | `class Judgement { ... }` | `class OSINTJudgement { ... }` |
| **Function names** | `function ExtractJudgement(text: string) -> Judgement` | `function ExtractOSINTJudgement(text: string) -> OSINTJudgement` |
| **Function names (plural)** | `function ExtractJudgements(texts: string[]) -> Judgement[]` | `function ExtractOSINTJudgements(texts: string[]) -> OSINTJudgement[]` |

### L.3, L.4, L.5 — No transformation

- L.3 — The shared legal enums are the canonical cross-platform taxonomy (cianfhoghlaim has no jurisdiction-specific overrides; ciandlithe consumes them as-is).
- L.4 — The PIAB BAML is CI-specific; both cianfhoghlaim (LC Business exam marking on PIAB) and ciandlithe (OSINT PIAB) consume the same shape.
- L.5 — The court rules BAML is the canonical cross-platform reference; both repos consume the same shape.

## Per-PR step-by-step checklist

### PR #1 — Lift the courts + judgements BAML (with the rename transformation) (3 items)

- [ ] **1.1** Copy `baml_src/british_isles/ireland/education/law/courts.baml` → `~/dev/ciandlithe/baml_src/education/law/courts.baml`; apply the 4 transformation rules
- [ ] **1.2** Copy `baml_src/british_isles/ireland/education/law/judgements.baml` → `~/dev/ciandlithe/baml_src/education/law/judgements.baml`; apply the 4 transformation rules
- [ ] **1.3** Regenerate the ciandlithe baml_client: `cd ~/dev/ciandlithe && uv run baml-cli generate`

### PR #2 — Lift the shared legal enums + PIAB (4 items)

- [ ] **2.1** Copy `baml_src/british_isles/ireland/education/law/shared_legal_enums.baml` → `~/dev/ciandlithe/baml_src/education/law/shared_legal_enums.baml` (no transformation)
- [ ] **2.2** Copy `baml_src/british_isles/ireland/education/law/piab.baml` → `~/dev/ciandlithe/baml_src/education/law/piab.baml` (no transformation)
- [ ] **2.3** Wire the PIAB + shared_legal_enums consumers into `~/dev/ciandlithe/sources/courts_ie.py` (the PIAB scraper)
- [ ] **2.4** Run `cd ~/dev/ciandlithe && uv run pytest sources/tests/test_courts_ie_piab.py -v`

### PR #3 — Lift the court rules + author the CI gate (5 items)

- [ ] **3.1** Copy `baml_src/british_isles/ireland/education/law/court_rules.baml` → `~/dev/ciandlithe/baml_src/education/law/court_rules.baml` (no transformation)
- [ ] **3.2** Author `~/dev/ciandlithe/baml_src/education/law/court_rules.test.baml` with the canonical cross-platform court rules tests
- [ ] **3.3** Wire the court_rules BAML to the Courts.ie + BAILII + ICLR + CaseMine scrapers in `~/dev/ciandlithe/sources/{courts_ie,bailii,iclr,casemine}.py`
- [ ] **3.4** Author `~/dev/ciandlithe/.github/workflows/court_rules_ci.yml` with the per-PR court_rules regression gate
- [ ] **3.5** Open the PR + verify all CI checks pass

## What stays behind (explicit)

- **The LC marking-mode refs (CI1/CI2/CI3/H1/H2/H3)** — these are
  LC exam-specific and stay in cianfhoghlaim. ciandlithe uses
  court-level (SCCD/HC/SC/SupCt) marking, not LC exam marking.
- **The `marking_mode` field on the `Judgement` class** — same
  reason.
- **The 7-vernacular BAML extractors** — these are BIEP-specific
  and stay in cianfhoghlaim + ciancheiltis (the Celtic corpus).

## Sister-repo hand-off

- Ciandlithe maintainer receives this lift patch + openspec change
  `2026-09-XX-ciandlithe-lift-v1.md` (authored in
  `~/dev/ciandlithe/openspec/changes/`).
- Approximate LOC delta: 470 LOC (~7 KB courts + ~9 KB judgements
  + ~5 KB shared_legal_enums + ~6 KB PIAB + ~9 KB court_rules +
  ~30 KB of CI/test scaffolding).
