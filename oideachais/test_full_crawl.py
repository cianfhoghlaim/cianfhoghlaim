import dlt
from oideachais.data_platform.dlt_sources.ireland.curriculum_source import curriculum_source
from oideachais.data_platform.dlt_sources.ireland.pdf_downloader import pdf_download_source
import logging
logging.basicConfig(level=logging.INFO)

print("Starting FULL test crawl pipeline...")
pipeline = dlt.pipeline(
    pipeline_name="curriculum_full_test", 
    destination="duckdb", 
    dataset_name="curriculum_full_data"
)

# Test subjects: English and Maths across Senior and Junior Cycle
subjects = ["english", "mathematics"]

print(f"Extracting from curriculum_source for {subjects}...")
# Note: we use sources=["ncca"] since curriculum_source normally handles ncca & curriculumonline.
# Let's do both cycles
for cycle in ["junior_cycle", "senior_cycle"]:
    for subject in subjects:
        print(f"Crawling {cycle} / {subject}")
        load_info = pipeline.run(
            curriculum_source(
                cycle=cycle, 
                subject=subject, 
                max_pages_per_subject=2, 
                sources=["ncca"]
            )
        )
        print(f"Load info for {cycle}/{subject}:", load_info)

print("Running PDF Downloader...")
# Run the downloader
pdf_info = pipeline.run(pdf_download_source(
    duckdb_path="/Users/cianmacandeisigh/dev/kings_college_galway/curriculum_full_test.duckdb",
    download_dir="/Users/cianmacandeisigh/dev/kings_college_galway/downloads/curriculum_pdfs",
    cycle=None, # Process all cycles
    subject=None, # Process all subjects
    max_files=10 # Get up to 10 files
))
print("PDF Download Complete!")
print(pdf_info)
