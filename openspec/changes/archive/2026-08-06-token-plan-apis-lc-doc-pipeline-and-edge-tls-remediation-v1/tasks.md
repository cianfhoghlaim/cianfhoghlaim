# Tasks — token-plan APIs + LC doc pipeline + edge TLS remediation

## 1. Immediate client-side unblock (completed in-authoring session 2026-08-06)

- [x] 1.1 Diagnose `unable to verify the first certificate`: confirm
  `litellm.cianfhoghlaim.ie` + `langfuse.cianfhoghlaim.ie` serve
  `CN=TRAEFIK DEFAULT CERT` (OpenSSL verify code 21) while the apex
  `cianfhoghlaim.ie` verifies OK.
- [x] 1.2 Repoint the opencode `minimax` provider from
  `https://litellm.cianfhoghlaim.ie` to the direct coding-plan endpoint
  `https://api.minimax.io/anthropic` (matches the build-agent description
  "direct coding-plan slot (no LiteLLM, no OpenCode Go)" and the
  `.infisical.env` `ANTHROPIC_BASE_URL`).
- [x] 1.3 Add a `qwen` provider to `opencode.json` reading
  `{env:DASHSCOPE_API_KEY}` + `{env:DASHSCOPE_BASE_URL}` with models
  `qwen3.7-plus`, `qwen3-coder-next`, `qwen3-coder-plus`.
- [x] 1.4 Add a `litellm_local` provider (`http://localhost:4000/v1`,
  `LITELLM_MASTER_KEY`) as the gateway fallback slot.
- [x] 1.5 Localhost-first fallback in `.infisical.env`:
  `LANGFUSE_HOST=http://localhost:3000`,
  `LITELLM_BASE_URL=http://localhost:4000/v1` (edge URLs documented for
  restoration).
- [x] 1.6 Add the token-plan section to `.infisical.env`:
  `MINIMAX_API_KEY=infisical://dev-baile/minimax/api_key`,
  `MINIMAX_BASE_URL=https://api.minimax.io/v1`,
  `DASHSCOPE_API_KEY=infisical://dev-baile/qwen/api_key`,
  `DASHSCOPE_BASE_URL=https://coding.dashscope.aliyuncs.com/v1`,
  `DASHSCOPE_ANTHROPIC_BASE_URL=https://coding.dashscope.aliyuncs.com/apps/anthropic`;
  replace the `ANTHROPIC_AUTH_TOKEN="<MINIMAX_API_KEY>"` placeholder with
  the vault ref.
- [x] 1.7 Ship `scripts/check-edge-tls.sh` (priority-domain TLS verify gate
  with `--strict` + `--all` modes and remediation guidance).

## 2. Secrets hydration (user action, before first token-plan run)

> Status 2026-08-07: BLOCKED on human/environment action. Hydration is
> unusable in agent shells: `mise run cianfhoghlaim:secrets:hydrate`
> fails (the `secrets` subcommand is documented in `mise.toml` but
> unimplemented in `scripts/cianfhoghlaim-cli.ts`), and the `locket
> exec` fallback needs `INFISICAL_CLIENT_ID`/`INFISICAL_CLIENT_SECRET`,
> which are absent. `MINIMAX_API_KEY` IS hydrated; `DASHSCOPE_API_KEY`
> is NOT (Qwen cross-check secondary fails auth until it is).

- [ ] 2.1 Add `DASHSCOPE_API_KEY=<qwen-cloud-plan-key>` to `.env`
  (never commit); confirm `MINIMAX_API_KEY` is present (it is, line 84).
- [ ] 2.2 Run `bun run scripts/init-vault.ts` (a.k.a. `mise run secrets:init`)
  to create `dev-baile/minimax/api_key` + `dev-baile/qwen/api_key` in the
  Infisical vault.
- [ ] 2.3 Re-enter the repo root so mise hooks re-hydrate `.env`; verify
  `DASHSCOPE_BASE_URL` + `MINIMAX_API_KEY` resolve (names only — never
  print values).

## 3. Edge TLS remediation on arm1-oci (server-side)

- [ ] 3.1 Run `mise run preflight-arm-oci` (mandatory before any arm1-oci
  mutation).
- [ ] 3.2 On arm1-oci, inspect `/opt/pangolin/config/traefik/traefik_config.yml`:
  the `certificatesResolvers` name MUST match the `certResolver: letsencrypt`
  referenced by the 7 stack `pangolin.yaml` files (cianfhoghlaim, cognee,
  hermes, langfuse, litellm, openchamber, openclaw). If the resolver is
  named differently (e.g. `letsencrypt-wildcard`), either rename the
  resolver or update the 7 `pangolin.yaml` files + redeploy.
- [ ] 3.3 Confirm `CLOUDFLARE_DNS_API_TOKEN` is set in `/opt/pangolin/.env`
  (the `.env.example` ships `__FILL_IN__`; Zone:DNS:Edit on cianfhoghlaim.ie).
- [ ] 3.4 `docker restart traefik` within the pangolin stack; watch Traefik
  logs for ACME issuance of `*.cianfhoghlaim.ie` / per-host names.
- [ ] 3.5 Re-run `bash scripts/check-edge-tls.sh --strict --all` — MUST exit
  0 before any consumer is repointed at the edge.
- [ ] 3.6 Wire the gate into `mise run iac-health` (call
  `scripts/check-edge-tls.sh --strict` for the priority domains).
- [ ] 3.7 Optional restoration: repoint `LITELLM_BASE_URL` to the vault ref
  and the opencode `minimax` provider to the edge ONLY after 3.5 passes.

## 4. Token-plan registration in the canonical registry

- [x] 4.1 Add token-plan endpoint entries to
  `meaisinfhoghlaim/models/model_registry.py` (family `text_llm`):
  ~~`minimax-m3` gains `endpoint="https://api.minimax.io/v1"` +
  `anthropic_endpoint="https://api.minimax.io/anthropic"` metadata~~ —
  DEFERRED: the `minimax-m3` entry was intentionally left untouched
  (its direct endpoint is configured via `.infisical.env`
  `MINIMAX_BASE_URL` + `baml_src/clients.baml` instead); new
  `qwen3.7-plus` + `qwen3-coder-next` entries ADDED with
  `backend="dashscope"`, `env_var="DASHSCOPE_API_KEY"`, roles
  `token_plan_primary` / `token_plan_coding` (registry now 60 entries;
  `resolve()` verified for both roles).
- [x] 4.2 Confirm `baml_src/clients.baml` `MINIMAX_BASE_URL` hydration works
  with the new template value — BAML regenerated clean via
  `.venv/bin/baml-cli generate --from baml_src` (NOTE: `uv run
  baml-cli generate` / `mise run cic:baml:generate` currently fail on a
  pre-existing `dagster-components` uv resolution conflict — separate
  follow-up). `mise run cic:baml:test` not run (same uv conflict).
- [x] 4.3 Add a `qwen` BAML client (openai-generic, `DASHSCOPE_BASE_URL` +
  `DASHSCOPE_API_KEY`, model `qwen3.7-plus`) as the secondary text client —
  DONE as `client<llm> ExtractQwenCrossCheck` in `baml_src/clients.baml`
  (retry_policy Simple); `minimax-m3` remains `text_llm/default`.
- [x] 4.4 Run `mise run lint:registry` — no new hardcoded model strings
  (0 drift; `scripts/registry_audit.py` `_KNOWN_MODEL_KEYS` updated with
  both new keys).

## 5. Leaving Certificate document processing (13 subjects × EN + GA)

> Status 2026-08-07: chemistry PILOT (1 of 13 subjects) complete through
> 5.1–5.6 with documented environment caveats; remaining 12 subjects are
> backlog (§6). Details in `docs/plans/2026-08-06-token-plan-progress-and-handoff.md`.

- [x] 5.1 DLT filesystem source over `leaving_certificate/<subject>/<lang>/`
  — consolidated on the EXISTING `dlt_sources/filesystem/leaving_cert_source.py`
  (`lc5_documents` resource; canonical per the handoff architectural
  decision; the `dlt/british_isles/...` path in the original task text is
  the pre-v7 location). Added `subjects` param for scoped dev runs.
  Files are already local — no live scraping. Dev run: all 16 chemistry
  files (8 en + 8 ga) processed. The duplicate
  `dlt_sources/british_isles/ireland/education/subjects/chemistry/{sources.py,schema.py}`
  was deprecated in place (docstrings only; grep confirmed zero live
  importers of `schema.py`, `sources.py` imported only by its own
  package `__init__.py`).
- [x] 5.2 OCR stage: `select_ocr_backend()` in `leaving_cert_source.py`
  health-checks the llama-swap `qwen3-vl-8b` path (GET
  `http://localhost:8086/health`) and falls back to a direct MiniMax-M3
  multimodal probe (`MINIMAX_BASE_URL`, logged `minimax_fallback_ok`).
  CAVEAT: llama-swap is DOWN in this environment (no Docker/GGUF
  weights) — the fallback path is the live path; verified with real
  MiniMax API replies during the dev run (backend counts:
  glm-4.6v-flash=8, gemma-4-26B-A4B=4, minimax-m3=2, molmo2-8b=2).
- [x] 5.3 BAML extraction stage — MiniMax-M3 primary + `qwen3.7-plus`
  secondary cross-check WIRED + primary VERIFIED LIVE:
  - New Python orchestration helper `dlt_sources/filesystem/lc6_cross_check.py`
    (`extract_with_cross_check()`): primary via the functions' default
    client (ExtractEn = MiniMax-M3), secondary via
    `baml_options={"client": "ExtractQwenCrossCheck"}`; diffs on
    topic_count / learning_outcome_count / level / source_pages;
    disagreements logged to Langfuse (`langfuse_trace` + span +
    `cross_check_agreement` score) with graceful degradation.
  - REQUIRED EN-ROUTE FIXES (all in `baml_src/`): `ExtractLC6Syllabus` +
    `ExtractChemSyllabus` had placeholder prompts ("Auto-generated
    extraction prompt." — no interpolation, rendered a system-only chat
    that MiniMax rejects with 400 "chat content is empty"). Both now
    have real extraction prompts with `{{ _.role("user") }}` markers +
    anti-ellipsis/stage guardrails; `SyllabusDocument.source_pages`
    made nullable (`int?`) to match `LCSyllabus.source_pages`. BAML
    regenerated clean.
  - Live result: both EN + GA chemistry syllabus PDFs extract
    topic_count=13, learning_outcome_count=53, level=LC_HL via MiniMax.
  - BLOCKED (expected): the Qwen secondary fails auth until a real
    `DASHSCOPE_API_KEY` lands in the Infisical vault (§2). Local
    Langfuse (http://localhost:3000) is currently DOWN — disagreement
    logging degrades to structlog without crashing.
- [x] 5.4 Load stage — chemistry pilot rows land in
  `md:cianfhoghlaim.leaving_cert.chemistry_pilot_documents` (16 rows) +
  `leaving_cert.chemistry_pilot_cross_check` (3 rows) via
  `ibis.duckdb.connect("md:cianfhoghlaim")` (the BIEP v3 ibis-first
  contract; loader: `scripts/load_lc_chemistry_pilot.py`, idempotent,
  `--skip-extraction` flag). DEVIATIONS (environment-forced):
  `get_dlt_destination(use_ducklake=True)` is IMPOSSIBLE in this
  environment (local lakehouse stack down — Garage :3900 + Postgres
  :5433 closed), so the load goes via the MotherDuck-hosted lakehouse
  alias directly; the canonical `cianfhoghlaim` database did not exist
  on this account's token and was CREATED by the loader (one documented
  raw `CREATE DATABASE` control-plane statement; all data writes are
  ibis). Full 13-subject `cianfhoghlaim.leaving_cert.<subject>` rollout
  is §6 backlog.
- [x] 5.5 Dagster assets — ADDITIVE pilot asset group
  `orchestration/defs/2_materials/lc_extraction/lc_chemistry_pilot_assets.py`
  (auto-discovered by `dg.load_defs()`): `lc_chem_pilot_ingested`
  (1_ingestion_education_lc_chemistry_pilot) →
  `lc_chem_pilot_cross_checked` → `lc_chem_pilot_loaded`
  (2_materials_education_lc_chemistry_pilot) +
  `lc_chem_pilot_documents_check` asset check (16 rows, both
  languages). `generic_ireland_assets.py` + `lc5_assets.py` untouched.
  NOT wired: `ocr_completion_sensor` (deferred — pilot scope is the
  2-path extraction, not the full per-cohort 5-phase pattern).
- [x] 5.6 Verify — `schema_introspect` lists both pilot tables (14
  columns each) via `notebooks/_shared/schema.py` (which gained a small
  ibis-12 `.execute()` compat shim in `schema_introspect`); row counts
  verified from a separate read-only process. Marimo summary cell
  DEFERRED (Phase E, out of pilot scope).

## 6. Execute the priority openspec backlog with the token plans

- [ ] 6.1 Use the prompt pack at
  `docs/plans/2026-08-06-token-plan-opencode-prompts.md` (P1–P6) with the
  opencode build/orchestrator agents on `minimax/MiniMax-M3` +
  `qwen/qwen3.7-plus`.
- [ ] 6.2 Complete the pending
  `2026-08-15-meaisinfhoghlaim-to-machine-learning-rename-v1` change
  (currently "No tasks" — author its tasks.md via prompt P3).
- [ ] 6.3 Run quality gates after each landed change:
  `mise run lint && mise run py:typecheck && mise run turbo typecheck`.

## 7. Archive gate

- [ ] 7.1 `openspec validate 2026-08-06-token-plan-apis-lc-doc-pipeline-and-edge-tls-remediation-v1 --strict`
  passes.
- [ ] 7.2 All of §2–§6 complete; then
  `openspec archive 2026-08-06-token-plan-apis-lc-doc-pipeline-and-edge-tls-remediation-v1 --yes`.
