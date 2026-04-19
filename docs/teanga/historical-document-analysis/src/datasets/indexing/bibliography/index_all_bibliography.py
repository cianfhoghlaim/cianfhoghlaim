import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
import dotenv
dotenv.load_dotenv()

from src.datasets.indexing.bibliography.index_bibliography import (
    index_bibliography_to_elasticsearch,
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    force=True
)
logger = logging.getLogger(__name__)


def find_metadata_files(root_dir: str) -> List[Path]:
    """Find all metadata JSON files in the directory tree.

    Looks for files matching patterns: *_metadata.json, *_meta.json, meta.json

    :param root_dir: Root directory to search in.
    :type root_dir: str
    :return: List of paths to metadata files.
    :rtype: List[Path]
    """
    root = Path(root_dir)
    metadata_files: List[Path] = []
    
    # Patterns to match metadata files
    patterns = ["*_metadata.json", "*_meta.json", "meta.json"]
    
    for pattern in patterns:
        metadata_files.extend(root.rglob(pattern))
    
    # Deduplicate while preserving order
    seen: set[str] = set()
    unique: List[Path] = []
    for p in metadata_files:
        p_str = str(p)
        if p_str not in seen:
            seen.add(p_str)
            unique.append(p)
    
    logger.info(f"Found {len(unique)} metadata files in {root_dir}")
    return unique


def find_structured_directories(
    metadata_file: Path,
    suffix: str = "*_gemini_gemini_2.5_flash"
) -> List[Path]:
    """Find structured directories matching the suffix pattern.

    Searches recursively in the parent directory of the metadata file and its subdirectories.

    :param metadata_file: Path to the metadata file.
    :type metadata_file: Path
    :param suffix: Suffix pattern to match (e.g., "*_gemini_gemini_2.5_flash").
                   Defaults to "*_gemini_gemini_2.5_flash".
    :type suffix: str
    :return: List of paths to structured directories.
    :rtype: List[Path]
    """
    # Remove the leading * from suffix to get the actual suffix
    # Handle both "*_suffix" and "_suffix" formats
    actual_suffix = suffix.lstrip("*")
    
    # Search recursively in the parent directory of the metadata file
    search_root = metadata_file.parent
    
    if not search_root.exists() or not search_root.is_dir():
        return []
    
    structured_dirs: List[Path] = []
    
    # Search recursively for directories ending with the suffix
    for dir_path in search_root.rglob("*"):
        if dir_path.is_dir() and dir_path.name.endswith(actual_suffix):
            # Verify it's actually a structured directory by checking for JSON files
            json_files = list(dir_path.glob("*_structured.json")) + list(dir_path.glob("page_*_structured.json"))
            if json_files:
                structured_dirs.append(dir_path)
    
    logger.debug(f"Found {len(structured_dirs)} structured directories for {metadata_file}")
    return structured_dirs


def find_image_directory(structured_dir: Path) -> Optional[Path]:
    """Find the corresponding image directory for a structured directory.

    Looks for directories named with *_images pattern in the same parent directory
    or in the structured directory's parent's subdirectories.

    :param structured_dir: Path to the structured directory.
    :type structured_dir: Path
    :return: Path to image directory if found, None otherwise.
    :rtype: Optional[Path]
    """
    parent = structured_dir.parent
    
    # Try to infer image directory name from structured directory name
    # e.g., "cairo_to_manchester_1_structured_gemini_gemini_2.5_flash" -> "cairo_to_manchester_1_images"
    base_name = structured_dir.name
    
    # Remove common structured suffixes to get base name
    suffixes_to_remove = [
        "_structured_gemini_gemini_2.5_flash",
        "_structured_gemini_gemini_1.5_flash",
        "_structured_ollama_gemma3_27b",
        "_structured",
    ]
    
    possible_bases = []
    for suffix in suffixes_to_remove:
        if base_name.endswith(suffix):
            possible_bases.append(base_name[:-len(suffix)])
    
    # Also try parent directory name
    possible_bases.append(parent.name)
    
    # Look for image directories in parent directory
    for base in possible_bases:
        if not base:
            continue
        
        # Try various image directory naming patterns
        image_dir = parent / f"{base}_images"
        if image_dir.exists() and image_dir.is_dir():
            # Check if it contains image files
            image_extensions = [".jpg", ".jpeg", ".png"]
            has_images = any(
                list(image_dir.glob(f"*{ext}")) for ext in image_extensions
            )
            if has_images:
                return image_dir
    
    # Fallback: search for any *_images directory in parent
    for image_dir in parent.glob("*_images"):
        if image_dir.is_dir():
            image_extensions = [".jpg", ".jpeg", ".png"]
            has_images = any(
                list(image_dir.glob(f"*{ext}")) for ext in image_extensions
            )
            if has_images:
                return image_dir
    
    # Also check if there's an images directory in the same directory as structured
    images_dir = parent / "images"
    if images_dir.exists() and images_dir.is_dir():
        image_extensions = [".jpg", ".jpeg", ".png"]
        has_images = any(
            list(images_dir.glob(f"*{ext}")) for ext in image_extensions
        )
        if has_images:
            return images_dir
    
    return None


def discover_indexing_tasks(
    root_dir: str,
    suffix: str = "*_gemini_gemini_2.5_flash"
) -> List[Dict[str, Any]]:
    """Discover all indexing tasks by finding metadata files and matching structured directories.

    :param root_dir: Root directory to search in.
    :type root_dir: str
    :param suffix: Suffix pattern for structured directories.
                   Defaults to "*_gemini_gemini_2.5_flash".
    :type suffix: str
    :return: List of dictionaries containing indexing task information.
             Each dict has keys: metadata_file, structured_dir, image_dir.
    :rtype: List[Dict[str, Any]]

    Example::

        tasks = discover_indexing_tasks(
            root_dir="/path/to/academic_literature",
            suffix="*_gemini_gemini_2.5_flash"
        )
        # Returns: [
        #     {
        #         "metadata_file": Path("/path/to/friedman_metadata.json"),
        #         "structured_dir": Path("/path/to/friedman_108_201_vol_1_structured_gemini_gemini_2.5_flash"),
        #         "image_dir": Path("/path/to/friedman_108_201_vol_1_images")
        #     },
        #     ...
        # ]
    """
    metadata_files = find_metadata_files(root_dir=root_dir)
    tasks: List[Dict[str, Any]] = []
    
    for metadata_file in metadata_files:
        structured_dirs = find_structured_directories(
            metadata_file=metadata_file,
            suffix=suffix
        )
        
        if not structured_dirs:
            logger.warning(
                f"No structured directories found for metadata file: {metadata_file}"
            )
            continue
        
        for structured_dir in structured_dirs:
            image_dir = find_image_directory(structured_dir=structured_dir)
            
            task = {
                "metadata_file": metadata_file,
                "structured_dir": structured_dir,
                "image_dir": image_dir,
            }
            tasks.append(task)
            
            logger.info(
                f"Discovered task: metadata={metadata_file.name}, "
                f"structured={structured_dir.name}, "
                f"images={'found' if image_dir else 'not found'}"
            )
    
    return tasks


def index_all_bibliography(
    root_dir: str,
    index_name: str = "genizah_bibliography_v1.0.0",
    embedding_mode: str = "hybrid",
    suffix: str = "*_gemini_gemini_2.5_flash",
    dry_run: bool = False,
) -> None:
    """Index all bibliography entries found in the directory tree.

    Automatically discovers metadata files and matching structured directories,
    then indexes each one using the index_bibliography_to_elasticsearch function.

    :param root_dir: Root directory containing academic literature data.
    :type root_dir: str
    :param index_name: Name of the Elasticsearch index to write to.
                       Defaults to "genizah_bibliography_v1.0.0".
    :type index_name: str
    :param embedding_mode: Embedding mode to use. Options: "text_only", "image_only", or "hybrid".
                           Defaults to "hybrid".
    :type embedding_mode: str
    :param suffix: Suffix pattern for structured directories.
                   Defaults to "*_gemini_gemini_2.5_flash".
    :type suffix: str
    :param dry_run: If True, only discover and log tasks without indexing.
                    Defaults to False.
    :type dry_run: bool
    :return: None
    :rtype: None

    Example::

        index_all_bibliography(
            root_dir="/Users/isaac1/.../academic_literature",
            index_name="genizah_bibliography_v1.0.0",
            embedding_mode="hybrid",
            suffix="*_gemini_gemini_2.5_flash",
            dry_run=False,
        )
    """
    logger.info(f"Starting automatic bibliography indexing in {root_dir}")
    logger.info(f"Searching for structured directories with suffix: {suffix}")
    logger.info(f"Embedding mode: {embedding_mode}")
    logger.info(f"Index name: {index_name}")
    
    tasks = discover_indexing_tasks(root_dir=root_dir, suffix=suffix)
    
    if not tasks:
        logger.warning("No indexing tasks discovered. Nothing to index.")
        return
    
    logger.info(f"Discovered {len(tasks)} indexing tasks")
    
    if dry_run:
        logger.info("DRY RUN MODE: Would index the following tasks:")
        for i, task in enumerate(tasks, 1):
            logger.info(
                f"  {i}. {task['metadata_file'].name} -> "
                f"{task['structured_dir'].name} "
                f"(images: {'yes' if task['image_dir'] else 'no'})"
            )
        return
    
    # Process each task
    successful = 0
    failed = 0
    
    for i, task in enumerate(tasks, 1):
        logger.info(
            f"\n{'='*80}\n"
            f"Processing task {i}/{len(tasks)}\n"
            f"Metadata: {task['metadata_file']}\n"
            f"Structured: {task['structured_dir']}\n"
            f"Images: {task['image_dir'] if task['image_dir'] else 'None'}\n"
            f"{'='*80}"
        )
        
        try:
            index_bibliography_to_elasticsearch(
                root_dir=str(task['structured_dir']),
                metadata_file=str(task['metadata_file']),
                index_name=index_name,
                embedding_mode=embedding_mode,
                image_dir=str(task['image_dir']) if task['image_dir'] else None,
            )
            successful += 1
            logger.info(f"Successfully indexed task {i}/{len(tasks)}")
        except Exception as e:
            failed += 1
            logger.error(
                f"Failed to index task {i}/{len(tasks)}: {type(e).__name__}: {e}",
                exc_info=True
            )
            # Continue with next task
            continue
    
    logger.info(
        f"\n{'='*80}\n"
        f"Indexing complete!\n"
        f"Successful: {successful}/{len(tasks)}\n"
        f"Failed: {failed}/{len(tasks)}\n"
        f"{'='*80}"
    )


def main() -> None:
    """CLI entrypoint for indexing all bibliography pages.

    Environment variables required:
    - ``ELASTIC_SEARCH_HOST``
    - ``ELASTIC_USER``
    - ``ELASTIC_PASSWORD``

    Example::

        python -m src.datasets.cairo_genizah.indexing.biblio.index_all_bibliography \
            --root /Users/isaac1/.../academic_literature \
            --index genizah_bibliography_v1.0.0 \
            --suffix "*_gemini_gemini_2.5_flash" \
            --mode hybrid \
            --dry-run
    """

    index_all_bibliography(
        root_dir="/Users/isaac/Documents/GitHub/historical-document-analysis/src/datasets/raw_data/cairo_genizah/academic_literature",
        index_name="bibliography_text_only_0.4",
        embedding_mode="text_only",
        suffix= "_gemini_gemini_2.5_flash",
        dry_run=False,
    )


if __name__ == "__main__":
    main()

