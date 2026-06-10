#!/usr/bin/env python3
"""
Example usage of BookOCRService and StructuredJSONLLM together.

This script demonstrates the complete pipeline:
1. Process PDF with OCR to extract text
2. Process OCR results with LLM to extract structured JSON
"""

import sys
import json
import logging
from pathlib import Path
import dotenv
from src.models.llm.add_full_text_to_structured import add_full_text_to_structured

# Add the src directory to the Python path
project_root = Path(__file__).parent.parent.parent.parent.parent.parent
data_root = project_root / "src" / "datasets" / "raw_data" / "cairo_genizah" / "academic_literature"
sys.path.append(str(project_root))

# Load environment variables from project root
dotenv.load_dotenv(project_root / ".env")

from src.models.ocr.book_ocr_service import BookOCRService
from src.models.llm.structured_json_llm import StructuredJSONLLM
from src.models.llm.secondary_llm_processing import SecondaryLLMProcessor
from src.models.llm.add_full_text_to_structured import add_full_text_to_structured

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def load_book_metadata(example_file: str) -> dict:
    """
    Load book metadata from a JSON file.

    :param example_file: The path to the example file
    :return: Dictionary containing book metadata
    """
    example_file_path = Path(example_file)
    metadata_file = data_root / example_file_path.parent / f"{example_file_path.stem}.json"

    if metadata_file.exists():
        with open(metadata_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        return None


def get_pdf_files_in_directory():
    pass


def run_specific_file(example_file: str, book_file: str, model_extension: str = "", use_gemini=True) -> dict:
    """Run the complete pipeline including secondary processing for enhanced analysis.
    :param example_file: The path to example file within in the academic_literature directory (e.g.cairo_to_manchester/cairo_to_manchester_intro.pdf)
    """
    print(f"Processing file: {example_file}")

    # Step 1: OCR Processing
    print("Step 1: Running OCR processing...")
    ocr_service = BookOCRService()
    example_file_path = Path(example_file)
    full_output_path = data_root / example_file_path.parent / example_file_path.stem
    full_pdf_path = data_root / example_file_path
    ocr_result = ocr_service.process_pdf_to_file(pdf_path=str(full_pdf_path), start_page=0,
                                                 output_path=str(full_output_path))
    print(f"OCR result: {ocr_result}")

    # Step 2: Initial Structured Processing
    print("Step 2: Running initial structured LLM processing...")

    # Load book metadata to provide context to the LLM
    book_metadata = load_book_metadata(book_file)
    if book_metadata:
        print(f"✅ Loaded book metadata: {book_metadata.get('title', 'Unknown title')}")

    structured_llm = StructuredJSONLLM(model_name="gemma3:27b", book_metadata=book_metadata, use_gemini=use_gemini)
    structured_result = structured_llm.process_from_ocr_service(ocr_result)
    print(f"Structured processing completed: {structured_result}")
    # Get the structured directory from the structured result
    pdf_name = Path(example_file).stem
    structured_dir = full_output_path / f"{pdf_name}_structured_"
    if model_extension:
        structured_dir = full_output_path / f"{pdf_name}_structured_{model_extension}"
    # Re-add full text after processing
    if structured_result.get('processed_pages', 0) > 0:
        print("Step 2.5: Adding full OCR text to structured files...")
        add_results = add_full_text_to_structured(
            structured_dir=str(structured_dir),
            ocr_results_path=ocr_result['ocr_results_path']
        )
        print(f"Added full text to {add_results['files_updated']} files")

    # Step 3: Secondary Enhanced Processing
    print("Step 3: Running secondary enhanced processing...")
    secondary_processor = SecondaryLLMProcessor(model_name="gemma3:27b")

    if structured_dir.exists():
        enhanced_data = secondary_processor.process_from_structured_dir(
            structured_dir,
            output_path=structured_dir.parent / f"{pdf_name}_enhanced.json"
        )
        print(f"Enhanced processing completed:")
        print(f"  - Pages processed: {enhanced_data.get('processing_metadata', {}).get('total_pages', 0)}")
        print(
            f"  - Enhanced shelf mark transcriptions: {len(enhanced_data.get('context_analysis', {}).get('enhanced_shelf_mark_transcriptions', {}))}")
        print(f"  - People extracted: {len(enhanced_data.get('people_locations', {}).get('people', []))}")
        print(f"  - Locations extracted: {len(enhanced_data.get('people_locations', {}).get('locations', []))}")
    else:
        print(f"Structured directory not found: {structured_dir}")
    print(f"Complete pipeline finished for {example_file}")
    print("-" * 80)


def run_digitized_file(example_file: str, book_file: str, use_gemini: bool = True, model_extension: str = None):
    """Run pipeline for born-digital PDFs: extract text via PyMuPDF and save images. No OCR from GCP.

    This skips external OCR and produces an OCR-compatible JSON so that the
    structured step remains identical.

    :param example_file: Path under `academic_literature` to the PDF (e.g. cairo_to_manchester/intro.pdf)
    :type example_file: str
    :param book_file: Path under `academic_literature` to metadata JSON, if available
    :type book_file: str
    :param use_gemini: Whether to use Gemini for LLM processing; if False, uses Ollama
    :type use_gemini: bool
    :param model_extension: Optional suffix for the structured output directory name
    :type model_extension: str
    """
    print(f"Processing text-only file: {example_file}")

    # Step 1: Text-only extraction with images
    print("Step 1: Extracting embedded text and saving images...")
    ocr_service = BookOCRService()
    example_file_path = Path(example_file)
    full_output_path = data_root / example_file_path.parent / example_file_path.stem
    full_pdf_path = data_root / example_file_path
    ocr_result = ocr_service.process_pdf_text_only_to_file(
        pdf_path=str(full_pdf_path),
        output_path=str(full_output_path),
        start_page=0,
        end_page=None,
        save_images=True
    )
    print(f"Text-only result: {ocr_result}")

    # Step 2: Structured processing
    print("Step 2: Running structured LLM processing...")
    book_metadata = load_book_metadata(book_file)
    if book_metadata:
        print(f"✅ Loaded book metadata: {book_metadata.get('title', 'Unknown title')}")

    structured_llm = StructuredJSONLLM(use_gemini=use_gemini, book_metadata=book_metadata)
    structured_result = structured_llm.process_from_ocr_service(ocr_service_result=ocr_result)
    print(f"Structured processing completed: {structured_result}")

    # Compute structured dir path (respect optional extension)
    pdf_name = Path(example_file).stem
    structured_dir = full_output_path / f"{pdf_name}_structured_"
    if model_extension:
        structured_dir = full_output_path / f"{pdf_name}_structured_{model_extension}"
    logger.log(level=1, msg=f"Structured output directory: {structured_dir}")

    # Step 2.5: Add full text to structured files (idempotent helper)
    print("Step 2.5: Adding full text to structured files...")
    try:
        add_results = add_full_text_to_structured(
            structured_dir=str(structured_dir),
            ocr_results_path=ocr_result['ocr_results_path']
        )
        print(f"Added full text to {add_results['files_updated']} files")
    except Exception as e:
        logger.warning(f"Failed to add full text to structured files: {e}")

    # Step 3: Secondary enhanced processing
    print("Step 3: Running secondary enhanced processing...")
    secondary_processor = SecondaryLLMProcessor(model_name="gemma3:27b")
    enhanced_json_path = full_output_path / f"{pdf_name}_enhanced.json"

    if structured_dir.exists():
        enhanced_data = secondary_processor.process_from_structured_dir(
            structured_dir,
            output_path=enhanced_json_path
        )
        print(f"Enhanced processing completed:")
        print(f"  - Pages processed: {enhanced_data.get('processing_metadata', {}).get('total_pages', 0)}")
        print(
            f"  - Enhanced shelf mark transcriptions: {len(enhanced_data.get('context_analysis', {}).get('enhanced_shelf_mark_transcriptions', {}))}")
        print(f"  - People extracted: {len(enhanced_data.get('people_locations', {}).get('people', []))}")
        print(f"  - Locations extracted: {len(enhanced_data.get('people_locations', {}).get('locations', []))}")
    else:
        print(f"Structured directory not found: {structured_dir}")

    print(f"Text-only pipeline finished for {example_file}")
    print("-" * 80)


def check_pipeline_status(example_file: str):
    """Check what steps of the pipeline have been completed for a given file.
    :param example_file: The path to example file within the academic_literature directory
    """
    print(f"Checking pipeline status for: {example_file}")

    example_file_path = Path(example_file)
    pdf_name = example_file_path.stem
    full_output_path = data_root / example_file_path.parent / example_file_path.stem

    # Expected file paths
    ocr_json_path = full_output_path / f"{pdf_name}_ocr_results.json"
    images_dir = full_output_path / f"{pdf_name}_images"
    structured_dir = full_output_path / f"{pdf_name}_structured"
    enhanced_json_path = full_output_path / f"{pdf_name}_enhanced.json"

    print(f"File: {example_file}")
    print(f"Base directory: {full_output_path}")
    print()

    # Check OCR
    if ocr_json_path.exists() and images_dir.exists():
        image_count = len(list(images_dir.glob("*.png"))) if images_dir.exists() else 0
        print(f"✅ OCR Processing: COMPLETED")
        print(f"   OCR results: {ocr_json_path}")
        print(f"   Images: {images_dir} ({image_count} files)")
    else:
        print(f"❌ OCR Processing: NOT COMPLETED")
        print(f"   OCR results: {ocr_json_path} {'✅' if ocr_json_path.exists() else '❌'}")
        print(f"   Images: {images_dir} {'✅' if images_dir.exists() else '❌'}")

    # Check Structured Processing
    if structured_dir.exists() and any(structured_dir.glob("*_structured.json")):
        structured_count = len(list(structured_dir.glob("*_structured.json")))
        print(f"✅ Structured Processing: COMPLETED ({structured_count} files)")
        print(f"   Directory: {structured_dir}")
    else:
        print(f"❌ Structured Processing: NOT COMPLETED")
        print(f"   Directory: {structured_dir} {'✅' if structured_dir.exists() else '❌'}")

    # Check Enhanced Processing
    if enhanced_json_path.exists():
        print(f"✅ Enhanced Processing: COMPLETED")
        print(f"   Results: {enhanced_json_path}")
    else:
        print(f"❌ Enhanced Processing: NOT COMPLETED")
        print(f"   Results: {enhanced_json_path}")

    print("-" * 80)


def resume_specific_file(example_file: str, run_structured: bool = True, book_file=None, use_gemini=True,
                         model_extension: str = None, page_number: int = None):
    """Resume the pipeline from where it left off, skipping completed steps.
    :param example_file: The path to example file within the academic_literature directory
    """
    print(f"Resuming processing for file: {example_file}")

    example_file_path = Path(example_file)
    pdf_name = example_file_path.stem
    full_output_path = data_root / example_file_path.parent / example_file_path.stem
    full_pdf_path = data_root / example_file_path

    # Expected file paths
    ocr_json_path = full_output_path / f"{pdf_name}_ocr_results.json"
    images_dir = full_output_path / f"{pdf_name}_images"
    structured_dir = full_output_path / f"{pdf_name}_structured_"
    if model_extension:
        structured_dir = full_output_path / f"{pdf_name}_structured_{model_extension}"
    enhanced_json_path = full_output_path / f"{pdf_name}_enhanced.json"

    ocr_result = None
    structured_result = None

    # Step 1: Check OCR Processing
    if ocr_json_path.exists() and images_dir.exists():
        print(f"✅ OCR already completed - skipping OCR processing")
        print(f"   OCR results: {ocr_json_path}")
        print(f"   Images directory: {images_dir}")
        ocr_result = {
            'ocr_results_path': str(ocr_json_path),
            'images_dir': str(images_dir)
        }
    else:
        print("Step 1: Running OCR processing...")
        ocr_service = BookOCRService()
        ocr_result = ocr_service.process_pdf_to_file(
            pdf_path=str(full_pdf_path),
            start_page=0,
            output_path=str(full_output_path)
        )
        print(f"OCR result: {ocr_result}")

    # Step 2: Check Structured Processing
    if structured_dir.exists() and any(structured_dir.glob("*_structured.json")) and not run_structured:
        print(f"✅ Structured processing already completed - skipping LLM processing")
        print(f"   Structured directory: {structured_dir}")
        structured_result = {
            'structured_dir': str(structured_dir),
            'total_pages': len(list(structured_dir.glob("*_structured.json")))
        }
    else:
        print("Step 2: Running initial structured LLM processing...")

        # Load book metadata to provide context to the LLM
        book_metadata = load_book_metadata(book_file)
        if book_metadata:
            print(f"✅ Loaded book metadata: {book_metadata.get('title', 'Unknown title')}")

        structured_llm = StructuredJSONLLM(use_gemini=use_gemini, book_metadata=book_metadata)
        structured_result = structured_llm.process_from_ocr_service(ocr_service_result=ocr_result, page_number=page_number)
        # add_full_text_to_structured(ocr_results_path=ocr_result.get('ocr_results_path'), structured_dir=structured_result.get('structured_dir'))
        print(f"Structured processing completed: {structured_result}")

        # Step 2.5: Add full OCR text back to structured files (to save tokens during LLM processing)
    print("Step 2.5: Adding full OCR text to structured files...")
    try:
        add_results = add_full_text_to_structured(
            structured_dir=str(structured_dir),
            ocr_results_path=ocr_result['ocr_results_path']
        )
        print(f"Added full text to {add_results['files_updated']} files")
    except Exception as e:
        logger.warning(f"Failed to add full text to structured files: {e}")

    # Step 3: Check Secondary Enhanced Processing
    if enhanced_json_path.exists():
        print(f"✅ Enhanced processing already completed - skipping secondary processing")
        print(f"   Enhanced results: {enhanced_json_path}")

        # Load and display summary of existing enhanced data
        try:
            import json
            with open(enhanced_json_path, 'r', encoding='utf-8') as f:
                enhanced_data = json.load(f)
            print(f"Enhanced processing summary:")
            print(f"  - Pages processed: {enhanced_data.get('processing_metadata', {}).get('total_pages', 0)}")
            print(
                f"  - Enhanced shelf mark transcriptions: {len(enhanced_data.get('context_analysis', {}).get('enhanced_shelf_mark_transcriptions', {}))}")
            print(f"  - People extracted: {len(enhanced_data.get('people_locations', {}).get('people', []))}")
            print(f"  - Locations extracted: {len(enhanced_data.get('people_locations', {}).get('locations', []))}")
        except Exception as e:
            print(f"Warning: Could not load enhanced data summary: {e}")
    else:
        print("Step 3: Running secondary enhanced processing...")
        secondary_processor = SecondaryLLMProcessor(model_name="gemma3:27b")

        # Use the correct structured directory path
        if structured_result and 'structured_dir' in structured_result:
            structured_dir_path = Path(structured_result['structured_dir'])
        else:
            structured_dir_path = structured_dir

        if structured_dir_path.exists():
            enhanced_data = secondary_processor.process_from_structured_dir(
                structured_dir_path,
                output_path=enhanced_json_path
            )
            print(f"Enhanced processing completed:")
            print(f"  - Pages processed: {enhanced_data.get('processing_metadata', {}).get('total_pages', 0)}")
            print(
                f"  - Enhanced shelf mark transcriptions: {len(enhanced_data.get('context_analysis', {}).get('enhanced_shelf_mark_transcriptions', {}))}")
            print(f"  - People extracted: {len(enhanced_data.get('people_locations', {}).get('people', []))}")
            print(f"  - Locations extracted: {len(enhanced_data.get('people_locations', {}).get('locations', []))}")
        else:
            print(f"Structured directory not found: {structured_dir_path}")

    print(f"Resume pipeline finished for {example_file}")
    print("-" * 80)

def run_all_pdf_in_dir(directory_to_process, book_metadata_dir, use_gemini):
    for file in Path(directory_to_process).glob("*.pdf"):
        run_specific_file(example_file=file, book_file=book_metadata_dir, model_extension="gemini_gemini_2.5_flash", use_gemini=use_gemini)

if __name__ == "__main__":
    #run_all_pdf_in_dir(directory_to_process="/Users/isaac1/Documents/GitHub/multimodal-document-analysis/src/datasets/raw_data/cairo_genizah/academic_literature/kettubah_palestine",
                       #book_metadata_dir="/Users/isaac1/Documents/GitHub/multimodal-document-analysis/src/datasets/raw_data/cairo_genizah/academic_literature/kettubah_palestine/friedman_meta.json",
                       #use_gemini=True,
    #)

    # Check pipeline status (useful to see what's already done)
    # check_pipeline_status("cairo_to_manchester/cairo_to_manchester_2.pdf")

    # Run complete pipeline (will re-run all steps)
    # resume_specific_file(example_file="cairo_to_manchester/cairo_to_manchester_1.pdf", book_file="cairo_to_manchester/cairo_to_manchester_metadata.json")

    # Resume pipeline (will skip completed steps to save OCR costs)
    # resume_specific_file("cairo_to_manchester/cairo_to_manchester_1.pdf")

    # Other examples:
    # run_specific_file("cairo_to_manchester/cairo_to_manchester_2.pdf", book_file="cairo_to_manchester/cairo_to_manchester_metadata.json")
    # resume_specific_file("cairo_to_manchester/cairo_to_manchester_intro.pdf", book_file="cairo_to_manchester/cairo_to_manchester_metadata.json", use_gemini=True, model_extension="gemini_gemini_2.5_flash", run_structured=False)
    # run_specific_file("cairo_to_manchester/dramits_persona.pdf")
    # run_specific_file("cairo_to_manchester/ginzburg_1.pdf")
    # run_specific_file("cairo_to_manchester/trader_1.pdf")
    #resume_specific_file(example_file="rylands_articles/dsd-article-p75_5.pdf",
                         #book_file="rylands_articles/dsd-article-p75_5_ocr_results.json", use_gemini=True,
                         #model_extension="gemini_gemini_2.5_flash", run_structured=False)
    # run_specific_file(example_file="india_traders/india_trader_350_424.pdf",
                       #book_file="india_traders/india_trader_metada.json",
                       #model_extension="gemini_gemini_2.5_flash"
                       #)
    #run_specific_file(example_file="rylands_articles/bjrl-article-p488.pdf",
                      #book_file="rylands_articles/bjrl-article-p488_meta.json",
                      #use_gemini=True,
                      #model_extension="gemini_gemini_2.5_flash"
                     # )

    # run_specific_file(example_file="rylands_articles/bjrl-article-p710.pdf",
                      # book_file="rylands_articles/bjrl-article-p710.json",
                      #use_gemini=True,
                      # model_extension="gemini_gemini_2.5_flash")
    run_digitized_file(
        example_file="mcgill/mcgill_frag.pdf",
        book_file="mcgill/mcgill_frag_metadata.json",
        use_gemini=True,
        model_extension="gemini_gemini_2.5_flash",
    )
