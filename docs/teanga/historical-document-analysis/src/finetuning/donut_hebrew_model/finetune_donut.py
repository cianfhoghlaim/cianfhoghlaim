import json
import logging
from io import BytesIO
import requests
from typing import Dict, List, Optional, Tuple
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import DonutProcessor, VisionEncoderDecoderModel, Trainer, TrainingArguments
from transformers import PreTrainedTokenizerFast
from tokenizers import Tokenizer, models, normalizers, pre_tokenizers, trainers, processors
from PIL import Image
import numpy as np
import evaluate
import re
import os
import cv2
import albumentations as A
from Levenshtein import distance as levenshtein_distance
class DocumentPreprocessor:
    """Handles preprocessing of historical document images"""

    def __init__(self):
        self.augmenter = A.Compose([
            # Simulates historical document conditions
            A.OneOf([
                A.GaussNoise(var_limit=(10.0, 50.0), p=0.5),
                A.MultiplicativeNoise(multiplier=(0.9, 1.1), p=0.5),
            ], p=0.2),
            # Simulates paper degradation
            A.OneOf([
                A.RandomBrightnessContrast(brightness_limit=0.2, contrast_limit=0.2),
                A.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.1),
            ], p=0.2),
            # Simulates document warping
            A.OneOf([
                A.OpticalDistortion(distort_limit=0.05, shift_limit=0.05),
                A.GridDistortion(num_steps=5, distort_limit=0.2),
            ], p=0.2),
        ])
        self.image_size = (480, 480)

    def preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Preprocess document image for better OCR

        Args:
            image: Input PIL Image

        Returns:
            Preprocessed PIL Image
        """
        # Convert to numpy array for OpenCV processing
        img_array = np.array(image)

        # Convert to grayscale if needed
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_array

        # Denoise
        denoised = cv2.fastNlMeansDenoising(gray)

        # Adaptive thresholding to handle uneven illumination
        binary = cv2.adaptiveThreshold(
            denoised,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11,
            2
        )
        pil_image = Image.fromarray(binary)
        # Resize to the target size
        print("Resizing image")
        pil_image = pil_image.resize(self.image_size, Image.Resampling.LANCZOS)

        # Convert to RGB if grayscale
        if pil_image.mode != 'RGB':
            pil_image = Image.merge('RGB', [pil_image, pil_image, pil_image])
        return pil_image


class HistoricalDocumentDataset(Dataset):
    def __init__(
            self,
            json_data: Dict,
            processor: DonutProcessor,
            max_length: int = 1024,
            image_cache_dir: str = "./image_cache",
            augment: bool = True
    ):
        """
        Dataset for historical Hebrew document transcription

        Args:
            json_data: Dictionary containing document data
            processor: DonutProcessor instance
            max_length: Maximum length for text encoding
            image_cache_dir: Directory to cache downloaded images
            augment: Whether to apply augmentation during training
        """
        self.processor = processor
        self.max_length = max_length
        self.image_cache_dir = image_cache_dir
        self.augment = augment
        self.doc_preprocessor = DocumentPreprocessor()
        self.data = []

        os.makedirs(image_cache_dir, exist_ok=True)

        # Process and validate the data
        for doc_id, doc_data in json_data.items():
            if 'images' not in doc_data or 'text' not in doc_data:
                continue

            # Get the largest resolution image URL
            image_urls = doc_data['images'][0].split(',\n')
            largest_image = max(image_urls, key=lambda x: int(re.search(r'/(\d+),/', x).group(1)))
            clean_url = largest_image.strip().split()[0]

            # Get the transcription text
            transcription = ''
            for text in doc_data['text']:
                if text.strip() and not text.startswith('Edition:'):
                    transcription += text.strip() + ' '

            if transcription and clean_url:
                self.data.append({
                    'image_url': clean_url,
                    'text': transcription,
                    'cache_path': os.path.join(image_cache_dir, f"{doc_id}.jpg")
                })

    def download_and_cache_image(self, url: str, cache_path: str) -> Optional[Image.Image]:
        """Download and cache image

        """
        if os.path.exists(cache_path):
            print("downloaded i")
            return Image.open(cache_path)
        try:
            print(f"Downloading image from {url}")
            response = requests.get(url)
            response.raise_for_status()
            # Use the response content directly instead of making a second request
            image = Image.open(BytesIO(response.content))
            image.save(cache_path)
            print("Image saved to cache")
            return image
        except Exception as e:
            logging.log(logging.ERROR, f"Failed to download image from {url}")
            logging.log(logging.ERROR, e)
            raise ValueError(f"Failed to download image from {url}")

    def __len__(self) -> int:
        return len(self.data)

    def __getitem__(self, idx: int) -> Dict:
        item = self.data[idx]

        # Download and process image
        image = self.download_and_cache_image(item['image_url'], item['cache_path'])
        if image is None:
            # Return empty tensors if image download fails
            return {
                'pixel_values': torch.zeros((3, 224, 224)),
                'labels': torch.zeros(self.max_length),
                'attention_mask': torch.zeros(self.max_length)
            }

        # Preprocess the image
        image = self.doc_preprocessor.preprocess_image(image)

        # Apply augmentation during training if enabled
        if self.augment:
            augmented = self.doc_preprocessor.augmenter(image=np.array(image))
            image = Image.fromarray(augmented['image'])

        # Process image with Donut processor
        pixel_values = self.processor(image, return_tensors="pt").pixel_values

        # Encode text
        encoded_text = self.processor.tokenizer(
            item['text'],
            padding="max_length",
            max_length=self.max_length,
            truncation=True,
            return_tensors="pt"
        )

        return {
            'pixel_values': pixel_values.squeeze(),
            'labels': encoded_text.input_ids.squeeze(),
            'attention_mask': encoded_text.attention_mask.squeeze()
        }


def train_hebrew_tokenizer(texts: List[str], vocab_size: int = 32000) -> PreTrainedTokenizerFast:
    """
    Train a custom tokenizer optimized for historical Hebrew texts
    """
    tokenizer = Tokenizer(models.BPE())

    # Add Hebrew-specific normalization
    tokenizer.normalizer = normalizers.Sequence([
        normalizers.NFKC(),
        normalizers.Replace(r'[\u0591-\u05C7]', ''),  # Remove Hebrew diacritics
        normalizers.Replace(r'[^\u0590-\u05FF\s]', ' '),  # Keep only Hebrew characters and spaces
        normalizers.Strip()
    ])

    # Configure pre-tokenization
    tokenizer.pre_tokenizer = pre_tokenizers.Sequence([
        pre_tokenizers.WhitespaceSplit(),
        pre_tokenizers.Metaspace()
    ])

    trainer = trainers.BpeTrainer(
        vocab_size=vocab_size,
        special_tokens=["[PAD]", "[UNK]", "[CLS]", "[SEP]", "[MASK]"],
        min_frequency=2
    )

    # Create temporary file with texts
    with open('temp_train.txt', 'w', encoding='utf-8') as f:
        for text in texts:
            f.write(text + '\n')

    tokenizer.train(['temp_train.txt'], trainer)
    os.remove('temp_train.txt')

    return PreTrainedTokenizerFast(
        tokenizer_object=tokenizer,
        unk_token="[UNK]",
        pad_token="[PAD]",
        cls_token="[CLS]",
        sep_token="[SEP]",
        mask_token="[MASK]"
    )


def compute_metrics(pred, processor) -> Dict[str, float]:
    """
    Compute evaluation metrics using the evaluate library

    Args:
        pred: Prediction object containing predictions and labels

    Returns:
        Dictionary of metric names and values
    """
    # Initialize metrics
    rouge = evaluate.load('rouge')

    labels_ids = pred.label_ids
    pred_ids = pred.predictions

    # Decode predictions and labels
    pred_str = processor.batch_decode(pred_ids, skip_special_tokens=True)
    labels_ids[labels_ids == -100] = processor.tokenizer.pad_token_id
    label_str = processor.batch_decode(labels_ids, skip_special_tokens=True)

    # Calculate ROUGE scores
    rouge_output = rouge.compute(predictions=pred_str, references=label_str, use_stemmer=True)

    # Calculate Character Error Rate (CER)
    cer_scores = []
    for pred, label in zip(pred_str, label_str):
        distance = levenshtein_distance(pred, label)
        cer = distance / max(len(label), 1)
        cer_scores.append(cer)

    return {
        'rouge1': rouge_output['rouge1'],
        'rouge2': rouge_output['rouge2'],
        'rougeL': rouge_output['rougeL'],
        'cer': np.mean(cer_scores)
    }


def train_donut(
        json_data: Dict,
        output_dir: str,
        num_train_epochs: int = 5,  # Increased epochs for better learning
        learning_rate: float = 2e-5,  # Slightly lower learning rate for stability
        batch_size: int = 4,
        gradient_accumulation_steps: int = 4,
        val_split: float = 0.1,
        warmup_steps: int = 500  # Added warmup steps
):
    """
    Fine-tune the Donut model for historical Hebrew document transcription.
    """
    print('starting training')
    # Collect all texts for tokenizer training
    all_texts = []
    for doc_data in json_data.values():
        if 'text' in doc_data:
            all_texts.extend([text for text in doc_data['text'] if text.strip()])

    # Train custom tokenizer
    hebrew_tokenizer = train_hebrew_tokenizer(all_texts)

    # Initialize processor with custom tokenizer
    processor = DonutProcessor.from_pretrained("naver-clova-ix/donut-base")
    processor.tokenizer = hebrew_tokenizer

    # Initialize model
    model = VisionEncoderDecoderModel.from_pretrained("naver-clova-ix/donut-base")
    model.decoder.resize_token_embeddings(len(hebrew_tokenizer))

    # Create datasets
    dataset = HistoricalDocumentDataset(json_data, processor, augment=True)
    train_size = int((1 - val_split) * len(dataset))
    val_size = len(dataset) - train_size
    train_dataset, val_dataset = torch.utils.data.random_split(dataset, [train_size, val_size])

    # Define training arguments
    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=num_train_epochs,
        learning_rate=learning_rate,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        gradient_accumulation_steps=gradient_accumulation_steps,
        evaluation_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="rouge1",
        logging_dir=f"{output_dir}/logs",
        logging_steps=100,
        warmup_steps=warmup_steps,
        weight_decay=0.01,  # Add weight decay for regularization
    )
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        compute_metrics=lambda pred1: compute_metrics(pred1, processor),
    )

    # Train the model
    trainer.train()

    # Save the final model and tokenizer
    trainer.save_model(f"{output_dir}/final-model")
    processor.save_pretrained(f"{output_dir}/final-model")
    hebrew_tokenizer.save_pretrained(f"{output_dir}/final-model")


if __name__ == '__main__':
    # Load historical document data
    with open("/genizah_data0.json", "r") as f:
        historical_data = json.load(f)

    # Train the Donut model
    train_donut(historical_data, "")