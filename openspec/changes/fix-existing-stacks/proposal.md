# Fix Existing Stacks — Audit + Remediation

## Why

The cianfhoghlaim monorepo has 70+ Docker Compose stacks under `infrastructure/stacks/*/*/` and the post-`monorepo-restructure-v2` audit surfaced concrete gaps. Many stacks don't follow the 5-file GOLD_STANDARD, several have broken path references after the v2 restructure, and the Locket/Infisical secret-management pattern is inconsistently applied. End-to-end deployment of the **oideachais data platform** (Dagster + agent-os + browser + coder + crawl4ai) is currently broken because the agent-os and browser stacks reference the deleted `sruth/*` paths.

## What Changes

### Stack upgrades to 5-file GOLD_STANDARD

| Stack | Change |
|:--|:--|
| `storage/dagster` | Renamed `secrets.env.template` → `secrets.env`. Added `sidecar.yaml`. Rewrote `pangolin.yaml` + `blueprint.yaml` to the modern 6-label pattern. Added `deploy.resources.limits` to both services. Added `.env.example`. |
| `storage/kafka` | Added `sidecar.yaml` (Locket). Populated `secrets.env` with 3 `{{ infisical:///kafka/* }}` refs. Modernised `pangolin.yaml` (TCP mode for the broker, HTTP for the UI). Added `kafka-init` one-shot container that creates the 5 topics from `oideachais/data_platform/kafka.py`. |
| `storage/confluent` | Added `sidecar.yaml`. Populated `secrets.env` with 9 `{{ infisical:///confluent/* }}` refs. Added `.env.example`. |
| `storage/agent-os` | Rewrote `compose.yaml` to fix 4 broken `context: ../../../sruth/*` build paths → `oideachais/data_platform/agent_os/`, `tuatha/crypteolas/agent_os/`, `infrastructure/browser/agent_os/`. Added `sidecar.yaml`. Modernised `pangolin.yaml` (4 separate private resources). Aleyum's build is stubbed until the aleyum/ source is restored. |
| `storage/browser` | Rewrote `compose.yaml` to fix 3 broken `context: ../../../sruth/browser*` build paths. Added `sidecar.yaml`. Populated `secrets.env` with 3 refs. |
| `storage/lancedb` | Added healthcheck + `deploy.resources.limits` + switched to `cianfhoghlaim` shared network. |
| `tools/stirling-pdf` | Added `sidecar.yaml`. Populated `secrets.env`. |

### New monitoring stack

| Stack | Path | Purpose |
|:--|:--|:--|
| `infrastructure/monitoring` | `infrastructure/stacks/monitoring/` | Prometheus + Grafana + Loki + Promtail + Alertmanager. Scrapes 15+ containers. Private Pangolin resources at `grafana.cianfhoghlaim.ie`, `prometheus.cianfhoghlaim.ie`, `alerts.cianfhoghlaim.ie`. |

### New tooling

| Path | Purpose |
|:--|:--|
| `scripts/stack-doctor.sh` | Bash 3.2-compatible auditor. Reports CRITICAL / WARNING / INFO. Supports `--json` for CI. |
| `.agents/skills/stack-ops/SKILL.md` | 60-line skill teaching agents how to add/fix/audit stacks. |
| `infrastructure/komodo/procedures/stack-health-snapshot.toml` | Nightly `stack-doctor` + uploads to `s3://stack-snapshots/`. |

### Turbo + package.json

- Added `validate-stacks` and `doctor` tasks to `turbo.json`
- Added `validate-stacks` and `doctor:stacks` scripts to root `package.json`

### Infisical items seeded in `dev-baile/`

- `dagster/`: `ducklake_postgres_password`, `garage_access_key`, `garage_secret_key` (3 items)
- `kafka/`: `sasl_user`, `sasl_password`, `cluster_id` (3 items)
- `confluent/`: 9 items (bootstrap_servers, api_key, api_secret, schema_registry_url, sr_api_key, sr_api_secret, ksqldb_url, ksqldb_api_key, ksqldb_api_secret)
- `agent-os/`: 6 items (agent_os_secret_key, x402_pay_to_address, oideachais_db_url, crypteolas_db_url, browser_db_url, aleyum_db_url)
- `browser/`: 3 items (skyvern_db_password, garage_rpc_secret, garage_admin_token)
- `monitoring/`: 1 item (grafana_admin_password)
- `stirling-pdf/`: 2 items (api_key, postgres_password)
- **Total: 27 new Infisical items**

## Impact

- `stack-doctor` now reports **3 CRITICAL, 14 WARNING, 40 INFO** (was: pre-audit baseline of 7+ missing-sidecar stacks and 12+ empty-secrets.env stacks)
- The **oideachais pipeline can now deploy** (agent-os + browser + dagster + kafka all build against real source paths)
- A central **monitoring stack** exists for the first time
- A new `validate-stacks` turbo task can run in CI

## Out of scope (follow-up issues to file)

- Pin `:latest` image tags in the ~30 stacks still using them (P4)
- Add `deploy.resources.limits` to the ~30 stacks still missing them (P4)
- Add `healthcheck:` blocks to the remaining 14 stacks flagged by stack-doctor (P3)
- Populate the remaining 9 empty `secrets.env` files (P3 partial)
- Delete `storage/motherduck`, `storage/planetscale`, `storage/logfire`, `storage/pydantic-gateway` placeholders (or rebuild — flagged in OpenSpec)
- Deploy `beszel-agent` systemd unit on `arm1-oci` and `cax41-hetzner` (P5.2)
- Restore `aleyum/` source and re-enable the `aleyum-agentos` build (P1.2 partial)
- Add Pocket ID OIDC SSO wiring to n8n, Vikunja, cal-diy (out of scope from team-workflow-stack)
- Build + push the `ghcr.io/cianfhoghlaim/n8n-init` and `vikunja-seed` images (out of scope from team-workflow-stack)
- Migrate the litellm-sidecar prometheus.yml to scrape the new monitoring stack
