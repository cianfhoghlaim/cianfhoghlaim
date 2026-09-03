"""
Modal GPU Job: Irish LLM Fine-tuning (v5 — Unsloth Qwen3.8-27B)

Fine-tunes Qwen3.8-27B (Unsloth GGUF) on Irish curriculum data
using Unsloth for 70% VRAM reduction.

Per the 2026-08-21-unsloth-v5-integration-v1 change, the v5
fine-tune target is Qwen3.8-27B (the new Unsloth flagship, 5.1M
downloads in 5 days post-launch). The v4 target was Gemma 4 31B;
Qwen3.8-27B is denser and more agentic-friendly for the Irish
fine-tune use case.

Per the 2026-06-29 v4 trim, the Modal GPU server is the primary
target for fine-tuning the largest v4 models. The M4 Max 48 GB
unified memory can serve Qwen3.8-27B at Q4_K_M (~16 GB resident
plus 6 GB KV cache) for inference, but the full 27B is too tight
for a 3-epoch Irish fine-tune (which needs ~30 GB at QLoRA r=16).
Modal H100 80 GB is the right home for this fine-tune.

For M4 Max 48 GB fine-tune, see finetune_unsloth_local.py (the
v6 sibling that uses QLoRA r=8 to fit on 48 GB).

Usage:
    # Direct Modal execution
    modal run meaisinfhoghlaim/training/modal_finetune/finetune_irish.py
    modal deploy meaisinfhoghlaim/training/modal_finetune/finetune_irish.py

    # Dagster orchestration (preferred)
    dagster asset materialize -m oideachais.dagster_defs --select modal_irish_llm_finetune

Cost estimate: ~$30 for 8 hours on H100 GPU (was ~$100 on A10G
for Llama-3.2-3B; H100 is faster per token despite higher $/hr)

Observability:
    - WandB for training metrics
    - MLflow for experiment tracking and model registry
    - Dagster Pipes for asset materialization
    - HuggingFace Hub for model publishing (Unsloth GGUF format)

Training Configuration (v5):
    - Base model: unsloth/Qwen3.8-27B-GGUF (the v5 27B dense SOTA)
    - Unsloth: 70% VRAM reduction, 2x faster training
    - LoRA: r=16, alpha=32 (optimal for Irish)
    - 4-bit quantization: QLoRA for memory efficiency
    - 6 Celtic languages (per the v5 Qwen3.8 capability)
"""

import time

import modal

# Modal app configuration
app = modal.App("irish-llm-finetune")

# Container image with training dependencies + observability
# Per the 2026-08-21 change: pin `unsloth[colab-new]==2026.8.0`
# (the stable PyPI release) instead of the git ref. The pinned
# version matches the canonical Unsloth Studio CLI surface.
training_image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "unsloth[colab-new]==2026.8.0",
        "torch>=2.1.0",
        "transformers>=4.36.0",
        "datasets>=2.16.0",
        "accelerate>=0.25.0",
        "peft>=0.7.0",
        "bitsandbytes>=0.41.0",
        "trl>=0.7.0",
        "wandb>=0.16.0",
        "huggingface_hub>=0.20.0",
        # Observability
        "mlflow>=2.10.0",
        "dagster-pipes>=0.1.0",
        "langfuse>=2.0.0",
    )
)

# Persistent volume for model checkpoints
model_volume = modal.Volume.from_name("irish-llm-checkpoints", create_if_missing=True)


@app.function(
    image=training_image,
    gpu="H100",  # 80GB VRAM - fits Gemma 4 31B QLoRA r=16 (~30GB) + headroom
    timeout=3600 * 8,  # 8 hours max
    secrets=[
        modal.Secret.from_name("huggingface"),
        modal.Secret.from_name("wandb"),
        modal.Secret.from_name("mlflow"),
    ],
    volumes={"/checkpoints": model_volume},
)
def finetune_irish_llm(
    base_model: str = "unsloth/Qwen3.8-27B-GGUF",  # v5 — was unsloth/gemma-4-31B-it-GGUF (v4)
    dataset_name: str = "cianfhoghlaim/sec-exam-irish",
    max_steps: int = 1000,
    learning_rate: float = 2e-4,
    batch_size: int = 4,
    gradient_accumulation_steps: int = 4,
    lora_r: int = 16,
    lora_alpha: int = 32,
    output_dir: str = "/checkpoints/irish-llama",
    hub_model_id: str = "cianfhoghlaim/irish-llama-3.2-3b-instruct",
    dagster_pipes_context: str | None = None,
):
    """
    Fine-tune Llama model on Irish educational data.

    Uses Unsloth for 2x faster training and 70% less VRAM.

    Observability:
        - WandB: Real-time training metrics
        - MLflow: Experiment tracking and model registry
        - Dagster Pipes: Asset materialization context

    Args:
        base_model: HuggingFace model ID (Unsloth-optimized)
        dataset_name: HuggingFace dataset with instruction format
        max_steps: Training steps (1000 ≈ 8 hours on A10G)
        learning_rate: Learning rate (2e-4 optimal for LoRA)
        batch_size: Per-device batch size (4 with A10G 24GB)
        gradient_accumulation_steps: Effective batch = batch_size * this
        lora_r: LoRA rank dimension (16 optimal for Irish)
        lora_alpha: LoRA alpha scaling (32 = 2x rank)
        output_dir: Checkpoint directory
        hub_model_id: HuggingFace Hub model ID for publishing
        dagster_pipes_context: Serialized Dagster Pipes context
    """
    import os

    import wandb
    from datasets import load_dataset
    from transformers import TrainingArguments
    from trl import SFTTrainer
    from unsloth import FastLanguageModel

    start_time = time.time()

    # Initialize MLflow tracking
    mlflow_enabled = False
    try:
        import mlflow
        mlflow_tracking_uri = os.getenv("MLFLOW_TRACKING_URI")
        if mlflow_tracking_uri:
            mlflow.set_tracking_uri(mlflow_tracking_uri)
            mlflow.set_experiment("irish-llm-finetune")
            mlflow_enabled = True
            print(f"MLflow tracking enabled: {mlflow_tracking_uri}")
    except ImportError:
        print("MLflow not available, using WandB only")

    # Initialize Dagster Pipes context
    pipes_context = None
    try:
        from dagster_pipes import open_dagster_pipes
        if dagster_pipes_context:
            pipes_context = open_dagster_pipes()
            print("Dagster Pipes context initialized")
    except ImportError:
        print("Dagster Pipes not available")

    # Start MLflow run
    if mlflow_enabled:
        mlflow.start_run(run_name=f"llama-3.2-3b-irish-{max_steps}steps")
        mlflow.log_params({
            "base_model": base_model,
            "dataset": dataset_name,
            "max_steps": max_steps,
            "learning_rate": learning_rate,
            "batch_size": batch_size,
            "gradient_accumulation_steps": gradient_accumulation_steps,
            "effective_batch_size": batch_size * gradient_accumulation_steps,
            "lora_r": lora_r,
            "lora_alpha": lora_alpha,
            "optimizer": "adamw_8bit",
            "quantization": "4-bit",
        })

    # Initialize wandb (primary training logger)
    wandb.init(
        project="irish-llm-finetune",
        name=f"llama-3.2-3b-irish-{max_steps}steps",
        config={
            "base_model": base_model,
            "dataset": dataset_name,
            "max_steps": max_steps,
            "learning_rate": learning_rate,
            "lora_r": lora_r,
            "lora_alpha": lora_alpha,
            "batch_size": batch_size,
            "gradient_accumulation_steps": gradient_accumulation_steps,
        }
    )

    print(f"Loading base model: {base_model}")

    # Load model with Unsloth optimizations
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=base_model,
        max_seq_length=2048,
        dtype=None,  # Auto-detect
        load_in_4bit=True,  # 4-bit quantization for memory efficiency
    )

    # Add LoRA adapters
    model = FastLanguageModel.get_peft_model(
        model,
        r=lora_r,
        target_modules=[
            "q_proj", "k_proj", "v_proj", "o_proj",
            "gate_proj", "up_proj", "down_proj",
        ],
        lora_alpha=lora_alpha,
        lora_dropout=0.05,
        bias="none",
        use_gradient_checkpointing="unsloth",
        random_state=42,
    )

    print("Loading dataset...")

    # Load Irish education dataset
    # Format: {"instruction": "...", "input": "...", "output": "..."}
    dataset = load_dataset(dataset_name, split="train")

    # Format for instruction tuning
    def format_prompt(example):
        prompt = f"""### Instruction:
{example['instruction']}

### Input:
{example['input']}

### Response:
{example['output']}"""
        return {"text": prompt}

    dataset = dataset.map(format_prompt)

    print(f"Dataset size: {len(dataset)} examples")

    # Training configuration
    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=3,
        max_steps=max_steps,
        per_device_train_batch_size=batch_size,
        gradient_accumulation_steps=gradient_accumulation_steps,
        learning_rate=learning_rate,
        fp16=True,
        logging_steps=10,
        save_steps=100,
        save_total_limit=3,
        warmup_ratio=0.03,
        lr_scheduler_type="cosine",
        report_to="wandb",
        optim="adamw_8bit",  # 8-bit optimizer for memory efficiency
    )

    # Initialize trainer
    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=dataset,
        dataset_text_field="text",
        max_seq_length=2048,
        args=training_args,
    )

    print("Starting training...")

    # Train
    trainer.train()

    # Save final model
    print("Saving model...")
    model.save_pretrained(f"{output_dir}/final")
    tokenizer.save_pretrained(f"{output_dir}/final")

    # Calculate training time
    training_time = time.time() - start_time
    training_hours = training_time / 3600

    # Log training artifacts to MLflow
    if mlflow_enabled:
        # Log model artifacts
        mlflow.log_artifact(f"{output_dir}/final", artifact_path="model")

        # Log final metrics
        mlflow.log_metrics({
            "training_time_s": training_time,
            "training_hours": training_hours,
            "dataset_size": len(dataset),
        })

        # Register model in MLflow Model Registry
        try:
            mlflow.register_model(
                f"runs:/{mlflow.active_run().info.run_id}/model",
                "irish-llama-3.2-3b-instruct"
            )
            print("Model registered in MLflow Model Registry")
        except Exception as e:
            print(f"MLflow model registration failed: {e}")

    # Push to HuggingFace Hub
    hf_token = os.getenv("HF_TOKEN")
    if hf_token:
        print(f"Pushing to HuggingFace Hub: {hub_model_id}")
        model.push_to_hub(
            hub_model_id,
            token=hf_token,
            private=True,
        )
        tokenizer.push_to_hub(
            hub_model_id,
            token=hf_token,
            private=True,
        )

        if mlflow_enabled:
            mlflow.log_param("hub_model_id", hub_model_id)

    # Report to Dagster Pipes
    if pipes_context:
        pipes_context.report_asset_materialization(
            metadata={
                "base_model": base_model,
                "dataset": dataset_name,
                "dataset_size": len(dataset),
                "max_steps": max_steps,
                "lora_r": lora_r,
                "lora_alpha": lora_alpha,
                "training_time_hours": training_hours,
                "output_dir": output_dir,
                "hub_model_id": hub_model_id if hf_token else None,
            }
        )

    # End tracking
    if mlflow_enabled:
        mlflow.end_run()
    wandb.finish()

    result = {
        "status": "success",
        "output_dir": output_dir,
        "hub_model_id": hub_model_id if hf_token else None,
        "training_time_hours": training_hours,
        "dataset_size": len(dataset),
    }

    print(f"Training complete! Time: {training_hours:.2f} hours")
    return result


@app.function(
    image=training_image,
    gpu="A10G",
    timeout=3600,
    secrets=[modal.Secret.from_name("huggingface")],
)
def evaluate_model(
    model_path: str = "/checkpoints/irish-llama/final",
    test_prompts: list[str] | None = None,
):
    """
    Evaluate fine-tuned Irish model.
    """
    from unsloth import FastLanguageModel

    if test_prompts is None:
        test_prompts = [
            "Cad é an difríocht idir uimhir phríomha agus uimhir chomhfhillte?",
            "Explain the Leaving Certificate grading system in Ireland.",
            "Cén chaoi a ndéantar anailís ar dhán Gaeilge?",
        ]

    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=model_path,
        max_seq_length=2048,
        load_in_4bit=True,
    )

    FastLanguageModel.for_inference(model)

    results = []
    for prompt in test_prompts:
        inputs = tokenizer(
            f"### Instruction:\n{prompt}\n\n### Response:\n",
            return_tensors="pt"
        ).to("cuda")

        outputs = model.generate(
            **inputs,
            max_new_tokens=256,
            temperature=0.7,
            do_sample=True,
        )

        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        results.append({"prompt": prompt, "response": response})
        print(f"\nPrompt: {prompt}\nResponse: {response}\n")

    return results


@app.local_entrypoint()
def main():
    """Run fine-tuning job."""
    print("Starting Irish LLM fine-tuning on Modal...")
    result = finetune_irish_llm.remote()
    print(f"Result: {result}")
