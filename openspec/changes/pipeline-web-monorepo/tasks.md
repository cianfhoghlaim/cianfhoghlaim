# Tasks: pipeline-web-monorepo

> Cross-batch web monorepo topic contract.
> No absorbed dated changes currently in the active set (the bundled
> `2026-08-13-web-monorepo-consolidation-and-agent-integration-v1`
> is already archived).

## 1. Web monorepo umbrella contract

- [ ] **W1.1** Document the 162-task web monorepo consolidation contract (status: already complete per the archived change)
- [ ] **W1.2** Track the 14 web apps + 5 packages + turbo.json workspace
- [ ] **W1.3** Verify `pnpm dev` + `turbo build` + `turbo test` all pass

## 2. Verification

- [ ] Run `openspec validate pipeline-web-monorepo --strict` — pass

## Verification

```bash
cd ~/dev/cianchosaint-laim 2>/dev/null || cd ~/dev/cianchoshlaim
openspec validate pipeline-web-monorepo --strict
```
