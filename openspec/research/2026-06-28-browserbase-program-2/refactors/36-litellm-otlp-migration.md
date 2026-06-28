# Refactor 36 — LiteLLM OTLP / Image Pin Migration

**Agent:** 36 (litellm-otlp-migration) · **Date:** 2026-06-29 · **Program:** 2 (Wave 3) · **Credits used:** ~0 (all context from Wave-1 research; no live browser) · **Wall clock:** ~22 min

> Cross-references: Agent 06 (`agent-06-litellm.md`), Agent 26 §3 P0-4, Agent 28 §3 C-2.3, infra `infrastructure/stacks/litellm/`, infra `infrastructure/stacks/langfuse/` (v3 deployed).

---

## 1. TL;DR

The `ghcr.io/berriai/litellm:main-stable` Docker tag is **DEPRECATED 2026-06-30** (2 days from research date) and our `model_info.fallback_chain` custom field **may not actually trigger fallback** — both need fixing this week. This spec pins the image to `1.84.0-stable`, migrates the Langfuse v2 callback block (config.yaml:760-765) to **Langfuse v3 OTLP/HTTP** (the upstream-recommended integration path), and rewrites the `minimax` 7-tier fallback onto the canonical `litellm_settings.fallbacks` syntax. Total wall-clock: **~6.5 hours across 1 day**; single PR; rollback is a `git revert` + `docker compose pull` of the old `:main-stable` SHA.

---

## 2. The 2-day deadline (P0-4)

Per **Agent 06** (`agent-06-litellm.md:11-12, 219, 241`) and the upstream blog `https://docs.litellm.ai/blog/cleaner-release-versions`:

- **Today (research date):** 2026-06-28 / 2026-06-29
- **Cutover:** **2026-06-30** — the `main-stable` Docker tag stops receiving rebuilds and the registry GC may remove the manifest
- **Our pin** (`infrastructure/stacks/litellm/compose.yaml:8`): `ghcr.io/berriai/litellm:main-stable` ← **broken in ≤48h**
- **Image copies (must edit both):** `infrastructure/stacks/litellm/compose.yaml:8` AND `cianfhoghlaim/stacks/litellm/compose.yaml:8` (verbatim duplicate per v4 consolidation mirror)
- **Risk if not migrated:** `docker compose pull` after 2026-06-30 will pull nothing or a 404; deploy fails open-loop with no observability into why

**Two other P0-4-tagged drift items surfaced by Agent 06 that this PR bundles:**

- **R5 — `model_info.fallback_chain` is a custom convention** (config.yaml:723-730). LiteLLM does NOT recognize the field; only `litellm_settings.fallbacks: [{"minimax": ["opencode-go/minimax-m3-slot1", ...]}]` actually triggers the 7-tier cycle. Today's `minimax` requests likely return 502 on the first 3-key exhaustion rather than gracefully falling through to `qwen3.7-max` → `kimi-k2.6` → `glm-4.6` → local GGUF.
- **R2 — Langfuse v3 OTEL is now the recommended integration path** (Agent 06 `agent-06-litellm.md:15, 123, 215`). Our v2-callback block (config.yaml:760-765) still works but is on a deprecation trajectory. Langfuse v3 (we deploy `langfuse/langfuse:3` per `infrastructure/stacks/langfuse/compose.yaml:66`) natively accepts OTLP/HTTP at `/api/public/otel/v1/traces` — no `langfuse` SDK import required on the LiteLLM side.

**Bundle rationale:** all three changes touch `infrastructure/stacks/litellm/config/config.yaml` and `compose.yaml`; doing them in one PR means one rollback, one cache-warm cycle, one Langfuse trace-shape comparison.

---

## 3. Upgrade step 1 — Image pin (1 hour)

**Diff for `infrastructure/stacks/litellm/compose.yaml:8`** (and the identical line in `cianfhoghlaim/stacks/litellm/compose.yaml:8`):

```diff
   litellm:
-    image: ghcr.io/berriai/litellm:main-stable
+    image: ghcr.io/berriai/litellm:1.84.0-stable
     container_name: litellm
```

**Version choice rationale:**

- `1.84.0-stable` is the first release on the **cleaner-versioning scheme** documented in the upstream blog (Agent 06:215, blog 2026-04-28). Stable tags no longer carry the `-stable` suffix in 1.85+; the `1.84.0-stable` tag is the **last tagged stable with the legacy convention** and is the cleanest "known-good" pin for the cutover.
- `1.83.0` is the security baseline per the March 2026 supply-chain advisory (`https://docs.litellm.ai/blog/security-update-march-2026`); `1.84.0-stable` is strictly newer.
- `:latest` is acceptable for dev but **NOT for prod** (Pangolin `litellm.cianfhoghlaim.ie` serves all 5 BAML sub-packages + 11 marimo notebooks + Dagster assets + opencode subagents). Reproducibility matters.
- `:main-stable` is what we're escaping.

**Pre-flight (5 min):**

```bash
# Verify the pin exists in GHCR before the PR
docker pull ghcr.io/berriai/litellm:1.84.0-stable
# Expected digest documented in PR description; pin to @sha256 after first pull
docker inspect --format='{{index .RepoDigests 0}}' ghcr.io/berriai/litellm:1.84.0-stable
```

**Companion edits (search-and-replace, 10 min):**

```bash
grep -rn "berriai/litellm:main-stable" infrastructure/ openspec/ docs/ 2>&1
```

Expected hits (per Agent 06 §8.1 + cross-spec):

- `infrastructure/stacks/litellm/compose.yaml:8` — edit
- `cianfhoghlaim/stacks/litellm/compose.yaml:8` — edit
- `infrastructure/stacks/litellm/README.md` — doc note
- `openspec/specs/infrastructure-stacks/spec.md` — search for `main-stable` mention
- `openspec/research/2026-06-28-browserbase-program-2/agent-06-litellm.md` — already documented (no edit, it's a research artifact)

**Healthcheck guard:** the existing healthcheck at lines 59-66 already calls `/health/liveliness` on `:4000`, which exists in `1.84.0-stable`. No edit needed.

---

## 4. Langfuse v3 OTLP migration (2 hours)

### 4.1 Why OTLP/HTTP and not the gRPC variant

Langfuse v3 (deployed at `langfuse/langfuse:3` per `infrastructure/stacks/langfuse/compose.yaml:66`) exposes the **OTLP/HTTP receiver** at `https://<host>/api/public/otel/v1/traces` (standard OpenTelemetry HTTP/protobuf + JSON paths both accepted). No separate gRPC `:4317` port to expose through Pangolin — we keep the existing `litellm.cianfhoghlaim.ie:4000` ↔ `langfuse.cianfhoghlaim.ie:3000` mesh.

This avoids the `langfuse` Python SDK import (we currently pin `langfuse==2.59.7`) and instead uses LiteLLM's built-in OTEL callback which is **maintained in lockstep with the LiteLLM release** — fewer version-coupling bugs than the v2 callback path.

### 4.2 Diff for `infrastructure/stacks/litellm/config/config.yaml`

**Remove lines 760-765** (the v2 callback block inside `general_settings:`):

```diff
   # Health checks
   health_check_interval: 30

-  # Langfuse observability (when LANGFUSE_HOST is set)
-  langfuse:
-    langfuse_enabled: true
-    langfuse_host: os.environ/LANGFUSE_HOST
-    langfuse_public_key: os.environ/LANGFUSE_PUBLIC_KEY
-    langfuse_secret_key: os.environ/LANGFUSE_SECRET_KEY
-
   # =============================================================================
   # ROUTING FALLBACKS (per route)
   # =============================================================================
```

**Add the OTEL exporter block** to `litellm_settings:` (which doesn't exist yet — create it immediately after the `router_settings:` block, at end of file, around line 776):

```yaml
# =============================================================================
# LITELLM SETTINGS (callbacks, fallbacks, telemetry)
# =============================================================================
litellm_settings:
  # ---- Langfuse v3 OTLP/HTTP exporter (replaces v2 callback) ----
  # Sends OpenTelemetry traces to Langfuse v3 at /api/public/otel/v1/traces.
  # Requires LANGFUSE_HOST (e.g. https://langfuse.cianfhoghlaim.ie) and the
  # Basic-auth pair LANGFUSE_PUBLIC_KEY:LANGFUSE_SECRET_KEY (Infisical-injected).
  # Per-request overrides via `langfuse_public_key=`, `langfuse_secret_key=`,
  # `langfuse_host=` kwargs (see https://docs.litellm.ai/docs/observability/langfuse_otel_integration).
  telemetry: false
  success_callback: ["langfuse_otel"]   # native OTEL path (LiteLLM 1.70+)
  failure_callback: ["langfuse_otel"]

  # ---- Canonical 7-tier fallback chain (replaces model_info.fallback_chain) ----
  # Order: 3× M3 slots → 3× cross-vendor alternates → local GGUF.
  # num_retries=3 in router_settings triggers the cycle; with this explicit
  # `fallbacks` map LiteLLM knows which models are eligible to be retried.
  # See https://docs.litellm.ai/docs/proxy/configs#load-balancing
  fallbacks:
    - minimax:
        - opencode-go/minimax-m3-slot1
        - opencode-go/minimax-m3-slot2
        - opencode-go/minimax-m3-slot0   # wrap-around so the last slot is also retry-eligible
        - opencode-go/qwen3.7-max
        - opencode-go/kimi-k2.6
        - openai/glm-4.6
        - local/math/qwen25-math
  context_window_fallbacks:
    - minimax:
        - opencode-go/qwen3.7-max        # 200K ctx vs M3's 200K — graceful degradation
        - openai/glm-4.6
        - local/math/qwen25-math
  allowed_fails: 3                       # cooldown a deployment after 3 fails in 60s
  cooldown_time: 60
```

**No change to `compose.yaml:48-51`** — the four `LANGFUSE_*` env vars (HOST / PUBLIC_KEY / SECRET_KEY) are still the same surface; OTLP/HTTP Basic auth reads them from the same env names.

### 4.3 Why this works without the `langfuse` Python SDK

LiteLLM's `langfuse_otel` callback ships **inside the LiteLLM wheel** at `litellm.integrations.langfuse_otel.langfuse_otel` (path: `litellm/.../langfuse_otel.py` in 1.84.0-stable). It uses the OpenTelemetry Python SDK (already a transitive dep of LiteLLM) and writes OTLP/HTTP frames to `<LANGFUSE_HOST>/api/public/otel/v1/traces` with HTTP Basic auth header `Authorization: Basic base64(public_key:secret_key)`. The v2 path imported the `langfuse` SDK and called its Python API directly — more coupling, more drift, more version pins to maintain.

### 4.4 Per-request credential override (preserved)

The new path supports per-request keys via the same kwargs the v2 path did:

```python
import litellm
litellm.completion(
    model="minimax",
    messages=[{"role": "user", "content": "..."}],
    langfuse_public_key="pk-lf-...",        # NEW: same kwargs as v2
    langfuse_secret_key="sk-lf-...",
    langfuse_host="https://langfuse.cianfhoghlaim.ie",
)
```

This preserves the per-tenant key-rotation pattern that BAML's `ExtractEn` client uses for multi-tenant tracing.

---

## 5. Fallback chain verification — `model_info.fallback_chain` → `litellm_settings.fallbacks` (1 hour)

### 5.1 The drift (Agent 06 R5)

Per `agent-06-litellm.md:88, 227, 235`, the `model_info.fallback_chain` block at `config.yaml:723-730` is a **KCG-local convention** documented in the spec at `openspec/changes/litellm-minimax-vendor-derisking/specs/llm-gateway/spec.md:18-25` but **not enforced by LiteLLM**. LiteLLM's canonical fallback syntax is `litellm_settings.fallbacks: [{"<primary>": ["<fallback1>", "<fallback2>", ...]}]`. Today, the `minimax` alias likely:

- Returns 502 / 500 after the first 3 retries exhaust (the 3 OPENCODE_GO_API_KEY_{0,1,2} slots are tried by `num_retries: 3`, but only because **multiple `model_list` entries share `model_name: opencode-go/minimax-m3-slot{0,1,2}`** and the router load-balances across them — see config.yaml:381-410).
- **Does NOT** fall through to `qwen3.7-max` → `kimi-k2.6` → `glm-4.6` → local GGUF when the entire `opencode.ai/zen/go` gateway is offline.

The change in §4.2 above adds the canonical `litellm_settings.fallbacks` block, which **LiteLLM actually honors**.

### 5.2 The diff for `config.yaml:719-730` (the model_info block on the `minimax` alias)

**Keep** the `model_info.fallback_chain` field for the spec's documentation purpose (the openspec change enforces the order), but **prefix it with a `_doc_only_` comment** so future operators know it's not the runtime contract:

```diff
   - model_name: minimax
     litellm_params:
       model: anthropic/minimax-m3
       api_base: https://opencode.ai/zen/go/v1/messages
       api_key: os.environ/OPENCODE_GO_API_KEY
     model_info:
       description: "Alias: minimax → M3 (3-key round-robin), then qwen3.7-max, kimi-k2.6, glm-4.6, then local qwen-math GGUF"
       capabilities: ["general", "agentic", "alias"]
       tier: paid
-      fallback_chain:
+      # _doc_only_ — runtime contract is `litellm_settings.fallbacks` below
+      # (see openspec/changes/litellm-minimax-vendor-derisking/specs/llm-gateway/spec.md)
+      _doc_only_fallback_chain_:
         - "opencode-go/minimax-m3-slot0"
         - "opencode-go/minimax-m3-slot1"
         - "opencode-go/minimax-m3-slot2"
         - "opencode-go/qwen3.7-max"
         - "opencode-go/kimi-k2.6"
         - "openai/glm-4.6"
         - "local/math/qwen25-math"
```

> **Why rename instead of delete:** deleting breaks the spec.md reference contract; renaming to `_doc_only_fallback_chain_` keeps the spec testable (CCC search hits still resolve) while making the runtime contract unambiguous.

### 5.3 Spec delta

This change modifies the `llm-gateway` capability; openspec delta to author in the new `litellm-otlp-cutover` change:

```markdown
## MODIFIED Requirements
### Requirement: Fallback chain ordering
The `minimax` alias SHALL fall through in the order
`minimax-m3-slot{0,1,2}` → `qwen3.7-max` → `kimi-k2.6` → `glm-4.6` →
`local/math/qwen25-math` when an upstream call returns a retryable error.

The runtime contract is `litellm_settings.fallbacks` (canonical LiteLLM).
The `model_info.fallback_chain` field is retained under the key
`_doc_only_fallback_chain_` for spec-anchoring purposes only and SHALL
NOT be relied on for runtime behaviour.

#### Scenario: opencode-go gateway fully down
- **WHEN** all three `minimax-m3-slot{0,1,2}` deployments return
  retryable errors and `num_retries: 3` is exhausted
- **THEN** the request cycles to `qwen3.7-max`, then `kimi-k2.6`, then
  `glm-4.6`, then `local/math/qwen25-math`
- **AND** the Langfuse v3 OTEL trace records the fallback chain
  (see `langfuse_otel` success_callback)

#### Scenario: 3-key slot exhaustion only
- **WHEN** the first 3 retries cycle through `slot0 → slot1 → slot2`
  and slot2 succeeds
- **THEN** the request returns successfully without falling through
  to cross-vendor alternates
```

---

## 6. Testing — verify the upgrade doesn't break (2 hours)

### 6.1 Pre-cutover (in the PR branch, on `bunchloch` dev)

```bash
# 1. Pull the new image and confirm banner
docker compose -f infrastructure/stacks/litellm/compose.yaml pull litellm
docker run --rm ghcr.io/berriai/litellm:1.84.0-stable --version
# Expected: LiteLLM: Version 1.84.0-stable   (per cleaner-release-versions blog)

# 2. Lint the config offline (catches YAML errors before container start)
docker run --rm \
  -v "$PWD/infrastructure/stacks/litellm/config:/app/config:ro" \
  ghcr.io/berriai/litellm:1.84.0-stable \
  --config=/app/config/config.yaml --help
# Expected: startup banner + "Validating config..." + zero error

# 3. Boot the stack, wait for healthcheck
./scripts/stack.sh litellm up -d
./scripts/stack.sh litellm logs -f litellm | grep -E "Loaded|model_list|fallbacks|otel"
# Expected: "Loaded 100+ models", "fallbacks: [minimax → ...]", "langfuse_otel: enabled"

# 4. Smoke test — basic completion routes through `minimax` (alias)
curl -sS http://litellm:4000/v1/chat/completions \
  -H "Authorization: Bearer ${LITELLM_MASTER_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "minimax",
    "messages": [{"role": "user", "content": "Reply with the single word: PONG"}],
    "max_tokens": 8
  }' | jq '.choices[0].message.content'
# Expected: "PONG" (or "pong"); latency < 2s

# 5. Smoke test — direct model access (bypass alias)
curl -sS http://litellm:4000/v1/chat/completions \
  -H "Authorization: Bearer ${LITELLM_MASTER_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "opencode-go/qwen3.7-max",
    "messages": [{"role": "user", "content": "Reply with the single word: PONG"}],
    "max_tokens": 8
  }' | jq '.choices[0].message.content'
# Expected: "PONG" via qwen3.7-max

# 6. JSON schema validation (BAML strict mode)
curl -sS http://litellm:4000/v1/chat/completions \
  -H "Authorization: Bearer ${LITELLM_MASTER_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "minimax",
    "messages": [{"role": "user", "content": "Return a JSON object with field `ok: true`"}],
    "response_format": {
      "type": "json_schema",
      "json_schema": {
        "name": "smoke",
        "schema": {"type": "object", "properties": {"ok": {"type": "boolean"}}, "required": ["ok"]},
        "strict": true
      }
    }
  }' | jq '.choices[0].message.content'
# Expected: '{"ok":true}' (string literal), confirming enable_json_schema_validation: true works

# 7. Fallback chain — force a 429 by spamming slot0 and watching Langfuse trace
for i in {1..20}; do
  curl -sS -o /dev/null -w "%{http_code}\n" http://litellm:4000/v1/chat/completions \
    -H "Authorization: Bearer ${LITELLM_MASTER_KEY}" \
    -H "Content-Type: application/json" \
    -d '{"model":"opencode-go/minimax-m3-slot0","messages":[{"role":"user","content":"hi"}],"max_tokens":1}' &
done; wait
# Then trigger a request to `minimax` and check the Langfuse v3 trace:
curl -sS http://litellm:4000/v1/chat/completions \
  -H "Authorization: Bearer ${LITELLM_MASTER_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"model":"minimax","messages":[{"role":"user","content":"hi"}],"max_tokens":4}'
# Open Langfuse UI at https://langfuse.cianfhoghlaim.ie → project `oideachais` →
# latest trace → expect "model" span = whichever slot answered
```

### 6.2 Assertions to make in the PR

| Assertion | How to verify |
|:--|:--|
| Image pulled, no 404 | `docker image inspect ghcr.io/berriai/litellm:1.84.0-stable` |
| Banner shows `1.84.0-stable` | `docker logs litellm 2>&1 \| head` |
| Healthcheck green within 60s | `docker inspect --format='{{.State.Health.Status}}' litellm` |
| Model count ≥ 100 | `curl -H "Authorization: Bearer $LITELLM_MASTER_KEY" http://litellm:4000/v1/models \| jq '.data \| length'` |
| Default model = `minimax` | `curl -H "Authorization: Bearer $LITELLM_MASTER_KEY" http://litellm:4000/config \| jq '.litellm.default_model'` |
| Fallbacks map present | `curl -H "Authorization: Bearer $LITELLM_MASTER_KEY" http://litellm:4000/config \| jq '.litellm_settings.fallbacks'` |
| `langfuse_otel` callback active | `curl -H "Authorization: Bearer $LITELLM_MASTER_KEY" http://litellm:4000/config \| jq '.litellm_settings.success_callback'` |
| Langfuse v3 receives OTLP trace | Open UI → latest trace shows `model: minimax`, tokens counted |
| JSON schema validation | Test 6 above |
| No regression on direct model access | Test 5 above |

### 6.3 Dagster asset check (existing — no edit needed)

`minimax_alias_health` at `cianfhoghlaim/assets/_oideachais_dagster_defs/assets/llm_gateway_assets.py:200-215` already runs on the `minimax` alias. With the new `litellm_settings.fallbacks` block, the health check should **also exercise a forced fallback** (a new asset check `_minimax_fallback_chain_health` is a P3 follow-up, not in this PR's scope).

---

## 7. Cutover — deploy to `bunchloch`, watch for errors, rollback (30 min)

### 7.1 Cutover sequence

```bash
# T-0: tag the deployed image so rollback is reproducible
ssh bunchloch "docker tag \$(docker inspect --format='{{.Image}}' litellm) ghcr.io/berriai/litellm:main-stable-pre-cutover-2026-06-29"

# T+0: merge the PR (or apply the stack directly via Komodo)
cd /Users/cianmacandeisigh/dev/kings_college_galway
git checkout main && git pull --rebase
git merge --no-ff refactor/litellm-otlp-cutover
git push origin main
# → Komodo resource_sync fires the litellm stack pull+up

# T+2min: watch the deploy
./scripts/stack.sh litellm logs -f litellm 2>&1 | head -200
# Look for: "Loaded 100+ models", "fallbacks: ...", "langfuse_otel: enabled",
#           "Connected to OTLP endpoint https://langfuse.cianfhoghlaim.ie/api/public/otel/v1/traces"

# T+5min: run the 7 smoke tests from §6.1
# (or: bun run ccc:search "llm_gateway_assets" then `mise run dagster:oideachais` and
#  materialize the minimax_alias_health asset)

# T+10min: confirm Langfuse v3 trace
open https://langfuse.cianfhoghlaim.ie
# → project oideachais → latest trace should show "model: minimax",
#   token counts, latency, the v3-native OTEL span shape (not the v2 callback shape)
```

### 7.2 Watch list (15 min post-cutover)

| Signal | Where to look | Action if RED |
|:--|:--|:--|
| Container OOMs on start | `docker stats litellm` | Increase `deploy.resources.limits.memory` 4G → 6G in compose.yaml |
| Healthcheck stays `starting` | `docker inspect --format='{{.State.Health.Status}}' litellm` | Check `start_period: 40s`; if model load > 40s bump to 90s |
| Langfuse v3 401 on OTLP POST | Langfuse worker logs | Verify `LANGFUSE_PUBLIC_KEY` / `LANGFUSE_SECRET_KEY` are base64-compatible ASCII (no `+` URL-encoding issues) |
| `fallbacks` not in `/config` | `curl .../config` | YAML merge-key collision — check for `fallbacks:` at multiple indentation levels |
| `minimax` returns 502 immediately | `docker logs litellm` | Likely the `minimax` model_list entry's `api_key: os.environ/OPENCODE_GO_API_KEY` is empty — Locket didn't inject |
| OpenCode Go 401 | OpenCode Go dashboard | Keys rotated; update Infisical `opencode_go/api_key_{0,1,2}` |
| No traces in Langfuse | Langfuse UI | Confirm `LANGFUSE_HOST` is the **full URL** `https://langfuse.cianfhoghlaim.ie` (not just hostname) |
| Dagster `minimax_alias_health` failing | Dagster UI | Re-run the 6 smoke tests; if model load > 30s, asset check times out — bump timeout |

### 7.3 Rollback plan (3 commands, ~90 sec)

```bash
# 1. Revert the merge commit (preserves the 1.84.0-stable tag for re-application)
ssh bunchloch "cd /opt/bonneagar && git revert --no-edit HEAD"
# 2. Force-recompose to the pinned pre-cutover image
ssh bunchloch "cd /opt/bonneagar && docker compose -f stacks/litellm/compose.yaml pull litellm"
# → pulls ghcr.io/berriai/litellm:main-stable (still resolvable for ~24h post-cutover
#   before the registry GC; if GC'd already, use the SHA we tagged at T-0)
ssh bunchloch "cd /opt/bonneagar && docker compose -f stacks/litellm/compose.yaml up -d litellm"
# 3. Verify rollback
./scripts/stack.sh litellm logs -f litellm 2>&1 | head -50
# Should show: "main-stable" banner, v2 langfuse callback re-engaged, no OTEL POSTs
```

**Rollback TTL caveat:** `:main-stable` may be GC'd from GHCR after 2026-06-30. **Before the cutover, mirror the `:main-stable` image to the local OCI registry** so rollback is independent of upstream:

```bash
# Pre-cutover (run once on bunchloch)
docker pull ghcr.io/berriai/litellm:main-stable
docker tag ghcr.io/berriai/litellm:main-stable harbor.cianfhoghlaim.ie/litellm/main-stable-pre-cutover:2026-06-29
docker push harbor.cianfhoghlaim.ie/litellm/main-stable-pre-cutover:2026-06-29
```

**Open follow-ups (out of scope, P3 backlog):**

- `credential_list` centralization for the 3 OPENCODE_GO_API_KEY_{0,1,2} duplicates (P3-6 in Agent 26).
- Per-tenant Langfuse key rotation via BAML `ExtractEn` client per-request kwargs.
- New Dagster asset check `_minimax_fallback_chain_health` that force-triggers 429s and asserts the chain cycled.
- Re-evaluate `minimax` alias → `kanon` / `briathar` rename to avoid MiniMax Inc. provider collision (P2-13).

---

## §8. Cross-references & ccc anchors

- **Image-pin P0:** Agent 06 §8.1; Agent 26 §3 P0-4; Agent 28 §3 C-2.3 + §6 C-CO.5
- **Fallback chain R5:** Agent 06 §8.3 + drift log line 215; Agent 28 §3 C-2.3
- **Langfuse v3 OTEL R2:** Agent 06 §8.4 + drift log line 215; Agent 28 §3 C-2.3 + C-3.2
- **MiniMax Inc. provider collision** (separate, P2-13): Agent 06 §8.2 — **NOT** addressed in this PR
- **Spec to author:** `openspec/changes/litellm-otlp-cutover/` (new) with delta to `openspec/specs/infrastructure-stacks/spec.md` (image pin) and `openspec/specs/meaisinfhoghlaim-platform/spec.md` (LiteLLM canonical — Langfuse v3 OTEL)
- **CCC anchors (post-PR):** `infrastructure/stacks/litellm/compose.yaml:8` (new pin), `infrastructure/stacks/litellm/config/config.yaml:760-765` (v2 block removed), `config.yaml:777+` (new `litellm_settings:` block with `fallbacks` + `langfuse_otel` callback)
- **PR title:** `fix(litellm): pin main-stable→1.84.0-stable, migrate Langfuse v2→v3 OTEL, fix minimax fallback chain (P0-4)`
- **Effort:** S+M+S = ~6.5 hours (1h image pin + 2h OTEL + 1h fallback chain + 2h testing + 30min cutover)
- **Risk:** med (Langfuse trace shape change is a one-time observability diff; rollback is well-pinned)
- **Bundle rationale:** all three changes touch the same two files; one PR = one review + one rollback
