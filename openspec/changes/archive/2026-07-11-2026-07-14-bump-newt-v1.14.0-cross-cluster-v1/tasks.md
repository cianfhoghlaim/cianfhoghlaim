# Tasks: 2026-07-14-bump-newt-v1.14.0-cross-cluster-v1

## Phase 0 — Pre-flight

- [x] Confirm `fosrl/newt:v1.14.0` is the latest release on GitHub
  - Result: `2026-07-02T21:54:12Z` by `@fosrl`; SHA: `60c78391e3b5cb8a260490fb26b8b7329ed5448077629da89a564af80d3a9fad`
- [x] Confirm the 3 image-pinning sites (bunchloch + arm1-oci + canonical)
- [x] Confirm no other code references `fosrl/newt:1.13.0` or `fosrl/newt:latest`

## Phase 1 — Bonneagar code changes

- [x] Create `bonneagar/stacks/newt/IMAGE` (canonical source of truth)
- [x] Edit `bonneagar/stacks/newt/docker-compose.yaml` (1 line: image pin)
- [x] Edit `bonneagar/stacks/pangolin/newt.yaml` (1 line: image pin)
- [x] Verify: `grep -rnE "fosrl/newt:(1\.13|latest)" bonneagar/stacks/` returns 0 matches (only in comments)

## Phase 2 — Openspec change

- [x] Write `proposal.md`
- [x] Write `cross-repo-sync.md`
- [x] Write `tasks.md` (this file)
- [x] Write `specs/infrastructure-stacks/spec.md` with 1 ADDED Requirement:
  - `### Requirement: newt image is pinned to v1.14.0 + SHA digest across all clusters`
  - 3 Scenarios: pinned at v1.14.0, mismatched version detected, image rotation via IMAGE file

## Phase 3 — Validate + commit + push

- [ ] `openspec validate 2026-07-14-bump-newt-v1.14.0-cross-cluster-v1 --strict` returns 0
- [ ] Commit on `pick-5b-bonneagar-v5-continuation`
- [ ] Push bonneagar branch
- [ ] Commit on `pick-4-biep-v1`
- [ ] Push cianfhoghlaim branch

## Phase 4 — Archive

- [ ] `openspec archive 2026-07-14-bump-newt-v1.14.0-cross-cluster-v1 --yes`
