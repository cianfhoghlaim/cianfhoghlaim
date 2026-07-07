# Tasks

## Phase 1 — Pre-flight (5 min)

- [ ] 1.1 Confirm Changes 1 + 2 are archived (the 19 stacks +
      2 observability stacks are available; Wave 3 dependencies
      are met).
- [ ] 1.2 Verify the marimo compose edits landed:
      ```bash
      grep -E "image:|mission_control" "bonneagar/stacks/marimo/compose.yaml"
      # Expect: ghcr.io/marimo-team/marimo:0.11.19
      # Expect: dashboards/mmo/mission_control.py
      grep "oideachais/notebooks\|cianfhoghlaim/notebooks" \
        "bonneagar/stacks/marimo/compose.yaml"
      # Expect: ../../cianfhoghlaim/notebooks:/notebooks:ro
      ```
- [ ] 1.3 Verify the canonical notebooks dir exists at the
      mounted path:
      ```bash
      ls ../../cianfhoghlaim/notebooks/dashboards/mmo/mission_control.py
      ```
- [ ] 1.4 Run `bun run validate-stacks` and confirm zero new
      failures.

## Phase 2 — Wave 3: marimo bring-up (5 min)

- [ ] 2.1 `./scripts/stack.sh marimo up -d`
- [ ] 2.2 `./scripts/stack.sh marimo ps` — confirm the marimo
      container is running with the pinned image.
- [ ] 2.3 `./scripts/stack.sh marimo logs 2>&1 | head -40` —
      confirm marimo started successfully and is loading
      `/notebooks/dashboards/mmo/mission_control.py`.
- [ ] 2.4 `curl -fsS http://localhost:2718/api/health` — marimo
      healthcheck endpoint responds.
- [ ] 2.5 Open `http://localhost:2718` in a browser. Confirm:
      - The marimo editor UI loads
      - The `mission_control.py` notebook is rendered
      - The 5-stage tabs (Aistear / Primary / JC / SC /
        Tertiary) are visible
- [ ] 2.6 Verify the notebook can read from the lakehouse:
      open one of the cells that queries DuckDB; the output
      should populate from `lakehouse-postgres` (via the
      `lakehouse_lakehouse` external network).

## Phase 3 — Validation (5 min)

- [ ] 3.1 Re-run `bun run validate-stacks` and confirm zero
      new failures.
- [ ] 3.2 Run `mise run lint:skills` and confirm 123/123 pass.
- [ ] 3.3 Run `openspec validate 2026-07-02-add-marimo-stack
      --strict` and confirm "is valid".
- [ ] 3.4 Re-run `docker ps --format "{{.Names}}\t{{.Image}}\t{{.Status}}"`
      and confirm `marimo` container using
      `ghcr.io/marimo-team/marimo:0.11.19`.
- [ ] 3.5 Capture the marimo UI URL + screenshot for the
      HEALTH_REPORT refresh.

## Phase 4 — Hand-off to Change 4

- [ ] 4.1 Cumulative state after Change 1 + 2 + 3:

      | Wave | Stacks | Status |
      |:--|:--|:--|
      | 1 | lakehouse, lancedb, falkordb, dragonfly | 4 ready |
      | 2a | litellm, llama-swap, mlflow, cognee, unstract, langfuse, graphiti, dagster | 8 ready |
      | 2b | logfire, dots-ocr | 1 ready, 1 broken (registry path) |
      | 2c | olmocr, paddleocr, docling-serve | 3 ready (pinned) |
      | 3 | invokeai, convex, risingwave, marimo | 4 ready |
      | 4 | hermes, openclaw, openchamber | 0 ready (Change 4) |

- [ ] 4.2 Hand off to Change 4 (`2026-07-02-add-agent-surface-stacks`).
      Change 4 adds 3 agent UI surfaces in Wave 4 (hermes +
      openclaw + openchamber), all routed through litellm.

## Rollback procedure

Per-stack:
```bash
./scripts/stack.sh marimo down
```

The compose edits are independent of container lifecycle; they
can be reverted via `git checkout` without stopping the
running container (Compose does not re-read image: tags or
volume mounts on restart).

## Memory budget

- marimo server: ~1-2 GB RAM (the compose caps at 2 GB)

The new stack adds ~2 GB to the Wave 3 peak, well within the
51.5 GB M4 baseline.

## Failure modes & escalation

- **marimo container exits immediately after pull** — the
  `ghcr.io/marimo-team/marimo:0.11.19` image may not include
  the Python deps required by `mission_control.py`. Check
  the logs: `./scripts/stack.sh marimo logs -f 2>&1 | head -50`.
  If a module is missing (e.g., `duckdb`, `cognee`,
  `litellm`), either (a) add it to a custom Dockerfile
  + `image:` rebuild, or (b) skip the marimo bring-up and
  use the local CLI: `cd ../../cianfhoghlaim/notebooks &&
  uv run marimo edit dashboards/mmo/mission_control.py`.
- **marimo can't reach lakehouse-postgres** — confirm the
  `lakehouse` stack is up and on the same
  `lakehouse_lakehouse` external network. The marimo compose
  joins both `cianfhoghlaim` (internal) and `lakehouse`
  (external); if `lakehouse` is not started, the
  lakehouse-lancedb-backed notebooks will fail.
- **The `--headless` flag prevents the marimo edit UI from
  rendering** — this is by design (we want a server-mode
  notebook, not an interactive edit). If you need the full
  marimo editor UX (drag-and-drop cells, hidden code
  toggles), drop the `--headless` flag and the compose will
  serve the editor view at the same port.
- **The `mission_control.py` notebook is interactive and
  expects user input** — running it in headless mode shows
  the current cell state but not interactive controls. For
  a passive dashboard view, swap the `edit` command for
  `run` (note: `marimo run` shows the notebook as a static
  HTML report, not the interactive editor; documented at
  https://docs.marimo.io/cli/).