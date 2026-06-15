"""
Author Archive dlt source package.

Ingest, extract, and index three personal-archive trees:

1. `oideachais.dlt_sources.author_archive.university_of_galway_source` —
   `author_cian_deacy_lyons_mac_an_déisigh_uí_liatháin/university_of_galway/`
2. `oideachais.dlt_sources.author_archive.gemini_deep_research_source` —
   `author_cian_deacy_lyons_mac_an_déisigh_uí_liatháin/gemini_deep_research/`
3. `oideachais.dlt_sources.author_archive.google_takeout_source` —
   one or more `Takeout/<account_label>/` directories, configured via
   `author_archive_accounts.yaml` (see `config.example.yaml`).

Reference: openspec/changes/author-archive-gemini-and-uos-ingestion/
"""

from ._scanner import (
    DEFAULT_FILE_TYPE_EXTENSIONS,
    DEFAULT_SKIP_PATTERNS,
    FileHashTracker,
    PathGrammar,
    compute_file_hash,
    detect_domain,
    detect_language,
    detect_subject,
    extract_content,
    extract_course_code,
    get_document_metadata,
    get_file_type,
    requires_handwriting_ocr,
    scan_directory,
    should_skip_file,
)
from ._takeout_paths import (
    DEFAULT_TAKEOUT_DOMAINS,
    TakeoutAccountConfig,
    TakeoutAccounts,
    load_takeout_accounts,
)
from .gemini_deep_research import (
    DEFAULT_GEMINI_PATH,
    GEMINI_DOMAINS,
    create_gemini_pipeline,
    gemini_deep_research_source,
    run_gemini_ingestion,
)
from .google_takeout import (
    DEFAULT_ACCOUNTS_PATH,
    create_takeout_pipeline,
    google_takeout_source,
    phase2_gmail_export,
    phase2_oauth_drive_export,
)
from .university_of_galway import (
    DEFAULT_UOG_PATH,
    create_uog_pipeline,
    run_uog_ingestion,
    university_of_galway_source,
)

__all__ = [
    # Scanner
    "DEFAULT_FILE_TYPE_EXTENSIONS",
    "DEFAULT_SKIP_PATTERNS",
    "PathGrammar",
    "FileHashTracker",
    "compute_file_hash",
    "get_file_type",
    "extract_course_code",
    "detect_subject",
    "detect_domain",
    "requires_handwriting_ocr",
    "should_skip_file",
    "detect_language",
    "get_document_metadata",
    "extract_content",
    "scan_directory",
    # Takeout config
    "DEFAULT_TAKEOUT_DOMAINS",
    "TakeoutAccountConfig",
    "TakeoutAccounts",
    "load_takeout_accounts",
    # University of Galway
    "DEFAULT_UOG_PATH",
    "university_of_galway_source",
    "create_uog_pipeline",
    "run_uog_ingestion",
    # Gemini Deep Research
    "DEFAULT_GEMINI_PATH",
    "GEMINI_DOMAINS",
    "gemini_deep_research_source",
    "create_gemini_pipeline",
    "run_gemini_ingestion",
    # Google Takeout
    "DEFAULT_ACCOUNTS_PATH",
    "google_takeout_source",
    "create_takeout_pipeline",
    "phase2_oauth_drive_export",
    "phase2_gmail_export",
]
