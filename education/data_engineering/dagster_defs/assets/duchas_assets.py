"""
Dúchas.ie Assets - Irish Folklore Handwriting Dataset.

Pipeline for scraping and processing 740K+ handwritten manuscript pages
from the Schools' Collection (1937-1939) for HTR/OCR training.

Asset Hierarchy:
    celtic.duchas.counties       - County seed data
    celtic.duchas.volumes        - Volume discovery per county
    celtic.duchas.pages          - Page scraping (rate-limited)
    celtic.duchas.images         - Image download to R2
    celtic.duchas.transcriptions - Existing transcriptions
    celtic.duchas.embeddings     - Page embeddings for search
    celtic.duchas.htr_training   - HTR training dataset

Partitioned by Irish county for granular execution.

Data Pipeline:
    Browser Scraping → Kafka Events → R2 Storage → LanceDB Embeddings

Critical Constraints:
    - Rate limit: 1 req/sec (duchas.ie policy)
    - Batch embeddings: min 100 (100x performance)
    - Single-threaded DB access (DuckDB constraint)
"""
# Note: Removed future annotations for Dagster compatibility


from dagster import (
    AssetKey,
    DynamicPartitionsDefinition,
    MaterializeResult,
    StaticPartitionsDefinition,
    asset,
    define_asset_job,
    get_dagster_logger,
)

# Import resources from definitions (will be injected)
# from ..definitions import DuckDBResource, LanceDBResource, KafkaResource

logger = get_dagster_logger()

# =============================================================================
# County Partitions
# =============================================================================

# All 32 Irish counties (26 Republic + 6 NI)
IRISH_COUNTIES = [
    # Connacht
    "galway", "mayo", "sligo", "leitrim", "roscommon",
    # Munster
    "cork", "kerry", "clare", "limerick", "tipperary", "waterford",
    # Leinster
    "dublin", "wicklow", "wexford", "carlow", "kilkenny",
    "laois", "offaly", "westmeath", "longford", "meath",
    "louth", "kildare",
    # Ulster (Republic)
    "donegal", "cavan", "monaghan",
    # Ulster (NI) - also in Schools' Collection
    "antrim", "armagh", "derry", "down", "fermanagh", "tyrone",
]

duchas_county_partitions = StaticPartitionsDefinition(IRISH_COUNTIES)
"""Partition by Irish county for granular scraping."""

# Dynamic partitions for volumes (populated during discovery)
duchas_volume_partitions = DynamicPartitionsDefinition(name="duchas_volumes")
"""Dynamic volume partitions populated during county scraping."""


# =============================================================================
# County Seed Data Asset
# =============================================================================

@asset(
    key=["celtic", "duchas", "counties"],
    group_name="duchas_collection",
    description="Seed data for Dúchas.ie Schools' Collection by county",
    compute_kind="config",
)
def duchas_county_seed(context) -> MaterializeResult:
    """
    Initialize county metadata for Dúchas.ie scraping.

    Returns county information including:
    - Estimated page counts
    - URL patterns
    - Collection metadata
    """
    county_metadata = {}

    for county in IRISH_COUNTIES:
        county_metadata[county] = {
            "county_id": county,
            "search_url": f"https://www.duchas.ie/en/cbes?County={county.title()}",
            "collection": "cbes",  # Schools' Collection
            "estimated_pages": None,  # To be discovered
            "province": _get_province(county),
        }

    context.log.info(f"Initialized {len(county_metadata)} counties")

    return MaterializeResult(
        metadata={
            "county_count": len(county_metadata),
            "provinces": {
                "connacht": 5,
                "munster": 6,
                "leinster": 12,
                "ulster": 9,
            },
            "collection": "Schools' Collection (1937-1939)",
        }
    )


def _get_province(county: str) -> str:
    """Map county to province."""
    provinces = {
        "connacht": ["galway", "mayo", "sligo", "leitrim", "roscommon"],
        "munster": ["cork", "kerry", "clare", "limerick", "tipperary", "waterford"],
        "leinster": ["dublin", "wicklow", "wexford", "carlow", "kilkenny",
                     "laois", "offaly", "westmeath", "longford", "meath",
                     "louth", "kildare"],
        "ulster": ["donegal", "cavan", "monaghan", "antrim", "armagh",
                   "derry", "down", "fermanagh", "tyrone"],
    }
    for province, counties in provinces.items():
        if county in counties:
            return province
    return "unknown"


# =============================================================================
# Volume Discovery Asset
# =============================================================================

@asset(
    key=["celtic", "duchas", "volumes"],
    group_name="duchas_collection",
    description="Discover manuscript volumes per county",
    deps=[AssetKey(["celtic", "duchas", "counties"])],
    partitions_def=duchas_county_partitions,
    compute_kind="browser",
)
async def duchas_volume_discovery(
    context,
) -> MaterializeResult:
    """
    Discover all volumes for a county from Dúchas.ie.

    Uses browser automation to:
    1. Navigate to county search page
    2. Extract volume IDs and metadata
    3. Register dynamic partitions for page scraping

    Rate limited: 1 req/sec
    """
    county = context.partition_key
    context.log.info(f"Discovering volumes for county: {county}")

    # Import scraper (lazy to avoid circular imports)
    from sruth.browser.tools.duchas_scraper import DuchasScraper

    scraper = DuchasScraper(rate_limit=1.0)

    # Search for pages in county
    page_ids = await scraper.search_county(county, max_results=1000)

    # Extract unique volume IDs from page IDs
    volume_ids = set()
    for page_id in page_ids:
        # Volume ID is typically the prefix of page ID
        parts = page_id.split("/")
        if len(parts) >= 2:
            volume_ids.add(parts[0])

    context.log.info(f"Found {len(volume_ids)} volumes, {len(page_ids)} pages for {county}")

    # Register dynamic partitions for volumes
    for vol_id in volume_ids:
        try:
            context.instance.add_dynamic_partitions(
                partitions_def_name="duchas_volumes",
                partition_keys=[f"{county}_{vol_id}"],
            )
        except Exception as e:
            context.log.warning(f"Failed to add partition {vol_id}: {e}")

    return MaterializeResult(
        metadata={
            "county": county,
            "volume_count": len(volume_ids),
            "page_count": len(page_ids),
            "sample_volumes": list(volume_ids)[:10],
        }
    )


# =============================================================================
# Page Scraping Asset
# =============================================================================

@asset(
    key=["celtic", "duchas", "pages"],
    group_name="duchas_collection",
    description="Scraped manuscript pages with metadata",
    deps=[AssetKey(["celtic", "duchas", "volumes"])],
    partitions_def=duchas_county_partitions,
    compute_kind="browser",
)
async def duchas_pages(
    context,
) -> MaterializeResult:
    """
    Scrape manuscript pages for a county.

    For each page:
    1. Extract metadata (school, collector, topic)
    2. Get image URL
    3. Extract existing transcription (if any)
    4. Produce Kafka event

    Rate limited: 1 req/sec (~86K pages/day max)
    """
    county = context.partition_key
    context.log.info(f"Scraping pages for county: {county}")

    from sruth.browser.tools.duchas_scraper import (
        scrape_duchas_collection,
    )

    # Use Blaxel for bulk scraping if available, else local
    try:
        from sruth.browser.backends.cloud.blaxel_backend import BlaxelBackend
        backend = BlaxelBackend()
        if backend.is_configured:
            context.log.info("Using Blaxel cloud backend for bulk scraping")
    except ImportError:
        context.log.info("Using local browser backend")

    # Scrape pages with Kafka event production
    result = await scrape_duchas_collection(
        county=county,
        max_pages=500,  # Limit per run to avoid timeout
        produce_to_kafka=True,
    )

    scraped = result.get("scraped_count", 0)
    transcribed = result.get("transcribed_count", 0)
    errors = result.get("error_count", 0)

    context.log.info(
        f"County {county}: scraped {scraped} pages, "
        f"{transcribed} transcribed, {errors} errors"
    )

    return MaterializeResult(
        metadata={
            "county": county,
            "pages_scraped": scraped,
            "pages_transcribed": transcribed,
            "errors": errors,
            "transcription_rate": f"{(transcribed/scraped*100):.1f}%" if scraped > 0 else "0%",
        }
    )


# =============================================================================
# Image Download Asset
# =============================================================================

@asset(
    key=["celtic", "duchas", "images"],
    group_name="duchas_collection",
    description="Downloaded manuscript images stored in R2",
    deps=[AssetKey(["celtic", "duchas", "pages"])],
    partitions_def=duchas_county_partitions,
    compute_kind="storage",
)
async def duchas_images(
    context,
) -> MaterializeResult:
    """
    Download manuscript images for HTR training.

    Images are stored in Cloudflare R2:
    - Path: r2://duchas/images/{county}/{page_id}_{hash}.jpg
    - Original resolution preserved
    - Deduplication via content hash
    """
    county = context.partition_key
    context.log.info(f"Downloading images for county: {county}")


    # In production, this would:
    # 1. Read page metadata from DuckDB/Kafka
    # 2. Download images in parallel (with rate limiting)
    # 3. Store to R2 with proper naming

    # Placeholder for actual implementation
    downloaded = 0
    total_bytes = 0

    context.log.info(f"Downloaded {downloaded} images ({total_bytes} bytes)")

    return MaterializeResult(
        metadata={
            "county": county,
            "images_downloaded": downloaded,
            "total_bytes": total_bytes,
            "storage_path": f"r2://duchas/images/{county}/",
        }
    )


# =============================================================================
# Transcription Extraction Asset
# =============================================================================

@asset(
    key=["celtic", "duchas", "transcriptions"],
    group_name="duchas_collection",
    description="Extracted existing transcriptions (ground truth for HTR)",
    deps=[AssetKey(["celtic", "duchas", "pages"])],
    partitions_def=duchas_county_partitions,
    compute_kind="extraction",
)
async def duchas_transcriptions(
    context,
) -> MaterializeResult:
    """
    Extract existing transcriptions as HTR ground truth.

    Transcriptions include:
    - Original Irish text
    - Collector notes
    - Topic classification
    - Alignment with image regions
    """
    county = context.partition_key
    context.log.info(f"Extracting transcriptions for county: {county}")

    # In production, this would:
    # 1. Read pages with transcriptions from DuckDB
    # 2. Clean and normalize text
    # 3. Create image-text pairs for HTR training

    transcribed = 0
    word_count = 0

    return MaterializeResult(
        metadata={
            "county": county,
            "transcriptions_extracted": transcribed,
            "total_words": word_count,
            "avg_words_per_page": word_count / max(transcribed, 1),
        }
    )


# =============================================================================
# Embedding Asset
# =============================================================================

@asset(
    key=["celtic", "duchas", "embeddings"],
    group_name="duchas_collection",
    description="Vector embeddings for semantic search",
    deps=[AssetKey(["celtic", "duchas", "transcriptions"])],
    partitions_def=duchas_county_partitions,
    compute_kind="embedding",
)
async def duchas_embeddings(
    context,
) -> MaterializeResult:
    """
    Generate embeddings for transcribed pages.

    Uses batch embedding with minimum 100 texts for performance.
    Stores in LanceDB Cloud for semantic search.

    Critical: Batch size >= 100 (100x performance difference)
    """
    county = context.partition_key
    context.log.info(f"Generating embeddings for county: {county}")

    from storage.lancedb_cloud import (
        LanceDBCloudClient,
    )

    client = LanceDBCloudClient()

    # In production, this would:
    # 1. Read transcriptions from DuckDB
    # 2. Batch into groups of 100+
    # 3. Generate embeddings via BGE-M3 or similar
    # 4. Store in LanceDB with metadata

    embedded = 0

    return MaterializeResult(
        metadata={
            "county": county,
            "pages_embedded": embedded,
            "lancedb_table": "duchas_pages",
        }
    )


# =============================================================================
# HTR Training Dataset Asset
# =============================================================================

@asset(
    key=["celtic", "duchas", "htr_dataset"],
    group_name="duchas_collection",
    description="HTR training dataset (image-text pairs)",
    deps=[
        AssetKey(["celtic", "duchas", "images"]),
        AssetKey(["celtic", "duchas", "transcriptions"]),
    ],
    compute_kind="ml_data",
)
async def duchas_htr_dataset(
    context,
) -> MaterializeResult:
    """
    Generate HTR training dataset from Dúchas.ie data.

    Dataset format (PyLaia-compatible):
    - images/: Line-level image crops
    - train.txt: Training image paths + transcriptions
    - val.txt: Validation split
    - test.txt: Test split

    Target: 50K+ training pairs for Irish historical handwriting
    """
    context.log.info("Generating HTR training dataset")

    # In production, this would:
    # 1. Aggregate data from all county partitions
    # 2. Segment pages into line images
    # 3. Create train/val/test splits
    # 4. Export in PyLaia format

    train_pairs = 0
    val_pairs = 0
    test_pairs = 0

    return MaterializeResult(
        metadata={
            "train_pairs": train_pairs,
            "val_pairs": val_pairs,
            "test_pairs": test_pairs,
            "total_pairs": train_pairs + val_pairs + test_pairs,
            "format": "pylaia",
            "output_path": "r2://duchas/htr_dataset/",
        }
    )


# =============================================================================
# Asset Collections and Jobs
# =============================================================================

duchas_assets = [
    duchas_county_seed,
    duchas_volume_discovery,
    duchas_pages,
    duchas_images,
    duchas_transcriptions,
    duchas_embeddings,
    duchas_htr_dataset,
]

# Job for scraping a single county
duchas_county_job = define_asset_job(
    name="duchas_county_scrape",
    selection=[
        "celtic/duchas/volumes",
        "celtic/duchas/pages",
    ],
    description="Scrape Dúchas.ie pages for a single county",
)

# Job for full pipeline
duchas_full_pipeline_job = define_asset_job(
    name="duchas_full_pipeline",
    selection="celtic/duchas/*",
    description="Full Dúchas.ie scraping and processing pipeline",
)
