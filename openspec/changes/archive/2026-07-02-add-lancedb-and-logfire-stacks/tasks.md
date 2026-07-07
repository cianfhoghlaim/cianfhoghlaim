# Tasks

## Phase 1 — Pre-flight (5 min)

- [ ] 1.1 Confirm Change 1 is archived (the 19 stacks are
      available and the Wave 1/2 dependencies are met).
- [ ] 1.2 Verify the 5 image pins landed:
      ```bash
      for s in cognee olmocr paddleocr docling-serve lancedb; do
        echo "--- $s ---"
        grep -E "^[[:space:]]+image:[[:space:]]" "bonneagar/stacks/$s/compose.yaml" | head -2
      done
      ```
- [ ] 1.3 Verify the 2 new stack dirs are GOLD_STANDARD-compliant:
      ```bash
      for s in lancedb logfire; do
        d="bonneagar/stacks/$s"
        for f in compose.yaml secrets.env sidecar.yaml blueprint.yaml README.md; do
          [ -f "$d/$f" ] && echo "  ✓ $s/$f" || echo "  ✗ $s/$f MISSING"
        done
      done
      ```
- [ ] 1.4 Run `bun run validate-stacks` and confirm zero new
      hard failures (the pre-existing `:latest` WARNING on
      `dots-ocr` is expected and accepted in this change).

## Phase 2 — Wave 1: lancedb bring-up (2 min)

- [ ] 2.1 `./scripts/stack.sh lancedb up -d` (the primary viewer
      service; the optional `s3` profile mounter is not started
      by default)
- [ ] 2.2 `./scripts/stack.sh lancedb ps` — confirm `lancedb`
      container is running.
- [ ] 2.3 `curl -fsS http://localhost:8081/` — LanceDB viewer
      responds with HTTP 200.
- [ ] 2.4 Verify the viewer can connect to the lakehouse
      lance-namespace: open `http://localhost:8081` in a browser
      and confirm the UI loads (the lance-namespace REST endpoint
      is at `rest://lakehouse-lance-namespace:8182` inside the
      `lakehouse_lakehouse` external network).

## Phase 3 — Wave 2b: logfire bring-up (after Wave 2 langfuse + mlflow are healthy)

- [ ] 3.1 `./scripts/stack.sh logfire up -d`
- [ ] 3.2 `./scripts/stack.sh logfire ps` — confirm
      `otel/opentelemetry-collector-contrib` is running.
- [ ] 3.3 `./scripts/stack.sh logfire logs 2>&1 | head -40` —
      confirm the collector is listening on the OTLP gRPC
      (`:4317`) and OTLP HTTP (`:4318`) ports.
- [ ] 3.4 Verify the collector is reachable from any Python
      service that wants to forward spans (via the
      `OTEL_EXPORTER_OTLP_ENDPOINT=http://logfire:4317` env var):
      ```bash
      nc -zv localhost 4317
      nc -zv localhost 4318
      ```
- [ ] 3.5 (Optional) If `LOGFIRE_TOKEN` is set, verify the
      collector is forwarding to Logfire SaaS:
      `./scripts/stack.sh logfire logs 2>&1 | grep -i 'logfire\|export'`
      — look for "Successfully exported spans" or similar.

## Phase 4 — Validation (5 min)

- [ ] 4.1 Re-run `bun run validate-stacks` and confirm zero new
      failures. The pre-existing `:latest` WARNING for
      `dots-ocr` is expected; all 6 other previously-unpinned
      images are now semver-pinned.
- [ ] 4.2 Run `mise run lint:skills` and confirm 123/123 pass.
- [ ] 4.3 Run `openspec validate 2026-07-02-add-lancedb-and-logfire-stacks --strict`
      and confirm "is valid".
- [ ] 4.4 Re-run `docker ps --format "{{.Names}}\t{{.Image}}\t{{.Status}}"`
      and confirm:
      - `lancedb` container using `ghcr.io/gordonmurray/lance-data-viewer:lancedb-0.24.3`
      - `logfire` container using `otel/opentelemetry-collector-contrib:0.104.0`
- [ ] 4.5 Capture the `lancedb` viewer screenshot / URL for the
      HEALTH_REPORT refresh (Change 1 Wave 3 task 5.1).

## Phase 5 — Hand-off to Change 3

- [ ] 5.1 The 21 bundles Change 1 + Change 2 leave the cluster
      at:
      - **Wave 1:** lakehouse, lancedb, falkordb, dragonfly (4 stacks)
      - **Wave 2:** litellm, llama-swap, mlflow, cognee, unstract,
        langfuse, logfire, graphiti, dagster, dots-ocr (BROKEN),
        olmocr, paddleocr, docling-serve (12 stacks; dots-ocr
        will not start until the deferred change lands)
      - **Wave 3:** invokeai, convex, risingwave (3 stacks — marimo
        added by Change 3)
- [ ] 5.2 Hand off to Change 3 (`2026-07-02-add-marimo-stack`).
      Change 3 adds the marimo notebook server in Wave 3.

## Rollback procedure

Per-stack:
```bash
./scripts/stack.sh lancedb down
./scripts/stack.sh logfire down
```

Whole-bundle (use with care; only if both new stacks cause issues):
```bash
./scripts/stack.sh lancedb down -v  # -v wipes the lance-data volume
./scripts/stack.sh logfire down
```

The 5 image pin edits in `compose.yaml` are independent of
container lifecycle — they can be reverted via `git checkout`
without stopping any running containers (Compose does not
re-read image: tags on restart unless the container is removed
and recreated).

## Memory budget

- `lancedb` viewer: ~1 GB RAM
- `logfire` OTel collector: ~200 MB RAM

The 2 new stacks combined add ~1.2 GB to the Wave 1 / Wave 2
peak, well within the 51.5 GB M4 baseline.

## Failure modes & escalation

- **`lancedb` can't connect to `lakehouse-lance-namespace`** —
  confirm the `lakehouse` stack is on the same external network
  (`lakehouse_lakehouse`). The `lancedb` compose's primary
  `cianfhoghlaim` network is internal; the viewer connects via
  browser UI (operator-driven), not via a service link. If you
  need service-link access, add `lakehouse` to the lancedb
  service's networks (deferred; not needed for the viewer use
  case).
- **`logfire` collector can't reach Logfire SaaS** —
  `logfire.pydantic.dev:443` must be reachable from the
  bunchloch host. If you're offline, the collector still accepts
  OTLP and drops the spans silently. To debug:
  `./scripts/stack.sh logfire logs -f | grep -i 'export\|error'`
- **olmocr container exits immediately after pull** — the
  compose's healthcheck expects `:8003/health` to return 200.
  The `alleninstituteforai/olmocr:0.4.27` image may have a
  different healthcheck path; check the image's docs at
  https://hub.docker.com/r/alleninstituteforai/olmocr. If the
  healthcheck path differs, update the compose accordingly in
  a follow-up fix (not blocking Change 2 itself).
- **paddleocr 2.6-cpu-latest is from 2023** — if you need
  newer OCR models, switch to a community fork. This change
  pins to the canonical upstream tag; do not bump without
  re-validating the API contract in
  `meaisínfhoghlaim/ocr/adapters.py`.