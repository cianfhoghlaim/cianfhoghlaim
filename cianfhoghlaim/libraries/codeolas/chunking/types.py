"""Type definitions for code chunking.

Shared types used across all flows that process code.
"""

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class ChunkType(StrEnum):
    """Types of code chunks extracted from AST."""

    FUNCTION = "function"
    CLASS = "class"
    METHOD = "method"
    MODULE = "module"
    INTERFACE = "interface"
    STRUCT = "struct"
    ENUM = "enum"
    IMPORT = "import"
    COMMENT = "comment"
    DOCSTRING = "docstring"
    VARIABLE = "variable"
    CONSTANT = "constant"
    TYPE_ALIAS = "type_alias"
    OTHER = "other"


@dataclass
class CodeChunk:
    """A chunk of code extracted from a source file."""

    text: str
    chunk_type: ChunkType
    name: str | None = None
    start_line: int = 0
    end_line: int = 0
    parent_name: str | None = None
    language: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
