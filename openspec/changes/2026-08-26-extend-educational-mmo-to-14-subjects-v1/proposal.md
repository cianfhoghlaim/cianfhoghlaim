# Change: Extend Educational MMO to 14 Subjects v1

## Why

The canonical `cianfhoghlaim-educational-mmo` spec currently
mandates the **8 NCCA Leaving Certificate subjects**
(Mathematics + Applied Mathematics + Chemistry + Geography +
History + English + Gaeilge + Computer Science). The standalone
`tuatha/` sub-project (`github.com/cianfhoghlaim/tuatha`)
extends coverage to **14 subjects** by adding 6 NCCA-adjacent
subjects (Accounting + Biology + Business + French + Irish (T2)
+ Physics) per the user's "all subjects" directive of
2026-08-26 + the BIEP hackathon / ciancheiltis / ciandlithe
evidence for high-demand NCCA-adjacent subjects.

This change extends the canonical main-repo spec to recognise
the 14-subject expansion. The 8 NCCA subjects remain the
canonical NCCA set; the 6 NCCA-adjacent subjects are an
additive extension the standalone tuatha repo ships. The
extension is **backwards-compatible** — every consumer that
expects 8 subjects still gets 8 NCCA subjects; consumers that
opt into the 14-subject surface get the 6 additional ones.

## What changes

### Layer 1 — MODIFIED `cianfhoghlaim-educational-mmo` spec

The `8 NCCA Subjects` requirement is extended to `14 NCCA +
NCCA-adjacent subjects`:

> **The system SHALL provide end-to-end per-subject
> pipelines for 14 subjects: the 8 NCCA Leaving Certificate
> subjects (mathematics + applied_mathematics + chemistry +
> geography + history + english + gaeilge + computer_science)
> + the 6 NCCA-adjacent subjects (accounting + biology +
> business + french + irish (T2) + physics).**

The 6 NCCA-adjacent subjects are an OPTIONAL extension
consumers can opt into. The 8 NCCA subjects remain
MANDATORY.

### Layer 2 — NEW `tuatha-british-isles-mmo` spec

The standalone `tuatha/` sub-project now ships a canonical
`tuatha-british-isles-mmo` spec that documents the 14-subject
expansion + the single MMO client + the per-subject
SUBJECT_WIRING_REGISTRY + the independent deployable TIER 3
subapp surface.

### Layer 3 — Mirror the standalone `tuatha/` openspec change

The standalone `tuatha/` repo's
`2026-08-26-tuatha-subject-expansion-to-14-v1` change is
mirrored to `openspec/changes/from-tuatha/` in this repo
(per the `kcg-sync-subapps` spec).

## Out of scope

- The 8 NCCA subjects + their existing per-subject stacks
  are preserved unchanged
- The on-chain AchievementToken credential is governed by
  the `learn-to-earn-token-credential` spec (unchanged)
- The 2D + 2.5D asset pipeline is governed by the
  `celtic-asset-generation` spec (unchanged)
- The `tuatha-platform` deprecated alias is left intact
  (the spec already supersedes it)

## Dependencies

- `Blocked by (soft): 2026-08-25-tuatha-british-isles-mmo-consolidation-v1`
  (the standalone tuatha consolidation — already shipped
  in commits c853e36 → 54c672a)
- `Blocked by (soft): 2026-08-26-tuatha-multimodel-2d-graphics-and-earn-pipeline-v1`
  (the multi-model 2D + 2.5D + earn pipeline — already shipped)

## Impact

- **Affected specs (2):**
  - `cianfhoghlaim-educational-mmo` — MODIFIED
    (8-subject requirement → 14-subject requirement)
  - `tuatha-british-isles-mmo` — NEW (the standalone spec)

- **New files (3):**
  - `openspec/changes/from-tuatha/2026-08-26-tuatha-subject-expansion-to-14-v1/{proposal.md,tasks.md,specs/cianfhoghlaim-educational-mmo/spec.md,specs/tuatha-british-isles-mmo/spec.md}` (4 mirrored files)
  - `openspec/specs/tuatha-british-isles-mmo/spec.md` (the canonical mirror)

- **Modified files (1):**
  - `openspec/specs/cianfhoghlaim-educational-mmo/spec.md`
    (the canonical 8 → 14 extension)
