"""
Cognee Memory Service for Celtic Linguistics.

Provides:
- Knowledge graph construction from linguistic data
- Semantic search across Celtic languages
- Entity extraction (words, cognates, manuscripts)
- Relationship mapping (etymology, dialectal variants)

Based on research in:
- taighde_teanga/knowledge-graph-linguistics.md
- taighde_bonneagar/cognee-integration.md

Usage:
    from memory import CelticMemoryService, CogneeConfig

    config = CogneeConfig.for_celtic_linguistics()
    service = CelticMemoryService(config)

    # Add knowledge
    await service.add_vocabulary(words, language="irish")
    await service.add_manuscript(transcription, source="duchas")

    # Search
    results = await service.search_cognates("teach", languages=["irish", "scottish_gaelic"])
"""

import re
import unicodedata
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from .cognee_config import CogneeConfig


@dataclass
class CelticEntity:
    """Represents a Celtic linguistic entity."""

    text: str
    language: str
    entity_type: str  # word, phrase, cognate, etc.
    metadata: dict[str, Any] = field(default_factory=dict)

    # Optional fields
    dialect: str | None = None
    etymology: str | None = None
    pronunciation: str | None = None
    translation: str | None = None

    def to_cognee_format(self) -> str:
        """Convert to Cognee-compatible text format."""
        parts = [f"Entity: {self.text}"]
        parts.append(f"Language: {self.language}")
        parts.append(f"Type: {self.entity_type}")

        if self.dialect:
            parts.append(f"Dialect: {self.dialect}")
        if self.etymology:
            parts.append(f"Etymology: {self.etymology}")
        if self.pronunciation:
            parts.append(f"Pronunciation: {self.pronunciation}")
        if self.translation:
            parts.append(f"Translation: {self.translation}")

        for key, value in self.metadata.items():
            parts.append(f"{key}: {value}")

        return "\n".join(parts)


@dataclass
class CelticRelationship:
    """Represents a relationship between Celtic entities."""

    source: str
    target: str
    relationship_type: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_cognee_format(self) -> str:
        """Convert to Cognee-compatible format."""
        return f"{self.source} --[{self.relationship_type}]--> {self.target}"


@dataclass
class SearchResult:
    """Result from a Celtic memory search."""

    content: str
    score: float
    entity_type: str | None = None
    language: str | None = None
    source: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class CelticMemoryService:
    """
    Memory service for Celtic linguistic knowledge.

    Handles:
    - Vocabulary storage and retrieval
    - Manuscript transcription memory
    - Cognate detection and storage
    - Cross-language semantic search
    """

    def __init__(
        self,
        config: CogneeConfig | None = None,
    ):
        """
        Initialize memory service.

        Args:
            config: Cognee configuration
        """
        self.config = config or CogneeConfig.for_celtic_linguistics()
        self._cognee = None
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize Cognee with configuration."""
        if self._initialized:
            return

        try:
            import cognee

            self._cognee = cognee
        except ImportError:
            raise ImportError("cognee package required: pip install cognee")

        # Apply configuration
        await self.config.apply()
        self._initialized = True

    async def _ensure_initialized(self) -> None:
        """Ensure service is initialized."""
        if not self._initialized:
            await self.initialize()

    def _normalize_irish_text(self, text: str) -> str:
        """
        Normalize Irish text according to configuration.
        """
        # Unicode normalization
        text = unicodedata.normalize("NFC", text)

        # Handle Tironian et based on config
        celtic_config = self.config.celtic
        if celtic_config.tironian_handling == "expand":
            text = text.replace("⁊", "agus")
        elif celtic_config.tironian_handling == "normalize":
            # Replace common OCR confusions
            text = text.replace("7", "⁊")

        # Pre-1948 orthography normalization
        if celtic_config.normalize_pre1948:
            # Common pre-1948 spellings to modern
            pre1948_map = {
                "átuighim": "aithním",
                "oidhche": "oíche",
                "maidin": "maidin",
                # Add more as needed
            }
            for old, new in pre1948_map.items():
                text = text.replace(old, new)

        return text

    async def add_vocabulary(
        self,
        words: list[dict[str, Any]],
        language: str = "irish",
        dataset: str | None = None,
    ) -> int:
        """
        Add vocabulary to knowledge base.

        Args:
            words: List of word dictionaries with text, translation, etc.
            language: Language code
            dataset: Dataset name (default: language-based)

        Returns:
            Number of words added
        """
        await self._ensure_initialized()

        dataset = dataset or f"{language}_vocabulary"
        added = 0

        for word in words:
            entity = CelticEntity(
                text=word.get("word", word.get("text", "")),
                language=language,
                entity_type="word",
                translation=word.get("translation"),
                pronunciation=word.get("pronunciation"),
                dialect=word.get("dialect"),
                etymology=word.get("etymology"),
                metadata=word.get("metadata", {}),
            )

            content = entity.to_cognee_format()
            await self._cognee.add(content, dataset_name=dataset)
            added += 1

        # Cognify to build knowledge graph
        if added > 0:
            await self._cognee.cognify()

        return added

    async def add_manuscript(
        self,
        transcription: str,
        source: str,
        image_path: str | None = None,
        metadata: dict[str, Any] | None = None,
        dataset: str = "manuscripts",
    ) -> str:
        """
        Add manuscript transcription to knowledge base.

        Args:
            transcription: Transcribed text
            source: Source identifier (e.g., "duchas", "isos")
            image_path: Path to manuscript image
            metadata: Additional metadata
            dataset: Dataset name

        Returns:
            Manuscript ID
        """
        await self._ensure_initialized()

        # Normalize text
        normalized = self._normalize_irish_text(transcription)

        # Build content
        content = f"""
Manuscript Transcription
Source: {source}
Language: {self.config.celtic.primary_language}
Transcription: {normalized}
Original: {transcription}
"""

        if image_path:
            content += f"Image: {image_path}\n"

        if metadata:
            for key, value in metadata.items():
                content += f"{key}: {value}\n"

        # Add timestamp
        manuscript_id = f"{source}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        content += f"ID: {manuscript_id}\n"
        content += f"Added: {datetime.now().isoformat()}\n"

        await self._cognee.add(content, dataset_name=dataset)
        await self._cognee.cognify()

        return manuscript_id

    async def add_cognates(
        self,
        cognate_group: list[dict[str, Any]],
        etymology: str | None = None,
        dataset: str = "cognates",
    ) -> None:
        """
        Add cognate group across Celtic languages.

        Args:
            cognate_group: List of cognates with language and text
            etymology: Shared etymology
            dataset: Dataset name
        """
        await self._ensure_initialized()

        # Build cognate content
        content = "Cognate Group:\n"

        for cognate in cognate_group:
            language = cognate.get("language", "unknown")
            text = cognate.get("text", "")
            meaning = cognate.get("meaning", "")

            content += f"- {language}: {text}"
            if meaning:
                content += f" ({meaning})"
            content += "\n"

        if etymology:
            content += f"Etymology: {etymology}\n"

        # Add relationships
        for i, source in enumerate(cognate_group):
            for target in cognate_group[i + 1 :]:
                rel = CelticRelationship(
                    source=f"{source['language']}:{source['text']}",
                    target=f"{target['language']}:{target['text']}",
                    relationship_type="is_cognate_of",
                )
                content += rel.to_cognee_format() + "\n"

        await self._cognee.add(content, dataset_name=dataset)
        await self._cognee.cognify()

    async def add_transcription_correction(
        self,
        original: str,
        corrected: str,
        source: str,
        error_type: str = "ocr",
        dataset: str = "ocr_corrections",
    ) -> None:
        """
        Add OCR correction for training.

        Args:
            original: Original OCR output
            corrected: Human-corrected text
            source: Source identifier
            error_type: Type of error (ocr, spelling, etc.)
            dataset: Dataset name
        """
        await self._ensure_initialized()

        content = f"""
Correction:
Original: {original}
Corrected: {corrected}
Source: {source}
Error Type: {error_type}
Added: {datetime.now().isoformat()}
"""

        await self._cognee.add(content, dataset_name=dataset)
        await self._cognee.cognify()

    async def search(
        self,
        query: str,
        search_type: str = "graph_completion",
        languages: list[str] | None = None,
        datasets: list[str] | None = None,
        top_k: int = 10,
    ) -> list[SearchResult]:
        """
        Search Celtic knowledge base.

        Args:
            query: Search query
            search_type: Type of search (chunks, insights, graph_completion)
            languages: Filter by languages
            datasets: Filter by datasets
            top_k: Maximum results

        Returns:
            List of search results
        """
        await self._ensure_initialized()

        from cognee.api.v1.search import SearchType

        # Map search type
        search_type_map = {
            "chunks": SearchType.CHUNKS,
            "insights": SearchType.INSIGHTS,
            "graph_completion": SearchType.GRAPH_COMPLETION,
            "summaries": SearchType.SUMMARIES,
            "feeling_lucky": SearchType.FEELING_LUCKY,
        }

        cognee_type = search_type_map.get(search_type, SearchType.GRAPH_COMPLETION)

        # Execute search
        results = await self._cognee.search(
            query_text=query,
            query_type=cognee_type,
            top_k=top_k,
        )

        # Convert to SearchResult
        search_results = []
        for result in results:
            # Parse result content
            content = str(result) if not isinstance(result, dict) else result.get("content", str(result))

            # Extract metadata from content
            language = None
            entity_type = None
            source = None

            if "Language:" in content:
                match = re.search(r"Language:\s*(\w+)", content)
                if match:
                    language = match.group(1)

            if "Type:" in content:
                match = re.search(r"Type:\s*(\w+)", content)
                if match:
                    entity_type = match.group(1)

            if "Source:" in content:
                match = re.search(r"Source:\s*(\w+)", content)
                if match:
                    source = match.group(1)

            # Filter by language if specified
            if languages and language and language not in languages:
                continue

            search_results.append(
                SearchResult(
                    content=content,
                    score=result.get("score", 0.0) if isinstance(result, dict) else 0.0,
                    entity_type=entity_type,
                    language=language,
                    source=source,
                )
            )

        return search_results

    async def search_cognates(
        self,
        word: str,
        source_language: str = "irish",
        target_languages: list[str] | None = None,
    ) -> list[SearchResult]:
        """
        Search for cognates of a word.

        Args:
            word: Word to find cognates for
            source_language: Language of the word
            target_languages: Target languages for cognates

        Returns:
            List of cognate search results
        """
        target_languages = target_languages or ["scottish_gaelic", "welsh", "manx"]

        query = f"Find cognates of {source_language} word '{word}' in {', '.join(target_languages)}"

        return await self.search(
            query=query,
            search_type="graph_completion",
            top_k=20,
        )

    async def search_etymology(
        self,
        word: str,
        language: str = "irish",
    ) -> list[SearchResult]:
        """
        Search for etymology of a word.

        Args:
            word: Word to find etymology for
            language: Language of the word

        Returns:
            Etymology search results
        """
        query = f"What is the etymology of {language} word '{word}'?"

        return await self.search(
            query=query,
            search_type="graph_completion",
            top_k=10,
        )

    async def search_dialect_variants(
        self,
        word: str,
        dialects: list[str] | None = None,
    ) -> list[SearchResult]:
        """
        Search for dialect variants of an Irish word.

        Args:
            word: Word to find variants for
            dialects: Dialects to search (default: all)

        Returns:
            Dialect variant search results
        """
        dialects = dialects or self.config.celtic.irish_dialects

        query = f"Find dialect variants of '{word}' in {', '.join(dialects)} Irish dialects"

        return await self.search(
            query=query,
            search_type="insights",
            top_k=10,
        )

    async def get_related_manuscripts(
        self,
        query: str,
        source: str | None = None,
        top_k: int = 5,
    ) -> list[SearchResult]:
        """
        Find related manuscript transcriptions.

        Args:
            query: Search query or text
            source: Filter by source (duchas, isos, etc.)
            top_k: Maximum results

        Returns:
            Related manuscript results
        """
        search_query = f"Find manuscripts related to: {query}"
        if source:
            search_query += f" from source {source}"

        return await self.search(
            query=search_query,
            search_type="chunks",
            datasets=["manuscripts"],
            top_k=top_k,
        )

    async def visualize_knowledge(
        self,
        output_path: str | Path = "./celtic_knowledge_graph.html",
    ) -> Path:
        """
        Generate visualization of knowledge graph.

        Args:
            output_path: Path for HTML output

        Returns:
            Path to visualization file
        """
        await self._ensure_initialized()

        output_path = Path(output_path)
        await self._cognee.visualize_graph(str(output_path))

        return output_path

    async def export_knowledge(
        self,
        output_path: str | Path,
        format: str = "json",
        datasets: list[str] | None = None,
    ) -> Path:
        """
        Export knowledge base.

        Args:
            output_path: Output file path
            format: Export format (json, cypher)
            datasets: Datasets to export

        Returns:
            Path to exported file
        """
        await self._ensure_initialized()

        output_path = Path(output_path)

        # Gather all knowledge via search
        all_results = await self.search(
            query="*",
            search_type="chunks",
            datasets=datasets,
            top_k=10000,
        )

        if format == "json":
            import json

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(
                    [
                        {
                            "content": r.content,
                            "score": r.score,
                            "language": r.language,
                            "entity_type": r.entity_type,
                            "source": r.source,
                        }
                        for r in all_results
                    ],
                    f,
                    indent=2,
                    ensure_ascii=False,
                )
        else:
            # Cypher export
            with open(output_path, "w", encoding="utf-8") as f:
                for r in all_results:
                    # Create basic Cypher node
                    props = {
                        "content": r.content,
                        "language": r.language or "unknown",
                        "type": r.entity_type or "unknown",
                    }
                    cypher = f"CREATE (n:CelticEntity {{{props}}})"
                    f.write(cypher + ";\n")

        return output_path

    async def prune(self, datasets: list[str] | None = None) -> None:
        """
        Clear knowledge base data.

        Args:
            datasets: Specific datasets to clear (None = all)
        """
        await self._ensure_initialized()

        if datasets:
            for dataset in datasets:
                await self._cognee.delete(dataset)
        else:
            await self._cognee.prune.prune_data()

    async def reset(self) -> None:
        """
        Full system reset including metadata.
        """
        await self._ensure_initialized()
        await self._cognee.prune.prune_system(metadata=True)
        self._initialized = False
