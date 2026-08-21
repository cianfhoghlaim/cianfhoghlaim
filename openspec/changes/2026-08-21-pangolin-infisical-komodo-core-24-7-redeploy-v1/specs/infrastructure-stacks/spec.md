## MODIFIED Requirements

### Requirement: Three-Tier Host Convergence

The system SHALL deploy the KCG platform across a
**3-tier host convergence model** rather than a single host
or a 2-tier model:

| Tier | Host | Role | Key stacks |
|:--|:--|:--|:--|
| **Control plane** | `arm1-oci` (Oracle Cloud ARM free tier) | Komodo (GitOps) + Pangolin (zero-trust) + Pocket ID (OIDC) + CrowdSec (WAF) | Komodo :9120, Pangolin :3001, Gerbil :51820/udp, Pocket ID :1411 |
| **Storage** | `cax41-hetzner` (Hetzner Cloud ARM) | Garage (S3) + Lakekeeper (Iceberg REST) + Postgres (catalog) + LakeFS (data versioning) | Garage :3900-3904, Lakekeeper :8181, Lance Namespace :8182, Postgres :5433 |
| **Workload** | `bunchloch` (MacBook M4 Max, 48GB) | Dagster (orchestration) + LiteLLM (LLM gateway) + CocoIndex (embedding) + the 70+ model backends (GGUF/MLX/safetensors) | Dagster :3335, LiteLLM :4000, llama-swap :8080, mlx-omni-server :10240, invokeai :9090 |
| **Core 24/7 subset (arm1-oci only)** | `arm1-oci` (the 12 services that MUST remain up 24/7) | 4 stacks with full 6-file GOLD_STANDARD coverage + 2 services bundled inside `pangolin/compose.yaml` + 6 services managed via the `komodo` resource-sync | pangolin + infisical + komodo + forgejo + (bundled) tinyauth + pocket-id + (resource-sync-managed) garage + middleware-manager + backrest + beszel + dozzle + crowdsec |

The 3 tiers are wired by **Pangolin WireGuard tunnels**
(arm1-oci Gerbil :51820/udp) and **Locket sidecars** that
inject Infisical secrets into every container (no plaintext
on disk).

#### Scenario: A Dagster asset on bunchloch reads from arm1-oci Pangolin

- **GIVEN** a Dagster asset on `bunchloch` is materialising
- **WHEN** it calls a service that is only exposed on the
  `arm1-oci` Pangolin proxy
- **THEN** the WireGuard tunnel (via Newt) routes the call
  through Pangolin
- **AND** Pocket ID OIDC validates the JWT
- **AND** the response returns within the standard RTT
  budget for the cluster

#### Scenario: A new Cognee dataset lands on the storage tier

- **GIVEN** a Dagster asset on `bunchloch` runs
  `cognee.cognify()`
- **WHEN** the cognify call writes to the knowledge graph
- **THEN** the data is persisted on the `cax41-hetzner`
  storage tier (Lakekeeper Iceberg REST + Lance Namespace)
- **AND** the metadata is registered in Postgres
- **AND** the next reader (on `bunchloch` or `arm1-oci`)
  reads the Iceberg table via the Lakekeeper REST API

#### Scenario: A non-core stack is tagged for arm1-oci

- **GIVEN** a developer adds a new stack at `bonneagar/stacks/<new>/`
- **AND** the stack requires > 4 GB RAM OR any GPU dependency
  (CUDA / Metal / ROCm)
- **WHEN** the Komodo resource-syncs poll the new TOML
- **THEN** the stack SHALL be assigned `host:bunchloch` (NOT
  `host:arm1-oci`) in the Komodo stack TOML
- **AND** the `stack-doctor` `oci-arm-compat` check SHALL fail
  if the stack is assigned to `host:arm1-oci`

### Requirement: Locket Sidecar Contract

The system SHALL enforce the canonical Locket sidecar template
across all 94 stacks. The contract is:

- `image:` MUST be ONE OF:
  - `ghcr.io/cianfhoghlaim/locket-shim:infisical-0.2.1` (or
    any newer `0.2.x`) — the in-house shim, known-good against
    Infisical v0.161+
  - `ghcr.io/bpbradley/locket:v0.18.0` (or any newer `v0.18.x`
    or `v1.x.x`) — the upstream image, only once it ships
    stable (NOT `v0.18.0-rc.1` / `v0.18.0-rc.2`; pre-releases
    are forbidden per the Image Pinning Policy)
  - `image: ghcr.io/bpbradley/locket:infisical` (the upstream
    `:latest` alias pointing at the BROKEN `v0.17.3`) is
    **forbidden** and SHALL fail the Locket migration gate
- `user: "65532:65532"` (nobody:nogroup)
- `security_opt: ["no-new-privileges:true"]`
- `cap_drop: ["ALL"]`
- `read_only: true`
- `tmpfs: [/run/secrets/locket:size=1m,mode=0700,uid=65532,gid=65532]`
- `volumes: [cianfhoghlaim_locket_secrets:/run/secrets/locket:ro]`
- `environment.LOCKET_MODE`: one of `watch` / `exec` / `oneshot`
- `environment.LOCKET_SECRETS_FILE: /run/secrets/locket/secrets.env`

The `cianfhoghlaim_locket_secrets` external tmpfs volume is
defined in `bonneagar/stacks/pangolin/sidecar.yaml` (or the
canonical shared sidecar compose) and is **shared** across all
94 stacks.

#### Scenario: A Locket sidecar uses the broken upstream `:infisical` alias

- **GIVEN** a developer's `sidecar.yaml` declares
  `image: ghcr.io/bpbradley/locket:infisical`
- **WHEN** the Locket migration gate runs (via
  `mise run cic-stack-doctor`)
- **THEN** the gate SHALL fail with exit code 64
  (`locket-image-broken-upstream`)
- **AND** the developer MUST change to
  `image: ghcr.io/cianfhoghlaim/locket-shim:infisical-0.2.1`
  (or the upstream `v0.18.0` once stable)

#### Scenario: A Locket sidecar uses the in-house shim

- **GIVEN** `bonneagar/stacks/<stack>/sidecar.yaml`
- **WHEN** the stack is deployed
- **THEN** the Locket container SHALL have `user: 65532:65532` +
  `no-new-privileges: true` + `cap_drop: [ALL]` + `read_only: true`
  + `tmpfs: [/run/secrets/locket:size=1m,mode=0700]`
- **AND** the `cianfhoghlaim_locket_secrets` external tmpfs volume
  SHALL be mounted

## ADDED Requirements

### Requirement: Core 24/7 stack subset on arm1-oci

The system SHALL keep exactly 12 services running on
`arm1-oci` (Oracle Cloud ARM free tier, 4 OCPU / 24 GB RAM) for
24/7 availability. The 12 services are:

| Service | Source | Component type |
|:--|:--|:--|
| pangolin | `bonneagar/stacks/pangolin/compose.yaml` (6-file GOLD_STANDARD; the `blueprint.yaml` is the 1 file added by this change) | Stack with full 6-file coverage |
| infisical | `bonneagar/stacks/infisical/compose.yaml` (6-file GOLD_STANDARD) | Stack with full 6-file coverage |
| komodo | `bonneagar/stacks/komodo/compose.yaml` (6-file GOLD_STANDARD) | Stack with full 6-file coverage |
| forgejo | `bonneagar/stacks/forgejo/compose.yaml` (6-file GOLD_STANDARD) | Stack with full 6-file coverage |
| tinyauth | bundled inside `pangolin/compose.yaml` | Sub-component |
| pocket-id | bundled inside `pangolin/compose.yaml` | Sub-component |
| garage | managed via `bonneagar/komodo/resource-syncs/arm1-oci.toml` | Resource-sync-managed |
| middleware-manager | managed via `bonneagar/komodo/resource-syncs/arm1-oci.toml` | Resource-sync-managed |
| backrest | managed via `bonneagar/komodo/resource-syncs/arm1-oci.toml` | Resource-sync-managed |
| beszel | managed via `bonneagar/komodo/resource-syncs/arm1-oci.toml` | Resource-sync-managed |
| dozzle | managed via `bonneagar/komodo/resource-syncs/arm1-oci.toml` | Resource-sync-managed |
| crowdsec | managed via `bonneagar/komodo/resource-syncs/arm1-oci.toml` | Resource-sync-managed |

The total RAM footprint of the 12 services SHALL be ≤ 6 GB
(~25% of the 24 GB OCI free tier). Every other stack SHALL
be torn down unless explicitly opted in via a `tier:core-24-7`
Komodo tag or a `host:arm1-oci` tag in the stack TOML.

#### Scenario: An operator tears down a non-core stack on arm1-oci

- **GIVEN** the operator runs
  `mise run iac:teardown-stack --host=arm1-oci
  --keep=pangolin,infisical,komodo,forgejo,tinyauth,pocket-id,backrest,beszel,dozzle,crowdsec,headplane,headscale,middleware-manager,garage`
- **WHEN** the command completes
- **THEN** exactly 12 containers SHALL remain on `arm1-oci`
  (one per core service)
- **AND** all other containers SHALL be `docker compose down`ed
- **AND** `mise run iac-health` SHALL report all 6 systems
  green (Komodo + Pangolin + Infisical + Newt + Pocket ID + Tinyauth)
- **AND** `bash bonneagar/audit/scripts/probe-public-urls.sh`
  SHALL return 0 for all 12 core URLs

#### Scenario: A new GPU stack is added

- **GIVEN** a developer adds a new GPU-dependent stack (e.g.
  vllm, invokeai, llama-swap) at `bonneagar/stacks/<new>/`
- **AND** the stack's Komodo TOML is tagged `host:arm1-oci`
- **WHEN** the resource-sync polls the new TOML
- **THEN** the `stack-doctor` `oci-arm-compat` check SHALL
  fail with exit code 128
- **AND** the developer MUST change the tag to
  `host:bunchloch` before the PR can merge

#### Scenario: A core stack is missing a GOLD_STANDARD file

- **GIVEN** the 4 core stacks (pangolin + infisical + komodo + forgejo)
  MUST each have the 6-file GOLD_STANDARD
- **WHEN** `mise run cic-stack-doctor` runs
- **THEN** any missing file SHALL fail the File gate (exit code 1)
- **AND** the developer MUST add the missing file before the
  PR can merge (this change adds the missing
  `bonneagar/stacks/pangolin/blueprint.yaml`)

### Requirement: Env-var fallback pattern (OCI source-of-truth + intermittent sync)

The system SHALL use the **OCI Infisical** as the single source of
truth for all `infisical://dev-baile/...` URIs across the 94
stacks. The local fallback SHALL be a flat `.env` file
(hydrated by the canonical `mise run secrets:env` mise task +
the new `secrets_env_refresh` Dagster asset), NOT a second
Infisical instance.

The pattern is:

1. `.infisical.env` (committed to the repo, the source-of-truth
   template) contains every `{{ infisical://dev-baile/... }}`
   reference
2. `mise run secrets:env` (the existing task, documented in
   `SECRETS-MANAGEMENT.md`) hydrates the `.env` file on
   directory entry via mise directory hooks
3. The new Dagster asset `secrets_env_refresh` (in the
   `secrets` group of `4_asset_generation`) re-runs
   `infisical export --in-file .infisical.env --out-file .env`
   on a 15-minute schedule + on every `iac:sync:secrets` invocation
4. Every Locket sidecar's `INFISICAL_URL` points at
   `https://infisical.cianfhoghlaim.ie` (the OCI URL) by default
5. Every Locket sidecar's `LOCKET_FALLBACK_FILE` points at
   `/run/secrets/locket/env-fallback.env` (the hydrated `.env`
   file, mounted read-only) for offline scenarios when the
   OCI vault is unreachable
6. The local Infisical containers (`infisical-backend` +
   `infisical-db` + `infisical-redis`) on `bunchloch` SHALL be
   torn down (per the env-var fallback decision)

The drift window between OCI and the local `.env` mirror is
bounded to ~15 min (the `secrets_env_refresh` schedule).

#### Scenario: A developer runs the dev environment offline

- **GIVEN** the developer is on `bunchloch` with no network to
  `infisical.cianfhoghlaim.ie`
- **AND** `mise run secrets:env` last hydrated the `.env` < 15 min ago
- **WHEN** `docker compose -f <stack>/compose.yaml up -d` runs
- **THEN** the Locket sidecar SHALL fall back to
  `LOCKET_FALLBACK_FILE=/run/secrets/locket/env-fallback.env`
- **AND** the stack SHALL start successfully using the cached
  `.env` values
- **AND** no `{{ infisical://... }}` placeholders SHALL appear in
  `/run/secrets/locket/secrets.env`

#### Scenario: The OCI Infisical is down

- **GIVEN** `infisical.cianfhoghlaim.ie/api/status` returns 502
  for > 1 min
- **WHEN** a Locket sidecar tries to fetch a secret
- **THEN** the sidecar SHALL fall back to the
  `LOCKET_FALLBACK_FILE` value
- **AND** the stack SHALL continue to operate using the cached
  value
- **AND** `docker logs <stack>-locket` SHALL print
  `warn: OCI Infisical unreachable, using fallback file`
- **AND** once OCI Infisical recovers, the sidecar SHALL
  resume fetching from OCI within 10s (Locket's `--mode=watch`
  poll interval)

#### Scenario: The `secrets_env_refresh` asset runs

- **GIVEN** the asset is on a 15-min Komodo schedule
- **WHEN** the schedule fires
- **THEN** the asset SHALL run
  `infisical export --in-file /Users/.../.infisical.env
  --out-file /Users/.../.env`
- **AND** the `.env` file SHALL be atomically replaced
  (write-temp + rename, per `bons-locket-shim.py:write_atomic`)
- **AND** the asset materialization SHALL record the new
  `.env` SHA in Dagster's asset catalog

#### Scenario: A new secret is added to OCI

- **GIVEN** a developer adds a new secret at
  `infisical://dev-baile/<stack>/<key>` in the OCI Infisical UI
- **WHEN** `mise run iac:sync:secrets` runs (or the
  15-min schedule fires)
- **THEN** the new secret SHALL appear in the local `.env`
  within 15 min
- **AND** the Locket sidecar SHALL pick up the new secret
  via its `--mode=watch` poll interval (2s debounce)
- **AND** the Locket sidecar SHALL NOT require a stack restart

#### Scenario: The local Infisical containers are still running

- **GIVEN** this change has been deployed
- **WHEN** `docker ps --filter name=infisical` runs on `bunchloch`
- **THEN** the local `infisical-backend` + `infisical-db` +
  `infisical-redis` containers SHALL NOT be present
- **AND** no `stacks/infisical/` reference to `host.docker.internal:8081`
  SHALL remain in any `sidecar.yaml` or `.env.example`
