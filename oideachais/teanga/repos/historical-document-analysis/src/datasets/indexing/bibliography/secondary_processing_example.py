#!/usr/bin/env python3
"""
Example usage of SecondaryLLMProcessor for enhanced bibliography analysis.

This script demonstrates how to use the secondary processing to improve
shelf mark to transcription linking and extract people and locations.
"""

import os
import sys
from pathlib import Path
import dotenv

# Add the src directory to the Python path
project_root = Path(__file__).parent.parent.parent.parent.parent.parent
sys.path.append(str(project_root))

# Load environment variables from project root
dotenv.load_dotenv(project_root / ".env")

from src.models.llm.secondary_llm_processing import SecondaryLLMProcessor


def run_secondary_processing_example():
    """Example of running secondary processing on existing structured data."""
    
    # Example structured data directory (adjust path as needed)
    structured_dir = Path("/Users/isaac1/Documents/GitHub/multimodal-document-analysis/src/datasets/cairo_genizah/indexing/biblio/raw_data/cairo_to_manchester_intro_structured")
    
    if not structured_dir.exists():
        print(f"Structured directory not found: {structured_dir}")
        print("Please run the complete pipeline first to generate structured data.")
        return
    
    print(f"Running secondary processing on: {structured_dir}")
    
    # Initialize secondary processor
    processor = SecondaryLLMProcessor(
        model_name="gemma3:27b",  # Use a larger model for better analysis
        context_window_pages=5
    )
    
    # Process the structured data
    enhanced_data = processor.process_from_structured_dir(
        structured_dir,
        output_path=structured_dir.parent / "cairo_to_manchester_intro_enhanced.json"
    )
    
    # Display results
    print("\n" + "="*60)
    print("SECONDARY PROCESSING RESULTS")
    print("="*60)
    
    metadata = enhanced_data.get('processing_metadata', {})
    print(f"Pages processed: {metadata.get('total_pages', 0)}")
    print(f"Model used: {metadata.get('model_used', 'N/A')}")
    
    # Enhanced shelf mark transcriptions
    context_analysis = enhanced_data.get('context_analysis', {})
    enhanced_transcriptions = context_analysis.get('enhanced_shelf_mark_transcriptions', {})
    print(f"\nEnhanced shelf mark transcriptions: {len(enhanced_transcriptions)}")
    
    for shelf_mark, data in enhanced_transcriptions.items():
        print(f"  {shelf_mark}:")
        print(f"    Transcription: {data.get('transcription', 'N/A')}")
        print(f"    Confidence: {data.get('confidence', 'N/A')}")
        print(f"    Pages: {data.get('context_pages', [])}")
        print(f"    Evidence: {data.get('linking_evidence', 'N/A')}")
        print()
    
    # People extracted
    people_locations = enhanced_data.get('people_locations', {})
    people = people_locations.get('people', [])
    print(f"People extracted: {len(people)}")
    
    for person in people[:5]:  # Show first 5
        print(f"  {person.get('name', 'N/A')}:")
        print(f"    Role: {person.get('role', 'N/A')}")
        print(f"    Context: {person.get('context', 'N/A')}")
        print(f"    Variants: {person.get('name_variants', [])}")
        print()
    
    # Locations extracted
    locations = people_locations.get('locations', [])
    print(f"Locations extracted: {len(locations)}")
    
    for location in locations[:5]:  # Show first 5
        print(f"  {location.get('name', 'N/A')}:")
        print(f"    Type: {location.get('type', 'N/A')}")
        print(f"    Context: {location.get('context', 'N/A')}")
        print(f"    Variants: {location.get('name_variants', [])}")
        print()
    
    # Cross-page references
    cross_references = context_analysis.get('cross_page_references', [])
    print(f"Cross-page references found: {len(cross_references)}")
    
    for ref in cross_references:
        print(f"  {ref.get('reference_type', 'N/A')}: {ref.get('description', 'N/A')}")
        print(f"    Pages: {ref.get('pages_involved', [])}")
        print(f"    Confidence: {ref.get('confidence', 'N/A')}")
        print()
    
    print("="*60)
    print("Secondary processing completed successfully!")
    print(f"Enhanced data saved to: {structured_dir.parent / 'cairo_to_manchester_intro_enhanced.json'}")


def analyze_pattern_analysis():
    """Example of analyzing the pattern analysis results."""
    
    structured_dir = Path("/Users/isaac1/Documents/GitHub/multimodal-document-analysis/src/datasets/cairo_genizah/indexing/biblio/raw_data/cairo_to_manchester_intro_structured")
    
    if not structured_dir.exists():
        print(f"Structured directory not found: {structured_dir}")
        return
    
    processor = SecondaryLLMProcessor()
    pages_data = processor._load_structured_data_files(structured_dir)
    pattern_analysis = processor._analyze_shelf_mark_patterns(pages_data)
    
    print("\n" + "="*60)
    print("PATTERN ANALYSIS RESULTS")
    print("="*60)
    
    print(f"Shelf mark frequency:")
    for shelf_mark, pages in pattern_analysis.get('shelf_mark_frequency', {}).items():
        print(f"  {shelf_mark}: appears on pages {pages}")
    
    print(f"\nUnlinked shelf marks: {pattern_analysis.get('unlinked_shelf_marks', [])}")
    print(f"Unlinked transcriptions: {pattern_analysis.get('unlinked_transcriptions', [])}")
    
    print(f"\nTranscriptions by page:")
    for page, transcriptions in pattern_analysis.get('transcriptions_by_page', {}).items():
        print(f"  Page {page}: {list(transcriptions.keys())}")


if __name__ == "__main__":
    print("Secondary LLM Processing Example")
    print("="*40)
    
    # Run the main example
    run_secondary_processing_example()
    
    # Run pattern analysis
    analyze_pattern_analysis()
