"""orchestration.components.pipeline_kind_handlers

Per-source-kind handler classes for the
`orchestration.components.pipeline_factory.PipelineFactoryComponent`.

Each handler implements a `process_pipeline(dlt_source, ctx)` method
that returns a list of Dagster `AssetsDefinition`s specialised for that
source kind (syllabus, exam_papers, personal_archive, official_docs,
comics, crypto, pdf, media).

The 8 handler classes map to the 8 pipeline kinds declared in the
master refactor plan. Each handler is intentionally minimal — the heavy
lifting is done by the `PipelineFactoryComponent` which calls into the
appropriate handler via `kind`.
"""

from orchestration.components.pipeline_kind_handlers.base_handler import (
    BasePipelineHandler,
    PipelineContext,
)
from orchestration.components.pipeline_kind_handlers.comics_handler import (
    ComicsHandler,
)
from orchestration.components.pipeline_kind_handlers.crypto_handler import (
    CryptoHandler,
)
from orchestration.components.pipeline_kind_handlers.exam_papers_handler import (
    ExamPapersHandler,
)
from orchestration.components.pipeline_kind_handlers.media_handler import (
    MediaHandler,
)
from orchestration.components.pipeline_kind_handlers.official_docs_handler import (
    OfficialDocsHandler,
)
from orchestration.components.pipeline_kind_handlers.pdf_handler import (
    PdfHandler,
)
from orchestration.components.pipeline_kind_handlers.personal_archive_handler import (
    PersonalArchiveHandler,
)
from orchestration.components.pipeline_kind_handlers.syllabus_handler import (
    SyllabusHandler,
)

__all__ = [
    "BasePipelineHandler",
    "PipelineContext",
    "ComicsHandler",
    "CryptoHandler",
    "ExamPapersHandler",
    "MediaHandler",
    "OfficialDocsHandler",
    "PdfHandler",
    "PersonalArchiveHandler",
    "SyllabusHandler",
]

# Mapping from `pipeline_kind` string to the handler class.
# Used by `PipelineFactoryComponent` to dispatch.
PIPELINE_KIND_HANDLERS: dict[str, type[BasePipelineHandler]] = {
    "syllabus": SyllabusHandler,
    "exam_papers": ExamPapersHandler,
    "personal_archive": PersonalArchiveHandler,
    "official_docs": OfficialDocsHandler,
    "comics": ComicsHandler,
    "crypto": CryptoHandler,
    "pdf": PdfHandler,
    "media": MediaHandler,
}
