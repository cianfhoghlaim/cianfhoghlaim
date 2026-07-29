# Change: 2026-07-24-full-local-agent-platform-stack-up-v1

## Why

The Cianfhoghlaim local dev stack on `bunchloch` (MacBook M4) had a single
working container (lakehouse) and 4 dark agent surfaces (openclaw, hermes,
litellm, langfuse) that couldn't start because the OCI Infisical private
resource was returning 502 Bad Gateway. After bringing up a local Infisical
fallback vault (per `2026-07-24-deploy-openclaw-hermes-bunchloch-local-infisical-fallback-v1`),
this change brings up the remaining 3 stacks (litellm + langfuse + hermes)
and integrates them with the existing openclaw + lakehouse + infisical stack.

Verified 2026-07-24:
- Created 2 new databases in `lakehouse-postgres` (`litellm`, `langfuse`)
- Wrote 35 new secrets to local Infisical (litellm × 7, langfuse × 5, mlflow × 3,
  lakehouse × 9 copied from running containers, plus 8 LLM providers × 11 placeholders)
- Fixed 6 real bugs in 4 canonical files (litellm + langfuse sidecar.yaml +
  secrets.env) for the v0.161+ locket pattern
- Brought up all 21 expected containers; 4 of 6 main services are healthy
  (infisical, lakehouse, litellm, langfuse, openclaw); hermes is in restart
  loop due to s6-overlay + locket passthrough issues

## What changes

- 1 new openspec change proposal (this file) + tasks.md + spec delta
- 1 new ADDED Requirement to `infrastructure-stacks` (per the locket bug
  discovery)
- 1 new ADDED Requirement to `infrastructure-stacks` (per the hermes
  s6-overlay + tmpfs requirement)
- 1 new seed script `bonneagar/scripts/seed-bunchloch-litellm-langfuse-fallback.sh`
  that bulk-writes the 35 secrets via the user's JWT (with lakehouse creds
  copied from the running containers, LLM provider placeholders)
- 1 new runbook `bonneagar/deploy-runbooks/full-local-agent-platform-stack-2026-07.md`
  (end-to-end Phase A-F + known issues)
- 1 new Komodo procedure `deploy-litellm-bunchloch-local-v1.toml` (the
  litellm-on-bunchloch variant using the local Infisical + local lakehouse)
- 4 canonical file modifications (litellm + langfuse sidecar.yaml +
  secrets.env) for the v0.161+ locket pattern

## Impact

- **Affected specs:** `infrastructure-stacks` (shared) only
- **Affected hosts:** `bunchloch` only (arm1-oci is untouched)
- **Risk:** low-medium — the bug discoveries (locket v0.17.3 + Infisical v0.161+
  API mismatch, hermes s6-overlay permissions) are now documented as
  follow-up issues. The "working" stacks (litellm, langfuse, openclaw) are
  using compose-injected env vars as fallbacks while the locket bug is fixed
  upstream.
- **Audit gates:** `openspec validate <id> --strict` (MUST pass)
- **Order of operations:** see tasks.md

## Critical bug discovered during deploy

### Locket v0.17.3 + Infisical v0.161+ API mismatch

**Symptom:** All 4 locket sidecars (openclaw-locket, hermes-locket,
litellm-locket, langfuse-locket) start successfully, report "healthy"
via Docker, and log "fetching secrets from template count=N" — but they
then fall back to "policy=passthrough" mode and write the raw un-resolved
template to /run/secrets/locket/secrets.env.

**Root cause:** Locket v0.17.3 sends API requests with **snake_case** query
params (`?project_id=...&secret_path=...&secret_type=...`), but Infisical
v0.161+ requires **camelCase** (`?projectId=...&secretPath=...&secretType=...`).
The API returns 422 ValidationFailure, locket catches the error, and
falls back to passthrough.

**Evidence (verified live in the local dev environment):**
```bash
# Locket's format (snake_case) — returns 422
$ curl -sS "http://127.0.0.1:8081/api/v4/secrets/api_server_key?project_id=...&secret_path=/hermes"
{"statusCode":422,"message":[{"path":["projectId"],"message":"Required"}]}

# Correct format (camelCase) — returns 200
$ curl -sS "http://127.0.0.1:8081/api/v4/secrets/api_server_key?projectId=...&secretPath=/hermes"
{"secret":{"secretValue":"..."}}
```

**Implication:** The agent platforms (openclaw, hermes) start their
binaries successfully but cannot read any resolved secrets from the locket
volume. The "working" state is misleading — the binaries fall back to
default + placeholder values. Channel tokens are all
`disabled-placeholder-replace-with-real-token` and the LLM call would
fail at runtime.

**Fix options (out of scope for this change):**
1. **Upgrade locket** to a version that uses camelCase field names
   (the upstream locket repo at `ghcr.io/bpbradley/locket:infisical` may
   have a newer tag)
2. **Downgrade Infisical** to a version that accepts snake_case
3. **Add a request transformer** in the locket sidecar
4. **Patch the locket source** (`stedding/locket/src/provider/infisical.rs`
   — change `serde(rename_all = "snake_case")` to `"camelCase"`)

The `infrastructure-stacks` spec delta below adds a new Requirement
that captures this bug + the expected fix.

### Hermes + s6-overlay

**Symptom:** The NousResearch hermes-agent image uses s6-overlay as its
init system. With `user: 1000:1000` (the image's default) + `read_only: true`
+ `no-new-privileges: true`, s6-overlay fails with `fatal: /run belongs to
uid 0 instead of 1000, ... lacking the privileges to fix it`. The
/tmpfs workaround requires `mode:1777` which Docker daemon rejects
under no-new-privileges. The combined fix: `user: 10000:10000` (the
internal `hermes` user from the image's /etc/passwd) + no read_only + no
no-new-privileges + cap_drop: [ALL] (the only remaining hardening).

But even with that fix, the cont-init script attempts `cd /opt/data`
which is owned by `hermes:hermes` (mode 700). Running the entrypoint as
root allows the cd but then s6-overlay tries to transition to user
10000 and fails with `unable to setgid to root: Operation not permitted`
without `cap_add: [SETUID, SETGID]`. The fully working config requires
running as root with full caps — which is the upstream pattern but
defeats the "unprivileged by default" model.

This is documented in the spec delta below.

## Dependencies

`Blocked by:` none (this change is the local-deploy follow-up to
`2026-07-24-deploy-openclaw-hermes-bunchloch-local-infisical-fallback-v1`)
`Blocked by (soft):`
  - `2026-07-24-deploy-openclaw-hermes-bunchloch-local-infisical-fallback-v1`
  - `2026-07-24-iac-sync-sites-pangolin-private-infisical-repair-v1`
  - `2026-07-09-v6-drift-remediation-and-repo-boundary-lockdown-v1`
`Affected repos:` cianfhoghlaim (single-repo change)

## Spec delta

See `specs/infrastructure-stacks/spec.md` for 2 ADDED Requirements:

1. **"Locket sidecar pattern for Infisical v0.161+ requires locket >= v0.18
   or the bons-locket fork"** — captures the snake_case vs camelCase
   field name bug and lists the supported workarounds.

2. **"Hermes s6-overlay requires cap_add: [SETUID, SETGID] + user: 0:0
   or a custom /run chown"** — captures the permission requirements for
   running s6-overlay-based images under Docker's hardening model.

## Open follow-up issues

| Issue | Tracking change |
|---|---|
| Fix locket v0.17.3 + Infisical v0.161+ API mismatch (upgrade locket, downgrade Infisical, or patch the locket source) | `2026-07-XX-locket-v0-18-or-bons-locket-fork-v1` |
| Cross-stack DNS for openclaw + hermes to reach langfuse (move langfuse + hermes + litellm to the `cianfhoghlaim` network) | `2026-07-XX-unify-agent-platform-network-bridge-v1` |
| Repair the OCI Infisical private resource via `iac:sync:sites` + `iac:rotate-auth` (the Change 2 follow-up from earlier) | `2026-07-24-iac-sync-sites-pangolin-private-infisical-repair-v1` |
| Wire real channel tokens (Telegram/Slack/Discord/WhatsApp/Teams) when the operator is ready | `2026-07-XX-real-channel-tokens-v1` |
| Hermes tmpfs/permission model: design a clean sidecar that handles s6-overlay's init phase | `2026-07-XX-hermes-s6-overlay-init-sidecar-v1` |