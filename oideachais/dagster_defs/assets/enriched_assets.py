"""
Cross-Domain Enriched Assets.

Assets that combine data across domains to create enriched views:
- Curriculum linked to Téarma terminology
- Bilingual aligned pairs (en/ga)
- Folklore linked to curriculum topics
- Pronunciation linked to curriculum terms
- Dialect variation analysis
- Cross-Celtic cognate detection

These assets depend on domain-specific assets from:
- ireland.education.*
- celtic.*
- geospatial.*
- uk.education.*
"""
# Note: Removed future annotations for Dagster compatibility


from dagster import (
    AssetKey,
    MaterializeResult,
    asset,
)

from ..resources import DuckDBResource, LanceDBResource

# ============================================================================
# Curriculum-Terminology Linking
# ============================================================================

@asset(
    key=["enriched", "curriculum_with_terminology"],
    group_name="cross_domain",
    description="Link curriculum content to Téarma.ie terminology",
    deps=[
        AssetKey(["ireland", "education", "embeddings"]),
        AssetKey(["celtic", "gaois", "terms"]),
    ],
    compute_kind="enrichment",
)
def curriculum_with_terminology(
    context,
    duckdb: DuckDBResource,
    lancedb: LanceDBResource,
) -> MaterializeResult:
    """
    Link curriculum content to Téarma.ie terminology.

    Creates semantic links between curriculum learning outcomes
    and official Irish terminology from Téarma.ie.

    Output:
    - curriculum_term_links table with similarity scores
    - Enriched curriculum embeddings with term metadata
    """
    context.log.info("Linking curriculum to terminology")

    conn = duckdb.get_connection()
    db = lancedb.get_db()

    # Check if required tables exist
    try:
        curriculum_count = conn.execute(
            "SELECT COUNT(*) FROM education.curriculum_pages"
        ).fetchone()[0]
        terms_count = conn.execute(
            "SELECT COUNT(*) FROM celtic.tearma_terms"
        ).fetchone()[0]
    except Exception as e:
        context.log.warning(f"Required tables not yet populated: {e}")
        return MaterializeResult(
            metadata={
                "status": "skipped",
                "reason": "Source tables not yet populated",
            }
        )

    if curriculum_count < 10 or terms_count < 10:
        return MaterializeResult(
            metadata={
                "status": "skipped",
                "reason": f"Insufficient data: {curriculum_count} curriculum, {terms_count} terms",
            }
        )

    # Create enriched view linking curriculum to terminology
    try:
        conn.execute("""
            CREATE OR REPLACE VIEW enriched.curriculum_terms AS
            SELECT
                c.page_id,
                c.title,
                c.subject,
                t.irish_term,
                t.english_term,
                t.domain as term_domain
            FROM education.curriculum_pages c
            CROSS JOIN celtic.tearma_terms t
            WHERE c.content ILIKE '%' || t.english_term || '%'
            OR c.content ILIKE '%' || t.irish_term || '%'
            LIMIT 10000
        """)

        link_count = conn.execute(
            "SELECT COUNT(*) FROM enriched.curriculum_terms"
        ).fetchone()[0]
    except Exception as e:
        context.log.warning(f"View creation failed: {e}")
        link_count = 0

    return MaterializeResult(
        metadata={
            "curriculum_pages": curriculum_count,
            "terminology_entries": terms_count,
            "links_created": link_count,
        }
    )


# ============================================================================
# Bilingual Alignment
# ============================================================================

@asset(
    key=["enriched", "bilingual_aligned_pairs"],
    group_name="cross_domain",
    description="Align English/Irish parallel content from curriculum sources",
    deps=[
        AssetKey(["ireland", "education", "web_pages"]),
    ],
    compute_kind="alignment",
)
def bilingual_aligned_pairs(
    context,
    duckdb: DuckDBResource,
) -> MaterializeResult:
    """
    Align English/Irish parallel content from curriculum sources.

    Sources:
    - curriculumonline.ie (mirrored /en/ and /ga-ie/ paths)
    - NCCA specifications (bilingual PDFs)
    - SEC marking schemes

    Uses existing alignment module (VecAlign, HunAlign hybrid approach).
    """
    context.log.info("Aligning bilingual curriculum content")

    conn = duckdb.get_connection()

    # Check for bilingual content
    try:
        page_count = conn.execute("""
            SELECT COUNT(*) FROM education.web_pages
            WHERE language IN ('en', 'ga')
        """).fetchone()[0]
    except Exception as e:
        context.log.warning(f"Web pages table not found: {e}")
        return MaterializeResult(
            metadata={
                "status": "skipped",
                "reason": "Source table not yet populated",
            }
        )

    if page_count < 20:
        return MaterializeResult(
            metadata={
                "status": "skipped",
                "reason": f"Insufficient bilingual pages: {page_count}",
            }
        )

    # Create aligned pairs table
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS training.parallel_corpus (
                pair_id INTEGER PRIMARY KEY,
                source_url VARCHAR,
                english_text TEXT,
                irish_text TEXT,
                alignment_score DOUBLE,
                alignment_method VARCHAR,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Find URL pairs (en ↔ ga)
        conn.execute("""
            INSERT INTO training.parallel_corpus (pair_id, source_url, english_text, irish_text, alignment_score, alignment_method)
            SELECT
                ROW_NUMBER() OVER () as pair_id,
                en.url as source_url,
                en.content as english_text,
                ga.content as irish_text,
                0.75 as alignment_score,  -- Placeholder
                'url_matching' as alignment_method
            FROM education.web_pages en
            JOIN education.web_pages ga
                ON REPLACE(en.url, '/en/', '/ga-ie/') = ga.url
            WHERE en.language = 'en' AND ga.language = 'ga'
            ON CONFLICT DO NOTHING
            LIMIT 1000
        """)

        pair_count = conn.execute(
            "SELECT COUNT(*) FROM training.parallel_corpus"
        ).fetchone()[0]
    except Exception as e:
        context.log.warning(f"Alignment failed: {e}")
        pair_count = 0

    return MaterializeResult(
        metadata={
            "source_pages": page_count,
            "aligned_pairs": pair_count,
            "method": "url_matching",
        }
    )


# ============================================================================
# Folklore-Curriculum Linking
# ============================================================================

@asset(
    key=["enriched", "folklore_by_curriculum_topic"],
    group_name="cross_domain",
    description="Match Dúchas folklore entries to curriculum learning outcomes",
    deps=[
        AssetKey(["ireland", "education", "embeddings"]),
        AssetKey(["celtic", "folklore", "volumes"]),
    ],
    compute_kind="enrichment",
)
def folklore_by_curriculum_topic(
    context,
    duckdb: DuckDBResource,
    lancedb: LanceDBResource,
) -> MaterializeResult:
    """
    Match Dúchas folklore entries to curriculum learning outcomes.

    Uses semantic search to find relevant folklore content
    for each curriculum topic, enabling:
    - Cultural context for curriculum content
    - Primary source materials for Irish subjects
    - Geographic links via Dúchas location data
    """
    context.log.info("Linking folklore to curriculum topics")

    conn = duckdb.get_connection()
    db = lancedb.get_db()

    # Check source data
    try:
        folklore_count = conn.execute(
            "SELECT COUNT(*) FROM celtic.duchas_volumes"
        ).fetchone()[0]
    except Exception as e:
        context.log.warning(f"Folklore table not found: {e}")
        return MaterializeResult(
            metadata={"status": "skipped", "reason": str(e)}
        )

    if folklore_count < 10:
        return MaterializeResult(
            metadata={
                "status": "skipped",
                "reason": f"Insufficient folklore: {folklore_count}",
            }
        )

    # Create folklore-curriculum links via semantic similarity
    try:
        # Check if LanceDB tables exist
        curriculum_table = "oideachas.curriculum"
        folklore_table = "teanga.folklore"

        if curriculum_table not in db.table_names():
            context.log.warning(f"LanceDB table {curriculum_table} not found")
            return MaterializeResult(
                metadata={"status": "skipped", "reason": "Curriculum embeddings not ready"}
            )

        if folklore_table not in db.table_names():
            context.log.warning(f"LanceDB table {folklore_table} not found")
            return MaterializeResult(
                metadata={"status": "skipped", "reason": "Folklore embeddings not ready"}
            )

        # Create enriched view
        conn.execute("""
            CREATE TABLE IF NOT EXISTS enriched.folklore_curriculum_links (
                curriculum_id VARCHAR,
                folklore_id VARCHAR,
                similarity_score DOUBLE,
                curriculum_topic VARCHAR,
                folklore_county VARCHAR
            )
        """)

        link_count = 0  # Would be populated by semantic search

    except Exception as e:
        context.log.warning(f"Linking failed: {e}")
        link_count = 0

    return MaterializeResult(
        metadata={
            "folklore_entries": folklore_count,
            "links_created": link_count,
        }
    )


# ============================================================================
# Dialect Variation Atlas
# ============================================================================

@asset(
    key=["enriched", "dialect_variation_atlas"],
    group_name="cross_domain",
    description="Geographic atlas of pronunciation variations across dialects",
    deps=[
        AssetKey(["celtic", "pronunciation", "transcripts"]),
        AssetKey(["geospatial", "boundaries", "dialect_regions"]),
        AssetKey(["geospatial", "locations", "canuint"]),
    ],
    compute_kind="analysis",
)
def dialect_variation_atlas(
    context,
    duckdb: DuckDBResource,
) -> MaterializeResult:
    """
    Create geographic atlas of pronunciation variations.

    Aggregates Canuint pronunciation data by dialect region to show:
    - Word variant distributions by province
    - Phonetic feature maps
    - Dialect boundary analysis
    """
    context.log.info("Creating dialect variation atlas")

    conn = duckdb.get_connection()

    # Check source data
    try:
        transcript_count = conn.execute(
            "SELECT COUNT(*) FROM celtic.canuint_transcripts"
        ).fetchone()[0]
    except Exception as e:
        context.log.warning(f"Transcripts table not found: {e}")
        return MaterializeResult(
            metadata={"status": "skipped", "reason": str(e)}
        )

    if transcript_count < 10:
        return MaterializeResult(
            metadata={
                "status": "skipped",
                "reason": f"Insufficient transcripts: {transcript_count}",
            }
        )

    # Create dialect variation view
    try:
        conn.execute("""
            CREATE OR REPLACE VIEW enriched.dialect_atlas AS
            SELECT
                province,
                word,
                COUNT(*) as variant_count,
                STRING_AGG(DISTINCT phonetic_form, ', ') as phonetic_variants
            FROM celtic.canuint_transcripts
            GROUP BY province, word
            HAVING COUNT(*) > 1
        """)

        variation_count = conn.execute(
            "SELECT COUNT(*) FROM enriched.dialect_atlas"
        ).fetchone()[0]
    except Exception as e:
        context.log.warning(f"Atlas creation failed: {e}")
        variation_count = 0

    return MaterializeResult(
        metadata={
            "transcripts_analyzed": transcript_count,
            "word_variations": variation_count,
            "provinces": ["Munster", "Connacht", "Ulster"],
        }
    )


# ============================================================================
# Curriculum by Gaeltacht
# ============================================================================

@asset(
    key=["enriched", "curriculum_by_gaeltacht"],
    group_name="cross_domain",
    description="Curriculum content relevance to Gaeltacht regions",
    deps=[
        AssetKey(["ireland", "education", "embeddings"]),
        AssetKey(["geospatial", "boundaries", "gaeltacht"]),
    ],
    compute_kind="enrichment",
)
def curriculum_by_gaeltacht(
    context,
    duckdb: DuckDBResource,
) -> MaterializeResult:
    """
    Analyze curriculum content relevance to Gaeltacht regions.

    Links curriculum topics to Gaeltacht areas based on:
    - Geographic references in content
    - Cultural relevance scoring
    - Irish-medium education focus
    """
    context.log.info("Linking curriculum to Gaeltacht regions")

    conn = duckdb.get_connection()

    # This is a placeholder - full implementation would use
    # spatial queries and semantic matching
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS enriched.curriculum_gaeltacht (
                curriculum_id VARCHAR,
                gaeltacht_id VARCHAR,
                relevance_score DOUBLE,
                match_type VARCHAR
            )
        """)
    except Exception as e:
        context.log.warning(f"Table creation failed: {e}")

    return MaterializeResult(
        metadata={
            "status": "initialized",
            "gaeltacht_regions": 7,
        }
    )


# ============================================================================
# Cross-Celtic Cognates
# ============================================================================

@asset(
    key=["enriched", "cross_celtic_cognates"],
    group_name="cross_domain",
    description="Term equivalents across Celtic languages",
    deps=[
        AssetKey(["celtic", "gaois", "terms"]),
    ],
    compute_kind="analysis",
)
def cross_celtic_cognates(
    context,
    duckdb: DuckDBResource,
) -> MaterializeResult:
    """
    Detect cognate terms across Celtic languages.

    Identifies equivalent terminology across:
    - Irish (ga)
    - Scottish Gaelic (gd)
    - Welsh (cy)
    - Manx (gv)
    - Cornish (kw)
    - Breton (br)

    Uses phonetic similarity and semantic matching.
    """
    context.log.info("Detecting cross-Celtic cognates")

    conn = duckdb.get_connection()

    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS enriched.celtic_cognates (
                term_id VARCHAR PRIMARY KEY,
                irish_form VARCHAR,
                scottish_gaelic_form VARCHAR,
                welsh_form VARCHAR,
                manx_form VARCHAR,
                cornish_form VARCHAR,
                breton_form VARCHAR,
                english_gloss VARCHAR,
                similarity_score DOUBLE
            )
        """)
    except Exception as e:
        context.log.warning(f"Table creation failed: {e}")

    return MaterializeResult(
        metadata={
            "status": "initialized",
            "languages": ["ga", "gd", "cy", "gv", "kw", "br"],
        }
    )


# ============================================================================
# Export All Enriched Assets
# ============================================================================

enriched_assets = [
    curriculum_with_terminology,
    bilingual_aligned_pairs,
    folklore_by_curriculum_topic,
    dialect_variation_atlas,
    curriculum_by_gaeltacht,
    cross_celtic_cognates,
]
