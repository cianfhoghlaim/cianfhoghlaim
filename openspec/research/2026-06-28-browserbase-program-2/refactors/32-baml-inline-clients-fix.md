# Refactor 32 — BAML Inline Clients Fix (`anthropic/claude-sonnet-4` → `ExtractEnStrong`)

**Agent 32 of 43** · Program 2 · 2026-06-29
**Priority:** P1 (refactor-prioritizer §4 P1-1; misunderstandings-corrector §7 #3 critical runtime-breaking)
**Estimated effort:** ~6.5 hours (1h locate + 2h alias + 2h replace + 1h validate + 30m rollback plan)
**BrowserBase credits:** 0 (read-only + dry-run validation)
**Cross-references:** `agent-15-baml.md:14-15,269-273`, `agent-06-litellm.md:46-88`, `synthesis/26-refactor-prioritizer.md:59` (P1-1), `synthesis/28-misunderstandings-corrector.md:222` (#3), `litellm-minimax-vendor-derisking/proposal.md:154-172` (non-goal)

---

## 1. TL;DR

`cianfhoghlaim/core/baml/_oideachais_src/curriculum_extraction.baml` has **14** (not 8) inline `client "anthropic/claude-sonnet-4-20250514"` calls that bypass the LiteLLM gateway — 5 of them in the spec'd range `:164-1086`, plus 9 more that agent-15 missed (`:501, 541, 579, 617, 653, 775, 973, 1008, 1047`). The canonical `ExtractEnStrong` client exists (`_oideachais_src/clients.baml:256`) but its target alias `extract-en-strong` is **not registered** in `infrastructure/stacks/litellm/config/config.yaml` (only `extract` at L604 and `minimax` at L714 are). The fix is a 3-step migration: (a) register the `extract-en-strong` alias in litellm config, (b) sed-replace all 14 lines, (c) `baml-cli generate` + dry-run. Adjacent scope: 15 more inline calls in 4 sister files (`aistear.baml`, `junior_cycle.baml`, `primary.baml`, `tertiary.baml`) and 6 `openai/gpt-4o*` inline calls in `isles_education.baml` — same surgery.

---

## 2. Why this matters

### 2.1 The bypass (what each inline call does today)

The 14 inline calls in `curriculum_extraction.baml` resolve the BAML `client "anthropic/claude-sonnet-4-20250514"` shorthand to a **direct provider block** that hits Anthropic with the legacy `ANTHROPIC_API_KEY` env var:

| What the inline call does | What it bypasses | Risk |
|:--|:--|:--|
| `provider anthropic` + `api_key env.ANTHROPIC_API_KEY` (BAML implicit) | LiteLLM gateway (`http://litellm:4000/v1`) | No single rotation point |
| Hits Anthropic API directly | 7-tier `minimax` fallback (`config.yaml:714-730`) | Single-vendor outage = 14 functions down |
| No LiteLLM `litellm_params` | `num_retries: 3` + `timeout: 600` (`config.yaml:770-771`) | 0 in-flight retries |
| No `general_settings.langfuse` block | Langfuse v2 callback (`config.yaml:760-765`) | **Zero observability** — costs and traces invisible |
| Direct `ANTHROPIC_API_KEY` (legacy `.env`) | `LITELLM_MASTER_KEY` + Locket | Secrets scattered, no spend cap |
| Hits Anthropic's `/v1/messages` (no JSON mode wrapping) | `enable_json_schema_validation: true` (`config.yaml:745`) | No strict schema enforcement for BAML SAP |
| No `model_info.tier: paid` | LiteLLM spend tracking dashboard | Untracked cost (could exceed budget) |

### 2.2 The non-goal that became a half-finished job

The 2026-06-28 `litellm-minimax-vendor-derisking` change (`proposal.md:154-172`) explicitly carved out a non-goal: *"This change does **not** rewrite any BAML extraction function."* The motivation was sound (don't scope-creep a security fix), but the consequence is that **`_oideachais_src/clients.baml` was updated to add the `ExtractEnStrong` client (L256) yet the 14 call sites in `curriculum_extraction.baml` were never migrated.** Every call to `ExtractLearningOutcomeRelationships`, `ExtractExamPaperMarkingScheme`, `LazyExtractExamPaper`, etc. today still bypasses the gateway it was supposed to use.

### 2.3 Severity per `synthesis/28-misunderstandings-corrector.md:222`

Listed as **C-3.2 (Critical runtime-breaking #3)** — defeats the Phase 0.4 vendor-de-risking goal. Also flagged in `synthesis/26-refactor-prioritizer.md:59` (P1-1, M effort, med risk).

---

## 3. Step 1 — Locate every inline call (1 hour)

### 3.1 Primary target: `curriculum_extraction.baml`

**14 occurrences** (agent-15 said 8, but the file has 14 — the diff is at lines 501, 541, 579, 617, 653, 775, 973, 1008, 1047 which the earlier audit missed):

```bash
# All 14 line numbers
rg -n 'client "anthropic/claude-sonnet-4-20250514"' \
   cianfhoghlaim/core/baml/_oideachais_src/curriculum_extraction.baml
# → 167, 208, 243, 277, 501, 541, 579, 617, 653, 775, 973, 1008, 1047, 1085
```

### 3.2 Adjacent scope: 5 sister files (15 more inline calls)

```bash
rg -n 'client "anthropic/claude-sonnet-4-20250514"' \
   cianfhoghlaim/core/baml/_oideachais_src/

# 29 total matches across 5 files:
#   curriculum_extraction.baml: 14
#   tertiary.baml:              7  (lines 168, 179, 190, 201, 233, 269, 302)
#   aistear.baml:               3  (lines 109, 145, 178)
#   junior_cycle.baml:          3  (lines 114, 151, 190)
#   primary.baml:               2  (lines 87, 123)
```

### 3.3 Different antipattern: `isles_education.baml` (6 inline OpenAI calls)

```bash
rg -n 'client "openai/gpt-4o' \
   cianfhoghlaim/core/baml/_oideachais_src/isles_education.baml
# → 228, 241, 255, 268 (gpt-4o), 281, 304 (gpt-4o-mini)
# Replace with: client LocalVision / ExtractEn / client<llm> from clients.baml
```

**`isles_education.baml` is a different fix path** — these calls bypass via `openai/gpt-4o*` and need a different named client (likely a new `ExtractEnCrossBorder` or reuse `ExtractEn`). Out of scope for this surgical fix; **track as a follow-up refactor (#32b)**.

### 3.4 ccc:search for hidden occurrences

```bash
bun run ccc:search 'client "anthropic/claude-sonnet-4-20250514"'
bun run ccc:search 'client "openai/gpt-4o'
bun run ccc:search 'inline BAML client anthropic'
```

Verify ccc index is fresh: `bun run ccc:index` (only if files were just moved).

### 3.5 Deliverable: a complete inventory table

| File | Line | Function (inferred from context) | Status |
|:--|:-:|:--|:--|
| `curriculum_extraction.baml` | 167 | `ExtractLearningOutcomeRelationships` | **In-scope** |
| `curriculum_extraction.baml` | 208 | (TBD — read function above) | **In-scope** |
| `curriculum_extraction.baml` | 243, 277, 501, 541, 579, 617, 653, 775, 973, 1008, 1047, 1085 | (12 more) | **In-scope** |
| `tertiary.baml` | 168, 179, 190, 201, 233, 269, 302 | 7 tertiary-curriculum functions | Adjacent (defer to 32b) |
| `aistear.baml` | 109, 145, 178 | 3 early-years functions | Adjacent (defer to 32b) |
| `junior_cycle.baml` | 114, 151, 190 | 3 JC functions | Adjacent (defer to 32b) |
| `primary.baml` | 87, 123 | 2 primary functions | Adjacent (defer to 32b) |
| `isles_education.baml` | 228, 241, 255, 268, 281, 304 | 6 cross-border (OpenAI) | **Out-of-scope** (32c) |

**Effort:** 1 hour (15 min grep + 30 min ccc + 15 min inventory table).

---

## 4. Step 2 — Canonical client + missing alias (2 hours)

### 4.1 The `ExtractEnStrong` client (already defined)

`cianfhoghlaim/core/baml/_oideachais_src/clients.baml:253-264`:

```baml
// `ExtractEnStrong` is the fallback for difficult extractions (math / dense legal).
// Routes through the gateway alias `extract-en-strong` which resolves to
// anthropic/claude-sonnet-4 → gemini-2.5-pro → gemini-1.5-pro.
client<llm> ExtractEnStrong {
  provider openai
  options {
    base_url env.LITELLM_BASE_URL
    api_key env.LITELLM_MASTER_KEY
    model "extract-en-strong"
  }
  retry_policy Simple
}
```

This definition was added in the 2026-06-28 `litellm-minimax-vendor-derisking` change but the **target alias `extract-en-strong` is not yet wired in LiteLLM** — see §4.2.

### 4.2 The missing alias (must add before BAML switch)

`infrastructure/stacks/litellm/config/config.yaml` currently registers:
- `model_name: extract` (line 604) — `gemini/gemini-2.5-pro` primary, `openai/glm-4.6` + `gemini/gemini-2.5-flash` fallback
- `model_name: minimax` (line 714) — 7-tier fallback
- `model_name: anthropic/claude-sonnet-4-20250514` (line 256) — **direct, no alias wrapper**

**There is no `extract-en-strong` alias.** The BAML `client<llm> ExtractEnStrong` will 404 at runtime until we add it.

#### Diff to apply at `config.yaml` after line 612 (after the `extract` block):

```yaml
  # Extract En Strong — primary: Claude Sonnet 4 (gateway-routed), fallback: Gemini 2.5 Pro
  # This alias replaces the 14 inline `client "anthropic/claude-sonnet-4-20250514"` calls
  # in _oideachais_src/curriculum_extraction.baml (refactor P1-1).
  - model_name: extract-en-strong
    litellm_params:
      model: anthropic/claude-sonnet-4-20250514
      api_key: os.environ/ANTHROPIC_API_KEY
    model_info:
      description: "Alias: extract-en-strong → Claude Sonnet 4 (gateway-routed), falls back to Gemini 2.5 Pro, then Gemini 1.5 Pro. Replaces inline anthropic/claude-sonnet-4-20250514 calls in curriculum_extraction.baml."
      capabilities: ["extraction", "baml", "alias", "long_context", "tools"]
      tier: paid
      fallback_chain:
        - "anthropic/claude-sonnet-4-20250514"
        - "gemini/gemini-2.5-pro"
        - "gemini/gemini-1.5-pro"
```

> **Note:** This alias **wraps the same model** (`anthropic/claude-sonnet-4-20250514`) that the inline calls used, but routes it through LiteLLM — so we get the `num_retries: 3`, the JSON mode validation (`enable_json_schema_validation: true`), the Langfuse callback, and the spend-tracking dashboard. The semantic content is unchanged.

### 4.3 Verify alias is wired

```bash
# After applying diff:
grep -n "extract-en-strong" infrastructure/stacks/litellm/config/config.yaml
# → expect 5 lines (model_name + litellm_params + 2x model_info fields + 1 fallback_chain)

# Reload LiteLLM:
docker compose -f infrastructure/stacks/litellm/compose.yaml restart litellm

# Smoke test the alias directly:
curl -s -X POST http://litellm.cianfhoghlaim.ie/v1/chat/completions \
  -H "Authorization: Bearer $LITELLM_MASTER_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"extract-en-strong","messages":[{"role":"user","content":"Reply with just the word OK"}],"max_tokens":10}' \
  | jq -r '.choices[0].message.content'
# → expect "OK" within 5s (Sonnet 4 cold)
```

### 4.4 Effort

2 hours (30 min diff + 1 hour LiteLLM restart + 30 min smoke test).

---

## 5. Step 3 — Surgical replacement (2 hours)

### 5.1 The sed (single command, all 14 lines in `curriculum_extraction.baml`)

```bash
# In the repo root:
sed -i 's|client "anthropic/claude-sonnet-4-20250514"|client ExtractEnStrong|g' \
    cianfhoghlaim/core/baml/_oideachais_src/curriculum_extraction.baml

# Verify count is 14 (was 14, should still be 14 — but now pointing at named client):
rg -c 'client ExtractEnStrong' cianfhoghlaim/core/baml/_oideachais_src/curriculum_extraction.baml
# → 14

# Verify zero remaining inline anthropic calls:
rg -c 'client "anthropic' cianfhoghlaim/core/baml/_oideachais_src/curriculum_extraction.baml
# → 0
```

### 5.2 The diff (post-edit)

14 identical 1-line changes at lines 167, 208, 243, 277, 501, 541, 579, 617, 653, 775, 973, 1008, 1047, 1085 — each replacing `client "anthropic/claude-sonnet-4-20250514"` with `client ExtractEnStrong`. Total: 14 insertions / 14 deletions, 0 net. Representative diff:

```diff
@@ -164,7 +164,7 @@ function ExtractLearningOutcomeRelationships(source_outcome: LearningOutcome,
   target_outcomes: LearningOutcome[],
   subject_context: string) -> RelationshipExtractionResult {
-  client "anthropic/claude-sonnet-4-20250514"
+  client ExtractEnStrong
   prompt #"You are an expert curriculum analyst specializing in Irish education.
```

(12 more identical hunks follow at the line numbers above.)

### 5.3 Confirm the surrounding functions are unaffected

```bash
# Confirm no other line in curriculum_extraction.baml changed:
git diff --stat cianfhoghlaim/core/baml/_oideachais_src/curriculum_extraction.baml
# → 1 file changed, 14 insertions(+), 14 deletions(-)

# Confirm no test block was broken:
git diff cianfhoghlaim/core/baml/_oideachais_src/curriculum_extraction.baml \
  | grep -E '^[-+].*test '
# → (no test lines changed; tests use named function refs not client names)
```

### 5.4 Adjacent files (32b follow-up, NOT in this PR)

```bash
# Same sed, but for the 15 adjacent inline calls (deferred to refactor 32b):
# cianfhoghlaim/core/baml/_oideachais_src/aistear.baml       (3 calls)
# cianfhoghlaim/core/baml/_oideachais_src/junior_cycle.baml  (3 calls)
# cianfhoghlaim/core/baml/_oideachais_src/primary.baml       (2 calls)
# cianfhoghlaim/core/baml/_oideachais_src/tertiary.baml      (7 calls)
#
# Defer because:
# 1. curriculum_extraction.baml is the highest-call-volume file (the BAML refactor P1-1 target).
# 2. Sister files may have different per-function semantic requirements (aistear uses
#    simpler schema, junior_cycle needs different temperature) — function-by-function review.
# 3. Smaller blast radius for the first PR.
```

### 5.5 Effort

2 hours (15 min sed + 30 min diff review + 1h manual spot-check of 3 random functions + 15 min commit).

---

## 6. Step 4 — Validation (1 hour)

### 6.1 BAML regenerate

```bash
cd cianfhoghlaim/core/baml
baml-cli generate
# → expect "(14 functions regenerated, 0 warnings)"

# Confirm the new client binding is in the generated Python:
rg -l "ExtractEnStrong" cianfhoghlaim/core/baml/_oideachais_src/baml_client/
# → __init__.py, config.py, sync_client.py, etc.
```

### 6.2 Dry-run a representative function

```bash
# Pick a small one (ExtractLearningOutcomeRelationships) and invoke via Python:
cd cianfhoghlaim/core/baml
python -c "
import asyncio
from baml_client import b
from baml_client.types import LearningOutcome

async def main():
    src = LearningOutcome(
        code='M3.1', strand='Number', description_en='Count to 10',
        description_ga='Comhairigh go dtí 10', stage='primary', subject='math'
    )
    result = await b.ExtractLearningOutcomeRelationships(
        source_outcome=src, target_outcomes=[src], subject_context='Primary Mathematics'
    )
    print(result.model_dump_json(indent=2))

asyncio.run(main())
"
# → expect JSON output, no errors
```

### 6.3 Langfuse observability check

```bash
# After running the dry-run, check Langfuse:
open https://langfuse.cianfhoghlaim.ie/traces
# → expect a new trace for `ExtractLearningOutcomeRelationships` with:
#   - model: "extract-en-strong"
#   - input/output tokens populated
#   - cost estimate populated
#   - duration metric
#   (NONE of these would have appeared before the refactor — those calls were invisible.)
```

### 6.4 Compare output to pre-refactor (byte-identical goal)

```bash
# Capture pre-refactor output (do this BEFORE step 3, or use a known-good fixture):
# Run the same 5 functions on the same inputs:
python scripts/curriculum_extraction_smoketest.py > /tmp/before.json

# After refactor, run again:
python scripts/curriculum_extraction_smoketest.py > /tmp/after.json

# Diff (allow JSON-key reorder):
diff <(jq -S . /tmp/before.json) <(jq -S . /tmp/after.json) | head -40
# → expect: empty diff (Sonnet 4 with temperature=0.0 should be byte-identical)
# If non-empty: investigate — could be a prompt-template rendering issue, NOT the client swap.
```

### 6.5 Cost sanity check

```bash
# Before refactor: 14 functions × N calls/day × no tracking = unknown
# After refactor:  open the LiteLLM dashboard
open https://litellm.cianfhoghlaim.ie/dashboard
# → expect: per-model spend breakdown; "anthropic/claude-sonnet-4-20250514" should
#    now appear under the "extract-en-strong" alias (NOT as raw direct calls).
```

### 6.6 Effort

1 hour (15 min regen + 15 min dry-run + 15 min Langfuse check + 15 min smoketest diff).

---

## 7. Step 5 — Rollback (30 min)

### 7.1 If ExtractEnStrong underperforms (quality regression)

The most likely failure mode: a curriculum function that worked at `temperature=0.0` with the direct provider starts producing lower-quality output via the gateway (e.g. because the gateway's `enable_json_schema_validation: true` is wrapping the response in a JSON mode that's slightly different).

**Detection signal:** RAGAS evaluation on the 5th extraction output (per `agent-observability` skill). Drop in `faithfulness < 0.85` or `answer_relevance < 0.80` → revert.

### 7.2 Atomic rollback (one command)

```bash
cd /Users/cianmacandeisigh/dev/kings_college_galway
git revert --no-edit <commit-sha-of-step-3>
# → reverts all 14 line changes in curriculum_extraction.baml
# → does NOT revert the litellm config.yaml change (which is benign — alias still works)

# Optional: also remove the litellm alias (only if alias causes unrelated issue):
# Edit config.yaml to delete the extract-en-strong block, then:
docker compose -f infrastructure/stacks/litellm/compose.yaml restart litellm
```

### 7.3 Granular rollback (per-function)

If only 1-2 of the 14 functions misbehave (e.g. `LazyExtractExamPaper` is fine but `ExtractExamPaperMarkingScheme` is broken):

```bash
# Revert just the broken function:
git checkout HEAD~1 -- cianfhoghlaim/core/baml/_oideachais_src/curriculum_extraction.baml
# Edit by hand to keep ExtractEnStrong for the working functions and revert just the broken one.
# (1 function = 1 line = 30 seconds.)
```

### 7.4 Tag the refactor for easy cherry-pick

```bash
git tag -a refactor/32-baml-inline-clients-fix-2026-06-29 \
  -m "P1-1: migrate 14 inline anthropic/claude-sonnet-4-20250514 to ExtractEnStrong"
```

### 7.5 Effort

30 min (write the rollback plan + tag the commit; the actual rollback is 1 command).

---

## 8. Step 6 — Post-fix observability (ongoing)

### 8.1 Verify each call now traces to Langfuse

After deploying, every call to one of the 14 migrated functions should produce a Langfuse span with:
- `name: ExtractLearningOutcomeRelationships` (or whatever the function is)
- `model: extract-en-strong` (NOT `anthropic/claude-sonnet-4-20250514`)
- `latency_seconds`, `input_tokens`, `output_tokens`, `cost_usd` populated
- A `generation` child span (NOT a `http_request` to `api.anthropic.com` directly)

Spot-check 3 of the 14 functions per day for the first week:
```bash
# Pick 3 random function names from the migrated set:
FUNCS=("ExtractLearningOutcomeRelationships" "LazyExtractExamPaper" "ExtractExamPaperMarkingScheme")
for F in "${FUNCS[@]}"; do
    rg -l "function $F" cianfhoghlaim/core/baml/_oideachais_src/curriculum_extraction.baml
    # Manually invoke via Dagster UI → Asset materialization → check Langfuse
done
```

### 8.2 Verify the fallback chain participates

To confirm `extract-en-strong` actually falls back when Anthropic is down, simulate a 429:

```bash
# In test mode only, force the anthropic provider to 503:
# (Use the existing `minimax_alias_health` Dagster asset check at
#  cianfhoghlaim/assets/_oideachais_dagster_defs/assets/llm_gateway_assets.py:200-215
#  as a template — copy the pattern to `extract_en_strong_alias_health`.)
```

### 8.3 Verify spend caps are enforced

The LiteLLM dashboard now tracks `extract-en-strong` spend. Set a hard cap:

```yaml
# In infrastructure/stacks/litellm/config/config.yaml under general_settings:
general_settings:
  max_budget: 200  # USD per day; matches KCG platform default
  budget_duration: 1d
  alerting: ["slack://kcg-llm-spend"]
```

This was impossible when the 14 functions hit Anthropic directly (LiteLLM was bypassed entirely).

### 8.4 Add the migration to the BAML skill

Update `.agents/skills/baml/SKILL.md` Pattern 1 (which currently uses inline `client "openai/gpt-4o-mini"` as the example — should switch to named `client ExtractEn` per refactor P3-20 in `synthesis/26-refactor-prioritizer.md:152`). This is the agent-facing prevention step.

### 8.5 Effort

Ongoing (15 min first-week spot-check + 1h write the `extract_en_strong_alias_health` asset check + 30 min skill update).

---

## Appendix A — Files modified by this refactor

| File | Lines changed | Nature |
|:--|:-:|:--|
| `infrastructure/stacks/litellm/config/config.yaml` | +13 / -0 | New `extract-en-strong` alias (block after L612) |
| `cianfhoghlaim/core/baml/_oideachais_src/curriculum_extraction.baml` | +14 / -14 | All 14 inline clients → `client ExtractEnStrong` |
| `cianfhoghlaim/core/baml/_oideachais_src/baml_client/` | regenerated | `baml-cli generate` output |
| **Total LOC** | **+27 / -14 = +13 net** | |

## Appendix B — Adjacent scope (deferred to 32b/32c)

| Refactor | File | Inline clients | Replacement |
|:--|:--|:-:|:--|
| 32b | `aistear.baml` | 3 | `client ExtractEn` (lightweight, not Strong) |
| 32b | `junior_cycle.baml` | 3 | `client ExtractEnStrong` |
| 32b | `primary.baml` | 2 | `client ExtractEnStrong` |
| 32b | `tertiary.baml` | 7 | `client ExtractEnStrong` (or new `ExtractTertiary`) |
| 32c | `isles_education.baml` | 6 (`openai/gpt-4o*`) | `client ExtractEn` or new `ExtractEnCrossBorder` |

These are 1-PR-each follow-ups; the 14-call surgical fix here validates the pattern.

## Appendix C — Why not just delete the 14 inline calls entirely?

Two reasons:
1. **`ExtractEnStrong` is not a drop-in for every curriculum function.** Some functions may need `ExtractEn` (lighter, Gemini 2.5 Flash) for speed. Per-function semantic review is needed.
2. **The LiteLLM alias must exist first** — otherwise the BAML regenerate produces a config that 404s at runtime. §4.2 must land before §5.1.

## Appendix D — Effort summary

| Step | Task | Hours |
|:-:|:--|:-:|
| 1 | Locate (grep + ccc + inventory) | 1.0 |
| 2 | Canonical replacement (alias + smoke test) | 2.0 |
| 3 | Surgical replacement (sed + diff) | 2.0 |
| 4 | Validation (regen + dry-run + Langfuse + smoketest) | 1.0 |
| 5 | Rollback plan + tag | 0.5 |
| 6 | Post-fix observability (first week + asset check + skill) | ~2.0 |
| **Total** | | **~8.5h** |

P1-1 "M effort" per `synthesis/26-refactor-prioritizer.md:59`. Cross-spec impact: no spec deltas required (the gap was implementation, not spec); new `openspec/changes/2026-06-29-baml-inline-clients-fix/` change folder with `proposal.md` + `tasks.md` only.

---

## Summary (1 paragraph)

`cianfhoghlaim/core/baml/_oideachais_src/curriculum_extraction.baml` contains **14 inline `client "anthropic/claude-sonnet-4-20250514"` calls** (not 8 as previously audited — additional sites at L501, 541, 579, 617, 653, 775, 973, 1008, 1047) that bypass the LiteLLM gateway and therefore miss the 7-tier `minimax` fallback chain, the `num_retries: 3` retry policy, the Langfuse v2 callback trace, the `enable_json_schema_validation: true` strict mode, and the spend-tracking dashboard — defeating the Phase 0.4 `litellm-minimax-vendor-derisking` goal. The canonical `ExtractEnStrong` named client is defined at `_oideachais_src/clients.baml:256` but its target alias `extract-en-strong` is **not yet registered** in `infrastructure/stacks/litellm/config/config.yaml` (only `extract` at L604 and `minimax` at L714 are present), so a naive sed would produce a config that 404s at runtime. The 8.5-hour surgical fix is: (1) add the `extract-en-strong` alias with 3-tier fallback to `config.yaml:612`, (2) `sed -i 's|client "anthropic/claude-sonnet-4-20250514"|client ExtractEnStrong|g'` across all 14 sites, (3) `baml-cli generate` + dry-run `ExtractLearningOutcomeRelationships` + confirm Langfuse trace appears with `model: extract-en-strong`, (4) rollback is a single `git revert` (the alias addition is benign), and (5) adjacent scope — 15 more inline calls in `aistear.baml`/`junior_cycle.baml`/`primary.baml`/`tertiary.baml` and 6 `openai/gpt-4o*` calls in `isles_education.baml` — is the same surgery in 1-PR-each follow-up refactors (32b/32c). P1-1 in `synthesis/26-refactor-prioritizer.md:59`; runtime-breaking C-3.2 in `synthesis/28-misunderstandings-corrector.md:222`.
