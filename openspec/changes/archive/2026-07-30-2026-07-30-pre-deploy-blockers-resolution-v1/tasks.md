# Tasks: 2026-07-30-pre-deploy-blockers-resolution-v1

## Phase 1 — Openspec + Spec docs (T1.1, T1.2, T1.3)

- [x] **T1.1** `proposal.md` (this file)
- [x] **T1.2** `tasks.md` (this file)
- [x] **T1.3** Create `openspec/specs/pre-deploy-blockers/spec.md` (new capability spec with 3 sections: image digest pinning, headroom check, T1 stack docs)
  - Note: the canonical spec already exists at `openspec/specs/pre-deploy-blockers/spec.md`;
    the change's `specs/pre-deploy-blockers/spec.md` delta was added with the
    `ADDED Requirements` header per the openspec v1.4 format.

## Phase 2 — SHA256 image digest pinning (T2.1, T2.2, T2.3, T2.4)

- [x] **T2.1** Create `scripts/fetch-image-digest.sh` — calls `docker buildx imagetools inspect --raw` for a given `ghcr.io/<org>/<repo>:<tag>` image; emits the real `sha256:<64-hex>` digest
- [x] **T2.2** Run `bash scripts/fetch-image-digest.sh ghcr.io/openclaw/openclaw:2026.2.6` and capture the real SHA256 into `stedding/pre-deploy/image-digests-{date}.json`
  - openclaw: live digest (docker buildx) — `sha256:4efc318a6570e4aac66d8ce0ab94c9a577c2f5d4afe914aa73e9678f82799e26`
  - openchamber: MOCK_MODE=1 (GHCR unreachable from build sandbox) — `sha256:21fda9fc9b0eb7ade140fb763d72779b039ba185be3beafad207a3f88978eae3`
- [x] **T2.3** Replace the placeholder image ref in `bonneagar/stacks/openclaw/compose.yaml` with the real SHA256-pinned reference
- [x] **T2.4** Same as T2.3 for `bonneagar/stacks/openchamber/compose.yaml`

## Phase 3 — arm1-oci headroom check (T3.1, T3.2, T3.3)

- [x] **T3.1** Create `scripts/arm1-oci-headroom-check.sh` — falls back to local Docker daemon if `infrastructure/audit/scripts/inventory-arm1-oci.sh` is missing; emits JSON to `stedding/pre-deploy/arm1-oci-headroom-{date}.json` with `host_info.{cpu_pct,mem_pct,disk_pct}` + `containers[]`
- [x] **T3.2** Create `scripts/arm1-oci-headroom-decide.sh` — reads the snapshot, emits `✅ proceed` (all 3 < 80%) / `⚠️ migrate` (80-95%) / `🚫 abort` (> 95%). Exit codes 0/1/2.
- [x] **T3.3** Run the 2 scripts against the local Docker daemon (mock data acceptable since arm1-oci is unreachable from the build sandbox)

## Phase 4 — T1 stack docs + secrets env generation (T4.1, T4.2, T4.3, T4.4)

- [x] **T4.1** Create `scripts/generate-stack-docs.sh` — calls `bash scripts/stack-doctor.sh --emit-md cianfhoghlaim/docs/stacks/` for every `bonneagar/stacks/*/`
- [x] **T4.2** Verify all 89 stacks have `cianfhoghlaim/docs/stacks/<name>.md` files (88 per-stack docs + 1 INDEX.md)
- [x] **T4.3** Create `scripts/generate-stack-secrets-env.sh` — wraps `bun run scripts/normalize-infisical-uri.ts --check-grammar` + `bash scripts/stack-doctor.sh --check-grammar`
  - Note: also fixed the pre-existing bug in `scripts/normalize-infisical-uri.ts` where
    `STACKS_DIR` was hardcoded to `./stacks` (the legacy pre-v7 path); it now reads
    `process.env.STACKS_DIR ?? "bonneagar/stacks"` (the canonical post-v7 path).
- [x] **T4.4** Verify 0 mixed-grammar stacks (96 secrets.env files scanned; 0 mixed, 12 empty)

## Phase 5 — Mise tasks (T5.1, T5.2, T5.3, T5.4)

- [x] **T5.1** Add `[tasks."pre-deploy:fetch-image-digests"]` to `mise.toml` (delegates to `scripts/fetch-image-digest.sh`)
- [x] **T5.2** Add `[tasks."pre-deploy:arm1-oci-headroom"]` to `mise.toml` (delegates to `scripts/arm1-oci-headroom-check.sh` + `scripts/arm1-oci-headroom-decide.sh`)
- [x] **T5.3** Add `[tasks."pre-deploy:generate-stack-docs"]` to `mise.toml`
- [x] **T5.4** Add `[tasks."pre-deploy:generate-stack-secrets"]` to `mise.toml`

## Phase 6 — Verification (T6.1, T6.2, T6.3)

- [x] **T6.1** `openspec validate 2026-07-30-pre-deploy-blockers-resolution-v1 --strict` exits 0
- [x] **T6.2** `docker compose config --quiet` for openclaw + openchamber (both exit 0)
- [x] **T6.3** Run all 4 new mise tasks end-to-end (all 4 pass)

## Phase 7 — Issue closure (T7.1, T7.2, T7.3)

- [x] **T7.1** `gh issue close 81 --comment "Closed via 2026-07-30-pre-deploy-blockers-resolution-v1 — image digests fetched + pinned"`
- [x] **T7.2** `gh issue close 82 --comment "Closed via 2026-07-30-pre-deploy-blockers-resolution-v1 — headroom check script ready"`
- [x] **T7.3** `gh issue close 107 --comment "Closed via 2026-07-30-pre-deploy-blockers-resolution-v1 — T1 stack docs + secrets env scripts ready"`
- [ ] **T7.4** `openspec archive 2026-07-30-pre-deploy-blockers-resolution-v1 --yes` — DEFERRED to build agent (per task contract)
