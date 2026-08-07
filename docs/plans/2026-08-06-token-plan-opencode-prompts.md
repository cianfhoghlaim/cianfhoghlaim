# Token-Plan Opencode Prompt Pack (MiniMax + Qwen)

Shipped by openspec change
`2026-08-06-token-plan-apis-lc-doc-pipeline-and-edge-tls-remediation-v1`.

These prompts are written to be pasted directly into **opencode** sessions in
this repo. The `build`, `plan`, `orchestrator`, and the 5 functional
subagents all resolve their model via the `minimax/MiniMax-M3` provider
(direct `https://api.minimax.io/anthropic`) and — for cross-checking and
load-spreading — the `qwen/qwen3.7-plus` provider
(`{env:DASHSCOPE_BASE_URL}`). The `litellm_local` provider
(`http://localhost:4000/v1`) is the gateway fallback.

> **Pre-flight for every session:** confirm `MINIMAX_API_KEY` and
> `DASHSCOPE_API_KEY` are hydrated (names only — never print values), and
> that `bash scripts/check-edge-tls.sh` still reports the edge status. If a
> prompt touches the arm1-oci edge, run `mise run preflight-arm-oci` first.

---

## Plan benefits (why these two plans carry the backlog)

**MiniMax coding plan (MiniMax-M3)**
- Frontier coding/agentic model on MSA sparse attention; **1M-token
  context** — whole syllabi, full exam-paper bundles, or the entire pending
  openspec backlog fit in one context window.
- Native multimodality — can read the LC PDF rasters directly when the
  local OCR path is uncertain.
- Flat-rate token plan: long agentic sessions (orchestrator runs, multi-file
  refactors) do not burn per-token budget.
- Direct endpoints: `https://api.minimax.io/anthropic` (Anthropic-compatible,
  used by the opencode `minimax` provider) + `https://api.minimax.io/v1`
  (OpenAI-compatible, used by the BAML `minimax-m3` clients).

**Qwen token plan (Qwen Cloud, served via the DashScope API platform)**
- One plan, many models: `qwen3.7-plus` (flagship), `qwen3-coder-next` +
  `qwen3-coder-plus` (coding specialists), `qwen3-max-2026-01-23`, plus
  third-party `glm-5`, `kimi-k2.5`, `MiniMax-M2.5` under the same
  subscription.
- Strong multilingual (EN + GA) text extraction — ideal as the secondary
  cross-check client for the bilingual Leaving Certificate corpus.
- Endpoint is switchable via `DASHSCOPE_BASE_URL`:
  `https://coding.dashscope.aliyuncs.com/v1` (coding plan, verified live
  2026-08-06) or `https://dashscope-intl.aliyuncs.com/compatible-mode/v1`
  (international console). Anthropic-compatible path at
  `https://coding.dashscope.aliyuncs.com/apps/anthropic`.

**Routing policy:** MiniMax-M3 = primary (build/plan/orchestrator + BAML
default). Qwen3.7-plus = secondary cross-check + load-spreading for batch
extraction. `litellm_local` = fallback when a direct token-plan endpoint is
unavailable. Public edge (`litellm.cianfhoghlaim.ie`) = NOT used until
`scripts/check-edge-tls.sh --strict` exits 0.

---

## P0 — Smoke-test the token-plan wiring (run first, ~2 min)

```
You are the build agent. Verify the token-plan wiring landed by openspec
change 2026-08-06-token-plan-apis-lc-doc-pipeline-and-edge-tls-remediation-v1:

1. Confirm opencode.json parses (jq . opencode.json) and has 4 providers:
   minimax (baseURL https://api.minimax.io/anthropic), qwen (baseURL
   {env:DASHSCOPE_BASE_URL}), litellm_local (http://localhost:4000/v1),
   opencode_go.
2. Confirm .env hydrates MINIMAX_API_KEY, DASHSCOPE_API_KEY,
   DASHSCOPE_BASE_URL, MINIMAX_BASE_URL (print names + lengths only, never
   values). If DASHSCOPE_API_KEY is missing, stop and tell me to run tasks
   2.1–2.3 of the change.
3. Run `bash scripts/check-edge-tls.sh` and report the status of the 3
   priority domains.
4. Send one 10-token chat completion to MiniMax-M3 (via
   https://api.minimax.io/v1/chat/completions, model minimax-m3) and one to
   qwen3.7-plus (via $DASHSCOPE_BASE_URL/chat/completions) using curl with
   the env keys; report HTTP status + latency for each. Do NOT print the
   keys.
5. Report a 5-line summary: minimax=OK/FAIL, qwen=OK/FAIL, edge=OK/FAIL,
   litellm_local reachable yes/no, langfuse localhost reachable yes/no.
```

## P1 — Execute the edge TLS remediation (orchestrator)

```
You are the orchestrator agent. Execute openspec change
2026-08-06-token-plan-apis-lc-doc-pipeline-and-edge-tls-remediation-v1,
phases 3 (edge TLS remediation) and 4 (registry registration) only.

1. openspec show 2026-08-06-token-plan-apis-lc-doc-pipeline-and-edge-tls-remediation-v1
   — re-read proposal + tasks.
2. Run `mise run preflight-arm-oci` and stop if it fails.
3. Walk tasks 3.1–3.7 in order. For 3.2/3.3, produce the exact commands I
   must run on arm1-oci (you cannot SSH from here): inspect
   /opt/pangolin/config/traefik/traefik_config.yml for the
   certificatesResolvers name, diff it against the `certResolver: letsencrypt`
   used by the 7 pangolin.yaml files (cianfhoghlaim, cognee, hermes,
   langfuse, litellm, openchamber, openclaw), and check
   CLOUDFLARE_DNS_API_TOKEN in /opt/pangolin/.env.
4. When I confirm the arm1-oci steps are done, run
   `bash scripts/check-edge-tls.sh --strict --all`. Only if it exits 0,
   proceed with task 3.7 (restoration of the edge URLs) — otherwise keep
   the localhost-first fallback.
5. Then tasks 4.1–4.4: add the token-plan endpoint metadata to
   meaisinfhoghlaim/models/model_registry.py (minimax-m3 endpoints +
   qwen3.7-plus/qwen3-coder-next entries), add the qwen BAML client to
   baml_src/clients.baml, run `mise run cic:baml:generate`,
   `mise run cic:baml:test`, and `mise run lint:registry`.
6. Quality gates: mise run lint && mise run py:typecheck && mise run turbo typecheck.
7. Update tasks.md checkboxes and report what changed.
```

## P2 — Process the Leaving Certificate documents (data-platform)

```
You are the data-platform subagent. Implement phase 5 of openspec change
2026-08-06-token-plan-apis-lc-doc-pipeline-and-edge-tls-remediation-v1 —
the Leaving Certificate corpus through the BIEP v3 5-phase pattern.

Corpus: leaving_certificate/ — 13 subjects (applied_mathematics, biology,
business, chemistry, computer_science, english, french, gaeilge, geography,
history, mathematics, technology, ukrainian), each with en/ + ga/ PDFs
(syllabi SCSEC09_*, specifications SC-*-Specification-*, guideline
material, exam papers LC022*).

1. Ingestion: create the DLT filesystem source at
   dlt/british_isles/ireland/education/leaving_certificate/ over
   leaving_certificate/<subject>/<lang>/. Files are local — set
   os.environ['USE_LOCAL_SCRAPES'] = 'true'; never live-scrape.
2. OCR: route rasters through the local llama-swap qwen3-vl-8b alias first
   (see meaisinfhoghlaim/models/llama_swap_config.yaml); pages below the
   confidence threshold go to the MiniMax-M3 multimodal endpoint.
3. Extraction: run the lc6 BAML functions (ExtractCurriculumSyllabus,
   ExtractExamPaperLayout, ExtractMarkingSchemeGuideline,
   ExtractCrossLinguisticConcept) with minimax-m3 primary and the new qwen
   client (qwen3.7-plus) secondary; log disagreements to Langfuse at
   $LANGFUSE_HOST (localhost:3000).
4. Load: DuckLake tables cianfhoghlaim.leaving_cert.<subject> via
   dlt.common.destinations_cianfhoghlaim.get_dlt_destination(use_ducklake=True).
5. Orchestration: add the LC assets to orchestration/defs/2_materials/
   following the per-cohort 5-phase pattern; wire ocr_completion_sensor.
6. Start with chemistry (en + ga) as the pilot subject; report row counts
   and one sample ExtractCurriculumSyllabus output before fanning out to
   the other 12 subjects.
7. Verify with schema_introspect: the new tables MUST appear. Quality
   gates: mise run lint && mise run py:typecheck.
```

## P3 — Priority openspec backlog + ongoing changes (orchestrator)

```
You are the orchestrator agent. Work the priority openspec backlog using
the token-plan capacity (MiniMax-M3 primary; dispatch parallel subagents
on qwen/qwen3.7-plus where independent).

1. `openspec list` — enumerate pending changes. Currently:
   - 2026-08-15-meaisinfhoghlaim-to-machine-learning-rename-v1 (No tasks)
   - 2026-08-06-token-plan-apis-lc-doc-pipeline-and-edge-tls-remediation-v1
2. For the rename change: author its missing tasks.md (read the proposal,
   enumerate every meaisinfhoghlaim → machine-learning path/config/doc
   reference via ccc search, produce an ordered task list with a quality
   gate per phase), then `openspec validate
   2026-08-15-meaisinfhoghlaim-to-machine-learning-rename-v1 --strict`.
   Do NOT implement it yet — hand back to me for approval.
3. For the token-plan change: continue any incomplete phases from P1/P2.
4. Cross-check the 4 priority specs from AGENTS.md (centralized-model-registry,
   centralized-schema-registry, deployment-control-panel, and the openspec
   capability list) for requirements not yet covered by a pending change;
   list the top 3 candidates for the NEXT change, each with a one-paragraph
   proposal sketch.
5. Respect the Dependencies rule: a change cannot archive until its
   blockers archive. Report the dependency graph of everything pending.
```

## P4 — Registry drift + hardcoded-model audit (build)

```
You are the build agent. Run the centralized-registry hygiene loop:

1. mise run lint:registry — detect hardcoded model strings bypassing
   MODEL_REGISTRY. Triage every finding: is it a legitimate registry gap
   (add the entry) or drift (route through model_for)?
2. Confirm the new token-plan entries (minimax-m3 endpoint metadata,
   qwen3.7-plus, qwen3-coder-next) resolve:
   python -c "from meaisinfhoghlaim.models import model_for; print(model_for('text_llm','default'), model_for('text_llm','token_plan_primary'))"
3. Check notebooks/00_control_panel.py (deployment control panel) shows the
   token-plan models in the Models tab; if deployment-choice.yaml lacks a
   token-plan section, draft the addition (do not enable anything).
4. mise run lint && mise run py:typecheck. Report findings + fixes.
```

## P5 — 1M-context deep pass over the LC corpus (build, MiniMax-M3)

```
You are the build agent on minimax/MiniMax-M3 (1M context). Perform the
deep-context pass that only the token plan makes economical:

1. Load the full chemistry EN + GA syllabus text (post-OCR) into context
   in one window, together with ExtractCurriculumSyllabus outputs for both
   languages.
2. Produce the EN↔GA concept-alignment table (concept key, EN term, GA
   term, syllabus section ref) and diff it against
   bilingual_concept_registry.py — list gaps.
3. Identify every exam-paper question in LC022ALP000EV / LC022GLP000EV
   that maps to a syllabus learning outcome; report coverage % and the
   unmapped questions.
4. Write the findings to
   stedding/sync-reports/lc-chemistry-deep-pass-$(date +%F).md and propose
   3 follow-up BAML test blocks (lowercase `test`) that lock the alignment.
```

## P6 — Observability + scheduled freshness (data-platform)

```
You are the data-platform subagent. Close the loop on the LC pipeline:

1. Confirm Langfuse traces for the chemistry extraction land at
   http://localhost:3000 (LANGFUSE_HOST). If the stack is down, start it
   via the lakehouse-critical-path order in bonneagar/AGENTS.md — never
   via the broken public edge.
2. Add a Dagster schedule (AutomationCondition.cron) for the LC cohort:
   weekly re-ingest of leaving_certificate/ to pick up newly published
   NCCA documents, per the BIEP v3 4-cadence scheduling policy.
3. Wire the change-detection skill's 4th layer (Firecrawl monitor) ONLY
   for the NCCA/gov.ie surfaces that publish LC updates — and only after
   USE_LOCAL_SCRAPES is confirmed for the test run.
4. Report: schedule name, next tick, and the Langfuse project link
   (localhost).
```

---

## Session hygiene (all prompts)

- Never write secrets to disk; `.env` is hydrated by mise + Infisical.
- For any live scrape, set `USE_LOCAL_SCRAPES=true` first.
- After code changes: `mise run lint && mise run py:typecheck &&
  mise run turbo typecheck`.
- Openspec loop: `list → proposal/tasks/deltas → validate --strict →
  implement → archive`. Commit/push only when the user explicitly asks.
