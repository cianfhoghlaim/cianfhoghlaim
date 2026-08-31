# Change: Tuatha Subject Expansion 8 → 14 v1

## Why

The standalone `tuatha/` repo (`github.com/cianfhoghlaim/tuatha`)
currently covers the canonical **8 NCCA Leaving Certificate
subjects** (Mathematics + Applied Mathematics + Chemistry +
Geography + History + English + Gaeilge + Computer Science) per
the `cianfhoghlaim-educational-mmo` spec.

The user (per the session 2026-08-26 directive) wants the
standalone tuatha to ship with **ALL** subjects — including the
6 NCCA-adjacent subjects that the BIEP hackathon pilots +
the ciancheiltis/ciandlithe jurisdictions exposed as
high-demand:

- **accounting** (cuntasaíocht) — financial + management
- **biology** (bitheolaíocht) — cell biology + genetics + ecology
- **business** (gnó) — people management + marketing + finance
- **french** (fraincis) — reading + writing + aural + oral
- **irish (T2)** — non-Gaeltacht learner pathway (distinct from
  the existing `gaeilge` T1 native-fluent pathway)
- **physics** (fisic) — mechanics + waves + electricity + modern

This change extends the standalone tuatha from 8 → 14 subjects
by adding 6 new NCCA-adjacent subjects. Each new subject ships
with the full per-subject stack (subject agent + 5 tools + BAML
contract + DLT source × 5 categories + PixiJS realm route +
sprite bank).

## What changes

### Layer 1 — 6 new subject agents

- **NEW** `tuatha/subjects/{accounting,biology,business,french,irish,physics}.py` — 6 ADK LlmAgent instances

### Layer 2 — 30 new per-subject tools

- **NEW** `tuatha/tools/<subject>_<tool>.py` — 6 subjects × 5 tools (syllabus_lookup / past_paper_lookup / marking_scheme_lookup / formative_item_generate / response_score)

### Layer 3 — 6 new BAML contracts

- **NEW** `tuatha/baml/qpack_{accounting,biology,business,french,irish,physics}.baml` — 6 BAML function sets (Generate<S>PastPaper + Generate<S>MarkingScheme + Generate<S>FormativeItem + Score<S>FormativeResponse + Generate<S>Syllabus)

### Layer 4 — 30 new DLT sources

- **NEW** `tuatha/dlt/{syllabus,past_paper,marking_scheme,formative_item,response_score}/<subject>.py` — 6 subjects × 5 categories (the thin re-exports of the canonical `ncca_<category>_source` template from commit `cf0d296`)

### Layer 5 — 6 new PixiJS realm routes

- **NEW** `tuatha/web/apps/tuatha-ui/src/routes/realm/{accounting,biology,business,french,irish,physics}.tsx` — 6 TanStack Start routes
- **MODIFIED** `tuatha/web/apps/tuatha-ui/src/router.tsx` — registers the 6 new routes
- **MODIFIED** `tuatha/web/packages/realm-canvas/src/types.ts` — adds 6 new `SubjectSlug` union members + 6 new `ALL_SUBJECT_SLUGS` entries

### Layer 6 — 6 new sprite banks

- **NEW** `tuatha/web/packages/realm-canvas/src/subjects/{accounting,biology,business,french,irish,physics}.ts` — 6 `RealmDescriptor` instances (palette + sprite bank + bilingual title + tagline + tiltRadians)

### Layer 7 — routing.py extension

- **MODIFIED** `tuatha/routing.py` — adds 6 new `SUBJECT_WIRING_REGISTRY` entries + 6 new `ROUTING_KEYWORDS` buckets (acct / biol / bus / fren / iris / phys)

### Layer 8 — openspec specs population

- **NEW** `openspec/specs/cianfhoghlaim-educational-mmo/spec.md` — copied from the canonical main repo (8 NCCA subjects)
- **NEW** `openspec/specs/celtic-asset-generation/spec.md` — copied from main repo
- **NEW** `openspec/specs/learn-to-earn-token-credential/spec.md` — copied from main repo
- **NEW** `openspec/specs/tuatha-british-isles-mmo/spec.md` — NEW spec (the standalone British Isles MMO spec)

## Out of scope

- The 8 NCCA subjects + their existing per-subject stacks are
  preserved unchanged (no renames, no schema migrations).
- The cross-subject mastery dashboard + the FIBO emblem
  rendering + the 2.5D PixiJS renderer are unchanged
  (the new sprite banks are additive).
- The `learn-to-earn-token-credential` AchievementToken spec
  is mirrored as-is (no change to the on-chain surface).

## Dependencies

- `Blocked by (soft): 2026-08-26-tuatha-multimodel-2d-graphics-and-earn-pipeline-v1`
  (the multi-model 2D + 2.5D + earn pipeline — already shipped
  in commits `b6a0e86` + `ca4f142`)

- `Blocked by (soft): 2026-08-25-tuatha-british-isles-mmo-consolidation-v1`
  (the standalone tuatha consolidation — already shipped in
  commits `b86ea3a` + `cf0d296`)

## Impact

Affected specs (2 MODIFIED + 1 NEW):

| Spec | Action | Reason |
|:--|:--|:--|
| `cianfhoghlaim-educational-mmo` | **MODIFIED** | the canonical spec's "8 NCCA subjects" requirement is extended to "14 subjects (8 NCCA + 6 NCCA-adjacent)" |
| `tuatha-british-isles-mmo` | **NEW** | the standalone British Isles MMO spec is authored for the first time |

Affected code (60 NEW files + 4 MODIFIED):

- 6 subject agents + 30 tools + 6 BAML contracts + 30 DLT
  sources + 6 PixiJS realm routes + 6 sprite banks = 84 NEW
- `tuatha/subjects/__init__.py` + `tuatha/tools/__init__.py`
  + `tuatha/routing.py` + `tuatha/web/apps/tuatha-ui/src/router.tsx`
  + `tuatha/web/packages/realm-canvas/src/types.ts` = 5 MODIFIED
- 4 NEW openspec specs in `openspec/specs/`

## Quality gates

- [ ] G1: `openspec validate 2026-08-26-tuatha-subject-expansion-to-14-v1 --strict` PASS
- [ ] G2: `ruff check tuatha/` all checks passed
- [ ] G3: `python3 -c "from tuatha.subjects import accounting, biology, business, french, irish, physics"` OK
- [ ] G4: `python3 -c "from tuatha.tools import *"` 70 tools OK
- [ ] G5: PixiJS smoke test on `/realm/accounting` + `/realm/physics` 2/2 routes render
