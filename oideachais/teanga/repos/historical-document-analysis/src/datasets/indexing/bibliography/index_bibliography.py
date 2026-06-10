import os
import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Literal
import dotenv
from src.datasets.document_models.bibliography_document import BibliographyDocument
from PIL import Image
from src.embeddings.embedding_models import NomicsEmbedding
from src.datasets.indexing.elastic_index_genizah import (
    ElasticsearchGenizahProcessor,
)

dotenv.load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', force=True)
logger = logging.getLogger(__name__)

def find_structured_pages(root_dir: str) -> List[Path]:
    """Recursively discover structured page JSON files under the root directory.

    :param root_dir: Root directory where academic literature data resides.
    :type root_dir: str
    :return: List of JSON file paths.
    :rtype: List[Path]

    Example::

        files = find_structured_pages(
            root_dir="/.../raw_data/cairo_genizah/academic_literature"
        )
    """
    root = Path(root_dir)
    patterns = ["*_structured.json", "page_*_structured.json"]
    results: List[Path] = []
    for pattern in patterns:
        results.extend(root.rglob(pattern))
    # Deduplicate while preserving order
    seen: set[str] = set()
    unique: List[Path] = []
    for p in results:
        p_str = str(p)
        if p_str not in seen:
            seen.add(p_str)
            unique.append(p)
    return unique


def load_book_metadata(metadata_file: str) -> Dict[str, Any]:
    """Load book metadata from a JSON file.

    :param metadata_file: Path to the metadata JSON file.
    :type metadata_file: str
    :return: Dictionary containing book metadata.
    :rtype: Dict[str, Any]

    Example::

        metadata = load_book_metadata(
            metadata_file="/path/to/cairo_to_manchester_metadata.json"
        )
    """
    metadata_path = Path(metadata_file)
    if not metadata_path.exists():
        raise FileNotFoundError(
            f"Metadata file not found: {metadata_file}. "
            f"Please provide a valid metadata JSON file."
        )

    with open(metadata_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    logger.info(f"Loaded book metadata from {metadata_file}")
    return metadata


def extract_page_number_from_filename(filename: str) -> Optional[int]:
    """Extract page number from structured JSON filename like 'page_001_structured.json'.

    :param filename: Filename to extract page number from.
    :type filename: str
    :return: Page number as integer if found, None otherwise.
    :rtype: Optional[int]

    Example::

        page_num = extract_page_number_from_filename("page_001_structured.json")
        # Returns: 1
    """
    # Match patterns like "page_001" or "page_1" in filename
    match = re.search(r'page[_-](\d+)', filename, re.IGNORECASE)
    if match:
        try:
            return int(match.group(1))
        except ValueError:
            return None
    return None


def load_image_for_document(doc: BibliographyDocument, image_dir: Optional[Path], structured_json_path: Optional[Path] = None) -> Optional[Image.Image]:
    """Load image for a bibliography document from the image directory.

    Attempts to find an image file matching the document's structured JSON filename pattern,
    doc_id, or page number. Supports common image formats: jpg, jpeg, png.

    If structured_json_path is provided, it will extract the page number from the filename
    (e.g., "page_001_structured.json" -> "page_001.png") and try that pattern first.
    This is useful when images are numbered to match structured JSON filenames.

    :param doc: Bibliography document to load image for.
    :type doc: BibliographyDocument
    :param image_dir: Optional directory containing images. If None, returns None.
    :type image_dir: Optional[Path]
    :param structured_json_path: Optional path to the structured JSON file. If provided,
                                 extracts page number from filename (e.g., "page_001_structured.json").
    :type structured_json_path: Optional[Path]
    :return: PIL Image if found, None otherwise.
    :rtype: Optional[Image.Image]

    Example::

        image = load_image_for_document(
            doc=my_doc,
            image_dir=Path("/path/to/images"),
            structured_json_path=Path("/path/to/page_001_structured.json")
        )
    """
    if image_dir is None or not image_dir.exists():
        return None

    # Try multiple naming patterns
    image_extensions = [".jpg", ".jpeg", ".png"]
    search_patterns = []

    # If structured_json_path is provided, extract page number from filename first
    if structured_json_path is not None:
        page_num_from_file = extract_page_number_from_filename(structured_json_path.name)
        if page_num_from_file is not None:
            # Try both zero-padded and non-padded versions
            search_patterns.append(f"page_{page_num_from_file:03d}")
            search_patterns.append(f"page_{page_num_from_file}")

    # Then try patterns based on document properties
    search_patterns.extend([
        doc.doc_id,  # e.g., "cairo_to_manchester_1_p058"
        f"{doc.pdf_name}_p{doc.page_number:03d}",  # e.g., "cairo_to_manchester_1_p058"
        f"{doc.pdf_name}_p{doc.page_number}",  # e.g., "cairo_to_manchester_1_p58"
        f"page_{doc.page_number:03d}",  # e.g., "page_058"
        f"page_{doc.page_number}",  # e.g., "page_58"
    ])

    for pattern in search_patterns:
        for ext in image_extensions:
            image_path = image_dir / f"{pattern}{ext}"
            if image_path.exists():
                try:
                    image = Image.open(image_path).convert("RGB")
                    logger.debug(f"Loaded image for {doc.doc_id} from {image_path}")
                    return image
                except Exception as e:
                    logger.warning(f"Failed to load image {image_path}: {e}")
                    continue

    logger.debug(f"No image found for {doc.doc_id} in {image_dir}")
    return None


def index_bibliography_to_elasticsearch(
        root_dir: str,
        metadata_file: str,
        index_name: str = "genizah_bibliography_v1.0.0",
        embedding_mode: Literal["text_only", "image_only", "hybrid"] = "hybrid",
        image_dir: Optional[str] = None,
) -> None:
    """Index academic literature structured pages into Elasticsearch using Nomic embeddings.

    :param root_dir: Directory containing the structured page JSON files (recursive).
    :type root_dir: str
    :param metadata_file: Path to the book metadata JSON file (e.g., cairo_to_manchester_metadata.json).
                          Must contain author, title, and optionally ISBN and subjects.
    :type metadata_file: str
    :param index_name: Name of the Elasticsearch index to write to.
    :type index_name: str
    :param embedding_mode: Embedding mode to use. Options: "text_only" (text embeddings only),
                           "image_only" (image embeddings only), or "hybrid" (combined text and image).
                           Defaults to "hybrid".
    :type embedding_mode: Literal["text_only", "image_only", "hybrid"]
    :param image_dir: Optional directory containing images for the bibliography pages.
                      Images should be named to match document IDs or page numbers.
                      If None, images will not be loaded.
    :type image_dir: Optional[str]
    :return: None
    :rtype: None

    Example::

        index_bibliography_to_elasticsearch(
            root_dir="/Users/isaac1/.../academic_literature/cairo_to_manchester_1_structured",
            metadata_file="/Users/isaac1/.../cairo_to_manchester_metadata.json",
            index_name="genizah_bibliography_v1.0.0",
            embedding_mode="hybrid",
            image_dir="/Users/isaac1/.../academic_literature/cairo_to_manchester_1/images",
        )
    """
    # Initialize embedding model with appropriate mode
    text_only = embedding_mode == "text_only"
    image_only = embedding_mode == "image_only"

    logger.info(f"Initializing embeddings model for bibliography indexing with mode: {embedding_mode}...")
    embeddings_model = NomicsEmbedding(text_only=text_only, image_only=image_only)

    elastic_config: Dict[str, Any] = {
        "hosts": [
            {
                "host": os.environ["ELASTIC_SEARCH_HOST"],
                "port": 443,
                "scheme": "https",
            }
        ],
        "basic_auth": (
            os.environ["ELASTIC_USER"],
            os.environ["ELASTIC_PASSWORD"],
        ),
    }

    # Determine embedding dims from the model with a short probe to align index mapping
    try:
        probe_vec = embeddings_model.get_embeddings(image=None, text="probe text for embedding dims")
        embedding_dims = int(probe_vec.shape[-1])
    except Exception as e:
        logger.warning(f"Failed to probe embedding dims: {e}. Falling back to 128.")
        embedding_dims = 128

    logger.info("Initializing Elasticsearch processor for bibliography index...")
    processor = ElasticsearchGenizahProcessor(
        embedding_model=embeddings_model,
        elasticsearch_config=elastic_config,
        index_name=index_name,
        embedding_dims=embedding_dims,
    )

    # Load book metadata
    logger.info(f"Loading book metadata from {metadata_file}...")
    book_metadata = load_book_metadata(metadata_file=metadata_file)

    # Prepare image directory if provided
    image_dir_path: Optional[Path] = None
    if image_dir:
        image_dir_path = Path(image_dir)
        if not image_dir_path.exists():
            logger.warning(f"Image directory does not exist: {image_dir}. Images will not be loaded.")
            image_dir_path = None
        else:
            logger.info(f"Using image directory: {image_dir}")

    files = find_structured_pages(root_dir=root_dir)
    logger.info(f"Discovered {len(files)} structured page files under {root_dir}")

    documents: List[BibliographyDocument] = []
    images_loaded_count = 0
    images_missing_count = 0

    # Process files and match images based on structured JSON filename
    for fp in files:
        try:
            doc = BibliographyDocument.from_structured_json(
                json_path=fp,
                book_metadata=book_metadata
            )
            # shelf_mark is already set from shelf_marks_mentioned (or NO_SHELF_MARK if empty)
            # Do NOT override it with pdf_name

            # Load image if image directory is provided and mode requires images
            # Pass the structured JSON file path to extract page number from filename
            # (e.g., "page_001_structured.json" -> "page_001.png")
            if image_dir_path and (embedding_mode == "image_only" or embedding_mode == "hybrid"):
                image = load_image_for_document(
                    doc=doc,
                    image_dir=image_dir_path,
                    structured_json_path=fp
                )
                if image is not None:
                    doc.image = image
                    images_loaded_count += 1
                    logger.debug(f"Loaded image for document {doc.doc_id}")
                else:
                    images_missing_count += 1
                    if embedding_mode == "image_only":
                        logger.warning \
                            (f"No image found for document {doc.doc_id} in image_only mode. Will fall back to text-only embedding.")
                    else:
                        logger.debug(f"No image found for document {doc.doc_id}")

            documents.append(doc)
        except Exception as e:
            import traceback
            logger.error(f"Failed to parse {fp}: {type(e).__name__}: {e}")
            logger.debug(f"Traceback for {fp}:\n{traceback.format_exc()}")
            # Try to log what data we could extract before the error
            try:
                with open(fp, "r") as f:
                    partial_data = json.load(f)
                    logger.debug(f"JSON keys in file: {list(partial_data.keys())}")
                    logger.debug(f"extracted_page_number: {partial_data.get('extracted_page_number')}")
                    logger.debug(f"metadata keys: {list(partial_data.get('metadata', {}).keys())}")
            except Exception:
                logger.debug(f"Could not read JSON file for debugging")

    if not documents:
        logger.warning("No documents parsed. Nothing to index.")
        return

    # Log image loading statistics
    if image_dir_path and (embedding_mode == "image_only" or embedding_mode == "hybrid"):
        logger.info \
            (f"Image loading summary: {images_loaded_count} loaded, {images_missing_count} missing out of {len(documents)} documents")
        if embedding_mode == "image_only" and images_missing_count > 0:
            logger.warning \
                (f"Warning: {images_missing_count} documents missing images in image_only mode. These will use text-only embeddings as fallback.")

    logger.info(f"Indexing {len(documents)} bibliography documents...")
    processor.process_documents(documents=documents, batch_size=10)


def main() -> None:
    """CLI entrypoint for indexing bibliography pages.

    Environment variables required:
    - ``ELASTIC_SEARCH_HOST``
    - ``ELASTIC_USER``
    - ``ELASTIC_PASSWORD``

    Example::

        python -m src.datasets.cairo_genizah.indexing.biblio.index_bibliography \
            --root \
            /Users/isaac1/Documents/GitHub/multimodal-document-analysis/src/datasets/raw_data/cairo_genizah/academic_literature \
            --index genizah_bibliography_v1.0.0
    """
    import argparse

    default_root = (
        "/Users/isaac1/Documents/GitHub/multimodal-document-analysis/"
        "src/datasets/raw_data/cairo_genizah/academic_literature"
    )


    # parser.add_argument("--root", type=str, default=default_root, help="Root directory containing structured JSON pages")
    # parser.add_argument("--index", type=str, default="genizah_bibliography_v1.0.0", help="Elasticsearch index name")

    #index_bibliography_to_elasticsearch(root_dir="/Users/isaac1/Documents/GitHub/multimodal-document-analysis/src/datasets/raw_data/cairo_genizah/academic_literature/cairo_to_manchester/cairo_to_manchester_1/cairo_to_manchester_1_structured", index_name="genizah_bibliography_v0.0.1")
    # index_bibliography_to_elasticsearch(
       # root_dir="/Users/isaac1/Documents/GitHub/multimodal-document-analysis/src/datasets/raw_data/cairo_genizah/academic_literature/kettubah_palestine/friedman_108_201_vol_1/friedman_108_201_vol_1_structured_gemini_gemini_2.5_flash",
        # metadata_file="/Users/isaac1/Documents/GitHub/multimodal-document-analysis/src/datasets/raw_data/cairo_genizah/academic_literature/kettubah_palestine/friedman_meta.json",
        #index_name="genizah_bibliography_v0.0.1")

    #index_bibliography_to_elasticsearch(
        #root_dir="/Users/isaac1/Documents/GitHub/multimodal-document-analysis/src/datasets/raw_data/cairo_genizah/academic_literature/rylands_articles/bjrl-article-p710/bjrl-article-p710_structured_gemini_gemini_2.5_flash",
        #metadata_file="/Users/isaac1/Documents/GitHub/multimodal-document-analysis/src/datasets/raw_data/cairo_genizah/academic_literature/rylands_articles/bjrl-article-p710.json",
        #ndex_name="genizah_bibliography_v0.0.1",
    #)
    # index_bibliography_to_elasticsearch(
        # root_dir="/Users/isaac1/Documents/GitHub/multimodal-document-analysis/src/datasets/raw_data/cairo_genizah/academic_literature/thesis_bible/ej_arrant/ej_arrant_structured_gemini_gemini_2.5_flash",
        #metadata_file="/Users/isaac1/Documents/GitHub/multimodal-document-analysis/src/datasets/raw_data/cairo_genizah/academic_literature/thesis_bible/meta.json",
        #index_name="genizah_bibliography_v0.0.1"
    #)
    # index_bibliography_to_elasticsearch(
        # root_dir="/Users/isaac1/Documents/GitHub/multimodal-document-analysis/src/datasets/raw_data/cairo_genizah/academic_literature/rylands_articles/bjrl-article-p488/bjrl-article-p488_structured_gemini_gemini_2.5_flash",
        # metadata_file="/Users/isaac1/Documents/GitHub/multimodal-document-analysis/src/datasets/raw_data/cairo_genizah/academic_literature/rylands_articles/bjrl-article-p488_meta.json",
        # index_name="genizah_bibliography_v0.0.0_image_only",
        # image_dir="/Users/isaac1/Documents/GitHub/multimodal-document-analysis/src/datasets/raw_data/cairo_genizah/academic_literature/rylands_articles/bjrl-article-p488/bjrl-article-p488_images",
        #embedding_mode="image_only",
    #)
    """
    index_bibliography_to_elasticsearch(
        root_dir="/Users/isaac1/Documents/GitHub/multimodal-document-analysis/src/datasets/raw_data/cairo_genizah/academic_literature/penn_articles/oldest_dated/oldest_dated_structured_gemini_gemini_2.5_flash",
        metadata_file="/Users/isaac1/Documents/GitHub/multimodal-document-analysis/src/datasets/raw_data/cairo_genizah/academic_literature/penn_articles/oldest_dated_metadata.json",
        index_name="bibliography_0.0.2",
        embedding_mode="text_only",

    )
    """
    index_bibliography_to_elasticsearch(
        root_dir="/Users/isaac1/Documents/GitHub/multimodal-document-analysis/src/datasets/raw_data/cairo_genizah/academic_literature/mcgill/mcgill_frag/mcgill_frag_structured_gemini_gemini_2.5_flash",
        metadata_file="/Users/isaac1/Documents/GitHub/multimodal-document-analysis/src/datasets/raw_data/cairo_genizah/academic_literature/mcgill/mcgill_frag/mcgill_frag_enhanced.json",
        index_name="bibliography_0.0.2",
        embedding_mode="text_only",

    )
if __name__ == "__main__":
    main()


#/Users/isaac1/Documents/GitHub/multimodal-document-analysis/src/datasets/raw_data/cairo_genizah/academic_literature/india_traders/india_trader_metada.json