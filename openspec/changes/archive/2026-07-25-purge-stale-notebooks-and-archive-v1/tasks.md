# 2026-07-25-purge-stale-notebooks-and-archive-v1 — Tasks

## Pre-implementation

- [ ] Verify openspec CLI ≥1.4: `openspec --version` → 1.4.1
- [ ] Verify Changes 1, 2, 3, 4 all merged on `feat/iac-ify-arm1-oci-control-plane`
- [ ] Verify the ccc code index is fresh: `bun run ccc:index`

## Stage 1 — Delete the 23-file stale LC subtree

- [ ] `rm -rf notebooks/leaving_cert/03_leaving_cert/`
- [ ] `git add -u notebooks/leaving_cert/03_leaving_cert/`
- [ ] Verify: `ls notebooks/leaving_cert/` — empty (or only README files)

## Stage 2 — Delete the 26-file `legacy/` subtree

- [ ] `rm -rf notebooks/legacy/corpora/`
- [ ] `rm -rf notebooks/legacy/leaving_cert_teacher_view/`
- [ ] `git add -u notebooks/legacy/`
- [ ] Verify: `ls notebooks/legacy/` — empty (will be replaced by README)

## Stage 3 — Create `notebooks/legacy/README.md`

- [ ] CREATE `notebooks/legacy/README.md` with:
  - A redirect to `notebooks/12_corpus_overview.py` (post-Change 4 name)
  - A git history note for the deleted corpora:
    "The legacy corpus notebooks (medicine, law, culture, politics,
    technology, author_archive, leaving_cert_teacher_view) have been
    folded into `12_corpus_overview.py`. The git history preserves the
    original files via `git log -- notebooks/legacy/corpora/`."

## Stage 4 — Archive all 5 openspec changes

- [ ] `openspec archive 2026-07-25-nb-utils-ibis-first-v1 --yes`
- [ ] `openspec archive 2026-07-25-cocoindex-per-subject-dedup-v1 --yes`
- [ ] `openspec archive 2026-07-25-baml-archive-orphaned-and-superseded-v1 --yes`
- [ ] `openspec archive 2026-07-25-flatten-notebooks-v1 --yes`
- [ ] `openspec archive 2026-07-25-purge-stale-notebooks-and-archive-v1 --yes`
- [ ] Verify: `openspec list` — all 5 changes now show as archived

## Stage 5 — Spec delta + validation

- [ ] Write the spec delta to
  `openspec/changes/2026-07-25-purge-stale-notebooks-and-archive-v1/specs/oideachais-marimo-dashboards/spec.md`
  with 2 `## REMOVED Requirements` sections
- [ ] Run `openspec validate 2026-07-25-purge-stale-notebooks-and-archive-v1 --strict`
- [ ] Commit the change on a dedicated branch `openspec/2026-07-25-purge-stale-notebooks-and-archive-v1`
- [ ] Open a PR on `origin/main` referencing this change
- [ ] Run `mise run lint:skills` — must remain 53/53
- [ ] After the PR merges and the change is deployed, the work is complete

## Post-implementation hand-off

- [ ] File any remaining bugs as GitHub issues
- [ ] Update `docs/notebooks/v8-flatten.md` with the final status
- [ ] Run `./scripts/sync_agent_docs.sh` per the global agent protocol
- [ ] Final summary email/Slack announcement (if applicable)