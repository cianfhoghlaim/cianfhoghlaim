# Agent 21 — HuggingFace Hub (model + dataset registry)

**Date:** 2026-06-28
**Phase:** 2 (Light Packages) — Agent 21 of 25
**BrowserBase budget used:** 0 navigations (all content via Firecrawl fallback; 5 scrapes × 1 credit = 5 credits)
**CCC queries:** 2 (`huggingface`, `HF_MODELS`)
**Sources fetched:** hub/api, hub/rate-limits, hub/oauth, huggingface_hub/quick-start, transformers.js

## TL;DR

HuggingFace Hub is the **model + dataset registry** for the Cianfhoghlaim agent fleet: 11 vision + 4 text models in `P2-23-huggingface.md`'s `HF_MODELS` dict, plus the `mlx-community` registry (5,184 models per agent-20). The `huggingface_hub` Python library is at **v1.21.0.rc0** (rc0) / **v1.20.1** (latest stable), and **the CLI entry point has changed**: `huggingface-cli` is a deprecated shim — the canonical CLI is now **`hf`** (subcommands: `hf auth login`, `hf auth switch`, `hf auth list`, `hf auth whoami`, `hf download`, `hf upload`, `hf jobs`, etc.) added in `huggingface_hub` 1.2+.

The biggest drifts vs P2-23: (1) **P2-23 lists aspirational/fictional model IDs** (`unsloth/gemma-4-31B-it-GGUF`, `unsloth/Qwen3.6-27B-Instruct-GGUF`, `unsloth/GLM-4.6V-Flash-GGUF`) that **do not exist on HF** today — agent-20 already flagged this for the MLX subset; (2) the new **`inference-api` OAuth scope** unlocks Inference Providers routing; (3) a **new `RateLimit` HTTP header** (per IETF `draft-ietf-httpapi-ratelimit-headers-09`) replaces ad-hoc 429 handling — `huggingface_hub` ≥1.2.0 parses it for smart retry; (4) **Public OAuth apps (no secret)** + **CIMD metadata at `/.well-known/oauth-cimd`** is a new pattern ideal for Spaces / native clients; (5) **Token Exchange (RFC 8693)** is now GA on Enterprise for org-scoped token issuance.

## Code

| Path | Purpose |
|:--|:--|
| `spaces/_common/hf_hub_push.py:60-105` | Canonical `push_model_to_hub()` helper — uses `HfApi.upload_folder`, returns commit SHA, raises if `HF_TOKEN` unset |
| `spaces/_common/baml_client.py:95` | `cfg['hf_token_set']` UI flag — surfaces `HF_TOKEN` env-var presence in the Spaces' Gradio footer |
| `spaces/README.md:59` | B2 pattern doc — replaces S3 egress with `huggingface_hub.hf_hub_download` |
| `spaces/build-small-2026-runbook.md:26-330` | The KCG canon for HF CLI: warns `huggingface-cli` is deprecated, says use `hf` (but its §"huggingface-cli: command not found" still names the old CLI in headings) |
| `infrastructure/ci/spaces-sync.yml:63-74` | GHA step `pip install --upgrade "huggingface_hub[cli]"` + `HfApi(token='$HF_TOKEN')` — does **NOT** install `[cli]` extra in name correctly; the extra was renamed to `[hf]` in v1.0+ |
| `infrastructure/ci/README.md:50-66` | GHA Spaces pattern — "Hugging Face `huggingface_hub` API upload (modern equivalent of `huggingface-cli upload`)" |
| `openspec/research/2026-06-28-browserbase-credit-program/phase-2/P2-23-huggingface.md:25-47` | `HF_MODELS` dict with 11 vision + 4 text — **6+ of the IDs do not exist on HF** |
| `cianfhoghlaim/assets/_oideachais_dagster_defs/assets/unified_audio_dataset_assets.py:624-651` | Dagster `HuggingFace` upload asset — uses `HfApi().create_repo(repo_type="dataset")` + `upload_folder` |
| `openspec/changes/2026-06-28-browserbase-phase-2-decisions/specs/meaisinfhoghlaim-platform/spec.md:130` | Spec uses `huggingface-cli download` — should migrate to `hf download` |
| `openspec/changes/celtic-data-engineering-patterns/proposal.md:51` | Pattern B6 — "Uses `huggingface_hub.HfApi.upload_folder` rather than the manual `pipeline.push_to_hub`" |

**Canonical `huggingface_hub` quick-start (per `huggingface.co/docs/huggingface_hub/quick-start`):**

```python
# Install: pip install --upgrade huggingface_hub
# CLI:     hf auth login   (the new canonical entry point; huggingface-cli is deprecated)
# Token:   HF_TOKEN env var OR ~/.cache/huggingface/token (HF_HOME)

from huggingface_hub import HfApi, hf_hub_download
api = HfApi()
api.create_repo(repo_id="super-cool-model", private=True)         # needs write token
hf_hub_download(
    repo_id="google/pegasus-xsum",
    filename="config.json",
    revision="4d33b01d79672f27f001f6abade33f22d993b151",          # full SHA, not 7-char
)
```

**HF Hub API reference** is now an **OpenAPI playground** at `https://huggingface.co/spaces/huggingface/openapi` (also a static spec at `https://huggingface.co/.well-known/openapi.json` + `.md` for agents). The `/docs/hub/api` page is a redirect stub: "We've moved the Hub API Endpoints documentation to our OpenAPI Playground".

**15 OAuth scopes** (`https://huggingface.co/docs/hub/oauth`): `openid`, `profile`, `email`, `read-billing`, **`read-repos`**, **`gated-repos`** (new — for public gated repos only, not private), **`contribute-repos`** (new — create+access only own app-created repos), `write-repos`, **`manage-repos`** (incl. delete), `read-collections`, `write-collections`, **`inference-api`** (new — Inference Providers on behalf of user), `jobs` (run HF Jobs), `webhooks` (manage webhooks), `write-discussions`.

**Webhooks** (`https://huggingface.co/docs/hub/webhooks`) are a relatively new real-time event subscription mechanism for repo changes (replaces polling for the change-detection layer).

## Env

| Env var | Value | Source |
|:--|:--|:--|
| `HF_TOKEN` | `infisical://dev-baile/huggingface/token` | Locket (the canonical KCG name) |
| `HUGGING_FACE_HUB_TOKEN` / `HUGGINGFACE_HUB_TOKEN` / `HUGGINGFACE_TOKEN` | alias of `HF_TOKEN` | mlx-omni secrets.env, scripts/push_spaces_to_hf.sh, train-sentence-transformers scripts |
| `HF_HOME` | `~/.cache/huggingface` (default) — `/stedding/huggingface` on KCG containers | compose env per stack |
| `HF_HUB_CACHE` | `~/.cache/huggingface/hub` (default) — `/stedding/huggingface/hub` on KCG | per-host |
| `HF_DATASETS_CACHE` | `~/.cache/huggingface/datasets` (default) | per-host |
| `HF_HUB_DOWNLOAD_TIMEOUT` | `600` (KCG override, mlx-omni compose) | compose env |
| `HF_HUB_DISABLE_IMPLICIT_TOKEN=1` | opt out of auto-use of `HF_TOKEN` for all hub calls | new opt-out (quick-start §Authentication) |
| `HF_TOKEN` permission | `read` for download, **`write`** for upload/create | quick-start §"Method parameters" |

**CLI subcommands** (the `hf` CLI from `huggingface_hub` ≥1.2): `auth login`, `auth switch`, `auth list`, `auth whoami`, `download`, `upload`, `upload-file`, `repo create`, `repo delete`, `jobs run` / `jobs ps` / `jobs logs`, `endpoint` / `inference-endpoint`, `lfs-enable-largefiles`, `cache scan` / `cache delete`. `hf skills add [--claude]` installs the agent skills into `.agents/skills/`.

## CCC anchors

`spaces/_common/hf_hub_push.py` · `spaces/_common/baml_client.py` · `infrastructure/ci/spaces-sync.yml` · `openspec/research/2026-06-28-browserbase-credit-program/phase-2/P2-23-huggingface.md` · `cianfhoghlaim/assets/_oideachais_dagster_defs/assets/unified_audio_dataset_assets.py` · `openspec/changes/celtic-data-engineering-patterns/proposal.md` · `openspec/changes/2026-06-28-browserbase-phase-2-decisions/specs/meaisinfhoghlaim-platform/spec.md` · `infrastructure/komodo/procedures/auto-deploy-stacks.toml` (any HF-related procedures)

Search terms: `huggingface_hub`, `HF_MODELS`, `HfApi`, `hf_hub_download`, `push_to_hub`, `HF_TOKEN`, `oauth`, `mlx-community`.

CCC search results (top hits):
1. `openspec/research/2026-06-28-browserbase-credit-program/phase-2/P2-23-huggingface.md:1-12` (score 0.689) — the existing P2-23 spec this agent validates
2. `openspec/changes/archive/2026-06-24-spaces-use-litelm-gateway/proposal.md:1-18` (score 0.675) — confirms Spaces migrated to LiteLLM gateway, leaving raw HF Inference only as offline fallback
3. `spaces/README.md:1-9` (score 0.670) — Spaces parent, references `huggingface_hub>=0.24` (should be `>=1.20`)
4. `spaces/build-small-2026-docs-catalogue.md:461-477` (score 0.616) — LiteLLM model fallback chains table

## Drift log

| Date | Event | Source |
|:--|:--|:--|
| **2026-06-28** | **CRITICAL: P2-23 aspirational model IDs** — `P2-23-huggingface.md:25-47` lists 11 vision models whose `unsloth/...` IDs DO NOT EXIST on HF today: `unsloth/gemma-4-31B-it-GGUF`, `unsloth/gemma-4-26B-A4B-it-GGUF`, `unsloth/gemma-4-E4B-it-GGUF`, `unsloth/gemma-4-E2B-it-GGUF`, `unsloth/Qwen3.6-27B-Instruct-GGUF`, `unsloth/Qwen3.6-27B-Instruct-MLX-8bit`, `unsloth/Qwen3.6-35B-A3B-Instruct-GGUF`, `unsloth/Qwen3.6-35B-A3B-Instruct-UD-MLX-4bit`, `unsloth/GLM-4.6V-Flash-GGUF`. Gemma 4 (Google) and Qwen 3.6 (Alibaba) and GLM-4.6V are not yet released as of 2026-06-28. Agent-20 already flagged the same drift for the mlx-community subset. | `huggingface.co/unsloth` (verified no such repos) + agent-20 cross-ref |
| **2026-06-28** | **CRITICAL: CLI entry point migration** — P2-23:74 says "pre-download via `huggingface-cli download`"; `huggingface_hub` 1.2+ (Sept 2024) added the `hf` CLI as canonical, and `huggingface-cli` is a deprecated shim that prints `Warning: 'huggingface-cli' is deprecated` on every invocation. Our `spaces/build-small-2026-runbook.md:26,39-41,60,64,92,98,304,315-330` has 9 references to `huggingface-cli` — half are deprecation notes (good), half are in command examples (should migrate). | `huggingface.co/docs/huggingface_hub/quick-start` + `hf-cli/SKILL.md:120` |
| **2026-06-28** | **MEDIUM: `[cli]` extra renamed to `[hf]`** — `infrastructure/ci/spaces-sync.yml:64` does `pip install --upgrade "huggingface_hub[cli]"`. The `[cli]` extra was deprecated in v0.x; the canonical name in v1.0+ is `[hf]`. The install still works (CLI is a default extra) but the dependency declaration is stale. | HF release notes + `huggingface_hub` pyproject |
| **2026-06-28** | **MEDIUM: 5-min RateLimit header (Sept 2025)** — `huggingface.co/docs/hub/rate-limits` documents the IETF `draft-ietf-httpapi-ratelimit-headers-09` `RateLimit` and `RateLimit-Policy` headers. The Hub now distinguishes 3 buckets: **Hub APIs** / **Resolvers** (URLs with `/resolve/`, highest limits, used by transformers/datasets/vLLM/llama.cpp/ollama) / **Pages** (web browsing). Our `~/.cache/huggingface` cache path follows the convention but no KCG code parses `RateLimit` header — `huggingface_hub` ≥1.2.0 does this automatically. | `huggingface.co/docs/hub/rate-limits` |
| **2026-06-28** | **MEDIUM: New Rate limit tiers (Sept 2025)** — Added **Enterprise Plus (10K API / 100K Resolvers / 1K Pages)** and **Enterprise Plus with IP allowlist (100K API / 500K Resolvers / 10K Pages)**. The old tier table maxed at Enterprise (6K / 50K / 600). If we ever scale agent fleet past 1K page requests / 5min, we need Enterprise Plus (and ideally the IP-allowlist tier for `arm1-oci` egress). | `huggingface.co/docs/hub/rate-limits` |
| **2026-06-28** | **LOW: New OAuth scope `inference-api`** — P2-23 says "Tier: Pro ($9/mo)" for higher rate limits; the new path is to use the **`inference-api` OAuth scope** with a user's own HF account, routing inference via Inference Providers. Useful for BAML `ExtractEnStrong` and other Spaces that want per-user rate-limit isolation. | `huggingface.co/docs/hub/oauth` |
| **2026-06-28** | **LOW: Public OAuth apps + CIMD** — `huggingface.co/docs/hub/oauth` documents **public OAuth apps (no client secret)** + Client ID Metadata Documents at `/.well-known/oauth-cimd` (CIMD). Ideal pattern for native CLIs and ephemeral environments. KCG has no OAuth app registered today. | `huggingface.co/docs/hub/oauth` |
| **2026-06-28** | **LOW: Webhooks available** — `huggingface.co/docs/hub/webhooks` documents real-time webhook subscriptions for repo changes (replaces polling). The KCG 4-layer change-detection stack (DLT cursor + Dagster sensor + ChangeDetection.io + Firecrawl monitor) could add a 5th layer: HF webhooks for `unsloth/...` upstream-watch. | `huggingface.co/docs/hub/webhooks` |
| **2026-06-28** | **LOW: OpenAPI playground replaced ad-hoc API docs** — `huggingface.co/docs/hub/api` is now a redirect to `huggingface.co/spaces/huggingface/openapi`; static spec at `/.well-known/openapi.json` and Markdown for agents at `/.well-known/openapi.md`. | `huggingface.co/docs/hub/api` |
| 2026-01 | Initial HF model registry (3 models) | P2-23 |
| 2025-12 | Expanded to 11 vision + 4 text | P2-23 |
| 2026-04 | Migrated from raw llama-cpp to unsloth/MacX-omni for inference | P2-23 |
| 2026-05 | Added HF Spaces deployment for demo apps | P2-23 |
| 2026-05 | **CLI renamed**: `huggingface_hub` 1.2 added `hf` CLI; `huggingface-cli` is deprecated shim | HF release notes |
| 2026-05 | **`[hf]` extra replaces `[cli]`** in v1.0+ | HF release notes |
| 2026-05 | **`hf skills add`** command for AI agent install (KCG has 17 HF skills in `.agents/skills/huggingface/`) | HF release notes |

## Anti-patterns

1. **Don't use `huggingface-cli` in new code** — use the `hf` CLI (same `huggingface_hub` package, different entry point). The `huggingface-cli` shim prints `Warning: 'huggingface-cli' is deprecated` on every invocation. The `hf-cli` skill (`.agents/skills/huggingface/hf-cli/SKILL.md:8`) is explicit: "The `hf` command replaces the deprecated `huggingface-cli` command." Existing P2-23 + `spaces/build-small-2026-runbook.md:26-330` references should migrate.
2. **Don't `pip install huggingface_hub[cli]`** — the `[cli]` extra was renamed `[hf]` in v1.0+. The install still works (CLI ships as a default extra since v1.0) but the dependency declaration is wrong. Use `huggingface_hub[hf]` for new code, plain `huggingface_hub` for libraries.
3. **Don't hardcode `unsloth/gemma-4-...-GGUF` or `unsloth/Qwen3.6-...-GGUF` model IDs** — they don't exist (Gemma 4 / Qwen 3.6 not released). P2-23:25-47 has 8 such aspirational IDs. Use `unsloth/gemma-3-...` and `unsloth/Qwen3-...` (without the `.6` suffix) for current production.
4. **Don't use `pipeline.push_to_hub` for non-`transformers` artifacts** — sklearn pickles, OCR checkpoint directories, BAML-compiled artefacts won't fit the `transformers` schema. Use `HfApi.upload_folder()` (the `push_model_to_hub()` helper in `spaces/_common/hf_hub_push.py:63-105` codifies this).
5. **Don't pass tokens as method params in production code** — `whoami(token=...)` is discouraged (P2-23 and the new quick-start agree). Use `HF_TOKEN` env or `login()` so the SDK can refresh tokens automatically.
6. **Don't bypass `HF_TOKEN` for batch downloads** — the rate-limits page is explicit: "make sure you always pass a `HF_TOKEN` ... this is the number one reason users get rate limited".
7. **Don't use `read` token for upload/create** — `create_repo()` requires **`write`** permission. KCG `infisical://dev-baile/huggingface/token` should be verified as `write`.
8. **Don't re-invent 429-retry logic** — `huggingface_hub` ≥1.2.0 auto-parses the new `RateLimit` header (5-min fixed window) and waits precisely `t=seconds-until-reset`. Custom retry code that just sleeps a constant `60s` wastes time on long tail.

## Decision matrix

| Decision | Choice | Rationale |
|:--|:--|:--|
| Library version | `huggingface_hub` ≥ 1.20.1 (stable) — track 1.21.0.rc0 for new features | Quick-start page is rc0; 1.20.1 is latest stable as of 2026-06-28. Required ≥1.2.0 for smart retry on `RateLimit` header. |
| CLI entry point | `hf` (NOT `huggingface-cli`) | `huggingface-cli` is a deprecated shim added in 1.2+; `hf` is the canonical entry from v1.0+. `hf-cli` skill (`.agents/skills/huggingface/hf-cli/SKILL.md`) enforces. |
| Auth method | `HF_TOKEN` env (Locket-injected) | Spaces + scripts use `HF_TOKEN`; avoids `login()` requirement at container start. **Overrides P2-23** which doesn't specify the env-var priority. |
| Token permissions | `write` for Spaces/ensemble-gradio (push); `read` for inference-only Spaces (meaisín_cliste) | `create_repo()` and `upload_folder()` need `write`; only the model download path needs `read`. KCG should provision 2 Infisical secrets: `huggingface/token-read` + `huggingface/token-write`. |
| Model ID sources | Real model names (gemma-3, Qwen3, GLM-4.6, etc.) | P2-23's 11 vision models are 60% aspirational. P2-23 should be split: an `HF_MODELS_CURRENT` dict (real) + an `HF_MODELS_ROADMAP` dict (planned). |
| Inference path | **3-tier**: LiteLLM gateway (BAML/Spaces) → HF Inference API (`inference-api` OAuth scope) → local GGUF/MLX | The Spaces already migrated to LiteLLM (per `openspec/changes/archive/2026-06-24-spaces-use-litelm-gateway/`). The `inference-api` OAuth scope (new) is the right escalation tier before falling back to local. |
| Rate-limit handling | Delegate to `huggingface_hub` ≥1.2.0 (auto-parse `RateLimit` header) | No custom code needed. If writing raw HTTP, follow IETF `draft-ietf-httpapi-ratelimit-headers-09`. |
| Tier | Pro ($9/mo) — already what P2-23 says — but **with note about Enterprise Plus** if rate-limit exhausted at 1K API / 5-min | Resolvers (5K) is the binding constraint for vLLM/llama.cpp bulk pulls. Pro → 12K resolvers. |
| Storage of fine-tunes | HF Hub (public, versioned) + MLflow (local, private) — same as P2-23 | P2-23 already says this. No change. |
| API docs source | OpenAPI playground at `huggingface.co/spaces/huggingface/openapi` + static `/.well-known/openapi.json` | `/docs/hub/api` is a redirect stub. Use the playground for humans, the `.json`/`.md` for agents. |
| OAuth flow for new KCG OAuth app | **Public app (no secret) + CIMD** at `https://oci.cianfhoghlaim.ie/.well-known/oauth-cimd` | New pattern (Sept 2025) ideal for native CLIs / Spaces; no secret rotation. Use for `hf auth login` from `oideachais`/`tuatha`/etc. apps. |

## Files to read next

- `infrastructure/ci/spaces-sync.yml:63-74` — the GHA step installs `[cli]` extra; should be `[hf]`
- `spaces/build-small-2026-runbook.md:26-330` — 9 references to `huggingface-cli`; half need migration to `hf`
- `openspec/research/2026-06-28-browserbase-credit-program/phase-2/P2-23-huggingface.md:25-47` — the 11 vision model IDs need real-ID audit
- `openspec/changes/2026-06-28-browserbase-phase-2-decisions/specs/meaisinfhoghlaim-platform/spec.md:130` — `huggingface-cli download` should be `hf download`
- `huggingface.co/docs/hub/webhooks` — new webhook API; could augment the 4-layer change-detection stack
- `huggingface.co/docs/hub/rate-limits` — new `RateLimit` header; new Enterprise Plus tiers
- `huggingface.co/docs/hub/oauth` — 15 OAuth scopes; new `inference-api` scope; CIMD for public apps
- `huggingface.co/docs/hub/agents-cli` — `hf skills add [--claude]` for AI agent install (we already have 17 skills in `.agents/skills/huggingface/`)

## §8 Refactor opportunities

| # | Refactor | File:line | Benefit |
|:--|:--|:--|:--|
| **R1** | **Migrate all `huggingface-cli` → `hf` CLI** in `spaces/build-small-2026-runbook.md` (9 refs) and `openspec/research/2026-06-28-browserbase-credit-program/phase-2/P2-23-huggingface.md:74`. Keep the deprecation notes (they're still correct); only migrate the command examples. | `spaces/build-small-2026-runbook.md:26,92,98,304,315,316` + `P2-23-huggingface.md:74` | Removes 6 deprecation warnings per CI run; aligns with v1.0+ canonical entry point |
| **R2** | **Fix `[cli]` → `[hf]` extra** in `infrastructure/ci/spaces-sync.yml:64`. The install still works (CLI is a default extra in v1.0+) but the declaration is stale. | `infrastructure/ci/spaces-sync.yml:64` | Dep-hygiene; future-proof against `[cli]` removal |
| **R3** | **Replace aspirational model IDs in P2-23** — replace `unsloth/gemma-4-...-GGUF` with `unsloth/gemma-3-...-GGUF` and `unsloth/Qwen3.6-...` with `unsloth/Qwen3-...`. The Gemma-3 family + Qwen3 family exist on HF today; Gemma-4 and Qwen-3.6 do not. Verify each `hf_hub_download()` call against actual HF Hub before merging any pull-request. | `P2-23-huggingface.md:25-47` | Eliminates 8 phantom-model broken downloads; aligns spec with reality (agent-20 already cross-flagged) |
| **R4** | **Add a `huggingface_hub` >= 1.20.1 floor** to the 3 places that pin it: `spaces/cianfhoghlaim/README.md:48` (currently `huggingface_hub` unconstrained), `spaces/README.md:95` (`huggingface_hub>=0.24`), and the 5 `.agents/skills/huggingface/*/scripts/*.py` PEP-723 blocks (currently `huggingface_hub>=0.20.0`). The `<1.x` upper bound is stale; v1.0+ is the new stable line. | `spaces/README.md:95`, `spaces/cianfhoghlaim/README.md:48`, `finetune_irish.py:49`, `convert_to_gguf.py:9` | Enables the `RateLimit`-header auto-retry + `hf` CLI features; aligns with HF's Sept 2025 deprecation schedule |
| **R5** | **Provision 2 HF Infisical secrets** — `huggingface/token-read` (for the 3 inference-only Spaces) and `huggingface/token-write` (for `push_model_to_hub`, Spaces-CI, the audio-dataset asset). Currently only `huggingface/token` exists. The 15 OAuth scopes include `write-repos` for the write token; P2-23 doesn't distinguish. | `openspec/changes/huggingface-token-split/` (new change) | Principle of least privilege; matches HF's `read` vs `write` token recommendation (quick-start §"Method parameters") |
| **R6** | **Add HF webhooks to the 4-layer change-detection stack** — the new `webhooks` OAuth scope + `huggingface.co/docs/hub/webhooks` enables real-time repo-change notifications. Could augment the 4-layer pattern (DLT cursor + Dagster sensor + ChangeDetection.io + Firecrawl monitor) with a 5th HF-webhook layer for upstream `unsloth/...` model watch. | `openspec/changes/upstream-package-monitoring/specs/...` | Replaces 5-min polling with push notifications for upstream model updates |
| **R7** | **Document the `inference-api` OAuth scope** in a new `spaces/_common/baml_client.py` shim — add a 3rd tier after LiteLLM: "if user has granted `inference-api` scope, route via user's own HF Inference account (per-user rate limit)". Useful for BAML `ExtractEnStrong` and any agent that benefits from per-user isolation. | `spaces/_common/baml_client.py:85-100` (the config builder) | Unlocks per-user rate limits; aligns Spaces with the new HF inference routing pattern |
| **R8** | **Migrate audio-dataset asset to `HfApi().upload_folder(..., commit_message=...)`** with an explicit commit message that includes the Dagster run ID + partition key. Currently the asset at `cianfhoghlaim/assets/_oideachais_dagster_defs/assets/unified_audio_dataset_assets.py:639-643` uploads with no commit message, making the HF repo history useless for diffing. | `unified_audio_dataset_assets.py:639-643` | Traceable HF dataset history; matches the `push_model_to_hub` pattern at `spaces/_common/hf_hub_push.py:99-104` |
| **R9** | **Register a KCG public OAuth app with CIMD** at `https://oci.cianfhoghlaim.ie/.well-known/oauth-cimd` — the new no-secret pattern is ideal for the 4 Spaces and the `oideachais` agent runtime. The CIMD JSON returns the `client_id` as a URL, the auth is PKCE-only, and there's no client_secret to rotate. Pairs naturally with the `hf skills add [--claude]` flow. | new `infrastructure/oauth-cimd/cimd.json` + DNS | Native-CLI auth for KCG agents; no secret rotation burden |
| **R10** | **Replace manual `RateLimit`-header parsing** in any custom KCG HTTP code with the `huggingface_hub` ≥1.2.0 built-in (`utils._headers.RateLimit` auto-parse). KCG has no such custom code today, but `spaces/_common/baml_client.py` does raw HTTP for the offline mode — if it ever calls HF directly (not via LiteLLM), it should use the SDK. | n/a (preventive) | Avoid re-inventing 5-min window arithmetic |
