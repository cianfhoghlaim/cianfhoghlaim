# Tasks: 2026-07-01-bonneagar-v5-drift-refactor-and-komodo-gitops

## Phase 0 — Security: Rotate Pangolin committed secrets (P0)

- [ ] 0.1 Add the 9 Pangolin files (`pangolin/api_key`,
      `pangolin/secrets.env`, `pangolin/secrets.env.resolved`,
      `pangolin/config/infisical_secret`, `pangolin/config/db/
      db.sqlite`, `pangolin/config/openapi.yaml`,
      `pangolin/config/tinyauth/users`, `pangolin/config/secrets/
      templates/*`, `pangolin/config/traefik/rules/*`) to
      `bonneagar/.gitignore`
- [ ] 0.2 Mint new Pocket ID OIDC `client_credentials` via
      `pangolin.cianfhoghlaim.ie/admin/api-clients`; save to
      `.infisical.env` as `infisical://dev-baile/pangolin/
      pocket_id_client_id` + `.../pocket_id_client_secret`
- [ ] 0.3 Mint new Infisical machine identity for Pangolin via
      `iac/commands/bootstrap.ts` Phase 2; save to
      `.infisical.env`
- [ ] 0.4 Rewrite `iac/auth.ts:ensurePangolinAuth()` to use the
      Pocket ID OIDC flow (replace the hardcoded API key path)
- [ ] 0.5 Rewrite `pangolin/secrets.env` as `infisical://dev-baile/...
      ` URIs; delete the committed plaintext
- [ ] 0.6 Delete the other 8 files (api_key, secrets.env.resolved,
      infisical_secret, db.sqlite, openapi.yaml, tinyauth/users,
      secrets/templates/*, traefik/rules/*)
- [ ] 0.7 Verify all 9 paths are now `git ls-files`-excluded
- [ ] 0.8 Mint new Tinyauth admin user; commit the bcrypt hash
      path to `.gitignore`; document the bootstrap flow
      (generate admin on first run) in `stacks/pangolin/
      .env.example`

## Phase 0.5 — PRUNE entire `ansible/` directory (P0)

- [ ] 0.5.1 Inline the unique Docker pre-install check from
      `ansible/compose.yaml` lines 27-35 into
      `iac/commands/bootstrap.ts` Phase 0 (sub-step:
      "verify Docker is installed on target host")
- [ ] 0.5.2 Inline the SSH key authorization helper from
      `ansible/ee-builder/entrypoint.sh` lines 22-27 into the
      bootstrap state machine
- [ ] 0.5.3 Delete the entire `bonneagar/ansible/` directory (28
      KB + 36 KB + 40 KB + 112 lines of playbooks + 86 lines of
      inventory + ee-builder + compose + secrets + README + cfg)
- [ ] 0.5.4 Move `deploy-runbooks/ansible.md` to
      `archive/deploy-runbooks/ansible.md`
- [ ] 0.5.5 Update `AGENTS.md`: remove the "ansible/" row from
      the "Where things live" table
- [ ] 0.5.6 Update `QUADRANT-TO-STACK-MAP.md`: remove the
      "ansible" row from the cross-quadrant infrastructure table
- [ ] 0.5.7 Update `DEPLOYMENT-STRATEGY.md`: remove all Ansible
      references; update §1 topology to 2-host only
- [ ] 0.5.8 Confirm `pulumi/Pulumi.yaml` + `pulumi/Pulumi.dev.yaml`
      are the only files with `cax41-hetzner` references (per
      user decision: Hetzner is Pulumi-only)
- [ ] 0.5.9 Verify `iac:bootstrap` Phase 0 covers what
      `ansible/compose.yaml` lines 27-35 used to do (Docker pre-
      install check)

## Phase 1 — IaC completion (P0)

- [ ] 1.1 Add `smol-toml` dependency to `bonneagar/package.json`
- [ ] 1.2 Fix `iac/sources/discover-stacks.ts:25` — change
      `"../../bonnegar/stacks"` → `"../../stacks"`
- [ ] 1.3 Fix `iac/commands/sync-procedures.ts:12` — change
      `"../../../bonnegar/komodo/procedures"` →
      `"../../komodo/procedures"`
- [ ] 1.4 Fix `iac/commands/sync-resource-syncs.ts:9,49` —
      same path fix
- [ ] 1.5 Fix `iac/sources/discover-secrets.ts:41` — change
      the 3-segment regex to 2-segment
- [ ] 1.6 Fix `iac/commands/sync-resources.ts:10` — change
      `"calcom"` → `"cal-diy"`
- [ ] 1.7 Fix `iac/commands/sync-resource-syncs.ts:47` —
      change `repo: "cliste/bonneagar"` →
      `repo: CONFIG.gitRepo`
- [ ] 1.8 Wire `iac/diff.ts` into `iac/commands/plan.ts`
      (import + call `deepDiff` + `redactSecrets`)
- [ ] 1.9 Clean up `iac/sources/key-stacks.ts` — replace the
      11 phantom names (see proposal §Phase 1 for the full list)
- [ ] 1.10 Resolve `iac/sources/key-stacks.ts` internal
      inconsistency (letta missing from array; `mlx-omni`
      duplicated)
- [ ] 1.11 Implement `iac/auth.ts:ensurePangolinAuth()`
      Pocket ID OIDC `client_credentials` flow
- [ ] 1.12 Implement `iac/auth.ts:ensureKomodoAuth()`
      `komodo-recover.sh` fallback (docker exec into
      komodo-ferretdb to reset the password)
- [ ] 1.13 Replace hardcoded `ciansedai` in
      `iac/auth.ts:17` with `CONFIG.komodoUsername` env var
- [ ] 1.14 Implement the 8-phase `iac/commands/bootstrap.ts`
      state machine (see IaC spec delta)
- [x] 1.15 Implement `iac/commands/teardown.ts` (reverse of
      `iac:bootstrap`; requires `--force`) — implemented in
      pick-5b (commit b4deb8722); 8-step reverse, --force + --dry-run
      supported
- [ ] 1.16 Add idempotent `getOrCreateOlmClient()` to
      `iac/commands/sync-olm.ts`
- [ ] 1.17 Use `smol-toml` in
      `iac/commands/sync-procedures.ts`
- [ ] 1.18 Use `smol-toml` + `CONFIG.gitRepo`/`gitProvider`
      in `iac/commands/sync-resource-syncs.ts`
- [ ] 1.19 Remove the Hetzner `CAX41_HETZNER_IP` env var from
      `iac/config.ts` (per user decision: 2-host only)
- [ ] 1.20 Update `iac/README.md` to reflect the cleanups
- [ ] 1.21 Verify `iac:bootstrap` Phase 0 (Docker pre-install)
      covers what `ansible/compose.yaml` lines 27-35 used to do
- [ ] 1.22 Verify NO v0 backward-compat aliases in
      `bonneagar/package.json` (clean break per user decision)

## Phase 2 — Komodo GitOps (P1)

- [ ] 2.1 Create `komodo/resource-syncs/arm1-oci.toml`
      (control plane: pangolin + komodo + infisical + locket +
      backrest + observability + openclaw + openchamber)
- [ ] 2.2 Create `komodo/resource-syncs/bunchloch.toml`
      (data plane: oideachais + litellm + langfuse + mlflow +
      dagster + lakehouse + cognee + lancedb + falkordb +
      graphiti + memgraph + hermes + llm)
- [ ] 2.3 Create `komodo/resource-syncs/cross-cutting.toml`
      (the 4 prerequisites: pangolin-first, komodo-core,
      infisical-first, locket-deploy)
- [ ] 2.4 Remove `iac:sync:procedures` +
      `iac:sync:resource-syncs` from `iac/commands/deploy.ts`
      (now Komodo handles this)
- [ ] 2.5 Add Komodo `listResourceSyncs()` check to
      `iac:health`
- [ ] 2.6 Delete `komodo/procedures/auto-deploy-stacks.toml`
      (replaced by the 3 resource-syncs)
- [ ] 2.7 Verify `iac:bootstrap` Phase 7 ("all sync
      commands") now only includes secrets + resources +
      monitors + alerts + variables + schedules +
      action-recipients + olm

## Phase 4 — Pangolin full consolidation (P1)

- [ ] 4.1 Move `pangolin/blueprint.yaml` →
      `stacks/pangolin/blueprint.yaml` (trim to just
      `pangolin.cianfhoghlaim.ie`)
- [ ] 4.2 Move `pangolin/a2a-resources.blueprint.yaml`
      entries → `stacks/agent-os/pangolin.yaml` +
      `blueprint.yaml` (drop the `a2a-internal` public
      resource)
- [ ] 4.3 Move `pangolin/olm-resources.blueprint.yaml` →
      `stacks/olm-arm1-oci/{pangolin.yaml,blueprint.yaml}`
      (collapse the 2 `ssh-oracle` + `ssh-oci` entries to one)
- [ ] 4.4 Split `pangolin/private-resources.blueprint.yaml`
      per-service into per-stack `pangolin.yaml` (mailcow
      gets the 3 missing routes); delete the master file
- [ ] 4.5 Move `pangolin/olm-oracle/{compose,sidecar,
      secrets.env}` → `stacks/olm-arm1-oci/`; add the missing
      3 files (`pangolin.yaml`, `blueprint.yaml`,
      `.env.example`); fix the unclosed-quote bug in
      `sidecar.yaml` line 29
- [ ] 4.6 Move `pangolin/olm.secrets.env`,
      `pangolin/newt.secrets.env` content → per-stack
      `secrets.env` files (replace the broken `{{ infisical:///id }}`
      Jinja syntax with proper `infisical://dev-baile/...`
      URIs)
- [ ] 4.7 Delete `pangolin/tenants/` (entire dir per user)
- [ ] 4.8 Delete `pangolin/private-resources-fixed.blueprint.yaml`
- [ ] 4.9 Delete `pangolin/multi-cloud-stack/`
- [ ] 4.10 Rewrite `pangolin/config/config.yml`:
      - Replace hardcoded `gerbil.base_endpoint: 132.145.27.89`
        with env-driven `${PANGOLIN_DOMAIN}`
      - Narrow `gerbil.subnet_group: 10.0.0.0/8` to
        `10.100.0.0/16`
      - Change `dns.nameservers` from `ns*.pangolin.net` to
        `1.1.1.1` + `8.8.8.8`
      - Add `# IaC-managed` comments to `allow_raw_resources: true`
        + `enable_integration_api: true`
      - Drop `dashboard_session_length_hours: 720` to `168`
- [ ] 4.11 Update `iac/commands/sync-olm.ts:12`: replace
      `cax41-hetzner-olm` (dead host) with `bunchloch-olm`
- [ ] 4.12 Rewrite `pangolin/config/traefik/dynamic_config.yml`
      lakehouse routes (use bunchloch newt instead of SSH
      tunnels; remove the SSH-tunnel workaround comment)
- [ ] 4.13 Slim `PANGOLIN-SETUP.md` from 15 KB → ~150 lines
      (keep architecture diagram + Pocket ID flow + TLS +
      rate limits + troubleshooting; drop Quick Start + EE
      features + File Structure diagram + multi-cloud
      references)
- [ ] 4.14 Replace 3 `op item create` 1Password CLI calls with
      `infisical secrets create` in `PANGOLIN-SETUP.md`
      (L99-101, L132-133, L196-197)
- [ ] 4.15 Update vault name `taisce-secrets` → `dev-baile` in
      `PANGOLIN-SETUP.md` L309-316

## Phase 5 — Stack consolidation (P2)

- [ ] 5.1 Delete `stacks/lakehouse-oci/` (stale duplicate)
- [ ] 5.2 Delete `stacks/r2/` (competing S3 stack)
- [ ] 5.3 Delete `stacks/olake/` + `stacks/nimtable/`
      (self-deprecated per their `DEPRECATED.md`)
- [ ] 5.4 Delete `stacks/{ci,motherduck,planetscale,
      pydantic-gateway,tools}/` (no `compose.yaml`)
- [ ] 5.5 Rename `stacks/infisical/docker-compose.yaml` →
      `compose.yaml`; `env.example` → `.env.example`
- [ ] 5.6 Rewrite 17+ stale `sruth/` build paths in
      `stacks/{oideachais,agent-os,frontend,komodo,cognee,
      logfire,motherduck,pydantic-gateway}/...`
- [ ] 5.7 Rewrite 4 remaining `op://` URIs in
      `stacks/sunshine/secrets.env` L9-10 and
      `stacks/drop/secrets.env` comment
- [ ] 5.8 Fix duplicate `Z_AI_API_KEY` / `ZAI_API_KEY` in
      `stacks/litellm/secrets.env` L23-24
- [ ] 5.9 Standardise `arm1.oci` → `arm1-oci` (dash) in all
      25+ affected stack files
- [ ] 5.10 Add `stacks/lakehouse-bunchloch.toml` (or rename
      `komodo/procedures/deploy-lakehouse-bunchloch.toml`'s
      target)
- [ ] 5.11 **DO NOT** split `stacks/browser/` (user decision)
- [ ] 5.12 **DO NOT** flatten `stacks/croilar/` sub-stacks
      (user decision)

## Phase 6 — Komodo file structure cleanup (P1)

### 6.1 — Original renames + duplicates

- [ ] 6.1.1 Delete 4 exact-duplicate procedure files
      (`procedures/{macbook-analytics,macbook-media,
      oci-control-plane,oci-devtools}.toml`)
- [ ] 6.1.2 Rename `procedures/deploy-macbook.toml` →
      `deploy-bunchloch.toml`
- [ ] 6.1.3 Rename `stacks/macbook-analytics.toml` →
      `bunchloch-analytics.toml`
- [ ] 6.1.4 Rename `stacks/macbook-media.toml` →
      `bunchloch-media.toml`
- [ ] 6.1.5 Update `stacks/komodo.toml`
      `komodo-periphery-macbook` → `komodo-periphery-bunchloch`
- [ ] 6.1.6 Update `stacks/storage-r2.toml`
      `r2-mounts-macbook` → `r2-mounts-bunchloch`
- [ ] 6.1.7 Rename `procedures/oci-control-plane.toml` →
      `arm1-oci-control-plane.toml`
- [ ] 6.1.8 Rename `procedures/oci-devtools.toml` →
      `arm1-oci-devtools.toml`
- [ ] 6.1.9 Rename `stacks/oci-control-plane.toml` →
      `arm1-oci-control-plane.toml`
- [ ] 6.1.10 Rename `stacks/oci-devtools.toml` →
      `arm1-oci-devtools.toml`
- [ ] 6.1.11 Update `stacks/pangolin-tunnels.toml`
      `newt-oci` → `newt-arm1-oci`,
      `olm-oci` → `olm-arm1-oci`
- [ ] 6.1.12 Rename `sites/macbook/` → `sites/bunchloch/`
- [ ] 6.1.13 Rename `sites/oci/` → `sites/arm1-oci/`
- [ ] 6.1.14 Delete `komodo/procedures/langfuse.toml`
- [ ] 6.1.15 Fix
      `komodo/resource-syncs/storage-infrastructure.toml`
      repo reference; remove non-existent `actions/*.toml`
      from resource_path list

### 6.7 — Delete 9 phantom Dagger-action procedures

- [ ] 6.7.1 Delete `procedures/init-site.toml`
- [ ] 6.7.2 Delete `procedures/sync-infrastructure.toml`
- [ ] 6.7.3 Delete `procedures/deploy-pangolin-full.toml`
- [ ] 6.7.4 Delete
      `procedures/deploy-authenticated-stack.toml`
- [ ] 6.7.5 Delete `procedures/deploy-periphery.toml`
- [ ] 6.7.6 Delete `procedures/health-check.toml`
- [ ] 6.7.7 Delete `procedures/staged-rollout.toml`
- [ ] 6.7.8 Delete `procedures/rollback.toml`
- [ ] 6.7.9 Delete `procedures/deploy-multi-cloud.toml`

### 6.8 — Delete 29 `[[stack]]`-only procedures

- [ ] 6.8.1 Delete `procedures/{agentos-api,aleyum-music,
      aleyum-portal,browser,codeolas-pipeline,
      crypteolas-pipeline,crypteolas-ui,dagster-unified,
      drop,forgejo,forgejo-runner,kapowarr,komodo,
      lakehouse-oci,linkwarden,mlflow,observability,
      pangolin-tunnels,paperless,pinchflat,romm,
      sruth-pipelines,storage-lakehouse,storage-r2,
      sunshine,team-stack-down,team-stack-up,
      uirlisi-devtools,uirlisi-scraping}.toml`

### 6.9 — Delete 3 stale procedures

- [ ] 6.9.1 Delete `procedures/deploy-storage-stack.toml`
- [ ] 6.9.2 Delete `procedures/deploy-macbook.toml`
- [ ] 6.9.3 Delete `procedures/deploy-cianfhoghlaim.toml`

### 6.10 — Delete `komodo/backups/` (1.5 MB)

- [ ] 6.10.1 Delete `komodo/backups/{2025-12-13_08-15-14,
      2025-12-14_01-00-01,2025-12-15_01-00-42,
      2025-12-16_01-00-01,2025-12-17_01-00-01,Stats.gz}`
- [ ] 6.10.2 Add `/bonneagar/komodo/backups/` to
      `.gitignore`
- [ ] 6.10.3 Configure Komodo to push future backups to
      `backrest` (the canonical destination)

### 6.11 — Add 3 CI lint rules to `bun run validate-stacks`

- [ ] 6.11.1 Lint: `if grep -lE '^\[\[stack\]\]'
      komodo/procedures/*.toml; then echo ERROR + exit 1`
- [ ] 6.11.2 Lint: `if grep -rE '"host:(oci-databases|
      oci-devtools|macbook-media|macbook-analytics|
      cax41)" komodo/; then echo ERROR + exit 1`
- [ ] 6.11.3 Lint: `if grep -rE 'op://' bonneagar/; then
      echo ERROR + exit 1`

## Phase 8 — Doc sync (P2)

- [ ] 8.1 Update `bonneagar/AGENTS.md`: remove the 4 IaC
      entry-points claim (no v0 aliases per clean break);
      remove the ansible/ row; update 5-group model counts;
      add `hermes` to agent-platform group
- [ ] 8.2 Update `bonneagar/README.md`: correct 88-vs-94
      stack count; note the v5 refactor
- [ ] 8.3 Update `bonneagar/DEPLOYMENT-STRATEGY.md`:
      2-host topology only (arm1-oci + bunchloch); mark all 4
      known blockers fixed; update §3 to reference the 8-phase
      bootstrap
- [ ] 8.4 Update `bonneagar/GOLD_STANDARD.md`: document the
      4 blueprint schema variants in active use; update §3
      Locket exemplar
- [ ] 8.5 Update `bonneagar/QUADRANT-TO-STACK-MAP.md`:
      remove `tuatha/dagster_assets/definitions.py` ref;
      fix `komodo-periphery-macbook` →
      `komodo-periphery-bunchloch`; add 18 missing domain
      entries
- [ ] 8.6 Rewrite `bonneagar/dagger/README.md`: reflect
      actual reality (engine v0.20.8; entry point
      `CianfhoghlaimDagger`; TypeScript submodule IS used per
      user; cross-module composition exists; 34 .ts files
      not 31; sub-packages don't exist as dirs)
- [ ] 8.7 Rewrite
      `bonneagar/dagger/ts_submodules/bonneagar/README.md`:
      reflect actual usage pattern (preserved per user
      decision)
- [ ] 8.8 Fix `bonneagar/cli.py`: 32 phantom stacks → 0;
      update stack count to 88
- [ ] 8.9 Update `openspec/project.md`: add the
      `bonneagar-komodo-gitops` capability row

## Phase 9 — Locket image canonicalization (P2)

### 9.1 — Fix fictional `ghcr.io/cianfhoghlaim/locket:*` refs

- [ ] 9.1.1 `bonneagar/GOLD_STANDARD.md` line 122 —
      `ghcr.io/cianfhoghlaim/locket:latest` →
      `ghcr.io/bpbradley/locket:infisical`
- [ ] 9.1.2 `bonneagar/stacks/frontend/sidecar.yaml`
      line 10 — same
- [ ] 9.1.3 `bonneagar/stacks/frontend/blueprint.yaml`
      line 12 — `run_docker_tag: ghcr.io/cianfhoghlaim/
      locket:latest` → `run_docker_tag: ghcr.io/bpbradley/
      locket:infisical`
- [ ] 9.1.4 `bonneagar/stacks/croilar/sidecar.yaml`
      line 17 — same
- [ ] 9.1.5 `bonneagar/stacks/ci/hf-watchdog/sidecar.yaml`
      line 13 — `ghcr.io/cianfhoghlaim/locket:1.2.3` →
      `ghcr.io/bpbradley/locket:infisical`
- [ ] 9.1.6 `bonneagar/stacks/lakehouse/README.md`
      line 92 — same
- [ ] 9.1.7 `bonneagar/stacks/oideachais/sidecar.yaml`
      line 32 — `ghcr.io/cianfhoghlaim/locket:1.2.3` →
      `ghcr.io/bpbradley/locket:infisical`
- [ ] 9.1.8 `bonneagar/stacks/oideachais/README.md`
      line 121 — update table row

### 9.2 — Fix wrong `:latest` and `:connect` tags

- [ ] 9.2.1 `bonneagar/stacks/drop/sidecar.yaml` line 12 —
      `ghcr.io/bpbradley/locket:latest` →
      `ghcr.io/bpbradley/locket:infisical`
- [ ] 9.2.2 `bonneagar/stacks/sunshine/sidecar.yaml`
      line 12 — same
- [ ] 9.2.3 `bonneagar/dagger/templates/sidecar.yaml.template`
      line 12 — Replace fake SHA
      `sha256:1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5
      d6e7f8a9b0c1d2` with `:infisical`
- [ ] 9.2.4 `bonneagar/ansible/roles/pangolin_core/defaults/main.yml`
      line 17 — `ghcr.io/bpbradley/locket:connect` →
      `ghcr.io/bpbradley/locket:infisical` (file deleted in
      Phase 0.5; verify post-deletion)

### 9.3 — Update GOLD_STANDARD.md §3

- [ ] 9.3.1 Replace the fictional `ghcr.io/cianfhoghlaim/
      locket:latest` exemplar with `ghcr.io/bpbradley/locket:
      infisical`
- [ ] 9.3.2 Add note: stacks SHOULD pin to `:infisical` tag;
      production SHOULD add `@sha256:<digest>` once
      bpbradley/locket publishes digest-stable builds
- [ ] 9.3.3 Add reference: https://github.com/bpbradley/locket

### 9.4 — Update `.agents/skills/`

- [ ] 9.4.1 `.agents/skills/secrets-management/SKILL.md`
      lines 82, 121, 261 — change fictional refs; update
      Locket repo URL to https://github.com/bpbradley/locket
- [ ] 9.4.2 `.agents/skills/komodo/SKILL.md` line 398 —
      same
- [ ] 9.4.3 `.agents/skills_backup/kcg-locket-sidecar/SKILL.md`
      lines 39, 147 — same
- [ ] 9.4.4 `.agents/skills_backup/kcg-convergence/SKILL.md`
      line 189 — same
- [ ] 9.4.5 `.agents/skills_backup/kcg-infrastructure-audit/SKILL.md`
      line 161 — same

### 9.5 — Update spec references

- [ ] 9.5.1
      `openspec/specs/infrastructure-stacks/spec.md` line 587
      — update the "Locket sidecar image" requirement
- [ ] 9.5.2
      `openspec/changes/oideachais-stack-polish/proposal.md`
      + `tasks.md` + `specs/oideachais-pipeline/spec.md` —
      already documents the drift; close it out in the next
      archive
- [ ] 9.5.3
      `openspec/changes/archive/2026-06-24-infrastructure-stack-doctor-v1/specs/
      infrastructure-stacks/spec.md` line 126 — same
      correction (historical; update if visible)
- [ ] 9.5.4 Skip `openspec/research/2026-06-28-browserbase-program-2/
      live-docs/93-live-infisical-current.md` (out of scope
      per AGENTS.md "never modify the 3 research files there";
      flag as known drift)

### 9.6 — CI lint enforcement

- [ ] 9.6.1 Add to `bun run validate-stacks`:
      ```bash
      if grep -rE 'ghcr\.io/(cianfhoghlaim/bpbradley)/locket:' \
         bonneagar/stacks/ | grep -v 'bpbradley/locket:infisical'; then
        echo "ERROR: only ghcr.io/bpbradley/locket:infisical is allowed"
        exit 1
      fi
      ```
- [ ] 9.6.2 Add to `bun run validate-stacks`:
      ```bash
      if grep -rE 'locket:(@sha256:|latest)' bonneagar/stacks/; then
        echo "ERROR: Locket image must use :infisical tag only"
        exit 1
      fi
      ```

## Phase 10 — Infisical URI normalization (P2)

- [ ] 10.1 Sweep all `secrets.env` files: replace 3-segment
      `infisical:///<key>` form with canonical 2-segment
      `infisical://dev-baile/<svc>/<key>` form
- [ ] 10.2 Target the ~43 files identified by the audit
      (after Phase 5 stack deletions reduce the count from 46
      to ~43)
- [ ] 10.3 Verify `iac:sync:secrets` discovers all secrets
      after the sweep

## Phase 11 — Per-host topology formalization (P1)

- [ ] 11.1 Update `DEPLOYMENT-STRATEGY.md` §1 to the 2-host
      topology only
- [ ] 11.2 Confirm `pulumi/Pulumi.yaml` is the only file with
      `cax41-hetzner` references (per user decision: Hetzner
      is Pulumi-only)
- [ ] 11.3 No `iac/config.ts` change needed (Phase 1.19
      removed `CAX41_HETZNER_IP`)

## Implementation Order

1. **Phase 0** (security) — 30 min
2. **Phase 0.5** (ansible prune) — 1 hour
3. **Phase 1** (IaC completion) — 2 dev days
4. **Phase 2** (Komodo resource-syncs) — 1 dev day
5. **Phase 4** (Pangolin consolidation) — 4 hours
6. **Phase 5** (stack consolidation) — 4 hours
7. **Phase 6** (komodo structure cleanup) — 4 hours
8. **Phase 9** (Locket image sweep) — 1 hour
9. **Phase 10** (Infisical URI normalization) — 4 hours
10. **Phase 8** (doc sync) — 4 hours
11. **Phase 11** (topology formalization) — 1 hour

**Total: ~5-7 dev days for an experienced engineer.**

After Phase 6, re-run `openspec validate --strict` to
confirm no spec drift.
After Phase 11, archive the change:
`openspec archive 2026-07-01-bonneagar-v5-drift-refactor-and-komodo-gitops --yes`
