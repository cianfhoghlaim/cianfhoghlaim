"""
Local file DLT sources for Crypteolas.

Provides ingestion for:
- Local workspace files
- Code repositories
- Documentation files
"""

from .file_watcher import (
    local_files_source,
    workspace_source,
    code_files_source,
)

__all__ = [
    "local_files_source",
    "workspace_source",
    "code_files_source",
]
