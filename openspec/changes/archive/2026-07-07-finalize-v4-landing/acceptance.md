# Acceptance criteria — 2026-07-07-finalize-v4-landing

This change has **two** layers of acceptance:

1. **Structural** — the absorption mechanics worked
2. **Substantive** — the underlying work landed

## Structural acceptance

| # | Gate | Verification |
|--:|:--|:--|
| G1 | Mega-change validates `--strict` | `openspec validate 2026-07-07-finalize-v4-landing --strict` exits 0 |
| G2 | The 29 absorbed changes are in archive | `ls openspec/changes/archive/ | wc -l` ≥ 174 (was 145 before) |
| G3 | Each absorbed change has `ABSORBED.md` | `ls openspec/changes/archive/*/ABSORBED.md | wc -l` ≥ 29 |
| G4 | `openspec list` shows ≤ 2 in-progress changes | `openspec list --json | python3 -c "import json,sys; d=json.load(sys.stdin); print(sum(1 for c in d['changes'] if c['status']=='in-progress'))"` ≤ 2 |
| G5 | Surviving flagship is untouched | `diff -r openspec/changes/2026-07-06-british-isles-education-pipeline-v1 <snapshot>` shows no changes |

## Substantive acceptance

| # | Gate | Verification |
|--:|:--|:--|
| G6 | All 9 T1 changes reach 100% completion | Each `absorbed/<name>/ABSORBED.md` shows the post-mega-change completion status |
| G7 | All 6 T2 changes reach 100% completion | Same |
| G8 | All 5 T3 flagship work-streams reach 100% completion | Same |
| G9 | All 11 T4 infra sub-tasks reach 100% completion | Same |
| G10 | Canonical spec surface unchanged | `openspec list --specs | wc -l` = 49 (47 canonical + 1 `__pycache__` + 1 header) |
| G11 | All 47 canonical specs pass `openspec validate --strict` | `openspec list --specs` validator implicit |
| G12 | Skill metadata still valid | `mise run lint:skills` passes |
| G13 | No sruth/ ghost paths in openspec/ | `grep -r "sruth/" openspec/` = 0 hits (in rewritten files; only archived plans may show) |
| G14 | No Purpose: TBD in any spec | `grep -rln "Purpose: TBD" openspec/specs/` = 0 hits |
| G15 | The mega-change itself archives cleanly | After `mv` + commit, `openspec list` shows 1 surviving in-progress (BIEP v1) |

## How to verify

```bash
# Step 1 — structural
openspec validate 2026-07-07-finalize-v4-landing --strict

# Step 2 — copy counts
openspec list --json | python3 -c "import json,sys; d=json.load(sys.stdin); print(len(d['changes']))"

# Step 3 — absorbed-change presence
ls openspec/changes/archive/*/ABSORBED.md | wc -l   # expect ≥ 29

# Step 4 — spec health
openspec list --specs | wc -l   # expect 49

# Step 5 — code health
mise run lint:skills

# Step 6 — ghost-path residue
grep -r 'sruth/' openspec/   # expect 0 hits
grep -r 'Purpose: TBD' openspec/specs/   # expect 0 hits

# Step 7 — surviving flagship
openspec show 2026-07-06-british-isles-education-pipeline-v1 | head
```

If any gate fails, fix and re-verify before archiving the mega-change.
