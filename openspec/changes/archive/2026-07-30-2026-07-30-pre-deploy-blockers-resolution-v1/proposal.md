# 2026-07-30-pre-deploy-blockers-resolution-v1

## Why

The 3 pre-deploy blockers (GitHub issues #81, #82, #107) have been open since 2026-06-26 / 2026-07-10. They block the 2 Komodo deploy procedures:
- `km run procedure deploy-openclaw-arm1-oci` (issues #81 + #82)
- `km run procedure deploy-openchamber-arm1-oci` (issues #81 + #82)

This change ships the 3 scripts that resolve all 3 blockers. **Autonomous, no operator invocation required.**

## What changes

### 1. SHA256 image digest pinning (closes #81)

- **NEW**: `scripts/fetch-image-digest.sh` — fetches the real SHA256 digest for any `ghcr.io/<org>/<repo>:<tag>` image via `docker buildx imagetools inspect --raw`. Pin format: `ghcr.io/openclaw/openclaw:v1.16.3@sha256:<64-hex>`
- **MODIFIED**: `bonneagar/stacks/openclaw/compose.yaml` — replace `sha256:0000000000000000000000000000000000000000000000000000000000000000` with the real digest
- **MODIFIED**: `bonneagar/stacks/openchamber/compose.yaml` — same
- **MODIFIED**: `mise.toml` — add `[tasks."pre-deploy:fetch-image-digests"]` (delegates to `scripts/fetch-image-digest.sh`)
- **NEW**: `stedding/pre-deploy/image-digests-{date}.json` — captured digests audit log

### 2. arm1-oci headroom check (closes #82)

- **NEW**: `scripts/arm1-oci-headroom-check.sh` — runs the existing `./infrastructure/audit/scripts/inventory-arm1-oci.sh` + emits a JSON snapshot to `stedding/pre-deploy/arm1-oci-headroom-{date}.json`
- **NEW**: `scripts/arm1-oci-headroom-decide.sh` — reads the snapshot + emits a deploy-or-abort verdict (✅ proceed if all 3 < 80%; ⚠️ migrate if 80-95%; 🚫 hard abort if > 95%)
- **MODIFIED**: `mise.toml` — add `[tasks."pre-deploy:arm1-oci-headroom"]` (delegates to the 2 scripts in sequence)

### 3. T1 stack docs + secrets env generation (closes #107)

- **NEW**: `scripts/generate-stack-docs.sh` — calls the existing `bun run scripts/stack-doctor.sh --emit-md cianfhoghlaim/docs/stacks/` for every `bonneagar/stacks/*/`
- **NEW**: `scripts/generate-stack-secrets-env.sh` — calls `bun run scripts/normalize-infisical-uri.ts` + validates via `bun run scripts/stack-doctor.sh --check-grammar` against every `bonneagar/stacks/*/secrets.env`
- **MODIFIED**: `mise.toml` — add `[tasks."pre-deploy:generate-stack-docs"]` + `[tasks."pre-deploy:generate-stack-secrets"]`

## Dependencies

`Blocked by: none` — all 3 scripts can be written + tested locally.

`Affected repos: cianfhoghlaim` (single-repo)

## Estimated effort

~3 hours of mechanical work. The fetch-image-digest.sh script needs network access to GHCR for the 2 image digests. The arm1-oci headroom script can be tested against the local Docker daemon (returns mock data if arm1-oci is unreachable). The T1 stack docs scripts can be run against the 89 local stacks.

## Acceptance gates

- [ ] `openspec validate 2026-07-30-pre-deploy-blockers-resolution-v1 --strict` exits 0
- [ ] `bash scripts/fetch-image-digest.sh ghcr.io/openclaw/openclaw:v1.16.3` returns a real SHA256 (not `0000…0000`)
- [ ] `bash scripts/fetch-image-digest.sh ghcr.io/openchamber/openchamber:v1.16.3` returns a real SHA256
- [ ] `bash scripts/arm1-oci-headroom-check.sh` emits a JSON with `host_info.cpu_pct`, `host_info.mem_pct`, `host_info.disk_pct`, `containers[]`
- [ ] `bash scripts/arm1-oci-headroom-decide.sh` emits `✅ proceed` (or `⚠️ migrate` / `🚫 abort`)
- [ ] `bash scripts/generate-stack-docs.sh` creates `cianfhoghlaim/docs/stacks/<name>.md` for all 89 stacks
- [ ] `bash scripts/generate-stack-secrets-env.sh` reports 0 mixed-grammar stacks
- [ ] The 2 compose.yaml files have real SHAs (not `0000…0000`)
- [ ] Issues #81, #82, #107 closed via `gh issue close <id>`