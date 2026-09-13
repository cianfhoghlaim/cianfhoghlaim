# Cross-repo sync: pipeline-sister-repo-handoff

This umbrella spans cianfhoghlaim + cianchosaint.

## Files touched

| Path | Repo | Change |
|:--|:--|:--|
| `openspec/changes/pipeline-sister-repo-handoff/proposal.md` | cianfhoghlaim | NEW |
| `openspec/changes/pipeline-sister-repo-handoff/tasks.md` | cianfhoghlaim | NEW |
| `openspec/changes/pipeline-sister-repo-handoff/specs/pipeline-sister-repo-handoff/spec.md` | cianfhoghlaim | NEW |
| `openspec/changes/sister-shared/spec.md` | cianfhoghlaim | NEW (the shared-stack contract) |
| `openspec/changes/cianfhoghlaim/spec.md` | cianfhoghlaim | NEW (the canonical surface) |
| `openspec/changes/pipeline-sister-repo-handoff/cross-repo-sync.md` | cianfhoghlaim | NEW (this file) |
| `cianchosaint/orchestration/defs/__init__.py` | cianchosaint | NEW (mirror) |
| `cianchosaint/orchestration/defs/{1_ingestion,2_materials,3_model_lifecycle,4_asset_generation,5_agent_ops}/` | cianchosaint | NEW (empty dirs) |
| `cianchosaint/orchestration/defs/2_materials/licence_enforcement_sensor.py` | cianchosaint | MOVED from old top-level |

## Files absorbed (archived under this umbrella)

- `cianchosaint-handoff-v1` ✓ Complete (archived under
  `openspec/changes/archive/2026-09-13-pipeline-sister-repo-handoff/cianchosaint-handoff-v1/`)
- `2026-09-13-cianchosaint-orchestration-init-v1` (7/9 in-progress;
  after archiving lives in `archive/2026-09-13-pipeline-sister-repo-handoff/`)

## Sister-repo consumers (no changes here)

- `ciandlithe/` — consumed via `openspec/changes/ciandlithe-dlt-sources-carveout-v1/`
- `ciancheiltis/` — consumed via `openspec/changes/2026-09-06-ciancheiltis-v1/`
- `tuatha/` — consumed via `openspec/changes/2026-08-25-tuatha-british-isles-mmo-consolidation-v1/`
- `gemini-hackathon/` — consumed via `openspec/changes/gemini-hackathon-sister-umbrella-contract/`

## Soft dependencies

- Dagster 1.13+ (for `dg list defs` parity) — already declared in
  the cianfhoghlaim pyproject.toml; cianchosaint pyproject needs
  bump to match (separate work).
- openspec CLI 1.11+ — already declared.
