"""Persistent credit budget tracker for paid browser backends.

Firecrawl (and similar paid backends) charge per-call credits. This module
provides a SQLite-backed counter that:

- Persists across processes (so the budget survives container restarts)
- Charges the same instance for both pre-research and bulk calls
- Returns a clear ``BudgetExhaustedError`` when the budget is depleted
- Writes an audit log of every charge for compliance and debugging
- Can be inspected at runtime via ``get_summary()`` for marimo dashboards

The budget is configured by environment variable:
    BROWSER_FIRECRAWL_BUDGET  - total credits (default 20000)
    BROWSER_CREDIT_DB         - path to SQLite file
                                (default ~/.cache/sruth_browser/credit_budget.sqlite)
"""

from __future__ import annotations

import json
import os
import sqlite3
import threading
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

import structlog

logger = structlog.get_logger()

DEFAULT_TOTAL = 20_000
DEFAULT_DB = os.path.expanduser("~/.cache/sruth_browser/credit_budget.sqlite")


class BudgetExhaustedError(Exception):
    """Raised when an operation would exceed the configured budget."""

    def __init__(
        self,
        backend: str,
        cost: int,
        used: int,
        total: int,
        purpose: str | None = None,
    ):
        self.backend = backend
        self.cost = cost
        self.used = used
        self.total = total
        self.purpose = purpose
        super().__init__(
            f"{backend} charge of {cost} credits rejected: "
            f"{used}/{total} used"
            + (f" (purpose={purpose})" if purpose else "")
        )


class CreditBudget:
    """SQLite-backed credit counter.

    Thread-safe and process-safe via a single ``_lock`` (cross-process safety
    is provided by SQLite's per-connection write lock; we use
    ``BEGIN IMMEDIATE`` for atomic check-and-charge).
    """

    def __init__(
        self,
        total: int = DEFAULT_TOTAL,
        db_path: str | os.PathLike[str] | None = None,
    ):
        self.total = total
        self.db_path = Path(db_path or os.environ.get("BROWSER_CREDIT_DB", DEFAULT_DB))
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(
            str(self.db_path),
            timeout=10.0,
            isolation_level=None,  # autocommit; we drive transactions explicitly
        )
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    @contextmanager
    def _txn(self) -> Iterator[sqlite3.Connection]:
        with self._lock:
            conn = self._connect()
            try:
                conn.execute("BEGIN IMMEDIATE")
                yield conn
                conn.execute("COMMIT")
            except Exception:
                try:
                    conn.execute("ROLLBACK")
                except sqlite3.OperationalError:
                    pass
                raise
            finally:
                conn.close()

    def _init_schema(self) -> None:
        with self._txn() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS budget_config (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    total INTEGER NOT NULL
                )
                """
            )
            conn.execute(
                "INSERT OR IGNORE INTO budget_config (id, total) VALUES (1, ?)",
                (self.total,),
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS credit_ledger (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ts TEXT NOT NULL,
                    backend TEXT NOT NULL,
                    cost INTEGER NOT NULL,
                    purpose TEXT,
                    url TEXT,
                    metadata TEXT
                )
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_ledger_ts ON credit_ledger(ts)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_ledger_backend ON credit_ledger(backend)"
            )
            conn.execute(
                "UPDATE budget_config SET total = ? WHERE id = 1",
                (self.total,),
            )

    @property
    def used(self) -> int:
        """Total credits charged since the budget was created."""
        with self._connect() as conn:
            row = conn.execute("SELECT COALESCE(SUM(cost), 0) FROM credit_ledger").fetchone()
            return int(row[0])

    @property
    def remaining(self) -> int:
        return max(0, self.total - self.used)

    def has(self, cost: int) -> bool:
        """Check whether ``cost`` credits are available without charging."""
        return self.used + cost <= self.total

    def charge(
        self,
        cost: int,
        backend: str,
        *,
        purpose: str | None = None,
        url: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> int:
        """Atomically check and deduct ``cost`` credits.

        Returns the new ``used`` total. Raises :class:`BudgetExhaustedError`
        if the charge would exceed ``total``.
        """
        if cost < 0:
            raise ValueError(f"credit cost must be non-negative, got {cost}")
        if cost == 0:
            return self.used

        with self._txn() as conn:
            row = conn.execute("SELECT total FROM budget_config WHERE id = 1").fetchone()
            total = int(row[0]) if row else self.total
            row = conn.execute(
                "SELECT COALESCE(SUM(cost), 0) FROM credit_ledger"
            ).fetchone()
            used = int(row[0])
            if used + cost > total:
                raise BudgetExhaustedError(
                    backend=backend,
                    cost=cost,
                    used=used,
                    total=total,
                    purpose=purpose,
                )
            conn.execute(
                "INSERT INTO credit_ledger (ts, backend, cost, purpose, url, metadata) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (
                    datetime.now(timezone.utc).isoformat(),
                    backend,
                    cost,
                    purpose,
                    url,
                    json.dumps(metadata) if metadata else None,
                ),
            )
            new_used = used + cost

        logger.info(
            "credit_charged",
            backend=backend,
            cost=cost,
            purpose=purpose,
            url=url,
            used=new_used,
            total=total,
        )
        return new_used

    def refund(
        self,
        cost: int,
        backend: str,
        *,
        purpose: str | None = None,
        url: str | None = None,
    ) -> int:
        """Refund a previously charged amount (e.g. on transient API failure)."""
        if cost < 0:
            raise ValueError(f"refund cost must be non-negative, got {cost}")
        if cost == 0:
            return self.used
        with self._txn() as conn:
            conn.execute(
                "INSERT INTO credit_ledger (ts, backend, cost, purpose, url, metadata) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (
                    datetime.now(timezone.utc).isoformat(),
                    backend,
                    -cost,
                    f"refund:{purpose}" if purpose else "refund",
                    url,
                    None,
                ),
            )
            row = conn.execute(
                "SELECT COALESCE(SUM(cost), 0) FROM credit_ledger"
            ).fetchone()
            new_used = int(row[0])
        logger.info(
            "credit_refunded",
            backend=backend,
            cost=cost,
            purpose=purpose,
            url=url,
            used=new_used,
        )
        return new_used

    def recent_charges(self, limit: int = 50) -> list[dict[str, Any]]:
        """Return the most recent ledger entries for dashboards / debugging."""
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT ts, backend, cost, purpose, url, metadata "
                "FROM credit_ledger ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
        out: list[dict[str, Any]] = []
        for ts, backend, cost, purpose, url, metadata in rows:
            entry: dict[str, Any] = {
                "ts": ts,
                "backend": backend,
                "cost": cost,
                "purpose": purpose,
                "url": url,
            }
            if metadata:
                try:
                    entry["metadata"] = json.loads(metadata)
                except json.JSONDecodeError:
                    entry["metadata"] = metadata
            out.append(entry)
        return out

    def burndown_by_backend(self) -> dict[str, int]:
        """Return ``{backend: total_cost}`` for every backend ever charged."""
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT backend, SUM(cost) FROM credit_ledger GROUP BY backend"
            ).fetchall()
        return {backend: int(cost) for backend, cost in rows}

    def get_summary(self) -> dict[str, Any]:
        """Return a dashboard-friendly summary dict."""
        return {
            "total": self.total,
            "used": self.used,
            "remaining": self.remaining,
            "by_backend": self.burndown_by_backend(),
            "db_path": str(self.db_path),
        }

    def reset(self) -> None:
        """Wipe the ledger. Useful for tests and for monthly budget rollover."""
        with self._txn() as conn:
            conn.execute("DELETE FROM credit_ledger")
        logger.warning("credit_budget_reset", db_path=str(self.db_path))


_budget: CreditBudget | None = None
_budget_lock = threading.Lock()


def get_budget() -> CreditBudget:
    """Get or create the global :class:`CreditBudget` instance.

    The total is read from the ``BROWSER_FIRECRAWL_BUDGET`` env var on first
    call, and persisted to the SQLite file thereafter. Subsequent calls
    always return the same instance.
    """
    global _budget
    if _budget is None:
        with _budget_lock:
            if _budget is None:
                total = int(os.environ.get("BROWSER_FIRECRAWL_BUDGET", DEFAULT_TOTAL))
                _budget = CreditBudget(total=total)
    return _budget


def reset_budget_for_tests(total: int = DEFAULT_TOTAL) -> CreditBudget:
    """Replace the global budget with a fresh one (test helper)."""
    global _budget
    with _budget_lock:
        _budget = CreditBudget(total=total)
    _budget.reset()
    return _budget


__all__ = [
    "CreditBudget",
    "BudgetExhaustedError",
    "get_budget",
    "reset_budget_for_tests",
]
