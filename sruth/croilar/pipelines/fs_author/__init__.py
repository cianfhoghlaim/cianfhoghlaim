"""Author-folder filesystem DLT source.

Public surface:

    from pipelines.fs_author import fs_author_source, run_fs_author_pipeline

Always local-only. Never uploads to R2.
"""

from .source import fs_author_source, run_fs_author_pipeline

__all__ = ["fs_author_source", "run_fs_author_pipeline"]
