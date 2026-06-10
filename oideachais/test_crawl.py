import dlt
from oideachais.data_platform.dlt_sources.ireland.ncca import ncca_source
from oideachais.data_platform.dlt_sources.ireland.pdf_downloader import pdf_download_source
import logging
logging.basicConfig(level=logging.INFO)

print("Starting test crawl pipeline...")
pipeline = dlt.pipeline(pipeline_name="curriculum_test", destination="duckdb", dataset_name="curriculum_test_data")
print("Extracting from NCCA (Maths/Junior Cycle)...")
# Just a tiny crawl
load_info = pipeline.run(ncca_source(cycle="junior_cycle", subject="mathematics", max_pages=2))
print("Crawl Complete! Load info:")
print(load_info)

print("Running PDF Downloader...")
# Run the downloader
pdf_info = pipeline.run(pdf_download_source(
    duckdb_path="/Users/cianmacandeisigh/dev/kings_college_galway/curriculum_test.duckdb", # Not quite, let's use the local duckdb
    download_dir="/Users/cianmacandeisigh/dev/kings_college_galway/downloads/curriculum_pdfs",
    cycle="junior_cycle",
    subject="mathematics",
    max_files=5
))
print("PDF Download Complete!")
print(pdf_info)
