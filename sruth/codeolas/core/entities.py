"""
Entity extraction and deduplication for códeolas.

Based on LightRAG pattern for canonicalization of code symbols.
Handles entity aliasing, deduplication, and cross-file resolution.
"""

import logging
import re
from collections import defaultdict
from difflib import SequenceMatcher

from sruth.codeolas.core.types import CodeChunk, Entity, NodeType

logger = logging.getLogger(__name__)


class EntityExtractor:
    """
    Extract and canonicalize code entities from chunks.

    Based on LightRAG pattern for multi-level RAG:
    Documents -> Chunks -> Entities -> Relationships

    Entity deduplication ensures consistent references across files.
    """

    def __init__(
        self,
        similarity_threshold: float = 0.85,
        case_sensitive: bool = False,
    ):
        self.similarity_threshold = similarity_threshold
        self.case_sensitive = case_sensitive
        self.entities: dict[str, Entity] = {}  # canonical_name -> Entity
        self._alias_index: dict[str, str] = {}  # alias -> canonical_name

    def extract_from_chunk(self, chunk: CodeChunk) -> list[Entity]:
        """
        Extract entities from a code chunk.

        Args:
            chunk: Code chunk to extract entities from

        Returns:
            List of extracted entities
        """
        entities = []

        # Extract main entity from chunk
        if chunk.name:
            entity_type = self._chunk_type_to_node_type(chunk.chunk_type)
            entity = self._get_or_create_entity(
                name=chunk.name,
                entity_type=entity_type,
                file_path=chunk.file_path,
            )
            entities.append(entity)

        # Extract referenced entities from text
        referenced = self._extract_references(chunk.text, chunk.language)
        for ref_name, ref_type in referenced:
            entity = self._get_or_create_entity(
                name=ref_name,
                entity_type=ref_type,
                file_path=chunk.file_path,
            )
            entities.append(entity)

        return entities

    def extract_from_chunks(self, chunks: list[CodeChunk]) -> list[Entity]:
        """
        Extract all entities from multiple chunks.

        Args:
            chunks: List of code chunks

        Returns:
            List of all unique entities
        """
        for chunk in chunks:
            self.extract_from_chunk(chunk)

        return list(self.entities.values())

    def _get_or_create_entity(
        self,
        name: str,
        entity_type: NodeType,
        file_path: str,
    ) -> Entity:
        """Get existing entity or create new one."""
        # Check for exact match
        normalized = self._normalize_name(name)
        if normalized in self.entities:
            entity = self.entities[normalized]
            entity.add_occurrence(file_path)
            return entity

        # Check alias index
        if normalized in self._alias_index:
            canonical = self._alias_index[normalized]
            entity = self.entities[canonical]
            entity.add_occurrence(file_path)
            return entity

        # Check for similar existing entity
        similar = self._find_similar_entity(name, entity_type)
        if similar:
            similar.add_alias(name)
            similar.add_occurrence(file_path)
            self._alias_index[normalized] = self._normalize_name(similar.canonical_name)
            return similar

        # Create new entity
        entity_id = f"{entity_type.value.lower()}:{normalized}"
        entity = Entity(
            id=entity_id,
            canonical_name=name,
            entity_type=entity_type,
            aliases=[],
            occurrences=[file_path],
        )
        self.entities[normalized] = entity
        return entity

    def _find_similar_entity(
        self,
        name: str,
        entity_type: NodeType,
    ) -> Entity | None:
        """Find similar existing entity."""
        normalized = self._normalize_name(name)

        for canonical, entity in self.entities.items():
            # Must be same type
            if entity.entity_type != entity_type:
                continue

            # Check similarity
            ratio = SequenceMatcher(None, normalized, canonical).ratio()
            if ratio >= self.similarity_threshold:
                return entity

        return None

    def _normalize_name(self, name: str) -> str:
        """Normalize a name for comparison."""
        if not self.case_sensitive:
            name = name.lower()

        # Remove common prefixes/suffixes
        name = re.sub(r"^(get|set|is|has|can|should)_?", "", name, flags=re.IGNORECASE)

        # Normalize separators
        name = re.sub(r"[-_]", "", name)

        return name.strip()

    def _chunk_type_to_node_type(self, chunk_type) -> NodeType:
        """Convert chunk type to node type."""
        from codeolas.core.types import ChunkType

        mapping = {
            ChunkType.FUNCTION: NodeType.FUNCTION,
            ChunkType.CLASS: NodeType.CLASS,
            ChunkType.METHOD: NodeType.METHOD,
            ChunkType.MODULE: NodeType.MODULE,
            ChunkType.INTERFACE: NodeType.INTERFACE,
            ChunkType.STRUCT: NodeType.CLASS,
            ChunkType.ENUM: NodeType.ENUM,
            ChunkType.VARIABLE: NodeType.VARIABLE,
            ChunkType.CONSTANT: NodeType.CONSTANT,
            ChunkType.TYPE_ALIAS: NodeType.TYPE_ALIAS,
            ChunkType.LAMBDA: NodeType.LAMBDA,
            ChunkType.PROPERTY: NodeType.PROPERTY,
            ChunkType.CONSTRUCTOR: NodeType.CONSTRUCTOR,
        }
        return mapping.get(chunk_type, NodeType.FUNCTION)

    def _extract_references(
        self,
        text: str,
        language: str,
    ) -> list[tuple[str, NodeType]]:
        """
        Extract entity references from code text.

        Returns list of (name, type) tuples.
        """
        references = []

        # Function/method calls
        call_pattern = r"([a-zA-Z_][a-zA-Z0-9_]*)\s*\("
        for match in re.finditer(call_pattern, text):
            name = match.group(1)
            if not self._is_keyword(name, language):
                references.append((name, NodeType.FUNCTION))

        # Class instantiation
        if language in ("python", "javascript", "typescript"):
            class_pattern = r"\bnew\s+([A-Z][a-zA-Z0-9_]*)"
            for match in re.finditer(class_pattern, text):
                references.append((match.group(1), NodeType.CLASS))

        # Python class instantiation
        if language == "python":
            py_class_pattern = r"([A-Z][a-zA-Z0-9_]*)\s*\("
            for match in re.finditer(py_class_pattern, text):
                references.append((match.group(1), NodeType.CLASS))

        return references

    def _is_keyword(self, name: str, language: str) -> bool:
        """Check if name is a language keyword."""
        keywords = {
            "python": {
                "if",
                "else",
                "elif",
                "for",
                "while",
                "def",
                "class",
                "return",
                "import",
                "from",
                "as",
                "try",
                "except",
                "finally",
                "with",
                "async",
                "await",
                "yield",
                "print",
                "len",
                "range",
                "list",
                "dict",
                "set",
                "str",
                "int",
                "float",
                "bool",
                "None",
                "True",
                "False",
            },
            "javascript": {
                "if",
                "else",
                "for",
                "while",
                "function",
                "class",
                "return",
                "import",
                "export",
                "const",
                "let",
                "var",
                "async",
                "await",
                "new",
                "this",
                "super",
                "console",
                "require",
            },
            "typescript": {
                "if",
                "else",
                "for",
                "while",
                "function",
                "class",
                "return",
                "import",
                "export",
                "const",
                "let",
                "var",
                "async",
                "await",
                "new",
                "this",
                "super",
                "console",
                "require",
                "interface",
                "type",
            },
        }
        lang_keywords = keywords.get(language, set())
        return name.lower() in lang_keywords


def deduplicate_entities(entities: list[Entity]) -> list[Entity]:
    """
    Deduplicate a list of entities.

    Args:
        entities: List of entities to deduplicate

    Returns:
        Deduplicated list with merged aliases and occurrences
    """
    extractor = EntityExtractor()

    for entity in entities:
        # Get or merge with existing
        merged = extractor._get_or_create_entity(
            name=entity.canonical_name,
            entity_type=entity.entity_type,
            file_path=entity.occurrences[0] if entity.occurrences else "",
        )

        # Merge aliases
        for alias in entity.aliases:
            merged.add_alias(alias)

        # Merge occurrences
        for occ in entity.occurrences:
            merged.add_occurrence(occ)

    return list(extractor.entities.values())
