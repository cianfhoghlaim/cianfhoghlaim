# Tasks

## Phase 1 — Pre-flight (5 min)

- [ ] 1.1 Confirm Changes 1 + 2 + 3 are archived (the 24
      stacks — 19 + lancedb + logfire + marimo — are
      available).
- [ ] 1.2 Confirm the 3 image edits landed:
      ```bash
      grep -E "image:" bonneagar/stacks/hermes/compose.yaml | head -1
      grep -E "image:" bonneagar/stacks/openclaw/compose.yaml | head -1
      grep -E "image:" bonneagar/stacks/openchamber/compose.yaml | head -1
      # Expect:
      #   ghcr.io/nousresearch/hermes-agent:0.17.0
      #   ghcr.io/openclaw/openclaw:2026.2.6
      #   ghcr.io/openchamber/openchamber:1.0.0
      ```
- [ ] 1.3 Confirm `docker login ghcr.io` is configured (for
      the private hermes + openchamber images):
      ```bash
      cat ~/.docker/config.json | jq -r '.auths["ghcr.io"].auth // "NOT CONFIGURED"'
      ```
      If "NOT CONFIGURED", run
      `echo "$GHCR_TOKEN" | docker login ghcr.io -u $GHCR_USER
      --password-stdin` with the appropriate NousResearch +
      openchamber PATs.
- [ ] 1.4 Confirm `litellm` (Change 1) is up and answering
      LLM pings on `:4000`:
      ```bash
      curl -fsS http://localhost:4000/health/liveliness
      ```
- [ ] 1.5 Confirm `langfuse` (Change 1) is up and answering
      on `:3001`:
      ```bash
      curl -fsS http://localhost:3001/api/public/health
      ```
- [ ] 1.6 Run `bun run validate-stacks` and confirm zero
      new failures.

## Phase 2 — Wave 4: agent surfaces bring-up (10 min)

- [ ] 2.1 `./scripts/stack.sh openclaw up -d` (the channel-
      fanout gateway; public image, will pull immediately)
- [ ] 2.2 `./scripts/stack.sh openclaw ps` — confirm
      `openclaw` container is running.
- [ ] 2.3 `./scripts/stack.sh openclaw logs 2>&1 | head -40`
      — confirm openclaw started and is listening on
      `:18789`.
- [ ] 2.4 `curl -fsS http://localhost:18789/api/health` —
      openclaw healthcheck endpoint responds.
- [ ] 2.5 `./scripts/stack.sh openchamber up -d` (the
      OpenCode web/desktop UI; private image, requires
      GHCR login)
- [ ] 2.6 `./scripts/stack.sh openchamber ps` — confirm
      `openchamber` container is running.
- [ ] 2.7 `./scripts/stack.sh openchamber logs 2>&1 | head
      -40` — confirm openchamber started and is listening
      on `:3000`.
- [ ] 2.8 `curl -fsS http://localhost:3000/api/health` —
      openchamber healthcheck endpoint responds.
- [ ] 2.9 `./scripts/stack.sh hermes up -d` (the autonomous
      agent runtime; private image, requires NousResearch
      credentials on GHCR)
- [ ] 2.10 `./scripts/stack.sh hermes ps` — confirm `hermes`
      container is running.
- [ ] 2.11 `./scripts/stack.sh hermes logs 2>&1 | head -40`
      — confirm hermes started and is listening on `:9119`.
- [ ] 2.12 `curl -fsS http://localhost:9119/api/health` —
      hermes healthcheck endpoint responds.

## Phase 3 — Cross-stack verification (10 min)

- [ ] 3.1 **Litellm chokepoint test (openclaw).** Send a
      test message via the openclaw WebSocket RPC
      (`:18789`). The LLM call SHALL route through
      `http://litellm:4000/v1` (verified by inspecting the
      litellm access log for a `model=<M3-model>` entry).
- [ ] 3.2 **Litellm chokepoint test (hermes).** Trigger a
      hermes conversation via the dashboard API
      (`:9119/api/sessions/*`). The LLM call SHALL route
      through `http://litellm:4000/v1`.
- [ ] 3.3 **Litellm chokepoint test (openchamber).** Open
      the openchamber UI at `http://localhost:3000/` and
      submit a prompt. The LLM call SHALL route through
      `http://litellm:4000/v1` (the `OPENAI_BASE_URL`
      env var in openchamber's `secrets.env` is Infisical-
      resolved at runtime).
- [ ] 3.4 **Langfuse trace verification.** Confirm all 3
      stacks emit traces to langfuse (`http://localhost:3001`).
      For each of the 3 test calls above, navigate to
      `langfuse-web` → Traces and confirm a new trace was
      recorded with the right `service.name` (openclaw-gateway,
      hermes-agent, or openchamber).
- [ ] 3.5 **3-layer auth verification (hermes).** Hermes
      requires (1) Pangolin TinyAuth (not exercised in
      dev mode), (2) `users.allowlist` (populated from
      `HERMES_OPERATOR_POCKET_ID_SUBJECT` in
      `secrets.env`), and (3) per-channel sender
      allowlists. In dev mode, the `init-allowlist.sh`
      script auto-runs and adds a default user. Verify:
      `./scripts/stack.sh hermes exec hermes cat /home/hermes/.hermes/state/users.json`
      — the operator's Pocket ID subject SHALL be present.

## Phase 4 — Validation (5 min)

- [ ] 4.1 Re-run `bun run validate-stacks` and confirm zero
      new failures.
- [ ] 4.2 Run `mise run lint:skills` and confirm 123/123
      pass.
- [ ] 4.3 Run `openspec validate
      2026-07-02-add-agent-surface-stacks --strict` and
      confirm "is valid".
- [ ] 4.4 Re-run `docker ps --format
      "{{.Names}}\t{{.Image}}\t{{.Status}}"` and confirm
      all 3 containers are running with their pinned
      images.

## Phase 5 — Hand-off (final change of the 4-change sequence)

- [ ] 5.1 Cumulative state after all 4 changes:

      | Wave | Stacks | Status |
      |:--|:--|:--|
      | 1 | lakehouse, lancedb, falkordb, dragonfly | 4 ready |
      | 2a | litellm, llama-swap, mlflow, cognee, unstract, langfuse, graphiti, dagster | 8 ready |
      | 2b | logfire, dots-ocr | 1 ready, 1 broken (registry path; deferred fix) |
      | 2c | olmocr, paddleocr, docling-serve | 3 ready (pinned) |
      | 3 | invokeai, convex, risingwave, marimo | 4 ready |
      | 4 | hermes, openclaw, openchamber | 3 ready |

      **Total ready: 24 of 25 stacks (dots-ocr excluded as
      broken; deferred to a separate follow-up change).**

- [ ] 5.2 Update `bonneagar/stacks/HEALTH_REPORT.md` with
      the live 2026-07-02 container inventory.
- [ ] 5.3 The 4-change sequence is complete. Hand off to
      the deferred backlog:
      - dots-ocr remediation
      - browser stack remediation
      - mailcow-dockerized (for oideachais-email-triage)
      - mlx-omni + ollama (for OCR backend parity)
      - Letta (for L5 agent memory)
      - Multi-notebook marimo dashboard
      - Infisical wiring for hermes + openchamber private
        image pulls
      - Renovate cycle for full SHA256 digest pinning

## Rollback procedure

Per-stack:
```bash
./scripts/stack.sh hermes down
./scripts/stack.sh openclaw down
./scripts/stack.sh openchamber down
```

The compose edits are independent of container lifecycle;
they can be reverted via `git checkout` without stopping
any running containers.

## Memory budget

- `hermes` agent runtime: ~1-2 GB RAM
- `openclaw` channel-fanout gateway: ~1-2 GB RAM
- `openchamber` web/desktop UI: ~0.5-1 GB RAM

The 3 new stacks combined add ~3-5 GB to the Wave 4 peak,
well within the 51.5 GB M4 baseline.

## Failure modes & escalation

- **GHCR 401 Unauthorized on hermes or openchamber** —
  the upstream images are private; the operator must add
  NousResearch + openchamber PATs to
  `~/.docker/config.json`:
  `echo "$GHCR_PAT" | docker login ghcr.io -u $GHCR_USER
  --password-stdin`. Re-run `./scripts/stack.sh hermes
  pull` after the login.
- **`LitellmBaseUrlNotReachable` error in hermes /
  openclaw / openchamber** — the `litellm` stack
  (Change 1 Wave 2) is not up. Bring it up:
  `./scripts/stack.sh litellm up -d` and wait for the
  `/health/liveliness` endpoint to respond.
- **hermes `init-allowlist.sh` fails** — the script
  writes the operator's Pocket ID subject to
  `hermes-state/users.json`; if the script cannot find
  the subject, hermes starts in "deny-all" mode. Verify
  `HERMES_OPERATOR_POCKET_ID_SUBJECT` is set in
  `secrets.env` (Locket-resolved at runtime, or
  hardcoded in dev mode).
- **openchamber UI doesn't load opencode-ai models** —
  the bundled opencode-ai runtime needs to fetch
  model metadata; if `OPENAI_BASE_URL` is malformed
  (e.g. `{{ infisical:///... }}` left unresolved by
  Locket), the model list will be empty. In dev mode
  (no Locket), set
  `OPENAI_BASE_URL=http://litellm:4000/v1` directly
  in the env.