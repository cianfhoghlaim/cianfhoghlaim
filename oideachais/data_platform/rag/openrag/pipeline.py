"""
Document processing pipeline for curriculum materials.

Orchestrates multimodal document ingestion, chunking,
and preparation for RAG retrieval.
"""

import hashlib
import logging
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from .multimodal import (
    DocumentConverter,
    ImageProcessor,
    TableExtractor,
    get_document_converter,
)
from .types import (
    DocumentChunk,
    DocumentType,
    ProcessedDocument,
    ProcessingConfig,
)

logger = logging.getLogger(__name__)


class DocumentPipeline:
    """
    Main pipeline for processing curriculum documents.

    Handles:
    - Document conversion (PDF, DOCX, HTML, images)
    - Text chunking with overlap
    - Table and image extraction
    - Integration with RAG storage
    """

    def __init__(
        self,
        config: ProcessingConfig | None = None,
        converter: DocumentConverter | None = None,
    ):
        self.config = config or ProcessingConfig()
        self.converter = converter
        self.image_processor = ImageProcessor(self.config)
        self.table_extractor = TableExtractor(self.config)

    async def _get_converter(self) -> DocumentConverter:
        """Get document converter."""
        if self.converter is None:
            self.converter = await get_document_converter(self.config)
        return self.converter

    async def process(
        self,
        source: str | Path,
        doc_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ProcessedDocument:
        """
        Process a document through the full pipeline.

        Args:
            source: File path or URL
            doc_id: Optional document ID (generated if not provided)
            metadata: Optional additional metadata

        Returns:
            ProcessedDocument with chunks, tables, and images
        """
        source_path = Path(source) if isinstance(source, str) and not source.startswith("http") else source
        source_str = str(source)

        # Generate doc_id if not provided
        if doc_id is None:
            doc_id = self._generate_doc_id(source_str)

        # Detect document type
        if isinstance(source_path, Path):
            doc_type = DocumentType.from_extension(source_path.suffix)
        else:
            # URL - try to detect from path
            parsed = urlparse(source_str)
            ext = Path(parsed.path).suffix
            doc_type = DocumentType.from_extension(ext) if ext else DocumentType.HTML

        logger.info(f"Processing {doc_type.value} document: {source_str}")

        # Convert document
        converter = await self._get_converter()
        raw_content = await converter.convert(source_str, doc_type)

        # Process tables
        tables = []
        if self.config.extract_tables:
            for table_data in raw_content.get("tables", []):
                table = self.table_extractor.process_extracted_table(table_data)
                tables.append(table)

        # Process images
        images = []
        if self.config.extract_images:
            doc_context = raw_content.get("text", "")[:500]  # First 500 chars for context
            for image_data in raw_content.get("images", []):
                image = await self.image_processor.process_extracted_image(
                    image_data,
                    doc_context,
                )
                images.append(image)

        # Chunk the text
        text = raw_content.get("text", "")
        chunks = self._chunk_text(text, doc_id, raw_content.get("page_count", 1))

        # Add table references to relevant chunks
        self._link_tables_to_chunks(chunks, tables)

        # Add image references to relevant chunks
        self._link_images_to_chunks(chunks, images)

        # Calculate total tokens
        total_tokens = sum(c.tokens for c in chunks)

        # Build result
        result = ProcessedDocument(
            doc_id=doc_id,
            source=source_str,
            doc_type=doc_type,
            title=self._extract_title(text),
            chunks=chunks,
            tables=tables,
            images=images,
            page_count=raw_content.get("page_count", 1),
            total_tokens=total_tokens,
            metadata={
                **(metadata or {}),
                **raw_content.get("metadata", {}),
            },
        )

        logger.info(
            f"Processed document {doc_id}: "
            f"{len(chunks)} chunks, {len(tables)} tables, {len(images)} images"
        )

        return result

    def _generate_doc_id(self, source: str) -> str:
        """Generate a unique document ID from source."""
        return hashlib.md5(source.encode()).hexdigest()[:16]

    def _chunk_text(
        self,
        text: str,
        doc_id: str,
        page_count: int,
    ) -> list[DocumentChunk]:
        """
        Split text into chunks with overlap.

        Uses sentence boundaries for cleaner splits.
        """
        if not text.strip():
            return []

        chunks = []
        chunk_size = self.config.chunk_size * 4  # Approximate chars per token
        overlap = self.config.chunk_overlap * 4

        start = 0
        chunk_idx = 0

        while start < len(text):
            end = min(start + chunk_size, len(text))

            # Try to break at sentence boundary
            if end < len(text):
                for sep in [". ", ".\n", "\n\n", "\n", " "]:
                    last_sep = text[start:end].rfind(sep)
                    if last_sep > chunk_size // 2:
                        end = start + last_sep + len(sep)
                        break

            content = text[start:end].strip()
            if content:
                chunk_id = hashlib.md5(
                    f"{doc_id}:chunk:{chunk_idx}".encode()
                ).hexdigest()[:12]

                # Estimate page number
                page_number = None
                if page_count > 1:
                    progress = start / len(text)
                    page_number = int(progress * page_count) + 1

                chunk = DocumentChunk(
                    id=chunk_id,
                    content=content,
                    doc_id=doc_id,
                    chunk_index=chunk_idx,
                    page_number=page_number,
                    tokens=len(content) // 4,  # Approximate
                )
                chunks.append(chunk)
                chunk_idx += 1

            start = end - overlap
            if start >= len(text) - overlap:
                break

        return chunks

    def _extract_title(self, text: str) -> str | None:
        """Extract title from document text."""
        lines = text.strip().split("\n")
        for line in lines[:10]:  # Check first 10 lines
            line = line.strip()
            # Skip empty lines and markdown headers
            if not line:
                continue
            # Check for markdown title
            if line.startswith("# "):
                return line[2:].strip()
            # First non-empty, non-heading line that's reasonably short
            if len(line) < 200 and not line.startswith("#"):
                return line
        return None

    def _link_tables_to_chunks(
        self,
        chunks: list[DocumentChunk],
        tables: list,
    ) -> None:
        """Link tables to their relevant chunks by page number."""
        if not tables:
            return

        for table in tables:
            if table.page_number is None:
                continue

            # Find chunks on the same page
            for chunk in chunks:
                if chunk.page_number == table.page_number:
                    chunk.table_refs.append(table.id)

    def _link_images_to_chunks(
        self,
        chunks: list[DocumentChunk],
        images: list,
    ) -> None:
        """Link images to their relevant chunks by page number."""
        if not images:
            return

        for image in images:
            if image.page_number is None:
                continue

            # Find chunks on the same page
            for chunk in chunks:
                if chunk.page_number == image.page_number:
                    chunk.image_refs.append(image.id)

    async def process_batch(
        self,
        sources: list[str | Path],
        metadata: dict[str, Any] | None = None,
    ) -> list[ProcessedDocument]:
        """
        Process multiple documents.

        Args:
            sources: List of file paths or URLs
            metadata: Optional shared metadata

        Returns:
            List of processed documents
        """
        results = []

        for source in sources:
            try:
                result = await self.process(source, metadata=metadata)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to process {source}: {e}")

        return results


async def process_document(
    source: str | Path,
    config: ProcessingConfig | None = None,
    doc_id: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> ProcessedDocument:
    """
    Convenience function to process a single document.

    Args:
        source: File path or URL
        config: Processing configuration
        doc_id: Optional document ID
        metadata: Optional additional metadata

    Returns:
        ProcessedDocument
    """
    pipeline = DocumentPipeline(config=config)
    return await pipeline.process(source, doc_id=doc_id, metadata=metadata)
