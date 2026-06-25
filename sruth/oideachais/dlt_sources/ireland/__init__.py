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
from .primary import (
    PRIMARY_AREAS,
    PRIMARY_CACHE_DIR,
    PRIMARY_SOURCE_URLS,
    create_ireland_primary_pipeline,
    ireland_primary_source,
    primary_curriculum_areas,
    primary_learning_outcomes,
    primary_specifications,
    primary_strands,
)
from .junior_cycle import (
    JC_CACHE_DIR,
    JC_SHORT_COURSES,
    JC_SOURCE_URLS,
    JC_SUBJECTS,
    cba_tasks,
    create_ireland_junior_cycle_pipeline,
    ireland_junior_cycle_source,
    jc_short_courses,
    jc_specifications,
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
    # Primary curriculum (12 NCCA curriculum areas)
    "PRIMARY_AREAS",
    "PRIMARY_CACHE_DIR",
    "PRIMARY_SOURCE_URLS",
    "ireland_primary_source",
    "create_ireland_primary_pipeline",
    "primary_specifications",
    "primary_curriculum_areas",
    "primary_strands",
    "primary_learning_outcomes",
    # Junior Cycle curriculum (18 subjects + 16 short courses)
    "JC_CACHE_DIR",
    "JC_SUBJECTS",
    "JC_SHORT_COURSES",
    "JC_SOURCE_URLS",
    "ireland_junior_cycle_source",
    "create_ireland_junior_cycle_pipeline",
    "jc_specifications",
    "jc_short_courses",
    "cba_tasks",
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
