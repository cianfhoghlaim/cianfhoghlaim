"""
LLM fine-tuning for Celtic languages.

Fine-tunes base models on Celtic language data:
- EuroLLM-22B
- BritLLM-3B
- UCCIX-13B
- Qomhrá-Mistral-7B
"""

from __future__ import annotations

from dagster import (
    asset,
    AssetExecutionContext,
    Config,
    Output,
    MetadataValue,
)


class LLMTrainingConfig(Config):
    """Configuration for LLM fine-tuning."""

    model_name: str = "qomhra-celtic-7b"
    base_model: str = "mistralai/Mistral-7B-v0.1"
    target_languages: list[str] = ["ga", "gd", "cy"]
    use_lora: bool = True
    lora_rank: int = 64
    batch_size: int = 4
    gradient_accumulation: int = 8
    epochs: int = 3
    gpu_provider: str = "modal"


# Celtic LLM base models
CELTIC_BASE_MODELS = [
    {
        "name": "EuroLLM-22B",
        "hf_id": "euro-llm/EuroLLM-22B",
        "languages": ["ga", "cy", "gd"],
        "type": "base",
        "size_gb": 44,
    },
    {
        "name": "BritLLM-3B",
        "hf_id": "britllm/BritLLM-3B",
        "languages": ["cy", "gd"],
        "type": "specialized",
        "size_gb": 6,
    },
    {
        "name": "UCCIX-13B",
        "hf_id": "uccix/UCCIX-13B",
        "languages": ["ga"],
        "type": "specialized",
        "size_gb": 26,
    },
    {
        "name": "Qomhrá-Mistral-7B",
        "hf_id": "qomhra/Qomhra-Mistral-7B",
        "languages": ["ga"],
        "type": "specialized",
        "size_gb": 14,
    },
]


@asset(
    group_name="llm_training",
    description="Prepare Celtic LLM training data",
)
def llm_training_data(
    context: AssetExecutionContext,
    config: LLMTrainingConfig,
    collected_celtic_texts: dict,
) -> Output[dict]:
    """Prepare training data for LLM fine-tuning."""
    training_data = {
        "format": "instruction_tuning",
        "languages": config.target_languages,
        "splits": {
            "train": 0,
            "validation": 0,
            "test": 0,
        },
        "sources": [],
    }

    for lang in config.target_languages:
        if lang in collected_celtic_texts:
            lang_data = collected_celtic_texts[lang]
            training_data["splits"]["train"] += len(lang_data.get("documents", []))
            training_data["sources"].append(
                {
                    "language": lang,
                    "documents": len(lang_data.get("documents", [])),
                }
            )

    return Output(
        training_data,
        metadata={
            "languages": MetadataValue.json(config.target_languages),
        },
    )


@asset(
    group_name="llm_training",
    description="Configure LLM fine-tuning run",
    deps=[llm_training_data],
)
def llm_training_config_asset(
    context: AssetExecutionContext,
    config: LLMTrainingConfig,
    llm_training_data: dict,
) -> Output[dict]:
    """Configure LLM fine-tuning run."""
    # Find base model info
    base_model_info = next(
        (m for m in CELTIC_BASE_MODELS if config.base_model in m["hf_id"]),
        {"name": config.base_model, "size_gb": 14},
    )

    training_config = {
        "model": {
            "name": config.model_name,
            "base": config.base_model,
            "base_info": base_model_info,
        },
        "peft": {
            "enabled": config.use_lora,
            "method": "lora" if config.use_lora else "full",
            "rank": config.lora_rank if config.use_lora else None,
            "alpha": config.lora_rank * 2 if config.use_lora else None,
            "target_modules": ["q_proj", "v_proj", "k_proj", "o_proj"],
        },
        "training": {
            "batch_size": config.batch_size,
            "gradient_accumulation": config.gradient_accumulation,
            "effective_batch_size": config.batch_size * config.gradient_accumulation,
            "epochs": config.epochs,
            "learning_rate": 2e-5,
            "optimizer": "adamw_8bit",
            "scheduler": "cosine",
        },
        "data": llm_training_data,
        "gpu_provider": config.gpu_provider,
        "estimated_cost": "$60-120",
    }

    return Output(
        training_config,
        metadata={
            "model_name": MetadataValue.text(config.model_name),
            "use_lora": MetadataValue.bool(config.use_lora),
        },
    )


@asset(
    group_name="llm_training",
    description="Fine-tune LLM on Celtic data",
    deps=[llm_training_config_asset],
)
def trained_llm_model(
    context: AssetExecutionContext,
    llm_training_config_asset: dict,
) -> Output[dict]:
    """Fine-tune LLM on Celtic language data."""
    # In production, this would:
    # 1. Submit training job to Modal/ThunderCompute
    # 2. Use LoRA for efficient fine-tuning
    # 3. Merge adapters after training

    model_info = {
        "name": llm_training_config_asset["model"]["name"],
        "base": llm_training_config_asset["model"]["base"],
        "status": "pending",
        "checkpoint_path": None,
        "adapter_path": None,
        "metrics": {
            "perplexity": None,
            "irish_blimp": None,  # Irish-BLiMP benchmark
        },
    }

    context.log.info(f"Would fine-tune {model_info['name']}")

    return Output(
        model_info,
        metadata={
            "model_name": MetadataValue.text(model_info["name"]),
        },
    )


# Export assets
llm_training_assets = [
    llm_training_data,
    llm_training_config_asset,
    trained_llm_model,
]
