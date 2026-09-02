## ADDED Requirements

### Requirement: Each sister repo MUST receive a per-file lift patch (transformation rules + per-PR checklist) before the cianfhoghlaim v6 era learnings can be activated in the sister repo

The Cianfhoghlaim sister-repo-customisation capability MUST
provide a per-sister-repo lift patch before the v6 era learnings
ship to that sister repo. A lift patch is a markdown file in
`openspec/sister-lifts/` with:

1. A clear 1-line summary of what's being lifted
2. The list of source files (paths in cianfhoghlaim)
3. The list of destination files (paths in the sister repo)
4. The transformation rules (rename / restructure / drop)
5. A per-PR step-by-step checklist (≥ 3 items per PR, ≥ 3 PRs per
   sister)

Per the 2026-09-XX-sister-repo-lift-v1 change (Phase 12 of the
cianfhoghlaim-nua v6 era plan), each of the 6 sister repos has a
lift patch:

- `openspec/sister-lifts/bonneagar-iac-gcp-mirror-lift-v1.md`
- `openspec/sister-lifts/tuatha-adk-pipecat-lift-v1.md`
- `openspec/sister-lifts/ciancheiltis-celtic-baml-lift-v1.md`
- `openspec/sister-lifts/ciandlithe-legal-baml-lift-v1.md`
- `openspec/sister-lifts/cianchosaint-defence-baml-lift-v1.md`
- `openspec/sister-lifts/gemini-hackathon-oss-substrate-lift-v1.md`

#### Scenario: The bonneagar lift patch is authored

- **WHEN** `2026-09-XX-sister-repo-lift-v1` archives
- **THEN** `openspec/sister-lifts/bonneagar-iac-gcp-mirror-lift-v1.md` exists
- **AND** it contains ≥ 5 source files (B.1-B.5)
- **AND** it contains ≥ 3 PRs
- **AND** each PR has ≥ 3 checklist items

#### Scenario: The 6 lift patches collectively cover all 6 sister repos

- **WHEN** the operator audits `openspec/sister-lifts/`
- **THEN** the directory contains exactly 6 lift patches
- **AND** each lift patch names a unique sister repo
- **AND** the union of the 6 lift patches covers the full v6 era
  surface (BAML + Convex + A2UI + Hono + React + CocoIndex + GCP
  + NCCE + certificate pipeline + Pipecat + TTS + planner +
  per-subject pattern + legal BAML + Celtic BAML + Eiraic
  Treasures + Docling grid segmenter)

### Requirement: The lift patches MUST be planning docs only — NOT actual code transfer

The Cianfhoghlaim sister-repo-customisation capability MUST
NOT modify files in the sister repos directly. The lift
patches are the per-sister-repo planning documents; the
actual code transfer happens in per-sister-repo PRs
authored by the sister repo maintainers.

The Phase 12 change therefore ships:
- 6 lift-patch markdown files
- 1 spec delta
- 1 test file

The Phase 12 change does NOT ship:
- Code in `~/dev/bonneagar/`, `~/dev/tuatha/`, `~/dev/ciancheiltis/`,
  `~/dev/ciandlithe/`, `~/dev/cianchosaint/`, or `~/dev/gemini_hackathon/`
- Updated v7 architecture doc
- Wholesale copies of the cianfhoghlaim substrate

#### Scenario: The lift patches stay planning docs

- **WHEN** `openspec archive 2026-09-XX-sister-repo-lift-v1 --yes` runs
- **THEN** the sister repo working trees are unchanged
- **AND** the lift patches in `openspec/sister-lifts/` are the only
  artefact of this change
- **AND** the sister repo maintainers receive a hand-off note with
  the lift patches + a per-sister scope summary
