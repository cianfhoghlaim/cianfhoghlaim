# Cianfhoghlaim Deployment Playbook

> **For:** Operators bringing up the platform from cold (new machine, OR forking the repo for a different jurisdiction) — the canonical 13-step recreation + 6-step confirmation + 4-blocker "if it doesn't work" recipe.
>
> **Companion docs:**
> - [`README.md §12`](../README.md#12--deployment--recreation-playbook) — the inline summary
> - [`README.md §11`](../README.md#11--data-engineering-pipelines--lakehouse) — the data-engineering context (what you're deploying)
> - [`../bonneagar/README.md`](../bonneagar/README.md) — the IaC mesh (the 6-step golden path)
> - [`../bonneagar/DEPLOYMENT-STRATEGY.md`](../bonneagar/DEPLOYMENT-STRATEGY.md) — the 2-host topology + the 8-phase bootstrap state machine
> - [`../AGENTS.md`](../AGENTS.md) — the canonical day-1 dev workflow
> - [`../docs/CHOP_AND_CHANGE_GUIDE.md`](./CHOP_AND_CHANGE_GUIDE.md) — the chop-and-change recipe for your own domain
>
> **Companion openspec change:** the `infrastructure-stacks` spec (the load-bearing constraint).

## §1 — The 13-step recreation recipe

Use this recipe when:
- You're a new operator with no existing platform
- You're forking cianfhoghlaim for a different jurisdiction (medical / legal / financial / etc.)
- You've lost your cluster and need to rebuild from cold

### Step 1 — Prerequisites

```
☐ 1.1  Apple Silicon Mac (M1 minimum, M4 Max recommended)
☐ 1.2  Oracle Cloud account (Always-Free tier; upgrade to Pay As You Go for 24 GB)
☐ 1.3  Cloudflare account (for DNS-01 wildcard cert at *.cianfhoghlaim.ie)
☐ 1.4  Pulumi account (for the 2-host topology bootstrap)
☐ 1.5  Hugging Face account (for the MODEL_REGISTRY live-check)
☐ 1.6  MiniMax Token Plan API key (Tier 3 of the provider chain)
```

### Step 2 — Clone + install

```bash
# 2.1 — Clone the monorepo
git clone https://github.com/cianfhoghlaim/cianfhoghlaim
cd cianfhoghlaim

# 2.2 — Install mise (the canonical task runner)
curl https://mise.jdx.dev/install.sh | sh
eval "$(~/.local/bin/mise activate bash)"

# 2.3 — Install mise-managed tools (bun + uv + dagger + pulumi + duckdb + opencode)
mise install

# 2.4 — Install TypeScript workspace deps
bun install

# 2.5 — Install Python sub-packages
uv sync
```

### Step 3 — Secrets bootstrap (the 3-way contract)

The secrets follow a strict 3-way contract:

1. **Source of truth** — `dev-baile` environment in the self-hosted Infisical vault
2. **Template** — `.infisical.env` (committed) — every value is an `infisical://dev-baile/...` reference
3. **Hydrated runtime** — `.env` (gitignored) — written by `mise` directory hooks from the template

```bash
# 3.1 — Create the dev-baile environment + folders in the Infisical vault
bun run scripts/create-env.ts

# 3.2 — Read .env + .infisical.env; create / update each vault secret
bun run scripts/init-vault.ts
# (alias for mise run secrets:init)

# 3.3 — Verify the secrets are hydrated
mise run validate-env
```

### Step 4 — IaC health check (the 6-way)

```bash
mise run iac:health
```

Expected: all 6 systems OK (Komodo + Pangolin + Infisical + Newt + Pocket ID + Tinyauth). If any FAIL, see §3 (the 4 known blockers).

### Step 5 — IaC plan (read-only diff)

```bash
mise run iac:plan
```

Walks the 4 discoverers (stacks + resources + secrets + key-stacks) and produces a per-system report. In `--dry-run` mode, only the filesystem discoverers run. **Use this as a CI gate** to catch drift before committing.

### Step 6 — Validate 88 stacks against 6-file GOLD_STANDARD

```bash
mise run cic:stack-doctor
# alias: bun run validate-stacks
```

Expected: **0 CRITICALS**. The audit walks `bonneagar/stacks/*/compose.yaml` and reports:

- **CRITICAL**: stacks missing `compose.yaml` or failing `docker compose config --quiet`
- **WARNING**: stacks missing one of the 6 GOLD_STANDARD files (sidecar / secrets / pangolin / blueprint / .env.example)
- **INFO**: stacks that pass all checks

### Step 7 — Bootstrap a new cluster (the 8-phase state machine)

```bash
mise run iac:bootstrap
```

The 8-phase bootstrap state machine:

1. **Pulumi** — provision cloud resources (Cloudflare + Hetzner + OCI)
2. **Infisical** — create the `dev-baile` environment + folders + 8 machine identities
3. **Pangolin** — wire the OIDC client + create the 3 hosts (`arm1-oci` + `bunchloch` + `cross-cutting`)
4. **Komodo** — register the Periphery agents
5. **Newt** — deploy the Pangolin client on each workload host
6. **All syncs** — register the 4 Komodo resource-syncs
7. **One-shot bootstrap** — run the 10 cross-cutting prerequisite procedures
8. **First sync** — wait for the resource-syncs to pull + verify each host's stack catalogue

The 3 of 10 phases that are still logWarn placeholders (Komodo Core + Periphery + Tinyauth deploy) are documented as **manual follow-ups** in the bootstrap output.

### Step 8 — Deploy the 13 stacks in dependency order

```bash
# The 13 stacks, in dependency order. Skipping a tier breaks downstream dependencies.

# Tier 1 — secrets
cd bonneagar/stacks/infisical && locket inject -- docker compose up -d && cd -

# Tier 2 — storage
cd bonneagar/stacks/motherduck && locket inject -- docker compose up -d && cd -
cd bonneagar/stacks/lakehouse && docker compose -f compose.yaml -f compose.dev.yaml up -d && cd -

# Tier 3 — LLM
cd bonneagar/stacks/litellm && locket inject -- docker compose up -d && cd -
cd bonneagar/stacks/unsloth-serve && docker compose up -d && cd -

# Tier 4 — observability
cd bonneagar/stacks/langfuse && locket inject -- docker compose up -d && cd -

# Tier 5 — browser
cd bonneagar/stacks/crawl4ai && locket inject -- docker compose up -d && cd -
cd bonneagar/stacks/stagehand && locket inject -- docker compose up -d && cd -

# Tier 6 — monitoring
cd bonneagar/stacks/changedetection && locket inject -- docker compose up -d && cd -

# Tier 7 — governance
cd bonneagar/stacks/komodo && locket inject -- docker compose up -d && cd -
cd bonneagar/stacks/pangolin && locket inject -- docker compose up -d && cd -
# (locket is automatic — no manual command; Locket sidecar hydrates secrets at container start)

# Tier 8 — UI
cd bonneagar/stacks/openchamber && locket inject -- docker compose up -d && cd -
```

### Step 9 — Materialise the lakehouse

```bash
# 9.1 — Launch the Dagster UI
mise run dagster:dev
# Expected: Dagster UI on http://localhost:3000

# 9.2 — Verify the assets loaded
uv run python -m orchestration.cli list-assets
# Expected: ~833 assets across the 5-layer architecture

# 9.3 — Materialise the canonical first asset
uv run python -m orchestration.cli materialise-leabharlann
# This kicks off the leabharlann corpus ingestion → DuckLake → LanceDB chain
```

### Step 10 — Run the 4 BIEP v1 Dives

```bash
# 10.1 — Verify the canonical 4 Dives are accessible
python -c "from motherduck import BIEP_DIVES; print([d.name for d in BIEP_DIVES])"
# Expected: ['lc_syllabus_topics', 'lc_exam_difficulty', 'lc_marking_complexity', 'gov_circulars_archive']

# 10.2 — Save all 4 Dives to the MotherDuck workspace
python -c "from motherduck import save_all; save_all()"
# Expected: 4

# 10.3 — Verify the 27 Flights are registered
python -c "from motherduck import run_flight; print(run_flight(name='test', cron='0 4 * * *', dry_run=True))"
```

### Step 11 — Run the canonical CI gate

```bash
mise run core:ci
# Runs: lint + test + openspec:validate-all + devops:validate-stacks
# Expected: all green
```

### Step 12 — Document any deviations

```
☐ 12.1  Add any new openspec change for deviations
☐ 12.2  Update the per-area AGENTS.md if the canonical surface changed
☐ 12.3  Update this playbook with the deviation recipe
```

### Step 13 — Push to remote (CI gate)

```bash
git pull --rebase
git push
git status  # MUST show "up to date with origin"
```

**Critical rule**: Work is NOT complete until `git push` succeeds. NEVER stop before pushing.

## §2 — The 6-step confirmation recipe (the "is it actually deployed?" check)

Use this recipe as a weekly health-check, OR after a fresh deploy, OR after any change to the IaC / Dagster / MotherDuck stack.

### Step 1 — IaC health

```bash
mise run iac:health
```

Expected: all 6 systems OK (Komodo + Pangolin + Infisical + Newt + Pocket ID + Tinyauth). If FAIL, see §3 (the 4 known blockers).

### Step 2 — Stack inventory

```bash
mise run devops:validate-stacks
```

Expected: **0 CRITICALS** across 88 stacks. If FAIL, check the 6-file GOLD_STANDARD for the failing stack.

### Step 3 — Dagster assets

```bash
mise run data:dagster:up
# Expected: Dagster UI on :3335 with ~833 assets loaded
# If FAIL: check orchestration/components/__init__.py (the registry surface)
```

### Step 4 — MotherDuck Dives

```bash
python -c "from motherduck import BIEP_DIVES; print([d.name for d in BIEP_DIVES])"
# Expected: 4 Dives (lc_syllabus_topics, lc_exam_difficulty, lc_marking_complexity, gov_circulars_archive)
# If FAIL: check motherduck/__init__.py (the canonical entrypoint)
```

### Step 5 — Model registry live-check

```bash
mise run ml:registry:audit
```

Expected: all 24 `VISION_MODELS` are live on Hugging Face Hub. If FAIL, check `meaisinfhoghlaim/models/registry.py` + `meaisinfhoghlaim/ci/hf_watchdog.py`.

### Step 6 — OpenSpec gate

```bash
mise run openspec:validate-all
```

Expected: 131 items pass (96 specs + 35 changes). If FAIL, check `openspec validate <change-id> --strict` for the failing item.

## §3 — The 4 known blockers (the "if it doesn't work" recipe)

Per `bonneagar/DEPLOYMENT-STRATEGY.md §4`. A deploy at the moment will hit these 4 known issues:

### Blocker 1 — Newt 1.12.5 + Pangolin server 1.18.4 incompatible

**Symptom:** `CLIENTS WILL NOT WORK ON THIS VERSION OF NEWT WITH THIS PANGOLIN SERVER`

**Fix:** Update Pangolin server to ≥1.13.0 OR downgrade newt to 1.11.x

```bash
# Check Pangolin server version
ssh oci.arm1 'docker exec pangolin -- pangolin --version'

# Check Newt client version
docker exec newt-bunchloch -- newt --version

# Upgrade Pangolin (preferred)
ssh oci.arm1 'cd /etc/komodo/storage/pangolin && docker compose pull && docker compose up -d'

# Or downgrade Newt (alternative)
docker pull fosrl/newt:1.11.5
```

### Blocker 2 — 3 manually-created private resources override the blueprints

**Symptom:** `Blueprint application failed: Site resource already exists with domain: <X>`

**Fix:** Open the Pangolin UI → Sites → each resource → delete the manual entry. Blueprint reapplies on the next newt cycle.

```bash
# Check which resources are manually-created
ssh oci.arm1 'sqlite3 /opt/pangolin/config/db/db.sqlite \
  "select siteId, name, niceId, online from sites;"'
```

### Blocker 3 — Both `PANGOLIN_API_KEY` and `PANGOLIN_API_KEY_0` in `.env` return 401

**Symptom:** 401 errors from Pangolin API

**Fix:** Use Pangolin UI to mint a fresh machine-identity token. Save to `.env` as `PANGOLIN_API_KEY`.

```bash
# Visit https://pangolin.cianchosaint.ie → API Keys → New Token
# Copy the token
echo "PANGOLIN_API_KEY=<new-token>" >> ~/.env
# Remove the duplicate
sed -i '/^PANGOLIN_API_KEY_0=/d' ~/.env
```

### Blocker 4 — `komodo-locket` sidecar fails with `${INFISICAL_CLIENT_ID}` parse error

**Symptom:** `error: invalid value '${INFISICAL_CLIENT_ID}'` (the Locket sidecar can't parse the YAML escape)

**Fix:** Switch to single-dollar Compose substitution; add `--infisical-default-environment` + `--infisical-default-project-id` flags; provision an Infisical machine identity with `/komodo` access

```bash
# Edit bonneagar/stacks/komodo/compose.yaml
# Change $${INFISICAL_CLIENT_ID} → ${INFISICAL_CLIENT_ID}
# Add the --infisical-default-environment + --infisical-default-project-id flags

# Provision the Infisical machine identity
bun run scripts/init-vault.ts
```

## §4 — The chop-and-change recipe (for your own jurisdiction)

Per [`CHOP_AND_CHANGE_GUIDE.md`](./CHOP_AND_CHANGE_GUIDE.md). 5 steps:

1. **Copy the gold-standard exemplars verbatim, delete everything else.** Keep `garage/`, `litellm/`, `pangolin/`, `lakehouse/` (the 4 reference impls per `GOLD_STANDARD.md §Exemplars`); delete `oideachais/`, `croilar/`, `tuatha/`, `meaisinfhoghlaim/`, `openclaw/`, `openchamber/`, `hermes/` (personal fleet); `motherduck/` (SaaS stub); `olm-arm1-oci/`; `wave2/`; the 5 `unstract` sidecar placeholders; `legacy/`.

2. **Replace the domain + two hostnames in one `sed` pass** — `cianfhoghlaim.ie` (in ~50 files), `arm1-oci` (in `servers.toml` + ~109 stack TOMLs), `bunchloch` (workload host). Run `rg 'cianfhoghlaim\.ie|arm1-oci|bunchloch' -l` first.

3. **Swap the 9 hard-coded env vars in `setup-iac-env.sh` + `.env`** — `DOMAIN`, `CF_DNS_API_TOKEN`, `PANGOLIN_API_KEY`, `POCKETID_*_CLIENT_ID/SECRET` (3 pairs), `CROWDSEC_BOUNCER_KEY`, `PANGOLIN_LICENCE` (Enterprise — remove if going FOSS-only), `INFISICAL_UNIVERSAL_AUTH_*` + `INFISICAL_PROJECT_ID`.

4. **Swap any one of the 6 backends** — Komodo → Coolify/Portainer/Dokku; Pangolin → Cloudflare Tunnel + Cloudflare Access (note the Enterprise licence); Pocket ID → Authelia/Authentik/Keycloak; Infisical → Doppler/Vault; Traefik → Caddy/Nginx Proxy Manager; Garage → MinIO.

5. **Replace `iac/pulumi/oci/`** with whatever cloud you actually use (`iac/pulumi/oci/Pulumi.prod.yaml:5` hard-codes `arm1-oci`). Delete `iac/pulumi/oci/` + `iac/pulumi/hetzner/` and write a new `iac/pulumi/<your-cloud>/index.ts`.

## §5 — The 4 cheap coding agents (the canonical day-1 dev setup)

Per [`CHOP_AND_CHANGE_GUIDE.md §0.1`](./CHOP_AND_CHANGE_GUIDE.md):

| Tool | Cost | Best for | Weak at | Recommendation |
|---|---|---|---|---|
| **Gemini Deep Research Pro** | €20/mo | First-hour research: finding authoritative ministry / exam-board / medical-register endpoints | Multi-file repo refactors | Use for the first hour |
| **MiniMax coding plan** | $10-30/mo | Repetitive file-local Python refactors; BAML schema edits; IaC rewrites | Web research; autonomous browsing | Use for IaC + BAML work |
| **OpenCode Go** (local CLI) | €0/mo | Multi-file repo edits with the in-stack `ccc` skill + the `agent-fleet-orchestration` skill | Pure research; needs skill ramp-up | Use as your default — already wired |
| **GitHub Copilot** | €10/mo | Single-file edits, IDE-anchored completion | Cross-cutting refactors | Single-file copilot only |

**Pair them**: Gemini Deep Research for the first hour → OpenCode Go or MiniMax for the next two days → GitHub Copilot as a single-file copilot.

## §6 — Cross-references

| If you want to ... | Open this file |
|---|---|
| Run the day-1 dev workflow | [`../AGENTS.md`](../AGENTS.md) |
| Find a specific openspec change | [`../openspec/AGENTS.md`](../openspec/AGENTS.md) |
| Understand the data engineering layer | [`../README.md §11`](../README.md#11--data-engineering-pipelines--lakehouse) |
| Understand the deployment mesh | [`../README.md §12`](../README.md#12--deployment--recreation-playbook) |
| Understand the IaC mesh | [`../bonneagar/README.md`](../bonneagar/README.md) |
| Understand the 2-host topology + bootstrap | [`../bonneagar/DEPLOYMENT-STRATEGY.md`](../bonneagar/DEPLOYMENT-STRATEGY.md) |
| Chop-and-change for your own domain | [`./CHOP_AND_CHANGE_GUIDE.md`](./CHOP_AND_CHANGE_GUIDE.md) |
| Run a Dagster asset | [`../orchestration/AGENTS.md`](../orchestration/AGENTS.md) |
| Add a new BAML extraction | [`../baml_src/AGENTS.md`](../baml_src/AGENTS.md) |
| Add a new CocoIndex flow | [`../cocoindex_flows/AGENTS.md`](../cocoindex_flows/AGENTS.md) |
| Add a new DLT source | [`../dlt_sources/AGENTS.md`](../dlt_sources/AGENTS.md) |
| Use the MODEL_REGISTRY | [`../meaisinfhoghlaim/models/model_registry.py`](../meaisinfhoghlaim/models/model_registry.py) |
| Run a MotherDuck Dive | [`../motherduck/README.md`](../motherduck/README.md) |

---

> **Final note**: This playbook is designed for **replication** by departments that may not have deep infrastructure expertise. Every step can be done DOMESTICALLY on your own machine with the self-hosted Docker bundle. The 13-step recreation recipe + the 6-step confirmation recipe + the 4-blocker "if it doesn't work" recipe together give you everything you need to bring up + verify + recover the platform.
