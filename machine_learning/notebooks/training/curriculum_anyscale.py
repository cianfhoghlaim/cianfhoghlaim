"""
Anyscale Curriculum LLM Training - Irish Education Model.

Distributed Ray training for bilingual Irish education LLM,
fine-tuned on SEC exam papers, marking schemes, and curriculum specs.

Usage:
    # Local testing with Ray
    python curriculum_anyscale.py --local

    # Submit to Anyscale ($100 credits)
    anyscale job submit -f curriculum_config.yaml

    # Deploy inference endpoint
    anyscale service deploy -f curriculum_serve.yaml

Cost Estimate:
    - g5.2xlarge (A10G): ~$1.50/hr per GPU
    - 4 GPU training: ~$6/hr = ~16 hours for $100
    - Full curriculum training: ~$50-80

Training Data:
    - SEC exam papers (2015-2024): ~5,000 papers
    - Marking schemes: ~5,000 documents
    - Curriculum specifications: ~40 subjects
    - Bilingual pairs (en/ga): ~50,000 aligned

Model:
    - Base: UCCIX-Llama2-13B-Instruct (Irish-optimized)
    - Fine-tuning: LoRA (r=64, alpha=128)
    - Target: +10% on IRLBench curriculum tasks

References:
    - UCCIX: https://huggingface.co/ReliableAI/UCCIX-Llama2-13B
    - Anyscale: https://docs.anyscale.com
    - Ray Train: https://docs.ray.io/en/latest/train
"""

import os
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Literal

import yaml


# =============================================================================
# Configuration Classes
# =============================================================================

class SubjectCategory(str, Enum):
    """Leaving Certificate subject categories."""
    LANGUAGES = "languages"
    SCIENCES = "sciences"
    HUMANITIES = "humanities"
    BUSINESS = "business"
    ARTS = "arts"
    TECHNOLOGY = "technology"
    MATHEMATICS = "mathematics"


class ExamLevel(str, Enum):
    """Exam difficulty levels."""
    LEAVING_CERT_HIGHER = "leaving_cert_higher"
    LEAVING_CERT_ORDINARY = "leaving_cert_ordinary"
    JUNIOR_CYCLE_HIGHER = "junior_cycle_higher"
    JUNIOR_CYCLE_ORDINARY = "junior_cycle_ordinary"


@dataclass
class CurriculumDataConfig:
    """Configuration for curriculum training data."""
    # Data sources
    exam_papers_path: str = "/mnt/cluster_storage/data/sec_papers"
    marking_schemes_path: str = "/mnt/cluster_storage/data/marking_schemes"
    curriculum_specs_path: str = "/mnt/cluster_storage/data/curriculum_specs"
    bilingual_pairs_path: str = "/mnt/cluster_storage/data/bilingual_pairs"

    # Subject filtering
    subjects: list[str] | None = None  # None = all subjects
    categories: list[SubjectCategory] | None = None
    levels: list[ExamLevel] | None = None

    # Year range
    year_start: int = 2015
    year_end: int = 2024

    # Language mix
    english_ratio: float = 0.5  # 50% English, 50% Irish
    include_bilingual_pairs: bool = True

    # Data splits
    train_ratio: float = 0.9
    val_ratio: float = 0.1

    # Dataset size limits
    max_samples: int | None = None
    max_seq_length: int = 4096


@dataclass
class CurriculumModelConfig:
    """Configuration for curriculum model training."""
    # Base model (Irish-optimized)
    base_model: str = "ReliableAI/UCCIX-Llama2-13B-Instruct"
    max_seq_length: int = 4096
    load_in_4bit: bool = True

    # LoRA configuration
    lora_r: int = 64
    lora_alpha: int = 128
    lora_dropout: float = 0.05
    lora_target_modules: list[str] = field(default_factory=lambda: [
        "q_proj", "k_proj", "v_proj", "o_proj",
        "gate_proj", "up_proj", "down_proj",
    ])

    # Training hyperparameters
    num_epochs: int = 3
    batch_size_per_device: int = 4
    gradient_accumulation_steps: int = 4
    learning_rate: float = 2e-4
    weight_decay: float = 0.01
    warmup_ratio: float = 0.03
    lr_scheduler: str = "cosine"

    # Precision
    fp16: bool = True
    bf16: bool = False

    # DeepSpeed
    deepspeed_stage: int = 2

    # Output
    output_dir: str = "/mnt/cluster_storage/checkpoints/curriculum"
    hub_model_id: str = "cianfhoghlaim/irish-curriculum-llm"


@dataclass
class AnyscaleConfig:
    """Anyscale cluster configuration."""
    cloud: str = "aws"
    region: str = "eu-west-1"

    # Head node
    head_instance_type: str = "m5.2xlarge"
    head_cpu: int = 8

    # Worker nodes
    worker_instance_type: str = "g5.2xlarge"  # A10G GPU
    min_workers: int = 2
    max_workers: int = 4
    worker_cpu: int = 8
    worker_gpu: int = 1

    # Auto-scaling
    idle_timeout_minutes: int = 10


# =============================================================================
# Data Processing Functions
# =============================================================================

def load_exam_papers(config: CurriculumDataConfig) -> list[dict[str, Any]]:
    """
    Load SEC exam papers from storage.

    Returns list of training examples in instruction format:
    {
        "instruction": "Solve this Leaving Certificate Mathematics question...",
        "input": "Question text with marks allocation",
        "output": "Step-by-step solution with marking scheme alignment"
    }
    """
    from pathlib import Path
    import json

    papers_dir = Path(config.exam_papers_path)
    examples = []

    for paper_file in papers_dir.glob("**/*.json"):
        with open(paper_file) as f:
            paper = json.load(f)

        # Filter by year
        year = paper.get("year", 0)
        if year < config.year_start or year > config.year_end:
            continue

        # Filter by subject
        subject = paper.get("subject")
        if config.subjects and subject not in config.subjects:
            continue

        # Filter by level
        level = paper.get("level")
        if config.levels and level not in [l.value for l in config.levels]:
            continue

        # Extract questions
        for section in paper.get("sections", []):
            for question in section.get("questions", []):
                # Create instruction example
                instruction = create_exam_instruction(
                    subject=subject,
                    level=level,
                    year=year,
                    marks=question.get("marks", 0),
                )

                example = {
                    "instruction": instruction,
                    "input": question.get("text", ""),
                    "output": question.get("solution", ""),
                    "subject": subject,
                    "level": level,
                    "year": year,
                    "marks": question.get("marks", 0),
                    "topic": question.get("topic", ""),
                    "language": paper.get("language", "en"),
                }

                examples.append(example)

                if config.max_samples and len(examples) >= config.max_samples:
                    return examples

    return examples


def load_marking_schemes(config: CurriculumDataConfig) -> list[dict[str, Any]]:
    """
    Load marking schemes for answer evaluation training.

    Creates examples for:
    - Evaluating student answers against criteria
    - Providing feedback with mark allocation
    """
    from pathlib import Path
    import json

    schemes_dir = Path(config.marking_schemes_path)
    examples = []

    for scheme_file in schemes_dir.glob("**/*.json"):
        with open(scheme_file) as f:
            scheme = json.load(f)

        subject = scheme.get("subject")
        if config.subjects and subject not in config.subjects:
            continue

        for criterion in scheme.get("criteria", []):
            # Create evaluation example
            instruction = f"""You are an examiner for the Irish {scheme.get('level', 'Leaving Certificate')} {subject} exam.

Evaluate the following student answer according to the marking scheme.
Provide specific feedback and allocate marks out of {criterion.get('total_marks', 0)}.

Marking Criteria:
{criterion.get('description', '')}

Key Points Required:
{', '.join(criterion.get('keywords', []))}
"""

            # Create synthetic student answer for training
            example = {
                "instruction": instruction,
                "input": criterion.get("sample_question", ""),
                "output": format_marking_feedback(criterion),
                "subject": subject,
                "type": "marking",
            }

            examples.append(example)

    return examples


def load_curriculum_specs(config: CurriculumDataConfig) -> list[dict[str, Any]]:
    """
    Load curriculum specifications for topic explanation.

    Creates examples for:
    - Explaining curriculum topics
    - Mapping learning outcomes to questions
    """
    from pathlib import Path
    import json

    specs_dir = Path(config.curriculum_specs_path)
    examples = []

    for spec_file in specs_dir.glob("**/*.json"):
        with open(spec_file) as f:
            spec = json.load(f)

        subject = spec.get("subject")
        if config.subjects and subject not in config.subjects:
            continue

        for strand in spec.get("strands", []):
            for outcome in strand.get("learning_outcomes", []):
                # Create explanation example
                instruction = f"""Explain the following {subject} curriculum topic for {spec.get('level', 'Leaving Certificate')} students.

Topic: {strand.get('name', '')}
Learning Outcome: {outcome.get('code', '')}

Provide a clear, educational explanation suitable for exam preparation.
Include relevant examples and key points to remember.
"""

                example = {
                    "instruction": instruction,
                    "input": outcome.get("description", ""),
                    "output": outcome.get("explanation", ""),
                    "subject": subject,
                    "type": "curriculum",
                }

                examples.append(example)

    return examples


def load_bilingual_pairs(config: CurriculumDataConfig) -> list[dict[str, Any]]:
    """
    Load bilingual English-Irish aligned pairs.

    Used for:
    - Translation between exam languages
    - Consistent terminology across languages
    """
    from pathlib import Path
    import json

    if not config.include_bilingual_pairs:
        return []

    pairs_dir = Path(config.bilingual_pairs_path)
    examples = []

    for pairs_file in pairs_dir.glob("**/*.json"):
        with open(pairs_file) as f:
            pairs = json.load(f)

        for pair in pairs:
            # English to Irish
            examples.append({
                "instruction": "Translate the following educational content from English to Irish, maintaining mathematical notation and technical terminology.",
                "input": pair.get("english", ""),
                "output": pair.get("irish", ""),
                "type": "translation_en_ga",
            })

            # Irish to English
            examples.append({
                "instruction": "Translate the following educational content from Irish to English, maintaining mathematical notation and technical terminology.",
                "input": pair.get("irish", ""),
                "output": pair.get("english", ""),
                "type": "translation_ga_en",
            })

    return examples


def create_exam_instruction(
    subject: str,
    level: str,
    year: int,
    marks: int,
) -> str:
    """Create instruction prompt for exam question."""
    level_name = level.replace("_", " ").title()

    instruction = f"""You are a knowledgeable Irish {level_name} {subject.title()} tutor.

Answer the following {year} exam question worth {marks} marks.
Show your working clearly and provide a complete solution.
If mathematical notation is needed, use LaTeX format.

Important:
- Address all parts of the question
- Show step-by-step working
- Allocate effort proportional to marks
- Use correct terminology
"""

    return instruction


def format_marking_feedback(criterion: dict) -> str:
    """Format marking scheme as evaluator feedback."""
    feedback = f"""## Evaluation

**Marks Awarded:** [X] / {criterion.get('total_marks', 0)}

### Criteria Assessment:

"""

    for i, point in enumerate(criterion.get("keywords", []), 1):
        feedback += f"{i}. **{point}**: [Present/Absent/Partial] - [Comment]\n"

    feedback += f"""
### Summary Feedback:
[Provide constructive feedback on the answer quality, areas for improvement, and commend good points.]

### Sample Model Answer:
{criterion.get('sample_answer', 'N/A')}
"""

    return feedback


def prepare_training_dataset(config: CurriculumDataConfig) -> tuple[list, list]:
    """
    Prepare complete training dataset from all sources.

    Returns:
        (train_examples, val_examples)
    """
    import random

    all_examples = []

    # Load from each source
    print("Loading exam papers...")
    all_examples.extend(load_exam_papers(config))

    print("Loading marking schemes...")
    all_examples.extend(load_marking_schemes(config))

    print("Loading curriculum specs...")
    all_examples.extend(load_curriculum_specs(config))

    print("Loading bilingual pairs...")
    all_examples.extend(load_bilingual_pairs(config))

    print(f"Total examples: {len(all_examples)}")

    # Shuffle and split
    random.shuffle(all_examples)
    split_idx = int(len(all_examples) * config.train_ratio)

    return all_examples[:split_idx], all_examples[split_idx:]


# =============================================================================
# Training Functions
# =============================================================================

def train_func(train_config: dict):
    """
    Distributed training function for Ray Train.

    Executed on each worker in the Anyscale cluster.
    """
    import torch
    from transformers import TrainingArguments
    from datasets import Dataset
    from trl import SFTTrainer
    from unsloth import FastLanguageModel
    import wandb
    import mlflow

    # Get worker info
    from ray import train as ray_train

    world_size = ray_train.get_context().get_world_size()
    rank = ray_train.get_context().get_world_rank()

    print(f"Worker {rank}/{world_size} starting curriculum training...")

    # Initialize tracking on rank 0
    if rank == 0:
        wandb.init(
            project="irish-curriculum-llm",
            name=f"curriculum-{world_size}gpu",
            config=train_config,
        )

        mlflow.set_tracking_uri(
            os.environ.get("MLFLOW_TRACKING_URI", "http://localhost:5000")
        )
        mlflow.set_experiment("curriculum-llm")
        mlflow.start_run()
        mlflow.log_params(train_config)

    # Configuration
    model_config = CurriculumModelConfig(**train_config.get("model", {}))
    data_config = CurriculumDataConfig(**train_config.get("data", {}))

    # Load model with Unsloth
    print(f"Worker {rank}: Loading model {model_config.base_model}...")
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=model_config.base_model,
        max_seq_length=model_config.max_seq_length,
        load_in_4bit=model_config.load_in_4bit,
    )

    # Add LoRA adapters
    print(f"Worker {rank}: Adding LoRA adapters...")
    model = FastLanguageModel.get_peft_model(
        model,
        r=model_config.lora_r,
        target_modules=model_config.lora_target_modules,
        lora_alpha=model_config.lora_alpha,
        lora_dropout=model_config.lora_dropout,
        bias="none",
        use_gradient_checkpointing="unsloth",
    )

    # Prepare dataset
    print(f"Worker {rank}: Loading training data...")
    train_examples, val_examples = prepare_training_dataset(data_config)

    # Convert to HuggingFace Dataset
    def format_prompt(example):
        """Format example as instruction-following prompt."""
        if example.get("input"):
            prompt = (
                f"### Instruction:\n{example['instruction']}\n\n"
                f"### Input:\n{example['input']}\n\n"
                f"### Response:\n{example['output']}"
            )
        else:
            prompt = (
                f"### Instruction:\n{example['instruction']}\n\n"
                f"### Response:\n{example['output']}"
            )
        return {"text": prompt}

    train_dataset = Dataset.from_list(train_examples)
    train_dataset = train_dataset.map(format_prompt)

    val_dataset = Dataset.from_list(val_examples)
    val_dataset = val_dataset.map(format_prompt)

    print(f"Worker {rank}: Train samples: {len(train_dataset)}, Val samples: {len(val_dataset)}")

    # Training arguments
    training_args = TrainingArguments(
        output_dir=model_config.output_dir,
        num_train_epochs=model_config.num_epochs,
        per_device_train_batch_size=model_config.batch_size_per_device,
        per_device_eval_batch_size=model_config.batch_size_per_device,
        gradient_accumulation_steps=model_config.gradient_accumulation_steps,
        learning_rate=model_config.learning_rate,
        weight_decay=model_config.weight_decay,
        warmup_ratio=model_config.warmup_ratio,
        lr_scheduler_type=model_config.lr_scheduler,
        fp16=model_config.fp16,
        bf16=model_config.bf16,
        logging_steps=10,
        save_steps=100,
        eval_steps=100,
        save_total_limit=3,
        evaluation_strategy="steps",
        report_to="wandb" if rank == 0 else "none",
        optim="adamw_8bit",
        # DeepSpeed
        deepspeed={
            "zero_optimization": {"stage": model_config.deepspeed_stage},
            "fp16": {"enabled": model_config.fp16},
        },
        # Distributed
        local_rank=rank,
        ddp_find_unused_parameters=False,
    )

    # Initialize trainer
    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        dataset_text_field="text",
        max_seq_length=model_config.max_seq_length,
        args=training_args,
    )

    # Train
    print(f"Worker {rank}: Starting training...")
    trainer.train()

    # Evaluate
    eval_results = trainer.evaluate()
    print(f"Worker {rank}: Evaluation results: {eval_results}")

    # Save on rank 0
    if rank == 0:
        print("Saving model...")

        # Save checkpoint
        model.save_pretrained(f"{model_config.output_dir}/final")
        tokenizer.save_pretrained(f"{model_config.output_dir}/final")

        # Log metrics
        mlflow.log_metrics({
            "eval_loss": eval_results.get("eval_loss", 0),
            "perplexity": torch.exp(torch.tensor(eval_results.get("eval_loss", 0))).item(),
        })

        # Push to Hub
        if train_config.get("push_to_hub", False):
            print(f"Pushing to Hub: {model_config.hub_model_id}")
            model.push_to_hub(
                model_config.hub_model_id,
                token=os.environ.get("HF_TOKEN"),
                private=True,
            )
            tokenizer.push_to_hub(
                model_config.hub_model_id,
                token=os.environ.get("HF_TOKEN"),
                private=True,
            )

        mlflow.end_run()
        wandb.finish()

    # Report completion
    ray_train.report({"status": "complete", "rank": rank, "eval_loss": eval_results.get("eval_loss", 0)})


def run_training(config: dict | None = None, local: bool = False):
    """
    Run distributed training on Anyscale or locally.

    Args:
        config: Training configuration override
        local: Run locally with Ray instead of Anyscale
    """
    import ray
    from ray import train
    from ray.train import ScalingConfig, RunConfig, CheckpointConfig
    from ray.train.torch import TorchTrainer

    # Load configuration
    if config is None:
        config_path = os.environ.get(
            "CURRICULUM_CONFIG",
            "curriculum_config.yaml"
        )
        if os.path.exists(config_path):
            with open(config_path) as f:
                config = yaml.safe_load(f)
        else:
            config = {}

    # Default configuration
    train_config = {
        "model": {
            "base_model": "ReliableAI/UCCIX-Llama2-13B-Instruct",
            "max_seq_length": 4096,
            "lora_r": 64,
            "lora_alpha": 128,
            "num_epochs": 3,
            "batch_size_per_device": 4,
            "learning_rate": 2e-4,
        },
        "data": {
            "year_start": 2020,
            "year_end": 2024,
            "english_ratio": 0.5,
        },
        **config,
    }

    # Initialize Ray
    if local:
        ray.init()
    else:
        ray.init(address="auto")  # Connect to Anyscale cluster

    # Configure trainer
    num_workers = int(os.environ.get("NUM_WORKERS", 4 if not local else 1))

    trainer = TorchTrainer(
        train_func,
        train_loop_config=train_config,
        scaling_config=ScalingConfig(
            num_workers=num_workers,
            use_gpu=True,
            resources_per_worker={"CPU": 8, "GPU": 1},
        ),
        run_config=RunConfig(
            name="irish-curriculum-llm",
            checkpoint_config=CheckpointConfig(
                num_to_keep=3,
                checkpoint_frequency=100,
            ),
        ),
    )

    # Run training
    result = trainer.fit()
    print(f"Training complete: {result}")

    return result


# =============================================================================
# Configuration Generation
# =============================================================================

def generate_anyscale_config(output_path: str = "curriculum_config.yaml"):
    """Generate Anyscale job configuration file."""
    config = {
        "name": "irish-curriculum-llm-training",
        "compute_config": {
            "cloud": "aws",
            "region": "eu-west-1",
            "head_node_type": {
                "name": "head",
                "instance_type": "m5.2xlarge",
                "resources": {"CPU": 8},
            },
            "worker_node_types": [{
                "name": "gpu-workers",
                "instance_type": "g5.2xlarge",
                "min_workers": 2,
                "max_workers": 4,
                "resources": {
                    "CPU": 8,
                    "GPU": 1,
                    "accelerator_type:A10G": 1,
                },
            }],
            "idle_timeout_minutes": 10,
        },
        "runtime_env": {
            "pip": [
                "torch>=2.1.0",
                "transformers>=4.36.0",
                "datasets>=2.16.0",
                "accelerate>=0.25.0",
                "deepspeed>=0.12.0",
                "ray[train]>=2.9.0",
                "unsloth @ git+https://github.com/unslothai/unsloth.git",
                "wandb>=0.16.0",
                "mlflow>=2.9.0",
                "huggingface_hub>=0.20.0",
            ],
            "env_vars": {
                "HF_TOKEN": "${HF_TOKEN}",
                "WANDB_API_KEY": "${WANDB_API_KEY}",
                "MLFLOW_TRACKING_URI": "${MLFLOW_TRACKING_URI}",
            },
        },
        "entrypoint": "python curriculum_anyscale.py",
        "model": {
            "base_model": "ReliableAI/UCCIX-Llama2-13B-Instruct",
            "max_seq_length": 4096,
            "lora_r": 64,
            "lora_alpha": 128,
            "num_epochs": 3,
            "batch_size_per_device": 4,
            "learning_rate": 2e-4,
            "hub_model_id": "cianfhoghlaim/irish-curriculum-llm",
        },
        "data": {
            "year_start": 2015,
            "year_end": 2024,
            "english_ratio": 0.5,
            "include_bilingual_pairs": True,
            "subjects": [
                "mathematics", "irish", "english",
                "biology", "chemistry", "physics",
                "history", "geography",
            ],
        },
        "push_to_hub": True,
    }

    with open(output_path, "w") as f:
        yaml.dump(config, f, default_flow_style=False)

    print(f"Generated Anyscale config: {output_path}")


# =============================================================================
# CLI Entry Point
# =============================================================================

def main():
    """Main entry point for curriculum LLM training."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Irish Curriculum LLM Training on Anyscale"
    )
    parser.add_argument(
        "--local",
        action="store_true",
        help="Run locally with Ray instead of Anyscale",
    )
    parser.add_argument(
        "--generate-config",
        action="store_true",
        help="Generate Anyscale configuration file",
    )
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to configuration YAML file",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Test with small dataset and few epochs",
    )

    args = parser.parse_args()

    if args.generate_config:
        generate_anyscale_config()
        return

    # Load config if provided
    config = None
    if args.config and os.path.exists(args.config):
        with open(args.config) as f:
            config = yaml.safe_load(f)

    # Override for dry run
    if args.dry_run:
        config = config or {}
        config["model"] = config.get("model", {})
        config["model"]["num_epochs"] = 1
        config["data"] = config.get("data", {})
        config["data"]["max_samples"] = 100

    print("=" * 60)
    print("Irish Curriculum LLM Training")
    print(f"Mode: {'Local' if args.local else 'Anyscale'}")
    print("=" * 60)

    result = run_training(config=config, local=args.local)

    print("\n" + "=" * 60)
    print("Training Complete!")
    print(f"Result: {result}")
    print("=" * 60)


if __name__ == "__main__":
    main()
