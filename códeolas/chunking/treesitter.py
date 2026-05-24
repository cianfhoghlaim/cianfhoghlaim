"""
TreeSitter-based code chunking using cAST algorithm.

Implements syntax-aware code chunking via Tree-sitter AST parsing.
Based on the ChunkHound pattern.

Three-phase process:
1. Parse & Extract: Tree-sitter generates AST, extract semantic concepts
2. Split: Break oversized chunks at syntax boundaries
3. Merge: Combine adjacent small chunks (respecting scope)

Supports 29 languages via Tree-sitter.
"""

import logging

from .languages import detect_language
from .types import ChunkType, CodeChunk

logger = logging.getLogger(__name__)


def chunk_code_file(
    content: str,
    file_path: str,
    max_chunk_size: int = 1200,
    min_chunk_size: int = 100,
    overlap_lines: int = 2,
) -> list[CodeChunk]:
    """
    Chunk a code file using Tree-sitter AST parsing.

    Three-phase process (cAST algorithm):
    1. Parse & Extract: Use Tree-sitter to parse AST and extract semantic units
    2. Split: Break oversized chunks at syntax boundaries
    3. Merge: Combine adjacent small chunks while respecting scope

    Args:
        content: Source code content
        file_path: Path to source file (for language detection)
        max_chunk_size: Maximum characters per chunk
        min_chunk_size: Minimum characters per chunk before merging
        overlap_lines: Number of lines to overlap between chunks

    Returns:
        List of CodeChunk objects
    """
    language = detect_language(file_path)

    if language is None:
        # Unknown language - fall back to line-based chunking
        return _chunk_by_lines(content, file_path, max_chunk_size)

    try:
        # Try Tree-sitter parsing
        return _chunk_with_treesitter(
            content,
            file_path,
            language,
            max_chunk_size,
            min_chunk_size,
            overlap_lines,
        )
    except Exception as e:
        logger.warning(f"Tree-sitter parsing failed for {file_path}: {e}")
        return _chunk_by_lines(content, file_path, max_chunk_size)


def _chunk_with_treesitter(
    content: str,
    file_path: str,
    language: str,
    max_chunk_size: int,
    min_chunk_size: int,
    overlap_lines: int,
) -> list[CodeChunk]:
    """Chunk using Tree-sitter AST parsing."""
    try:
        import tree_sitter_languages
    except ImportError:
        logger.warning("tree_sitter_languages not installed, falling back to line-based")
        return _chunk_by_lines(content, file_path, max_chunk_size)

    try:
        parser = tree_sitter_languages.get_parser(language)
    except Exception:
        logger.warning(f"No Tree-sitter parser for {language}, falling back to line-based")
        return _chunk_by_lines(content, file_path, max_chunk_size)

    tree = parser.parse(content.encode("utf-8"))
    root = tree.root_node

    # Phase 1: Extract semantic chunks from AST
    raw_chunks = _extract_ast_chunks(root, content, language)

    if not raw_chunks:
        return _chunk_by_lines(content, file_path, max_chunk_size)

    # Phase 2: Split oversized chunks
    split_chunks = []
    for chunk in raw_chunks:
        if len(chunk.text) > max_chunk_size:
            split_chunks.extend(_split_chunk(chunk, max_chunk_size, overlap_lines))
        else:
            split_chunks.append(chunk)

    # Phase 3: Merge small adjacent chunks
    merged_chunks = _merge_small_chunks(split_chunks, min_chunk_size, max_chunk_size)

    # Set language on all chunks
    for chunk in merged_chunks:
        chunk.language = language

    return merged_chunks


def _extract_ast_chunks(
    node,
    content: str,
    language: str,
    parent_name: str | None = None,
) -> list[CodeChunk]:
    """Extract semantic chunks from AST nodes."""
    chunks = []

    # Define node types that create chunks per language
    chunk_node_types = _get_chunk_node_types(language)

    # Check if current node is a chunk boundary
    if node.type in chunk_node_types:
        chunk_type = chunk_node_types[node.type]
        name = _extract_node_name(node, language)

        text = content[node.start_byte:node.end_byte]

        chunk = CodeChunk(
            text=text,
            chunk_type=chunk_type,
            name=name,
            start_line=node.start_point[0] + 1,
            end_line=node.end_point[0] + 1,
            parent_name=parent_name,
        )
        chunks.append(chunk)

        # Use this as parent for nested nodes
        parent_name = name or parent_name

    # Recurse into children
    for child in node.children:
        chunks.extend(_extract_ast_chunks(child, content, language, parent_name))

    return chunks


def _get_chunk_node_types(language: str) -> dict[str, ChunkType]:
    """Get AST node types that should create chunks for a language."""
    # Common patterns across languages
    common = {
        "comment": ChunkType.COMMENT,
    }

    language_specific = {
        "python": {
            "function_definition": ChunkType.FUNCTION,
            "async_function_definition": ChunkType.FUNCTION,
            "class_definition": ChunkType.CLASS,
            "decorated_definition": ChunkType.FUNCTION,
            "import_statement": ChunkType.IMPORT,
            "import_from_statement": ChunkType.IMPORT,
        },
        "javascript": {
            "function_declaration": ChunkType.FUNCTION,
            "arrow_function": ChunkType.FUNCTION,
            "class_declaration": ChunkType.CLASS,
            "method_definition": ChunkType.METHOD,
            "import_statement": ChunkType.IMPORT,
            "export_statement": ChunkType.IMPORT,
        },
        "typescript": {
            "function_declaration": ChunkType.FUNCTION,
            "arrow_function": ChunkType.FUNCTION,
            "class_declaration": ChunkType.CLASS,
            "method_definition": ChunkType.METHOD,
            "interface_declaration": ChunkType.INTERFACE,
            "type_alias_declaration": ChunkType.TYPE_ALIAS,
            "import_statement": ChunkType.IMPORT,
            "export_statement": ChunkType.IMPORT,
        },
        "rust": {
            "function_item": ChunkType.FUNCTION,
            "impl_item": ChunkType.CLASS,
            "struct_item": ChunkType.STRUCT,
            "enum_item": ChunkType.ENUM,
            "trait_item": ChunkType.INTERFACE,
            "use_declaration": ChunkType.IMPORT,
        },
        "go": {
            "function_declaration": ChunkType.FUNCTION,
            "method_declaration": ChunkType.METHOD,
            "type_declaration": ChunkType.TYPE_ALIAS,
            "import_declaration": ChunkType.IMPORT,
        },
        "java": {
            "method_declaration": ChunkType.METHOD,
            "constructor_declaration": ChunkType.METHOD,
            "class_declaration": ChunkType.CLASS,
            "interface_declaration": ChunkType.INTERFACE,
            "enum_declaration": ChunkType.ENUM,
            "import_declaration": ChunkType.IMPORT,
        },
    }

    node_types = dict(common)
    if language in language_specific:
        node_types.update(language_specific[language])

    return node_types


def _extract_node_name(node, language: str) -> str | None:
    """Extract the name from an AST node."""
    # Look for identifier children
    for child in node.children:
        if child.type in ("identifier", "name", "property_identifier"):
            return child.text.decode("utf-8") if child.text else None

    return None


def _split_chunk(
    chunk: CodeChunk,
    max_size: int,
    overlap_lines: int,
) -> list[CodeChunk]:
    """Split an oversized chunk at line boundaries."""
    lines = chunk.text.split("\n")
    chunks = []
    current_lines = []
    current_size = 0

    for i, line in enumerate(lines):
        line_size = len(line) + 1  # +1 for newline

        if current_size + line_size > max_size and current_lines:
            # Create chunk from current lines
            text = "\n".join(current_lines)
            chunks.append(CodeChunk(
                text=text,
                chunk_type=chunk.chunk_type,
                name=chunk.name,
                start_line=chunk.start_line + len(chunks) * (len(current_lines) - overlap_lines),
                end_line=chunk.start_line + i,
                parent_name=chunk.parent_name,
                metadata={"split_index": len(chunks)},
            ))

            # Keep overlap lines for next chunk
            current_lines = current_lines[-overlap_lines:] if overlap_lines > 0 else []
            current_size = sum(len(l) + 1 for l in current_lines)

        current_lines.append(line)
        current_size += line_size

    # Final chunk
    if current_lines:
        text = "\n".join(current_lines)
        chunks.append(CodeChunk(
            text=text,
            chunk_type=chunk.chunk_type,
            name=chunk.name,
            start_line=chunk.start_line + len(chunks) * (len(current_lines) - overlap_lines) if chunks else chunk.start_line,
            end_line=chunk.end_line,
            parent_name=chunk.parent_name,
            metadata={"split_index": len(chunks)},
        ))

    return chunks


def _merge_small_chunks(
    chunks: list[CodeChunk],
    min_size: int,
    max_size: int,
) -> list[CodeChunk]:
    """Merge adjacent small chunks while respecting scope."""
    if not chunks:
        return []

    merged = []
    current = chunks[0]

    for next_chunk in chunks[1:]:
        # Check if we can merge
        can_merge = (
            len(current.text) < min_size
            and len(current.text) + len(next_chunk.text) <= max_size
            and current.parent_name == next_chunk.parent_name
            and current.chunk_type == next_chunk.chunk_type
        )

        if can_merge:
            # Merge chunks
            current = CodeChunk(
                text=current.text + "\n" + next_chunk.text,
                chunk_type=current.chunk_type,
                name=current.name,
                start_line=current.start_line,
                end_line=next_chunk.end_line,
                parent_name=current.parent_name,
            )
        else:
            merged.append(current)
            current = next_chunk

    merged.append(current)
    return merged


def _chunk_by_lines(
    content: str,
    file_path: str,
    max_chunk_size: int,
    lines_per_chunk: int = 50,
) -> list[CodeChunk]:
    """Fallback: chunk by line count."""
    lines = content.split("\n")
    chunks = []

    for i in range(0, len(lines), lines_per_chunk):
        chunk_lines = lines[i:i + lines_per_chunk]
        text = "\n".join(chunk_lines)

        if text.strip():  # Skip empty chunks
            chunks.append(CodeChunk(
                text=text,
                chunk_type=ChunkType.OTHER,
                start_line=i + 1,
                end_line=min(i + lines_per_chunk, len(lines)),
                language=detect_language(file_path) or "text",
            ))

    return chunks
