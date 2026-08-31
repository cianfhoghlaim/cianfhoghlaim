# Active Openspec Roadmap

**Status (2026-08-26, corrected — the previous "0 active changes /
2026-07-29" claim below was 4 weeks stale and wrong by 60 changes):**
**60 active openspec changes** per `uv run openspec list` (verified
2026-08-26). 37 of those sit at 0/N tasks — created but not started,
several superseded by later work. This file cannot be trusted as a
point-in-time snapshot on this repo's change velocity; the numbers
above will be stale again soon. Always cross-check with:

```bash
uv run openspec list           # live active-change list + task completion + age
uv run openspec list --specs   # live spec list (101 specs as of 2026-08-26)
```

A full triage of the 60 active changes (archive the superseded 0/N
ones, confirm the rest are genuinely in-flight) was identified as
high-value follow-up work during the 2026-08-26 data-side-remediation
session but deliberately NOT executed in that session — it requires
judgment calls about which changes are superseded vs genuinely
pending that shouldn't be made unilaterally by an agent without the
owning developer's input, and several `openspec/changes/*` entries
were being actively created/edited by a concurrent session at the
time (dated as recently as today), making bulk archival risky.

## Active changes

_See `uv run openspec list` for the live list — not reproduced here (see Status above for why)._

## Forward-looking openspec seeds (tracked by issues)

The following changes were archived with "Forward seed / Deferred" notes. Reopen each when the corresponding work begins:

| Tracked by | Change | Scope |
|:--|:--|:--|
| issue #140 | `2026-07-30-biep-v3-sct-wls-ni-v1` | Scotland (SQA) + Wales (WJEC) + Northern Ireland (CCEA) — ~320 cohorts |
| issue #140 | `2026-07-31-biep-v3-crown-dependencies-v1` | Jersey + Guernsey + Isle of Man — ~120 cohorts |

## Deferred openspec changes (tracked by issues)

| Tracked by | Change | Scope |
|:--|:--|:--|
| issue #141 | `2026-08-15-centralized-model-schema-registry-and-deployment-control-panel-v1` (Phase 1.3-1.10 + 1.12-1.19) | Complete remaining MODEL_REGISTRY migrations |
| issue #142 | same change (Phase 2.2-2.5) | Activate BAML TypeScript codegen — root cause diagnosed 2026-08-26: `baml-cli generate` fails for ~240 of 334 `.baml` files (syntax errors, likely a CLI version bump); see `.agents/skills/schema-codegen/SKILL.md` "Current status" |
| issue #143 | same change (Phase 5) | Build web UI control panel |
| issue #144 | same change (Phase 7-9) | Pydantic dedup rollout |
| issue #145 | same change (Phase 7) | CocoIndex factory rollout (collapse Irish LC + BI parity Apps) |
| issue #146 | same change (Phase 8) | Refactor 10 per-jurisdiction Dagster assets |

## Open issues (11)

| # | Title | Status |
|:--|:--|:--|
| 81 | Pre-deploy: replace placeholder SHA256 image digests in openclaw + openchamber | help wanted |
| 82 | Pre-deploy: arm1-oci headroom check before openclaw + openchamber | help wanted |
| 107 | Follow up T1 stack docs and secrets env generation | open |
| 139 | Force-push remaining 33 feat/* branches after Claude Code trailer rewrite | open |
| 140 | BIEP v3 extension: Scotland/Wales/NI + Crown Dependencies | enhancement |
| 141 | Complete remaining MODEL_REGISTRY migrations | open |
| 142 | Activate BAML TypeScript codegen | open |
| 143 | Build web UI control panel | open |
| 144 | Pydantic dedup rollout | open |
| 145 | CocoIndex factory rollout | open |
| 146 | Refactor 10 per-jurisdiction Dagster assets | open |

## Next wave candidates (when a forward-looking issue is picked up)

The next wave should pick **one** of the 6 centralized-model-schema-registry follow-up issues (#141-#146) OR start the BIEP v3 extension (#140). The most valuable single-change target is **#145 CocoIndex factory rollout** — collapsing 14 CocoIndex v1 Apps into 1 factory would reduce ~3300 LOC and unblock the multimodal deferred work.
