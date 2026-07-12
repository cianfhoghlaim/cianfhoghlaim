# Komodo Procedure `server_id` Convention

Every Komodo procedure TOML under `komodo/procedures/` SHOULD declare a
top-level `server_id` field that tells Komodo Core which host this
procedure runs on. The valid values are:

| Value | Meaning |
|:--|:--|
| `"bunchloch"` | Runs on the `bunchloch` host (this Mac, the workload + dev host). |
| `"arm1-oci"` | Runs on the `arm1-oci` host (Oracle Cloud Free Tier, Frankfurt, the control-plane host). |

## How Komodo uses `server_id`

Each Komodo Core host (bunchloch + arm1-oci) has a `komodo/resource-syncs/*.toml`
file. The sync pulls every procedure under `komodo/procedures/*.toml`, but
the per-host UI + REST API filters the list to procedures whose `server_id`
matches that host. This keeps the arm1-oci `km` UI from showing bunchloch
procedures (and vice versa).

## Procedure inventory (post-2026-07-13 change)

### bunchloch procedures (`server_id = "bunchloch"`)

| Procedure | Purpose |
|:--|:--|
| `deploy-agent-platform-cluster-bunchloch.toml` | Omnibus: 8-stack cluster on bunchloch |
| `deploy-apple-photos-ingest-bunchloch.toml` | Apple Photos ingest pipeline |
| `deploy-bunchloch-stack-bootstrap.toml` | Cold-boot: bring up 19 base stacks |
| `deploy-cognee-bunchloch.toml` | Knowledge graph memory |
| `deploy-croilar-bunchloch.toml` | Croílár portfolio stack |
| `deploy-falkordb-bunchloch.toml` | FalkorDB graph backend |
| `deploy-graphiti-bunchloch.toml` | Temporal knowledge graph |
| `deploy-hermes-bunchloch.toml` | Hermes (bunchloch) |
| `deploy-lakehouse-bunchloch.toml` | Lakehouse (MotherDuck + DuckLake) |
| `deploy-lancedb-bunchloch.toml` | LanceDB vector search |
| `deploy-langfuse-bunchloch.toml` | Langfuse observability |
| `deploy-litellm-bunchloch.toml` | LiteLLM M3 chokepoint |
| `deploy-llama-swap-bunchloch.toml` | llama-swap GGUF local model |
| `deploy-logfire-bunchloch.toml` | Logfire Python OTel |
| `deploy-mailcow-dockerized-bunchloch.toml` | Mailcow mail server |
| `deploy-mlflow-bunchloch.toml` | MLflow experiment tracking |
| `deploy-oideachais-bunchloch.toml` | Oideachais BIEP stack |
| `deploy-openchamber-bunchloch.toml` | OpenChamber (bunchloch) |
| `deploy-openclaw-bunchloch.toml` | OpenClaw (bunchloch) |
| `deploy-newt-bunchloch.toml` | newt v1 (legacy, single WireGuard client on this Mac) |
| `deploy-newt-bunchloch-v2.toml` | newt v2 (RECOMMENDED, v1.14.0 + iac:sync:sites auto-provision) |
| `deploy-pocket-id-bunchloch.toml` | Pocket ID v2.9.0 OIDC IdP (the bunchloch side; 5th cross-cutting prereq) |
| `deploy-tinyauth-bunchloch.toml` | Tinyauth v4 ForwardAuth middleware (the bunchloch side; 6th cross-cutting prereq; fixes the crash loop) |
| `cron-ccc-reindex-bunchloch.toml` | Daily 03:00 UTC CocoIndex Code rebuild |

### arm1-oci procedures (`server_id = "arm1-oci"`)

| Procedure | Purpose |
|:--|:--|
| `deploy-agent-platform-cluster-arm1-oci.toml` | Omnibus: 3 agent surfaces on arm1-oci |
| `deploy-hermes-arm1-oci.toml` | Hermes (arm1-oci) |
| `deploy-openclaw-arm1-oci.toml` | OpenClaw channel-fanout gateway |
| `deploy-openchamber-arm1-oci.toml` | OpenChamber OpenCode UI |
| `deploy-langfuse-arm1-oci.toml` | Langfuse observability sink |
| `deploy-observability-arm1-oci.toml` | logfire + dozzle + beszel foundation |
| `deploy-pocket-id-arm1-oci.toml` | Pocket ID v2.9.0 OIDC IdP (arm1-oci migration target) |
| `deploy-pangolin-newt-arm1-oci.toml` | newt client on arm1-oci (secondary, v1.14.0) |

### Host-agnostic / cross-cutting (4 procedures — all 4 include `server_id` info but are pulled by both syncs)

| Procedure | Purpose |
|:--|:--|
| `pangolin-first.toml` | ssh + Pangolin health + Pocket ID OIDC ready |
| `komodo-core.toml` | Komodo Core pod alive + REST API + periphery |
| `infisical-first.toml` | Vault reachable + project=dev-baile + machine identities |
| `locket-deploy.toml` | locket binary + infisical_secret + secrets resolved |

## Back-compat (no `server_id` field)

Procedures with no `server_id` field appear in BOTH hosts' UIs and emit
a deprecation warning in the Komodo logs:

```
WARN: procedure '<name>' has no server_id field; defaulting to both hosts.
      Add server_id = 'bunchloch' or 'arm1-oci'.
```

New procedures MUST declare a `server_id` field. The `openspec validate`
gate emits an error if the field is absent (per the
`infrastructure-stacks` spec's "Procedure `server_id` field" requirement).

## How to add a new procedure

1. Create the TOML under `komodo/procedures/<name>.toml`
2. Add `server_id = "bunchloch"` (or `"arm1-oci"`) at the top of the file
3. Run `openspec validate <change-id> --strict` to confirm the field is present
4. Commit + push to the right branch (good: `pick-4-biep-v1` for cianfhoghlaim + `pick-5b-bonneagar-v5-continuation` for bonneagar)
5. The resource-sync's 60s pull cycle picks it up automatically
