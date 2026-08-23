# 2026-08-22-retire-pre-v7-oideachais-stubs-v1

## Why

The 2026-08-22-openspec-audit-and-merge-v1 audit identified 7 pre-v7
`oideachais-*` capability specs that should be retired per the v4
(2026-06-28) + v7 (2026-07-17) consolidations. Each is a single-Requirement
stub that says "Phase 1 complete" — they exist only as retirement markers,
not as authoritative specs.

This change archives the 3 single-Requirement stubs (where archiving is
unambiguous). The 4 content-bearing `oideachais-*` specs (baml-schemas 12 reqs,
cognify 4 reqs, marimo-dashboards 11 reqs, pipeline 16 reqs) require unique-
requirement extraction into their `cianfhoghlaim-*` successors — that's a
separate change (out of scope here).

## Scope

This change retires:

| Spec | Reqs | Action |
|:--|--:|:--|
| `oideachais-cocoindex-v1-migration` | 1 | **ARCHIVE** — retirement marker |
| `oideachais-leabharlann` | 1 | **ARCHIVE** — retirement marker |
| `oideachais-university-deep-extraction` | 1 | **ARCHIVE** — retirement marker |

The 3 archived specs preserve their content as a retirement marker with
one cross-reference Requirement pointing at the canonical
`cianfhoghlaim-*` successor.

## Out of scope (separate change)

The 4 content-bearing `oideachais-*` specs (which have real Requirements
beyond the retirement marker):

| Spec | Reqs | Successor | Action (future change) |
|:--|--:|:--|:--|
| `oideachais-baml-schemas` | 12 | `cianfhoghlaim-baml-schemas` (19) | MERGE unique reqs first, then ARCHIVE |
| `oideachais-cognify-knowledge-graph` | 4 | `cianfhoghlaim-cognify-knowledge-graph` (9) | MERGE unique reqs first, then ARCHIVE |
| `oideachais-marimo-dashboards` | 11 | `cianfhoghlaim-marimo-dashboards` (10) | MERGE unique reqs first, then ARCHIVE |
| `oideachais-pipeline` | 16 | `cianfhoghlaim-pipeline` (54) | MERGE unique reqs first, then ARCHIVE |

These 4 need a separate openspec change because each requires:
1. Diff the oideachais-* and cianfhoghlaim-* specs for unique Requirements
2. Add the unique ones as ADDED Requirements to the cianfhoghlaim-* spec
3. Archive the oideachais-* spec as a retirement marker

## Dependencies

`Blocked by: none` (the audit was the only prerequisite — already archived)
`Blocked by (soft): 2026-08-22-openspec-audit-and-merge-v1` (this change implements finding 1 of the audit)
`Affected repos: cianfhoghlaim`

## What changes

### Spec deltas

- **MODIFIED `oideachais-cocoindex-v1-migration`** — replace the single Requirement with a cross-reference pointing at `cianfhoghlaim-cocoindex-v1-migration`
- **MODIFIED `oideachais-leabharlann`** — replace the single Requirement with a cross-reference pointing at `cianfhoghlaim-leabharlann`
- **MODIFIED `oideachais-university-deep-extraction`** — replace the single Requirement with a cross-reference pointing at `cianfhoghlaim-university-deep-extraction`

After archive, the 3 specs become thin retirement markers with one Requirement each.

## Cross-references

- `openspec/changes/2026-08-22-openspec-audit-and-merge-v1/proposal.md` — finding 1 of the audit
- `openspec/specs/retrospective-cleanup/spec.md` — the umbrella drift cleanup spec
- `openspec/specs/dev-tooling-surfaces/spec.md` — covers the openspec workflow