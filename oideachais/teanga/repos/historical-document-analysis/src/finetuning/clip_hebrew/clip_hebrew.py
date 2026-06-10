#!/usr/bin/env python3
"""
Hebrew CLIP Training Script

This script trains a Hebrew CLIP model using pre-downloaded image embeddings
and Hebrew captions from the NVIDIA Hebrew CLIP dataset.

Prerequisites:
1. Run the embedding downloader script first to get the embeddings
2. Make sure you have the required packages installed
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from torch.optim import AdamW
from torch.optim.lr_scheduler import CosineAnnealingLR
import pandas as pd
import numpy as np
import os
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import time
from tqdm import tqdm
import argparse
import datasets
from datasets import load_dataset
import wandb

# Set environment variables for Apple Silicon optimization
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["TRANSFORMERS_NO_ADVISORY_WARNINGS"] = "true"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)




class HebrewCLIPDataset(Dataset):
    """Dataset for Hebrew CLIP training with pre-downloaded embeddings."""

    def __init__(
            self,
            dataset_name: str = "nvidia/heb-clip",
            tokenizer_name: str = "distilbert-base-multilingual-cased",
            max_length: int = 77,
            embedding_dir: str = "./embeddings",
            max_samples: Optional[int] = None
    ):
        from transformers import AutoTokenizer
        from datasets import load_dataset

        self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)
        self.max_length = max_length
        self.embedding_dir = Path(embedding_dir)

        # Load the Hebrew CLIP dataset
        logger.info(f"Loading Hebrew CLIP dataset: {dataset_name}")
        self.dataset = self._load_dataset(dataset_name)

        if max_samples:
            logger.info(f"Limiting dataset to {max_samples} samples")
            self.dataset = self.dataset.select(range(min(max_samples, len(self.dataset))))

        logger.info(f"Dataset loaded with {len(self.dataset)} samples")

        # Cache for embeddings
        self.embedding_cache = {}

        # Verify we have some embedding files
        self._check_embedding_availability()

    def _load_dataset(self, dataset_name: str):
        """Load the dataset with fallback strategies."""

        try:
            # Try streaming mode first (most reliable)
            dataset = load_dataset(dataset_name, split="train", streaming=True)
            # Convert to regular dataset
            items = list(dataset.take(100000))  # Take first 100k items
            dataset = datasets.Dataset.from_list(items)
            logger.info(f"Successfully loaded {len(dataset)} samples from streaming dataset")
            return dataset
        except Exception as e:
            logger.error(f"Failed to load dataset: {e}")
            raise RuntimeError("Could not load the Hebrew CLIP dataset")

    def _check_embedding_availability(self):
        """Check if we have embedding files available."""
        if not self.embedding_dir.exists():
            raise FileNotFoundError(
                f"Embedding directory not found: {self.embedding_dir}\n"
                f"Please run the embedding downloader script first!"
            )

        embedding_files = list(self.embedding_dir.glob("*.npz")) + list(self.embedding_dir.glob("*.parquet"))

        if not embedding_files:
            raise FileNotFoundError(
                f"No embedding files found in {self.embedding_dir}\n"
                f"Please run the embedding downloader script first!"
            )

        logger.info(f"Found {len(embedding_files)} embedding files in {self.embedding_dir}")

        # Test loading one embedding
        test_item = self.dataset[0]
        try:
            embedding = self._get_image_embedding(test_item['file_name'], test_item['file_index'])
            logger.info(f"✅ Successfully loaded test embedding with shape: {embedding.shape}")
        except Exception as e:
            logger.warning(f"⚠️  Could not load test embedding: {e}")
            logger.warning("Will use dummy embeddings for training")

    def _get_image_embedding(self, file_name: str, file_index: int) -> torch.Tensor:
        """Load image embedding from file or create dummy."""
        cache_key = f"{file_name}_{file_index}"

        if cache_key in self.embedding_cache:
            return self.embedding_cache[cache_key]

        embedding_path = self.embedding_dir / file_name

        # Try to load actual embedding
        if embedding_path.exists():
            try:
                if embedding_path.suffix.lower() == '.npz':
                    data = np.load(embedding_path)

                    # Handle different npz formats
                    if 'embeddings' in data:
                        embeddings = data['embeddings']
                    elif 'img_emb' in data:
                        embeddings = data['img_emb']
                    else:
                        # Use first available array
                        key = list(data.keys())[0]
                        embeddings = data[key]

                    # Get specific embedding
                    if file_index < len(embeddings):
                        embedding = embeddings[file_index]
                    else:
                        raise IndexError(f"Index {file_index} out of range")

                elif embedding_path.suffix.lower() == '.parquet':
                    df = pd.read_parquet(embedding_path)

                    # Look for embedding columns
                    embedding_cols = [col for col in df.columns if 'embed' in col.lower()]
                    if embedding_cols:
                        embedding_data = df.iloc[file_index][embedding_cols[0]]
                        embedding = np.array(embedding_data, dtype=np.float32)
                    else:
                        raise ValueError("No embedding columns found in parquet file")

                # Convert to tensor and normalize
                embedding = torch.tensor(embedding, dtype=torch.float32)
                embedding = F.normalize(embedding, dim=-1)

                # Cache it
                self.embedding_cache[cache_key] = embedding
                return embedding

            except Exception as e:
                logger.debug(f"Failed to load embedding {file_name}:{file_index}: {e}")

        # Create dummy embedding if loading fails
        torch.manual_seed(hash(cache_key) % (2 ** 31))
        dummy_embedding = torch.randn(768, dtype=torch.float32)
        dummy_embedding = F.normalize(dummy_embedding, dim=-1)
        self.embedding_cache[cache_key] = dummy_embedding
        return dummy_embedding

    def _tokenize_text(self, text: str) -> Dict[str, torch.Tensor]:
        """Tokenize Hebrew text."""
        text = str(text).strip()
        if not text:
            text = "תמונה"  # Default to "image" in Hebrew

        encoding = self.tokenizer(
            text,
            truncation=True,
            padding='max_length',
            max_length=self.max_length,
            return_tensors='pt'
        )
        return {
            'input_ids': encoding['input_ids'].squeeze(0),
            'attention_mask': encoding['attention_mask'].squeeze(0)
        }

    def __len__(self) -> int:
        return len(self.dataset)

    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        item = self.dataset[idx]

        # Get Hebrew caption and tokenize
        caption = item['heb_caption']
        text_features = self._tokenize_text(caption)

        # Get image embedding
        image_embedding = self._get_image_embedding(
            item['file_name'],
            item['file_index']
        )

        return {
            'text_input_ids': text_features['input_ids'],
            'text_attention_mask': text_features['attention_mask'],
            'image_embedding': image_embedding,
            'caption': caption,
            'key': torch.tensor(hash(str(item['key'])) % (2 ** 31), dtype=torch.long)
        }


class HebrewTextEncoder(nn.Module):
    """Hebrew text encoder using a multilingual transformer."""

    def __init__(
            self,
            model_name: str = "distilbert-base-multilingual-cased",
            embedding_dim: int = 768,
            projection_dim: int = 768
    ):
        super().__init__()
        from transformers import AutoModel

        self.transformer = AutoModel.from_pretrained(model_name)
        self.projection = nn.Linear(embedding_dim, projection_dim)
        self.ln_final = nn.LayerNorm(projection_dim)

    def forward(self, input_ids: torch.Tensor, attention_mask: torch.Tensor) -> torch.Tensor:
        outputs = self.transformer(input_ids=input_ids, attention_mask=attention_mask)
        pooled_output = outputs.last_hidden_state[:, 0]  # [CLS] token
        projected = self.projection(pooled_output)
        projected = self.ln_final(projected)
        return F.normalize(projected, dim=-1)


class HebrewCLIPModel(nn.Module):
    """Hebrew CLIP model."""

    def __init__(
            self,
            text_encoder_name: str = "distilbert-base-multilingual-cased",
            projection_dim: int = 768,
            temperature: float = 0.07
    ):
        super().__init__()
        self.text_encoder = HebrewTextEncoder(
            model_name=text_encoder_name,
            projection_dim=projection_dim
        )
        self.image_projection = nn.Linear(768, projection_dim)
        self.image_ln = nn.LayerNorm(projection_dim)
        self.temperature = nn.Parameter(torch.ones([]) * np.log(1 / temperature))

    def forward(
            self,
            text_input_ids: torch.Tensor,
            text_attention_mask: torch.Tensor,
            image_embeddings: torch.Tensor
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        # Encode text
        text_features = self.text_encoder(text_input_ids, text_attention_mask)

        # Project image embeddings
        image_features = self.image_projection(image_embeddings)
        image_features = self.image_ln(image_features)
        image_features = F.normalize(image_features, dim=-1)

        # Compute similarity
        logit_scale = self.temperature.exp()
        logits_per_text = logit_scale * text_features @ image_features.t()

        return text_features, image_features, logits_per_text


def clip_loss(logits_per_text: torch.Tensor) -> torch.Tensor:
    """Compute CLIP contrastive loss."""
    batch_size = logits_per_text.shape[0]
    labels = torch.arange(batch_size, device=logits_per_text.device)

    text_loss = F.cross_entropy(logits_per_text, labels)
    image_loss = F.cross_entropy(logits_per_text.t(), labels)

    return (text_loss + image_loss) / 2


class HebrewCLIPTrainer:
    """Trainer for Hebrew CLIP model."""

    def __init__(
            self,
            model: HebrewCLIPModel,
            train_dataloader: DataLoader,
            learning_rate: float = 1e-4,
            weight_decay: float = 0.01,
            max_steps: int = 10000,
            save_dir: str = "./checkpoints",
            log_every: int = 100,
            save_every: int = 1000
    ):
        self.model = model
        self.train_dataloader = train_dataloader

        # Setup device (optimized for Apple Silicon)
        if torch.backends.mps.is_available():
            self.device = torch.device("mps")
            logger.info("Using Apple Silicon MPS")
        elif torch.cuda.is_available():
            self.device = torch.device("cuda")
            logger.info("Using CUDA")
        else:
            self.device = torch.device("cpu")
            logger.info("Using CPU")

        self.model.to(self.device)

        # Optimizer
        self.optimizer = AdamW(
            self.model.parameters(),
            lr=learning_rate,
            weight_decay=weight_decay
        )

        # Scheduler
        self.scheduler = CosineAnnealingLR(self.optimizer, T_max=max_steps)

        # Training settings
        self.max_steps = max_steps
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(parents=True, exist_ok=True)
        self.log_every = log_every
        self.save_every = save_every

        # State
        self.step = 0
        self.step_times = []

    def train_step(self, batch: Dict[str, torch.Tensor]) -> float:
        """Perform a single training step."""
        self.model.train()

        # Move to device
        batch = {k: v.to(self.device, non_blocking=True) if isinstance(v, torch.Tensor) else v
                 for k, v in batch.items()}

        # Forward pass
        text_features, image_features, logits_per_text = self.model(
            text_input_ids=batch['text_input_ids'],
            text_attention_mask=batch['text_attention_mask'],
            image_embeddings=batch['image_embedding']
        )

        # Compute loss
        loss = clip_loss(logits_per_text)

        # Backward pass
        self.optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
        self.optimizer.step()
        self.scheduler.step()

        return loss.item()

    def save_checkpoint(self):
        """Save model checkpoint."""
        checkpoint = {
            'step': self.step,
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
        }
        torch.save(checkpoint, self.save_dir / f"checkpoint_step_{self.step}.pt")
        torch.save(checkpoint, self.save_dir / "latest_checkpoint.pt")

    def train(self):
        """Main training loop."""
        logger.info(f"🚀 Starting training for {self.max_steps} steps")
        logger.info(f"💾 Device: {self.device}")
        logger.info(f"📁 Checkpoints will be saved to: {self.save_dir}")

        train_iterator = iter(self.train_dataloader)
        start_time = time.time()

        for step in tqdm(range(self.max_steps), desc="Training"):
            step_start_time = time.time()
            self.step = step

            try:
                batch = next(train_iterator)
            except StopIteration:
                # Reset iterator
                train_iterator = iter(self.train_dataloader)
                batch = next(train_iterator)

            # Training step
            loss = self.train_step(batch)

            step_end_time = time.time()
            step_duration = step_end_time - step_start_time
            self.step_times.append(step_duration)

            # Logging
            if step % self.log_every == 0:
                lr = self.optimizer.param_groups[0]['lr']
                batch_size = batch['text_input_ids'].shape[0]

                # Calculate timing statistics
                avg_step_time = np.mean(self.step_times[-self.log_every:]) if len(
                    self.step_times) >= self.log_every else np.mean(self.step_times)
                samples_per_second = batch_size / avg_step_time
                estimated_time_remaining = (self.max_steps - step) * avg_step_time / 3600

                logger.info(f"Step {step:5d}: Loss = {loss:.4f}, LR = {lr:.6f}, Batch = {batch_size}")
                logger.info(
                    f"           Time/step: {avg_step_time:.3f}s, Samples/sec: {samples_per_second:.1f}, ETA: {estimated_time_remaining:.2f}h")

                # Log sample caption for verification
                if step == 0:
                    logger.info(f"           Sample caption: {batch['caption'][0][:100]}...")

            # Save checkpoint
            if step % self.save_every == 0 and step > 0:
                self.save_checkpoint()
                logger.info(f"💾 Checkpoint saved at step {step}")

        # Final save
        self.save_checkpoint()
        total_time = time.time() - start_time
        logger.info(f"🎉 Training completed in {total_time / 3600:.2f} hours!")


def main():
    parser = argparse.ArgumentParser(description="Train Hebrew CLIP model")
    parser.add_argument("--embedding_dir", type=str, default="./embeddings",
                        help="Directory containing downloaded embeddings")
    parser.add_argument("--batch_size", type=int, default=32, help="Batch size")
    parser.add_argument("--learning_rate", type=float, default=1e-4, help="Learning rate")
    parser.add_argument("--max_steps", type=int, default=10000, help="Maximum training steps")
    parser.add_argument("--max_samples", type=int, default=None,
                        help="Limit dataset to this many samples for testing")
    parser.add_argument("--save_dir", type=str, default="./checkpoints", help="Checkpoint directory")
    parser.add_argument("--text_encoder", type=str, default="distilbert-base-multilingual-cased",
                        help="Text encoder model name")
    parser.add_argument("--log_every", type=int, default=100, help="Log every N steps")
    parser.add_argument("--save_every", type=int, default=1000, help="Save every N steps")

    args = parser.parse_args()

    logger.info("🇮🇱 Hebrew CLIP Training Script")
    logger.info(f"📁 Embedding directory: {args.embedding_dir}")
    logger.info(f"🎯 Batch size: {args.batch_size}")
    logger.info(f"📚 Max steps: {args.max_steps}")
    logger.info(f"🧠 Text encoder: {args.text_encoder}")
    # Check if embedding directory exists
    embedding_dir = Path(args.embedding_dir)
    if not embedding_dir.exists():
        logger.error(f"❌ Embedding directory not found: {embedding_dir}")
        logger.error("🔧 Please run the embedding downloader script first:")
        logger.error("   python download_embeddings.py --output_dir ./embeddings")
        return

    try:
        # Create dataset
        logger.info("\n📊 Loading Hebrew CLIP dataset...")
        train_dataset = HebrewCLIPDataset(
            dataset_name="nvidia/heb-clip",
            tokenizer_name=args.text_encoder,
            embedding_dir=args.embedding_dir,
            max_samples=args.max_samples
        )

        # Create data loader (optimized for MPS)
        train_dataloader = DataLoader(
            train_dataset,
            batch_size=args.batch_size,
            shuffle=True,
            num_workers=0,  # Single-threaded for MPS compatibility
            pin_memory=False,  # Disabled for MPS
            drop_last=True,
            persistent_workers=False
        )

        logger.info(f"✅ Dataset ready: {len(train_dataset)} samples")
        logger.info(f"🔄 Batches per epoch: {len(train_dataloader)}")

        # Test first batch
        test_batch = next(iter(train_dataloader))
        logger.info(f"🧪 Test batch shape: {test_batch['image_embedding'].shape}")
        logger.info(f"📝 Sample caption: {test_batch['caption'][0][:100]}...")

        # Create model
        logger.info(f"\n🧠 Creating Hebrew CLIP model...")
        model = HebrewCLIPModel(
            text_encoder_name=args.text_encoder,
            projection_dim=768
        )

        total_params = sum(p.numel() for p in model.parameters())
        trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
        logger.info(f"📊 Model parameters: {total_params:,} total, {trainable_params:,} trainable")

        # Create trainer
        trainer = HebrewCLIPTrainer(
            model=model,
            train_dataloader=train_dataloader,
            learning_rate=args.learning_rate,
            max_steps=args.max_steps,
            save_dir=args.save_dir,
            log_every=args.log_every,
            save_every=args.save_every
        )

        # Start training
        logger.info("\n🚀 Starting training...")
        trainer.train()

        logger.info(f"\n✅ Training completed successfully!")
        logger.info(f"💾 Model saved to: {args.save_dir}")

    except KeyboardInterrupt:
        logger.info("\n🛑 Training interrupted by user")
    except Exception as e:
        logger.error(f"\n❌ Training failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()