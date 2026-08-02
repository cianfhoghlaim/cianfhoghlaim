"""
CORD-v2 Dataset Loader

This module provides functionality to load the CORD-v2 dataset from Hugging Face.
CORD-v2 is a dataset for document understanding and OCR, containing receipt images
with structured annotations.

Dataset: naver-clova-ix/cord-v2
Paper: https://arxiv.org/abs/2103.10213
"""

import os
import logging
from pathlib import Path
from typing import Any
from datasets import load_dataset, DatasetDict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CordDatasetLoader:
    """
    A class to handle loading and managing the CORD-v2 dataset.
    """
    
    def __init__(self, base_dir: str | None = None):
        """
        Initialize the CORD dataset loader.
        
        Args:
            base_dir: Base directory for storing dataset files. 
                     Defaults to './data' in the current working directory.
        """
        if base_dir is None:
            base_dir = os.path.join(os.getcwd(), "data")
        
        self.base_dir = Path(base_dir)
        self.dataset_dir = self.base_dir / "cord-v2"
        self.cache_dir = self.dataset_dir / "cache"
        
        # Create directories if they don't exist
        self.dataset_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Dataset directory: {self.dataset_dir}")
        logger.info(f"Cache directory: {self.cache_dir}")
    
    def load_dataset(self, force_reload: bool = False) -> DatasetDict:
        """
        Load the CORD-v2 dataset from Hugging Face.
        
        Args:
            force_reload: If True, forces re-download even if cached data exists.
            
        Returns:
            DatasetDict containing the loaded dataset splits.
        """
        try:
            logger.info("Loading CORD-v2 dataset from Hugging Face...")
            
            # Load dataset with caching
            dataset = load_dataset(
                "naver-clova-ix/cord-v2",
                cache_dir=str(self.cache_dir),
                download_mode="force_redownload" if force_reload else None
            )
            
            logger.info(f"Dataset loaded successfully!")
            logger.info(f"Available splits: {list(dataset.keys())}")
            
            # Log dataset statistics
            for split_name, split_data in dataset.items():
                logger.info(f"{split_name} split: {len(split_data)} examples")
            
            return dataset
            
        except Exception as e:
            logger.error(f"Error loading dataset: {str(e)}")
            raise
    
    def get_dataset_info(self, dataset: DatasetDict) -> dict[str, Any]:
        """
        Get information about the loaded dataset.
        
        Args:
            dataset: The loaded DatasetDict
            
        Returns:
            Dictionary containing dataset information
        """
        info = {
            "splits": list(dataset.keys()),
            "total_examples": sum(len(split) for split in dataset.values()),
            "features": {}
        }
        
        # Get features from the first available split
        if dataset:
            first_split = next(iter(dataset.values()))
            info["features"] = first_split.features
            
            # Get a sample example to understand the structure
            if len(first_split) > 0:
                sample = first_split[0]
                info["sample_keys"] = list(sample.keys())
        
        return info
    
    def save_dataset_locally(self, dataset: DatasetDict, format: str = "parquet") -> None:
        """
        Save the dataset to local files in the specified format.
        Note: Images cannot be saved to JSON/CSV formats, only parquet preserves them.
        
        Args:
            dataset: The loaded DatasetDict
            format: Format to save in ('parquet', 'metadata_json'). Default is 'parquet'.
        """
        save_dir = self.dataset_dir / "saved"
        save_dir.mkdir(exist_ok=True)
        
        logger.info(f"Saving dataset to {save_dir} in {format} format...")
        
        for split_name, split_data in dataset.items():
            if format == "parquet":
                file_path = save_dir / f"{split_name}.parquet"
                split_data.to_parquet(str(file_path))
                logger.info(f"Saved {split_name} split to {file_path}")
            elif format == "metadata_json":
                # Save only the metadata (ground_truth) without images
                file_path = save_dir / f"{split_name}_metadata.json"
                metadata_only = split_data.remove_columns(['image'])
                metadata_only.to_json(str(file_path))
                logger.info(f"Saved {split_name} metadata to {file_path}")
            else:
                raise ValueError(f"Unsupported format: {format}. Use 'parquet' or 'metadata_json'")
    
    def save_images_and_metadata(self, dataset: DatasetDict, max_samples: int = None) -> None:
        """
        Save images and their metadata separately for easy inspection.
        
        Args:
            dataset: The loaded DatasetDict
            max_samples: Maximum number of samples to save per split. If None, saves all samples.
        """
        save_dir = self.dataset_dir / "images_and_metadata"
        save_dir.mkdir(exist_ok=True)
        
        logger.info(f"Saving images and metadata to {save_dir}...")
        
        for split_name, split_data in dataset.items():
            split_dir = save_dir / split_name
            split_dir.mkdir(exist_ok=True)
            
            num_samples = len(split_data) if max_samples is None else min(max_samples, len(split_data))
            
            logger.info(f"Saving {num_samples} samples from {split_name} split...")
            
            for i in range(num_samples):
                sample = split_data[i]
                
                # Save image
                image_path = split_dir / f"{split_name}_{i:03d}.png"
                sample['image'].save(str(image_path))
                
                # Save metadata
                metadata_path = split_dir / f"{split_name}_{i:03d}_metadata.json"
                with open(metadata_path, 'w') as f:
                    import json
                    json.dump(sample['ground_truth'], f, indent=2, ensure_ascii=False)
                
                # Progress indicator for large datasets
                if (i + 1) % 50 == 0 or (i + 1) == num_samples:
                    logger.info(f"  Processed {i + 1}/{num_samples} samples for {split_name}")
            
            logger.info(f"Completed saving {num_samples} samples from {split_name} split to {split_dir}")
    
    def get_sample_data(self, dataset: DatasetDict, split: str = "train", num_samples: int = 5) -> list:
        """
        Get sample data from a specific split.
        
        Args:
            dataset: The loaded DatasetDict
            split: Split to sample from (default: "train")
            num_samples: Number of samples to return (default: 5)
            
        Returns:
            List of sample examples
        """
        if split not in dataset:
            available_splits = list(dataset.keys())
            raise ValueError(f"Split '{split}' not found. Available splits: {available_splits}")
        
        split_data = dataset[split]
        num_samples = min(num_samples, len(split_data))
        
        return [split_data[i] for i in range(num_samples)]


def load_cord_dataset(base_dir: str | None = None, force_reload: bool = False) -> DatasetDict:
    """
    Convenience function to load the CORD-v2 dataset.
    
    Args:
        base_dir: Base directory for storing dataset files.
        force_reload: If True, forces re-download even if cached data exists.
        
    Returns:
        DatasetDict containing the loaded dataset.
    """
    loader = CordDatasetLoader(base_dir)
    return loader.load_dataset(force_reload)


def main():
    """
    Download and save the complete CORD-v2 dataset in all formats.
    """
    print("🚀 Starting CORD-v2 dataset download and processing...")
    
    # Initialize the loader
    loader = CordDatasetLoader()
    
    # Load the dataset
    print("\n📥 Loading dataset from Hugging Face...")
    dataset = loader.load_dataset()
    
    # Get dataset information
    info = loader.get_dataset_info(dataset)
    print("\n📊 Dataset Information")
    print("=" * 50)
    print(f"Splits: {info['splits']}")
    print(f"Total examples: {info['total_examples']}")
    print(f"Sample keys: {info.get('sample_keys', 'N/A')}")
    
    # Show breakdown by split
    for split_name, split_data in dataset.items():
        print(f"  {split_name}: {len(split_data)} examples")
    
    print("\n💾 Saving dataset in multiple formats...")
    
    # 1. Save all images and metadata as individual files
    print("\n1️⃣ Saving all images and metadata as individual files...")
    loader.save_images_and_metadata(dataset, max_samples=None)  # Save ALL samples
    
    # 2. Save metadata in JSON format (without images)
    print("\n2️⃣ Saving metadata in JSON format...")
    loader.save_dataset_locally(dataset, format="metadata_json")
    
    # 3. Save full dataset in parquet format (with images)
    print("\n3️⃣ Saving full dataset in Parquet format...")
    loader.save_dataset_locally(dataset, format="parquet")
    
    # Summary
    print("\n✅ Complete! Dataset saved in multiple formats:")
    print("=" * 60)
    print(f"📁 Dataset directory: {loader.dataset_dir}")
    print(f"🗂️  Cache (Arrow format): {loader.cache_dir}")
    print(f"🖼️  Individual images: {loader.dataset_dir}/images_and_metadata/")
    print(f"📄 Metadata JSON files: {loader.dataset_dir}/saved/*_metadata.json")
    print(f"📦 Parquet files: {loader.dataset_dir}/saved/*.parquet")
    
    print(f"\n📈 Dataset Statistics:")
    print(f"  • Total examples: {info['total_examples']}")
    print(f"  • Train: {len(dataset['train'])} examples")
    print(f"  • Validation: {len(dataset['validation'])} examples") 
    print(f"  • Test: {len(dataset['test'])} examples")
    
    print("\n🎯 Ready for multimodal evaluation tasks!")


if __name__ == "__main__":
    main()
