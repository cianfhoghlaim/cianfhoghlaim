# Tasks — Unsloth v5 Architecture Refinement

Total: 8 tasks across 1 phase. Estimated effort: **~15 minutes** (all runtime verification).

## Phase 1 — Runtime verification (15 min)

- [ ] **1.1** Verify the Unsloth Studio is still running on `localhost:8888`: `curl -fs http://localhost:8888/api/auth/status | jq`
- [ ] **1.2** Verify the litellm has loaded 18+ unsloth routes: `curl -fs -H "Authorization: Bearer $LITELLM_MASTER_KEY" http://localhost:4000/v1/models | jq '[.data[] | select(.id | startswith("local/unsloth/") or startswith("public/unsloth/"))] | length'`
- [ ] **1.3** Run the 7-step verification protocol (per proposal.md § Verification). All 7 steps must pass.
- [ ] **1.4** Run `mise run lint:registry` to confirm no hardcoded model strings were introduced
- [ ] **1.5** Run `openspec validate 2026-08-21-unsloth-v5-architecture-refinement-v1 --strict` to confirm the change validates
- [ ] **1.6** Run `openspec validate --all` to confirm no regressions (139 specs expected)
- [ ] **1.7** (When Infisical is back online) `bun run scripts/init-vault.ts` to push `dev-baile/unsloth/api_key` to the vault and replace the hardcoded dev key
- [ ] **1.8** Commit + push: `git add -A && git commit -m "fix(unsloth-v5): replace container stack with direct host.docker.internal + Pangolin private resource" && git push`

## Done-when criteria

- [ ] All 7 steps of the verification protocol pass
- [ ] `openspec validate --all` returns 139/139
- [ ] `mise run lint:registry` exits 0
- [ ] `git push` succeeds

## Out of scope (future changes)

- Adding Cloudflare tunnel support (per Unsloth's `--secure` flag) for an additional public URL
- Replacing the hardcoded API key with an Infisical lookup once the vault is online
- Adding more unsloth model families (currently 16 + 1 public + 2 existing = 19 total)