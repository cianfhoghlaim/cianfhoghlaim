# Tasks: 2026-07-31-agentic-mesh-and-ocr-pipeline-coherence-v1

15 actions across 6 sub-areas. Each task is independently shippable as a commit.

## Sub-area A — Cross-agent context handoff protocol

- [ ] **A.1** Write `agents/contracts/context-envelope.py` — Pydantic v2 model (`agent_run_id`, `parent_trace_id`, `context_payload: dict[str, Any]`, `mtls_subject: str`, `created_at: datetime`, `expires_at: datetime`, optional `sender: str`, `recipient: str`)
- [ ] **A.2** Write `agents/contracts/openclaw_handler.py` — receives a context envelope from openchamber OR hermes, unpacks into the openclaw channel fanout context
- [ ] **A.3** Write `agents/contracts/openchamber_handler.py` — receives from openclaw OR hermes, routes into the IDE/CLI session
- [ ] **A.4** Write `agents/contracts/hermes_handler.py` — receives from openclaw OR openchamber, routes into the hermes agent runtime

## Sub-area B — ocr-router stack

- [ ] **B.1** Write `bonneagar/stacks/ocr-router/compose.yaml` — single FastAPI service (`ghcr.io/cianfhoghlaim/ocr-router:v0.1.0`), port 8090, depends on paddleocr / dots-ocr / olmocr / docling-serve / mlx-omni / llama-swap (network access only — no stack ownership)
- [ ] **B.2** Write `bonneagar/stacks/ocr-router/sidecar.yaml` — Locket shim (`ghcr.io/cianfhoghlaim/locket-shim:infisical-0.2.0`), per the openclaw pattern
- [ ] **B.3** Write `bonneagar/stacks/ocr-router/secrets.env` — `OCR_ROUTER_API_KEY`, `OCR_WEBHOOK_URL` (optional), plus the 6 backends' endpoint URLs as no-secret compose refs
- [ ] **B.4** Write `bonneagar/stacks/ocr-router/pangolin.yaml` — `Host(\`ocr-router.cianfhoghlaim.ie\`) → ocr-router:8090` with `tinyauth,secure-headers` middleware
- [ ] **B.5** Write `bonneagar/stacks/ocr-router/blueprint.yaml` — private resource, `Member` role
- [ ] **B.6** Write `bonneagar/stacks/ocr-router/README.md` — explain what the router does + the 6 backends it routes to

## Sub-area C — litellm config repair

- [ ] **C.1** Edit `bonneagar/stacks/litellm/config/config.yaml.full.bak`: rewrite the 7 dead `transformers` routes to real services (deepseek-ocr-2 → docling-serve:5001, olmocr-2-7b-1025 → olmocr:8003, uccix-* → mlx-omni:10240, molmo2-* → docling-serve:5001)
- [ ] **C.2** Edit `bonneagar/stacks/litellm/config/config.yaml.full.bak`: fix the 8 `fallback_chain` schema mismatches (litellm 1.x wants dicts, the .bak has strings). Convert each to the `[{primary: ...}, {fallbacks: [{...}, ...]}]` form
- [ ] **C.3** Move `config.yaml.full.bak` → `config.yaml` (promote the repaired config). Rename the current 12-line stub → `config.yaml.minimal.bak`
- [ ] **C.4** Edit `bonneagar/stacks/litellm/config/config.dev.yaml`: remove the `transformers` reference; keep the 3 active dev models (minimax-m3, local/vision/gemma-4-E4B, stub)

## Sub-area D — OCR Pangolin fixes + symlink fix

- [ ] **D.1** Edit `bonneagar/stacks/paddleocr/pangolin.yaml`: replace `noop: true` with a real Traefik overlay routing `paddleocr.cianfhoghlaim.ie` → `paddleocr:8000` with `tinyauth,secure-headers` middleware
- [ ] **D.2** Edit `bonneagar/stacks/dots-ocr/pangolin.yaml`: same fix for `dotsocr.cianfhoghlaim.ie` → `dots-ocr:8001`
- [ ] **D.3** Delete `bonneagar/stacks/llama-swap/config.yaml` (the broken symlink); re-create as a symlink to `../../meaisinfhoghlaim/models/llama_swap_config.yaml`

## Sub-area E — OCR webhook convention + dagster sensor

- [ ] **E.1** Edit `bonneagar/stacks/ocr-router/compose.yaml` (already covered by B.1): add `OCR_WEBHOOK_URL` to the env block (no default; sensor-discovery at runtime)
- [ ] **E.2** Write `orchestration/sensors/ocr_completion_sensor.py` — Dagster sensor that polls the OCR webhook endpoint, emits a per-document OCR completion event, triggers downstream pipeline assets

## Sub-area F — Cross-agent URL wiring

- [ ] **F.1** Edit `bonneagar/stacks/openclaw/.env.example`: add 3 vars (URLs + bridge token) for handoff to openchamber + hermes
- [ ] **F.2** Edit `bonneagar/stacks/openchamber/.env.example`: add 3 vars for handoff to openclaw + hermes
- [ ] **F.3** Edit `bonneagar/stacks/hermes/.env.example`: add 3 vars for handoff to openclaw + openchamber

## Final verification

- [ ] `openspec validate 2026-07-31-agentic-mesh-and-ocr-pipeline-coherence-v1 --strict` passes
- [ ] `mise run stack-doctor:strict` reports zero grammar regressions
- [ ] `docker compose -f ocr-router/compose.yaml -f ocr-router/sidecar.yaml config --quiet` passes
- [ ] `python -m py_compile agents/contracts/context-envelope.py` succeeds
- [ ] Git commit lands; push succeeds

## Dependency graph

```
A.1 ──► A.2 ──► A.3 ──► A.4 ──┐
                              │
B.1 ──► B.2 ──► B.3 ──► B.4 ──► B.5 ──► B.6 ──┐
                                                │
C.1 ──► C.2 ──► C.3 ──► C.4 ─────────────────────┤
                                                │
D.1 ──► D.2 ──► D.3 ─────────────────────────────┤
                                                │
E.1 ──► E.2 ─────────────────────────────────────┤
                                                │
F.1 ──► F.2 ──► F.3 ─────────────────────────────┤
                                                │
                                                ▼
                                  openspec validate --strict
                                                │
                                                ▼
                                          commit + push