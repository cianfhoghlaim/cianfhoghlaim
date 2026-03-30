# embedding_models.py
import os
import torch
import numpy as np
import pickle
import hashlib
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Union, Tuple
from abc import ABC, abstractmethod
from transformers import CLIPModel
from transformers.models.clip import CLIPProcessor

# Import NOMIC-specific modules
from colpali_engine.models import ColQwen2_5, ColQwen2_5_Processor
from transformers.utils.import_utils import is_flash_attn_2_available


logger = logging.getLogger(__name__)

class TextEmbedding(ABC):
    """Base class for text embedding models with common methods and attributes"""

    def __init__(self):
        self.device = self._get_device()
        self.cache_dir = Path("embedding_cache")
        self.cache_dir.mkdir(exist_ok=True)

    def _get_device(self):
        """Determine the best available device"""
        if torch.cuda.is_available():
            return "cuda:0"
        elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            return "mps"
        else:
            return "cpu"

    @abstractmethod
    def get_text_embeddings(self, text: str):
        """Get embeddings for text"""
        pass

class MultiModalEmbedding(ABC):
    """Base class for multimodal embedding models with common methods and attributes"""

    def __init__(self):
        self.device = self._get_device()
        self.cache_dir = Path("embedding_cache")
        self.cache_dir.mkdir(exist_ok=True)

    def _get_device(self):
        """Determine the best available device"""
        if torch.cuda.is_available():
            return "cuda:0"
        elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            return "mps"
        else:
            return "cpu"

    @abstractmethod
    def get_embeddings(self, image, text: str):
        """Get embeddings for image and text"""
        pass

    @abstractmethod
    def get_embedding_multilingual(self, image, text, description_text, translation_text):
        """Get embeddings for image and multiple text types"""
        pass

    def get_cache_path(self, model_name: str, identifier: str) -> Path:
        """Generate a unique cache path based on the model and identifier"""
        hash_obj = hashlib.md5((model_name + identifier).encode())
        hash_id = hash_obj.hexdigest()
        return self.cache_dir / f"embeddings_{hash_id}.pkl"

    def save_to_cache(self, cache_path: Path, data):
        """Save embedding data to cache using Pickle"""
        with open(cache_path, 'wb') as f:
            pickle.dump(data, f)
        logger.info(f"Embeddings cached to {cache_path}")

    def load_from_cache(self, cache_path: Path):
        """Load embedding data from cache"""
        with open(cache_path, 'rb') as f:
            data = pickle.load(f)
        logger.info(f"Embeddings loaded from cache: {cache_path}")
        return data

    def check_cache(self, cache_path: Path) -> bool:
        """Check if cache file exists"""
        return cache_path.exists()


class NomicsEmbedding(MultiModalEmbedding):
    """NOMIC multimodal embedding model implementation"""

    def __init__(self, model_name: str = "nomic-ai/colnomic-embed-multimodal-7b", text_only: bool = False,
                 image_only: bool = False):
        """
        The code to create Nomics Multimodal Embedding model is based on the code from the following link:
        :param model_name: The name of the model to use. Default is "nomic-ai/colnomic-embed-multimodal-7b"
        :type model_name: str
        :param text_only: Whether to use only text embeddings. Default is False.
        :type text_only: bool
        :param image_only: Whether to use only image embeddings. Default is False.
        :type image_only: bool
        """
        super().__init__()
        self.model_name = model_name
        self.model, self.processor = self._setup_model()
        logger.info(f"NomicsEmbedding initialized with device: {self.device}")
        self.text_only = text_only
        self.image_only = image_only

    def _setup_model(self) -> tuple[Any, Any]:
        """Initialize the model and processor with appropriate settings
        :return: A tuple containing the model and processor objects.
        """
        # Set up flash attention if available
        attn_implementation = "flash_attention_2" if is_flash_attn_2_available() else None

        # Load model and processor
        model = ColQwen2_5.from_pretrained(
            self.model_name,
            torch_dtype=torch.bfloat16,
            device_map=self.device,
            attn_implementation=attn_implementation,
        ).eval()

        processor = ColQwen2_5_Processor.from_pretrained(self.model_name)

        return model, processor

    def create_text_representation(self, doc) -> str:
        """Create a textual representation of a document for embedding"""
        text_parts = []

        # Add document ID
        if hasattr(doc, 'doc_id') and doc.doc_id:
            text_parts.append(f"Document ID: {doc.doc_id}")

        # Add description (prioritized)
        if hasattr(doc, 'description') and doc.description:
            text_parts.append(f"Description: {doc.description}")

        # Add language
        if hasattr(doc, 'language') and doc.language and doc.language != "Unknown":
            text_parts.append(f"Language: {doc.language}")

        # Add date information
        if hasattr(doc, 'date') and doc.date:
            date_str = ""
            for k, v in doc.date.items():
                if v:
                    date_str += f"{k}: {v}, "
            date_str = date_str.rstrip(", ")

            if date_str:
                text_parts.append(f"Date: {date_str}")

        # Add transcription (truncated if very long)
        if hasattr(doc, 'transcriptions') and doc.transcriptions:
            combined_transcription = ""
            for transcription in doc.transcriptions:
                if hasattr(transcription, 'lines') and transcription.lines:
                    for line_num, line_text in sorted(transcription.lines.items()):
                        combined_transcription += f"{line_text} "
                elif isinstance(transcription, dict) and 'lines' in transcription:
                    for line_num, line_text in sorted(transcription['lines'].items()):
                        combined_transcription += f"{line_text} "

            # Truncate transcription if it's too long
            max_length = 1000
            if len(combined_transcription) > max_length:
                combined_transcription = combined_transcription[:max_length] + "..."

            if combined_transcription:
                text_parts.append(f"Transcription: {combined_transcription}")

        return "\n".join(text_parts)

    def get_embeddings(self, image, text: str, use_cache: bool = True) -> np.ndarray:
        """Get multimodal embedding for a document using both text and image if available"""
        # Generate identifier for caching
        doc_identifier = hashlib.md5(text.encode()).hexdigest()[:10]
        cache_path = self.get_cache_path(self.model_name, f"doc_{doc_identifier}")

        # Check cache first
        if use_cache and self.check_cache(cache_path):
            return self.load_from_cache(cache_path)

        # If no image, use text-only embedding
        if image is None or (isinstance(image, str) and "Invalid" in image):
            logger.info(f"Using text-only embedding for document {doc_identifier}")
            batch_queries = self.processor.process_queries([text]).to(self.device)
            with torch.no_grad():
                embeddings = self.model(**batch_queries)
                mean_embedding = torch.mean(embeddings, dim=1)
                embedding = mean_embedding.cpu().to(torch.float32).numpy()

            if use_cache:
                self.save_to_cache(cache_path, embedding)

            return embedding

        # Use multimodal embedding
        try:
            logger.info(f"Using multimodal embedding for document {doc_identifier}")
            # Process query (text) and image
            batch_queries = self.processor.process_queries([text]).to(self.device)
            batch_images = self.processor.process_images([image]).to(self.device)

            # Get embeddings
            with torch.no_grad():
                query_embeddings = self.model(**batch_queries)
                image_embeddings = self.model(**batch_images)

                # Combine text and image embeddings
                # Weight the text embedding higher (70%) as description is prioritized
                mean_query_embedding = torch.mean(query_embeddings, dim=1)
                mean_image_embedding = torch.mean(image_embeddings, dim=1)

                weighted_embedding = (0.7 * mean_query_embedding + 0.3 * mean_image_embedding)
                embedding = weighted_embedding.cpu().to(torch.float32).numpy()

            if use_cache:
                self.save_to_cache(cache_path, embedding)
            if self.image_only:
                logger.info(f"Using image-only embedding for document {doc_identifier}")
                return torch.mean(image_embeddings, dim=1).cpu().to(torch.float32).numpy()
            if self.text_only:
                return torch.mean(query_embeddings, dim=1).cpu().to(torch.float32).numpy()
            return embedding

        except Exception as e:
            logger.error(f"Error getting embedding for document {doc_identifier}: {e}")
            # Fallback to text-only
            logger.info(f"Falling back to text-only embedding for document {doc_identifier}")
            batch_queries = self.processor.process_queries([text]).to(self.device)
            with torch.no_grad():
                embeddings = self.model(**batch_queries)
                mean_embedding = torch.mean(embeddings, dim=1)
                embedding = mean_embedding.cpu().to(torch.float32).numpy()

            if use_cache:
                self.save_to_cache(cache_path, embedding)

            return embedding

    def get_embedding_multilingual(self, image, text, description_text, translation_text):
        """Get embeddings for image and multiple text types"""
        # Combine all text types with weights
        combined_text = ""
        if description_text:
            combined_text += f"Description: {description_text}\n"
        if text:
            combined_text += f"Text: {text}\n"
        if translation_text:
            combined_text += f"Translation: {translation_text}"

        return self.get_embeddings(image, combined_text)

    def get_embeddings_for_documents(self, docs: List, use_cache: bool = True) -> np.ndarray:
        """Get embeddings for a list of document objects"""
        all_embeddings = []

        for i, doc in enumerate(docs):
            doc_id = getattr(doc, 'doc_id', f"doc_{i}")
            logger.info(f"Processing document {i + 1}/{len(docs)} (ID: {doc_id})")

            text_representation = self.create_text_representation(doc)
            image = getattr(doc, 'image', None)

            embedding = self.get_embeddings(image, text_representation, use_cache)
            all_embeddings.append(embedding)

        return np.vstack(all_embeddings)


class CLIP(MultiModalEmbedding):
    def __init__(self, model_name="openai/clip-vit-base-patch32"):
        """
        Initialize CLIP model with the specified model name

        Args:
            model_name (str): Name of the CLIP model to use from Hugging Face
        """
        super().__init__()
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = CLIPModel.from_pretrained(model_name).to(self.device)
        self.processor = CLIPProcessor.from_pretrained(model_name)

    def get_embeddings(self, image, text: str) -> Dict:
        """
        Get embeddings for image and its associated text

        Args:
            image: PIL Image or path to image file
            text (str or List[str]): Text or list of texts associated with the image

        Returns:
            Dict containing image and text embeddings
        """
        # Handle image input (can be PIL image or path to image)
        if isinstance(image, str):
            image = Image.open(image)
        if len(text) > 77:
            logging.log(
                logging.WARNING,
                f"Text input is too long. Truncating to 77 characters: {text}")
            text = text[:77]
        # Handle text input (can be single string or list of strings)
        if isinstance(text, str):
            text = [text]
        print(len(text[0]))
        # Process inputs
        inputs = self.processor(
            text=text,
            images=image,
            return_tensors="pt",
            padding=True
        ).to(self.device)

        # Get embeddings
        with torch.no_grad():
            outputs = self.model(**inputs)

        # Extract and normalize embeddings
        image_embeds = outputs.image_embeds.cpu().numpy()
        text_embeds = outputs.text_embeds.cpu().numpy()

        return {
            "image_embeddings": image_embeds,
            "text_embeddings": text_embeds
        }

    def get_embedding_multilingual(self, image, text, description_text, translation_text):
        """
        Get embeddings for image and multiple text types (original, description, translation)

        Args:
            image: PIL Image or path to image file
            text (str): Primary text associated with the image
            description_text (str): Descriptive text about the image
            translation_text (str): Translated text

        Returns:
            Dict containing image and various text embeddings
        """
        # Handle image input
        if isinstance(image, str):
            image = Image.open(image)

        # Get embeddings for primary text
        primary_result = self.get_embeddings(image, text)

        # Get embeddings for description text
        description_result = self.get_embeddings(image, description_text)

        # Get embeddings for translation text
        translation_result = self.get_embeddings(image, translation_text)

        return {
            "image_embeddings": primary_result["image_embeddings"],
            "text_embeddings": primary_result["text_embeddings"],
            "description_embeddings": description_result["text_embeddings"],
            "translation_embeddings": translation_result["text_embeddings"]
        }

    def get_similarity(self, image_embedding, text_embedding):
        """
        Calculate cosine similarity between image and text embeddings

        Args:
            image_embedding: Image embedding vector
            text_embedding: Text embedding vector

        Returns:
            Cosine similarity score
        """
        # Convert to tensors if they're numpy arrays
        if isinstance(image_embedding, np.ndarray):
            image_embedding = torch.from_numpy(image_embedding)
        if isinstance(text_embedding, np.ndarray):
            text_embedding = torch.from_numpy(text_embedding)

        # Ensure we have the right shape
        if image_embedding.dim() == 2 and image_embedding.size(0) == 1:
            image_embedding = image_embedding.squeeze(0)
        if text_embedding.dim() == 2 and text_embedding.size(0) == 1:
            text_embedding = text_embedding.squeeze(0)

        # Compute cosine similarity
        similarity = torch.nn.functional.cosine_similarity(
            image_embedding, text_embedding, dim=0
        )

        return similarity.item()
