"""
Local file source constants.

Paths and configuration for local document processing.
"""

from pathlib import Path

# Base path for local document storage
BUNCHLOCH_PATH = Path.home() / "dev" / "cianfhoghlaim" / "taighde_scoil"

# Hash database for tracking processed files
LOCAL_HASH_DB_PATH = Path.home() / ".cache" / "oideachais" / "file_hashes.db"

# Extraction configuration
EXTRACTION_CONFIG = {
    "pdf": {
        "ocr_enabled": True,
        "ocr_languages": ["ga", "en"],
        "extract_images": True,
        "extract_tables": True,
        "max_pages": 100,  # Maximum pages to extract
    },
    "docx": {
        "extract_images": True,
        "extract_tables": True,
    },
    "pptx": {
        "extract_images": True,
        "extract_notes": True,
    },
    "xlsx": {
        "all_sheets": True,
        "include_formulas": False,
    },
}

# File type extensions
FILE_TYPE_EXTENSIONS = {
    "pdf": [".pdf"],
    "word": [".doc", ".docx"],
    "excel": [".xls", ".xlsx", ".xlsm"],
    "powerpoint": [".ppt", ".pptx"],
    "text": [".txt", ".md", ".rst"],
    "code": [".py", ".ipynb", ".js", ".ts", ".sql", ".r", ".R"],
    "image": [".png", ".jpg", ".jpeg", ".gif", ".tiff", ".bmp"],
    "audio": [".mp3", ".wav", ".flac", ".m4a", ".ogg"],
    "video": [".mp4", ".mov", ".avi", ".mkv", ".webm"],
}

# Subject-specific paths
LOCAL_SUBJECT_PATHS = {
    "gaeilge": BUNCHLOCH_PATH / "gaeilge",
    "matamaitic": BUNCHLOCH_PATH / "matamaitic",
    "bearla": BUNCHLOCH_PATH / "bearla",
    "stair": BUNCHLOCH_PATH / "stair",
    "tireolaiocht": BUNCHLOCH_PATH / "tireolaiocht",
    "eolaiocht": BUNCHLOCH_PATH / "eolaiocht",
}


def detect_language(text: str) -> str:
    """
    Detect language of text (Irish or English).

    Args:
        text: Input text

    Returns:
        Language code ('ga' for Irish, 'en' for English)
    """
    # Simple heuristic: check for common Irish words/patterns
    irish_markers = [
        "agus", "an", "na", "le", "ar", "ach", "go", "is",
        "á", "é", "í", "ó", "ú", "bhí", "atá", "seo", "sin",
    ]

    text_lower = text.lower()
    irish_count = sum(1 for marker in irish_markers if marker in text_lower)

    # If enough Irish markers found, classify as Irish
    return "ga" if irish_count >= 3 else "en"


def detect_subject_from_path(path: Path) -> str:
    """
    Detect subject from file path.

    Args:
        path: File path

    Returns:
        Subject name or 'unknown'
    """
    path_str = str(path).lower()

    subject_keywords = {
        "gaeilge": ["gaeilge", "irish", "teanga"],
        "matamaitic": ["matamaitic", "mathematics", "maths", "math"],
        "bearla": ["bearla", "english"],
        "stair": ["stair", "history"],
        "tireolaiocht": ["tireolaiocht", "geography"],
        "eolaiocht": ["eolaiocht", "science", "biology", "chemistry", "physics"],
    }

    for subject, keywords in subject_keywords.items():
        if any(kw in path_str for kw in keywords):
            return subject

    return "unknown"


def extract_course_code(path: Path) -> str | None:
    """
    Extract course code from file path or name.

    Args:
        path: File path

    Returns:
        Course code or None
    """
    import re

    # Common patterns for course codes
    patterns = [
        r"LC[0-9]{4}",  # Leaving Certificate
        r"JC[0-9]{4}",  # Junior Cycle
        r"[A-Z]{2,4}[0-9]{2,4}",  # Generic code
    ]

    path_str = str(path)

    for pattern in patterns:
        match = re.search(pattern, path_str)
        if match:
            return match.group()

    return None


def get_document_metadata(path: Path) -> dict:
    """
    Extract metadata from document file.

    Args:
        path: Path to document

    Returns:
        Metadata dictionary
    """

    stat = path.stat()

    return {
        "filename": path.name,
        "extension": path.suffix.lower(),
        "size_bytes": stat.st_size,
        "modified_time": stat.st_mtime,
        "created_time": stat.st_ctime,
        "subject": detect_subject_from_path(path),
        "course_code": extract_course_code(path),
    }


def get_file_type(path: Path) -> str:
    """
    Get file type category from path.

    Args:
        path: File path

    Returns:
        File type category (pdf, word, excel, etc.)
    """
    ext = path.suffix.lower()

    for file_type, extensions in FILE_TYPE_EXTENSIONS.items():
        if ext in extensions:
            return file_type

    return "unknown"


def should_process_file(path: Path, processed_hashes: set | None = None) -> bool:
    """
    Check if file should be processed.

    Args:
        path: File path
        processed_hashes: Set of already processed file hashes

    Returns:
        True if file should be processed
    """
    import hashlib

    # Skip hidden files
    if path.name.startswith("."):
        return False

    # Skip non-files
    if not path.is_file():
        return False

    # Skip files with unknown type
    if get_file_type(path) == "unknown":
        return False

    # Skip already processed files
    if processed_hashes is not None:
        file_hash = hashlib.md5(path.read_bytes()).hexdigest()
        if file_hash in processed_hashes:
            return False

    return True
