"""Language detection and extension mappings for code chunking.

Supports 29+ programming languages via Tree-sitter.
"""

from pathlib import Path


# Language to file extension mapping
LANGUAGE_EXTENSIONS: dict[str, list[str]] = {
    "python": [".py", ".pyi", ".pyx"],
    "javascript": [".js", ".mjs", ".cjs"],
    "typescript": [".ts", ".mts", ".cts"],
    "tsx": [".tsx"],
    "jsx": [".jsx"],
    "rust": [".rs"],
    "go": [".go"],
    "java": [".java"],
    "kotlin": [".kt", ".kts"],
    "c": [".c", ".h"],
    "cpp": [".cpp", ".cc", ".cxx", ".hpp", ".hxx", ".h"],
    "csharp": [".cs"],
    "swift": [".swift"],
    "ruby": [".rb"],
    "php": [".php"],
    "scala": [".scala"],
    "haskell": [".hs", ".lhs"],
    "ocaml": [".ml", ".mli"],
    "lua": [".lua"],
    "bash": [".sh", ".bash"],
    "yaml": [".yaml", ".yml"],
    "json": [".json"],
    "toml": [".toml"],
    "markdown": [".md", ".markdown"],
    "html": [".html", ".htm"],
    "css": [".css"],
    "sql": [".sql"],
    "dockerfile": ["Dockerfile"],
}

# Reverse mapping: extension to language
EXTENSION_TO_LANGUAGE: dict[str, str] = {}
for lang, exts in LANGUAGE_EXTENSIONS.items():
    for ext in exts:
        EXTENSION_TO_LANGUAGE[ext] = lang


def detect_language(file_path: str) -> str | None:
    """Detect programming language from file extension.

    Args:
        file_path: Path to the source file

    Returns:
        Language name (e.g., 'python', 'typescript') or None if unknown
    """
    path = Path(file_path)

    # Check exact filename matches (e.g., Dockerfile)
    if path.name in EXTENSION_TO_LANGUAGE:
        return EXTENSION_TO_LANGUAGE[path.name]

    # Check extension
    suffix = path.suffix.lower()
    return EXTENSION_TO_LANGUAGE.get(suffix)


def get_supported_languages() -> list[str]:
    """Get list of all supported language names."""
    return list(LANGUAGE_EXTENSIONS.keys())


def get_extensions_for_language(language: str) -> list[str]:
    """Get file extensions for a language.

    Args:
        language: Language name (e.g., 'python')

    Returns:
        List of file extensions (e.g., ['.py', '.pyi', '.pyx'])
    """
    return LANGUAGE_EXTENSIONS.get(language, [])
