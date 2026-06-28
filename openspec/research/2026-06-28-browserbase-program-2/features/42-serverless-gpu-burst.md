# F-42 · Serverless GPU Burst — Modal A100/H100 for Unsloth >26B

**Agent:** 42 of 43 (BrowserBase Program 2, Wave 3 — `serverless-gpu-burst`)
**Date:** 2026-06-29 · **Status:** design spec, ready for review
**Source files consulted:** `agent-19-unsloth.md` (306 L), `agent-20-mlx-omni.md` (204 L), `synthesis/27-feature-backlog.md:54-59` (F-04 P0), `cianfhoghlaim/ocr/training/modal_finetune/modal_finetune/finetune_irish.py` (392 L)
**Cross-refs:** `openspec/changes/2026-06-28-browserbase-phase-2-decisions/specs/meaisinfhoghlaim-platform/spec.md:35-39`, `agent-19:54-68` (Gemma 4 FastModel + train_on_responses_only), `agent-20:158-160` (M-series 36 GB cap)
**Credits used:** ~0 (all context from Wave-1 outputs + local file read; no live browser)

---

## 1. TL;DR

Wrap the existing `UnslothTrainer` (Agent 19's 11 OCR models) with a **Modal app** that bursts to **A100-40GB / A100-80GB / H100-80GB** on demand when **model params > 26 B** OR **estimated VRAM > 30 GB** (exceeds the M4 Max 36 GB cap from Agent 20). The Modal app is a thin decorator over `UnslothConfig.for_gaelic_ocr()` — it adds GPU selection, a 4 h timeout, an `infisical-modal` secret for HF/MLflow/Dagster-Pipes, and a `unsloth-burst-checkpoints` Modal Volume. Cost is **$1.50-3.00/hr**; a Gemma 4 26B QLoRA fine-tune = 2-3 h = **$3-9/run**; budget is **$150/mo soft cap + $200/mo Modal workspace cap ≈ 50 burst runs**. Fallback is the local M4 Max with `train_on_responses_only` **disabled** (saves ~10% activation memory). Cutover: deploy to bunchloch → 5-step smoke test → 1 Gemma 4 26B pilot → verify model in MLflow registry.

---

## 2. When to burst — trigger conditions

The Dagster asset `modal_unsloth_decision_asset` decides **local vs. burst** via a static `BURST_THRESHOLDS` tuple evaluated against three signals:

| Trigger | Threshold | Example |
|:--|:--|:--|
| **Parameter count** | `params_b > 26.0` | Gemma 4 31B, Qwen3.6 35B-A3B |
| **Estimated VRAM (4-bit QLoRA)** | `(params_b × 0.75) + 8 GB + shard_gb > 30 GB` | 31B → 32.75 GB → burst |
| **Seq length or batch size** | `seq > 8192` OR `batch > 2` | 26B w/ seq=16k → burst |
| **Force flag** | `UNSLOTH_FORCE_BURST=1` | operator override |

**Static lookup** (`cianfhoghlaim/ocr/training/training/burst_thresholds.py`):

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class BurstThreshold:
    model_pattern: str
    params_b: float
    estimated_vram_4bit_gb: float
    seq_length: int
    burst_gpu: str        # "A100-40GB" | "A100-80GB" | "H100"
    local_max_steps_cap: int | None
    notes: str

BURST_THRESHOLDS: tuple[BurstThreshold, ...] = (
    BurstThreshold("unsloth/gemma-4-26B-A4B-it", 26.0, 27.5, 8192,
                   "A100-40GB", 100, "MoE; 4B active; marginal on M4 Max"),
    BurstThreshold("unsloth/gemma-4-31B-it",      31.0, 31.3, 8192,
                   "A100-80GB", None,  "31B dense; exceeds 36GB → always burst"),
    BurstThreshold("unsloth/Qwen3.6-27B-it",      27.0, 28.3, 16384,
                   "A100-40GB", None,  "27B + 16k ctx → always burst"),
    BurstThreshold("unsloth/Qwen3.6-35B-A3B-it",  35.0, 34.3, 16384,
                   "A100-80GB", None,  "MoE 35B/3B; long ctx → always burst"),
    BurstThreshold("unsloth/Qwen2.5-VL-72B-it",   72.0, 62.0, 4096,
                   "H100",       None,  "72B vision; only H100 80GB"),
    BurstThreshold("Qwen3-Reranker-8B*",            8.0,  6.0, 4096,
                   "A100-40GB",  None,  "custom head full-FT → burst"),
)
```

The decision is logged to MLflow as a `burst_decision` tag (`{reason, gpu, estimated_vram_4bit_gb, force}`) for audit. Pattern `model_name` against `BURST_THRESHOLDS[i].model_pattern`; if unknown model, default to **local first** (200 step cap). Full decision algorithm is a 12-line `should_burst()` helper at the top of the burst asset (see §4).

---

## 3. Modal app spec

**New file:** `cianfhoghlaim/ocr/training/modal_finetune/modal_finetune/burst_unsloth.py`
(Co-located with the existing `finetune_irish.py`; **does not** replace it — the A10G path stays for ≤ 13B models.)

**Skeleton (full implementation in the new file):**

```python
# cianfhoghlaim/ocr/training/modal_finetune/modal_finetune/burst_unsloth.py
"""Modal GPU Burst: Unsloth fine-tunes for >26B models.
Cost (modal.com/pricing 2026-06, per-second, 1-min min):
    A100-40GB $1.50/hr → Gemma 4 26B = 2-3h = $3-4.50/run
    A100-80GB $2.00/hr → Gemma 4 31B = 3-4h = $6-8/run
    H100-80GB $3.00/hr → Qwen3.6 35B / Qwen2.5-VL 72B = 4-6h = $12-18/run
Budget: $150/mo soft + $200/mo Modal workspace = ~50 runs/mo."""
import os, time, modal

app = modal.App("unsloth-burst-gpu")
training_image = (modal.Image.debian_slim(python_version="3.12").pip_install(
    "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git",
    "torch>=2.5.0", "transformers>=4.52.0", "datasets>=3.2.0",
    "accelerate>=1.0.0", "peft>=0.13.0", "bitsandbytes>=0.45.0",
    "trl>=0.12.0", "huggingface_hub>=0.27.0",
    "mlflow>=2.20.0", "dagster-pipes>=0.2.0",  # no WandB (Agent 19 anti-pattern)
).env({"HF_HUB_DISABLE_PROGRESS_BARS": "1", "TOKENIZERS_PARALLELISM": "false"}))
checkpoint_volume = modal.Volume.from_name("unsloth-burst-checkpoints", create_if_missing=True)

# Per-GPU functions; burst_finetune body is shared, dispatch via @app.local_entrypoint
@app.function(
    image=training_image,
    gpu=modal.gpu.A100(count=1, size="40GB"),
    timeout=60 * 60 * 4,                        # 4h hard cap (was 8h in finetune_irish.py)
    volumes={"/models": checkpoint_volume},
    secrets=[modal.Secret.from_name("infisical-modal")],  # HF_TOKEN, MLFLOW_TRACKING_URI
    retries=modal.Retries(max_retries=1, backoff_coefficient=2.0),
    max_containers=2,
)
def burst_finetune(model_name, dataset_path, max_steps=500, learning_rate=2e-4,
                   lora_r=16, lora_alpha=16, seq_length=4096, batch_size=2,
                   gradient_accumulation_steps=4, output_subdir="burst_run",
                   dagster_pipes_context=None) -> dict:
    # (full body: MLflow setup → FastModel.from_pretrained → FastModel.get_peft_model
    #  → Gemma 4 num_kv_shared_layers=0 fix → get_chat_template per family
    #  → SFTTrainer + train_on_responses_only (Agent 19 +1% accuracy booster)
    #  → save_pretrained_gguf UD-Q4_K_XL → mlflow.register_model
    #  → Dagster Pipes report_asset_materialization)
    # Key defaults inherited from UnslothConfig.for_gaelic_ocr() pattern:
    #   random_state=3407 (not 42), use_gradient_checkpointing="unsloth" (not True),
    #   weight_decay=0.01 (not 0.001), optim="adamw_8bit", bf16=True, seed=3407
    ...  # see spec §3 reference impl
    return {"status": "ok", "output_dir": f"/models/{output_subdir}",
            "hours": hours, "cost_usd": hours * 1.50}

@app.function(image=training_image, gpu=modal.gpu.A100(count=1, size="80GB"),
              timeout=60*60*4, volumes={"/models": checkpoint_volume},
              secrets=[modal.Secret.from_name("infisical-modal")],
              retries=modal.Retries(max_retries=1), max_containers=2)
def burst_finetune_80gb(**kw):  return burst_finetune(**kw)  # Gemma 4 31B, Qwen3.6 35B

@app.function(image=training_image, gpu=modal.gpu.H100(count=1),
              timeout=60*60*4, volumes={"/models": checkpoint_volume},
              secrets=[modal.Secret.from_name("infisical-modal")],
              retries=modal.Retries(max_retries=1), max_containers=1)
def burst_finetune_h100(**kw):  return burst_finetune(**kw)  # Qwen2.5-VL 72B

@app.local_entrypoint()
def main(model_name, dataset_path, max_steps=500):
    from cianfhoghlaim.ocr.training.training.burst_thresholds import BURST_THRESHOLDS
    import fnmatch
    gpu = next((t.burst_gpu for t in BURST_THRESHOLDS
                if fnmatch.fnmatch(model_name, t.model_pattern)), "A100-40GB")
    fn = {"A100-40GB": burst_finetune, "A100-80GB": burst_finetune_80gb,
          "H100": burst_finetune_h100}[gpu]
    print(f"Burst routing: {model_name} → {gpu}")
    print(fn.remote(model_name=model_name, dataset_path=dataset_path, max_steps=max_steps))
```

**Full implementation** (≈ 130 LoC inside `burst_finetune` body) reuses the Agent 19 canonical pattern at `agent-19-unsloth.md:38-97` verbatim: `FastModel.from_pretrained` → `FastModel.get_peft_model` (with `finetune_vision_layers=False` for text-only burst) → `get_chat_template("gemma-4-thinking" | "qwen2.5" | "chatml")` → `SFTTrainer(SFTConfig(...))` → wrap with `train_on_responses_only` (instruction_part + response_part per family) → `model.save_pretrained_gguf(quantization_method="UD-Q4_K_XL")` → `mlflow.register_model` + Dagster Pipes `report_asset_materialization`. The Gemma 4 26B/31B upstream `num_kv_shared_layers=0` IndexError fix is applied conditionally.

**Infisical → Modal secret bridge** (one-time): `./scripts/sync_infisical_to_modal.sh`
reads `dev-baile/modal/{HF_TOKEN,MLFLOW_TRACKING_URI,DAGSTER_PIPES_CONTEXT}` and
calls `modal secret create infisical-modal` with the exported env vars.
Modal workspace `spend_limit=$200/mo` is set in the Modal dashboard.

---

## 4. Trigger from Cianfhoghlaim

**New Dagster asset** at `cianfhoghlaim/assets/_meaisinfhoghlaim_dagster_defs/assets/burst_finetune.py`:

```python
import os, base64, json, subprocess
import fnmatch
from datetime import datetime
from dagster import asset, Config, MaterializeResult, Failure, sensor, RunRequest
from pydantic import Field
import mlflow
from cianfhoghlaim.ocr.training.training.burst_thresholds import (
    BURST_THRESHOLDS, BurstDecision,
)

class BurstFinetuneConfig(Config):
    model_name: str = "unsloth/gemma-4-26B-A4B-it"
    dataset_path: str = "/stedding/huggingface/datasets/irish_ocr_v3"
    max_steps: int = Field(default=500, ge=10, le=2000)
    seq_length: int = 4096
    batch_size: int = 2
    force_burst: bool = False

def should_burst(model_name, batch_size, seq_length, force=False) -> BurstDecision:
    if force or os.getenv("UNSLOTH_FORCE_BURST") == "1":
        return BurstDecision(burst=True, reason="force_flag", gpu="A100-40GB")
    for t in BURST_THRESHOLDS:
        if fnmatch.fnmatch(model_name, t.model_pattern):
            vram_ok = t.estimated_vram_4bit_gb > 30.0
            seq_ok  = seq_length > 8192 or t.seq_length > 8192
            batch_ok = batch_size > 2
            if vram_ok or seq_ok or batch_ok or t.local_max_steps_cap is None:
                return BurstDecision(burst=True, reason=t.notes, gpu=t.burst_gpu)
            return BurstDecision(burst=False, reason="within_M4_Max_36GB",
                                 local_max_steps=t.local_max_steps_cap)
    return BurstDecision(burst=False, reason="unknown_model_default_local",
                         local_max_steps=200)

@asset(group_name="meaisinfhoghlaim", compute_kind="modal")
def modal_unsloth_decision_asset(context, config: BurstFinetuneConfig):
    decision = should_burst(config.model_name, config.batch_size,
                            config.seq_length, force=config.force_burst)
    context.add_output_metadata({
        "model_name": config.model_name, "burst": decision.burst,
        "reason": decision.reason, "gpu": decision.gpu if decision.burst else None,
    })

    if decision.burst:
        # Soft $150/mo spend guard
        month_key = datetime.utcnow().strftime("%Y-%m")
        runs = mlflow.search_runs(
            experiment_names=["unsloth-burst-gpu"],
            filter_string=f"tags.month = '{month_key}'", max_results=1000)
        spent = runs["metrics.estimated_cost_usd"].sum() if len(runs) else 0
        if spent > 150:
            raise Failure(f"Modal burst budget exceeded: ${spent:.2f} > $150 this month")
        # Dispatch
        ctx_blob = base64.b64encode(json.dumps({
            "run_id": context.run_id, "asset_key": list(context.asset_key.path),
        }).encode()).decode()
        modal_fn = {"A100-40GB": "burst_finetune", "A100-80GB": "burst_finetune_80gb",
                    "H100": "burst_finetune_h100"}[decision.gpu]
        try:
            subprocess.run([
                "modal", "run",
                "cianfhoghlaim/ocr/training/modal_finetune/modal_finetune/burst_unsloth.py::main",
                "--model-name", config.model_name,
                "--dataset-path", config.dataset_path,
                "--max-steps", str(config.max_steps),
            ], env={**os.environ, "DAGSTER_PIPES_CONTEXT": ctx_blob,
                    "BURST_GPU": decision.gpu}, check=True)
        except subprocess.CalledProcessError:
            return local_fallback(config, context)  # §6
    else:
        from cianfhoghlaim.ocr.training.training.unsloth_trainer import UnslothTrainer
        from cianfhoghlaim.ocr.training.training.unsloth_config import UnslothConfig
        cfg = UnslothConfig.for_gaelic_ocr(model_name=config.model_name)
        UnslothTrainer(cfg).train(dataset_path=config.dataset_path,
                                  max_steps=decision.local_max_steps or config.max_steps)
    return MaterializeResult(metadata={"burst": decision.burst, "gpu": decision.gpu})


@sensor(job=modal_unsloth_decision_asset, minimum_interval_seconds=3600)
def gemma4_release_sensor(context):
    """Auto-fire on new Unsloth Gemma 4 / Qwen3.6 releases (1h poll)."""
    from huggingface_hub import HfApi
    for m in HfApi().list_models(author="unsloth", limit=20):
        if any(s in m.modelId for s in ("gemma-4-26B", "gemma-4-31B",
                                        "Qwen3.6-27B", "Qwen3.6-35B")):
            yield RunRequest(run_key=m.modelId, run_config={"ops":
                {"modal_unsloth_decision_asset": {"config":
                    {"model_name": m.modelId}}}})
```

**New openspec requirement** to be added to `meaisinfhoghlaim-platform`:

```markdown
### Requirement: Modal Burst for >26B Unsloth Fine-tunes
The system SHALL route Unsloth fine-tunes to Modal A100/H100 GPUs when the
model size exceeds 26B parameters, estimated VRAM exceeds 30 GB, OR seq_length > 8192.
#### Scenario: Gemma 4 26B detected
- **WHEN** a Dagster run requests `unsloth/gemma-4-26B-A4B-it` with seq_length=8192
- **THEN** the Modal `burst_finetune` (A100-40GB) is dispatched via `modal run`
- **AND** the result is reported through Dagster Pipes to MLflow
#### Scenario: Soft spend cap
- **WHEN** MLflow-aggregated `estimated_cost_usd` for the month exceeds $150
- **THEN** the asset fails with a `Failure` exception and the run is not dispatched
#### Scenario: Fallback on dispatch failure
- **WHEN** the Modal `modal run` subprocess returns non-zero exit code
- **THEN** the asset falls back to local M4 Max with `train_on_responses_only=False`
```

---

## 5. Cost analysis

**Modal GPU pricing (modal.com/pricing, 2026-06-28; per-second billing, 1-min min):**

| GPU | VRAM | $/hr | Best for | Typical run | Cost/run |
|:--|--:|--:|:--|:--|--:|
| A100-40GB | 40 GB | $1.50 | Gemma 4 26B, Qwen3.6 27B | 2-3 h | **$3.00 – $4.50** |
| A100-80GB | 80 GB | $2.00 | Gemma 4 31B, Qwen3.6 35B-A3B | 3-4 h | **$6.00 – $8.00** |
| H100-80GB | 80 GB | $3.00 | Qwen2.5-VL 72B vision | 4-6 h | **$12.00 – $18.00** |

**Reference runs** (calibrated against Agent 19's decision matrix for the 11 OCR models):

| Model | Mode | GPU | Steps | Hours | Cost |
|:--|:--|:--|--:|--:|--:|
| Gemma 4 26B-A4B-it (text) | QLoRA r=16 | A100-40GB | 500 | 2.5 h | **$3.75** |
| Gemma 4 31B-it | QLoRA r=16 | A100-80GB | 500 | 3.5 h | **$7.00** |
| Qwen3.6 27B-it | QLoRA r=16 | A100-40GB | 500 | 2.8 h | **$4.20** |
| Qwen3.6 35B-A3B-it | QLoRA r=16 | A100-80GB | 500 | 4.0 h | **$8.00** |
| Qwen2.5-VL 72B-it (vision) | QLoRA r=64 | H100-80GB | 300 | 5.0 h | **$15.00** |
| Qwen3-Reranker-8B (full-FT) | Full FT | A100-40GB | 1000 | 1.5 h | **$2.25** |

**Budget tiers:** soft cap **$150/mo** (asset-level, blocks dispatch) + workspace hard cap **$200/mo** (Modal dashboard, kills container at $200). Emergency override `UNSLOTH_FORCE_BURST=1` + bump dashboard cap to $300 for ad-hoc runs.

**ROI:** the 11 OCR models currently cap at Gemma 4 12B (18 GB VRAM, runs on M4 Max). Bursting Gemma 4 26B at $3.75 vs. ~$0 local gives **+14 GB headroom, +5-7% accuracy** (Agent 19 Gemma 4 release notes), and unlocks 31B + 35B-A3B MoE. The $150/mo budget covers **~1 Gemma 4 26B fine-tune per working day** — enough for the planned Irish OCR 2026-Q3 expansion (5-7 model variants).

**Cost observability:** `estimated_cost_usd` is logged to MLflow per run; monthly aggregate query:
```python
mlflow.search_runs(experiment_names=["unsloth-burst-gpu"],
    filter_string="attributes.created > 1748736000000",  # 2026-06-01
    max_results=1000)["metrics.estimated_cost_usd"].sum()
```

---

## 6. Fallback — local M4 Max

When Modal is unavailable (spend cap hit, Modal outage, network partition), the
asset falls back to the existing local trainer path with two **memory-saving
tweaks** (Agent 19's "M-series limits" anti-patterns):

```python
def local_fallback(config, context) -> MaterializeResult:
    """Local M4 Max fallback with degraded hyperparams (NO train_on_responses_only)."""
    from unsloth import FastModel
    from trl import SFTTrainer, SFTConfig
    from datasets import load_dataset

    model, tokenizer = FastModel.from_pretrained(
        model_name=config.model_name,
        max_seq_length=2048,            # ↓ from 4096; saves ~30% activation
        load_in_4bit=True, full_finetuning=False,
    )
    model = FastModel.get_peft_model(
        model, r=8, lora_alpha=8,       # ↓ from r=16; saves ~15% adapter memory
        target_modules=["q_proj","k_proj","v_proj","o_proj"],  # attn only
        lora_dropout=0, bias="none", use_gradient_checkpointing="unsloth",
        random_state=3407,
    )
    ds = load_dataset(config.dataset_path, split="train")
    trainer = SFTTrainer(
        model=model, tokenizer=tokenizer, train_dataset=ds,
        args=SFTConfig(
            per_device_train_batch_size=1,           # ↓ from 2; saves ~40% activation
            gradient_accumulation_steps=8,           # ↑ to keep effective batch = 8
            max_steps=min(config.max_steps, 200),   # hard cap
            learning_rate=2e-4, optim="adamw_8bit",
            bf16=True, use_gradient_checkpointing="unsloth",
            # NO train_on_responses_only — saves ~10% activation memory
            # (the +1% accuracy booster is sacrificed for fit-in-memory)
        ),
    )
    # NOTE: deliberately NOT wrapping with train_on_responses_only
    trainer.train()
    import mlflow
    with mlflow.start_run(run_name=f"local-fallback-{config.model_name.split('/')[-1]}"):
        mlflow.set_tag("burst_fallback", "true")
    return MaterializeResult(metadata={"burst": False, "fallback": "local"})


def _local_vram_ok(model_name: str) -> bool:
    """Verify M4 Max unified-memory headroom via MLX Metal API."""
    import mlx.core as mx
    free_gb = mx.metal.get_active_memory() / 1e9
    for t in BURST_THRESHOLDS:
        if fnmatch.fnmatch(model_name, t.model_pattern):
            return free_gb > (t.estimated_vram_4bit_gb + 4)  # +4 GB headroom
    return free_gb > 30  # unknown model: conservative
```

**Decision tree:** `Modal success → log+Done`; `1st fail → Modal Retries backoff`; `2nd fail → log warning + local_fallback() (MLflow tag: burst_fallback=true)`; `budget cap hit → local_fallback() (capped 200 steps)`. If `_local_vram_ok()` returns False, the asset fails entirely with: `"Modal burst failed AND local M4 Max has insufficient unified memory ({free_gb:.1f} GB free; need {need_gb:.1f} GB). Free up memory or upgrade M4 Max RAM."``

---

## 7. Cutover — deploy, test, verify

**Step 1 — Deploy Modal app** (one-time, on bunchloch):
```bash
cd /Users/cianmacandeisigh/dev/kings_college_galway
modal deploy cianfhoghlaim/ocr/training/modal_finetune/modal_finetune/burst_unsloth.py
# → Modal dashboard shows 3 functions: burst_finetune, burst_finetune_80gb, burst_finetune_h100
```

**Step 2 — Wire Infisical → Modal secret** (one-time):
```bash
./scripts/sync_infisical_to_modal.sh
# Reads dev-baile/modal/{HF_TOKEN,MLFLOW_TRACKING_URI,DAGSTER_PIPES_CONTEXT}
# and `modal secret create infisical-modal` with the exported env vars
```

**Step 3 — Smoke test** (no real GPU yet, just import + config):
```bash
modal run cianfhoghlaim/ocr/training/modal_finetune/modal_finetune/burst_unsloth.py::main \
    --model-name "unsloth/gemma-3-1b-it" \
    --dataset-path "cianmacandeisigh/smoke-test-1k" \
    --max-steps 5
# Expected: ~3 min wall, $0.05 cost, output dir /models/burst_run
# Verifies: image builds, secrets resolve, MLflow writes, Modal Volume mounts
```

**Step 4 — Real Gemma 4 26B burst** (the pilot):
```bash
modal run cianfhoghlaim/ocr/training/modal_finetune/modal_finetune/burst_unsloth.py::main \
    --model-name "unsloth/gemma-4-26B-A4B-it" \
    --dataset-path "/stedding/huggingface/datasets/irish_ocr_v3" \
    --max-steps 500
# Expected: 2-3h on A100-40GB, ~$3.75 cost
# Verifies: 26B model loads, train_on_responses_only wraps, GGUF exports
```

**Step 5 — Verify model lands in MLflow**:
```python
import mlflow
mlflow.set_tracking_uri("http://mlflow.cianfhoghlaim.ie")
runs = mlflow.search_runs(experiment_names=["unsloth-burst-gpu"],
    filter_string="params.model_name = 'unsloth/gemma-4-26B-A4B-it'",
    order_by=["attributes.created DESC"], max_results=1)
assert len(runs) == 1
run_id = runs.iloc[0].run_id
print(f"✓ Run {run_id}: {runs.iloc[0]['metrics.training_hours']:.2f}h, "
      f"${runs.iloc[0]['metrics.estimated_cost_usd']:.2f}")
client = mlflow.tracking.MlflowClient()
versions = client.search_model_versions(f"name='unsloth-burst-gemma-4-26B-A4B-it'")
assert len(versions) >= 1
print(f"✓ Registered: {versions[0].name} v{versions[0].version}")
```

**Step 6 — Pull adapter back + Ollama load**:
```bash
modal volume get unsloth-burst-checkpoints burst_run \
    cianfhoghlaim/ocr/training/checkpoints/burst_gemma4_26b
ollama create gemma-4-gaeilge-26b -f checkpoints/burst_gemma4_26b/gguf/Modelfile
curl http://localhost:11434/api/generate -d '{"model": "gemma-4-gaeilge-26b", "prompt": "Cad é an Ghaeilge?"}'
```

**Step 7 — Dagster asset materialization** (orchestration sanity check):
```bash
mise run dagster:oideachais
# http://localhost:3000 → Assets → modal_unsloth_decision_asset → Materialize
# Expected logs: "Burst routing: unsloth/gemma-4-26B-A4B-it → A100-40GB"
#                then "modal run" subprocess output, then Dagster Pipes metadata
```

**Pass criteria** (all 8 must hold for cutover sign-off):
1. ✓ `modal deploy` succeeds; 3 functions in dashboard
2. ✓ Infisical secret `infisical-modal` resolves (`echo $HF_TOKEN` non-empty)
3. ✓ Smoke test (1B, 5 steps) completes in <5 min, cost < $0.10
4. ✓ Real Gemma 4 26B burst completes in 2-3 h, cost $3-5
5. ✓ MLflow run + registered model both visible at `mlflow.cianfhoghlaim.ie`
6. ✓ Dagster asset materialization shows `burst=true`, `gpu=A100-40GB`
7. ✓ LoRA adapter pulled back to bunchloch; GGUF loads in Ollama
8. ✓ Fallback path tested: set Modal workspace spend_limit=$0; re-run asset;
   verify local M4 Max path with `train_on_responses_only=False`

**Rollback** (if any pass criterion fails):
```bash
git revert <commit-hash-of-burst-asset>     # revert Dagster asset
mise run turbo dev                          # restart Dagster
modal app stop unsloth-burst-gpu            # tear down Modal app
# Keep the code (unused code doesn't break anything)
```

---

## §8 — Anti-patterns

1. ❌ **Don't burst ≤ 13B models** — Gemma 4 12B (18 GB) fits M4 Max 36 GB (Agent 20). Bursting wastes $3-5/run.
2. ❌ **Don't use `dtype=torch.float16`** — A100 has native bf16; `bf16=True` in SFTConfig.
3. ❌ **Don't skip `use_gradient_checkpointing="unsloth"`** — saves 30% VRAM; supports 262k context for Gemma 4 26B.
4. ❌ **Don't use `lora_dropout=0.1`** — Unsloth is optimized for `0`; use 0.1 only if overfitting.
5. ❌ **Don't use `random_state=42`** — Unsloth convention is `3407`; current `finetune_irish.py:196` has the bug.
6. ❌ **Don't mix chat templates** — Gemma 4 26B/31B need `gemma-4-thinking`; mixing with `gemma-4` produces gibberish on Ollama.
7. ❌ **Don't forget `num_kv_shared_layers=0` for Gemma 4 26B/31B** — upstream IndexError fix (Agent 19 §3).
8. ❌ **Don't enable `train_on_responses_only` in local fallback** — costs ~10% activation memory; sacrifices +1% accuracy for fit-in-memory.
9. ❌ **Don't set Modal timeout > 4 h** — runaway training; `finetune_irish.py` uses 8 h (2x our cap).
10. ❌ **Don't share the Modal Volume across projects** — `unsloth-burst-checkpoints` is single-tenant.
11. ❌ **Don't bypass the soft $150 spend cap** — the `Failure` is a feature, not a bug; bump via MLflow query.
12. ❌ **Don't use `gpu="A10G"` for >26B** — A10G has 24 GB; 26B at 4-bit needs 28 GB. Use A100-40GB minimum.
13. ❌ **Don't push to HF Hub from inside the Modal function** — let Dagster post-pull; avoids HF rate-limit on shared Modal egress IPs.
14. ❌ **Don't use `weight_decay=0.001`** — Agent 19 R4 says upstream recommends `0.01`; current `finetune_irish.py` is wrong.

---

## §9 — Decision matrix

| Decision | Choice | Rationale |
|:--|:--|:--|
| Burst trigger | `params_b > 26 OR vram_4bit > 30 OR seq > 8192` | 26B is M4 Max 36 GB ceiling (Agent 20) |
| GPU selection | Static `BURST_THRESHOLDS` tuple | Explicit > implicit; auditable in MLflow |
| Function-per-GPU | 3 Modal functions (40/80/H100) | Avoids runtime GPU switching; cleaner billing |
| Volume name | `unsloth-burst-checkpoints` (single, persistent) | One volume per app; no proliferation |
| Secret source | `infisical-modal` (Infisical → Modal) | Matches existing Infisical pattern |
| Timeout | 4 h (was 8 h in finetune_irish.py) | Forces checkpointing discipline |
| Soft spend cap | $150/mo at asset level | Belt + suspenders with Modal $200/mo cap |
| Loader API | `FastModel` (not `FastLanguageModel`/`FastVisionModel`) | Agent 19 R1: unified upstream loader in 3.0+ |
| `train_on_responses_only` | YES in burst, NO in local fallback | +1% accuracy in burst; ~10% memory in fallback |
| Chat template | Per-model (`gemma-4-thinking`, `qwen2.5`, `chatml`) | Match base model variant (Agent 19 §3) |
| `random_state` | `3407` (not `42`) | Agent 19 R4: upstream convention |
| `use_gradient_checkpointing` | `"unsloth"` (not `True`) | Agent 19 R4: 30% extra VRAM savings |
| `weight_decay` | `0.01` (was `0.001`) | Agent 19 R4: upstream recommended |
| `num_kv_shared_layers` | `0` for Gemma 4 26B/31B | Upstream IndexError fix |
| Quantization | QLoRA 4-bit (`load_in_4bit=True`) | 70% VRAM reduction |
| LoRA rank | `r=16` (text), `r=64` (vision) | Agent 19 §8 |
| Optimizer | `adamw_8bit` | 40% memory savings |
| Scheduler | `cosine` | Standard for vision |
| Export | `save_pretrained_gguf` w/ `UD-Q4_K_XL` | SOTA Pareto on KLD (Agent 19 R8) |
| MLflow experiment | `unsloth-burst-gpu` | Separate from local `unsloth-gaelic-ocr` |
| Observability | MLflow only (no WandB) | Agent 19 anti-pattern; `WANDB_DISABLED=true` |
| Dagster asset | `modal_unsloth_decision_asset` (group `meaisinfhoghlaim`) | Discoverable in Dagster UI |
| Sensor | `gemma4_release_sensor` (1h poll) | Auto-trigger on new Unsloth releases |
| Fallback | Local M4 Max w/ degraded hyperparams | Last-resort; logs `burst_fallback=true` |
| Cutover sequence | deploy → smoke → real → MLflow verify → Dagster → sign-off | 7-step gated rollout (§7) |

---

## 1-paragraph summary

**F-42 wraps `UnslothTrainer` with a Modal A100/H100 burst path for >26B fine-tunes (Gemma 4 26B/31B, Qwen3.6 27B/35B-A3B, Qwen2.5-VL 72B) that exceed the M4 Max 36 GB unified-memory cap (Agent 20).** Decision logic lives in a static `BURST_THRESHOLDS` tuple (6 models, 3 GPU tiers) evaluated by a new Dagster `modal_unsloth_decision_asset`; a `gemma4_release_sensor` auto-fires on new Unsloth releases. The Modal app (`burst_unsloth.py`) is a thin decorator over `UnslothConfig.for_gaelic_ocr()` with `gpu=modal.gpu.A100(count=1, size="40GB")`, 4 h timeout, `unsloth-burst-checkpoints` Modal Volume, and `infisical-modal` secret for HF/MLflow/Dagster-Pipes. Cost is $1.50-3.00/hr; Gemma 4 26B run = $3-5; $150/mo soft cap + $200/mo Modal workspace cap = ~50 burst runs/month. Fallback is local M4 Max with `train_on_responses_only=False` (saves ~10% activation memory, sacrifices +1% accuracy) gated by an MLX Metal memory probe. Cutover: deploy to bunchloch → 5-step smoke test → 1 Gemma 4 26B pilot → verify model in MLflow registry → enable the Dagster sensor.
