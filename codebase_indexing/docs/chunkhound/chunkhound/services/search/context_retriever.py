"""Context retrieval utilities for search operations.

This module provides functionality for retrieving additional context around
search results, including surrounding chunks and file-level chunk information.
"""

from typing import Any

from loguru import logger

from chunkhound.core.types.common import ChunkId
from chunkhound.interfaces.database_provider import DatabaseProvider


class ContextRetriever:
    """Utility class for retrieving context around search results."""

    def __init__(self, database_provider: DatabaseProvider):
        """Initialize context retriever.

        Args:
            database_provider: Database provider for data access
        """
        self._db = database_provider

    def get_chunk_context(
        self, chunk_id: ChunkId, context_lines: int = 5
    ) -> dict[str, Any]:
        """Get additional context around a specific chunk.

        Args:
            chunk_id: ID of the chunk to get context for
            context_lines: Number of lines before/after to include

        Returns:
            Dictionary with chunk details and surrounding context
        """
        try:
            # Get chunk details
            chunk_query = """
                SELECT c.*, f.path, f.language
                FROM chunks c
                JOIN files f ON c.file_id = f.id
                WHERE c.id = ?
            """
            chunk_results = self._db.execute_query(chunk_query, [chunk_id])

            if not chunk_results:
                return {}

            chunk = chunk_results[0]

            # Get surrounding chunks for context
            context_query = """
                SELECT symbol, start_line, end_line, code, chunk_type
                FROM chunks
                WHERE file_id = ?
                AND (
                    (start_line BETWEEN ? AND ?) OR
                    (end_line BETWEEN ? AND ?) OR
                    (start_line <= ? AND end_line >= ?)
                )
                ORDER BY start_line
            """

            start_context = max(1, chunk["start_line"] - context_lines)
            end_context = chunk["end_line"] + context_lines

            context_results = self._db.execute_query(
                context_query,
                [
                    chunk["file_id"],
                    start_context,
                    end_context,
                    start_context,
                    end_context,
                    start_context,
                    end_context,
                ],
            )

            return {
                "chunk": chunk,
                "context": context_results,
                "file_path": chunk["path"],
                "language": chunk["language"],
            }

        except Exception as e:
            logger.error(f"Failed to get chunk context for {chunk_id}: {e}")
            return {}

    def get_file_chunks(self, file_path: str) -> list[dict[str, Any]]:
        """Get all chunks for a specific file.

        Args:
            file_path: Path to the file

        Returns:
            List of chunks in the file ordered by line number
        """
        try:
            query = """
                SELECT c.*, f.language
                FROM chunks c
                JOIN files f ON c.file_id = f.id
                WHERE f.path = ?
                ORDER BY c.start_line
            """

            results = self._db.execute_query(query, [file_path])

            return results

        except Exception as e:
            logger.error(f"Failed to get chunks for file {file_path}: {e}")
            return []
