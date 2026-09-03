# Proposal: Clean up dangling cross-references to deleted `infrastructure/legacy/{ANALYSIS,LOCKET-MODES}.md`

## Context

Round 11 phase 16 (`infrastructure-audit-phase-2-delete-superseded-legacy-docs`)
deleted 2 superseded reference docs:

- `infrastructure/legacy/ANALYSIS.md` (15,539 bytes) — superseded by `.agents/skills/kcg-pangolin-stack/SKILL.md`
- `infrastructure/legacy/LOCKET-MODES.md` (8,630 bytes) — superseded by `.agents/skills/kcg-locket-sidecar/SKILL.md`

At the time, the 2 cross-reference lines in the skill docs were
flagged as "user follow-up, NOT in this commit" because
`.agents/skills/*.md` was on the user's exclusion list of
pre-existing in-flight work. After phase 16 landed, the skill
docs still point at the deleted files (now dangling references).

## Current state (verified 2026-06-27)

Active references to the deleted files (post-Phase-16):

| Reference | Status |
|:--|:--|
| `.agents/skills/kcg-pangolin-stack/SKILL.md:155` | DANGLING (active, points to deleted file) |
| `.agents/skills/kcg-locket-sidecar/SKILL.md:201` | DANGLING (active, points to deleted file) |

Historical references (in archived openspec changes — KEEP as record):

| Reference | Status |
|:--|:--|
| `openspec/changes/archive/2026-06-27-infrastructure-audit-phase-2-delete-superseded-legacy-docs/proposal.md` | historical record (KEEP) |
| `openspec/changes/archive/2026-06-27-infrastructure-audit-phase-2-delete-superseded-legacy-docs/tasks.md` | historical record (KEEP) |
| `openspec/changes/archive/2026-06-27-infrastructure-audit-phase-2-delete-superseded-legacy-docs/specs/indexing-and-cognition/spec.md` | historical record (KEEP) |
| `openspec/specs/indexing-and-cognition/spec.md` (Phase 16 ADDED requirement + scenarios) | canonical spec (KEEP) |

The skill files are currently CLEAN (no pre-existing in-flight
modifications — verified via `git status -s`). Safe to edit.

## What changes

1. Edit `.agents/skills/kcg-pangolin-stack/SKILL.md`: remove the
   dangling `- \`infrastructure/legacy/ANALYSIS.md\` ... (now superseded)`
   line (currently line 155, the last line of "Cross-references").
2. Edit `.agents/skills/kcg-locket-sidecar/SKILL.md`: remove the
   dangling `- \`infrastructure/legacy/LOCKET-MODES.md\` ... (now superseded)`
   line (currently line 201, the last line of "Cross-references").

These are the ONLY 2 dangling cross-references in the active
repo (verified via `grep -rn "legacy/ANALYSIS\|legacy/LOCKET-MODES"`
excluding `.git`/`.venv`/`__pycache__`).

## Impact

- 2 lines removed from skill docs (1 per file)
- Risk: zero — surgical edits to 2 clean files
- Skill docs remain valid (`mise run lint:skills` = 123/123)
- Spec delta: 1 NEW scenario added to the existing Phase 16
  requirement "No superseded `infrastructure/legacy/{ANALYSIS,LOCKET-MODES}.md`"
  in `openspec/specs/indexing-and-cognition/spec.md`

## Why a NEW scenario (not a new requirement)

The capability is the same as Phase 16: ensure the legacy
files don't appear in the active repo. The original Phase 16
scenario "Files removed" only covered the deletion itself;
this follow-up covers the post-deletion cleanup. Adding a
scenario to the existing requirement keeps the spec
maintainable.

## Spec delta

Adds 1 NEW scenario to the existing Phase 16 requirement
(`no-dead-superseded-legacy-docs`) in
`openspec/specs/indexing-and-cognition/spec.md`.