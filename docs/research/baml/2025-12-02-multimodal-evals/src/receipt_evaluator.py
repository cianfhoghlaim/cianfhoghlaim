"""
Receipt Evaluation Module

This module processes receipt images using BAML extraction and applies comprehensive
runtime evaluations to validate the extracted data.
"""

import os
import json
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import base64
import tempfile
from PIL import Image as PILImage, ImageEnhance
from dotenv import load_dotenv
from baml_client.async_client import b
from baml_client.types import ReceiptData
from baml_py import Image

# Load environment variables
load_dotenv()

@dataclass
class EvaluationResult:
    """Represents the result of a single evaluation check."""
    check_name: str
    passed: bool
    message: str
    expected_value: Optional[Any] = None
    actual_value: Optional[Any] = None


@dataclass
class ReceiptEvaluationResult:
    """Represents the complete evaluation result for a single receipt."""
    receipt_id: str
    image_path: str
    extraction_successful: bool
    extraction_error: Optional[str] = None
    extracted_data: Optional[ReceiptData] = None
    evaluations: List[EvaluationResult] = field(default_factory=list)
    retry_attempted: bool = False
    first_attempt_data: Optional[ReceiptData] = None
    first_attempt_evaluations: List[EvaluationResult] = field(default_factory=list)
    
    @property
    def overall_passed(self) -> bool:
        """Returns True if extraction was successful and all evaluations passed."""
        return self.extraction_successful and all(eval.passed for eval in self.evaluations)
    
    @property
    def pass_rate(self) -> float:
        """Returns the percentage of evaluations that passed."""
        if not self.evaluations:
            return 0.0
        return sum(1 for eval in self.evaluations if eval.passed) / len(self.evaluations)


class ReceiptEvaluator:
    """Main class for evaluating receipt extraction results."""
    
    def __init__(self, data_dir: str, results_dir: Optional[str] = None):
        self.data_dir = Path(data_dir)
        self.training_wheels_dir = self.data_dir / "cord-v2" / "images_and_metadata" / "train_100"
        
        # Set up results directory
        if results_dir:
            self.results_dir = Path(results_dir)
        else:
            self.results_dir = self.data_dir.parent / "results"
        
        # Create results directory if it doesn't exist
        self.results_dir.mkdir(exist_ok=True)
        
    def get_receipt_files(self) -> List[Tuple[str, str]]:
        """Get all receipt image files and their corresponding metadata files."""
        receipt_files = []
        
        for png_file in self.training_wheels_dir.glob("train_*.png"):
            receipt_id = png_file.stem
            metadata_file = self.training_wheels_dir / f"{receipt_id}_metadata.json"
            
            if metadata_file.exists():
                receipt_files.append((str(png_file), str(metadata_file)))
            else:
                receipt_files.append((str(png_file), None))
        
        return sorted(receipt_files)
    
    def convert_to_grayscale_and_enhance(
        self,
        input_path: str, 
        output_path: str, 
        contrast_factor: float = 1
    ) -> PILImage.Image:
        """
        Convert a PNG to grayscale and increase contrast.
        
        Args:
            input_path: Path to input PNG file
            output_path: Path to save the output image
            contrast_factor: Contrast enhancement factor (1.0 = no change, >1.0 = more contrast)
        
        Returns:
            PIL Image object in grayscale mode ('L')
        """
        # Open the image
        img = PILImage.open(input_path)
        
        # Convert to grayscale
        # grayscale_img = img.convert('L')
        
        # Enhance contrast
        enhancer = ImageEnhance.Contrast(img)
        enhanced_img = enhancer.enhance(contrast_factor)
        
        # Save the result
        enhanced_img.save(output_path)
        
        return enhanced_img
    
    async def extract_receipt_data(self, image_path: str) -> Tuple[bool, Optional[ReceiptData], Optional[str]]:
        """Extract receipt data using BAML with image preprocessing."""
        try:
            # Create a temporary file for the processed image
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                temp_path = temp_file.name
            
            try:
                # Preprocess the image (convert to grayscale and enhance contrast)
                self.convert_to_grayscale_and_enhance(image_path, temp_path)
                
                # Read the processed image
                with open(temp_path, "rb") as image_file:
                    image_data = image_file.read()
                base64_string = base64.b64encode(image_data).decode('utf-8')
                image = Image.from_base64("image/png", base64_string)
                extracted_data = await b.ExtractReceiptTransactions(image)
                return True, extracted_data, None
            finally:
                # Clean up the temporary file
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
        except Exception as e:
            return False, None, str(e)
    
    def evaluate_sum_validation(self, data: ReceiptData) -> EvaluationResult:
        """Check if sum of transactions + service charge + tax + rounding - discount_on_total equals grand_total."""
        try:
            transaction_sum = sum(transaction.total_price for transaction in data.transactions)
            
            # Start with transaction sum
            calculated_total = transaction_sum
            components = [f"transactions: {transaction_sum:.2f}"]
            
            # Add service charge if present
            if data.service_charge is not None:
                calculated_total += data.service_charge
                components.append(f"service: {data.service_charge:.2f}")
            
            # Add tax if present
            if data.tax is not None:
                calculated_total += data.tax
                components.append(f"tax: {data.tax:.2f}")
            
            # Add rounding if present
            if data.rounding is not None:
                calculated_total += data.rounding
                components.append(f"rounding: {data.rounding:.2f}")
            
            # Subtract absolute value of discount_on_total if present
            # This handles both positive and negative discount values properly
            if data.discount_on_total is not None:
                discount_amount = abs(data.discount_on_total)
                calculated_total -= discount_amount
                components.append(f"discount: -{discount_amount:.2f}")
            
            # Allow for small floating point differences
            tolerance = 0.01
            difference = abs(calculated_total - data.grand_total)
            
            passed = difference <= tolerance
            message = f"Calculated total: {calculated_total:.2f} ({' + '.join(components)}), Grand total: {data.grand_total:.2f}"
            if not passed:
                message += f" (difference: {difference:.2f})"
            
            return EvaluationResult(
                check_name="sum_validation",
                passed=passed,
                message=message,
                expected_value=data.grand_total,
                actual_value=calculated_total
            )
        except Exception as e:
            return EvaluationResult(
                check_name="sum_validation",
                passed=False,
                message=f"Error during sum validation: {str(e)}"
            )
    
    def evaluate_positive_values(self, data: ReceiptData) -> EvaluationResult:
        """Ensure all monetary values (except rounding and discount) are positive."""
        try:
            negative_values = []
            
            # Check transaction values
            for i, transaction in enumerate(data.transactions):
                if transaction.total_price < 0:
                    negative_values.append(f"Transaction {i+1} total_price: {transaction.total_price}")
                if transaction.unit_price < 0:
                    negative_values.append(f"Transaction {i+1} unit_price: {transaction.unit_price}")
                if transaction.quantity < 0:
                    negative_values.append(f"Transaction {i+1} quantity: {transaction.quantity}")
            
            # Check receipt totals (excluding rounding and discount which can be negative)
            if data.subtotal is not None and data.subtotal < 0:
                negative_values.append(f"Subtotal: {data.subtotal}")
            if data.service_charge is not None and data.service_charge < 0:
                negative_values.append(f"Service charge: {data.service_charge}")
            if data.tax is not None and data.tax < 0:
                negative_values.append(f"Tax: {data.tax}")
            if data.grand_total < 0:
                negative_values.append(f"Grand total: {data.grand_total}")
            
            # Note: discount and rounding are excluded from positive value checks as they can legitimately be negative
            
            passed = len(negative_values) == 0
            message = "All values are positive" if passed else f"Negative values found: {', '.join(negative_values)}"
            
            return EvaluationResult(
                check_name="positive_values",
                passed=passed,
                message=message
            )
        except Exception as e:
            return EvaluationResult(
                check_name="positive_values",
                passed=False,
                message=f"Error during positive values check: {str(e)}"
            )
    
    def evaluate_subtotal_consistency(self, data: ReceiptData) -> EvaluationResult:
        """Verify sum of transactions equals subtotal when present."""
        try:
            if data.subtotal is None:
                return EvaluationResult(
                    check_name="subtotal_consistency",
                    passed=True,
                    message="No subtotal present, check skipped"
                )
            
            transaction_sum = sum(transaction.total_price for transaction in data.transactions)
            
            # Allow for small floating point differences
            tolerance = 0.01
            difference = abs(transaction_sum - data.subtotal)
            
            passed = difference <= tolerance
            message = f"Transaction sum: {transaction_sum:.2f}, Subtotal: {data.subtotal:.2f}"
            if not passed:
                message += f" (difference: {difference:.2f})"
            
            return EvaluationResult(
                check_name="subtotal_consistency",
                passed=passed,
                message=message,
                expected_value=data.subtotal,
                actual_value=transaction_sum
            )
        except Exception as e:
            return EvaluationResult(
                check_name="subtotal_consistency",
                passed=False,
                message=f"Error during subtotal consistency check: {str(e)}"
            )
    
    def evaluate_unit_price_accuracy(self, data: ReceiptData) -> EvaluationResult:
        """Check (unit_price - unit_discount) * quantity = total_price for each transaction."""
        try:
            errors = []
            tolerance = 0.01
            
            for i, transaction in enumerate(data.transactions):
                # Calculate effective unit price after discount
                effective_unit_price = transaction.unit_price
                if transaction.unit_discount is not None:
                    # Subtract absolute value of discount from unit price
                    effective_unit_price -= abs(transaction.unit_discount)
                
                expected_total = effective_unit_price * transaction.quantity
                difference = abs(expected_total - transaction.total_price)
                
                if difference > tolerance:
                    if transaction.unit_discount is not None:
                        errors.append(
                            f"Transaction {i+1} ({transaction.item_name}): "
                            f"({transaction.unit_price} - {abs(transaction.unit_discount)}) × {transaction.quantity} = {expected_total:.2f}, "
                            f"but total_price is {transaction.total_price:.2f}"
                        )
                    else:
                        errors.append(
                            f"Transaction {i+1} ({transaction.item_name}): "
                            f"{transaction.unit_price} × {transaction.quantity} = {expected_total:.2f}, "
                            f"but total_price is {transaction.total_price:.2f}"
                        )
            
            passed = len(errors) == 0
            message = "All unit price calculations are correct" if passed else f"Errors: {'; '.join(errors)}"
            
            return EvaluationResult(
                check_name="unit_price_accuracy",
                passed=passed,
                message=message
            )
        except Exception as e:
            return EvaluationResult(
                check_name="unit_price_accuracy",
                passed=False,
                message=f"Error during unit price accuracy check: {str(e)}"
            )
    
    def evaluate_grand_total_calculation(self, data: ReceiptData) -> EvaluationResult:
        """Verify subtotal + service_charge + tax + rounding - discount_on_total = grand_total."""
        try:
            calculated_total = 0.0
            components = []
            
            if data.subtotal is not None:
                calculated_total += data.subtotal
                components.append(f"subtotal: {data.subtotal}")
            else:
                # If no subtotal, use sum of transactions
                transaction_sum = sum(transaction.total_price for transaction in data.transactions)
                calculated_total += transaction_sum
                components.append(f"transaction sum: {transaction_sum}")
            
            if data.service_charge is not None:
                calculated_total += data.service_charge
                components.append(f"service: {data.service_charge}")
            
            if data.tax is not None:
                calculated_total += data.tax
                components.append(f"tax: {data.tax}")
            
            if data.rounding is not None:
                calculated_total += data.rounding
                components.append(f"rounding: {data.rounding}")
            
            # Subtract absolute value of discount_on_total if present
            # This handles both positive and negative discount values properly
            if data.discount_on_total is not None:
                discount_amount = abs(data.discount_on_total)
                calculated_total -= discount_amount
                components.append(f"discount: -{discount_amount:.2f}")
            
            tolerance = 0.01
            difference = abs(calculated_total - data.grand_total)
            
            passed = difference <= tolerance
            message = f"Calculated: {calculated_total:.2f} ({' + '.join(components)}), Grand total: {data.grand_total:.2f}"
            if not passed:
                message += f" (difference: {difference:.2f})"
            
            return EvaluationResult(
                check_name="grand_total_calculation",
                passed=passed,
                message=message,
                expected_value=data.grand_total,
                actual_value=calculated_total
            )
        except Exception as e:
            return EvaluationResult(
                check_name="grand_total_calculation",
                passed=False,
                message=f"Error during grand total calculation check: {str(e)}"
            )
    
    def evaluate_data_completeness(self, data: ReceiptData) -> EvaluationResult:
        """Check for missing required fields."""
        try:
            missing_fields = []
            
            # Check required fields
            if not data.transactions:
                missing_fields.append("transactions (empty list)")
            
            if data.grand_total is None:
                missing_fields.append("grand_total")
            
            # Check transaction completeness
            for i, transaction in enumerate(data.transactions):
                if not transaction.item_name or transaction.item_name.strip() == "":
                    missing_fields.append(f"Transaction {i+1} item_name")
                if transaction.quantity is None:
                    missing_fields.append(f"Transaction {i+1} quantity")
                if transaction.unit_price is None:
                    missing_fields.append(f"Transaction {i+1} unit_price")
                if transaction.total_price is None:
                    missing_fields.append(f"Transaction {i+1} total_price")
            
            passed = len(missing_fields) == 0
            message = "All required fields present" if passed else f"Missing fields: {', '.join(missing_fields)}"
            
            return EvaluationResult(
                check_name="data_completeness",
                passed=passed,
                message=message
            )
        except Exception as e:
            return EvaluationResult(
                check_name="data_completeness",
                passed=False,
                message=f"Error during data completeness check: {str(e)}"
            )
    
    async def evaluate_receipt(self, image_path: str, metadata_path: Optional[str] = None) -> ReceiptEvaluationResult:
        """Evaluate a single receipt with retry logic for failed evaluations."""
        receipt_id = Path(image_path).stem
        
        # First attempt: Extract data using BAML
        extraction_successful, extracted_data, extraction_error = await self.extract_receipt_data(image_path)
        
        result = ReceiptEvaluationResult(
            receipt_id=receipt_id,
            image_path=image_path,
            extraction_successful=extraction_successful,
            extraction_error=extraction_error,
            extracted_data=extracted_data
        )
        
        # If extraction failed, return early (no retry for extraction failures)
        if not extraction_successful or extracted_data is None:
            return result
        
        # Run all evaluations on first attempt
        first_evaluations = [
            self.evaluate_sum_validation(extracted_data),
            self.evaluate_positive_values(extracted_data),
            self.evaluate_subtotal_consistency(extracted_data),
            self.evaluate_unit_price_accuracy(extracted_data),
            self.evaluate_grand_total_calculation(extracted_data),
            self.evaluate_data_completeness(extracted_data)
        ]
        
        result.evaluations = first_evaluations
        
        # Check if any evaluations failed - if so, retry extraction
        if not result.overall_passed:
            print(f"  ⚠️  First attempt failed evaluations for {receipt_id}, retrying extraction...")
            
            # Store first attempt data
            result.first_attempt_data = extracted_data
            result.first_attempt_evaluations = first_evaluations
            result.retry_attempted = True
            
            # Second attempt: Extract data again
            retry_extraction_successful, retry_extracted_data, retry_extraction_error = await self.extract_receipt_data(image_path)
            
            # Update result with second attempt (regardless of success/failure)
            result.extraction_successful = retry_extraction_successful
            result.extraction_error = retry_extraction_error
            result.extracted_data = retry_extracted_data
            
            if retry_extraction_successful and retry_extracted_data is not None:
                # Run evaluations on second attempt
                retry_evaluations = [
                    self.evaluate_sum_validation(retry_extracted_data),
                    self.evaluate_positive_values(retry_extracted_data),
                    self.evaluate_subtotal_consistency(retry_extracted_data),
                    self.evaluate_unit_price_accuracy(retry_extracted_data),
                    self.evaluate_grand_total_calculation(retry_extracted_data),
                    self.evaluate_data_completeness(retry_extracted_data)
                ]
                result.evaluations = retry_evaluations
                
                # Log retry outcome
                if result.overall_passed:
                    print(f"  ✅ Retry successful for {receipt_id}")
                else:
                    print(f"  ❌ Retry also failed for {receipt_id}")
            else:
                # Second extraction failed, clear evaluations
                result.evaluations = []
                print(f"  ❌ Retry extraction failed for {receipt_id}")
        
        return result
    
    def evaluate_all_receipts(self) -> List[ReceiptEvaluationResult]:
        """Evaluate all receipts in the training_wheels dataset (synchronous wrapper)."""
        return asyncio.run(self.evaluate_all_receipts_async())
    
    async def evaluate_all_receipts_async(self, max_concurrent: int = 10) -> List[ReceiptEvaluationResult]:
        """Evaluate all receipts in the training_wheels dataset with async concurrency control.
        
        Args:
            max_concurrent: Maximum number of concurrent API calls (default: 10)
        
        Returns:
            List of evaluation results for all receipts
        """
        receipt_files = self.get_receipt_files()
        semaphore = asyncio.Semaphore(max_concurrent)
        completed_count = 0
        total_count = len(receipt_files)
        
        print(f"Found {total_count} receipts to evaluate (max {max_concurrent} concurrent)...")
        
        async def process_with_semaphore(image_path: str, metadata_path: Optional[str], index: int) -> ReceiptEvaluationResult:
            nonlocal completed_count
            async with semaphore:
                try:
                    result = await self.evaluate_receipt(image_path, metadata_path)
                    completed_count += 1
                    print(f"[{completed_count}/{total_count}] Processed: {Path(image_path).name}")
                    return result
                except Exception as e:
                    # Create a failed result for unexpected errors
                    receipt_id = Path(image_path).stem
                    completed_count += 1
                    print(f"[{completed_count}/{total_count}] Failed: {Path(image_path).name} - {str(e)}")
                    return ReceiptEvaluationResult(
                        receipt_id=receipt_id,
                        image_path=image_path,
                        extraction_successful=False,
                        extraction_error=f"Unexpected error: {str(e)}"
                    )
        
        # Create tasks for all receipts
        tasks = [
            process_with_semaphore(image_path, metadata_path, i)
            for i, (image_path, metadata_path) in enumerate(receipt_files)
        ]
        
        # Run all tasks concurrently with semaphore limiting
        results = await asyncio.gather(*tasks)
        
        return list(results)
    
    def get_summary_statistics(self, results: List[ReceiptEvaluationResult]) -> Dict[str, Any]:
        """Generate summary statistics from evaluation results."""
        total_receipts = len(results)
        successful_extractions = sum(1 for r in results if r.extraction_successful)
        overall_passed = sum(1 for r in results if r.overall_passed)
        
        # Evaluation statistics by type
        eval_stats = {}
        if results and results[0].evaluations:
            for eval_result in results[0].evaluations:
                check_name = eval_result.check_name
                passed_count = sum(1 for r in results 
                                 if r.extraction_successful and 
                                 any(e.check_name == check_name and e.passed for e in r.evaluations))
                eval_stats[check_name] = {
                    'passed': passed_count,
                    'total': successful_extractions,
                    'pass_rate': passed_count / successful_extractions if successful_extractions > 0 else 0
                }
        
        return {
            'total_receipts': total_receipts,
            'successful_extractions': successful_extractions,
            'extraction_success_rate': successful_extractions / total_receipts if total_receipts > 0 else 0,
            'overall_passed': overall_passed,
            'overall_pass_rate': overall_passed / total_receipts if total_receipts > 0 else 0,
            'evaluation_statistics': eval_stats,
            'timestamp': datetime.now().isoformat()
        }
    
    def save_results(self, results: List[ReceiptEvaluationResult], run_id: Optional[str] = None, run_name: Optional[str] = None) -> str:
        """Save evaluation results to disk."""
        if run_id is None:
            run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create run directory
        run_dir = self.results_dir / run_id
        run_dir.mkdir(exist_ok=True)
        
        # Prepare data for serialization
        results_data = []
        for result in results:
            result_dict = {
                "receipt_id": result.receipt_id,
                "image_path": result.image_path,
                "extraction_successful": result.extraction_successful,
                "extraction_error": result.extraction_error,
                "overall_passed": result.overall_passed,
                "pass_rate": result.pass_rate,
                "retry_attempted": result.retry_attempted,
                "evaluations": [
                    {
                        "check_name": e.check_name,
                        "passed": e.passed,
                        "message": e.message,
                        "expected_value": e.expected_value,
                        "actual_value": e.actual_value
                    } for e in result.evaluations
                ]
            }
            
            # Add extracted data if available
            if result.extracted_data:
                result_dict["extracted_data"] = {
                    "transactions": [
                        {
                            "item_name": t.item_name,
                            "quantity": t.quantity,
                            "unit_price": t.unit_price,
                            "unit_discount": t.unit_discount,
                            "total_price": t.total_price
                        } for t in result.extracted_data.transactions
                    ],
                    "subtotal": result.extracted_data.subtotal,
                    "service_charge": result.extracted_data.service_charge,
                    "tax": result.extracted_data.tax,
                    "rounding": result.extracted_data.rounding,
                    "discount_on_total": result.extracted_data.discount_on_total,
                    "grand_total": result.extracted_data.grand_total
                }
            
            # Add first attempt data if retry was attempted
            if result.retry_attempted:
                result_dict["first_attempt_evaluations"] = [
                    {
                        "check_name": e.check_name,
                        "passed": e.passed,
                        "message": e.message,
                        "expected_value": e.expected_value,
                        "actual_value": e.actual_value
                    } for e in result.first_attempt_evaluations
                ]
                
                if result.first_attempt_data:
                    result_dict["first_attempt_data"] = {
                        "transactions": [
                            {
                                "item_name": t.item_name,
                                "quantity": t.quantity,
                                "unit_price": t.unit_price,
                                "unit_discount": t.unit_discount,
                                "total_price": t.total_price
                            } for t in result.first_attempt_data.transactions
                        ],
                        "subtotal": result.first_attempt_data.subtotal,
                        "service_charge": result.first_attempt_data.service_charge,
                        "tax": result.first_attempt_data.tax,
                        "rounding": result.first_attempt_data.rounding,
                        "discount_on_total": result.first_attempt_data.discount_on_total,
                        "grand_total": result.first_attempt_data.grand_total
                    }
                       
            results_data.append(result_dict)
        
        # Generate summary statistics
        summary_stats = self.get_summary_statistics(results)
        
        # Save detailed results
        results_file = run_dir / "detailed_results.json"
        with open(results_file, 'w') as f:
            json.dump(results_data, f, indent=2, default=str)
        
        # Save summary statistics
        summary_file = run_dir / "summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary_stats, f, indent=2, default=str)
        
        # Save metadata
        metadata = {
            "run_id": run_id,
            "run_name": run_name,
            "timestamp": datetime.now().isoformat(),
            "total_receipts": len(results),
            "data_directory": str(self.training_wheels_dir),
            "results_directory": str(run_dir)
        }
        
        metadata_file = run_dir / "metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2, default=str)
        
        print(f"✅ Results saved to: {run_dir}")
        return run_id
    
    def load_results(self, run_id: str) -> Tuple[List[ReceiptEvaluationResult], Dict[str, Any]]:
        """Load evaluation results from disk."""
        run_dir = self.results_dir / run_id
        
        if not run_dir.exists():
            raise FileNotFoundError(f"Results directory not found: {run_dir}")
        
        # Load detailed results
        results_file = run_dir / "detailed_results.json"
        if not results_file.exists():
            raise FileNotFoundError(f"Detailed results file not found: {results_file}")
        
        with open(results_file, 'r') as f:
            results_data = json.load(f)
        
        # Load summary
        summary_file = run_dir / "summary.json"
        if summary_file.exists():
            with open(summary_file, 'r') as f:
                summary_stats = json.load(f)
        else:
            summary_stats = {}
        
        # Load metadata
        metadata_file = run_dir / "metadata.json"
        if metadata_file.exists():
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            # Merge metadata into summary_stats for backward compatibility
            summary_stats.update(metadata)
        else:
            # Ensure run_id is available even without metadata file
            summary_stats['run_id'] = run_id
        
        # Reconstruct ReceiptEvaluationResult objects
        results = []
        for result_dict in results_data:
            evaluations = [
                EvaluationResult(
                    check_name=e["check_name"],
                    passed=e["passed"],
                    message=e["message"],
                    expected_value=e.get("expected_value"),
                    actual_value=e.get("actual_value")
                ) for e in result_dict["evaluations"]
            ]
            
            # Reconstruct extracted data if available
            extracted_data = None
            if "extracted_data" in result_dict and result_dict["extracted_data"]:
                from baml_client.types import Transaction
                
                transactions = [
                    Transaction(
                        item_name=t["item_name"],
                        quantity=t["quantity"],
                        unit_price=t["unit_price"],
                        unit_discount=t.get("unit_discount"),  # Backward compatibility
                        total_price=t["total_price"]
                    ) for t in result_dict["extracted_data"]["transactions"]
                ]
                
                # Handle both old and new field names for discount
                # Old: "discount", New: "discount_on_total"
                discount_value = result_dict["extracted_data"].get("discount_on_total") or result_dict["extracted_data"].get("discount")
                
                extracted_data = ReceiptData(
                    transactions=transactions,
                    subtotal=result_dict["extracted_data"]["subtotal"],
                    service_charge=result_dict["extracted_data"]["service_charge"],
                    tax=result_dict["extracted_data"]["tax"],
                    rounding=result_dict["extracted_data"]["rounding"],
                    discount_on_total=discount_value,  # Backward compatibility
                    grand_total=result_dict["extracted_data"]["grand_total"]
                )
                       
            # Reconstruct first attempt data if available
            first_attempt_data = None
            first_attempt_evaluations = []
            retry_attempted = result_dict.get("retry_attempted", False)
            
            if retry_attempted and "first_attempt_data" in result_dict and result_dict["first_attempt_data"]:
                from baml_client.types import Transaction
                
                first_transactions = [
                    Transaction(
                        item_name=t["item_name"],
                        quantity=t["quantity"],
                        unit_price=t["unit_price"],
                        unit_discount=t.get("unit_discount"),
                        total_price=t["total_price"]
                    ) for t in result_dict["first_attempt_data"]["transactions"]
                ]
                
                first_discount_value = result_dict["first_attempt_data"].get("discount_on_total") or result_dict["first_attempt_data"].get("discount")
                
                first_attempt_data = ReceiptData(
                    transactions=first_transactions,
                    subtotal=result_dict["first_attempt_data"]["subtotal"],
                    service_charge=result_dict["first_attempt_data"]["service_charge"],
                    tax=result_dict["first_attempt_data"]["tax"],
                    rounding=result_dict["first_attempt_data"]["rounding"],
                    discount_on_total=first_discount_value,
                    grand_total=result_dict["first_attempt_data"]["grand_total"]
                )
            
            if retry_attempted and "first_attempt_evaluations" in result_dict:
                first_attempt_evaluations = [
                    EvaluationResult(
                        check_name=e["check_name"],
                        passed=e["passed"],
                        message=e["message"],
                        expected_value=e.get("expected_value"),
                        actual_value=e.get("actual_value")
                    ) for e in result_dict["first_attempt_evaluations"]
                ]
            
            result = ReceiptEvaluationResult(
                receipt_id=result_dict["receipt_id"],
                image_path=result_dict["image_path"],
                extraction_successful=result_dict["extraction_successful"],
                extraction_error=result_dict.get("extraction_error"),
                extracted_data=extracted_data,
                evaluations=evaluations,
                retry_attempted=retry_attempted,
                first_attempt_data=first_attempt_data,
                first_attempt_evaluations=first_attempt_evaluations
            )
            
            results.append(result)
        
        return results, summary_stats
    
    def list_available_runs(self) -> List[Dict[str, Any]]:
        """List all available evaluation runs."""
        runs = []
        
        if not self.results_dir.exists():
            return runs
        
        for run_dir in self.results_dir.iterdir():
            if run_dir.is_dir():
                metadata_file = run_dir / "metadata.json"
                if metadata_file.exists():
                    try:
                        with open(metadata_file, 'r') as f:
                            metadata = json.load(f)
                        runs.append(metadata)
                    except Exception:
                        # Skip corrupted metadata files
                        continue
                else:
                    # Create basic metadata for runs without metadata file
                    runs.append({
                        "run_id": run_dir.name,
                        "timestamp": datetime.fromtimestamp(run_dir.stat().st_mtime).isoformat(),
                        "results_directory": str(run_dir)
                    })
        
        # Sort by timestamp (newest first)
        runs.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return runs


def run_evaluation_cli(data_dir: str, results_dir: Optional[str] = None, run_id: Optional[str] = None, run_name: Optional[str] = None, concurrency: int = 10):
    """CLI interface to run evaluations and save results."""
    print("🚀 Starting Receipt Evaluation (Async)...")
    
    evaluator = ReceiptEvaluator(data_dir, results_dir)
    
    print(f"📁 Data directory: {evaluator.training_wheels_dir}")
    print(f"💾 Results directory: {evaluator.results_dir}")
    print(f"⚡ Concurrency: {concurrency} concurrent requests")
    
    # Run evaluations asynchronously
    results = asyncio.run(evaluator.evaluate_all_receipts_async(max_concurrent=concurrency))
    
    # Save results
    saved_run_id = evaluator.save_results(results, run_id, run_name)
    
    # Display summary
    print("\n" + "="*50)
    print("EVALUATION SUMMARY")
    print("="*50)
    
    stats = evaluator.get_summary_statistics(results)
    print(f"Total receipts: {stats['total_receipts']}")
    print(f"Successful extractions: {stats['successful_extractions']} ({stats['extraction_success_rate']:.1%})")
    print(f"Overall passed: {stats['overall_passed']} ({stats['overall_pass_rate']:.1%})")
    
    print("\nEvaluation breakdown:")
    for check_name, check_stats in stats['evaluation_statistics'].items():
        print(f"  {check_name}: {check_stats['passed']}/{check_stats['total']} ({check_stats['pass_rate']:.1%})")
    
    # Show failed receipts
    failed_receipts = [r for r in results if not r.overall_passed]
    if failed_receipts:
        print(f"\nFailed receipts ({len(failed_receipts)}):")
        for result in failed_receipts[:5]:  # Show first 5 failures
            print(f"  {result.receipt_id}: ", end="")
            if not result.extraction_successful:
                print(f"Extraction failed - {result.extraction_error}")
            else:
                failed_evals = [e.check_name for e in result.evaluations if not e.passed]
                print(f"Failed evaluations: {', '.join(failed_evals)}")
        
        if len(failed_receipts) > 5:
            print(f"  ... and {len(failed_receipts) - 5} more failures")
    
    print(f"\n💾 Results saved with ID: {saved_run_id}")
    print("📊 View results in Streamlit dashboard or load programmatically")
    
    return saved_run_id


def main():
    """Main function - CLI interface."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Receipt Evaluation System")
    parser.add_argument(
        "--data-dir", 
        default="/Users/kevingregory/Desktop/development/python/ai-that-works/2025-12-02-multimodal-evals/data",
        help="Path to data directory containing receipt images"
    )
    parser.add_argument(
        "--results-dir",
        help="Path to results directory (default: data_dir/../results)"
    )
    parser.add_argument(
        "--run-id",
        help="Custom run ID (default: timestamp)"
    )
    parser.add_argument(
        "--run-name",
        help="Human-readable name for this evaluation run"
    )
    parser.add_argument(
        "--list-runs",
        action="store_true",
        help="List available evaluation runs"
    )
    parser.add_argument(
        "--load-run",
        help="Load and display results from a specific run ID"
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=10,
        help="Maximum number of concurrent API calls (default: 10)"
    )
    
    args = parser.parse_args()
    
    if args.list_runs:
        evaluator = ReceiptEvaluator(args.data_dir, args.results_dir)
        runs = evaluator.list_available_runs()
        
        if not runs:
            print("No evaluation runs found.")
            return
        
        print("Available evaluation runs:")
        print("-" * 50)
        for run in runs:
            run_name = run.get("run_name")
            timestamp = run.get("timestamp", "Unknown")
            total_receipts = run.get("total_receipts", "Unknown")
            
            if run_name:
                print(f"Name: {run_name}")
                print(f"  ID: {run['run_id']}")
            else:
                print(f"ID: {run['run_id']}")
            
            print(f"  Timestamp: {timestamp}")
            print(f"  Total receipts: {total_receipts}")
            print()
        
        return
    
    if args.load_run:
        evaluator = ReceiptEvaluator(args.data_dir, args.results_dir)
        try:
            results, stats = evaluator.load_results(args.load_run)
            
            print(f"📊 Loaded results for run: {args.load_run}")
            print("-" * 50)
            print(f"Total receipts: {stats.get('total_receipts', len(results))}")
            print(f"Successful extractions: {stats.get('successful_extractions', 'Unknown')}")
            print(f"Overall pass rate: {stats.get('overall_pass_rate', 0):.1%}")
            
            if 'evaluation_statistics' in stats:
                print("\nEvaluation breakdown:")
                for check_name, check_stats in stats['evaluation_statistics'].items():
                    print(f"  {check_name}: {check_stats['passed']}/{check_stats['total']} ({check_stats['pass_rate']:.1%})")
            
        except FileNotFoundError as e:
            print(f"❌ Error: {e}")
        
        return
    
    # Run evaluation
    run_evaluation_cli(args.data_dir, args.results_dir, args.run_id, args.run_name, args.concurrency)


if __name__ == "__main__":
    main()
