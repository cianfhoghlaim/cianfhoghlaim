"""
Core type definitions for códeolas.

Includes 40+ relationship types from knowledge-graph pattern,
precise source ranges (line:column), and comprehensive code entity types.
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
    LAMBDA = "lambda"
    PROPERTY = "property"
    CONSTRUCTOR = "constructor"
    ENUM_ENTRY = "enum_entry"
    PROC = "proc"  # Ruby procs
    SINGLETON_METHOD = "singleton_method"
    OTHER = "other"


class NodeType(StrEnum):
    """Types of nodes in the code knowledge graph."""

    # Structural nodes
    DIRECTORY = "Directory"
    FILE = "File"

    # Definition nodes
    MODULE = "Module"
    CLASS = "Class"
    INTERFACE = "Interface"
    FUNCTION = "Function"
    METHOD = "Method"
    SINGLETON_METHOD = "SingletonMethod"
    PROPERTY = "Property"
    CONSTRUCTOR = "Constructor"
    LAMBDA = "Lambda"
    PROC = "Proc"

    # Data nodes
    VARIABLE = "Variable"
    CONSTANT = "Constant"
    ENUM = "Enum"
    ENUM_ENTRY = "EnumEntry"

    # Import nodes
    IMPORTED_SYMBOL = "ImportedSymbol"

    # Type nodes
    TYPE_ALIAS = "TypeAlias"


class EdgeType(StrEnum):
    """
    Basic relationship types (backwards-compatible).

    For fine-grained relationships, use RelationshipType.
    """

    CONTAINS = "CONTAINS"
    IMPORTS = "IMPORTS"
    CALLS = "CALLS"
    EXTENDS = "EXTENDS"
    IMPLEMENTS = "IMPLEMENTS"
    USES = "USES"
    DEFINES = "DEFINES"


class RelationshipType(StrEnum):
    """
    Comprehensive relationship types for code knowledge graphs.

    Based on bonneagar/examples/knowledge-graph pattern with 40+ relationship types.
    Enables precise semantic queries like "find all classes that implement interface X".
    """

    # Directory relationships
    DIR_CONTAINS_DIR = "DIR_CONTAINS_DIR"
    DIR_CONTAINS_FILE = "DIR_CONTAINS_FILE"

    # File relationships
    FILE_DEFINES = "FILE_DEFINES"
    FILE_IMPORTS = "FILE_IMPORTS"

    # Definition-imported-symbol relationships
    DEFINES_IMPORTED_SYMBOL = "DEFINES_IMPORTED_SYMBOL"

    # Module relationships
    MODULE_TO_METHOD = "MODULE_TO_METHOD"
    MODULE_TO_SINGLETON_METHOD = "MODULE_TO_SINGLETON_METHOD"
    MODULE_TO_CLASS = "MODULE_TO_CLASS"
    MODULE_TO_MODULE = "MODULE_TO_MODULE"

    # Class relationships
    CLASS_TO_METHOD = "CLASS_TO_METHOD"
    CLASS_TO_SINGLETON_METHOD = "CLASS_TO_SINGLETON_METHOD"
    CLASS_TO_CLASS = "CLASS_TO_CLASS"
    CLASS_TO_LAMBDA = "CLASS_TO_LAMBDA"
    CLASS_TO_PROC = "CLASS_TO_PROC"
    CLASS_TO_INTERFACE = "CLASS_TO_INTERFACE"
    CLASS_TO_PROPERTY = "CLASS_TO_PROPERTY"
    CLASS_TO_CONSTRUCTOR = "CLASS_TO_CONSTRUCTOR"
    CLASS_TO_ENUM_ENTRY = "CLASS_TO_ENUM_ENTRY"

    # Function relationships
    FUNCTION_TO_FUNCTION = "FUNCTION_TO_FUNCTION"
    FUNCTION_TO_CLASS = "FUNCTION_TO_CLASS"
    FUNCTION_TO_LAMBDA = "FUNCTION_TO_LAMBDA"
    FUNCTION_TO_PROC = "FUNCTION_TO_PROC"

    # Lambda relationships
    LAMBDA_TO_LAMBDA = "LAMBDA_TO_LAMBDA"
    LAMBDA_TO_CLASS = "LAMBDA_TO_CLASS"
    LAMBDA_TO_FUNCTION = "LAMBDA_TO_FUNCTION"
    LAMBDA_TO_PROC = "LAMBDA_TO_PROC"
    LAMBDA_TO_METHOD = "LAMBDA_TO_METHOD"
    LAMBDA_TO_PROPERTY = "LAMBDA_TO_PROPERTY"
    LAMBDA_TO_INTERFACE = "LAMBDA_TO_INTERFACE"

    # Method relationships
    METHOD_TO_METHOD = "METHOD_TO_METHOD"
    METHOD_TO_CLASS = "METHOD_TO_CLASS"
    METHOD_TO_FUNCTION = "METHOD_TO_FUNCTION"
    METHOD_TO_LAMBDA = "METHOD_TO_LAMBDA"
    METHOD_TO_PROC = "METHOD_TO_PROC"
    METHOD_TO_PROPERTY = "METHOD_TO_PROPERTY"
    METHOD_TO_INTERFACE = "METHOD_TO_INTERFACE"

    # Interface relationships
    INTERFACE_TO_INTERFACE = "INTERFACE_TO_INTERFACE"
    INTERFACE_TO_CLASS = "INTERFACE_TO_CLASS"
    INTERFACE_TO_METHOD = "INTERFACE_TO_METHOD"
    INTERFACE_TO_FUNCTION = "INTERFACE_TO_FUNCTION"
    INTERFACE_TO_PROPERTY = "INTERFACE_TO_PROPERTY"
    INTERFACE_TO_LAMBDA = "INTERFACE_TO_LAMBDA"

    # Reference relationships
    CALLS = "CALLS"
    AMBIGUOUSLY_CALLS = "AMBIGUOUSLY_CALLS"
    PROPERTY_REFERENCE = "PROPERTY_REFERENCE"

    # Imported symbol relationships
    IMPORTED_SYMBOL_TO_IMPORTED_SYMBOL = "IMPORTED_SYMBOL_TO_IMPORTED_SYMBOL"
    IMPORTED_SYMBOL_TO_DEFINITION = "IMPORTED_SYMBOL_TO_DEFINITION"
    IMPORTED_SYMBOL_TO_FILE = "IMPORTED_SYMBOL_TO_FILE"

    # Legacy (backwards compatibility)
    CONTAINS = "CONTAINS"
    IMPORTS = "IMPORTS"
    EXTENDS = "EXTENDS"
    IMPLEMENTS = "IMPLEMENTS"
    USES = "USES"
    DEFINES = "DEFINES"

    # Empty (placeholder)
    EMPTY = "EMPTY"

    @classmethod
    def all_types(cls) -> list["RelationshipType"]:
        """Get all relationship types."""
        return list(cls)

    @classmethod
    def structural_types(cls) -> list["RelationshipType"]:
        """Get structural relationship types (contains, defines)."""
        return [
            cls.DIR_CONTAINS_DIR,
            cls.DIR_CONTAINS_FILE,
            cls.FILE_DEFINES,
            cls.CONTAINS,
            cls.DEFINES,
        ]

    @classmethod
    def reference_types(cls) -> list["RelationshipType"]:
        """Get reference relationship types (calls, uses)."""
        return [
            cls.CALLS,
            cls.AMBIGUOUSLY_CALLS,
            cls.PROPERTY_REFERENCE,
            cls.USES,
        ]


@dataclass
class SourceRange:
    """
    Precise source code location with line:column ranges.

    Based on knowledge-graph pattern for go-to-definition support.
    All values are 1-indexed (as displayed in editors).
    """

    start_line: int
    start_column: int
    end_line: int
    end_column: int

    @classmethod
    def from_node(cls, node) -> "SourceRange":
        """Create from Tree-sitter node (0-indexed to 1-indexed)."""
        return cls(
            start_line=node.start_point[0] + 1,
            start_column=node.start_point[1] + 1,
            end_line=node.end_point[0] + 1,
            end_column=node.end_point[1] + 1,
        )

    def to_dict(self) -> dict[str, int]:
        """Convert to dictionary."""
        return {
            "start_line": self.start_line,
            "start_column": self.start_column,
            "end_line": self.end_line,
            "end_column": self.end_column,
        }

    def __str__(self) -> str:
        """Format as file_path:line:column reference."""
        if self.start_line == self.end_line:
            return f"{self.start_line}:{self.start_column}-{self.end_column}"
        return f"{self.start_line}:{self.start_column}-{self.end_line}:{self.end_column}"


@dataclass
class CodeChunk:
    """A chunk of code extracted from a source file."""

    text: str
    chunk_type: ChunkType
    name: str | None = None
    file_path: str = ""
    language: str = ""

    # Precise location (line:column)
    source_range: SourceRange | None = None

    # Legacy line-only fields (for backwards compatibility)
    start_line: int = 0
    end_line: int = 0

    # Hierarchy
    parent_name: str | None = None
    parent_id: str | None = None

    # Metadata
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Set line fields from source_range if available."""
        if self.source_range and self.start_line == 0:
            self.start_line = self.source_range.start_line
            self.end_line = self.source_range.end_line


@dataclass
class GraphNode:
    """A node in the code knowledge graph."""

    id: str
    node_type: NodeType
    name: str
    file_path: str

    # Precise locations
    source_range: SourceRange | None = None
    definition_range: SourceRange | None = None

    # Legacy line fields
    start_line: int | None = None
    end_line: int | None = None

    # Metadata
    language: str = ""
    signature: str | None = None  # Function/method signature
    doc: str | None = None  # Docstring
    properties: dict[str, Any] | None = None


@dataclass
class GraphEdge:
    """A relationship between nodes in the code graph."""

    source_id: str
    target_id: str
    edge_type: EdgeType | RelationshipType

    # Source location where the reference occurs
    reference_range: SourceRange | None = None

    # Metadata
    properties: dict[str, Any] | None = None


@dataclass
class SearchResult:
    """Result from semantic code search."""

    chunk: CodeChunk
    score: float
    distance: float | None = None

    # Relevance metadata
    rerank_score: float | None = None
    explanation: str | None = None


@dataclass
class Entity:
    """
    A code entity for deduplication and canonicalization.

    Based on LightRAG pattern for entity management.
    """

    id: str
    canonical_name: str
    entity_type: NodeType
    aliases: list[str] = field(default_factory=list)
    occurrences: list[str] = field(default_factory=list)  # File paths
    metadata: dict[str, Any] = field(default_factory=dict)

    def matches(self, name: str) -> bool:
        """Check if name matches this entity."""
        normalized = name.lower().strip()
        if self.canonical_name.lower() == normalized:
            return True
        return any(alias.lower() == normalized for alias in self.aliases)

    def add_alias(self, alias: str) -> None:
        """Add an alias if not already present."""
        if alias not in self.aliases and alias != self.canonical_name:
            self.aliases.append(alias)

    def add_occurrence(self, file_path: str) -> None:
        """Record an occurrence of this entity."""
        if file_path not in self.occurrences:
            self.occurrences.append(file_path)
