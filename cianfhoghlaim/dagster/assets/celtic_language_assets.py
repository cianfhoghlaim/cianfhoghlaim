"""
Celtic Language Assets.

Pipeline for Celtic language corpus from:
- Dúchas: National Folklore Collection (with geolocation)
- Canuint: Irish pronunciation recordings (with dialect regions)
- Téarma: Irish terminology database
- Logainm: Irish placename database (with coordinates)
- Universal Dependencies: Celtic treebanks

Asset Hierarchy:
    celtic.folklore.volumes (Dúchas with location metadata)
    celtic.folklore.schools_xml (Schools Collection with lat/lon)
    celtic.pronunciation.areas (Canuint provinces/areas)
    celtic.pronunciation.recordings
    celtic.pronunciation.transcripts
    celtic.treebank.sentences (Universal Dependencies)
    celtic.gaois.placenames (Logainm with coordinates)
    celtic.gaois.terms (Téarma terminology)
    celtic.embeddings (unified embeddings)

Designed for independent execution via celtic_multipartitions.
"""
# Note: Removed future annotations for Dagster compatibility


from dagster import (
    AssetKey,
    MaterializeResult,
    asset,
)
from dagster_dlt import DagsterDltResource

from ..partitions import (
    dialect_partitions,
    language_partitions,
)
from ..resources import DuckDBResource, LanceDBResource

# ============================================================================
# Dúchas Folklore Assets (with geolocation)
# ============================================================================

@asset(
    key=["celtic", "folklore", "volumes"],
    group_name="celtic_language",
    description="Dúchas National Folklore Collection volumes with location metadata",
    compute_kind="dlt",
)
def duchas_volumes(
    context,
    dlt: DagsterDltResource,
    duckdb: DuckDBResource,
) -> MaterializeResult:
    """
    Ingest Dúchas folklore volumes.

    Location fields preserved:
    - county: County name (e.g., "Cork", "Galway")
    - lat, lon: Coordinates for mapping
    - logainm_id: Link to placename database
    - logainm_url: URL for placename details

    Content types: Stories, customs, beliefs, songs, games.
    """
    context.log.info("Ingesting Dúchas folklore volumes")

    from cianfhoghlaim.dlt.british_isles.ie.culture.duchas import duchas_source

    pipeline = dlt.build_dlt_pipeline(
        pipeline_name="duchas_volumes",
        destination="duckdb",
        dataset_name="celtic",
    )

    source = duchas_source(collection="main")
    load_info = pipeline.run(source)

    row_counts = pipeline.last_trace.last_normalize_info.row_counts if pipeline.last_trace else {}

    return MaterializeResult(
        metadata={
            "collection": "main",
            "volumes_loaded": sum(row_counts.values()),
            "location_fields": ["county", "lat", "lon", "logainm_id", "logainm_url"],
        }
    )


@asset(
    key=["celtic", "folklore", "schools_xml"],
    group_name="celtic_language",
    description="Dúchas Schools Collection with geolocation",
    compute_kind="dlt",
)
def duchas_schools_collection(
    context,
    dlt: DagsterDltResource,
    duckdb: DuckDBResource,
) -> MaterializeResult:
    """
    Ingest Dúchas Schools Collection (Bailiúchán na Scol).

    1930s collection from primary schools with rich location data.

    Location fields:
    - school_name: Original school name
    - county: County of collection
    - townland: Townland name
    - lat, lon: Coordinates
    - logainm_id: Link to placenames
    """
    context.log.info("Ingesting Dúchas Schools Collection")

    from cianfhoghlaim.dlt.british_isles.ie.culture.duchas import duchas_source

    pipeline = dlt.build_dlt_pipeline(
        pipeline_name="duchas_schools",
        destination="duckdb",
        dataset_name="celtic",
    )

    source = duchas_source(collection="schools")
    load_info = pipeline.run(source)

    row_counts = pipeline.last_trace.last_normalize_info.row_counts if pipeline.last_trace else {}

    return MaterializeResult(
        metadata={
            "collection": "schools",
            "pages_loaded": sum(row_counts.values()),
            "location_fields": ["school_name", "county", "townland", "lat", "lon", "logainm_id"],
        }
    )


# ============================================================================
# Canuint Pronunciation Assets (with dialect regions)
# ============================================================================

@asset(
    key=["celtic", "pronunciation", "areas"],
    group_name="celtic_language",
    description="Canuint pronunciation dialect areas with province mapping",
    compute_kind="dlt",
)
def canuint_areas(
    context,
    dlt: DagsterDltResource,
    duckdb: DuckDBResource,
) -> MaterializeResult:
    """
    Ingest Canuint dialect areas.

    Dialect fields:
    - area_id: Unique area identifier
    - area_name: Irish name of area (e.g., "Múscraí", "Cois Fharraige")
    - province: Dialect province (Munster/Connacht/Ulster)

    These areas map to Gaeltacht regions and enable
    geographic analysis of pronunciation variation.
    """
    context.log.info("Ingesting Canuint dialect areas")

    from dlt_sources.ie.culture.canuint import canuint_source

    pipeline = dlt.build_dlt_pipeline(
        pipeline_name="canuint_areas",
        destination="duckdb",
        dataset_name="celtic",
    )

    source = canuint_source(resource="areas")
    load_info = pipeline.run(source)

    row_counts = pipeline.last_trace.last_normalize_info.row_counts if pipeline.last_trace else {}

    return MaterializeResult(
        metadata={
            "areas_loaded": sum(row_counts.values()),
            "dialect_fields": ["area_id", "area_name", "province"],
            "provinces": ["Cúige Mumhan", "Cúige Connacht", "Cúige Uladh"],
        }
    )


@asset(
    key=["celtic", "pronunciation", "recordings"],
    group_name="celtic_language",
    description="Canuint pronunciation audio recordings",
    deps=[AssetKey(["celtic", "pronunciation", "areas"])],
    partitions_def=dialect_partitions,
    compute_kind="dlt",
)
def canuint_recordings(
    context,
    dlt: DagsterDltResource,
    duckdb: DuckDBResource,
) -> MaterializeResult:
    """
    Ingest Canuint pronunciation recordings by dialect.

    Partitioned by dialect region (munster/connacht/ulster/standard).
    Links recordings to areas for geographic analysis.
    """
    dialect = context.partition_key
    context.log.info(f"Ingesting Canuint recordings for dialect: {dialect}")

    from dlt_sources.ie.culture.canuint import canuint_source

    # Map partition key to province filter
    province_map = {
        "munster": "Cúige Mumhan",
        "connacht": "Cúige Connacht",
        "ulster": "Cúige Uladh",
        "standard": "Caighdeán Oifigiúil",
    }
    province = province_map.get(dialect, dialect)

    pipeline = dlt.build_dlt_pipeline(
        pipeline_name=f"canuint_recordings_{dialect}",
        destination="duckdb",
        dataset_name="celtic",
    )

    source = canuint_source(resource="recordings", province_filter=province)
    load_info = pipeline.run(source)

    row_counts = pipeline.last_trace.last_normalize_info.row_counts if pipeline.last_trace else {}

    return MaterializeResult(
        metadata={
            "dialect": dialect,
            "province": province,
            "recordings_loaded": sum(row_counts.values()),
        }
    )


@asset(
    key=["celtic", "pronunciation", "transcripts"],
    group_name="celtic_language",
    description="Canuint pronunciation transcripts with phonetic data",
    deps=[AssetKey(["celtic", "pronunciation", "recordings"])],
    partitions_def=dialect_partitions,
    compute_kind="dlt",
)
def canuint_transcripts(
    context,
    dlt: DagsterDltResource,
    duckdb: DuckDBResource,
) -> MaterializeResult:
    """
    Ingest Canuint transcripts with phonetic transcriptions.

    Links word forms to pronunciations across dialects.
    Enables comparative dialectology analysis.
    """
    dialect = context.partition_key
    context.log.info(f"Ingesting Canuint transcripts for dialect: {dialect}")

    from dlt_sources.ie.culture.canuint import canuint_source

    province_map = {
        "munster": "Cúige Mumhan",
        "connacht": "Cúige Connacht",
        "ulster": "Cúige Uladh",
        "standard": "Caighdeán Oifigiúil",
    }
    province = province_map.get(dialect, dialect)

    pipeline = dlt.build_dlt_pipeline(
        pipeline_name=f"canuint_transcripts_{dialect}",
        destination="duckdb",
        dataset_name="celtic",
    )

    source = canuint_source(resource="transcripts", province_filter=province)
    load_info = pipeline.run(source)

    row_counts = pipeline.last_trace.last_normalize_info.row_counts if pipeline.last_trace else {}

    return MaterializeResult(
        metadata={
            "dialect": dialect,
            "transcripts_loaded": sum(row_counts.values()),
        }
    )


# ============================================================================
# Universal Dependencies Treebank Assets
# ============================================================================

@asset(
    key=["celtic", "treebank", "sentences"],
    group_name="celtic_language",
    description="Universal Dependencies treebank sentences for Celtic languages",
    partitions_def=language_partitions,
    compute_kind="dlt",
)
def ud_treebank_sentences(
    context,
    dlt: DagsterDltResource,
    duckdb: DuckDBResource,
) -> MaterializeResult:
    """
    Ingest Universal Dependencies treebank data.

    Available treebanks:
    - ga: UD_Irish-IDT, UD_Irish-TwittIrish
    - gd: UD_Scottish_Gaelic-ARCOSG
    - cy: UD_Welsh-CCG
    - br: UD_Breton-KEB
    """
    language = context.partition_key
    context.log.info(f"Ingesting UD treebank for language: {language}")

    from cianfhoghlaim.dlt.british_isles.ie.education.universal_dependencies import ud_source

    pipeline = dlt.build_dlt_pipeline(
        pipeline_name=f"ud_treebank_{language}",
        destination="duckdb",
        dataset_name="celtic",
    )

    source = ud_source(language=language)
    load_info = pipeline.run(source)

    row_counts = pipeline.last_trace.last_normalize_info.row_counts if pipeline.last_trace else {}

    return MaterializeResult(
        metadata={
            "language": language,
            "sentences_loaded": sum(row_counts.values()),
        }
    )


# ============================================================================
# Gaois API Assets (Logainm, Téarma)
# ============================================================================

@asset(
    key=["celtic", "gaois", "placenames"],
    group_name="celtic_language",
    description="Logainm Irish placename database with coordinates",
    compute_kind="dlt",
)
def logainm_placenames(
    context,
    dlt: DagsterDltResource,
    duckdb: DuckDBResource,
) -> MaterializeResult:
    """
    Ingest Logainm.ie placename data.

    Location fields:
    - logainm_id: Unique identifier
    - irish_name: Irish form
    - english_name: English form
    - county: County
    - lat, lon: Coordinates (WGS84)
    - category: Place type (townland, parish, etc.)

    Essential for linking folklore and curriculum to geography.
    """
    context.log.info("Ingesting Logainm placenames")

    from dlt_sources.ie.culture.logainm import logainm_source

    pipeline = dlt.build_dlt_pipeline(
        pipeline_name="logainm_placenames",
        destination="duckdb",
        dataset_name="celtic",
    )

    source = logainm_source()
    load_info = pipeline.run(source)

    row_counts = pipeline.last_trace.last_normalize_info.row_counts if pipeline.last_trace else {}

    return MaterializeResult(
        metadata={
            "placenames_loaded": sum(row_counts.values()),
            "location_fields": ["logainm_id", "irish_name", "english_name", "county", "lat", "lon", "category"],
        }
    )


@asset(
    key=["celtic", "gaois", "terms"],
    group_name="celtic_language",
    description="Téarma.ie Irish terminology database",
    compute_kind="dlt",
)
def tearma_terms(
    context,
    dlt: DagsterDltResource,
    duckdb: DuckDBResource,
) -> MaterializeResult:
    """
    Ingest Téarma.ie terminology.

    Fields:
    - term_id: Unique identifier
    - irish_term: Irish form
    - english_term: English equivalent
    - domain: Subject domain (education, science, etc.)
    - definition_ga: Irish definition
    - definition_en: English definition

    Critical for curriculum term alignment.
    """
    context.log.info("Ingesting Téarma terminology")

    from dlt_sources.ie.culture.tearma import tearma_source

    pipeline = dlt.build_dlt_pipeline(
        pipeline_name="tearma_terms",
        destination="duckdb",
        dataset_name="celtic",
    )

    source = tearma_source()
    load_info = pipeline.run(source)

    row_counts = pipeline.last_trace.last_normalize_info.row_counts if pipeline.last_trace else {}

    return MaterializeResult(
        metadata={
            "terms_loaded": sum(row_counts.values()),
            "domains": ["oideachas", "eolaíocht", "teicneolaíocht", "dlí", "eile"],
        }
    )


# ============================================================================
# Celtic Embeddings Asset
# ============================================================================

@asset(
    key=["celtic", "embeddings"],
    group_name="celtic_language",
    description="Unified embeddings for Celtic language content",
    deps=[
        AssetKey(["celtic", "folklore", "volumes"]),
        AssetKey(["celtic", "pronunciation", "transcripts"]),
        AssetKey(["celtic", "treebank", "sentences"]),
        AssetKey(["celtic", "gaois", "terms"]),
    ],
    compute_kind="embedding",
)
def celtic_embeddings(
    context,
    duckdb: DuckDBResource,
    lancedb: LanceDBResource,
) -> MaterializeResult:
    """
    Generate embeddings for Celtic language content.

    Stores in LanceDB with teanga.* namespace:
    - teanga.folklore: Dúchas content
    - teanga.terminology: Téarma terms
    - teanga.pronunciation: Canuint transcripts
    """
    from sentence_transformers import SentenceTransformer

    context.log.info("Generating Celtic language embeddings")

    conn = duckdb.get_connection()
    db = lancedb.get_db()
    model = SentenceTransformer(lancedb.embedding_model)

    total_embedded = 0

    # Embed folklore content
    try:
        query = """
            SELECT
                'folklore' as source,
                title,
                content,
                county,
                lat,
                lon
            FROM celtic.duchas_volumes
            WHERE content IS NOT NULL
            LIMIT 300
        """
        rows = conn.execute(query).fetchall()

        if len(rows) >= 10:
            texts = [f"{row[1]}\n{row[2]}" for row in rows]
            metadata = [{
                "source": row[0],
                "title": row[1],
                "county": row[3],
                "lat": row[4],
                "lon": row[5],
            } for row in rows]

            embeddings = model.encode(texts, batch_size=100, show_progress_bar=True)

            data = [
                {"text": text[:2000], "vector": emb.tolist(), **meta}
                for text, emb, meta in zip(texts, embeddings, metadata)
            ]

            table_name = "teanga.folklore"
            if table_name in db.table_names():
                db.open_table(table_name).add(data)
            else:
                db.create_table(table_name, data)

            total_embedded += len(data)

    except Exception as e:
        context.log.warning(f"Folklore embedding failed: {e}")

    # Embed terminology
    try:
        query = """
            SELECT
                'terminology' as source,
                irish_term,
                english_term,
                domain,
                definition_ga
            FROM celtic.tearma_terms
            WHERE irish_term IS NOT NULL
            LIMIT 500
        """
        rows = conn.execute(query).fetchall()

        if len(rows) >= 10:
            texts = [f"{row[1]} ({row[2]}): {row[4] or ''}" for row in rows]
            metadata = [{
                "source": row[0],
                "irish_term": row[1],
                "english_term": row[2],
                "domain": row[3],
            } for row in rows]

            embeddings = model.encode(texts, batch_size=100, show_progress_bar=True)

            data = [
                {"text": text, "vector": emb.tolist(), **meta}
                for text, emb, meta in zip(texts, embeddings, metadata)
            ]

            table_name = "teanga.terminology"
            if table_name in db.table_names():
                db.open_table(table_name).add(data)
            else:
                db.create_table(table_name, data)

            total_embedded += len(data)

    except Exception as e:
        context.log.warning(f"Terminology embedding failed: {e}")

    return MaterializeResult(
        metadata={
            "total_embedded": total_embedded,
            "tables": ["teanga.folklore", "teanga.terminology"],
        }
    )


# ============================================================================
# Export All Assets
# ============================================================================

celtic_language_assets = [
    duchas_volumes,
    duchas_schools_collection,
    canuint_areas,
    canuint_recordings,
    canuint_transcripts,
    ud_treebank_sentences,
    logainm_placenames,
    tearma_terms,
    celtic_embeddings,
]
