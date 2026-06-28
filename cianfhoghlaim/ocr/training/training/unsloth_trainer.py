"""
Unsloth Training Orchestration for Qwen2-VL Fine-tuning.

Handles:
- Model loading with 4-bit quantization
- LoRA adapter application
- Dataset preparation
- Training with gradient checkpointing
- MLflow experiment tracking

Based on research in:
- taighde_teanga/Finetuning Qwen3-VL for Gaelic OCR.md
- taighde_new/document-intelligence-ocr.md

Usage:
    from training import UnslothTrainer, UnslothConfig

    config = UnslothConfig.for_gaelic_ocr()
    trainer = UnslothTrainer(config)

    # Train on dataset
    trainer.train(resume_from_checkpoint=None)

    # Save adapter
    trainer.save_adapter("./gaelic-ocr-adapter")
"""

import json
import os
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from .unsloth_config import UnslothConfig


@dataclass
class TrainingState:
    """Tracks training progress."""

    current_step: int = 0
    current_epoch: float = 0.0
    best_eval_loss: float = float("inf")
    best_checkpoint: str | None = None
    training_loss: float = 0.0
    eval_loss: float | None = None
    learning_rate: float = 0.0
    started_at: str = field(default_factory=lambda: datetime.now().isoformat())


class UnslothTrainer:
    """
    Training orchestrator for Qwen2-VL fine-tuning with Unsloth.
    """

    def __init__(
        self,
        config: UnslothConfig,
        callbacks: list[Any] | None = None,
    ):
        """
        Initialize trainer.

        Args:
            config: Training configuration
            callbacks: Optional list of training callbacks
        """
        self.config = config
        self.callbacks = callbacks or []
        self.state = TrainingState()

        # Lazy-loaded components
        self._model = None
        self._tokenizer = None
        self._processor = None
        self._trainer = None
        self._train_dataset = None
        self._eval_dataset = None

    def _setup_mlflow(self) -> None:
        """Configure MLflow tracking."""
        try:
            import mlflow

            mlflow.set_tracking_uri(self.config.mlflow_tracking_uri)
            mlflow.set_experiment(self.config.mlflow_experiment_name)

            # Log configuration
            mlflow.log_params(
                {
                    "model_name": self.config.model_name,
                    "lora_r": self.config.lora.r,
                    "lora_alpha": self.config.lora.lora_alpha,
                    "learning_rate": self.config.training.learning_rate,
                    "batch_size": self.config.training.per_device_train_batch_size,
                    "gradient_accumulation": self.config.training.gradient_accumulation_steps,
                    "finetune_vision": self.config.vision.finetune_vision_layers,
                }
            )
        except ImportError:
            print("MLflow not available, skipping experiment tracking")

    def _load_model(self) -> tuple[Any, Any, Any]:
        """Load model with Unsloth optimizations."""
        try:
            from unsloth import FastVisionModel
        except ImportError:
            raise ImportError(
                "Unsloth package required. Install with: pip install unsloth"
            )

        model, tokenizer = FastVisionModel.from_pretrained(
            self.config.model_name,
            load_in_4bit=self.config.load_in_4bit,
            use_gradient_checkpointing=self.config.lora.use_gradient_checkpointing,
        )

        # Apply LoRA
        model = FastVisionModel.get_peft_model(
            model,
            finetune_vision_layers=self.config.vision.finetune_vision_layers,
            finetune_language_layers=True,
            finetune_attention_modules=True,
            finetune_mlp_modules=True,
            r=self.config.lora.r,
            lora_alpha=self.config.lora.lora_alpha,
            lora_dropout=self.config.lora.lora_dropout,
            bias=self.config.lora.bias,
            random_state=self.config.training.seed,
            use_rslora=False,
            loftq_config=None,
        )

        # Get processor for vision
        from transformers import AutoProcessor

        processor = AutoProcessor.from_pretrained(
            self.config.model_name.replace("-bnb-4bit", "").replace("unsloth/", ""),
            min_pixels=self.config.vision.min_pixels,
            max_pixels=self.config.vision.max_pixels,
        )

        return model, tokenizer, processor

    def _load_dataset(self) -> tuple[Any, Any]:
        """Load training and evaluation datasets."""
        from datasets import load_dataset

        dataset_path = Path(self.config.dataset_path)

        # Load JSONL files
        train_path = dataset_path / self.config.train_file
        eval_path = dataset_path / self.config.eval_file

        if not train_path.exists():
            raise FileNotFoundError(f"Training file not found: {train_path}")

        train_dataset = load_dataset(
            "json",
            data_files=str(train_path),
            split="train",
        )

        eval_dataset = None
        if eval_path.exists():
            eval_dataset = load_dataset(
                "json",
                data_files=str(eval_path),
                split="train",
            )

        # Apply sample limits
        if self.config.max_train_samples:
            train_dataset = train_dataset.select(
                range(min(len(train_dataset), self.config.max_train_samples))
            )

        if eval_dataset and self.config.max_eval_samples:
            eval_dataset = eval_dataset.select(
                range(min(len(eval_dataset), self.config.max_eval_samples))
            )

        return train_dataset, eval_dataset

    def _prepare_dataset(
        self,
        dataset: Any,
        processor: Any,
    ) -> Any:
        """
        Prepare dataset for vision-language training.

        Converts JSONL format to model input format.
        """
        from PIL import Image

        def convert_to_conversation(sample: dict) -> dict:
            """Convert sample to conversation format."""
            # Load image
            image_path = sample.get("image_path") or sample.get("image")
            if image_path and os.path.exists(image_path):
                image = Image.open(image_path).convert("RGB")
            else:
                # Create placeholder if image missing
                image = Image.new("RGB", (224, 224), color="white")

            # Get transcription
            transcription = sample.get("transcription") or sample.get("text", "")

            # Build conversation
            conversation = [
                {
                    "role": "user",
                    "content": [
                        {"type": "image"},
                        {
                            "type": "text",
                            "text": "Transcribe the handwritten Irish text in this image exactly as written.",
                        },
                    ],
                },
                {
                    "role": "assistant",
                    "content": [{"type": "text", "text": transcription}],
                },
            ]

            return {
                "images": [image],
                "messages": conversation,
            }

        def apply_chat_template(examples: dict) -> dict:
            """Apply chat template to batch."""
            texts = []
            images_list = []

            for i in range(len(examples.get("messages", []))):
                messages = examples["messages"][i]
                images = examples["images"][i]

                text = processor.apply_chat_template(
                    messages,
                    add_generation_prompt=False,
                )
                texts.append(text)
                images_list.append(images)

            batch = processor(
                text=texts,
                images=images_list,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=self.config.training.max_seq_length,
            )

            return batch

        # Convert dataset
        converted = dataset.map(
            convert_to_conversation,
            remove_columns=dataset.column_names,
            num_proc=self.config.training.dataloader_num_workers,
        )

        # Apply chat template
        prepared = converted.map(
            apply_chat_template,
            batched=True,
            batch_size=self.config.training.per_device_train_batch_size,
        )

        return prepared

    def train(
        self,
        resume_from_checkpoint: str | None = None,
        progress_callback: Callable[[TrainingState], None] | None = None,
    ) -> TrainingState:
        """
        Run training.

        Args:
            resume_from_checkpoint: Path to checkpoint to resume from
            progress_callback: Optional callback for progress updates

        Returns:
            Final training state
        """
        from transformers import TrainingArguments
        from trl import SFTTrainer

        # Setup MLflow
        self._setup_mlflow()

        # Load components
        print("Loading model...")
        self._model, self._tokenizer, self._processor = self._load_model()

        print("Loading dataset...")
        self._train_dataset, self._eval_dataset = self._load_dataset()

        print("Preparing dataset...")
        train_prepared = self._prepare_dataset(self._train_dataset, self._processor)
        eval_prepared = None
        if self._eval_dataset:
            eval_prepared = self._prepare_dataset(self._eval_dataset, self._processor)

        # Create output directory
        output_dir = Path(self.config.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Training arguments
        training_args = TrainingArguments(
            output_dir=str(output_dir),
            per_device_train_batch_size=self.config.training.per_device_train_batch_size,
            per_device_eval_batch_size=self.config.training.per_device_eval_batch_size,
            gradient_accumulation_steps=self.config.training.gradient_accumulation_steps,
            warmup_steps=self.config.training.warmup_steps,
            max_steps=self.config.training.max_steps,
            num_train_epochs=self.config.training.num_train_epochs,
            learning_rate=self.config.training.learning_rate,
            weight_decay=self.config.training.weight_decay,
            optim=self.config.training.optim,
            lr_scheduler_type=self.config.training.lr_scheduler_type,
            logging_steps=self.config.training.logging_steps,
            eval_steps=self.config.training.eval_steps if eval_prepared else None,
            eval_strategy="steps" if eval_prepared else "no",
            save_steps=self.config.training.save_steps,
            save_total_limit=self.config.training.save_total_limit,
            seed=self.config.training.seed,
            fp16=self.config.training.fp16,
            bf16=self.config.training.bf16,
            dataloader_num_workers=self.config.training.dataloader_num_workers,
            remove_unused_columns=self.config.training.remove_unused_columns,
            report_to=["mlflow"] if self.config.mlflow_tracking_uri else [],
            load_best_model_at_end=bool(eval_prepared),
            metric_for_best_model="eval_loss" if eval_prepared else None,
        )

        # Create trainer
        self._trainer = SFTTrainer(
            model=self._model,
            tokenizer=self._tokenizer,
            args=training_args,
            train_dataset=train_prepared,
            eval_dataset=eval_prepared,
            callbacks=self.callbacks,
        )

        # Train
        print("Starting training...")
        train_result = self._trainer.train(
            resume_from_checkpoint=resume_from_checkpoint
        )

        # Update state
        self.state.current_step = self._trainer.state.global_step
        self.state.current_epoch = self._trainer.state.epoch or 0.0
        self.state.training_loss = train_result.training_loss

        if eval_prepared:
            eval_result = self._trainer.evaluate()
            self.state.eval_loss = eval_result.get("eval_loss")

        # Save final model
        final_path = output_dir / "final"
        self.save_adapter(final_path)
        self.state.best_checkpoint = str(final_path)

        print(f"Training complete. Final loss: {self.state.training_loss:.4f}")

        return self.state

    def save_adapter(self, path: str | Path) -> Path:
        """
        Save LoRA adapter.

        Args:
            path: Output path for adapter

        Returns:
            Path to saved adapter
        """
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)

        if self._model is None:
            raise ValueError("No model loaded. Run train() first.")

        # Save adapter weights
        self._model.save_pretrained(path)

        # Save tokenizer
        if self._tokenizer:
            self._tokenizer.save_pretrained(path)

        # Save config
        config_path = path / "training_config.json"
        with open(config_path, "w") as f:
            json.dump(self.config.to_dict(), f, indent=2)

        print(f"Adapter saved to: {path}")
        return path

    def save_merged(self, path: str | Path, quantization: str = "q4_k_m") -> Path:
        """
        Save merged model (base + adapter).

        Args:
            path: Output path
            quantization: GGUF quantization level

        Returns:
            Path to saved model
        """
        path = Path(path)

        if self._model is None:
            raise ValueError("No model loaded. Run train() first.")

        try:

            # Merge and save
            self._model.save_pretrained_merged(
                path,
                self._tokenizer,
                save_method="merged_16bit",
            )

            # Optionally quantize to GGUF
            if quantization:
                gguf_path = path / f"model-{quantization}.gguf"
                self._model.save_pretrained_gguf(
                    str(gguf_path),
                    self._tokenizer,
                    quantization_method=quantization,
                )

        except Exception as e:
            print(f"Merge failed: {e}")
            # Fallback: just save adapter
            self.save_adapter(path / "adapter")

        return path

    def push_to_hub(
        self,
        repo_id: str,
        private: bool = True,
        adapter_only: bool = True,
    ) -> str:
        """
        Push model to Hugging Face Hub.

        Args:
            repo_id: Repository ID (e.g., "username/model-name")
            private: Whether repo should be private
            adapter_only: Push only adapter (not merged model)

        Returns:
            URL to model on Hub
        """
        if self._model is None:
            raise ValueError("No model loaded. Run train() first.")

        if adapter_only:
            self._model.push_to_hub(
                repo_id,
                private=private,
            )
            if self._tokenizer:
                self._tokenizer.push_to_hub(repo_id)
        else:
            try:

                self._model.push_to_hub_merged(
                    repo_id,
                    self._tokenizer,
                    save_method="merged_16bit",
                    private=private,
                )
            except Exception as e:
                print(f"Merged push failed: {e}, pushing adapter only")
                self._model.push_to_hub(repo_id, private=private)

        return f"https://huggingface.co/{repo_id}"

    def evaluate_on_test(
        self,
        test_file: str | Path,
        output_file: str | Path | None = None,
    ) -> dict[str, float]:
        """
        Evaluate model on test set.

        Args:
            test_file: Path to test JSONL
            output_file: Optional path to save predictions

        Returns:
            Evaluation metrics
        """
        from datasets import load_dataset

        if self._model is None:
            raise ValueError("No model loaded. Run train() first.")

        # Load test data
        test_dataset = load_dataset("json", data_files=str(test_file), split="train")

        # Prepare
        test_prepared = self._prepare_dataset(test_dataset, self._processor)

        # Evaluate
        results = self._trainer.evaluate(test_prepared)

        # Generate predictions if output requested
        if output_file:
            predictions = self._generate_predictions(test_prepared)
            self._save_predictions(predictions, test_dataset, output_file)

        return results

    def _generate_predictions(self, dataset: Any) -> list[str]:
        """Generate predictions for dataset."""
        from unsloth import FastVisionModel

        FastVisionModel.for_inference(self._model)

        predictions = []
        for sample in dataset:
            # Generate
            outputs = self._model.generate(
                **{k: v.unsqueeze(0) for k, v in sample.items() if k != "labels"},
                max_new_tokens=512,
                temperature=0.1,
            )

            # Decode
            pred = self._tokenizer.decode(outputs[0], skip_special_tokens=True)
            predictions.append(pred)

        return predictions

    def _save_predictions(
        self,
        predictions: list[str],
        dataset: Any,
        output_file: str | Path,
    ) -> None:
        """Save predictions to file."""
        output_file = Path(output_file)

        results = []
        for i, pred in enumerate(predictions):
            sample = dataset[i]
            results.append(
                {
                    "image": sample.get("image_path", sample.get("image", "")),
                    "ground_truth": sample.get("transcription", sample.get("text", "")),
                    "prediction": pred,
                }
            )

        with open(output_file, "w", encoding="utf-8") as f:
            for result in results:
                f.write(json.dumps(result, ensure_ascii=False) + "\n")
