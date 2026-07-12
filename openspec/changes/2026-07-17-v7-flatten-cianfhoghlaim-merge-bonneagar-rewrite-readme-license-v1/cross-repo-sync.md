# Cross-repo sync plan — v7 flatten + bonneagar re-merge

## Repos affected

- **cianfhoghlaim** (THIS repo): receives bonneagar contents + flattens
  own structure. The change is entirely contained in this repo.
- **bonneagar** (the standalone GitHub repo at
  `https://github.com/cianfhoghlaim/bonneagar.git`): becomes
  read-only after this change lands. Renamed to `archive-bonneagar`
  remote.
- **leabharlann** (the separate corpus repo at
  `https://github.com/cianfhoghlaim/leabharlann.git`): **NO changes**
  per the leabharlann-independence rule. A separate follow-up change
  in the leabharlann repo will update its README to reflect the new
  post-v7 cianfhoghlaim layout.

## Commit order

1. **cianfhoghlaim first** — this change lands entirely in the main
   repo. The sequence is:
   - `b1016692a` chore(snapshot) — Phase 1.1 catch-up
   - `deb333ff0` merge — Phase 2.2 IaC merge into main
   - `56c409dd3` chore(v7-flatten) — Phase 2.3 cianfhoghlaim/ → root
     + IaC → bonneagar/
   - `f98a8df29` chore(manifests) — Phase 2.4 manifest updates
   - (Phase 2.6-2.9 forthcoming) spec deltas + AGENTS.md + skills +
     pending openspec changes
   - (Phase 3 forthcoming) remote branch cleanup + bonneagar remote rename
   - (Phase 4 forthcoming) LICENSE.md edit + README.md rewrite

2. **bonneagar (archive)** — the final commit on `bonneagar/main`
   before this change was authored was
   `2230c3c3b fix(iac): rename POCKETID_CLIENT_ID`. That branch's tip
   is captured in the merge commit `deb333ff0` above. After this
   change lands, the `bonneagar` GitHub remote is renamed
   `archive-bonneagar` and no further commits are pushed.

## Push targets

- `origin` (the cianfhoghlaim GitHub remote): receives the v7 branch
  when the user explicitly asks for push.
- `archive-bonneagar` (the renamed bonneagar GitHub remote): no
  further commits. The remote retains its full history up to
  `2230c3c3b`.

## Order of operations

1. Finish Phase 2.6-2.9 (spec deltas + AGENTS.md + skills + pending
   openspec changes) — these are local-only commits.
2. Phase 3 (remote branch cleanup + remote rename) — destructive;
   once done, the repo is permanently simplified.
3. Phase 4 (LICENSE.md + README.md) — final text commits.
4. Phase 5 (verification battery) — must pass before Phase 6.
5. Phase 6 (push) — only when the user explicitly asks.

## What is NOT done in this change

- **leabharlann updates** — handled in a separate change in the
  leabharlann repo, scoped to README path updates + any
  cianfhoghlaim/ → root path references in its docs.
- **CI workflow file path updates** (`.github/workflows/*`,
  `.forgejo/workflows/*`) — handled in a follow-up change.
- **CI runs** — no CI is triggered by these commits (no push yet).
