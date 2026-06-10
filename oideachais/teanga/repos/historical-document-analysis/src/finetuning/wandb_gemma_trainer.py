import wandb
import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import dotenv
from difflib import SequenceMatcher
from PIL import Image
from pydantic import BaseModel, Field
from transformers.trainer_callback import TrainerCallback
from src.finetuning_scripts.diagnostic_scripts.gemma_trainer_diagnostic import complete_diagnostic_and_fix
from src.models.llm.gemma_three import Gemma3Provider, TrainingParameters, LoraTrainingConfig
from src.datasets.talmud_dataset import StructuredTalmudDataLoader
dotenv.load_dotenv()

class WandbConfig(BaseModel):
    """Configuration for Weights & Biases integration.

    Example:
        wandb_config = WandbConfig(
            project_name="talmud-transcription",
            experiment_name="gemma3-donut-style",
            tags=["gemma3", "talmud", "donut"],
            notes="Testing Donut-style training on Hebrew manuscripts"
        )
    """
    project_name: str = Field(description="W&B project name")
    experiment_name: Optional[str] = Field(default=None, description="Experiment name (auto-generated if None)")
    entity: Optional[str] = Field(default=None, description="W&B entity/organization name")
    tags: List[str] = Field(default_factory=lambda: ["gemma3", "talmud"], description="Experiment tags")
    notes: Optional[str] = Field(default=None, description="Experiment notes")

    class Config:
        extra = "forbid"


class ExperimentConfig(BaseModel):
    """Complete experiment configuration combining model, training, and logging settings.

    Example:
        config = ExperimentConfig(
            model_name="google/gemma-3-4b-it",
            training_mode="donut_style",
            training_params=TrainingParameters(learning_rate=1e-4, batch_size=8),
            wandb_config=WandbConfig(project_name="my-project"),
            output_dir="./models/donut-hebrew"
        )
    """
    model_name: str = Field(default="google/gemma-3-4b-it", description="HuggingFace model identifier")
    training_mode: str = Field(default="donut_style", description="Training strategy")
    training_params: TrainingParameters = Field(default_factory=TrainingParameters, description="Training parameters")
    lora_config: Optional[LoraTrainingConfig] = Field(default=None, description="LoRA configuration if using LoRA")
    wandb_config: WandbConfig = Field(description="W&B configuration")
    output_dir: str = Field(default="./output", description="Output directory for model")
    use_vision: bool = Field(default=True, description="Enable vision capabilities")
    enable_pan_scan: bool = Field(default=True, description="Enable adaptive image cropping")
    device: str = Field(default="auto", description="Device placement strategy")
    max_sequence_length: int = Field(default=2048, ge=1, description="Maximum input sequence length")
    max_output_length: int = Field(default=512, ge=1, description="Maximum output length")

    class Config:
        extra = "forbid"


class DatasetStatistics(BaseModel):
    """Statistics for training/validation datasets."""
    size: int = Field(ge=0, description="Number of examples")
    avg_length: float = Field(ge=0.0, description="Average transcription length")
    min_length: int = Field(ge=0, description="Minimum transcription length")
    max_length: int = Field(ge=0, description="Maximum transcription length")
    total_chars: int = Field(ge=0, description="Total character count")
    hebrew_chars: int = Field(ge=0, description="Hebrew character count")
    hebrew_ratio: float = Field(ge=0.0, le=1.0, description="Ratio of Hebrew characters")


class EvaluationResults(BaseModel):
    """Results from model evaluation."""
    test_samples: int = Field(ge=0, description="Number of test samples")
    avg_similarity: float = Field(ge=0.0, le=1.0, description="Average similarity score")
    min_similarity: float = Field(ge=0.0, le=1.0, description="Minimum similarity score")
    max_similarity: float = Field(ge=0.0, le=1.0, description="Maximum similarity score")
    avg_pred_length: float = Field(ge=0.0, description="Average prediction length")
    avg_target_length: float = Field(ge=0.0, description="Average target length")


class WandbGemma3Trainer:
    """Enhanced Gemma3 trainer with W&B integration for manuscript transcription.

    Integrates with the enhanced Gemma3Provider to provide comprehensive experiment tracking,
    model versioning, and training monitoring through Weights & Biases.

    :param experiment_config: Complete experiment configuration including model, training, and W&B settings
    :type experiment_config: ExperimentConfig

    Example:
        # Create configuration
        config = ExperimentConfig(
            model_name="google/gemma-3-4b-it",
            training_mode="donut_style",
            training_params=TrainingParameters(learning_rate=1e-4, batch_size=8),
            wandb_config=WandbConfig(
                project_name="talmud-transcription",
                experiment_name="donut-hebrew-v1"
            ),
            output_dir="./models/donut-hebrew"
        )

        # Initialize trainer
        trainer = WandbGemma3Trainer(experiment_config=config)

        # Train with automatic logging
        trainer.train_with_wandb(
            training_data=train_data,
            validation_data=val_data
        )
    """

    def __init__(self, experiment_config: ExperimentConfig) -> None:
        """Initialize the trainer with experiment configuration.

        :param experiment_config: Complete experiment configuration
        :type experiment_config: ExperimentConfig
        """
        self.config = experiment_config

        # Generate experiment name if not provided
        if self.config.wandb_config.experiment_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.config.wandb_config.experiment_name = f"gemma3_{self.config.training_mode}_{timestamp}"

        # Setup logging
        self.logger = logging.getLogger(__name__)

        # Initialize components
        self.gemma3_provider: Optional[Gemma3Provider] = None
        self.wandb_run: Optional[wandb.run] = None

        self.logger.info(f"Initialized WandbGemma3Trainer: {self.config.wandb_config.experiment_name}")

    def setup_model(self) -> None:
        """Initialize the Gemma3 model with experiment configuration.

        Example:
            trainer.setup_model()
            model_info = trainer.get_model_info()
        """
        self.gemma3_provider = Gemma3Provider(
            model_name=self.config.model_name,
            device=self.config.device,
            use_vision=self.config.use_vision,
            enable_pan_scan=self.config.enable_pan_scan,
            max_input_sequence=self.config.max_sequence_length,
            max_output_length=self.config.max_output_length
        )

        # Prepare for training with specified mode
        self.gemma3_provider.prepare_for_training(
            training_mode=self.config.training_mode,
            lora_config=self.config.lora_config,
            enable_gradient_checkpointing=True
        )

        self.logger.info("Gemma3 model initialized and prepared for training")

    def init_wandb(self) -> None:
        """Initialize Weights & Biases run with experiment configuration.

        Example:
            trainer.init_wandb()
            print(f"W&B URL: {trainer.wandb_run.url}")
        """
        # Create W&B configuration
        wandb_config = {
            **self.config.training_params.dict(),
            "model_name": self.config.model_name,
            "training_mode": self.config.training_mode,
            "use_vision": self.config.use_vision,
            "enable_pan_scan": self.config.enable_pan_scan,
            "device": self.config.device,
            "max_sequence_length": self.config.max_sequence_length,
            "max_output_length": self.config.max_output_length
        }

        # Add LoRA config if present
        if self.config.lora_config:
            wandb_config["lora_config"] = self.config.lora_config.dict()

        # Initialize W&B run
        self.wandb_run = wandb.init(
            project=self.config.wandb_config.project_name,
            entity=self.config.wandb_config.entity,
            name=self.config.wandb_config.experiment_name,
            config=wandb_config,
            tags=self.config.wandb_config.tags,
            notes=self.config.wandb_config.notes,
            reinit=True
        )

        self.logger.info(f"W&B run initialized: {self.wandb_run.id}")

    def calculate_dataset_statistics(self,
                                     data: List[Dict[str, Any]],
                                     dataset_name: str) -> DatasetStatistics:
        """Calculate comprehensive statistics for a dataset.

        :param data: Dataset to analyze with keys 'target', 'text', etc.
        :type data: List[Dict[str, Any]]
        :param dataset_name: Name of the dataset for logging
        :type dataset_name: str
        :return: Dataset statistics
        :rtype: DatasetStatistics

        Example:
            stats = trainer.calculate_dataset_statistics(
                data=training_data,
                dataset_name="training"
            )
            print(f"Dataset size: {stats.size}, Hebrew ratio: {stats.hebrew_ratio:.2%}")
        """
        transcription_lengths = []
        total_chars = 0
        hebrew_chars = 0

        for item in data:
            target = item.get("target", "")
            transcription_lengths.append(len(target))
            total_chars += len(target)
            # Count Hebrew characters (Unicode range for Hebrew)
            hebrew_chars += sum(1 for c in target if '\u0590' <= c <= '\u05FF')

        return DatasetStatistics(
            size=len(data),
            avg_length=sum(transcription_lengths) / len(transcription_lengths) if transcription_lengths else 0,
            min_length=min(transcription_lengths) if transcription_lengths else 0,
            max_length=max(transcription_lengths) if transcription_lengths else 0,
            total_chars=total_chars,
            hebrew_chars=hebrew_chars,
            hebrew_ratio=hebrew_chars / total_chars if total_chars > 0 else 0.0
        )

    def log_dataset_info(self,
                         training_data: List[Dict[str, Any]],
                         validation_data: Optional[List[Dict[str, Any]]] = None) -> None:
        """Log dataset statistics and samples to W&B.

        :param training_data: Training dataset with structure [{"text": str, "target": str, "images": List}, ...]
        :type training_data: List[Dict[str, Any]]
        :param validation_data: Optional validation dataset in same format
        :type validation_data: Optional[List[Dict[str, Any]]]

        Example:
            trainer.log_dataset_info(
                training_data=train_examples,
                validation_data=val_examples
            )
        """
        if not self.wandb_run:
            self.logger.warning("W&B not initialized. Call init_wandb() first.")
            return

        # Calculate and log training statistics
        train_stats = self.calculate_dataset_statistics(data=training_data, dataset_name="training")
        wandb.log({
            "dataset/train_size": train_stats.size,
            "dataset/train_avg_length": train_stats.avg_length,
            "dataset/train_hebrew_ratio": train_stats.hebrew_ratio,
            "dataset/train_total_chars": train_stats.total_chars
        })

        # Calculate and log validation statistics if provided
        if validation_data:
            val_stats = self.calculate_dataset_statistics(data=validation_data, dataset_name="validation")
            wandb.log({
                "dataset/val_size": val_stats.size,
                "dataset/val_avg_length": val_stats.avg_length,
                "dataset/val_hebrew_ratio": val_stats.hebrew_ratio,
                "dataset/val_total_chars": val_stats.total_chars
            })

        # Log sample data tables
        self._log_sample_data_table(samples=training_data[:5], table_name="train_samples")
        if validation_data:
            self._log_sample_data_table(samples=validation_data[:3], table_name="val_samples")

    def _log_sample_data_table(self,
                               samples: List[Dict[str, Any]],
                               table_name: str) -> None:
        """Log sample data as a W&B table.

        :param samples: List of data samples
        :type samples: List[Dict[str, Any]]
        :param table_name: Name for the W&B table
        :type table_name: str
        """
        columns = ["image", "text_prompt", "target_transcription", "transcription_length"]
        table_data = []

        for i, sample in enumerate(samples):
            # Load image if available
            image = None
            if "images" in sample and sample["images"]:
                img_path = sample["images"][0]
                if os.path.exists(img_path):
                    pil_img = Image.open(img_path)
                    image = wandb.Image(pil_img, caption=f"Sample {i + 1}")

            target_text = sample.get("target", "")
            display_text = target_text[:200] + "..." if len(target_text) > 200 else target_text

            table_data.append([
                image,
                sample.get("text", ""),
                display_text,
                len(target_text)
            ])

        table = wandb.Table(columns=columns, data=table_data)
        wandb.log({table_name: table})

    def create_training_callback(self) -> TrainerCallback:
        """Create a custom training callback for enhanced logging.

        :return: Custom training callback
        :rtype: TrainerCallback

        Example:
            callback = trainer.create_training_callback()
            # This callback is automatically used in train_with_wandb()
        """

        class EnhancedLoggingCallback(TrainerCallback):
            def __init__(self, trainer_instance: 'WandbGemma3Trainer'):
                self.trainer_instance = trainer_instance
                self.start_time = None

            def on_train_begin(self, args, state, control, **kwargs):
                print("\n" + "=" * 60)
                print(f"TRAINING STARTED: {self.trainer_instance.config.wandb_config.experiment_name}")
                print(f"Training mode: {self.trainer_instance.config.training_mode}")
                print(f"Total steps: {state.max_steps}")
                print("=" * 60 + "\n")
                self.start_time = datetime.now()
                wandb.log({
                    "training/started": 1,
                    "training/max_steps": state.max_steps,
                    "training/mode": self.trainer_instance.config.training_mode
                })

            def on_step_end(self, args, state, control, **kwargs):
                if state.global_step % args.logging_steps == 0:
                    elapsed = (datetime.now() - self.start_time).total_seconds() if self.start_time else 0
                    print(f"Step {state.global_step}/{state.max_steps} - Elapsed: {elapsed:.1f}s")

            def on_log(self, args, state, control, logs=None, **kwargs):
                if logs:
                    loss = logs.get("loss", "N/A")
                    lr = logs.get("learning_rate", "N/A")
                    print(f"[Step {state.global_step}] Loss: {loss}, LR: {lr}")

                    wandb.log({
                        "train/loss": loss,
                        "train/learning_rate": lr,
                        "train/global_step": state.global_step,
                        "train/epoch": state.epoch if state.epoch else 0
                    })

            def on_epoch_begin(self, args, state, control, **kwargs):
                epoch = int(state.epoch) if state.epoch else 0
                print(f"\nEPOCH {epoch + 1} STARTED\n")
                wandb.log({"train/epoch_started": epoch + 1})

            def on_epoch_end(self, args, state, control, **kwargs):
                epoch = int(state.epoch) if state.epoch else 0
                print(f"\nEPOCH {epoch + 1} COMPLETED\n")
                wandb.log({"train/epoch_completed": epoch + 1})

        return EnhancedLoggingCallback(trainer_instance=self)

    def train_with_wandb(self,
                         training_data: List[Dict[str, Any]],
                         validation_data: Optional[List[Dict[str, Any]]] = None) -> bool:
        """Train the model with comprehensive W&B logging.

        :param training_data: Training examples with structure [{"text": str, "target": str, "images": List}, ...]
        :type training_data: List[Dict[str, Any]]
        :param validation_data: Optional validation examples in same format
        :type validation_data: Optional[List[Dict[str, Any]]]
        :return: Success status of training
        :rtype: bool

        Example:
            success = trainer.train_with_wandb(
                training_data=train_data,
                validation_data=val_data
            )
            if success:
                print("Training completed successfully!")
        """
        print("=" * 60)
        print("STARTING ENHANCED WANDB TRAINING")
        print("=" * 60)

        # Initialize model if not done
        if not self.gemma3_provider:
            print("Setting up model...")
            self.setup_model()

        # Initialize W&B
        print("Initializing W&B...")
        self.init_wandb()
        wandb.log({"status": "training_started"})
        print(f"W&B URL: {self.wandb_run.url}")

        # Log dataset information
        print("Logging dataset information...")
        self.log_dataset_info(training_data=training_data, validation_data=validation_data)

        # Log model information
        model_info = self.gemma3_provider.get_model_info()
        wandb.log({
            "model/total_parameters": model_info.total_parameters,
            "model/trainable_parameters": model_info.trainable_parameters,
            "model/trainable_ratio": model_info.trainable_ratio,
            "model/training_mode": model_info.training_mode
        })

        print(f"Model ready - Trainable: {model_info.trainable_parameters:,} / Total: {model_info.total_parameters:,}")
        success = complete_diagnostic_and_fix(self.gemma3_provider)
        if not success:
            self.logger.error("❌ Gradient issues not resolved!")
        # Train the model
        trainer = self.gemma3_provider.train(
            training_data=training_data,
            validation_data=validation_data,
            output_dir=self.config.output_dir,
            training_params=self.config.training_params,
            report_to="wandb"
        )

        # Add custom callback
        trainer.add_callback(self.create_training_callback())

        print("Starting training...")

        # Start training
        trainer.train()

        print("Training completed! Saving model...")
        trainer.save_model()
        print(f"Model saved to {self.config.output_dir}")

        # Log completion
        wandb.log({"status": "training_completed"})

        # Log final model artifacts
        self._log_model_artifacts(model_dir=self.config.output_dir)

        # Generate sample predictions
        if validation_data:
            self._log_sample_predictions(sample_data=validation_data[:3])

        print("Training pipeline completed successfully!")
        return True

    def _log_model_artifacts(self, model_dir: str) -> None:
        """Log the trained model as W&B artifacts.

        :param model_dir: Directory containing the saved model
        :type model_dir: str
        """
        artifact = wandb.Artifact(
            name=f"{self.config.wandb_config.experiment_name}-model",
            type="model",
            description=f"Fine-tuned Gemma3 model for manuscript transcription"
        )

        model_path = Path(model_dir)
        if model_path.exists():
            artifact.add_dir(str(model_path))
            wandb.log_artifact(artifact)
            self.logger.info("Model artifacts logged to W&B")

    def _log_sample_predictions(self, sample_data: List[Dict[str, Any]]) -> None:
        """Generate and log sample predictions for evaluation.

        :param sample_data: Sample data for prediction
        :type sample_data: List[Dict[str, Any]]
        """
        if not sample_data:
            return

        self.logger.info("Generating sample predictions...")
        predictions_data = []

        for i, sample in enumerate(sample_data):
            result = self.gemma3_provider.call_llm([sample])

            if result and len(result) > 0:
                prediction = result[0].get("generated_text", "")
                ground_truth = sample.get("target", "")

                similarity = self._calculate_text_similarity(
                    pred=prediction,
                    target=ground_truth
                )

                predictions_data.append([
                    i + 1,
                    ground_truth[:200] + "..." if len(ground_truth) > 200 else ground_truth,
                    prediction[:200] + "..." if len(prediction) > 200 else prediction,
                    len(ground_truth),
                    len(prediction),
                    similarity
                ])

        if predictions_data:
            columns = ["sample_id", "ground_truth", "prediction", "gt_length", "pred_length", "similarity"]
            predictions_table = wandb.Table(columns=columns, data=predictions_data)
            wandb.log({"predictions/sample_predictions": predictions_table})

            avg_similarity = sum(row[5] for row in predictions_data) / len(predictions_data)
            wandb.log({"predictions/avg_similarity": avg_similarity})

    def _calculate_text_similarity(self, pred: str, target: str) -> float:
        """Calculate similarity score between predicted and target text.

        :param pred: Predicted text
        :type pred: str
        :param target: Ground truth text
        :type target: str
        :return: Similarity score between 0 and 1
        :rtype: float
        """
        if not pred or not target:
            return 0.0

        return SequenceMatcher(None, pred.strip(), target.strip()).ratio()

    def evaluate_model(self, test_data: List[Dict[str, Any]]) -> EvaluationResults:
        """Evaluate the fine-tuned model on test data.

        :param test_data: Test dataset with same structure as training data
        :type test_data: List[Dict[str, Any]]
        :return: Comprehensive evaluation metrics
        :rtype: EvaluationResults

        Example:
            results = trainer.evaluate_model(test_data=test_examples)
            print(f"Average similarity: {results.avg_similarity:.2%}")
        """
        if not self.gemma3_provider:
            raise RuntimeError("Model not initialized")

        self.logger.info(f"Evaluating model on {len(test_data)} test examples...")

        predictions = []
        ground_truths = []
        similarities = []

        for i, sample in enumerate(test_data):
            result = self.gemma3_provider.call_llm([sample])

            if result and len(result) > 0:
                prediction = result[0].get("generated_text", "")
                ground_truth = sample.get("target", "")

                predictions.append(prediction)
                ground_truths.append(ground_truth)

                similarity = self._calculate_text_similarity(pred=prediction, target=ground_truth)
                similarities.append(similarity)

            if i % 10 == 0:
                self.logger.info(f"Processed {i + 1}/{len(test_data)} test examples")

        # Create evaluation results
        results = EvaluationResults(
            test_samples=len(similarities),
            avg_similarity=sum(similarities) / len(similarities) if similarities else 0.0,
            min_similarity=min(similarities) if similarities else 0.0,
            max_similarity=max(similarities) if similarities else 0.0,
            avg_pred_length=sum(len(p) for p in predictions) / len(predictions) if predictions else 0.0,
            avg_target_length=sum(len(t) for t in ground_truths) / len(ground_truths) if ground_truths else 0.0
        )

        # Log to W&B if available
        if self.wandb_run:
            wandb.log({"evaluation": results.dict()})

        self.logger.info(f"Evaluation completed. Average similarity: {results.avg_similarity:.3f}")
        return results

    def get_model_info(self) -> Dict[str, Any]:
        """Get comprehensive model and experiment information.

        :return: Model and experiment information
        :rtype: Dict[str, Any]

        Example:
            info = trainer.get_model_info()
            print(f"Experiment: {info['experiment_name']}")
            print(f"Training mode: {info['training_mode']}")
        """
        if not self.gemma3_provider:
            return {"status": "Model not initialized"}

        model_info = self.gemma3_provider.get_model_info()

        return {
            **model_info.dict(),
            "experiment_name": self.config.wandb_config.experiment_name,
            "project_name": self.config.wandb_config.project_name,
            "wandb_run_id": self.wandb_run.id if self.wandb_run else None,
            "wandb_url": self.wandb_run.url if self.wandb_run else None
        }

    def cleanup(self) -> None:
        """Clean up resources and finish W&B run.

        Example:
            trainer.cleanup()  # Call this when done with training
        """
        if self.wandb_run:
            wandb.finish()
            self.logger.info("W&B run finished")


def create_donut_experiment_config() -> ExperimentConfig:
    """Create a sample configuration for Donut-style training.

    :return: Complete experiment configuration for Donut-style training
    :rtype: ExperimentConfig

    Example:
        config = create_donut_experiment_config()
        trainer = WandbGemma3Trainer(experiment_config=config)
    """
    return ExperimentConfig(
        model_name="google/gemma-3-4b-it",
        training_mode="donut_style",
        training_params=TrainingParameters(
            learning_rate=1e-4,
            batch_size=8,
            gradient_accumulation_steps=2,
            num_epochs=5,
            warmup_ratio=0.05,
            weight_decay=0.01,
            lr_scheduler_type="cosine"
        ),
        wandb_config=WandbConfig(
            project_name="talmud-transcription",
            experiment_name="gemma3-donut-hebrew",
            tags=["gemma3", "donut", "hebrew", "manuscripts"],
            notes="Donut-style training for Hebrew manuscript transcription"
        ),
        output_dir="./models/gemma3-donut-hebrew",
        use_vision=True,
        enable_pan_scan=True,
        device="auto"
    )

def run_enhanced_training_example(data_dir: str, output_dir: str) -> None:
    """Run an example training session with the enhanced trainer.

    :param data_dir: Directory containing training data
    :type data_dir: str
    :param output_dir: Directory to save trained model
    :type output_dir: str

    Example:
        run_enhanced_training_example(
            data_dir="./talmud_data",
            output_dir="./models/enhanced-gemma3"
        )
    """
    # Create experiment configuration
    config = create_donut_experiment_config()
    config.output_dir = output_dir

    # Initialize trainer
    trainer = WandbGemma3Trainer(experiment_config=config)

    # Load data
    print("Loading training data...")
    dataloader = StructuredTalmudDataLoader(
        data_dir=data_dir,
        max_section_length=512,
        create_targeted_examples=True
    )

    pages = dataloader.load_dataset()
    all_training_data = dataloader.prepare_training_data(pages)

    # Split data
    split_idx = int(len(all_training_data) * 0.8)
    train_data = all_training_data[:split_idx]
    val_data = all_training_data[split_idx:]

    print(f"Training examples: {len(train_data)}")
    print(f"Validation examples: {len(val_data)}")

    # Train with enhanced logging
    success = trainer.train_with_wandb(
        training_data=train_data,
        validation_data=val_data
    )

    if success:
        print(f"\nTraining completed successfully!")
        print(f"Model saved to: {output_dir}")

        # Evaluate on validation data
        print("Running evaluation...")
        results = trainer.evaluate_model(test_data=val_data[:10])
        print(f"Evaluation results: {results.avg_similarity:.2%} average similarity")
    else:
        print("\nTraining failed!")

    # Clean up
    trainer.cleanup()


if __name__ == "__main__":
    # Example usage with enhanced trainer
    run_enhanced_training_example(
        data_dir="/Users/isaac1/Documents/GitHub/multimodal-document-analysis/src/etl/talmud_complete",
        output_dir="./models/enhanced_gemma3_talmud"
    )