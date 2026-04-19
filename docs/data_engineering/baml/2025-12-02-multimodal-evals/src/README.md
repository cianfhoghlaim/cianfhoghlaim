# Receipt Evaluation System

A comprehensive system for evaluating receipt extraction accuracy using BAML (Basically, A Made-Up Language) and runtime validation checks.

## Features

### 🧾 Receipt Processing
- Processes receipt images from the CORD-v2 training_wheels dataset
- Uses BAML's `ExtractReceiptTransactions` function for data extraction
- Handles extraction failures gracefully

### 🔍 Comprehensive Evaluations
1. **Sum Validation**: Verifies that the sum of all transaction total_prices equals the grand_total
2. **Positive Values**: Ensures all monetary values (except rounding) are positive
3. **Subtotal Consistency**: Verifies that the sum of transactions equals the subtotal when present
4. **Unit Price Accuracy**: Checks that unit_price × quantity = total_price for each transaction
5. **Grand Total Calculation**: Verifies that subtotal + service_charge + tax + rounding = grand_total
6. **Data Completeness**: Checks for missing required fields

### 📊 Interactive Dashboard
- Streamlit-based web interface
- File-based architecture for stability
- Visual charts and statistics
- Detailed per-receipt analysis
- Export functionality

## Quick Start

### 1. Install Dependencies
```bash
# From the project root directory
pip install -e .
```

### 2. Run Evaluations (CLI)
```bash
# Run evaluations and save results
uv run python src/receipt_evaluator.py

# List available evaluation runs
uv run python src/receipt_evaluator.py --list-runs

# Load specific run results
uv run python src/receipt_evaluator.py --load-run RUN_ID
```

### 3. Launch the Dashboard
```bash
# Option 1: Using the launch script
python src/run_streamlit.py

# Option 2: Direct streamlit command
streamlit run src/streamlit_app.py
```

### 4. View Results
1. Select an evaluation run from the dropdown
2. Click "📊 Load Results" to view the analysis
3. Explore the results in the different tabs

## Command Line Usage

### Test the System
```bash
python src/test_evaluator.py
```

### Run Evaluations Programmatically
```python
from src.receipt_evaluator import ReceiptEvaluator

# Initialize evaluator
evaluator = ReceiptEvaluator("data")

# Run evaluations on all receipts
results = evaluator.evaluate_all_receipts()

# Save results to disk
run_id = evaluator.save_results(results)

# Load results later
loaded_results, summary = evaluator.load_results(run_id)

print(f"Overall pass rate: {summary['overall_pass_rate']:.1%}")
```

## Project Structure

```
src/
├── __init__.py              # Package initialization
├── receipt_evaluator.py     # Core evaluation logic
├── streamlit_app.py         # Interactive dashboard
├── run_streamlit.py         # Launch script
├── test_evaluator.py        # Test script
└── README.md               # This file
```

## Dataset

The system processes the CORD-v2 training_wheels dataset, which contains:
- 30+ receipt images (PNG format)
- Corresponding metadata files (JSON format)
- Located in `data/cord-v2/images_and_metadata/training_wheels/`

## Evaluation Results

Each receipt evaluation includes:
- **Extraction Status**: Whether BAML successfully extracted data
- **Individual Check Results**: Pass/fail status for each validation
- **Overall Pass Rate**: Percentage of checks that passed
- **Detailed Messages**: Specific information about failures

## Error Handling

The system includes comprehensive error handling for:
- BAML extraction failures
- Missing or corrupted image files
- Invalid data formats
- Network or API issues
- Unexpected runtime errors

## Export Functionality

Results can be exported as JSON files containing:
- Summary statistics
- Detailed per-receipt results
- Evaluation check details
- Extracted data (when successful)

## Troubleshooting

### Common Issues

1. **"No receipt files found"**
   - Ensure the training_wheels dataset is properly downloaded
   - Check that files are in the correct directory structure

2. **BAML extraction errors**
   - Verify API keys are properly configured
   - Check network connectivity
   - Ensure image files are not corrupted

3. **Streamlit won't start**
   - Make sure all dependencies are installed
   - Try running with `python -m streamlit run src/streamlit_app.py`

### Getting Help

If you encounter issues:
1. Run the test script: `python src/test_evaluator.py`
2. Check the console output for detailed error messages
3. Verify your environment setup and dependencies

## Development

To extend the system:

1. **Add new evaluation checks**: Extend the `ReceiptEvaluator` class with new `evaluate_*` methods
2. **Modify the UI**: Update `streamlit_app.py` to display new metrics
3. **Change data sources**: Modify the `get_receipt_files` method to use different datasets

## License

This project is part of the AI That Works series and follows the same licensing terms.
