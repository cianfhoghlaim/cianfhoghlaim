"""Browser automation tools for oideachais (education) domain.

Domain-specific scrapers for:
- curriculumonline.ie (NCCA curriculum specifications)
- examinations.ie (SEC exam papers and reports)
- duchas.ie (Irish folklore archive)
- canuint.ie (Irish pronunciation database)
"""

from .ncca_scraper import NCCAScraper

__all__ = ["NCCAScraper"]
