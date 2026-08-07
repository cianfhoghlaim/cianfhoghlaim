# Token-plan APIs + LC doc pipeline + edge-TLS remediation — progress & handoff

**Session date**: 2026-08-06. Written because the current session is near its usage
limit; this is the handoff doc for continuing in a fresh session/agent.

**Governing plan**: `/Users/cianmacandeisigh/.claude/plans/after-the-prompt-find-stateless-nova.md`
(the approved plan this session executed against — read it for full rationale).

**Openspec change being implemented**:
`openspec/changes/2026-08-06-token-plan-apis-lc-doc-pipeline-and-edge-tls-remediation-v1/`
(`proposal.md`, `tasks.md`, `specs/*.md` — read `tasks.md` for the authoritative
section-by-section checklist; this doc summarizes progress against it but
`tasks.md` itself has NOT yet been updated to reflect what's done — do that as part
of finishing up).

---

## What triggered this work

User ran the token-plan prompt pack (`docs/plans/2026-08-06-token-plan-opencode-prompts.md`)
through opencode against MiniMax-M3/Qwen and hit `unable to verify the first
certificate`. This session diagnosed it and began implementing the pending openspec
tasks via Claude Code subagents (scope: tasks.md §2 + §4 + §5 only — §3, §6, §7
explicitly excluded per user decision).

## Diagnosis (confirmed, resolved — no further action needed here)

- `litellm.cianfhoghlaim.ie` / `langfuse.cianfhoghlaim.ie` → OpenSSL verify code 21,
  self-signed `CN=TRAEFIK DEFAULT CERT`. **Still broken server-side, out of scope**
  (arm1-oci Traefik ACME issue — tasks.md §3, not touched this session).
- `api.minimax.io`, `dashscope.aliyuncs.com`, `dashscope-intl.aliyuncs.com` all verify
  fine (code 0). `opencode.json`'s direct-endpoint fix (tasks.md §1, done before this
  session) is architecturally correct.
- The error persisted because of two separate gaps, NOT the edge cert itself:
  1. Secrets were never hydrated into the shell (`DASHSCOPE_API_KEY`/`DASHSCOPE_BASE_URL`
     unset despite being correctly defined in `.infisical.env`).
  2. The Python-side `MODEL_REGISTRY`/`clients.baml` routing path (separate from
     opencode's own chat UI) had **no DashScope/Qwen entry at all** — this session's
     Phase 1 fixed that (see below).
- **Secrets hydration is blocked in ANY Claude-Code-session shell in this environment**:
  `mise run cianfhoghlaim:secrets:hydrate` fails — the `secrets` subcommand namespace
  is documented in `mise.toml` (`cianfhoghlaim:secrets:lint|verify|hydrate|seed`) but
  **not implemented** in `scripts/cianfhoghlaim-cli.ts` (`error: unknown command:
  secrets`). The fallback, `locket exec --provider infisical ...`, also fails because
  Locket's own bootstrap credentials (`INFISICAL_CLIENT_ID`/`INFISICAL_CLIENT_SECRET`)
  are absent from the shell too. **This is a standing environment gap, not something
  fixable by a coding agent** — whoever continues this needs a shell where those two
  vars (or an already-authenticated `locket`/`infisical` session) are present, or
  needs to fix `cianfhoghlaim-cli.ts`'s missing `secrets` subcommand implementation
  (a legitimate, separate small task if no one has direct Infisical access either).

## Progress against tasks.md

- **§1 client-side unblock** — done before this session (uncommitted `opencode.json`
  diff: direct `minimax`/`qwen`/`litellm_local` providers).
- **§2 secrets hydration** — verification attempted, blocked as above. Real
  `DASHSCOPE_API_KEY` still needs to be added to the Infisical vault by a human with
  vault access; hydration mechanism itself needs either credentials or a CLI fix.
  **Not resolvable by an agent alone.**
- **§3 arm1-oci server fix** — explicitly out of scope this session, untouched.
- **§4 registry registration — DONE THIS SESSION.**
  - `meaisinfhoghlaim/models/model_registry.py`: added `qwen3.7-plus` (role
    `token_plan_primary`) and `qwen3-coder-next` (role `token_plan_coding`), both
    `family="text_llm"`, `backend="dashscope"` (new backend string, mirrors the
    existing single-word hosted-API convention), `env_var="DASHSCOPE_API_KEY"`.
    Inserted right after the untouched `minimax-m3` entry (`backend="opencode_go"`,
    left alone).
  - `baml_src/clients.baml`: new `client<llm> ExtractQwenCrossCheck` —
    `provider "openai-generic"`, `base_url env.DASHSCOPE_BASE_URL`,
    `api_key env.DASHSCOPE_API_KEY`, `model "qwen3.7-plus"`,
    `retry_policy Simple` (`Exponential` stays reserved for the 3 BIEP v3 clients).
  - `scripts/registry_audit.py`: `_KNOWN_MODEL_KEYS` updated with both new keys.
    `mise run lint:registry` → clean, 0 drift.
  - BAML regenerated clean (`ExtractQwenCrossCheck` confirmed present in generated
    `baml_client/`). Note: `uv run baml-cli generate` currently fails for an
    **unrelated, pre-existing reason** — a `dagster-components` version conflict in
    `uv`'s dependency resolution. Workaround used: call `.venv/bin/baml-cli generate
    --from baml_src` directly. Worth fixing separately; not part of this plan's scope
    but will keep tripping up anyone running the standard `mise` task.
  - Verified: `MODEL_REGISTRY.resolve("text_llm", "token_plan_primary")` →
    `qwen3.7-plus`; `resolve("text_llm", "token_plan_coding")` → `qwen3-coder-next`.
    Registry now has 60 entries total.
- **§5 LC document pipeline (chemistry pilot) — MAJOR UPDATE.** A prior session
  (same day, ~01:23–02:29 local time, ~17-18h before this discovery) had **already
  built Phase 2b, 2c, and 2d as untracked files**, sitting uncommitted in the working
  tree the whole time. This was missed by this session's initial plan-mode
  exploration (which only checked `docs/plans/`, the openspec change, and
  `opencode.json` — not these specific filenames) and only surfaced when the Phase
  2b subagent grepped for existing cross-check code before writing its own. **Do not
  rebuild any of this — it already exists, verify/finish it instead:**
  - `dlt_sources/filesystem/lc6_cross_check.py` — the Phase 2b orchestration helper.
    `extract_with_cross_check(text, subject, language, source_pdf, baml_function)` →
    `CrossCheckResult`. Uses `baml_options={"client": "ExtractQwenCrossCheck"}`
    per-call (confirmed a supported key in generated `BamlCallOptions`) rather than
    duplicating `.baml` functions — correct pattern, no BAML regen needed.
  - `scripts/load_lc_chemistry_pilot.py` — the Phase 2c loader (see below).
  - `orchestration/defs/2_materials/lc_extraction/lc_chemistry_pilot_assets.py` —
    the Phase 2d Dagster assets (see below), additive, doesn't touch
    `lc5_assets.py` or `generic_ireland_assets.py`.
  - All three correctly follow this doc's already-made architectural decisions
    (2-path not 4-path ensemble, additive not retargeted, secret hygiene via
    `os.environ.setdefault` for non-secret endpoint defaults only, never touching
    `*_API_KEY`).

  Phase 2a result (confirmed, not guessed):
  - `dlt_sources/filesystem/leaving_cert_source.py`: added `select_ocr_backend()`,
    `_llama_swap_qwen_healthy()` (GETs `http://localhost:8086/health`, the standard
    llama.cpp health endpoint — no bespoke convention existed to reuse), and
    `_minimax_multimodal_fallback()` (live POST to `MINIMAX_BASE_URL`, model
    `MiniMax-M3`). Backend resolution wired into `_row()` (new `resolved_backend`/
    `backend_reason` columns). Added `subjects` param to `lc5_documents()` for
    scoped dev runs.
  - `subjects/chemistry/sources.py` and `schema.py`: deprecation docstrings added
    (schema.py's broken `{prefix}...` import block left untouched, as instructed).
    Grep confirmed **zero live importers outside the package's own `__init__.py`**
    (`sources.py` is imported by `subjects/chemistry/__init__.py`; `schema.py` has
    zero importers anywhere, fully dead code) — safe to deprecate in place, nothing
    was flagged/stopped for.
  - **Dev-mode run confirmed real, live results**: all 16 chemistry files processed,
    zero Docker/llama-swap required. Backend counts: `glm-4.6v-flash`=8 (all `ga/`
    files — `_classify_pdf()` short-circuits to this backend on `language=="ga"`,
    pre-existing behavior, unchanged), `gemma-4-26B-A4B`=4, `minimax-m3`=2 (the
    fallback — both were the English exam papers, llama-swap correctly detected as
    down on :8086, MiniMax fallback call succeeded live with real API replies,
    logged `minimax_fallback_ok`), `molmo2-8b`=2.
  - **Notable finding to carry forward**: because Irish-variant (`ga`) files always
    route to `glm-4.6v-flash` regardless of doc type, only the 2 English exam papers
    ever exercise the qwen3-vl-8b→MiniMax fallback path. Not a bug introduced this
    session — just worth knowing when interpreting Phase 2b/2c output.
  - Used `.venv/bin/python3` directly for the dev run (not `uv run`) — same
    `dagster-components` `uv` resolution conflict noted under Phase 1, pre-existing,
    unrelated to this change.
  - Confirmed: not a dlthub-managed workspace for this pipeline (`.dlt/` at repo root
    only has the AI toolkit registry, no `config.toml`/`secrets.toml`/profiles) — the
    file's existing `main()` pattern (direct `dlt.pipeline(..., destination=
    dlt.destinations.duckdb(...))`) was used as-is, no profile switching needed.

  **Phase 2b — VERIFIED LIVE THIS SESSION (code pre-existed, not written by us):**
  - MiniMax primary: **confirmed working with real API calls** — `ExtractChemSyllabus`
    on the EN syllabus PDF (79 pages, 118s) → `topic_count=13,
    learning_outcome_count=53, level=LC_HL`; `ExtractLC6Syllabus` on the guideline
    PDF also succeeded.
  - Qwen secondary: fails cleanly with `LLM client 'ExtractQwenCrossCheck' requires
    environment variable 'DASHSCOPE_API_KEY'...` — caught, `status="secondary_failed"`,
    logged via `structlog` warning, no crash. Expected, unchanged blocker.
  - **Two NEW blockers found for Langfuse disagreement logging** (separate from
    DASHSCOPE_API_KEY, don't conflate):
    1. Local Langfuse (`http://localhost:3000`) is not running — `curl` gets
       connection refused.
    2. `observability/langfuse_config.py` (shared repo-wide wrapper, **not part of
       this openspec change**, pre-existing) calls Langfuse SDK v3-style methods
       (`client.trace()`, `trace.span()`, `client.score(trace_id=...)`) that don't
       exist on the installed `langfuse==4.14.1` (v4 uses
       `start_as_current_observation`/`create_score`). Confirmed via
       `AttributeError: 'Langfuse' object has no attribute 'trace'`, caught,
       degrades to a warning (never raises/crashes the pipeline — by design). Even
       once local Langfuse is up, disagreement logging won't actually deliver until
       this wrapper is updated to the v4 API. **This is a real bug worth a separate
       fix, out of scope for this openspec change** (shared file, no task in
       tasks.md §5 asks for it) — flag to the user, don't fix it as part of this plan
       unless asked.
    3. Confirmed `LANGFUSE_HOST` env var IS correctly honored by
       `observability/env_config.py:118-120` — wiring is correct, only delivery is
       blocked.
  - `lc_chem_pilot_cross_checked`'s Dagster asset design deliberately degrades to
    stub statuses (never raises) when BAML/API keys are unavailable — this is
    intentional, not a bug to fix.

  **Phase 2c/2d — code exists, being live-verified now** (see "What's left").

- **§6 broader backlog, §7 archive gate** — explicitly out of scope this session.

## Architectural decisions already made (do not re-litigate — follow these)

Four separate, overlapping implementations touch LC chemistry ingestion. Consolidate
on **`dlt_sources/filesystem/leaving_cert_source.py`** as canonical (reads the real
local corpus at `leaving_certificate/<subject>/{en,ga}/`, already covers chemistry,
already has an OCR-backend-selection heuristic — matches tasks.md §5 literally).
- Deprecate (docstring only, don't delete)
  `dlt_sources/british_isles/ireland/education/subjects/chemistry/{sources.py,schema.py}`
  in place — `schema.py` is actively broken (unfilled template literal, will
  SyntaxError on import) and self-marked deprecated already. Only do this after
  confirming nothing else imports `sources.py`'s `chem_source()` — if something does,
  that's a decision point for a human, not something to silently rewire.
- Leave `dlt_sources/british_isles/ireland/education/leaving_cert.py`,
  `ireland_jurisdiction_pipeline.py`, and
  `orchestration/defs/2_materials/ireland_education/generic_ireland_assets.py`'s
  existing chemistry asset **untouched** — those are scrape-cache-sourced and out of
  scope; Dagster work for this pilot is a **separate, additive** asset group, not a
  retarget of the existing one.
- OCR: `qwen3-vl-8b` via llama-swap (port 8086) is configured but not running (no
  Docker access, no GGUF weights downloaded in this environment). Cannot be fixed by
  an agent here — needs a different machine with Docker+GPU. Mitigation: health-check
  port 8086, fall back to a **direct MiniMax-M3 multimodal call** (confirmed
  TLS-healthy, `MINIMAX_API_KEY`/`MINIMAX_BASE_URL` are present/hydrated in this
  session's shell — this specific fallback path IS live-testable, unlike DashScope).

## What's left (in dependency order)

Phase 2a is confirmed complete. Phase 2b's code was found pre-existing and verified
live (MiniMax path confirmed working, Qwen path confirmed correctly blocked). **Do
NOT rewrite 2a/2b.** Phase 2c/2d code also already exists (pre-existing, untracked,
same prior-session origin) — the remaining work is verification/finishing, not
building from scratch:

1. **Confirm Phase 2c's live run.** `scripts/load_lc_chemistry_pilot.py` was
   launched in the background at the end of this session (`.venv/bin/python3
   scripts/load_lc_chemistry_pilot.py`, ~6 min expected runtime, `MOTHERDUCK_TOKEN`
   confirmed present so a real `md:cianfhoghlaim` write was attempted). **Check
   whether it completed and what it reported** before assuming success or restarting
   it — look for `=== LC chemistry pilot load summary ===` in its output, expected
   tables `cianfhoghlaim.leaving_cert.chemistry_pilot_documents` (16 rows) and
   `...chemistry_pilot_cross_check` (3 rows, with the Qwen secondary fields blank/
   error'd as expected). If it didn't finish or wasn't checked, re-run it directly
   (it's self-contained, `--skip-extraction` flag available for an LLM-free re-run
   once the tables exist once already).
2. **Materialize/verify Phase 2d's Dagster assets**
   (`orchestration/defs/2_materials/lc_extraction/lc_chemistry_pilot_assets.py`,
   auto-discovered by `dg.load_defs()`, purely additive — 3 assets +
   `lc_chem_pilot_documents_check`). This has not been materialized/tested by any
   agent yet — do that next (`dg materialize` or the repo's normal Dagster dev-run
   command; check `mise.toml` for the right invocation). `lc_chem_pilot_loaded`
   shells out to the same `load_lc_chemistry_pilot.py` from step 1 as a subprocess
   (6 min timeout, 1800s), so this step re-exercises step 1's path via Dagster.
3. **Two new, real bugs surfaced this session, separate from the DASHSCOPE_API_KEY
   blocker — flag to the user, do not silently fix unless asked (out of this
   openspec change's scope):**
   - Local Langfuse (`http://localhost:3000`) is not running, so disagreement
     logging has nowhere to deliver to.
   - `observability/langfuse_config.py` (shared, repo-wide, not part of this
     change) calls Langfuse SDK v3-style methods (`.trace()`, `.span()`,
     `.score(trace_id=...)`) incompatible with the installed `langfuse==4.14.1`
     (v4 API is `start_as_current_observation`/`create_score`). Degrades to a
     warning, never crashes — but disagreement logging will never actually land
     until this is fixed, independent of whether local Langfuse is up.
4. **Update `tasks.md`** in the openspec change to check off what's actually done
   (§4 fully done; §5: 2a/2b done+verified, 2c pending final confirmation, 2d
   pending materialization). Do not run `openspec archive` — §6/§7 are still out
   of scope.
5. **Other side findings worth flagging to the user** (not blocking, not in
   original plan scope): the `cianfhoghlaim-cli.ts` `secrets` subcommand is
   documented but unimplemented; `uv run` fails repo-wide on a pre-existing
   `dagster-components` dependency conflict (use `.venv/bin/...` directly, as done
   throughout this session); Irish-variant (`ga`) LC files never exercise the
   qwen3-vl-8b/MiniMax OCR fallback path since `_classify_pdf()` short-circuits
   them to `glm-4.6v-flash` regardless of doc type; the Langfuse SDK v3/v4
   incompatibility above.

## Hard constraints (still apply to whoever continues)

- Never read `*.secrets.toml` or print any secret value. Env-presence checks only
  (`env | grep -c '^VAR='`), never the value.
- Never fabricate/substitute a `DASHSCOPE_API_KEY`. That's a real user action.
- Don't attempt `mise run cianfhoghlaim:secrets:hydrate` or `locket exec` again
  without first confirming `INFISICAL_CLIENT_ID`/`INFISICAL_CLIENT_SECRET` are
  actually present in the new session's shell — confirmed absent in this session,
  may or may not be present elsewhere.
- Don't touch arm1-oci/Traefik/litellm/langfuse infra (§3, out of scope).
- Don't retarget `generic_ireland_assets.py` or the two scrape-cache-sourced
  pipelines to the local corpus — that's broader-backlog work (§6), out of scope.

---

## Ready-to-paste prompt for the next coding agent

```
Continue the Leaving Certificate chemistry pilot for the token-plan-apis openspec
change in this repo. Read
docs/plans/2026-08-06-token-plan-progress-and-handoff.md FIRST — it has full context,
confirmed diagnosis, architectural decisions already made, and hard constraints.

IMPORTANT: Phase 1 (registry/BAML plumbing), Phase 2a (chemistry DLT source), and
Phase 2b (Qwen cross-check helper + Langfuse logging) are ALL ALREADY DONE — Phase
2b's code was even found pre-existing (written by an earlier session on the same
day) and only needed live verification, not writing. Do NOT rewrite any of
dlt_sources/filesystem/leaving_cert_source.py's OCR-backend logic,
dlt_sources/filesystem/lc6_cross_check.py, baml_src/clients.baml, or
meaisinfhoghlaim/models/model_registry.py. Phase 2c (scripts/load_lc_chemistry_pilot.py)
and Phase 2d (orchestration/defs/2_materials/lc_extraction/lc_chemistry_pilot_assets.py)
ALSO already exist as code from that same earlier session — your job is to verify/
finish them, not build them from scratch. Just execute the "What's left" section:

1. Check whether the background run of `scripts/load_lc_chemistry_pilot.py` from
   the end of the prior session completed and succeeded (look for its output/logs
   first; MOTHERDUCK_TOKEN was confirmed present so it should have been a real
   write attempt to md:cianfhoghlaim). If it didn't finish cleanly, re-run it
   directly with `.venv/bin/python3 scripts/load_lc_chemistry_pilot.py` (`uv run`
   fails repo-wide on a pre-existing dagster-components conflict, unrelated to
   this change — use the .venv binary directly).
2. Materialize/verify the Phase 2d Dagster assets in
   orchestration/defs/2_materials/lc_extraction/lc_chemistry_pilot_assets.py (3
   assets + 1 asset_check, auto-discovered, purely additive — do not modify
   lc5_assets.py or generic_ireland_assets.py). Find this repo's normal Dagster
   materialize/dev-run command (check mise.toml) rather than inventing one.
3. Flag to the user, don't silently fix (out of this change's scope unless asked):
   local Langfuse (http://localhost:3000) isn't running, so disagreement logging
   has nowhere to deliver; and observability/langfuse_config.py (shared, unrelated
   file) calls Langfuse SDK v3-style methods incompatible with the installed
   langfuse==4.14.1 v4 SDK -- confirmed via AttributeError, degrades to a warning,
   never crashes, but means disagreement logging never actually lands regardless of
   whether local Langfuse comes up.
4. Update tasks.md in
   openspec/changes/2026-08-06-token-plan-apis-lc-doc-pipeline-and-edge-tls-remediation-v1/
   to reflect what's actually done (§4 fully done; §5: 2a/2b done+verified, 2c/2d
   per your run's outcome). Do not run openspec archive -- §6/§7 stay out of scope.

Hard constraints: never read *.secrets.toml or print secret values (env-presence
checks only); never fabricate a DASHSCOPE_API_KEY; don't touch arm1-oci/Traefik
infra or the two scrape-cache-sourced LC pipelines
(leaving_cert.py/ireland_jurisdiction_pipeline.py) or
generic_ireland_assets.py's existing chemistry asset. Report back clearly what was
done, what's blocked, and why.
```
