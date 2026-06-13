"""
DLT Sources for Irish Education Data.

Sources:
- NCCA curriculum documents
- SEC examinations and reports
- OIDE CPD resources
- EdcoLearning exam audio
- Local document processing
"""
from .curriculum_source import (
    curriculum_source,
)

# EdcoLearning is guarded — its `oideachais.http_utils` import is broken
# post-cleanup (commit 8484a6353 removed the legacy http_utils shim).
# Wrapping the import in try/except lets the rest of the ireland sources
# load for the LC + curriculum pipelines without dragging in a dead
# dependency.
try:
    from .edcolearning import (  # noqa: F401
        EdcoCredentials,
        ExamLevel,
        ExamSubject,
        edcolearning_source,
        french_lc_audio_source,
        german_lc_audio_source,
        irish_lc_audio_source,
        languages_lc_audio_source,
        spanish_lc_audio_source,
    )
    _edcolearning_imported = True
except ImportError as e:
    import structlog as _sl
    _sl.get_logger().warning("ireland_edcolearning_import_skipped: %s", e)
    _edcolearning_imported = False

from .examinations import (
    examinations_source,
    junior_cycle_exams_source,
    leaving_certificate_source,
    mathematics_exams_source,
    science_subjects_exams_source,
    sec_examinations_browser_source,
)
from .leaving_cert import (
    SUBJECTS,
    leaving_cert_source,
)
from .local_documents import (
    FileHashTracker,
    local_documents_by_subject_source,
    local_education_documents_source,
)
from .ncca import ncca_source
from .oide import oide_all_subjects_source, oide_gaeilge_source, oide_source, oide_subject_source
from .sec_aural_transcripts import (
    AuralTranscript,
    IrishDialect,
    SpeakerSegment,
    TranscriptType,
    irish_lc_transcripts_source,
    languages_lc_transcripts_source,
    sec_aural_transcripts_source,
)

__all__ = [
    # NCCA
    "ncca_source",
    # OIDE
    "oide_source",
    "oide_subject_source",
    "oide_gaeilge_source",
    "oide_all_subjects_source",
    # SEC Examinations
    "examinations_source",
    "sec_examinations_browser_source",
    "leaving_certificate_source",
    "junior_cycle_exams_source",
    "mathematics_exams_source",
    "science_subjects_exams_source",
    # Local Documents
    "local_education_documents_source",
    "local_documents_by_subject_source",
    "FileHashTracker",
    # Unified Curriculum
    "curriculum_source",
    # Leaving Certificate 2026 (7 priority subjects)
    "leaving_cert_source",
    "SUBJECTS",
]

# EdcoLearning is conditional on the import succeeding above.
if _edcolearning_imported:
    __all__ += [
        "edcolearning_source",
        "irish_lc_audio_source",
        "languages_lc_audio_source",
        "french_lc_audio_source",
        "german_lc_audio_source",
        "spanish_lc_audio_source",
        "EdcoCredentials",
        "ExamLevel",
        "ExamSubject",
    ]
