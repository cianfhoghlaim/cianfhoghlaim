"""
Dagster assets for Leaving Certificate Exam Analysis.

Integrates:
1. dlt extraction of PDFs to Garage S3 and MotherDuck.
2. VLM parsing with BAML for structured extraction.
3. FIBO asset generation for study plans.
"""

from dagster import (
    asset,
    AssetExecutionContext,
    MaterializeResult,
    MetadataValue,
    Config,
)
from typing import List
import json
from pathlib import Path

# Local imports
from dlt_sources.leaving_cert import leaving_cert_source

class ExamAnalysisConfig(Config):
    years: List[int] = [2022, 2023, 2024, 2025]
    subjects: List[str] = [
        "gaeilge", "english", "mathematics", "geography", 
        "history", "biology", "chemistry"
    ]
    motherduck_dataset: str = "leaving_cert"


@asset(group_name="exam_analysis", compute_kind="dlt")
def ingest_leaving_cert_documents(
    context: AssetExecutionContext,
    config: ExamAnalysisConfig
) -> MaterializeResult:
    """
    Extracts Leaving Cert syllabus, exams, and marking schemes.
    Stores PDFs in Garage S3 and metadata in MotherDuck.
    """
    import dlt
    
    # Configure dlt pipeline
    pipeline = dlt.pipeline(
        pipeline_name="leaving_cert",
        destination="duckdb", # Will use MOTHERDUCK_TOKEN if set
        dataset_name=config.motherduck_dataset
    )
    
    # Run the source
    source = leaving_cert_source(years=config.years, subjects=config.subjects)
    
    # Normally we would run this:
    # load_info = pipeline.run(source)
    # context.log.info(f"Loaded {load_info}")
    
    context.log.info(f"Simulating dlt pipeline run for {config.subjects} over years {config.years}")
    
    return MaterializeResult(
        metadata={
            "subjects": MetadataValue.json(config.subjects),
            "years": MetadataValue.json(config.years),
            "destination": "MotherDuck + Garage S3"
        }
    )


@asset(group_name="exam_analysis", deps=["ingest_leaving_cert_documents"], compute_kind="vlm")
def parse_exam_documents_with_vlm(context: AssetExecutionContext, config: ExamAnalysisConfig) -> MaterializeResult:
    """
    Uses Vision Language Models (via LiteLLM) and BAML to parse
    complex exam pages (Math formulas, Chemistry diagrams) into structured data.
    """
    # Pseudo-code for BAML integration:
    # from baml_client import baml
    # from baml_client.types import ExamQuestion, MarkingSchemeRubric
    
    context.log.info("Simulating VLM + BAML extraction...")
    
    # Simulate VLM extraction for a sample Biology question
    sample_extracted_data = {
        "question_id": "2024-BIOL-H-Q1",
        "subject": "biology",
        "marks_available": 20,
        "requires_diagram": True,
        "visual_requirements": [
            {
                "diagram_type": "CELL_DIAGRAM",
                "description": "Cross-section of an animal cell",
                "mandatory_labels": ["mitochondrion", "nucleus", "ribosome"]
            }
        ]
    }
    
    # Write to a local file for the next step to pick up
    output_dir = Path("data/exam_analysis")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with open(output_dir / "parsed_exams.json", "w") as f:
        json.dump([sample_extracted_data], f, indent=2)
        
    return MaterializeResult(
        metadata={
            "parsed_questions": 1,
            "sample_question_id": sample_extracted_data["question_id"]
        }
    )


@asset(group_name="exam_analysis", deps=["parse_exam_documents_with_vlm"], compute_kind="fibo")
def generate_study_plan_assets(context: AssetExecutionContext, config: ExamAnalysisConfig) -> MaterializeResult:
    """
    Generates targeted FIBO visual assets based on the VLM's analysis 
    of the marking schemes and exam papers.
    """
    context.log.info("Generating FIBO assets from parsed exam requirements...")
    
    # Read parsed data
    input_file = Path("data/exam_analysis/parsed_exams.json")
    if not input_file.exists():
         context.log.warning("No parsed exams found.")
         return MaterializeResult(metadata={"assets_generated": 0})
         
    with open(input_file, "r") as f:
        parsed_data = json.load(f)
        
    assets_generated = 0
    for question in parsed_data:
        if question.get("requires_diagram") and question.get("visual_requirements"):
            for req in question["visual_requirements"]:
                context.log.info(f"Triggering FIBO generation for {req['diagram_type']}: {req['description']}")
                
                # Here we would call the FiboResource
                # image = await fibo_resource.generate(prompt=req['description'])
                assets_generated += 1
                
    # Cache final results to Cloudflare R2 (Simulated)
    context.log.info("Uploading final study plans and assets to Cloudflare R2 cache...")
    
    return MaterializeResult(
        metadata={
            "fibo_assets_generated": assets_generated,
            "distribution_cache": "Cloudflare R2"
        }
    )
