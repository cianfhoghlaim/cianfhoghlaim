# Auto-Retry on Eval Failure

The **auto-retry pattern** is the canonical way to combine BAML
extraction with runtime evals: re-run the extraction if any eval
fails, capped to prevent runaway cost. This is the pattern from the
`2025-12-02-multimodal-evals` example.

## Why retry on eval failure (not on API failure)?

- **BAML retries API failures natively** — see the
  `clients-and-retries.md` reference for the `retry_policy Constant`
  / `Exponential` blocks
- **Eval failures are different** — the LLM succeeded, but the
  output is wrong. Retrying the same input often produces a
  different (correct) output, because LLMs are non-deterministic
- **The retry is on a wrong extraction, not a failed call** — it's
  a quality improvement, not a fault tolerance

## The pattern

```python
from dataclasses import dataclass
from baml_client import b

@dataclass
class EvaluationResult:
    check: str
    passed: bool
    message: str

def evaluate_receipt(receipt: ReceiptData) -> list[EvaluationResult]:
    """Run the 6 standard evals. See runtime-evals.md."""
    return [
        sum_validation(receipt),
        positive_values(receipt),
        subtotal_consistency(receipt),
        unit_price_accuracy(receipt),
        grand_total_calculation(receipt),
        data_completeness(receipt),
    ]

def extract_with_retry(
    image,
    max_retries: int = 1,
) -> tuple[ReceiptData, list[EvaluationResult], bool]:
    """Run BAML extraction + evals. Retry on eval failure.

    Returns: (final_receipt, final_evals, retry_succeeded)
    """
    # First attempt
    receipt = b.ExtractReceiptTransactions(receipt_image=image)
    results = evaluate_receipt(receipt)
    if all(r.passed for r in results):
        return receipt, results, False  # no retry needed

    # Retry on failure
    for attempt in range(1, max_retries + 1):
        print(f"Retry attempt {attempt}/{max_retries}")
        receipt_retry = b.ExtractReceiptTransactions(receipt_image=image)
        results_retry = evaluate_receipt(receipt_retry)
        if all(r.passed for r in results_retry):
            return receipt_retry, results_retry, True

    # All retries failed
    return receipt, results, False
```

## Comparison: first attempt vs retry

```python
def extract_with_comparison(image, max_retries: int = 1):
    """Like extract_with_retry, but also returns the first attempt for comparison."""
    first_receipt = b.ExtractReceiptTransactions(receipt_image=image)
    first_results = evaluate_receipt(first_receipt)

    if all(r.passed for r in first_results):
        return first_receipt, first_results, None, None, False

    for attempt in range(1, max_retries + 1):
        retry_receipt = b.ExtractReceiptTransactions(receipt_image=image)
        retry_results = evaluate_receipt(retry_receipt)
        if all(r.passed for r in retry_results):
            return retry_receipt, retry_results, first_receipt, first_results, True

    return first_receipt, first_results, None, None, False
```

## Logging and metrics

```python
import structlog

logger = structlog.get_logger()

def extract_with_retry_logged(image, max_retries: int = 1):
    receipt, results, retry_succeeded = extract_with_retry(image, max_retries)
    logger.info(
        "baml_extraction",
        pass_rate=sum(r.passed for r in results) / len(results),
        retry_succeeded=retry_succeeded,
        failed_checks=[r.check for r in results if not r.passed],
    )
    return receipt, results
```

## Cost control

Auto-retry **multiplies API costs** (each failed eval triggers a
full re-extraction). Mitigations:

- **Cap `max_retries` at 1** — the marginal pass-rate gain from 2+
  retries is small (< 5%) but doubles or triples cost
- **Pre-validate the input** — for PDFs, check the page count and
  file size before calling the LLM. For images, run OCR first and
  check that text is extractable
- **Cache successful extractions** — `functools.lru_cache` on the
  image hash + prompt version
- **Use a smaller model for the retry** — `gpt-4o-mini` retry after
  a `gpt-4o` failure may catch the second-time lucky

## When to use this pattern

✅ **Use when**:
- The output has deterministic mathematical relationships (receipts,
  invoices, financial reports, exam papers with known mark schemes)
- The cost of a wrong extraction is high (downstream DuckLake writes,
  cognify passes, RAG results)
- The LLM is the bottleneck on quality (not the prompt)

❌ **Don't use when**:
- The output is open-ended (creative writing, summarisation)
- The LLM is already very accurate (> 95% pass rate)
- The cost of a wrong extraction is low (a re-search is cheap)

## Reference

- The `2025-12-02-multimodal-evals` example project (deleted with
  `docs/baml/`) is the canonical reference. The same example is in
  the upstream [BoundaryML/baml-examples](https://github.com/BoundaryML/baml-examples)
  repo.
- The full auto-retry code is in
  `src/receipt_evaluator.py:419-489` of the deleted example.
- See [`runtime-evals.md`](runtime-evals.md) for the 6 standard checks.
