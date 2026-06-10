from typing import Dict, List, Any, Optional
from PIL import Image
import json
import logging
from dataclasses import dataclass
from enum import Enum
from src.models.llm.gemma_three import Gemma3Provider  # Assuming the enhanced version
from src.finetuning_scripts.diagnostic_scripts.gemma_trainer_diagnostic import fix_gradient_issues

class DocumentType(Enum):
    """Document type enumeration for specialized processing."""
    MANUSCRIPT = "manuscript"
    PRINTED_TEXT = "printed_text"
    HANDWRITTEN = "handwritten"
    FORM = "form"
    TABLE = "table"
    MIXED = "mixed"


@dataclass
class DonutTrainingConfig:
    """Configuration for Donut-style training..."""
    # Model settings
    model_name: str = "google/gemma-3-1b-it"
    training_mode: str = "donut_style"

    # Training parameters
    learning_rate: float = 1e-4
    batch_size: int = 8
    gradient_accumulation_steps: int = 2
    num_epochs: int = 5
    warmup_ratio: float = 0.05
    weight_decay: float = 0.01

    # Document-specific settings
    document_type: DocumentType = DocumentType.MANUSCRIPT
    max_sequence_length: int = 2048
    max_output_length: int = 512

    # Vision settings
    enable_pan_scan: bool = True
    image_preprocessing: Dict[str, Any] = None

    # Output settings
    output_dir: str = "./donut-gemma-model"
    save_steps: int = 100
    eval_steps: int = 100
    logging_steps: int = 10

    def __post_init__(self):
        if self.image_preprocessing is None:
            self.image_preprocessing = {
                "resize": True,
                "target_size": (224, 224),
                "normalize": True,
                "enhance_contrast": True
            }


class DonutDataPreprocessor:
    """Preprocessor for document transcription data in Donut style."""

    def __init__(self, config: DonutTrainingConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)

    def preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Preprocess image for better document recognition.

        :param image: Input image
        :type image: Image.Image
        :return: Preprocessed image
        :rtype: Image.Image
        """
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')

        # Apply preprocessing based on config
        if self.config.image_preprocessing.get("enhance_contrast", False):
            from PIL import ImageEnhance
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.2)

        if self.config.image_preprocessing.get("resize", False):
            target_size = self.config.image_preprocessing.get("target_size", (224, 224))
            image = image.resize(target_size, Image.Resampling.LANCZOS)

        return image

    def format_transcription_prompt(self,
                                    document_type: DocumentType,
                                    language: str = "hebrew",
                                    additional_instructions: Optional[str] = None) -> str:
        """
        Create specialized prompts for different document types.

        :param document_type: Type of document
        :type document_type: DocumentType
        :param language: Document language
        :type language: str
        :param additional_instructions: Extra instructions
        :type additional_instructions: Optional[str]
        :return: Formatted prompt
        :rtype: str
        """
        base_prompts = {
            DocumentType.MANUSCRIPT: f"Transcribe this {language} manuscript accurately, preserving the original text structure and formatting.",
            DocumentType.PRINTED_TEXT: f"Extract and transcribe all {language} text from this printed document.",
            DocumentType.HANDWRITTEN: f"Carefully transcribe this handwritten {language} text, noting any unclear characters.",
            DocumentType.FORM: f"Extract all text content from this {language} form, maintaining field relationships.",
            DocumentType.TABLE: f"Transcribe this {language} table, preserving row and column structure.",
            DocumentType.MIXED: f"Transcribe all {language} text from this document, noting different text types and layouts."
        }

        prompt = base_prompts.get(document_type, base_prompts[DocumentType.MIXED])

        if additional_instructions:
            prompt += f" {additional_instructions}"

        return prompt

    def prepare_training_example(self,
                                 image_path: str,
                                 transcription: str,
                                 document_type: Optional[DocumentType] = None,
                                 language: str = "hebrew",
                                 metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Prepare a single training example in Donut format.

        :param image_path: Path to document image
        :type image_path: str
        :param transcription: Ground truth transcription
        :type transcription: str
        :param document_type: Type of document
        :type document_type: Optional[DocumentType]
        :param language: Document language
        :type language: str
        :param metadata: Additional metadata
        :type metadata: Optional[Dict[str, Any]]
        :return: Formatted training example
        :rtype: Dict[str, Any]
        """
        document_type = document_type or self.config.document_type

        # Load and preprocess image
        image = Image.open(image_path)
        processed_image = self.preprocess_image(image)

        # Create prompt
        prompt = self.format_transcription_prompt(
            document_type=document_type,
            language=language
        )

        return {
            "text": prompt,
            "target": transcription,
            "images": [processed_image],
            "metadata": {
                "image_path": image_path,
                "document_type": document_type.value,
                "language": language,
                **(metadata or {})
            }
        }

    def prepare_dataset_from_json(self, json_path: str) -> List[Dict[str, Any]]:
        """
        Prepare dataset from JSON annotation file.

        Expected JSON format:
        [
            {
                "image_path": "path/to/image.jpg",
                "transcription": "transcribed text",
                "document_type": "manuscript",
                "language": "hebrew",
                "metadata": {...}
            },
            ...
        ]

        :param json_path: Path to JSON annotations
        :type json_path: str
        :return: List of training examples
        :rtype: List[Dict[str, Any]]
        """
        with open(json_path, 'r', encoding='utf-8') as f:
            annotations = json.load(f)

        training_examples = []
        for annotation in annotations:
            try:
                doc_type = DocumentType(annotation.get("document_type", "manuscript"))

                example = self.prepare_training_example(
                    image_path=annotation["image_path"],
                    transcription=annotation["transcription"],
                    document_type=doc_type,
                    language=annotation.get("language", "hebrew"),
                    metadata=annotation.get("metadata", {})
                )
                training_examples.append(example)

            except Exception as e:
                self.logger.warning(f"Failed to process annotation: {annotation}. Error: {e}")
                continue

        self.logger.info(f"Prepared {len(training_examples)} training examples from {json_path}")
        return training_examples


class DonutTrainingPipeline:
    """Complete training pipeline for Donut-style document transcription."""

    def __init__(self, config: DonutTrainingConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.preprocessor = DonutDataPreprocessor(config)

    def setup_model(self) -> 'Gemma3Provider':
        """
        Setup and configure the model for training.

        :return: Configured Gemma3Provider
        :rtype: Gemma3Provider
        """

        provider = Gemma3Provider(
            model_name=self.config.model_name,
            device="auto",
            use_vision=True,
            enable_pan_scan=self.config.enable_pan_scan,
            max_input_sequence=self.config.max_sequence_length,
            max_output_length=self.config.max_output_length
        )

        # Prepare for Donut-style training
        provider.prepare_for_training(
            training_mode=self.config.training_mode,
            enable_gradient_checkpointing=True
        )

        success = fix_gradient_issues(provider)
        if not success:
            self.logger.error("❌ Gradient issues not resolved!")
            raise ValueError("Diagnostic failing")
        return provider

    def train_from_annotations(self,
                               train_json: str,
                               val_json: Optional[str] = None,
                               resume_from_checkpoint: Optional[str] = None) -> 'Trainer':
        """
        Train model from JSON annotation files.

        :param train_json: Path to training annotations
        :type train_json: str
        :param val_json: Path to validation annotations
        :type val_json: Optional[str]
        :param resume_from_checkpoint: Path to checkpoint to resume from
        :type resume_from_checkpoint: Optional[str]
        :return: Trainer instance
        :rtype: Trainer
        """
        # Prepare data
        self.logger.info("Preparing training data...")
        train_data = self.preprocessor.prepare_dataset_from_json(train_json)

        val_data = None
        if val_json:
            self.logger.info("Preparing validation data...")
            val_data = self.preprocessor.prepare_dataset_from_json(val_json)

        # Setup model
        self.logger.info("Setting up model...")
        provider = self.setup_model()

        # Log model info
        model_info = provider.get_model_info()
        self.logger.info(f"Model setup complete: {model_info['trainable_parameters']:,} trainable parameters "
                         f"({model_info['trainable_ratio']:.2%} of total)")

        # Train
        self.logger.info("Starting training...")
        trainer = provider.train(
            training_data=train_data,
            validation_data=val_data,
            output_dir=self.config.output_dir,
            batch_size=self.config.batch_size,
            gradient_accumulation_steps=self.config.gradient_accumulation_steps,
            num_epochs=self.config.num_epochs,
            learning_rate=self.config.learning_rate,
            warmup_ratio=self.config.warmup_ratio,
            logging_steps=self.config.logging_steps,
            save_steps=self.config.save_steps,
            eval_steps=self.config.eval_steps,
            use_recommended_params=False  # We're providing our own params
        )

        return trainer

    def evaluate_transcription_quality(self,
                                       provider: 'Gemma3Provider',
                                       test_data: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Evaluate transcription quality on test data.

        :param provider: Trained model provider
        :type provider: Gemma3Provider
        :param test_data: Test examples
        :type test_data: List[Dict[str, Any]]
        :return: Evaluation metrics
        :rtype: Dict[str, float]
        """
        from difflib import SequenceMatcher

        results = provider.call_llm(test_data)

        exact_matches = 0
        similarity_scores = []

        for i, (result, expected) in enumerate(zip(results, test_data)):
            predicted = result["generated_text"].strip()
            target = expected["target"].strip()

            # Exact match
            if predicted == target:
                exact_matches += 1

            # Similarity score
            similarity = SequenceMatcher(None, predicted, target).ratio()
            similarity_scores.append(similarity)

        return {
            "exact_match_accuracy": exact_matches / len(test_data),
            "average_similarity": sum(similarity_scores) / len(similarity_scores),
            "total_examples": len(test_data)
        }


# Usage example function
def create_donut_training_example():
    """Example of how to use the Donut training pipeline."""

    # Configuration
    config = DonutTrainingConfig(
        model_name="google/gemma-3-1b-it",
        training_mode="donut_style",
        document_type=DocumentType.MANUSCRIPT,
        learning_rate=1e-4,
        batch_size=4,
        num_epochs=3,
        output_dir="./hebrew-manuscript-model"
    )

    # Create pipeline
    pipeline = DonutTrainingPipeline(config)

    # Train (assuming you have annotation files)
    # trainer = pipeline.train_from_annotations(
    #     train_json="train_annotations.json",
    #     val_json="val_annotations.json"
    # )

    return pipeline


if __name__ == "__main__":
    # Example usage
    pipeline = create_donut_training_example()
    print("Donut training pipeline created successfully!")
    print(f"Config: {pipeline.config}")