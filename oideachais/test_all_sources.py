import dlt
from oideachais.data_platform.dlt_sources.ireland.curriculum_source import curriculum_source
from oideachais.data_platform.dlt_sources.ireland.examinations import sec_examinations_browser_source
from oideachais.data_platform.dlt_sources.ireland.pdf_downloader import pdf_download_source
import logging
logging.basicConfig(level=logging.INFO)

print("Starting FULL integration test pipeline...")
pipeline = dlt.pipeline(
    pipeline_name="curriculum_all_test", 
    destination="duckdb", 
    dataset_name="curriculum_all_data"
)

# 1. Test CurriculumOnline
print("Running curriculum_source for English (curriculumonline)...")
try:
    load_info = pipeline.run(
        curriculum_source(
            cycle="senior_cycle", 
            subject="english", 
            max_pages_per_subject=2, 
            sources=["curriculumonline"]
        )
    )
    print("CurriculumOnline Crawl Complete! Load info:")
    print(load_info)
except Exception as e:
    print(f"Failed curriculum_source: {e}")

# 2. Test Examinations.ie
print("Running sec_examinations_browser_source for English...")
try:
    load_info2 = pipeline.run(
        sec_examinations_browser_source(
            subjects=["english"], 
            years=[2023], 
            level="leaving_certificate"
        )
    )
    print("Examinations.ie Scrape Complete! Load info:")
    print(load_info2)
except Exception as e:
    print(f"Failed examinations_source: {e}")

# 3. PDF Downloader
print("Running PDF Downloader for all extracted PDFs...")
try:
    pdf_info = pipeline.run(pdf_download_source(
        duckdb_path="/Users/cianmacandeisigh/dev/kings_college_galway/curriculum_all_test.duckdb",
        download_dir="/Users/cianmacandeisigh/dev/kings_college_galway/downloads/curriculum_pdfs",
        cycle=None,
        subject=None,
        max_files=10
    ))
    print("PDF Download Complete!")
    print(pdf_info)
except Exception as e:
    print(f"Failed PDF Downloader: {e}")
