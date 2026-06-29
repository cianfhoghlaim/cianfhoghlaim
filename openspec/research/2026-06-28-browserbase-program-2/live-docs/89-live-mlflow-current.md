# 89-live-mlflow-current.md

> Live verification of MLflow docs & PyPI on 2026-06-29 (Agent 89)
> Tools used: webfetch (PyPI JSON, GitHub releases), firecrawl_scrape (tracking.html, model-registry.html), chrome (PyPI JSON eval), ccc (code search)
> **NO browserbase** (per task constraint)

## 1. TL;DR (3 lines)

- **MLflow 3.14.0** is the current release on PyPI, uploaded **2026-06-17 07:57:42 UTC** (10 days before this report); GitHub tag `v3.14.0` matches.
- The Wave 1 skill file (`.agents/skills/mlflow/SKILL.md`, "Version: 3.x | Last Updated: 2025-01") is **~18 months stale** — it predates the new `models:/<model_id>` URI, `mlflow.search_logged_models`, `mlflow.create_external_model`, the entire `mlflow.genai` module, the `@mlflow.test` pytest marker, the `mlflow agent setup` CLI, Review Queues, and the LLM Playground.
- Three breaking changes shipped in v3.14.0 (sklearn/pytorch/lightgbm `serialization_format` defaults) are **not reflected** in the skill and will break any `mlflow.sklearn.log_model` call that relied on the old `cloudpickle` default.

## 2. Current Version (PyPI) + Release Date

Pulled live from `https://pypi.org/pypi/mlflow/json` via Chrome `fetch()`:

| Field | Value |
|---|---|
| Package | `mlflow` |
| Latest version | **`3.14.0`** |
| Upload time (PyPI) | `2026-06-17T07:57:42` |
| GitHub tag | `v3.14.0` (commit `86cd7f5`, tagger `harupy`) |
| Requires Python | `>=3.10` |
| Total releases on PyPI | 182 |
| Project URLs | docs=https://mlflow.org/docs/latest • repo=https://github.com/mlflow/mlflow |

Recent 3.x timeline (last 10 PyPI uploads):

| Version | Upload date |
|---|---|
| 3.14.0 | 2026-06-17 |
| 3.13.0 | 2026-06-01 |
| 2.22.5 | 2026-05-12 (LTS) |
| 3.12.0 | 2026-05-05 |
| 3.11.1 | 2026-04-07 |
| 3.11.0 | 2026-04-07 |

## 3. Verbatim Code Examples (5-10)

All copied from the live `mlflow.org/docs/latest/...` pages, not from the skill file.

### 3.1 `mlflow.start_run` + `log_param` / `log_metric` (Tracking docs)

```python
import mlflow

with mlflow.start_run():
    mlflow.log_param("lr", 0.001)
    # Your ml code
    ...
    mlflow.log_metric("val_loss", val_loss)
```

> URL: `https://mlflow.org/docs/latest/tracking.html` (section "Tracking Runs")

### 3.2 Auto-logging (Tracking docs)

```python
import mlflow

mlflow.autolog()

# Your training code...
```

> Note from docs: "Auto-logging supports popular libraries such as Scikit-learn, XGBoost, PyTorch, Keras, Spark, and more."

### 3.3 `mlflow.search_logged_models` — NEW in MLflow 3

```python
import mlflow

# Find high-performing models across experiments
top_models = mlflow.search_logged_models(
    experiment_ids=["1", "2"],
    filter_string="metrics.accuracy > 0.95 AND params.model_type = 'RandomForest'",
    order_by=[{"field_name": "metrics.f1_score", "ascending": False}],
    max_results=5,
)

# Load the best model directly
loaded_model = mlflow.pyfunc.load_model(f"models:/{best_model.model_id}")
```

> Docs: "MLflow 3 introduces powerful model search capabilities through `mlflow.search_logged_models()`."

### 3.4 Model checkpoints with `step=` + linked metrics (Tracking docs — MLflow 3)

```python
import mlflow
import mlflow.pytorch

with mlflow.start_run() as run:
    for epoch in range(100):
        # Train your model
        train_model(model, epoch)
        # Log model checkpoint every 10 epochs
        if epoch % 10 == 0:
            model_info = mlflow.pytorch.log_model(
                pytorch_model=model,
                name=f"checkpoint-epoch-{epoch}",
                step=epoch,
                input_example=sample_input,
            )
            accuracy = evaluate_model(model, validation_data)
            mlflow.log_metric(
                key="accuracy",
                value=accuracy,
                step=epoch,
                model_id=model_info.model_id,  # Link metric to specific model
                dataset=validation_dataset,
            )
```

### 3.5 New `models:/<model_id>` URI (Tracking docs — MLflow 3)

```python
# New MLflow 3 model URI format
model_uri = f"models:/{model_info.model_id}"
loaded_model = mlflow.pyfunc.load_model(model_uri)

# This replaces the older run-based URI format:
# model_uri = f"runs:/{run_id}/model_path"
```

### 3.6 `mlflow.register_model` (Model Registry docs)

```text
# Option 1: specify `registered_model_name` parameter when logging a model
mlflow.<flavor>.log_model(..., registered_model_name="<YOUR_MODEL_NAME>")

# Option 2: register a logged model
mlflow.register_model(model_uri="<YOUR_MODEL_URI>", name="<YOUR_MODEL_NAME>")
```

### 3.7 Loading a registered model (Model Registry docs)

```text
mlflow.<flavor>.load_model("models:/<YOUR_MODEL_NAME>/<YOUR_MODEL_VERSION>")
```

### 3.8 Model Aliases (Model Registry docs)

> "Model aliases allow you to assign a mutable, named reference to a particular version of a registered model. […] you can use the alias to refer to that model version via a model URI or the model registry API. […] `models:/MyModel@champion`. […] `models:/MyModel@production`."

### 3.9 Databricks UC registry URI (Model Registry docs)

```python
import mlflow

mlflow.set_registry_uri("databricks-uc")
```

### 3.10 `mlflow.create_external_model` (NEW since MLflow 3 — Model Registry docs)

> "An MLflow Model is created with one of the model flavor's `mlflow.<model_flavor>.log_model()` methods, or `mlflow.create_external_model()` API **since MLflow 3**."

## 4. Changelog Since Wave 1

Wave 1 snapshot (from skill file header) = MLflow 3.x at 2025-01. Releases since then (PyPI + GitHub release notes for v3.14.0):

### v3.14.0 (2026-06-17) — major release
> "MLflow 3.14.0 includes several major features and improvements"
> *Source: `https://github.com/mlflow/mlflow/releases/tag/v3.14.0`*

**Major new features:**
- 🚀 `mlflow agent setup` — one-command agent onboarding for Claude Code / OpenAI Codex / OpenCode (installs + writes skills to `.agents/skills`)
- ⚡ WAL-based durable Claude Code tracing (`MlflowWalSpanExporter`, #23641)
- 📝 Review Queues for traces — assign traces to reviewers/agents, collect structured feedback, write to trace
- 🗂️ Revamped evaluation dataset UI (Dataset v2, #23560)
- 🧪 `@mlflow.test` pytest marker for GenAI regression tests (#23864, #23869, #23985)
- 🎛️ LLM Playground (browser iteration over AI Gateway + Prompt Registry) (#23273)

**Breaking changes (v3.14.0):**
- `#23987` `mlflow.sklearn` `serialization_format` default `cloudpickle` → `skops`
- `#23988` `mlflow.pytorch.log_model` / `save_model` `serialization_format` default → `pt2`
- `#23986` `mlflow.lightgbm` `serialization_format` default → `skops`

**Other notable additions:**
- `MLFLOW_GENAI_JUDGE_DEFAULT_MODEL` env var (#23860)
- Google ADK LLM judge scorers — Hallucination / Safety / ResponseEvaluation (#22496)
- OTLP trace ingestion now supports `x-mlflow-run-id` header (#23664)
- `gen_ai.conversation.id` mapped to MLflow trace session (#23584)
- `/responses/compact` passthrough route in AI Gateway (#23353)
- Rule-based scorers: `RegexMatch`, `PIIDetection`, `ResponseLength` (#22571)
- 21 new models added to Databricks model catalog (#23520)

### v3.13.0 (2026-06-01) — mid-cycle
(Detail in release notes; the v3.14.0 notes reference `EvaluationResult.passed/.reason`, dataset v2 port, label schemas.)

### v3.12.0 (2026-05-05)
Referenced indirectly by v3.14.0 changelog (label schema entity / validation / SQL store, #23597).

### v3.11.0 (2026-04-07) + 3.11.1
> Released the same day; 3.11.1 is a hotfix.

### v2.22.5 (2026-05-12) — LTS branch
2.x line still receives security/LTS patches in parallel with 3.x.

## 5. Drift Items vs Wave 1 (skill file)

| # | Wave 1 skill says | Current (v3.14.0) reality | Source |
|---|---|---|---|
| 1 | "Version: 3.x \| Last Updated: 2025-01" | **v3.14.0, 2026-06-17** — 18 months stale | PyPI JSON |
| 2 | `mlflow.pytorch.log_model(pytorch_model, "model", registered_model_name="...")` | New `step=`, `model_id`, `name=` (replaces positional artifact path) | tracking.html |
| 3 | `mlflow.log_metric("accuracy", 0.95)` | Now accepts `step=`, `model_id=`, `dataset=` for per-checkpoint + per-dataset attribution | tracking.html |
| 4 | (no mention) | `mlflow.search_logged_models()` — SQL-like filter across experiments | tracking.html |
| 5 | `models:/my-classifier/1` (version) or `models:/my-classifier@production` (alias) | New **third** form: `models:/<model_id>` for direct ID-based loading | tracking.html |
| 6 | `runs:/<run_id>/model_path` | **Deprecated for tracked models** — docs say "this replaces the older run-based URI format" | tracking.html |
| 7 | "Model is created with `mlflow.<flavor>.log_model()`" | **+ `mlflow.create_external_model()` since MLflow 3** | model-registry.html |
| 8 | `mlflow.set_prompt_alias(name, alias, version=3)` | Still valid; now also exposed via Prompt Playground UI (#24021) | release notes |
| 9 | (no agent onboarding) | `mlflow agent setup` CLI ships skills to `.agents/skills` for Claude Code / OpenAI Codex / OpenCode | release notes |
| 10 | (no review queues) | Review Queues with assignment, schema-based questions, deep links | release notes |
| 11 | (no pytest integration) | `@mlflow.test` marker for GenAI regression tests + `EvaluationResult.passed`/`.reason` | release notes |
| 12 | (no LLM Playground) | Browser-based playground over AI Gateway + Prompt Registry | release notes |
| 13 | Default sklearn serialization = `cloudpickle` | **Default flipped to `skops` in v3.14.0** ⚠️ breaking | release notes #23987 |
| 14 | Default pytorch serialization = `cloudpickle` | **Default flipped to `pt2` in v3.14.0** ⚠️ breaking | release notes #23988 |
| 15 | Default lightgbm serialization = `cloudpickle` | **Default flipped to `skops` in v3.14.0** ⚠️ breaking | release notes #23986 |
| 16 | Datadog FastAPI middleware pattern | Local code `cianfhoghlaim/core/obs/observability/mlflow_config.py` still uses `runs:/<run_id>/model` URI for registration — should migrate to `models:/<model_id>` for MLflow 3 | ccc search |
| 17 | (no mention of Google ADK) | Google ADK LLM judge scorers added in v3.14.0 (Hallucination, Safety, ResponseEvaluation) — directly relevant to KCG agent stack | release notes #22496 |

## 6. Skill File Update Diffs

Proposed diffs to `.agents/skills/mlflow/SKILL.md` (not applied — report only):

```diff
- **Version:** 3.x | **Last Updated:** 2025-01
+ **Version:** 3.14.0 | **Last Updated:** 2026-06-29
+ **Python:** >=3.10 | **PyPI releases:** 182 (latest 3.14.0 on 2026-06-17)
+ **LTS branch:** 2.22.5 (2026-05-12)
```

```diff
+ ## MLflow 3 — What's New
+
+ - **`mlflow.search_logged_models()`** — SQL-like filter across experiments
+ - **`mlflow.create_external_model()`** — register models trained outside MLflow
+ - **`models:/<model_id>` URI** — direct ID-based model loading (replaces `runs:/<run_id>/path`)
+ - **Checkpoint-aware `log_metric`** — `step=`, `model_id=`, `dataset=` args
+ - **`mlflow agent setup`** — installs `.agents/skills` for Claude Code / Codex / OpenCode
+ - **`@mlflow.test`** — pytest marker for GenAI regression tests
+ - **Review Queues** — assign traces to reviewers, collect structured feedback
+ - **LLM Playground** — browser iteration over AI Gateway + Prompt Registry
+ - **WAL tracing** — durable, low-latency Claude Code traces
+
+ ## v3.14.0 Breaking Changes
+
+ - `mlflow.sklearn` `serialization_format` default: `cloudpickle` → `skops` (#23987)
+ - `mlflow.pytorch.log_model` / `save_model` default → `pt2` (#23988)
+ - `mlflow.lightgbm` default → `skops` (#23986)
+ → Pin `serialization_format="cloudpickle"` explicitly if you need the old behavior.
```

```diff
+ ### MLflow 3 — Model Checkpoint Logging
+
+ ```python
+ with mlflow.start_run() as run:
+     for epoch in range(100):
+         if epoch % 10 == 0:
+             model_info = mlflow.pytorch.log_model(
+                 pytorch_model=model,
+                 name=f"checkpoint-epoch-{epoch}",
+                 step=epoch,
+             )
+             mlflow.log_metric(
+                 "accuracy", value, step=epoch,
+                 model_id=model_info.model_id,
+                 dataset=validation_dataset,
+             )
+
+ # Load by model_id (new URI form)
+ loaded = mlflow.pyfunc.load_model(f"models:/{model_info.model_id}")
+
+ # Search logged models across experiments
+ top = mlflow.search_logged_models(
+     experiment_ids=["1"],
+     filter_string="metrics.accuracy > 0.9",
+     order_by=[{"field_name": "metrics.accuracy", "ascending": False}],
+     max_results=1,
+     output_format="list",
+ )[0]
+ ```
```

```diff
+ ### MLflow 3 — External Model Registration
+
+ ```python
+ import mlflow
+ mlflow.create_external_model(name="my-external-model")
+ ```
```

```diff
- | LangChain | `mlflow.langchain.autolog()` | 2.14.0 |
- | OpenAI | `mlflow.openai.autolog()` | 2.14.0 |
+ | LangChain | `mlflow.langchain.autolog()` | 2.14.0+ |
+ | OpenAI | `mlflow.openai.autolog()` | 2.14.0+ |
+ | Google ADK | `mlflow.google_adk.autolog()` | 3.0+ (judge scorers in 3.14.0) |
+ | OpenAI Agents SDK | `mlflow.openai_agents.autolog()` | 3.0+ |
```

```diff
  ## Best Practices
+ 6. **MLflow 3 model_id URIs**: prefer `models:/<model_id>` over `runs:/<run_id>/path` for new code
+ 7. **Serialization pinning**: set `serialization_format` explicitly on `log_model` calls in v3.14.0+ to avoid the default flip
+ 8. **Local KCG code**: `cianfhoghlaim/core/obs/observability/mlflow_config.py` should migrate `runs:/{run_id}/model` → `models:/{model_info.model_id}` for MLflow 3
```

## 7. Cross-Reference: KCG Local Code Touches MLflow

From `ccc search` (5 hits):

| File | Use |
|---|---|
| `cianfhoghlaim/core/obs/observability/mlflow_config.py` | Logs to MLflow Model Registry; deployed at `mlflow.cianfhoghlaim.ie`; still uses `runs:/{run_id}/model` URI |
| `cianfhoghlaim/core/obs/observability/__init__.py` | Exports `log_model_to_registry`, `setup_experiment`, etc. |
| `cianfhoghlaim/core/obs/observability/fastapi_middleware.py` | ML pipeline metrics middleware (HTR / TTS / curriculum / etc.) — orthogonal to MLflow changes |

**Action item for build agent:** the `log_model_to_registry` helper in `mlflow_config.py:445-473` should be updated to:
1. Use `mlflow.pyfunc.load_model` with the new `models:/<model_id>` URI.
2. Pin `serialization_format="cloudpickle"` if any downstream consumer expects unpicklable sklearn models, OR test the `skops` path.
3. Consider `mlflow.search_logged_models()` for the model-selection step (currently it does manual `register_model`).

## Sources (URLs)

- `https://pypi.org/pypi/mlflow/json` (live JSON, fetched via Chrome `fetch()`)
- `https://mlflow.org/docs/latest/tracking.html` (firecrawl scrape, 200 OK)
- `https://mlflow.org/docs/latest/model-registry.html` (firecrawl scrape, 200 OK)
- `https://github.com/mlflow/mlflow/releases` (webfetch, tag `v3.14.0`)
- `.agents/skills/mlflow/SKILL.md` (Wave 1 baseline, 407 lines)
- `openspec/research/2026-06-28-browserbase-program-2/agent-21-huggingface.md` (refs MLflow as observability)
- `openspec/research/2026-06-28-browserbase-program-2/features/41-agent-observability.md` (mentions MLflow)
- `openspec/research/2026-06-28-browserbase-program-2/synthesis/27-feature-backlog.md` (cites MLflow)
