"""Label Scrapers.

Firecrawl-based scrapers for extracting artist data from record label websites.
Extracts releases, artwork, and profile information.

Supported Labels:
    - Monstercat (monstercat.com)
    - Lemongrass Music (lemongrassmusic.de)
    - Fokuz Recordings (fokuzrecordings.com)
    - Immersed (immersedrec.com)
    - Offworld Recordings (offworldrecordings.com)
    - Soul Deep Recordings (souldeeprecordings.com)

Usage:
    from pipelines.labels import label_source, scrape_all_labels

    # Run DLT pipeline
    source = label_source(artist_slug="aleyum")
    pipeline.run(source)

    # Or scrape directly
    releases = await scrape_all_labels("aleyum")
"""

from pipelines.labels.scraper import (
    LabelRelease,
    LabelProfile,
    LabelScraper,
    label_source,
    scrape_label,
    scrape_all_labels,
    run_labels_pipeline,
)

__all__ = [
    "LabelRelease",
    "LabelProfile",
    "LabelScraper",
    "label_source",
    "scrape_label",
    "scrape_all_labels",
    "run_labels_pipeline",
]
