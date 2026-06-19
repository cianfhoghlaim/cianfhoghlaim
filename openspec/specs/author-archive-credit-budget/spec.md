# author-archive-credit-budget Specification

## Purpose
TBD - created by archiving change author-archive-v1. Update Purpose after archive.
## Requirements
### Requirement: Total budget

The total budget SHALL default to 20,000 credits and be overridable
via the `BROWSER_FIRECRAWL_BUDGET` environment variable. Changing the
total on a subsequent `CreditBudget(total=X, db_path=Y)` call SHALL
update the `budget_config.total` row but SHALL NOT clear the existing
`credit_ledger` rows.

#### Scenario: First construction

- **WHEN** `CreditBudget(total=100, db_path=/tmp/x.sqlite)` is called
- **AND** the file `/tmp/x.sqlite` does not exist
- **THEN** the file is created
- **AND** the `budget_config` table has one row with `total = 100`

#### Scenario: Changing the total

- **WHEN** `CreditBudget(total=100, db_path=X)` is called
- **AND** the user charges 50 credits
- **AND** a new `CreditBudget(total=200, db_path=X)` is created
- **THEN** the new instance has `total = 200`
- **AND** the new instance has `used = 50`

### Requirement: Atomic charge

The `charge(cost, backend, purpose, url, metadata)` method SHALL raise
`ValueError` for `cost < 0`, return early for `cost == 0` without
touching the database, and for `cost > 0` SHALL:

1. Acquire the process-local `threading.Lock`
2. `BEGIN IMMEDIATE` (acquires SQLite's write lock)
3. `SELECT COALESCE(SUM(cost), 0) FROM credit_ledger` to get the
   current `used` total
4. If `used + cost > total`, raise `BudgetExhaustedError` (do not
   insert a ledger row)
5. Otherwise `INSERT INTO credit_ledger (...)` with the charge
6. `COMMIT`
7. Release the lock

The `refund(cost, backend, purpose, url)` method SHALL be the inverse:
insert a negative-cost ledger row. It SHALL raise `ValueError` for
`cost < 0` and return early for `cost == 0`.

#### Scenario: Successful charge

- **WHEN** `budget.charge(10, "firecrawl", purpose="scrape", url="https://x")` is called
- **AND** `used + 10 <= total`
- **THEN** a row is inserted in `credit_ledger`
- **AND** `used` increases by 10

#### Scenario: Budget exhausted

- **WHEN** `used + 10 > total`
- **THEN** `BudgetExhaustedError` is raised
- **AND** no row is inserted in `credit_ledger`

#### Scenario: Concurrent charges

- **WHEN** 10 concurrent calls each try to charge 5 credits
- **AND** the total budget is 30 credits
- **THEN** exactly 6 succeed and 4 raise `BudgetExhaustedError`
- **AND** the final `used` is exactly 30

#### Scenario: Refund

- **WHEN** `budget.charge(10)` is called
- **AND** `budget.refund(5, "firecrawl", purpose="failed_call")` is called
- **THEN** `used` decreases by 5

### Requirement: BudgetExhaustedError

`BudgetExhaustedError` SHALL be raised when a charge would exceed the
total. It SHALL carry the following attributes: `backend` (str),
`cost` (int), `used` (int), `total` (int), `purpose` (str | None).
The error message SHALL include all 4 numeric fields and the purpose
(if set), formatted as: `{backend} charge of {cost} credits rejected: {used}/{total} used (purpose={purpose})`.

#### Scenario: Error message

- **WHEN** `BudgetExhaustedError(backend="firecrawl", cost=10, used=19990, total=20000, purpose="pre_research")` is raised
- **THEN** `str(err)` contains "firecrawl", "10 credits", "19990/20000", and "pre_research"

### Requirement: Dashboard summary

The `get_summary()` method SHALL return a dict with: `total` (int),
`used` (int), `remaining` (int), `by_backend` (dict[str, int]),
`db_path` (str).

#### Scenario: Summary shape

- **WHEN** the budget has `used = 50` across `firecrawl` (30) and `zai` (20)
- **THEN** `get_summary()` returns `{"total": 20000, "used": 50, "remaining": 19950, "by_backend": {"firecrawl": 30, "zai": 20}, "db_path": "..."}`

### Requirement: Global singleton

`get_budget()` SHALL return a process-wide singleton `CreditBudget`
instance, lazily initialised on first call. The `total` SHALL be read
from the `BROWSER_FIRECRAWL_BUDGET` env var on first call (default
20,000). Subsequent calls SHALL return the same instance.
`reset_budget_for_tests(total)` SHALL replace the singleton with a
fresh instance and clear the ledger.

#### Scenario: First call

- **WHEN** `get_budget()` is called for the first time
- **THEN** a new `CreditBudget(total=int(os.environ.get("BROWSER_FIRECRAWL_BUDGET", 20000)))` is created
- **AND** the instance is cached

#### Scenario: Subsequent calls

- **WHEN** `get_budget()` is called again
- **THEN** the same instance is returned

