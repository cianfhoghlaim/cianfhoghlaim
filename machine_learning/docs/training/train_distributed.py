"""
Distributed Training Script for Anyscale.

Ray-based distributed fine-tuning with DeepSpeed ZeRO-2 optimization.

Usage:
    # Local testing
    python train_distributed.py

    # Anyscale cluster
    anyscale job submit -f anyscale_config.yaml
"""

import os
import ray
from ray import train
from ray.train import ScalingConfig, RunConfig, CheckpointConfig
from ray.train.torch import TorchTrainer


def train_func(config: dict):
    """
    Training function executed on each worker.

    Args:
        config: Training configuration dict
    """
    import torch
    from transformers import TrainingArguments
    from datasets import load_dataset
    from trl import SFTTrainer
    from unsloth import FastLanguageModel
    import wandb

    # Get worker info
    world_size = train.get_context().get_world_size()
    rank = train.get_context().get_world_rank()

    print(f"Worker {rank}/{world_size} starting...")

    # Initialize wandb on rank 0 only
    if rank == 0:
        wandb.init(
            project="irish-llm-distributed",
            name=f"distributed-{world_size}gpu",
            config=config,
        )

    # Load model with Unsloth
    model_config = config.get("model", {})
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=model_config.get("name", "unsloth/Llama-3.2-3B-Instruct"),
        max_seq_length=model_config.get("max_seq_length", 2048),
        load_in_4bit=model_config.get("load_in_4bit", True),
    )

    # Add LoRA adapters
    lora_config = config.get("lora", {})
    model = FastLanguageModel.get_peft_model(
        model,
        r=lora_config.get("r", 16),
        target_modules=lora_config.get("target_modules", [
            "q_proj", "k_proj", "v_proj", "o_proj",
            "gate_proj", "up_proj", "down_proj",
        ]),
        lora_alpha=lora_config.get("alpha", 32),
        lora_dropout=lora_config.get("dropout", 0.05),
        bias="none",
        use_gradient_checkpointing="unsloth",
    )

    # Load dataset
    dataset_config = config.get("dataset", {})
    dataset = load_dataset(
        dataset_config.get("name", "cianfhoghlaim/sec-exam-irish"),
        split=dataset_config.get("split", "train"),
    )

    # Format prompts
    def format_prompt(example):
        return {
            "text": f"### Instruction:\n{example['instruction']}\n\n"
                   f"### Input:\n{example['input']}\n\n"
                   f"### Response:\n{example['output']}"
        }

    dataset = dataset.map(format_prompt)

    # Training arguments
    training_config = config.get("training", {})
    output_config = config.get("output", {})

    training_args = TrainingArguments(
        output_dir=output_config.get("checkpoint_dir", "./checkpoints"),
        num_train_epochs=training_config.get("num_epochs", 3),
        per_device_train_batch_size=training_config.get("batch_size_per_device", 4),
        gradient_accumulation_steps=training_config.get("gradient_accumulation_steps", 4),
        learning_rate=training_config.get("learning_rate", 2e-4),
        warmup_ratio=training_config.get("warmup_ratio", 0.03),
        lr_scheduler_type=training_config.get("lr_scheduler", "cosine"),
        fp16=training_config.get("fp16", True),
        logging_steps=10,
        save_steps=output_config.get("save_steps", 100),
        save_total_limit=3,
        report_to="wandb" if rank == 0 else "none",
        optim="adamw_8bit",
        # DeepSpeed configuration
        deepspeed={
            "zero_optimization": {
                "stage": training_config.get("deepspeed_stage", 2),
            },
            "fp16": {"enabled": training_config.get("fp16", True)},
        },
        # Distributed training
        local_rank=rank,
        ddp_find_unused_parameters=False,
    )

    # Initialize trainer
    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=dataset,
        dataset_text_field="text",
        max_seq_length=model_config.get("max_seq_length", 2048),
        args=training_args,
    )

    # Train
    print(f"Worker {rank}: Starting training...")
    trainer.train()

    # Save on rank 0
    if rank == 0:
        print("Saving model...")
        model.save_pretrained(f"{output_config.get('checkpoint_dir', './checkpoints')}/final")
        tokenizer.save_pretrained(f"{output_config.get('checkpoint_dir', './checkpoints')}/final")

        # Push to Hub
        hub_id = output_config.get("hub_model_id")
        if hub_id:
            print(f"Pushing to HuggingFace Hub: {hub_id}")
            model.push_to_hub(hub_id, token=os.getenv("HF_TOKEN"), private=True)
            tokenizer.push_to_hub(hub_id, token=os.getenv("HF_TOKEN"), private=True)

        wandb.finish()

    # Report metrics
    train.report({"status": "complete", "rank": rank})


def main():
    """Main entry point for distributed training."""
    import yaml

    # Load configuration
    config_path = os.getenv("ANYSCALE_CONFIG", "anyscale_config.yaml")
    if os.path.exists(config_path):
        with open(config_path) as f:
            full_config = yaml.safe_load(f)
            config = full_config.get("job_config", {})
    else:
        # Default configuration
        config = {
            "model": {
                "name": "unsloth/Llama-3.2-3B-Instruct",
                "max_seq_length": 2048,
                "load_in_4bit": True,
            },
            "lora": {
                "r": 16,
                "alpha": 32,
                "dropout": 0.05,
            },
            "training": {
                "num_epochs": 3,
                "batch_size_per_device": 4,
                "learning_rate": 2e-4,
            },
            "dataset": {
                "name": "cianfhoghlaim/sec-exam-irish",
            },
            "output": {
                "checkpoint_dir": "./checkpoints",
            },
        }

    # Initialize Ray
    ray.init()

    # Configure trainer
    trainer = TorchTrainer(
        train_func,
        train_loop_config=config,
        scaling_config=ScalingConfig(
            num_workers=int(os.getenv("NUM_WORKERS", 4)),
            use_gpu=True,
            resources_per_worker={"CPU": 8, "GPU": 1},
        ),
        run_config=RunConfig(
            name="irish-llm-distributed",
            checkpoint_config=CheckpointConfig(
                num_to_keep=3,
                checkpoint_frequency=100,
            ),
        ),
    )

    # Run training
    result = trainer.fit()
    print(f"Training complete: {result}")


if __name__ == "__main__":
    main()
