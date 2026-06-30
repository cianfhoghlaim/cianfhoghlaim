"""
Author Archive dlt source package.

Ingest, extract, and index personal-archive trees under `leabharlann/`:

1. `oideachais.dlt_sources.leabharlann.university_of_galway_source` —
   `leabharlann/ollscoil_na_gaillimhe/` (renamed from the old
   `author_cian_deacy_lyons_…/university_of_galway/`).
2. `oideachais.dlt_sources.leabharlann.gemini_deep_research_source` —
   `leabharlann/gemini_deep_research/`.
3. `oideachais.dlt_sources.leabharlann.google_takeout_source` —
   `Takeout/<account_label>/` (per-account, configured via YAML).
4. `oideachais.dlt_sources.leabharlann.leabharlann_books_source` —
   `leabharlann/{gaeilge,aigne}/` with EPUB support + preview pairing.
5. `oideachais.dlt_sources.leabharlann.zotero_source` —
   `leabharlann/zotero/` (real Zotero storage format with arxiv IDs).
6. `oideachais.dlt_sources.leabharlann.takeout_v1_source` —
   `stedding/Takeout/` (single- or multi-account auto-discovery).
7. `oideachais.dlt_sources.leabharlann.email_inbox_source` —
   `/srv/mailcow-exports/*.mbox` (the 4-account email-inbox pipeline).

Reference: openspec/changes/leabharlann-cocoindex-v1/
            (supersedes author-archive-gemini-and-uos-ingestion)
            + openspec/changes/2026-06-29-leabharlann-email-inbox-pipeline/
"""

from ._epub_extractor import EBOOKLIB_AVAILABLE, extract_epub_chapters
from .email_inbox import (
    DEFAULT_MBOX_ROOT,
    build_thread_rows,
    build_threads,
    create_email_inbox_pipeline,
    detect_legal_flag,
    email_inbox_source,
    iter_message_meta,
    normalise_subject,
    year_from_mbox_filename,
)
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
from .leabharlann_books import (
    BOOK_SUBJECTS,
    DEFAULT_LEABHARLANN_ROOT,
    create_leabharlann_books_pipeline,
    leabharlann_books_source,
)
from .previews import find_preview_for, iter_books_with_previews
from .takeout_v1 import (
    DEFAULT_TAKEOUT_ROOT,
    _KNOWN_PRODUCTS,
    _detect_account_label,
    create_takeout_v1_pipeline,
    takeout_v1_source,
)
from .university_of_galway import (
    DEFAULT_UOG_PATH,
    create_uog_pipeline,
    run_uog_ingestion,
    university_of_galway_source,
)
from .zotero import (
    DEFAULT_ZOTERO_ROOT,
    create_zotero_pipeline,
    zotero_source,
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
    # Takeout config (legacy + v1)
    "DEFAULT_TAKEOUT_DOMAINS",
    "TakeoutAccountConfig",
    "TakeoutAccounts",
    "load_takeout_accounts",
    # University of Galway (renamed location)
    "DEFAULT_UOG_PATH",
    "university_of_galway_source",
    "create_uog_pipeline",
    "run_uog_ingestion",
    # Gemini Deep Research (renamed location)
    "DEFAULT_GEMINI_PATH",
    "GEMINI_DOMAINS",
    "gemini_deep_research_source",
    "create_gemini_pipeline",
    "run_gemini_ingestion",
    # Google Takeout (legacy per-account YAML)
    "DEFAULT_ACCOUNTS_PATH",
    "google_takeout_source",
    "create_takeout_pipeline",
    "phase2_oauth_drive_export",
    "phase2_gmail_export",
    # Leabharlann books (new in leabharlann-cocoindex-v1)
    "BOOK_SUBJECTS",
    "DEFAULT_LEABHARLANN_ROOT",
    "leabharlann_books_source",
    "create_leabharlann_books_pipeline",
    # Zotero (new in leabharlann-cocoindex-v1)
    "DEFAULT_ZOTERO_ROOT",
    "zotero_source",
    "create_zotero_pipeline",
    # Takeout v1 (new in leabharlann-cocoindex-v1)
    "DEFAULT_TAKEOUT_ROOT",
    "_KNOWN_PRODUCTS",
    "_detect_account_label",
    "takeout_v1_source",
    "create_takeout_v1_pipeline",
    # Email inbox (new in 2026-06-29-leabharlann-email-inbox-pipeline)
    "DEFAULT_MBOX_ROOT",
    "email_inbox_source",
    "create_email_inbox_pipeline",
    "normalise_subject",
    "detect_legal_flag",
    "iter_message_meta",
    "build_threads",
    "build_thread_rows",
    "year_from_mbox_filename",
    # EPUB + previews helpers
    "EBOOKLIB_AVAILABLE",
    "extract_epub_chapters",
    "find_preview_for",
    "iter_books_with_previews",
]
