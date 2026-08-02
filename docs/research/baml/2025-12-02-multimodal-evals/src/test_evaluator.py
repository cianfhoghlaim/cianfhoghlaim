#!/usr/bin/env python3
"""
Test script for the receipt evaluator to verify basic functionality.
"""

import sys
from pathlib import Path

from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.receipt_evaluator import ReceiptEvaluator


def test_basic_functionality():
    """Test basic functionality of the receipt evaluator."""
    print("🧪 Testing Receipt Evaluator...")
    
    # Initialize evaluator
    data_dir = project_root / "data"
    evaluator = ReceiptEvaluator(str(data_dir))
    
    # Check if data directory exists
    print(f"📁 Data directory: {evaluator.training_wheels_dir}")
    print(f"💾 Results directory: {evaluator.results_dir}")
    
    if not evaluator.training_wheels_dir.exists():
        print("❌ Training wheels directory not found!")
        return False
    
    # Get receipt files
    receipt_files = evaluator.get_receipt_files()
    print(f"📄 Found {len(receipt_files)} receipt files")
    
    if not receipt_files:
        print("❌ No receipt files found!")
        return False
    
    # Test with first receipt
    print(f"🔍 Testing with first receipt: {Path(receipt_files[0][0]).name}")
    
    try:
        result = evaluator.evaluate_receipt(receipt_files[0][0], receipt_files[0][1])
        
        print(f"📊 Extraction successful: {result.extraction_successful}")
        if result.extraction_successful:
            print(f"📈 Pass rate: {result.pass_rate:.1%}")
            print(f"✅ Overall passed: {result.overall_passed}")
            
            print("\n📋 Evaluation results:")
            for eval_result in result.evaluations:
                status = "✅" if eval_result.passed else "❌"
                print(f"  {status} {eval_result.check_name}: {eval_result.message}")
        else:
            print(f"❌ Extraction error: {result.extraction_error}")
        
        print("\n✅ Basic functionality test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_save_load_functionality():
    """Test save and load functionality."""
    print("\n🧪 Testing Save/Load Functionality...")
    
    data_dir = project_root / "data"
    evaluator = ReceiptEvaluator(str(data_dir))
    
    # Create mock results for testing
    from src.receipt_evaluator import ReceiptEvaluationResult, EvaluationResult
    
    mock_results = [
        ReceiptEvaluationResult(
            receipt_id="test_001",
            image_path="/test/path.png",
            extraction_successful=True,
            evaluations=[
                EvaluationResult("sum_validation", True, "Test passed"),
                EvaluationResult("positive_values", False, "Test failed")
            ]
        ),
        ReceiptEvaluationResult(
            receipt_id="test_002",
            image_path="/test/path2.png",
            extraction_successful=False,
            extraction_error="Mock error"
        )
    ]
    
    try:
        # Test saving
        test_run_id = "test_run_" + datetime.now().strftime("%Y%m%d_%H%M%S")
        saved_run_id = evaluator.save_results(mock_results, test_run_id)
        print(f"💾 Saved results with ID: {saved_run_id}")
        
        # Test loading
        loaded_results, loaded_summary = evaluator.load_results(saved_run_id)
        print(f"📂 Loaded {len(loaded_results)} results")
        
        # Test listing runs
        available_runs = evaluator.list_available_runs()
        print(f"📋 Found {len(available_runs)} available runs")
        
        # Verify the test run is in the list
        test_run_found = any(run['run_id'] == saved_run_id for run in available_runs)
        if test_run_found:
            print(f"✅ Test run found in available runs list")
        else:
            print(f"❌ Test run not found in available runs list")
            return False
        
        # Clean up test run
        import shutil
        test_run_dir = evaluator.results_dir / saved_run_id
        if test_run_dir.exists():
            shutil.rmtree(test_run_dir)
            print(f"🧹 Cleaned up test run directory")
        
        print("\n✅ Save/Load functionality test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error during save/load testing: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_summary_stats():
    """Test summary statistics generation."""
    print("\n🧪 Testing Summary Statistics...")
    
    data_dir = project_root / "data"
    evaluator = ReceiptEvaluator(str(data_dir))
    
    # Create mock results for testing
    from src.receipt_evaluator import ReceiptEvaluationResult, EvaluationResult
    
    mock_results = [
        ReceiptEvaluationResult(
            receipt_id="test_001",
            image_path="/test/path.png",
            extraction_successful=True,
            evaluations=[
                EvaluationResult("sum_validation", True, "Test passed"),
                EvaluationResult("positive_values", False, "Test failed")
            ]
        ),
        ReceiptEvaluationResult(
            receipt_id="test_002",
            image_path="/test/path2.png",
            extraction_successful=False,
            extraction_error="Mock error"
        )
    ]
    
    try:
        stats = evaluator.get_summary_statistics(mock_results)
        
        print(f"📊 Total receipts: {stats['total_receipts']}")
        print(f"📈 Extraction success rate: {stats['extraction_success_rate']:.1%}")
        print(f"✅ Overall pass rate: {stats['overall_pass_rate']:.1%}")
        
        print("\n✅ Summary statistics test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error during summary stats testing: {str(e)}")
        return False


def main():
    """Run all tests."""
    print("🚀 Starting Receipt Evaluator Tests...\n")
    
    tests_passed = 0
    total_tests = 3
    
    if test_basic_functionality():
        tests_passed += 1
    
    if test_save_load_functionality():
        tests_passed += 1
    
    if test_summary_stats():
        tests_passed += 1
    
    print(f"\n📊 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed!")
        return True
    else:
        print("❌ Some tests failed!")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
