# Runtime Evals (6 Deterministic Checks)

**Runtime evals** are deterministic Python checks that validate a
BAML extraction's output **after** the LLM call, using pure math /
logic. They are **not LLM-as-judge**. The 6 standard checks below
are the canonical pattern from the
`2025-12-02-multimodal-evals` example (BAML's `ai that works` series).

## Why runtime evals (not LLM-as-judge)?

| LLM-as-judge | Runtime evals |
|:--|:--|
| Doubles API cost | Free (pure Python) |
| Non-deterministic | Deterministic (same input → same output) |
| Circular reasoning (LLM validating LLM) | No circularity |
| Slow (1-3s per call) | Fast (< 1ms per check) |
| Hard to debug | Each check returns explicit `expected_value` and `actual_value` |

## The 6 standard checks

```python
from dataclasses import dataclass

@dataclass
class EvaluationResult:
    check: str
    passed: bool
    message: str
    expected_value: float | None = None
    actual_value: float | None = None

# 1. Sum validation
def sum_validation(receipt: ReceiptData) -> EvaluationResult:
    """Σ transactions + charges + tax + rounding − |discount| ≈ grand_total"""
    expected = (
        sum(t.total_price for t in receipt.transactions)
        + (receipt.service_charge or 0)
        + (receipt.tax or 0)
        + (receipt.rounding or 0)
        - abs(receipt.discount or 0)
    )
    actual = receipt.grand_total
    passed = abs(expected - actual) < 0.01
    return EvaluationResult(
        check="sum_validation",
        passed=passed,
        message=f"expected={expected:.2f}, actual={actual:.2f}",
        expected_value=expected,
        actual_value=actual,
    )

# 2. Positive values
def positive_values(receipt: ReceiptData) -> EvaluationResult:
    """All monetary fields ≥ 0 except rounding and discount."""
    bad_fields = []
    for t in receipt.transactions:
        if t.unit_price < 0 or t.total_price < 0 or t.quantity < 0:
            bad_fields.append(f"transaction.{t.item_name}")
    for field in ("service_charge", "tax", "subtotal", "grand_total"):
        val = getattr(receipt, field)
        if val is not None and val < 0:
            bad_fields.append(field)
    passed = len(bad_fields) == 0
    return EvaluationResult(
        check="positive_values",
        passed=passed,
        message=f"negative fields: {bad_fields}" if bad_fields else "all positive",
    )

# 3. Subtotal consistency
def subtotal_consistency(receipt: ReceiptData) -> EvaluationResult:
    """When subtotal present: Σ transaction totals ≈ subtotal."""
    if receipt.subtotal is None:
        return EvaluationResult(
            check="subtotal_consistency",
            passed=True,
            message="no subtotal to check",
        )
    expected = sum(t.total_price for t in receipt.transactions)
    actual = receipt.subtotal
    passed = abs(expected - actual) < 0.01
    return EvaluationResult(
        check="subtotal_consistency",
        passed=passed,
        message=f"Σ transactions={expected:.2f}, subtotal={actual:.2f}",
        expected_value=expected,
        actual_value=actual,
    )

# 4. Unit price accuracy
def unit_price_accuracy(receipt: ReceiptData) -> EvaluationResult:
    """Per-line: (unit_price − |unit_discount|) × quantity ≈ total_price."""
    bad_lines = []
    for t in receipt.transactions:
        expected = (t.unit_price - abs(t.unit_discount or 0)) * t.quantity
        if abs(expected - t.total_price) >= 0.01:
            bad_lines.append(t.item_name)
    passed = len(bad_lines) == 0
    return EvaluationResult(
        check="unit_price_accuracy",
        passed=passed,
        message=f"bad lines: {bad_lines}" if bad_lines else "all accurate",
    )

# 5. Grand total calculation
def grand_total_calculation(receipt: ReceiptData) -> EvaluationResult:
    """subtotal + service + tax + rounding − |discount| ≈ grand_total."""
    if receipt.subtotal is None:
        return EvaluationResult(
            check="grand_total_calculation",
            passed=True,
            message="no subtotal to check",
        )
    expected = (
        receipt.subtotal
        + (receipt.service_charge or 0)
        + (receipt.tax or 0)
        + (receipt.rounding or 0)
        - abs(receipt.discount or 0)
    )
    actual = receipt.grand_total
    passed = abs(expected - actual) < 0.01
    return EvaluationResult(
        check="grand_total_calculation",
        passed=passed,
        message=f"expected={expected:.2f}, actual={actual:.2f}",
        expected_value=expected,
        actual_value=actual,
    )

# 6. Data completeness
def data_completeness(receipt: ReceiptData) -> EvaluationResult:
    """transactions non-empty, grand_total present, every transaction has required fields."""
    missing = []
    if not receipt.transactions:
        missing.append("transactions")
    if receipt.grand_total is None:
        missing.append("grand_total")
    for t in receipt.transactions:
        for field in ("item_name", "quantity", "unit_price", "total_price"):
            if not hasattr(t, field) or getattr(t, field) is None:
                missing.append(f"transaction.{t.item_name or '?'}.{field}")
    passed = len(missing) == 0
    return EvaluationResult(
        check="data_completeness",
        passed=passed,
        message=f"missing: {missing}" if missing else "complete",
    )

# Run all 6
EVALS = [
    sum_validation,
    positive_values,
    subtotal_consistency,
    unit_price_accuracy,
    grand_total_calculation,
    data_completeness,
]

def evaluate_receipt(receipt: ReceiptData) -> list[EvaluationResult]:
    return [eval_fn(receipt) for eval_fn in EVALS]
```

## Auto-retry on failure

```python
def evaluate_with_retry(image, max_retries: int = 1) -> tuple[ReceiptData, list[EvaluationResult]]:
    """Run BAML extraction + 6 evals. Retry on failure (capped to prevent cost runaway)."""
    receipt = b.ExtractReceiptTransactions(receipt_image=image)
    results = evaluate_receipt(receipt)

    if not all(r.passed for r in results) and max_retries > 0:
        print("Retry due to failing eval(s):", [r.check for r in results if not r.passed])
        receipt_retry = b.ExtractReceiptTransactions(receipt_image=image)
        results_retry = evaluate_receipt(receipt_retry)
        return receipt_retry, results_retry

    return receipt, results
```

See [`auto-retry.md`](auto-retry.md) for the full pattern with
first-attempt-vs-retry comparison.

## Pass-rate reporting

```python
def pass_rate(results: list[EvaluationResult]) -> float:
    return sum(r.passed for r in results) / len(results)

stats = {
    "total": len(all_results),
    "passed": sum(1 for r in all_results if r.passed),
    "by_check": {
        check: sum(1 for r in all_results if r.check == check and r.passed)
        / sum(1 for r in all_results if r.check == check)
        for check in {r.check for r in all_results}
    },
}
```

## When to add a 7th check

- **Currency code consistency** — all amounts in the same currency
- **Date plausibility** — transaction date within ±1 day of receipt date
- **Vendor whitelist** — vendor is in a known-good list
- **Custom business rules** — e.g. "all transactions must be ≤ $1000"

## Reference

- The `2025-12-02-multimodal-evals` example project (deleted with
  `docs/baml/`) is the canonical reference. The same example is in
  the upstream [BoundaryML/baml-examples](https://github.com/BoundaryML/baml-examples)
  repo as `2025-12-02-multimodal-evals/`.
- The `ai that works: Multimodal Evals` video: <https://www.youtube.com/@BoundaryML>
- The runtime evals dashboard (Streamlit) is a follow-on pattern
  for visualising pass rates across runs.
