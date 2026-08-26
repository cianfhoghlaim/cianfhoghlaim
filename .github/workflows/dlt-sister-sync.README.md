# dlt-sister-sync — per-PR reusable workflow

Per the
[`2026-08-24-dlt-sources-to-multi-repo-scaffold-v1`](../changes/2026-08-24-dlt-sources-to-multi-repo-scaffold-v1/)
openspec change (Phase 2.3). This is the canonical reciprocal
mirror workflow for the 3-repo active topology
(cianfhoghlaim + ciandlithe + cianchosaint).

## Files

| File | Repo | Purpose |
| --- | --- | --- |
| `.github/workflows/dlt-sister-sync.yml` | **cianfhoghlaim** | The reusable workflow **definition** (workflow_call only) |
| `.github/workflows/dlt-sister-sync-call.yml` | **ciandlithe** | The call site — fires on PR to `dlt_sources/law/**` + `_cross/**` |
| `.github/workflows/dlt-sister-sync-call.yml` | **cianchosaint** | The call site — fires on PR to `dlt_sources/{defence,policing,intelligence_oversight}/**` + `_cross/**` |

## Inputs (to the reusable workflow)

| Input | Required | Default | Description |
| --- | --- | --- | --- |
| `sister-repo` | yes | — | Sister repo name (e.g. `ciandlithe`) |
| `changed-files` | yes | — | JSON manifest of changed file paths |
| `source-pr` | no | `0` | Sister repo PR number |
| `source-sha` | no | `""` | Sister repo commit SHA |
| `source-branch` | no | `main` | Sister repo branch |
| `target-branch` | no | `main` | Cianfhoghlaim branch to PR against |
| `dry-run` | no | `false` | Log the PR payload but do not POST |
| `macos-sed-target` | no | `darwin-bsd-sed` | macOS sed target platform identifier |

## Outputs

| Output | Description |
| --- | --- |
| `reciprocal-pr-number` | Cianfhoghlaim PR number opened |
| `reciprocal-pr-url` | Cianfhoghlaim PR URL |
| `per-file-count` | Number of mirrored files in the reciprocal PR |

## Flow

```
┌──────────────────────┐                              ┌────────────────────────────┐
│ ciandlithe           │                              │ cianfhoghlaim              │
│                      │                              │                            │
│ dlt-sister-sync-call │  uses: cianmacandeisigh/...  │ dlt-sister-sync.yml        │
│        │             │ ──────────────────────────▶   │       │                    │
│        ▼             │                              │       ▼                    │
│ build JSON manifest  │                              │ compute reciprocal paths   │
│ call reusable wf     │                              │ POST gh api .../pulls      │
│                      │                              │ apply labels:              │
└──────────────────────┘                              │   dlt-sister-sync          │
                                                      │   auto-mirror              │
                                                      │ trigger downstream         │
                                                      │   dlt:smoke-all           │
                                                      │ trigger Dagster sensor    │
                                                      │   dlt_nightly_mirror_merge │
                                                      └────────────────────────────┘
```

## Mirror path convention

```
<sister>/dlt_sources/<vertical>/<rel-path>
       ↓
cianfhoghlaim/dlt_sources/_sister_refs/<sister-repo>/<vertical>/<rel-path>
```

The reciprocal PR title is `dlt:sister-sync(<sister-repo>): <count> files from #<pr-num>`.

## PR labels

- `dlt-sister-sync` — visible to all reviewers
- `auto-mirror` — signals that the PR is auto-generated; not for human merge

## Downstream CI gate

Every reciprocal PR on cianfhoghlaim triggers the canonical
`mise run dlt:smoke-all` (per `tests/dlt/test_imports.py`). The
gate exits 0 as long as the 9 pre-existing FAILs remain stable; any
new FAIL is treated as a regression.

## Nightly mirror-merge

The Dagster sensor `dlt_nightly_mirror_merge` (at
`orchestration/defs/2_materials/dlt_nightly_mirror_merge.py`) runs at
02:30 UTC nightly (per `orchestration/automation/biiep_scheduling.py:NIGHTLY_AUDIT_CRON`
adjusted to `30 2 * * *`). It reads the
`dlt_sources/_sister_refs/<repo>/...` accumulated diff and emits a
`dlt:mirror-ack` notification back to the sister repo via
`gh api repos/<sister>/issues -f body=...`.

## Test with a dummy PR

The dummy-PR test stub lives at `scripts/test_dlt_sister_sync.sh` in
cianfhoghlaim. It:

1. POSTs to `gh api repos/cianmacandeisigh/cianfhoghlaim/pulls` with
   the dummy file `dlt_sources/_sister_refs/ciandlithe/law/england/_factory.py`
   + a fake SHA `deadbeef0000000000000000000000000000cafe`
2. Captures the response
3. Verifies the response shape (`{"number": int, "html_url": str}`)
4. Writes a JSON summary to `stedding/sync-reports/dlt-sister-sync-test-{ts}.json`

**NOTE**: The test stub does NOT require the sister repo to actually
exist or have an open PR. It exercises the GH API contract only.
Use `--dry-run` to validate the JSON payload shape without POSTing.

## Required secrets on cianfhoghlaim

| Secret | Purpose |
| --- | --- |
| `CROSS_REPO_PR_TOKEN` | A PAT with `repo` + `workflow` scope on both cianfhoghlaim and the sister repos |

## Related files

- `orchestration/defs/2_materials/dlt_nightly_mirror_merge.py` — the Dagster sensor that consumes the reciprocal PRs
- `orchestration/defs/2_materials/sister_repo_cognee_sync.py` — the Cognee twin-cluster sync (per Phase 2.4)
- `orchestration/defs/2_materials/lakehouse_maintenance.py` — the nightly DuckLake maintenance (sibling schedule)
- `mise.toml` — `[tasks."dlt:smoke-all"]` + `[tasks."sync:cognee"]` orchestrator
