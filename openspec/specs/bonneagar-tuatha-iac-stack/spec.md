# Spec: `bonneagar-tuatha-iac-stack`

## Purpose

This capability specifies the GOLD_STANDARD IaC contract that the
`bonneagar/stacks/tuatha/` directory must satisfy. The contract mirrors
the canonical 6-file pattern (compose + sidecar + secrets.env + pangolin +
blueprint + .env.example) established for the agent-platform clusters and
adds the Tuatha-specific 3-route public exposure (api, ui, game) wired to
the Pocket ID OIDC identity provider.
## Requirements
### Requirement: 6-file GOLD_STANDARD IaC contract

The system SHALL provide the 6 canonical IaC files at
`bonneagar/stacks/tuatha/` (compose.yaml, compose.dev.yaml, sidecar.yaml,
secrets.env, pangolin.yaml, blueprint.yaml, .env.example, README.md) per
the 6-label pattern defined in `.agents/skills/infrastructure-stacks/SKILL.md`.

#### Scenario: All 6 files present and valid

- **WHEN** `bun run validate-stacks tuatha` is run
- **THEN** the validator exits 0 with "GOLD_STANDARD compliant" output

#### Scenario: Locket sidecar populates the 6 secrets at runtime

- **WHEN** `docker compose -f bonneagar/stacks/tuatha/compose.yaml up -d` runs
- **THEN** the 6 Locket-managed secrets (TUATH_OPENAI_API_KEY, etc.) are
  injected into the running containers' env

### Requirement: IaC GOLD_STANDARD

The `bonneagar/stacks/tuatha/` directory MUST contain the same 7 files that
`bonneagar/stacks/pocket-id/` contains:

1. `compose.yaml` — the Docker Compose stack
2. `pangolin.yaml` — the Pangolin auto-discovery labels (one file, plural
   form `pangolin.resource.*` consistent with pocket-id)
3. `README.md` — module-level operator documentation
4. `secrets.env` — Locket-managed secret references (all `TUATH_*` prefix)
5. `sidecar.yaml` — the Locket sidecar template
6. `blueprint.yaml` — the Pangolin private-resource blueprint
7. `.env.example` — local dev env template

#### Scenario: Operator runs `ls bonneagar/stacks/tuatha/` and counts files

```
$ ls bonneagar/stacks/tuatha/
README.md
blueprint.yaml
compose.dev.yaml   # dev-only override (optional but expected)
compose.yaml
.env.example
pangolin.yaml
secrets.env
sidecar.yaml
```

#### Scenario: Operator opens `secrets.env` and sees only `TUATH_*` secrets

```
TUATH_OPENAI_API_KEY={{ infisical://... }}
TUATH_ANTHROPIC_API_KEY={{ infisical://... }}
TUATH_LANGFUSE_PUBLIC_KEY={{ infisical://... }}
TUATH_LANGFUSE_SECRET_KEY={{ infisical://... }}
TUATH_X402_PAYMENT_URL={{ infisical://... }}
TUATH_JWT_SIGNING_KEY={{ infisical://... }}
```

### Requirement: Three named Pangolin routes

`bonneagar/stacks/tuatha/pangolin.yaml` MUST declare the 3 named routes that
the Tuatha stack exposes to the public internet:

1. `tuath-api.cianfhoghlaim.ie` — TinyAuth passkey-gated (`tinyauth,rate-limit-api` middleware)
2. `tuath-ui.cianfhoghlaim.ie` — TinyAuth passkey-gated (`tinyauth` middleware)
3. `tuath.cianfhoghlaim.ie` — public, rate-limited only

The Dagster webserver is intentionally NOT routed through Pangolin.

#### Scenario: Operator runs the bound Pangolin resources

```
$ curl -ksS -H "Authorization: Bearer $PANGOLIN_API_KEY" \
   $PANGOLIN_URL/api/v1/resources?org_id=$PANGOLIN_ORG_ID | \
   python3 -m json.tool | jq '.data[].full_domain'

"tuath-api.cianfhoghlaim.ie"
"tuath-ui.cianfhoghlaim.ie"
"tuath.cianfhoghlaim.ie"
```

### Requirement: Locket sidecar contract

`bonneagar/stacks/tuatha/sidecar.yaml` MUST contain a `locket` service that:

- Uses the `ghcr.io/bpbradley/locket:infisical` image
- Runs as user `65532:65532` (the bons-locket-shim shim container)
- Drops ALL capabilities and sets `no-new-privileges:true`
- Mounts `./secrets.env` as `/templates/secrets.env:ro`
- Mounts `stack-secrets` (tmpfs, mode 700) at `/run/secrets/locket`
- References the project's `infisical_secret` Docker secret
- Health-check endpoint on `locket healthcheck`
- `api`, `ui`, and `game` services depend on `service_healthy: locket`
- All 3 services `env_file: /run/secrets/locket/secrets.env`

#### Scenario: Operator deploys via Komodo

```
$ komodo deploy stack tuatha --server bunchloch
[locket]   ✓ Healthy (memory=2MB, uptime=2s)
[api]      ✓ Up (port 8002 open)
[ui]       ✓ Up (port 3010 open)
[game]     ✓ Up (port 8080 open)
$ curl -s http://localhost:8002/healthz
{"status":"ok","locket":"healthy","infisical_project_id":"f3cff583-..."}
```

### Requirement: Operator onboarding script contract

`scripts/onboard-tuatha.sh` MUST exist and accept the following args:

- `--non-interactive` (reads `.env` instead of prompting)
- `--skip-wire` (only writes `.env`, doesn't run the wire script)
- `--no-infisical` (skips the local Infisical write)
- `--domain=DOMAIN` (override the root domain)
- `-h, --help`

It MUST prompt for these 12 secrets:

```
POCKETID_URL, POCKETID_API_KEY, PANGOLIN_URL, PANGOLIN_API_KEY,
PANGOLIN_ORG_ID, KOMODO_URL, KOMODO_API_KEY, INFISICAL_URL,
INFISICAL_CLIENT_ID, INFISICAL_CLIENT_SECRET, OPENAI_API_KEY,
ANTHROPIC_API_KEY
```

It MUST write them to `$WORKTREE/.env` (idempotent upsert).

It MUST (by default) run `scripts/wire-tuatha.sh` after dry-run, prompting
for a Y/N confirmation before running the non-dry-run path.

#### Scenario: First-time operator runs the wizard

```
$ ./scripts/onboard-tuatha.sh
[14:32:01] Tuatha + Pangolin + Komodo + Infisical Onboarding Wizard
[14:32:01] =======================================================
=== Step 1: Collect credentials ===
  Pocket ID URL [https://auth.cianfhoghlaim.ie]:
  Pocket ID admin API key [*****]:
  ...
[14:32:18] Updated /Users/cian/.config/opencode/.env
[14:32:19] ===================================
Run wire for real (not dry-run)? [y/N]: y
[14:32:25] Tuatha + Pangolin + Komodo + Infisical wiring: COMPLETE
```

### Requirement: Secret rotation cron contract

`scripts/rotate-tuatha-secrets.sh` MUST exist and accept:

- `--install-cron` (writes `/etc/cron.d/tuatha-rotation`)
- `--dry-run` (logs without mutating)
- `--force` (rotates even when not due)
- `-h, --help`

The `--install-cron` arg MUST write a cron entry at `/etc/cron.d/tuatha-rotation`
that runs every 90 days at 03:00 UTC.

The script MUST rotate the Pocket ID `tuatha` OIDC client secret and update
the Komodo stack env block. It MUST write an audit record to
`/tmp/tuatha-rotation-{ts}.json` and post to `ROTATION_WEBHOOK_URL` if set.

#### Scenario: Operator installs the cron

```
$ sudo ./scripts/rotate-tuatha-secrets.sh --install-cron
[14:32:01] Installing cron entry to /etc/cron.d/tuatha-rotation
  ✓ Installed /etc/cron.d/tuatha-rotation (every 90 days @ 03:00)
  ✓ Logs at /var/log/tuatha-rotation.log
```

#### Scenario: Cron fires at 03:00 on day 1 of every 3rd month

```
$ tail -f /var/log/tuatha-rotation.log
[03:00:01] rotate-tuatha-secrets: starting
[03:00:01] Step 1: Rotate Pocket ID OIDC client secret for the 'tuatha' client
  ✓ Pocket ID secret rotated (length=64)
[03:00:02] Step 2: Issue a fresh Pangolin API key with a 7-day TTL
  ✓ Pangolin API key rotated (7-day TTL)
[03:00:03] Step 3: Push rotated secrets into Komodo tuatha stack
  ✓ Komodo stack env updated
[03:00:04] rotate-tuatha-secrets: ok
[03:00:04]   audit: /tmp/tuatha-rotation-20261001T030001Z.json
```

