import dlt
from oideachais.data_platform.dlt_sources.ireland.curriculum_source import curriculum_source
from oideachais.data_platform.dlt_sources.ireland.pdf_downloader import pdf_download_source
import logging
logging.basicConfig(level=logging.INFO)

print("Starting test crawl pipeline...")
pipeline = dlt.pipeline(pipeline_name="curriculum_test2", destination="duckdb", dataset_name="curriculum_test2_data")
print("Extracting from curriculum_source (Maths/Senior Cycle)...")
# Run curriculum_source directly so it does classification and BAML metadata!
load_info = pipeline.run(curriculum_source(cycle="senior_cycle", subject="english", max_pages_per_subject=2, sources=["ncca"]))
print("Crawl Complete! Load info:")
print(load_info)

print("Running PDF Downloader...")
# Run the downloader
pdf_info = pipeline.run(pdf_download_source(
    duckdb_path="/Users/cianmacandeisigh/dev/kings_college_galway/curriculum_test2.duckdb",
    download_dir="/Users/cianmacandeisigh/dev/kings_college_galway/downloads/curriculum_pdfs",
    cycle="senior_cycle",
    subject="english",
    max_files=5
))
print("PDF Download Complete!")
print(pdf_info)
