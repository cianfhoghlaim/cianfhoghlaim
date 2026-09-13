## Context

The 7 `oideachais-*` / `cianfhoghlaim-*` spec pairs flagged by the
2026-09-02 spec-registry audit came in 2 distinct shapes: 3 of the
`oideachais-*` sides were deliberately-written retirement markers
(single-requirement specs that explicitly say "Phase X complete — see
cianfhoghlaim-Y for the canonical spec"), and 4 had genuine
content-side-by-side with the canonical successor. This change handles
only the retirement markers; the genuine content overlaps are deferred
to follow-up tasks. See `openspec/plans/2026-09-02-pipeline-rename-and-refactor-audit-v1.md`
for the audit's classification (this change's author verified each
classification by reading the actual `openspec/specs/oideachais-*/spec.md`
files, not by trusting the audit's high-level counts).

## Goals / Non-Goals

**Goals:**
- Retire the 3 single-requirement retirement-marker specs cleanly,
  without losing any contract the canonical successor doesn't already
  own.
- Document the classification logic so future spec-registry audits can
  apply the same criterion.

**Non-Goals:**
- This change does NOT resolve the 5 deeper content overlaps
  (`oideachais-pipeline` ↔ `cianfhoghlaim-pipeline`, etc.). Those are
  listed in `tasks.md` §3 as deferred follow-up work, not as
  fabricated merges in this change.
- This change does NOT touch the 3 versioned `british-isles-education-pipeline*`
  specs (`-v1` base + `-v2` + `-v3`). They are intentional versioned
  umbrellas covering the same surface at different evolution stages,
  not duplicates.
- This change does NOT fix any typos. The 2 typos named in the
  original audit (`meaisinfoghlaim-ocr-htr` and
  `ciandlithe-dlt-sources-carveout-v1`) do not exist as live specs in
  the current registry — the rename has already happened.

## Decisions

**Retire, don't delete outright.** A spec archive step removes the
capability from `openspec list --specs`, which is what we want — but
the change itself must use `## REMOVED Requirements` deltas against
each retirement marker, NOT `openspec rm` against the live spec.
This keeps the deletion auditable and reversible until archive.

**Verify each retirement marker by reading the spec, not by line count.**
The audit's "7 pairs" count was right, but its "7 genuine content
overlaps" framing was wrong — 3 of those 7 turned out to be
deliberately-written retirement markers. Line-count alone couldn't
tell; the `## Purpose` placeholder plus the 1-requirement shape was
the real signal.

## Risks / Trade-offs

- [Risk] After archive, the 3 retired specs disappear from
  `openspec list --specs` — any script or skill that hard-codes one
  of them by name will break → Mitigation: a grep before archive to
  enumerate every cross-reference (`rg -l "oideachais-leabharlann\|oideachais-cocoindex-v1-migration\|oideachais-university-deep-extraction" . --type-add 'spec:*.md' -tspec`)
  is in `tasks.md` §4.1; each finding is updated to point at the
  canonical successor.
- [Risk] Misclassifying a genuine content overlap as a retirement
  marker would silently delete a load-bearing invariant → Mitigation:
  this change's `tasks.md` §2.1 records the per-spec verification
  (reading the spec, not just line-count) that classified each
  candidate before retirement.

## Migration Plan

1. The 3 retired specs' `## Purpose` placeholder ("TBD - created by
   archiving change...") gets removed at archive time by `openspec
   archive --yes`.
2. After archive, `openspec list --specs` SHALL drop from 102 to 99.
3. Cross-references in skills/READMEs updated by `tasks.md` §4.1.