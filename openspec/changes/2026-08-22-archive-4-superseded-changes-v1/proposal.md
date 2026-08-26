# 2026-08-22-archive-4-superseded-changes-v1

## Why

Per the 2026-08-22-stale-changes-triage-v1 (Group B: CLOSE), 4 pending
openspec changes are superseded by other completed work and should be
archived.

## Scope: 4 changes to archive

| Change | Tasks | Days stale | Superseded by |
|:--|--:|--:|:--|
| `2026-08-21-unsloth-v5-architecture-refinement-v1` | 12 | 11h | `2026-08-21-unsloth-v5-vision-llm-hermes-openclaw-opencode-marimo-integration-v1` (already archived) |
| `2026-08-21-complete-browserbase-archive-and-crawl4ai-mcp-v1` | 39 | 1d | `2026-08-21-archive-legacy-sruth-mcp-servers-v1` (KEEP, covers most of this) |
| `2026-08-13-count-drift-rebase-and-indexing-cognition-cleanup-v1` | 31 | 9d | Already done implicitly by the linter (no count drift in current state) |
| `2026-08-10-england-biiep-pipeline-v1` | 17 | 3h | Superseded by `british-isles-education-pipeline-v3` (the canonical BIEP) |

## What changes

This is a documentation-only change. It updates the per-change
`proposal.md` of each of the 4 superseded changes to mark them as
"Superseded by X" + adds a single retirement marker Requirement to a
documentation spec.

## Dependencies

`Blocked by: none` (the triage change was the only prerequisite — already archived)
`Blocked by (soft): 2026-08-22-stale-changes-triage-v1` (this change implements Phase 1 of the triage execution plan)
`Affected repos: cianfhoghlaim`

## Cross-references

- `openspec/changes/2026-08-22-stale-changes-triage-v1/proposal.md` — the triage document
- `openspec/changes/2026-08-22-openspec-audit-and-merge-v1/proposal.md` — the audit