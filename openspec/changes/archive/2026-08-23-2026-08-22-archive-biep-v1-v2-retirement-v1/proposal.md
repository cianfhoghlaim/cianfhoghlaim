# 2026-08-22-archive-biep-v1-v2-retirement-v1

## Why

The 2026-08-22-openspec-audit-and-merge-v1 audit identified that
`british-isles-education-pipeline-v1/v2/v3` (3 versioned specs) coexist
with 70 total requirements:
- v1 (41 reqs) — the original LC subjects + gov.ie circulars
- v2 (4 reqs) — the 4-jurisdiction upgrade bridge (transitional)
- v3 (25 reqs) — the 5-milestone sequential plan (canonical)

This change archives v1 + v2 as retirement markers (similar to the
Phase E1 `oideachais-*` retirement). The v3 stays as the canonical;
a separate Phase E follow-up change may rename v3 to drop the `-v3`
suffix.

## Scope

This change archives:

| Spec | Reqs | Action |
|:--|--:|:--|
| `british-isles-education-pipeline` (v1) | 41 | **KEEP** — this is the canonical name; v1 is the current canonical spec. No action. |
| `british-isles-education-pipeline-v2` | 4 | **ARCHIVE** — retirement marker |
| `british-isles-education-pipeline-v3` | 25 | **KEEP** — the canonical 5-milestone plan |

Wait — this raises a question. The audit's Finding 2 said "v1 = the original (41 reqs) → ARCHIVE; v2 = 4-jurisdiction bridge → ARCHIVE; v3 = 5-milestone plan → RENAME to canonical (drop -v3 suffix)".

But the canonical name `british-isles-education-pipeline` is currently the v1 spec (41 reqs). To "rename v3 to canonical" would require:
1. Move v3 file to `british-isles-education-pipeline/spec.md` (overwrite v1)
2. Move v1 file to `british-isles-education-pipeline-v1/spec.md` (preserve)
3. Update all references

This is a destructive operation (loses 41 v1 reqs unless we preserve them). The audit's "non-destructive merge" recommendation is actually a renaming operation, not a true merge.

**Revised approach (this change):**
1. KEEP `british-isles-education-pipeline` (v1) as the canonical name (the 41 v1 reqs are still valid)
2. ARCHIVE `british-isles-education-pipeline-v2` as a retirement marker
3. KEEP `british-isles-education-pipeline-v3` (the 25 v3 reqs cover the v3 5-milestone plan)
4. The v1 + v3 coexist; v1 = the original spec; v3 = the umbrella for the 5-milestone rollout

This is more conservative than the audit's recommendation. The full rename is deferred to a follow-up Phase E change that handles the file system move.

## What changes

### Spec deltas

- **MODIFIED `british-isles-education-pipeline-v2`** — replace the 4 Requirements with a single retirement marker pointing at v3

The 4 v2 Requirements are:
- `4-jurisdiction BIEP coverage`
- `4-path OCR/VLM ensemble with RAGAS voting`
- `Cross-jurisdiction marimo portal`
- `England ChangeDetection freshness guarantee`

All 4 are superseded by v3 requirements (the 5-milestone plan + per-cohort 5-phase pattern).

## Out of scope (separate change)

- **Rename `british-isles-education-pipeline-v3` → `british-isles-education-pipeline`** — requires a file system move + reference updates. The current canonical name is the v1 spec (41 reqs); renaming v3 to drop the suffix would overwrite v1 unless we first move v1 to `british-isles-education-pipeline-v1/`.
- **Archive the 4 content-bearing `oideachais-*` specs** (baml-schemas, cognify, marimo-dashboards, pipeline) — done in a separate change (Phase E2 follow-up).
- **Triage the 34 stale pending changes** — Phase E3.

## Dependencies

`Blocked by: none` (the audit was the only prerequisite — already archived)
`Blocked by (soft): 2026-08-22-openspec-audit-and-merge-v1` (this change implements finding 2 of the audit)
`Affected repos: cianfhoghlaim`

## Cross-references

- `openspec/changes/2026-08-22-openspec-audit-and-merge-v1/proposal.md` — finding 2 of the audit
- `openspec/specs/british-isles-education-pipeline-v3/spec.md` — the canonical 5-milestone plan