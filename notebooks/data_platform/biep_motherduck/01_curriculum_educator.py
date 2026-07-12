# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo>=0.13.0",
#     "duckdb>=1.0",
#     "pandas>=2.0",
# ]
# ///
"""Curriculum Educator — interactive deep-dive into the BIEP (British-Isles
Education pipeline).

Traces the 6-stage journey of the 6 LC subjects (mathematics, applied
mathematics, english, gaeilge, biology, chemistry) + gov.ie circulars
from raw NCCA / SEC / curriculumonline.ie pages all the way to typed
BGE-M3 embeddings in LanceDB.

Tools demonstrated:

- DLT (Extraction & Loading) via the v4 ``cianfhoghlaim.dlt.british_isles.ireland.education.*``
  registry.
- Dagster (Orchestration) with MultiPartitions(subject, language).
- DuckLake + DuckDB (Storage & local analytics) at ``md:oideachais``.
- CocoIndex v1 (Transformations & BGE-M3 embeddings).
- LanceDB (Vector Search via ``lance_scan('s3://...')``).

Query path: ``mo.sql(engine=md:oideachais)`` so the notebook executes
end-to-end against the shared MotherDuck + DuckLake lakehouse.
"""
from __future__ import annotations

import marimo

__generated_with = "0.23.8"
app = marimo.App(width="medium")


@app.cell
def _():
    import os
    import marimo as mo
    import duckdb
import ibis  # ibis-first entrypoint (per wire-biep-notebooks-to-lakehouse change)

    mo.md(
        """
        # BIEP — From Syllabus to Vector Space

        Welcome to the interactive educator notebook! This guide traces the journey
        of the **6 LC subjects** (mathematics, applied_mathematics, english,
        gaeilge, biology, chemistry) from raw NCCA / SEC / curriculumonline.ie
        pages all the way to typed BGE-M3 embeddings in LanceDB.

        ### The Modern Data Stack

        Our architecture is local-first but production-ready:

        1. **Extraction (DLT + Firecrawl/Stagehand)** — crawl the curriculum sites
           and parse the content. Firecrawl v2 handles standard web pages
           (markdown + link extraction); Stagehand automates complex interactions
           like downloading SEC exam papers from dropdowns.
        2. **Orchestration (Dagster)** — concurrent, partitioned runs to avoid
           rate limits while ensuring robust retries.
        3. **Storage (DuckLake)** — lightweight lakehouse: DuckDB compute +
           Garage S3 storage + PostgreSQL catalog metadata.
        4. **Transformation (CocoIndex v1)** — incremental BGE-M3 chunking +
           embedding into LanceDB.
        5. **Retrieval (LanceDB)** — embedded vector storage with HNSW indexing
           and hybrid text/vector search.
        """
    )
    return duckdb, mo, os


@app.cell
def _(duckdb, mo, os):
    env_dropdown = mo.ui.dropdown(
        options=["md:oideachais", "local_duckdb"],
        value="md:oideachais",
        label="Lakehouse attach",
    )

    senior_cycle_subjects = [
        "mathematics",
        "applied_mathematics",
        "english",
        "gaeilge",
        "biology",
        "chemistry",
    ]

    subject_selector = mo.ui.multiselect(
        options=senior_cycle_subjects,
        value=["biology", "chemistry"],
        label="Target LC subjects",
    )

    language_selector = mo.ui.multiselect(
        options=["en", "ga"],
        value=["en"],
        label="Working languages",
    )

    mo.hstack(
        [env_dropdown, subject_selector, language_selector],
        justify="start",
        gap=1.0,
    )
    return env_dropdown, language_selector, senior_cycle_subjects, subject_selector


@app.cell
def _(env_dropdown, language_selector, mo, subject_selector):
    engine_label = env_dropdown.value
    subjects = ", ".join(f"`{s}`" for s in subject_selector.value)
    langs = ", ".join(f"`{l}`" for l in language_selector.value)
    mo.md(
        f"""
        **Current configuration:**

        - **Engine:** `{engine_label}` (live MotherDuck + DuckLake lakehouse, or
          local `.duckdb` file for offline dev)
        - **Selected subjects:** {subjects}
        - **Working languages:** {langs}
        """
    )
    return engine_label, langs, subjects


@app.cell
def _(mo):
    mo.md(
        """
        ## 2. Orchestration with Dagster

        To process the 6 LC subjects + gov.ie circulars without triggering API
        rate limits on Firecrawl or the SEC website, we use **Dagster
        MultiPartitions**.

        Instead of one massive run, we partition by `subject` and `language`.

        ```python
        # cianfhoghlaim/orchestration/components/layer1_ingestion.py

        from dagster import MultiPartitionsDefinition, StaticPartitionsDefinition

        senior_cycle_partition = MultiPartitionsDefinition({
            "subject": StaticPartitionsDefinition([
                "mathematics", "applied_mathematics", "english",
                "gaeilge", "biology", "chemistry",
            ]),
            "language": StaticPartitionsDefinition(["en", "ga"]),
        })

        @dg.asset(
            partitions_def=senior_cycle_partition,
            op_tags={"dagster/concurrency_key": "oideachais_lc"},
        )
        def senior_cycle_asset(context):
            partition_key_str = context.partition_key  # e.g. "en|biology"
            ...
        ```
        """
    )
    return


@app.cell
def _(mo):
    mo.md(
        """
        ## 3. How Dagster Routes to DuckDB / DuckLake

        Before data is extracted, Dagster decides *where* the data should land.
        In the v4 layer-1 ingestion component
        (`cianfhoghlaim/orchestration/components/layer1_ingestion.py`), the DLT
        pipeline output is routed dynamically:

        ```python
        from cianfhoghlaim.dlt.common.motherduck_options import byob_destination

        # Default to the BIEP "sweet spot": MotherDuck catalog + Garage S3 storage
        destination = byob_destination()
        ```

        This seamless routing means developers can test locally on a simple
        `.duckdb` file, while production leverages the scalable, multi-user
        DuckLake architecture with Garage S3 + PostgreSQL.
        """
    )
    return


@app.cell
def _(mo):
    mo.md(
        """
        ## 4. Extraction with DLT and Firecrawl v2

        DLT (Data Load Tool) dynamically creates table schemas based on the data
        we `yield`. The v4 source registry lives at
        `cianfhoghlaim/dlt/british_isles/ireland/education/`.

        ```python
        # cianfhoghlaim/dlt/british_isles/ireland/education/curriculum_source.py

        @dlt.resource(
            name="curriculum_pages",
            write_disposition="merge",
            primary_key=["content_hash"],
        )
        def curriculum_pages() -> Iterator[dict]:
            scrape_opts = ScrapeOptions(formats=["markdown", "links"], onlyMainContent=True)
            result = app.crawl(
                url="https://www.curriculumonline.ie/Senior-cycle/Senior-Cycle-Subjects/Biology/",
                limit=50,
                scrape_options=scrape_opts,
            )
            for page in result.data:
                yield {
                    "url": page.metadata["sourceURL"],
                    "markdown": page.markdown,
                    "content_hash": hashlib.sha256(page.markdown.encode()).hexdigest(),
                    "subject": "biology",
                }
        ```

        Notice `write_disposition="merge"`: ensures idempotent runs — we only
        update rows where the `content_hash` changes.
        """
    )
    return


@app.cell
def _(mo):
    mo.md(
        """
        ## 5. The DuckLake Architecture & Dual Execution

        Once DLT extracts the data, it routes to two distinct locations:

        1. **DuckLake (Primary):** the BIEP default — MotherDuck catalog +
           Garage S3 storage + DuckDB compute.

           - **Compute:** Fast, local, in-process analytics using `DuckDB`.
           - **Storage:** Cheap, decoupled Parquet files in `s3://ducklake/oideachais/`.
           - **Metadata:** ACID compliance via the MotherDuck Postgres endpoint.

        2. **Filesystem Export (Secondary):** for offline educators /
           researchers. DLT maps a secondary `filesystem` destination to
           `./downloads/structured_export/`. PDFs are normalised by BAML schema
           metadata (e.g. `2024_Higher_Biology_ExamPaper_a1b2c3.pdf`).
        """
    )
    return


@app.cell
def _(mo, subject_selector, language_selector):
    query_text = f"""
    -- Querying the BIEP DuckLake catalog
    SELECT
        cp.subject,
        cp.language,
        COUNT(DISTINCT cp.content_hash) AS pages_crawled,
        COUNT(DISTINCT pdfs.url) AS pdfs_discovered,
        COUNT(DISTINCT CASE
            WHEN dl.status IN ('downloaded', 'already_exists') THEN dl.url
        END) AS pdfs_downloaded,
        COUNT(DISTINCT CASE
            WHEN pdfs.pdf_type = 'exam_paper' THEN pdfs.url
        END) AS exam_papers,
        COUNT(DISTINCT CASE
            WHEN pdfs.pdf_type = 'marking_scheme' THEN pdfs.url
        END) AS marking_schemes
    FROM curriculum.curriculum_pages cp
    LEFT JOIN curriculum.curriculum_pdfs pdfs
        ON cp.subject = pdfs.subject AND cp.language = pdfs.language
    LEFT JOIN curriculum.pdf_downloads dl ON pdfs.url = dl.url
    WHERE cp.subject IN ({", ".join(f"'{s}'" for s in subject_selector.value)})
      AND cp.language IN ({", ".join(f"'{l}'" for l in language_selector.value)})
    GROUP BY cp.subject, cp.language
    ORDER BY cp.subject, cp.language
    """

    sql_area = mo.ui.text_area(
        value=query_text.strip(), rows=10, full_width=True, label="Test query"
    )
    run_query = mo.ui.run_button(label="Execute against md:oideachais")
    mo.vstack([mo.md("### Query the BIEP lakehouse"), sql_area, run_query])
    return run_query, sql_area


@app.cell
def _(duckdb, mo, os, run_query, sql_area):
    import pandas as pd

    mo.stop(
        not run_query.value,
        mo.md("*Click *Execute* to run the SQL query against the active lakehouse.*"),
    )

    output_ui = None
    try:
        token = os.environ.get("MOTHERDUCK_TOKEN", "")
        if token:
            # ibis.duckdb.connect() picks up the MotherDuck token from the
# connection URL (?motherduck_token=...) so no global SET is needed.
        con = ibis.duckdb.connect("md:oideachais")
        df = con.execute(sql_area.value).to_pandas()
        con.close()
        output_ui = mo.ui.table(df) if not df.empty else mo.md(
            "*Query executed successfully — 0 rows returned.*"
        )
    except Exception as e:
        output_ui = mo.callout(
            mo.md(
                f"**Execution Error:**\n\n```text\n{e}\n```\n\n"
                "*(Have you run the BIEP Dagster job to populate the "
                "`md:oideachais` lakehouse yet?)*"
            ),
            kind="danger",
        )
    output_ui
    return df, pd


@app.cell
def _(mo):
    mo.md(
        """
        ## 6. Stagehand: Browser Automation for Exam Papers

        While Firecrawl handles standard sites, downloading past papers from the
        SEC (`examinations.ie`) requires interacting with dropdowns. We use
        **Stagehand** via Browserbase for this.

        ```python
        # The Stagehand extraction logic for the BIEP
        materials = scrape_exam_materials_sync(
            subject="biology",
            years=[2023, 2024],
            level="leaving_certificate",
        )
        ```
        """
    )
    return


@app.cell
def _(mo):
    mo.md(
        """
        ## 7. CocoIndex v1: Incremental BGE-M3 Transformations

        Now that our lakehouse holds clean Markdown and downloaded PDFs, we
        convert them into vector embeddings for RAG. **CocoIndex v1** is our
        transformation engine.

        CocoIndex operates **incrementally** — it tracks which rows have changed
        and only processes the new ones. The v1 BIEP Apps at
        `cianfhoghlaim/cocoindex_flows/` are: `leabharlann_books_embedding`,
        `leabharlann_zotero_embedding`, `leabharlann_takeout_embedding`, and the
        per-subject syllabus embeddings.

        ```python
        import cocoindex
        from annotated_types import Annotated
        from numpy import NDArray

        @cocoindex.flow_def(name="BiepSyllabusEmbedding")
        def embed_curriculum(flow_builder, data_scope):
            data_scope["pages"] = flow_builder.add_source(
                cocoindex.sources.Postgres(
                    connection=...,
                    query="SELECT content_hash, subject, markdown FROM curriculum.curriculum_pages",
                )
            )
            target = data_scope.add_collector()
            with data_scope["pages"].row() as page:
                page["chunks"] = page["markdown"].transform(
                    cocoindex.functions.SplitRecursively(
                        language="markdown", chunk_size=1500,
                    )
                )
                with page["chunks"].row() as chunk:
                    chunk["vector"] = chunk["text"].transform(
                        cocoindex.functions.EmbedText(
                            api_type=cocoindex.LlmApiType.OPENAI,
                            model="BAAI/bge-m3",
                        )
                    )
                    target.collect(
                        id=cocoindex.GeneratedField.UUID,
                        subject=page["subject"],
                        content_hash=page["content_hash"],
                        text=chunk["text"],
                        vector=chunk["vector"],
                    )
            target.export(
                "lancedb_export",
                cocoindex.targets.LanceDB(
                    uri="s3://lance/oideachais/",
                    table_name="biep_curriculum_embeddings",
                ),
                primary_key_fields=["id"],
            )
        ```
        """
    )
    return


@app.cell
def _(mo):
    mo.md(
        """
        ## 8. LanceDB: Vector Retrieval

        Finally, CocoIndex writes the BGE-M3 embeddings directly to **LanceDB**
        in the `biep_curriculum_embeddings` table.

        Why LanceDB?

        - **Embedded:** Runs in-process via `lance_scan('s3://...')`.
        - **Multimodal:** Supports text, images, and vectors in one place.
        - **HNSW Indexing:** High-speed approximate nearest neighbor search.
        - **Hybrid Search:** Mixes semantic search with keyword filtering.

        ```python
        import lancedb

        db = lancedb.connect("s3://lance/oideachais/")
        table = db.open_table("biep_curriculum_embeddings")
        table.create_fts_index("text")

        results = (
            table.search("mitosis cellular division", query_type="hybrid")
            .where("subject = 'biology'")
            .limit(5)
            .rerank(method="rrf")
            .to_pandas()
        )
        ```

        And just like that, the 6 LC subjects have been fully ingested,
        processed, embedded, and are ready to power our AI agents!
        """
    )
    return


if __name__ == "__main__":
    app.run()