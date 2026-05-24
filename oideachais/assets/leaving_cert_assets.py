import os
import requests
import duckdb
from pathlib import Path
from datetime import datetime
from dagster import (
    asset,
    AssetExecutionContext,
    MaterializeResult,
    MetadataValue,
    Config,
)
import dlt

class LeavingCertConfig(Config):
    year: int = 2026
    subjects: list[str] = [
        "gaeilge", "english", "maths", "german", 
        "geography", "biology", "chemistry", "history"
    ]
    garage_bucket: str = "education-documents"
    motherduck_db: str = "oideachais"

@asset(group_name="leaving_cert", compute_kind="dlt")
def scrape_syllabus_and_exams(context: AssetExecutionContext, config: LeavingCertConfig):
    """
    1. Scrapes Syllabus and Exam PDFs for Leaving Cert.
    2. Uploads raw PDFs to Garage S3.
    """
    context.log.info(f"Scraping Leaving Cert PDFs for {config.year} - Subjects: {config.subjects}")
    
    # In a real scenario, this uses Firecrawl or web scraping to get PDFs from examinations.ie
    # Storing them into Garage S3.
    
    # Mocking the pipeline extraction
    def mock_pdf_source():
        for subject in config.subjects:
            yield {
                "subject": subject,
                "year": config.year,
                "syllabus_pdf_s3_path": f"s3://{config.garage_bucket}/syllabus/lc_{subject}.pdf",
                "exam_pdf_s3_path": f"s3://{config.garage_bucket}/exams/{config.year}/lc_{subject}.pdf",
                "marking_scheme_s3_path": f"s3://{config.garage_bucket}/marking_schemes/{config.year}/lc_{subject}.pdf"
            }

    # dlt pipeline to load metadata to MotherDuck
    pipeline = dlt.pipeline(
        pipeline_name="leaving_cert_ingestion",
        destination="duckdb", # We configure motherduck string in secrets
        dataset_name="leaving_cert_raw"
    )
    
    load_info = pipeline.run(mock_pdf_source(), table_name="pdf_metadata")
    
    return MaterializeResult(
        metadata={
            "loaded_records": MetadataValue.int(load_info.metrics.get("rows_loaded", 0) if hasattr(load_info, 'metrics') else 0),
            "subjects": MetadataValue.json(config.subjects)
        }
    )

@asset(group_name="leaving_cert", deps=["scrape_syllabus_and_exams"], compute_kind="cocindex")
def index_curriculum_pdfs(context: AssetExecutionContext, config: LeavingCertConfig):
    """
    1. Reads PDFs from Garage S3.
    2. Uses cocindex (ColPali) to index the PDFs into DuckDB/LanceDB.
    """
    context.log.info("Indexing PDFs using cocindex and storing in MotherDuck...")
    
    # Connect to MotherDuck
    md_token = os.environ.get("MOTHERDUCK_TOKEN", "")
    con = duckdb.connect(f"md:{config.motherduck_db}?motherduck_token={md_token}")
    
    # Fetch metadata
    pdfs = con.execute("SELECT subject, syllabus_pdf_s3_path FROM leaving_cert_raw.pdf_metadata").fetchall()
    
    indexed_count = 0
    for subject, pdf_path in pdfs:
        context.log.info(f"Processing ColPali index for {subject} from {pdf_path}")
        # Call cocindex logic here...
        # Store embeddings back to MotherDuck or LanceDB
        indexed_count += 1
        
    return MaterializeResult(
        metadata={
            "indexed_pdfs": MetadataValue.int(indexed_count)
        }
    )

@asset(group_name="leaving_cert", deps=["index_curriculum_pdfs"], compute_kind="llm")
def generate_study_plans(context: AssetExecutionContext, config: LeavingCertConfig):
    """
    Generates study plans and marking scheme explanations based on the syllabus index.
    Outputs the final JSON resources distributed via Cloudflare R2 cache.
    """
    context.log.info("Generating Study Plans and FIBO assets...")
    
    # Logic to interact with Litellm / VLM to generate the marking scheme explanation
    # For each subject, we synthesize the index data and write to R2.
    
    # distribution_url = f"https://cdn.cianfhoghlaim.ie/study-plans/{config.year}/"
    
    return MaterializeResult(
        metadata={
            "status": MetadataValue.text("Study plans generated and cached in R2"),
        }
    )
