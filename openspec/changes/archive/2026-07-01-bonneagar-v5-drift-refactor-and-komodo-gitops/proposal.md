# Change: 2026-07-01-bonneagar-v5-drift-refactor-and-komodo-gitops

## Why

After the 2026-06-28 v4 cianfhoghlaim consolidation and the
2026-06-29 `bonneagar-v4-canonical-and-stack-migration` +
`2026-06-29-bonneagar-iac-merge-komodo-pangolin-infisical`
changes, `bonneagar/` still has substantial residual drift
across 6 directories that actively breaks the GitOps loop:

1. **`pangolin/`** — 5 plaintext secrets committed to git
   (`api_key`, `secrets.env`, `secrets.env.resolved`,
   `config/infisical_secret`, `config/db/db.sqlite`); the
   duplicate `private-resources-fixed.blueprint.yaml`; the
   broken `multi-cloud-stack/multi-cloud-blueprint.yaml`
   (mixes YAML with WireGuard INI, has duplicate keys,
   wrong paths); 3 `op item create` 1Password CLI calls in
   `PANGOLIN-SETUP.md` + `olm-oracle/secrets.env`; legacy
   `mbp` + `aleyum.com` cert; 4 root blueprint files
   (`blueprint.yaml`, `a2a-resources.blueprint.yaml`,
   `olm-resources.blueprint.yaml`,
   `private-resources.blueprint.yaml`) that should move to
   per-stack `pangolin.yaml` files; `openapi.yaml`
   (132 KB), `tinyauth/users` (committed bcrypt), and 7
   stub `secrets/templates/*` files that are dead weight;
   `pangolin/olm.secrets.env` + `pangolin/newt.secrets.env`
   use broken `{{ infisical:///id }}` Jinja syntax (missing
   vault + path).

2. **`iac/`** — 5 critical path bugs that make `iac:plan`,
   `iac:sync:procedures`, `iac:sync:secrets`,
   `iac:sync:resource-syncs` non-functional
   (`"bonnegar"` typos in 4 files; wrong relative paths in
   2 files; the 2-vs-3-segment Infisical URI regex); the
   30-stack curated list contains 11 phantom names
   (`pocketid`, `tinyauth`, `traefik`, `locket`, `gerbil`,
   `duckdb`, `ducklake`, `letta`, `oideachais_*`); 4 of 8
   `iac:bootstrap` phases are `logWarn` stubs; auth.ts
   has 2 explicit TODOs + hardcoded `ciansedai` username;
   `diff.ts` is orphaned (complete but never imported).

3. **`komodo/`** — 84 procedures, 30 stack registrations,
   2 sites. ~50% of procedures contain `[[stack]]` blocks
   that should live in `stacks/` (structural drift); the
   `procedures/{macbook-analytics,macbook-media,
   oci-control-plane,oci-devtools}.toml` files are exact
   duplicates of `stacks/<same>.toml` (4 dead-weight
   files); the 1575-line `procedures/auto-deploy-stacks.toml`
   monolith has a duplicate `[[server]] arm1-oci` block
   referencing the legacy Frankfurt OCI region; the
   `sites/{macbook,oci}/` directory names + container_name
   strings use legacy host names; 11 of 14 DeployStack
   calls in `deploy-storage-stack.toml` reference
   non-existent stacks; `deploy-lakehouse-bunchloch.toml`
   DeployStacks `lakehouse-bunchloch` which doesn't exist;
   stack TOMLs reference non-existent paths
   (`infrastructure/stacks/<x>/`,
   `cianfhoghlaim/stacks/<x>/`, `croilar/`,
   `meaisínfhoghlaim/`); 9 procedures call phantom
   `RunAction` with action names that don't exist
   anywhere in `dagger/`; 5 dated backup directories +
   `Stats.gz` (1.5 MB) are dead weight (Backrest is the
   proper destination).

4. **`ansible/`** — The user's deep-dive confirmed that
   `ansible/` is functionally dead code that has never
   been deployed end-to-end:
   - `deploy-runbooks/ansible.md` line 127-132 admits
     *"no end-to-end provision executed"*
   - The 3 roles (`komodo_core`, `newt`, `pangolin_core`)
     have content (28 KB + 36 KB + 40 KB = 104 KB total)
     but it's broken Jinja that duplicates `stacks/komodo/`,
     `stacks/newt/`, `stacks/pangolin/`
   - 30+ bugs: hardcoded Mac paths, `arm1.oci` dot form
     (should be `arm1-oci` dash), wrong Locket tag
     (`:connect`), broken healthcheck YAML (semicolons
     instead of newlines), Jinja + bash brace expansion
     fragility, missing 5 of 8 env vars in `secrets.env`,
     1Password-migration leftover `op_connect_cianfhoghlaim`
     vault path
   - The IaC TypeScript subsystem at `iac/` explicitly
     replaces this whole Ansible mechanism
   - 5 different Locket images referenced across the
     codebase

5. **`stacks/`** — 17+ files reference `sruth/oideachais/...`
   build paths removed in v4 consolidation (will fail
   to build in clean checkouts); 2 stacks (`sunshine`,
   `drop`) still use the old 1Password `op://` URI pattern;
   6 directories without `compose.yaml` (`ci/`,
   `infisical/` (after filename fix), `motherduck/`,
   `planetscale/`, `pydantic-gateway/`, `tools/`);
   `stacks/olake/` + `stacks/nimtable/` are self-deprecated
   (explicit `DEPRECATED.md` saying "merged into lakehouse");
   `stacks/lakehouse-oci/` is a 1/6 GOLD_STANDARD stale
   duplicate of `stacks/lakehouse/` that contradicts the
   host topology; `stacks/r2/` is a competing S3 stack to
   `stacks/garage/`; ~46 of 82 stack `secrets.env` files
   use the non-canonical 3-segment `infisical:///<key>`
   URI form (should be canonical 2-segment
   `infisical://dev-baile/<svc>/<key>`).

6. **`dagger/`** — the TypeScript submodule at
   `ts_submodules/bonneagar/src/` (34 .ts files, 17.7k LOC)
   is preserved per the user's explicit decision ("we also
   use TS not Python only") but the `README.md` documents
   8 false claims (wrong engine version, wrong entry point,
   non-existent sub-package dirs, wrong file count). The
   Python `cianfhoghlaim_dagger/__init__.py` module is the
   canonical runtime but has an internal 5× Komodo-curl
   duplication opportunity.

The canonical `iac-merge` openspec change set out 4
blockers from `DEPLOYMENT-STRATEGY.md` that the IaC
would fix. **None of these blockers are actually fixed in
code.** The IaC has the right shape (3 clients + 3 models
+ 16 commands + a working diff engine) but only ~50% of
the commands are functional end-to-end.

The Locket sidecar image is the **community fork** at
https://github.com/bpbradley/locket (NOT a project-owned
image). All 100+ sidecar references use
`ghcr.io/bpbradley/locket:infisical` correctly. The 10+
fictional `ghcr.io/cianfhoghlaim/locket:*` references
(e.g. `:latest`, `:1.0.0`, `:1.2.3`) are drift that this
change corrects.

## User Decisions (locked in)

1. **Delete `pangolin/tenants/` entirely** — the multi-
   tenant abstraction is unnecessary for the single-tenant
   `cianfhoghlaim.ie` setup.
2. **Leave Hetzner references only in `pulumi/`** — no
   `cax41-hetzner` in inventory, ansible, iac.
3. **2-host topology only**: `arm1-oci` + `bunchloch`. No
   3rd host. No future-host commented entries.
4. **Clean break**: no v0 backward-compat aliases in
   `package.json`.
5. **PRUNE entire `ansible/` directory** — functionally
   dead code per `deploy-runbooks/ansible.md` line 127-132.
6. **Keep `dagger/ts_submodules/bonneagar/`** — preserved
   as documented TypeScript reference (user: "we also use
   TS not Python only"). The README will be rewritten to
   reflect actual reality, not deleted.
7. **Keep `stacks/browser/` and `stacks/croilar/` as-is** —
   no structural split (the multi-service browser stack and
   the nested croilar sub-stacks remain).
8. **Full Pangolin consolidation**: move 4 root blueprint
   files to `stacks/<name>/`; delete 9 dead files; slim
   `PANGOLIN-SETUP.md` from 15 KB → ~150 lines.
9. **Canonical Locket image**: `ghcr.io/bpbradley/locket:infisical`
   (the community fork at https://github.com/bpbradley/locket).

## What Changes

### Phase 0 — Security: Rotate Pangolin committed secrets (P0)

The 9 plaintext + regenerated-artifact files at `pangolin/`
must be rotated + added to `.gitignore`:

| File | Content | Action |
|:--|:--|:--|
| `pangolin/api_key` | Pangolin Integration API key | Rotate via Pocket ID OIDC; rewrite `iac/auth.ts:ensurePangolinAuth()` to use the Pocket ID flow (replaces the hardcoded API key path) |
| `pangolin/secrets.env` | 6 dev secrets | Add to `.gitignore`; rewrite as `infisical://dev-baile/...` URIs; delete the committed plaintext |
| `pangolin/secrets.env.resolved` | Duplicate of above | Delete |
| `pangolin/config/infisical_secret` | 40-char hex (Infisical machine identity) | Rotate; move to `.infisical.env` as `infisical://dev-baile/pangolin/machine_identity` |
| `pangolin/config/db/db.sqlite` | 266 KB Middleware Manager DB | Add to `.gitignore` (regenerated by Pangolin at runtime) |
| `pangolin/config/openapi.yaml` (132 KB) | Regenerated artifact | Add to `.gitignore` |
| `pangolin/config/tinyauth/users` (67 B) | bcrypt hash of admin user | Generate on first run; add to `.gitignore`; add `TINYAUTH_ADMIN_USER` + `TINYAUTH_ADMIN_PASSWORD` to `stacks/pangolin/.env.example` |
| `pangolin/config/secrets/templates/*` (7 files) | Stub files documenting what IaC should manage | Delete (superseded by `stacks/<name>/secrets.env`) |
| `pangolin/config/traefik/rules/{resource-overrides,tenant-routing}.yml` | Dead Traefik docs sample + multi-tenant routing for a non-existent portal service | Delete |

### Phase 0.5 — PRUNE entire `ansible/` directory (P0)

The user's deep-dive confirmed that `ansible/` is
functionally dead code. Action:

1. Inline the unique Docker pre-install check from
   `ansible/compose.yaml` lines 27-35 into
   `iac/commands/bootstrap.ts` Phase 0
2. Inline the SSH key authorization helper from
   `ansible/ee-builder/entrypoint.sh` lines 22-27 into the
   bootstrap state machine
3. Delete the entire `bonneagar/ansible/` directory (28
   KB + 36 KB + 40 KB + 112 lines of playbooks + 86 lines
   of inventory + ee-builder + compose + secrets + README
   + cfg)
4. Move `deploy-runbooks/ansible.md` to
   `archive/deploy-runbooks/ansible.md`
5. Update `AGENTS.md`: remove the "ansible/" row from the
   "Where things live" table
6. Update `QUADRANT-TO-STACK-MAP.md`: remove the "ansible"
   row from the cross-quadrant infrastructure table
7. Update `DEPLOYMENT-STRATEGY.md`: remove all Ansible
   references; update §1 topology to 2-host only
8. Confirm `pulumi/Pulumi.yaml` is the only file with
   `cax41-hetzner` references (per user decision: Hetzner
   is Pulumi-only)

### Phase 1 — IaC completion (P0)

| Bug | File | Fix |
|:--|:--|:--|
| `bonnegar` typo in `rootDir` default | `iac/sources/discover-stacks.ts:25` | Change to `"../../stacks"` (the right relative path from `iac/sources/` is `../../stacks`, NOT `../../bonnegar/stacks`) |
| `bonnegar` typo in runtime `join()` | `iac/commands/sync-procedures.ts:12` | Change to `"../../komodo/procedures"` |
| `bonnegar` typo in runtime `join()` | `iac/commands/sync-resource-syncs.ts:9,49` | Same fix |
| `discover-secrets.ts:41` regex (3 path segments required, actual is 2) | `iac/sources/discover-secrets.ts` | Change regex from `[^/]+/[^/]+/[^/]+/?$` to `[^/]+/[^/]+/?$` |
| `diff.ts` orphaned (never imported) | `iac/commands/plan.ts` | Import + call `deepDiff` + `redactSecrets` |
| 11 phantom key-stacks | `iac/sources/key-stacks.ts` | Replace `pocketid` → `pocket-id`, `tinyauth` → DELETE (no stack; it's a Pangolin bundle component), `traefik` → DELETE (same), `locket` → DELETE (it's a sidecar pattern, not a stack), `gerbil` → DELETE (Pangolin component), `duckdb` → DELETE (in-process, no stack), `ducklake` → DELETE (use `lakehouse` + `motherduck`), `letta` → DELETE (not deployed; referenced only in skill docs), `oideachais_dagster` → `oideachais-dagster` (sub-service of `oideachais/`), `oideachais-frontend` → `frontend` (the stack is `frontend/`), `oideachais-agent-os` → `agent-os`, `oideachais-adk-agents` → DELETE (sub-service of `oideachais/`) |
| `iac/auth.ts` 2 TODOs + hardcoded `ciansedai` | `iac/auth.ts` | (1) Add Pocket ID OIDC `client_credentials` flow → `ensurePangolinAuth()`; (2) Add `komodo-recover.sh` invocation → `ensureKomodoAuth()` fallback; (3) Move `ciansedai` to `CONFIG.komodoUsername` env var |
| `iac:bootstrap` 4 of 8 phases are `logWarn` stubs | `iac/commands/bootstrap.ts` | Implement the 8-phase state machine (see IaC spec delta) |
| `iac:teardown` is just `logWarn + exit(0)` | `iac/commands/teardown.ts` | Implement reverse of `iac:bootstrap` (requires `--force` flag) |
| `iac:sync:olm` is not idempotent | `iac/commands/sync-olm.ts` | Add `getOrCreateOlmClient()` (list → check `client.id` exists → create only if missing) |
| `iac:sync:procedures` parses only filename | `iac/commands/sync-procedures.ts` | Use `smol-toml` to parse; sync the full `[[procedure]]` block including `[[stage]]` + `[[stage.action]]` |
| `iac:sync:resource-syncs` hardcodes `repo: cliste/bonneagar` | `iac/commands/sync-resource-syncs.ts` | Read `CONFIG.gitRepo` + `CONFIG.gitProvider`; use `smol-toml` to parse the resource-sync file |
| `iac:sync:resources` hardcodes `"calcom"` | `iac/commands/sync-resources.ts:10` | Change to `"cal-diy"` |

### Phase 2 — Komodo GitOps: convert procedures to resource-syncs (P1)

Currently 84 procedures live as TOML files at
`komodo/procedures/*.toml` and are pushed via
`iac:sync:procedures`. This is NOT canonical GitOps —
each `iac:deploy` invocation is a state mutation, not a
sync. The canonical Komodo GitOps pattern is
**resource-syncs**: declare the resource (stack,
procedure, monitor, action-recipient, variable, schedule)
in TOML, register it with Komodo via `POST /sync`, and
let Komodo auto-pull from the repo on every commit.

The migration:

1. **Move procedures into 3 resource-syncs** — one per
   deploy surface:
   - `komodo/resource-syncs/arm1-oci.toml` — all
     procedures targeting `arm1-oci` (control plane +
     Pangolin + Komodo + Infisical + Locket + Backrest +
     observability + openclaw + openchamber)
   - `komodo/resource-syncs/bunchloch.toml` — all
     procedures targeting `bunchloch` (data plane +
     oideachais + litellm + langfuse + mlflow + dagster +
     lakehouse + cognee + lancedb + falkordb + graphiti +
     memgraph + hermes + openclaw + llm)
   - `komodo/resource-syncs/cross-cutting.toml` — cross-
     host procedures (the 4 prerequisites: pangolin-first,
     komodo-core, infisical-first, locket-deploy)
2. **Slim `iac/`** — remove `iac:sync:procedures` +
   `iac:sync:resource-syncs` from the `iac:deploy`
   command (now Komodo handles this). The IaC becomes
   the **orchestration layer** that ensures
   resource-syncs are configured + secrets are synced.
   `iac:health` adds a Komodo `listResourceSyncs()` check.
3. **Delete `procedures/auto-deploy-stacks.toml`** — the
   1575-line monolith is replaced by the 3 resource-syncs.

### Phase 4 — Pangolin full consolidation (P1)

Per the user's "Full consolidation" decision:

| Action | File |
|:--|:--|
| Move | `pangolin/blueprint.yaml` → `stacks/pangolin/blueprint.yaml` (trim to just `pangolin.cianfhoghlaim.ie`) |
| Move | `pangolin/a2a-resources.blueprint.yaml` entries → `stacks/agent-os/pangolin.yaml` + `blueprint.yaml` (drop the `a2a-internal` public resource) |
| Move | `pangolin/olm-resources.blueprint.yaml` → `stacks/olm-arm1-oci/{pangolin.yaml,blueprint.yaml}` (collapse the 2 `ssh-oracle` + `ssh-oci` entries to one) |
| Split | `pangolin/private-resources.blueprint.yaml` per-service into per-stack `pangolin.yaml` (mailcow gets the 3 missing routes); delete the master file |
| Move | `pangolin/olm-oracle/{compose,sidecar,secrets.env}` → `stacks/olm-arm1-oci/`; add the missing 3 files (`pangolin.yaml`, `blueprint.yaml`, `.env.example`); fix the unclosed-quote bug in `sidecar.yaml` line 29 |
| Move | `pangolin/olm.secrets.env`, `pangolin/newt.secrets.env` content → `stacks/olm-arm1-oci/secrets.env` + `stacks/pangolin/newt.secrets.env` (the existing canonical ones, using `infisical://dev-baile/pangolin/newt-arm1-oci/<key>` format) |
| Delete | `pangolin/tenants/` (entire dir per user) |
| Delete | `pangolin/private-resources-fixed.blueprint.yaml` (duplicate) |
| Delete | `pangolin/multi-cloud-stack/multi-cloud-blueprint.yaml` (broken YAML + WireGuard INI mix) |
| Rewrite | `pangolin/config/config.yml`: replace hardcoded `gerbil.base_endpoint: 132.145.27.89` with env-driven `${PANGOLIN_DOMAIN}`; narrow `gerbil.subnet_group: 10.0.0.0/8` to `10.100.0.0/16`; change `dns.nameservers` from `ns*.pangolin.net` to `1.1.1.1` + `8.8.8.8`; add `# IaC-managed` comments to `allow_raw_resources: true` + `enable_integration_api: true` |
| Update | `iac/commands/sync-olm.ts:12`: replace `cax41-hetzner-olm` (dead host) with `bunchloch-olm` |
| Rewrite | `pangolin/config/traefik/dynamic_config.yml` lakehouse routes (use bunchloch newt instead of SSH tunnels) |
| Slim | `PANGOLIN-SETUP.md` from 15 KB → ~150 lines (keep architecture diagram + Pocket ID flow + TLS + rate limits + troubleshooting; drop Quick Start + EE features + File Structure diagram + multi-cloud references) |
| Replace | `PANGOLIN-SETUP.md` + `pangolin/olm-oracle/secrets.env`'s 3 `op item create` 1Password CLI calls with `infisical secrets create` (per the 2026-06 1Password → Infisical migration) |
| Update | `PANGOLIN-SETUP.md` vault name `taisce-secrets` → `dev-baile` |

### Phase 5 — Stack consolidation (P2)

| Action | File |
|:--|:--|
| Delete | `stacks/lakehouse-oci/`, `stacks/r2/` (user-targeted) |
| Delete | `stacks/olake/`, `stacks/nimtable/` (self-deprecated per `DEPRECATED.md`) |
| Delete | `stacks/{ci,motherduck,planetscale,pydantic-gateway,tools}/` (no compose.yaml) |
| Rename | `stacks/infisical/docker-compose.yaml` → `compose.yaml`; `env.example` → `.env.example` |
| Rewrite | 17+ stale `sruth/` build paths in `stacks/{oideachais,agent-os,frontend,komodo,cognee,logfire,motherduck,pydantic-gateway}/...` |
| Rewrite | 4 remaining `op://` URIs in `stacks/sunshine/secrets.env` L9-10 and `stacks/drop/secrets.env` comment |
| Fix | duplicate `Z_AI_API_KEY` / `ZAI_API_KEY` in `stacks/litellm/secrets.env` L23-24 |
| Standardise | `arm1.oci` → `arm1-oci` (dash) in all 25+ affected stack files |
| Add | `stacks/lakehouse-bunchloch.toml` (or rename `komodo/procedures/deploy-lakehouse-bunchloch.toml`'s target) |
| **DO NOT** split | `stacks/browser/` (user decision: keep as monolithic 11-service compose) |
| **DO NOT** flatten | `stacks/croilar/` sub-stacks (user decision: keep nested structure) |

### Phase 6 — Komodo file structure cleanup (P1)

#### 6.1 — Original renames + duplicates

| Action | File |
|:--|:--|
| Delete | 4 exact-duplicate procedure files (`komodo/procedures/{macbook-analytics,macbook-media,oci-control-plane,oci-devtools}.toml`) |
| Rename | `komodo/procedures/deploy-macbook.toml` → `deploy-bunchloch.toml` |
| Rename | `komodo/stacks/macbook-analytics.toml` → `bunchloch-analytics.toml` |
| Rename | `komodo/stacks/macbook-media.toml` → `bunchloch-media.toml` |
| Update | `komodo/stacks/komodo.toml` `komodo-periphery-macbook` → `komodo-periphery-bunchloch` |
| Update | `komodo/stacks/storage-r2.toml` `r2-mounts-macbook` → `r2-mounts-bunchloch` (r2 is being deleted but the file may persist briefly) |
| Rename | `komodo/procedures/oci-control-plane.toml` → `arm1-oci-control-plane.toml` |
| Rename | `komodo/procedures/oci-devtools.toml` → `arm1-oci-devtools.toml` |
| Rename | `komodo/stacks/oci-control-plane.toml` → `arm1-oci-control-plane.toml` |
| Rename | `komodo/stacks/oci-devtools.toml` → `arm1-oci-devtools.toml` |
| Update | `komodo/stacks/pangolin-tunnels.toml` `newt-oci` → `newt-arm1-oci`, `olm-oci` → `olm-arm1-oci` |
| Rename | `komodo/sites/macbook/` → `komodo/sites/bunchloch/` (update container_name strings inside) |
| Rename | `komodo/sites/oci/` → `komodo/sites/arm1-oci/` |
| Delete | `komodo/procedures/langfuse.toml` (self-acknowledged legacy) |
| Fix | `komodo/resource-syncs/storage-infrastructure.toml` repo reference (`repo: "cliste/bonneagar"` → `repo: CONFIG.gitRepo`); remove non-existent `actions/*.toml` from resource_path list |

#### 6.7 — Delete 9 phantom Dagger-action procedures

These procedures call `RunAction` with action names that
**do not exist anywhere in the Dagger module** (verified
via grep across `bonneagar/dagger/`):

| File | Phantom actions called |
|:--|:--|
| `procedures/init-site.toml` | `validate-deployments`, `sync-dns-records`, `setup-pangolin-site`, `generate-ansible-inventory` |
| `procedures/sync-infrastructure.toml` | `sync-dns-records`, `sync-storage-configs`, `generate-ansible-inventory`, `validate-deployments` |
| `procedures/deploy-pangolin-full.toml` | `validate-deployments` + `deploy-pangolin-dagger` × 6 |
| `procedures/deploy-authenticated-stack.toml` | `deploy-auth-stack-dagger` × 4 |
| `procedures/deploy-periphery.toml` | `sync-ansible-files`, `run-ansible-playbook` (ansible/ is being deleted in Phase 0.5) |
| `procedures/health-check.toml` | `komodo-cli` (phantom CLI) × 60 |
| `procedures/staged-rollout.toml` | `komodo-cli` × 5 |
| `procedures/rollback.toml` | `komodo-cli deploy --version` + phantom `DuckLake snapshot` |
| `procedures/deploy-multi-cloud.toml` | `komodo-cli deploy` × 12 + references ghost stacks |

#### 6.8 — Delete 29 `[[stack]]`-only procedures

These are pure `[[stack]]` blocks that should live in
`stacks/` (structural drift): `agentos-api`,
`aleyum-music`, `aleyum-portal`, `browser`,
`codeolas-pipeline`, `crypteolas-pipeline`,
`crypteolas-ui`, `dagster-unified`, `drop`, `forgejo`,
`forgejo-runner`, `kapowarr`, `komodo`, `lakehouse-oci`,
`linkwarden`, `mlflow`, `observability`,
`pangolin-tunnels`, `paperless`, `pinchflat`, `romm`,
`sruth-pipelines`, `storage-lakehouse`, `storage-r2`,
`sunshine`, `team-stack-down`, `team-stack-up`,
`uirlisi-devtools`, `uirlisi-scraping`.

#### 6.9 — Delete 3 stale procedures

- `procedures/deploy-storage-stack.toml` (references
  non-existent stacks `graphiti`, `nimtable`,
  `mathesar`)
- `procedures/deploy-macbook.toml` (whole
  macbook-analytics cluster is being renamed)
- `procedures/deploy-cianfhoghlaim.toml` (calls ghost
  hosts `oci-databases`, `oci-devtools`)

#### 6.10 — Delete `komodo/backups/` (1.5 MB dead weight)

5 date-stamped Komodo backup directories +
`Stats.gz`. The canonical Komodo state lives in
`servers/servers.toml` + `stacks/*.toml` +
`procedures/*.toml` in this very repo (GitOps). The
2025-12 backups predate the v3 → v4 consolidation.
Backrest is the proper Restic destination for future
data backups.

#### 6.11 — Add 3 CI lint rules to `bun run validate-stacks`

- (a) `if grep -lE '^\[\[stack\]\]' komodo/procedures/*.toml;
  then echo "ERROR: procedures/*.toml must not contain
  [[stack]] blocks" + exit 1`
- (b) `if grep -rE '"host:(oci-databases|oci-devtools|
  macbook-media|macbook-analytics|cax41)" komodo/; then
  echo "ERROR: ghost host reference" + exit 1`
- (c) `if grep -rE 'op://' bonneagar/; then echo "ERROR:
  1Password URI found" + exit 1`

### Phase 8 — Doc sync (P2)

| File | Change |
|:--|:--|
| `bonneagar/AGENTS.md` | Replace 4 IaC entry points claim with the actual 15 (no v0 backward-compat aliases per the clean break); remove the ansible/ row; update 5-group model counts; add `hermes` to agent-platform group |
| `bonneagar/README.md` | Correct 88-vs-94 stack count; note the v5 refactor |
| `bonneagar/DEPLOYMENT-STRATEGY.md` | 2-host topology only (arm1-oci + bunchloch); mark all 4 known blockers fixed; update §3 to reference the 8-phase bootstrap |
| `bonneagar/GOLD_STANDARD.md` | Document the 4 blueprint schema variants in active use; update §3 Locket exemplar to `ghcr.io/bpbradley/locket:infisical` |
| `bonneagar/QUADRANT-TO-STACK-MAP.md` | Remove `tuatha/dagster_assets/definitions.py` ref; fix `komodo-periphery-macbook` → `komodo-periphery-bunchloch`; add 18 missing domain entries |
| `bonneagar/dagger/README.md` | Rewrite to reflect actual reality (engine v0.20.8; entry point `CianfhoghlaimDagger`; the TypeScript submodule IS used per user; cross-module composition exists; 34 .ts files not 31; sub-packages don't exist as dirs) |
| `bonneagar/dagger/ts_submodules/bonneagar/README.md` | Rewrite to reflect actual usage pattern (preserved per user decision) |
| `bonneagar/cli.py` | Fix 32 phantom stacks → 0; update stack count to 88 |

### Phase 9 — Locket image canonicalization (P2)

The canonical Locket image is
**`ghcr.io/bpbradley/locket:infisical`** (the community
fork at https://github.com/bpbradley/locket). All 100+
sidecar references use it correctly. The 10+ fictional
`ghcr.io/cianfhoghlaim/locket:*` references + 2 `:latest`
tags are drift.

#### 9.1 — Fix fictional `ghcr.io/cianfhoghlaim/locket:*` references

| File | Change |
|:--|:--|
| `bonneagar/GOLD_STANDARD.md` line 122 | `ghcr.io/cianfhoghlaim/locket:latest` → `ghcr.io/bpbradley/locket:infisical` |
| `bonneagar/stacks/frontend/sidecar.yaml` line 10 | same |
| `bonneagar/stacks/frontend/blueprint.yaml` line 12 | `run_docker_tag: ghcr.io/cianfhoghlaim/locket:latest` → `run_docker_tag: ghcr.io/bpbradley/locket:infisical` |
| `bonneagar/stacks/croilar/sidecar.yaml` line 17 | same |
| `bonneagar/stacks/ci/hf-watchdog/sidecar.yaml` line 13 | `ghcr.io/cianfhoghlaim/locket:1.2.3` → `ghcr.io/bpbradley/locket:infisical` |
| `bonneagar/stacks/lakehouse/README.md` line 92 | same |
| `bonneagar/stacks/oideachais/sidecar.yaml` line 32 | `ghcr.io/cianfhoghlaim/locket:1.2.3` → `ghcr.io/bpbradley/locket:infisical` |
| `bonneagar/stacks/oideachais/README.md` line 121 | update table row |

#### 9.2 — Fix wrong `:latest` and `:connect` tags

| File | Change |
|:--|:--|
| `bonneagar/stacks/drop/sidecar.yaml` line 12 | `ghcr.io/bpbradley/locket:latest` → `ghcr.io/bpbradley/locket:infisical` |
| `bonneagar/stacks/sunshine/sidecar.yaml` line 12 | same |
| `bonneagar/dagger/templates/sidecar.yaml.template` line 12 | Replace fake SHA `sha256:1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2` with `:infisical` |
| `bonneagar/ansible/roles/pangolin_core/defaults/main.yml` line 17 | `ghcr.io/bpbradley/locket:connect` → `ghcr.io/bpbradley/locket:infisical` (file deleted in Phase 0.5 anyway) |

#### 9.3 — Update GOLD_STANDARD.md §3

Replace the fictional exemplar with the community image.
Add note about future SHA pinning.

#### 9.4 — Update `.agents/skills/`

| File | Change |
|:--|:--|
| `.agents/skills/secrets-management/SKILL.md` lines 82, 121, 261 | `ghcr.io/cianfhoghlaim/locket:latest` → `ghcr.io/bpbradley/locket:infisical`; update Locket repo URL to https://github.com/bpbradley/locket |
| `.agents/skills/komodo/SKILL.md` line 398 | same |
| `.agents/skills_backup/kcg-locket-sidecar/SKILL.md` lines 39, 147 | same |
| `.agents/skills_backup/kcg-convergence/SKILL.md` line 189 | same |
| `.agents/skills_backup/kcg-infrastructure-audit/SKILL.md` line 161 | same |

#### 9.5 — Update spec references

| File | Change |
|:--|:--|
| `openspec/specs/infrastructure-stacks/spec.md` line 587 | `ghcr.io/cianfhoghlaim/locket:<sha-pinned-tag>` → `ghcr.io/bpbradley/locket:infisical` (with `@sha256:<digest>` once available) |
| `openspec/changes/oideachais-stack-polish/proposal.md` + `tasks.md` + `specs/oideachais-pipeline/spec.md` | already documents the drift; close it out in the next archive |
| `openspec/changes/archive/2026-06-24-infrastructure-stack-doctor-v1/specs/infrastructure-stacks/spec.md` line 126 | same correction (historical) |
| `openspec/research/2026-06-28-browserbase-program-2/live-docs/93-live-infisical-current.md` lines 232, 245 | OUT OF SCOPE per AGENTS.md ("never modify the 3 research files there; they're point-in-time artifacts") — flag as known drift |

#### 9.6 — CI lint enforcement

Add to `bun run validate-stacks`:

```bash
# 9.6.1: Only bpbradley/locket:infisical is allowed
if grep -rE 'ghcr\.io/(cianfhoghlaim/bpbradley)/locket:' bonneagar/stacks/ \
   | grep -v 'bpbradley/locket:infisical'; then
  echo "ERROR: only ghcr.io/bpbradley/locket:infisical is allowed in stack sidecars"
  exit 1
fi

# 9.6.2: No :latest, no @sha256: pinning (until digest is published)
if grep -rE 'locket:(@sha256:|latest)' bonneagar/stacks/; then
  echo "ERROR: Locket image must use :infisical tag only"
  exit 1
fi
```

### Phase 10 — Infisical URI normalization (P2)

Normalize the 46 `secrets.env` files that use the
3-segment `infisical:///<key>` form to the canonical
2-segment `infisical://dev-baile/<svc>/<key>` form. This
is a prerequisite for `iac:sync:secrets` to actually
discover all secrets (regex fix in Phase 1 is necessary
but not sufficient).

The change in `iac/sources/discover-secrets.ts:41` to
match 2-segment URIs enables discovery; this phase
makes the 43 stacks that use 3-segment URIs actually
discoverable.

### Phase 11 — Per-host topology formalization (P1)

The canonical 2-host topology is `arm1-oci` (control
plane) + `bunchloch` (data plane + dev). Per user
decision, **no 3rd host** is allowed anywhere.

1. Update `bonneagar/DEPLOYMENT-STRATEGY.md` §1 to the
   2-host topology (remove any 3-host tables from
   earlier drafts)
2. Confirm `pulumi/Pulumi.yaml` is the only file with
   `cax41-hetzner` references (Hetzner is Pulumi-only
   per user decision)
3. No `iac/config.ts` change needed (Phase 1.19
   removed `CAX41_HETZNER_IP`)

## Impact

### Affected specs (4 total)

- MODIFIED `infrastructure-stacks` — +7 Requirements
- MODIFIED `bonneagar-iac-merge` — +4 Requirements
  (incl. new "Hetzner Exclusion")
- NEW `bonneagar-komodo-gitops` — 3 Requirements
- MODIFIED `dagger-pipelines` — +2 Requirements
  (incl. new "TypeScript Submodule Preservation")

### New files

```
openspec/specs/bonneagar-komodo-gitops/spec.md
```

### Modified files

(very long list — refer to the phase breakdowns above)

### Deleted files (refined list)

**Pangolin (Phase 0):**
- `pangolin/api_key`
- `pangolin/secrets.env`, `pangolin/secrets.env.resolved`
- `pangolin/config/infisical_secret`
- `pangolin/config/db/db.sqlite`
- `pangolin/config/openapi.yaml`
- `pangolin/config/tinyauth/users`
- `pangolin/config/secrets/templates/*` (7 files)
- `pangolin/config/traefik/rules/{resource-overrides,tenant-routing}.yml`
- `pangolin/tenants/` (entire dir)
- `pangolin/private-resources-fixed.blueprint.yaml`
- `pangolin/multi-cloud-stack/` (entire dir)
- `pangolin/olm.secrets.env`, `pangolin/newt.secrets.env`
  (content moved to per-stack secrets.env)

**Pangolin (Phase 4): moved, not deleted**
- `pangolin/blueprint.yaml` → `stacks/pangolin/blueprint.yaml`
- `pangolin/a2a-resources.blueprint.yaml` → `stacks/agent-os/{pangolin.yaml,blueprint.yaml}`
- `pangolin/olm-resources.blueprint.yaml` → `stacks/olm-arm1-oci/{pangolin.yaml,blueprint.yaml}`
- `pangolin/private-resources.blueprint.yaml` → split per-service
- `pangolin/olm-oracle/` → `stacks/olm-arm1-oci/`

**Ansible (Phase 0.5 — ENTIRE DIRECTORY):**
- `bonneagar/ansible/` (entire dir)
- `bonneagar/deploy-runbooks/ansible.md` → `archive/deploy-runbooks/ansible.md`

**Komodo (Phase 6):**
- `komodo/procedures/{macbook-analytics,macbook-media,oci-control-plane,oci-devtools}.toml` (4 dups)
- `komodo/procedures/auto-deploy-stacks.toml` (1575-line monolith)
- `komodo/procedures/langfuse.toml`
- 29 `[[stack]]`-only procedures (full list in 6.8)
- 9 phantom Dagger procedures (full list in 6.7)
- 3 stale procedures (full list in 6.9)
- `komodo/backups/{2025-12-13..17,Stats.gz}`
- `komodo/sites/{macbook,oci}/` (renames)

**Stacks (Phase 5):**
- `stacks/lakehouse-oci/`, `stacks/r2/`, `stacks/olake/`,
  `stacks/nimtable/`, `stacks/ci/`, `stacks/motherduck/`,
  `stacks/planetscale/`, `stacks/pydantic-gateway/`,
  `stacks/tools/` (9 dirs)

### Hetzner handling

Per user decision: Hetzner (`cax41-hetzner`) is **only**
referenced in `bonneagar/pulumi/`. All references in:

- `bonneagar/iac/config.ts` (removed in Phase 1.19)
- `bonneagar/ansible/` (deleted in Phase 0.5)
- `bonneagar/DEPLOYMENT-STRATEGY.md` (updated in Phase 8)
- `bonneagar/AGENTS.md` (updated in Phase 8)
- `komodo/stacks/sruth-pipelines.toml` (deleted in Phase 6.8)
- `komodo/procedures/{agentos-api,codeolas-pipeline,crypteolas-pipeline,crypteolas-ui}.toml` (deleted in Phase 6.8)

### Affected CI

`openspec validate 2026-07-01-bonneagar-v5-drift-refactor-and-komodo-gitops --strict` MUST pass.

After implementation:
1. `bun run validate-stacks` MUST report exactly 88 stacks, each with the canonical 6/6 GOLD_STANDARD
2. `bun run iac:health` MUST return 0 (all 3 systems healthy)
3. `bun run iac:plan --dry-run` MUST show 0 unexpected diffs
4. `bun run iac:bootstrap` MUST complete all 8 phases
5. `grep -rE 'op://' bonneagar/` MUST return zero results
6. `grep -rE 'ghcr\.io/(cianfhoghlaim/bpbradley)/locket:' bonneagar/stacks/ | grep -v 'bpbradley/locket:infisical'` MUST return zero results
7. `grep -lE '^\[\[stack\]\]' komodo/procedures/*.toml` MUST return zero results
8. `grep -rE '"host:(oci-databases|oci-devtools|macbook-media|macbook-analytics|cax41)" komodo/` MUST return zero results
9. `git log -p --all -- pangolin/api_key` MUST return empty
10. The 5 ghost Pangolin secrets MUST be rotated; no plaintext in git history (verification via `git log -p --all -S`)
11. `ansible/` MUST NOT exist

## Non-Goals

- This change does NOT migrate the IaC `iac/commands/` from Bun to TypeScript standalone (the Bun runtime is the canonical toolchain).
- This change does NOT introduce the shared `kcg/base:latest` base image (a future change).
- This change does NOT split `bonneagar/` into a standalone GitHub repo (a future change after the IaC is fully functional).
- This change does NOT auto-discover Pangolin resources from `pangolin.yaml` (the per-stack `pangolin.yaml` is the canonical source).
- This change does NOT migrate the 3 bash scripts at `scripts/` to TypeScript (a future change after the IaC is fully functional).
- This change does NOT introduce a Python Locket SDK in addition to the sidecar (the community sidecar is canonical).
- This change does NOT migrate the 5 different Locket tags to `:latest` (the canonical tag is `:infisical`, pinned via `@sha256:` once bpbradley publishes digest-stable builds).
- This change does NOT delete the `dagger/ts_submodules/bonneagar/` TypeScript implementation (preserved per user decision: "we also use TS not Python only").
- This change does NOT split `stacks/browser/` or flatten `stacks/croilar/` (preserved per user decision).
- This change does NOT introduce the 3rd host `cax41-hetzner` anywhere outside Pulumi (per user decision).

## Risk Assessment

- **Risk: rotating the Pangolin API key breaks the IaC.** **Mitigation:** the new Pocket ID OIDC flow in `iac/auth.ts:ensurePangolinAuth()` is the replacement; the rotated key is the *new* Pocket ID `client_credentials` token. Both old and new auth paths work during the transition.
- **Risk: deleting `procedures/auto-deploy-stacks.toml` breaks the 9 procedures it contains.** **Mitigation:** the 9 procedures are migrated to the 3 new resource-syncs (one per host + cross-cutting) before the monolith is deleted.
- **Risk: deleting `ansible/` removes the only working Docker pre-install helper.** **Mitigation:** the helper is inlined into `iac/commands/bootstrap.ts` Phase 0 in Phase 0.5.1 (DOCKER pre-install is the first sub-step of Phase 0).
- **Risk: deleting the 6 stack dirs without `compose.yaml` breaks downstream tooling.** **Mitigation:** `iac/sources/discover-stacks.ts` already excludes them; no IaC code references them; the per-stack docs at `cianfhoghlaim/docs/stacks/` are preserved.
- **Risk: renaming `*-macbook` → `*-bunchloch` breaks Komodo resource references.** **Mitigation:** the rename is done in a single atomic commit; Komodo's resource-syncs auto-detect the rename and apply it.
- **Risk: implementing the 8-phase bootstrap introduces ordering bugs.** **Mitigation:** each phase is idempotent + re-runnable; `iac:health` reports phase state; `--force` flag allows manual recovery.
- **Risk: deleting `komodo/backups/` loses the only Komodo-native backup snapshot.** **Mitigation:** the 5 dated backups are 7+ months stale and predate the v3→v4 consolidation; the canonical state is in this repo (GitOps); future backups go to Backrest.

## Validation

1. `openspec validate 2026-07-01-bonneagar-v5-drift-refactor-and-komodo-gitops --strict` passes
2. `bun install` succeeds (the new `smol-toml` dep is added)
3. `bun run iac:health` returns 0 (Komodo + Pangolin + Infisical all healthy)
4. `bun run iac:plan --dry-run` shows the expected diff (88 stacks; 3 resource-syncs; 0 phantom key-stacks)
5. `bun run iac:bootstrap` completes all 8 phases end-to-end (Pulumi → Infisical → Pangolin → Komodo Core → Komodo Periphery → Newt → resource-syncs → all syncs)
6. `bun run iac:health` (post-deploy) confirms the 3 systems are consistent
7. `bun run validate-stacks` passes (88 stacks; no missing GOLD_STANDARD files; no `[[stack]]` blocks in procedures/; no ghost hosts; no `op://` URIs; only `ghcr.io/bpbradley/locket:infisical`)
8. The 9 ghost Pangolin secrets are rotated + no longer in `git log`
9. `ansible/` MUST NOT exist
10. `golangang.bad` shim: Stack counts: 88 stacks (was 88), 30 procedures (was 84, -64%), 0 komodo-cloned duplicates, 0 ghost hosts, 0 `op://` URIs, 0 fictional `cianfhoghlaim/locket` references
11. AGENTS.md + DEPLOYMENT-STRATEGY.md + GOLD_STANDARD.md + QUADRANT-TO-STACK-MAP.md + dagger/README.md match reality

## Estimated effort

- 11 phases + 4 spec deltas + 1 new capability spec
- ~250 P0/P1 items + ~50 P2 items
- ~7,000-10,000 LoC of TypeScript + ~50 markdown edits
- ~5-7 dev days for an experienced Bun + TypeScript + IaC engineer

## Cross-references

- `openspec/changes/2026-06-29-bonneagar-v4-canonical-and-stack-migration/` — the prior change this builds on
- `openspec/changes/2026-06-29-bonneagar-iac-merge-komodo-pangolin-infisical/` — the IaC merge change
- `openspec/specs/infrastructure-stacks/spec.md` — the existing 88-stack spec
- `openspec/specs/bonneagar-iac-merge/spec.md` — the existing IaC spec
- `openspec/specs/dagger-pipelines/spec.md` — the existing Dagger spec
- https://github.com/bpbradley/locket — the canonical Locket community fork
- `.agents/skills/secrets-management/SKILL.md` — the Infisical + Locket + mise 3-way contract
- `.agents/skills/infrastructure-stacks/SKILL.md` — the stack-ops skill
- `bonneagar/AGENTS.md` — the canonical bonneagar orientation doc
- `bonneagar/DEPLOYMENT-STRATEGY.md` — the bring-up playbook (this change replaces §3)
