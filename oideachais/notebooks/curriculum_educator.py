"""
Curriculum Educator - Interactive deep-dive into the Oideachais Data Pipeline.

This Marimo notebook explores the end-to-end flow from web scraping 
to vector databases, specifically focusing on the Senior Cycle curriculum.

Tools demonstrated:
- Dagster (Orchestration)
- DLT (Extraction & Loading)
- Firecrawl & Stagehand (Web scraping & browser automation)
- DuckLake & DuckDB (Storage & local analytics)
- CocoIndex (Transformations & embeddings)
- LanceDB (Vector Search)
"""

import marimo

__generated_with = "0.10.14"
app = marimo.App(width="medium")

@app.cell
def _():
    import os
    import marimo as mo
    
    mo.md("""
    # Oideachais Pipeline: From Syllabus to Vector Space
    
    Welcome to the interactive educator notebook! This guide traces the journey of Irish Senior Cycle subjects 
    from raw web pages on NCCA, CurriculumOnline, and Examinations.ie, all the way to structured, searchable 
    embeddings in a vector database.
    
    ### The Modern Data Stack
    
    Our architecture uses a modern, local-first but production-ready stack:
    1. **Extraction (DLT + Firecrawl/Stagehand):** We crawl the curriculum sites and parse the content. Firecrawl v2 handles standard web pages (with automatic markdown conversion and link extraction), while Stagehand automates complex interactions like downloading exam papers from dropdowns.
    2. **Orchestration (Dagster):** Manages concurrent, partitioned runs to avoid rate limits while ensuring robust retries.
    3. **Storage (DuckLake):** A lightweight Lakehouse separating compute (DuckDB) from storage (S3/R2) and metadata (Postgres/PlanetScale).
    4. **Transformation (CocoIndex):** Real-time, incremental processing to chunk documents and generate LLM embeddings.
    5. **Retrieval (LanceDB):** Embedded vector storage utilizing HNSW indexing for hybrid text/vector search.
    """)
    return mo, os

@app.cell
def _(mo, os):
    # Pipeline Configuration UI
    mo.md("## 1. Pipeline Configuration")
    
    env_dropdown = mo.ui.dropdown(
        options=["local", "production"],
        value="local",
        label="DuckLake Environment",
    )
    
    senior_cycle_subjects = [
        "english", "mathematics", "gaeilge", "biology", "geography", 
        "history", "german", "business", "chemistry"
    ]
    
    subject_selector = mo.ui.multiselect(
        options=senior_cycle_subjects,
        value=["biology", "chemistry"],
        label="Target Subjects"
    )
    
    mo.hstack([
        env_dropdown,
        subject_selector
    ], justify="start", gap=1.0)
    return env_dropdown, senior_cycle_subjects, subject_selector

@app.cell
def _(env_dropdown, mo, os, subject_selector):
    # Apply environment and display config
    os.environ["DLT_ENVIRONMENT"] = env_dropdown.value
    
    mo.md(f"""
    **Current Configuration:**
    - **Environment:** `{env_dropdown.value}` (Routes DLT outputs to local S3/Postgres vs Cloudflare R2/PlanetScale).
    - **Selected Subjects:** {', '.join([f'`{s}`' for s in subject_selector.value])}
    """)
    return

@app.cell
def _(mo):
    mo.md("""
    ## 2. Orchestration with Dagster
    
    To process the entire Irish curriculum without triggering API rate limits on Firecrawl or the SEC website, we use **Dagster MultiPartitions**.
    
    Instead of one massive run, we partition by `subject` and `language`.
    
    ```python
    # dagster_defs/assets/ireland/curriculum_dlt_assets.py
    
    # 1. Define the dimensions of our data
    senior_cycle_partition = MultiPartitionsDefinition({
        "subject": StaticPartitionsDefinition(["biology", "chemistry", "mathematics", ...]),
        "language": StaticPartitionsDefinition(["en", "ga"]),
    })
    
    # 2. Assign partition to the asset and limit concurrency
    @dg.asset(
        partitions_def=senior_cycle_partition,
        op_tags={"dagster/concurrency_key": "curriculum_senior_cycle"}, # Prevents Firecrawl rate limits!
    )
    def senior_cycle_asset(context):
        partition_key_str = context.partition_key # e.g., "en|biology"
        ...
    ```
    """)
    return

@app.cell
def _(mo):
    mo.md("""
    ## 3. How Dagster Routes to DuckDB / DuckLake
    
    Before data is extracted, Dagster decides *where* the data should land. In `curriculum_dlt_assets.py`, we dynamically route the DLT pipeline output based on the environment:
    
    ```python
    # 1. Check environment toggle
    use_ducklake = os.environ.get("USE_DUCKLAKE", "true").lower() == "true"
    
    if use_ducklake:
        # Resolves to a PostgreSQL catalog + S3/R2 storage (True Lakehouse)
        destination = get_dlt_destination()
    else:
        # Fallback: Resolves to a local .duckdb file
        destination = get_duckdb_fallback_destination(
            str(DLT_PIPELINES_DIR / DLT_PIPELINE_NAME / f"{DLT_DATASET_NAME}.duckdb")
        )
        
    # 2. Configure the DLT pipeline
    dlt_pipeline = dlt.pipeline(
        pipeline_name="curriculum_unified",
        destination=destination,
        dataset_name="curriculum",
    )
    
    # 3. Execute with safety
    # We use a serial executor for DuckDB safety to avoid concurrent write locks!
    load_info = safe_dlt_run(dlt_pipeline, source)
    ```
    
    This seamless routing means developers can test locally on a simple `.duckdb` file, while production leverages the scalable, multi-user DuckLake architecture with Postgres/PlanetScale.
    """)
    return

@app.cell
def _(mo):
    mo.md("""
    ## 4. Extraction with DLT and Firecrawl v2
    
    DLT (Data Load Tool) dynamically creates table schemas based on the data we `yield`. We have a central source function `curriculum_source()` that combines multiple web sources.
    
    ```python
    # oideachais/data_platform/dlt_sources/ireland/curriculum_source.py
    
    @dlt.resource(
        name="curriculum_pages",
        write_disposition="merge",           # Idempotent: only inserts/updates, never duplicates
        primary_key=["content_hash"],        # Cross-source deduplication key
    )
    def curriculum_pages() -> Iterator[dict]:
        # Using Firecrawl v2 API patterns
        scrape_opts = ScrapeOptions(formats=["markdown", "links"], onlyMainContent=True)
        
        result = app.crawl(
            url="https://www.curriculumonline.ie/Senior-cycle/Senior-Cycle-Subjects/Biology/",
            limit=50,
            scrape_options=scrape_opts
        )
        
        for page in result.data:
            yield {
                "url": page.metadata["sourceURL"],
                "markdown": page.markdown,
                "content_hash": hashlib.sha256(page.markdown.encode()).hexdigest(),
                "subject": "biology"
            }
    ```
    
    Notice `write_disposition="merge"`: This ensures that if we run the pipeline weekly, we don't duplicate data. We only update rows where the `content_hash` changes.
    """)
    return

@app.cell
def _(mo):
    mo.md("""
    ## 5. The DuckLake Architecture
    
    Once DLT extracts the data, it loads it into **DuckLake**. 
    
    DuckLake solves a massive problem: it gives us a lightweight data lakehouse without needing Spark or a heavy Hive Metastore.
    - **Compute:** Fast, local, in-process analytics using `DuckDB`.
    - **Storage:** Cheap, decoupled storage using `Parquet` files on `S3` or Cloudflare `R2`.
    - **Metadata:** ACID compliance and multi-user concurrency using a `PostgreSQL` catalog.
    """)
    return

@app.cell
def _(env_dropdown, mo, subject_selector):
    # Interactive Query UI
    query_text = f"""
    -- Querying the DuckLake Catalog
    SELECT 
        subject, 
        COUNT(*) as pages_crawled, 
        MIN(crawled_at) as first_crawl
    FROM curriculum.curriculum_pages 
    WHERE subject IN ({', '.join([f"'{s}'" for s in subject_selector.value])})
    GROUP BY subject;
    """
    
    sql_area = mo.ui.text_area(value=query_text.strip(), rows=6, full_width=True, label="Test Query")
    run_query = mo.ui.run_button(label="Execute against DuckLake")
    
    mo.vstack([
        mo.md("### Query the Lakehouse"),
        sql_area,
        run_query
    ])
    return run_query, sql_area

@app.cell
def _(mo, run_query, sql_area):
    import dlt
    import pandas as pd
    import os
    import sys
    from pathlib import Path
    
    # Add project root to path so we can import our modules safely
    project_root = Path(__file__).parent.parent.parent if "__file__" in globals() else Path().absolute().parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    from oideachais.data_platform.dlt_utils import get_duckdb_fallback_destination, get_dlt_destination
    
    mo.stop(not run_query.value, mo.md("*Click 'Execute' to run the SQL query against the active DuckLake environment.*"))
    
    output_ui = None
    try:
        # Defaulting to false so the tutorial runs without needing Docker Postgres
        use_ducklake = os.environ.get("USE_DUCKLAKE", "false").lower() == "true"
        
        if use_ducklake:
            destination = get_dlt_destination()
        else:
            # Match the exact local dev duckdb path used by the curriculum_dlt_assets!
            dlt_dir = project_root / "oideachais/data_platform/.dlt"
            db_path = str(dlt_dir / "curriculum_unified" / "curriculum_unified.duckdb")
            destination = get_duckdb_fallback_destination(db_path)
            
        # We use our built-in factory to guarantee we use the same DuckDB/Postgres destination as the Dagster assets
        pipeline = dlt.pipeline(
            pipeline_name="curriculum_unified", 
            dataset_name="curriculum",
            destination=destination
        )
        
        with pipeline.sql_client() as client:
            with client.execute_query(sql_area.value) as cursor:
                columns = [col[0] for col in cursor.description] if cursor.description else []
                rows = cursor.fetchall()
                
        if rows:
            df = pd.DataFrame(rows, columns=columns)
            output_ui = mo.ui.table(df)
        else:
            output_ui = mo.md("*No results found. (The query ran successfully, but returned 0 rows)*")
            
    except Exception as e:
        # Format the exception beautifully
        output_ui = mo.callout(mo.md(f"**Execution Error:**\n\n```text\n{e}\n```\n\n*(Have you run the `dagster dev` pipeline to generate the `curriculum_unified` dataset yet?)*"), kind="danger")
        
    output_ui
    return dlt, pd, output_ui

@app.cell
def _(mo):
    mo.md("""
    ## 6. Stagehand: Browser Automation for Exam Papers
    
    While Firecrawl handles standard sites, downloading past papers from the SEC (`examinations.ie`) requires interacting with dropdowns. We use **Stagehand** via Browserbase for this.
    
    ```python
    # Stagehand extraction logic
    from sruth_browser.tools.examinations_scraper import scrape_exam_materials_sync
    
    # We yield metadata to DLT, which creates a `curriculum_pdfs` table
    materials = scrape_exam_materials_sync(
        subject="biology",
        years=[2023, 2024],
        level="leaving_certificate"
    )
    
    # Later, our pdf_downloader.py queries DuckLake for pending PDFs and safely downloads them:
    # SELECT url FROM curriculum_pdfs WHERE subject = 'biology'
    ```
    """)
    return

@app.cell
def _(mo):
    mo.md("""
    ## 7. CocoIndex: Incremental LLM Transformations
    
    Now that our Lakehouse holds clean Markdown and downloaded PDFs, we need to convert them into vector embeddings for RAG. **CocoIndex** is our transformation engine.
    
    CocoIndex is incredible because it operates **incrementally**. It tracks which rows in DuckLake/Postgres have changed and only processes the new ones.
    
    ### Example CocoIndex Flow
    
    Notice how CocoIndex operates strictly on row fields via `.transform()`. We do not mutate existing fields or use intermediate variables.
    
    ```python
    import cocoindex
    
    @cocoindex.flow_def(name="SeniorCycleEmbeddings")
    def embed_curriculum(flow_builder: cocoindex.FlowBuilder, data_scope: cocoindex.DataScope):
        
        # 1. Source: Read from DuckLake Postgres Catalog
        data_scope["pages"] = flow_builder.add_source(
            cocoindex.sources.Postgres(
                connection=...,
                query="SELECT content_hash, subject, markdown FROM curriculum.curriculum_pages"
            )
        )
        
        target = data_scope.add_collector()
        
        # 2. Iterate rows
        with data_scope["pages"].row() as page:
        
            # 3. Transform: Chunk the markdown
            page["chunks"] = page["markdown"].transform(
                cocoindex.functions.SplitRecursively(
                    language="markdown", 
                    chunk_size=1500
                )
            )
            
            # 4. Nested iteration over the generated chunks
            with page["chunks"].row() as chunk:
            
                # 5. Transform: LLM Embeddings (via OpenAI/Voyage API)
                chunk["vector"] = chunk["text"].transform(
                    cocoindex.functions.EmbedText(
                        api_type=cocoindex.LlmApiType.OPENAI,
                        model="text-embedding-3-small"
                    )
                )
                
                # Collect the final results
                target.collect(
                    id=cocoindex.GeneratedField.UUID,
                    subject=page["subject"],
                    content_hash=page["content_hash"],
                    text=chunk["text"],
                    vector=chunk["vector"]
                )
                
        # 6. Target: Export to LanceDB
        target.export(
            "lancedb_export",
            cocoindex.targets.LanceDB(uri="s3://lancedb/curriculum", table_name="vectors"),
            primary_key_fields=["id"]
        )
    ```
    """)
    return

@app.cell
def _(mo):
    mo.md("""
    ## 8. LanceDB: Vector Retrieval
    
    Finally, CocoIndex writes the embeddings directly to **LanceDB**. 
    
    Why LanceDB?
    - **Embedded:** Runs in process.
    - **Multimodal:** Supports text, images, and vectors in one place.
    - **HNSW Indexing:** High-speed approximate nearest neighbor search.
    - **Hybrid Search:** Mixes semantic search with keyword filtering.
    
    ```python
    import lancedb
    
    db = lancedb.connect("s3://lancedb/curriculum")
    table = db.open_table("vectors")
    
    # Create Full-Text Search index
    table.create_fts_index("text")
    
    # Hybrid search for Biology queries
    results = (table.search("mitosis cellular division", query_type="hybrid")
              .where("subject = 'biology'")
              .limit(5)
              .rerank(method="rrf")
              .to_pandas())
    ```
    
    And just like that, the Irish curriculum has been fully ingested, processed, embedded, and is ready to power our AI agents!
    """)
    return

if __name__ == "__main__":
    app.run()
