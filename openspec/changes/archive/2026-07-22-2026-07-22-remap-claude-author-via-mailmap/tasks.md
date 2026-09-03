# Tasks

- [x] Add `.mailmap` at repo root with a single line:
      `cianfhoghlaim <cianmacliathain@gmail.com> <claude@anthropic.com>`
- [x] Commit `.mailmap` on `main` with message beginning
      `fix(attribution): …`
- [x] Force-push to origin (no `--force-with-lease` issues since
      `.mailmap` is a brand-new file, not a branch update)
- [x] Verify locally with `git shortlog -sn` (Claude count drops to 0)
- [x] Write the openspec proposal/tasks/spec delta documenting the
      new mechanism
- [ ] Run `openspec validate 2026-07-22-remap-claude-author-via-mailmap --strict`
- [ ] Apply the spec delta (creates MODIFIED requirements on
      `agent-runtime-and-attribution`)
- [ ] Commit the spec delta
- [ ] Verify on GitHub UI (Contributors graph) — manual visual check
- [ ] Re-apply the spec delta incrementally on the 33 `feat/*`
      branches once they get force-pushed (the mailmap on `main` will
      already do the display rewrite, but the spec should be present
      on those branches too for in-repo consistency)
- [ ] Archive the openspec change with
      `openspec archive 2026-07-22-remap-claude-author-via-mailmap --yes`
