"""Tests for the persistent credit budget."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from sruth_browser.credit_budget import (
    BudgetExhaustedError,
    CreditBudget,
    get_budget,
    reset_budget_for_tests,
)


@pytest.fixture
def tmp_budget(tmp_path: Path) -> CreditBudget:
    """A fresh budget backed by a tmp SQLite file."""
    db = tmp_path / "budget.sqlite"
    return CreditBudget(total=100, db_path=db)


class TestCreditBudgetInit:
    def test_creates_db_file(self, tmp_path: Path) -> None:
        db = tmp_path / "fresh.sqlite"
        assert not db.exists()
        CreditBudget(total=50, db_path=db)
        assert db.exists()

    def test_zero_used_at_init(self, tmp_budget: CreditBudget) -> None:
        assert tmp_budget.used == 0
        assert tmp_budget.remaining == 100
        assert tmp_budget.has(0) is True
        assert tmp_budget.has(50) is True
        assert tmp_budget.has(100) is True
        assert tmp_budget.has(101) is False

    def test_summary_shape(self, tmp_budget: CreditBudget) -> None:
        s = tmp_budget.get_summary()
        assert s["total"] == 100
        assert s["used"] == 0
        assert s["remaining"] == 100
        assert s["by_backend"] == {}
        assert "db_path" in s


class TestCreditBudgetCharge:
    def test_single_charge(self, tmp_budget: CreditBudget) -> None:
        new_used = tmp_budget.charge(10, backend="firecrawl", purpose="scrape")
        assert new_used == 10
        assert tmp_budget.used == 10
        assert tmp_budget.remaining == 90

    def test_charge_with_url(self, tmp_budget: CreditBudget) -> None:
        tmp_budget.charge(2, backend="firecrawl", purpose="pre_research", url="https://x.com")
        charges = tmp_budget.recent_charges(limit=10)
        assert len(charges) == 1
        assert charges[0]["backend"] == "firecrawl"
        assert charges[0]["purpose"] == "pre_research"
        assert charges[0]["url"] == "https://x.com"
        assert charges[0]["cost"] == 2

    def test_charge_with_metadata(self, tmp_budget: CreditBudget) -> None:
        tmp_budget.charge(
            1,
            backend="firecrawl",
            purpose="pre_research",
            url="https://x.com",
            metadata={"estimated_pages": 42},
        )
        charges = tmp_budget.recent_charges()
        assert charges[0]["metadata"] == {"estimated_pages": 42}

    def test_zero_charge_is_noop(self, tmp_budget: CreditBudget) -> None:
        new_used = tmp_budget.charge(0, backend="firecrawl")
        assert new_used == 0
        assert tmp_budget.used == 0

    def test_negative_charge_raises(self, tmp_budget: CreditBudget) -> None:
        with pytest.raises(ValueError, match="non-negative"):
            tmp_budget.charge(-1, backend="firecrawl")

    def test_charge_exhausting_budget(self, tmp_budget: CreditBudget) -> None:
        tmp_budget.charge(90, backend="firecrawl")
        # exactly at the cap is allowed
        tmp_budget.charge(10, backend="firecrawl")
        assert tmp_budget.used == 100
        assert tmp_budget.remaining == 0
        # one more cent rejected
        with pytest.raises(BudgetExhaustedError) as exc_info:
            tmp_budget.charge(1, backend="firecrawl")
        assert exc_info.value.used == 100
        assert exc_info.value.total == 100
        assert exc_info.value.cost == 1

    def test_charge_records_purpose(self, tmp_budget: CreditBudget) -> None:
        tmp_budget.charge(2, backend="firecrawl", purpose="pre_research", url="https://a")
        tmp_budget.charge(1, backend="firecrawl", purpose="scrape", url="https://b")
        charges = tmp_budget.recent_charges()
        assert [c["purpose"] for c in charges] == ["scrape", "pre_research"]


class TestCreditBudgetRefund:
    def test_refund_decreases_used(self, tmp_budget: CreditBudget) -> None:
        tmp_budget.charge(10, backend="firecrawl")
        tmp_budget.refund(5, backend="firecrawl", purpose="failed_call")
        assert tmp_budget.used == 5

    def test_refund_zero_is_noop(self, tmp_budget: CreditBudget) -> None:
        tmp_budget.charge(10, backend="firecrawl")
        tmp_budget.refund(0, backend="firecrawl")
        assert tmp_budget.used == 10

    def test_refund_negative_raises(self, tmp_budget: CreditBudget) -> None:
        with pytest.raises(ValueError, match="non-negative"):
            tmp_budget.refund(-5, backend="firecrawl")


class TestCreditBudgetPersistence:
    def test_credits_persist_across_instances(self, tmp_path: Path) -> None:
        db = tmp_path / "persist.sqlite"
        a = CreditBudget(total=100, db_path=db)
        a.charge(30, backend="firecrawl")
        # New instance, same DB file
        b = CreditBudget(total=100, db_path=db)
        assert b.used == 30

    def test_total_can_be_changed_via_new_instance(self, tmp_path: Path) -> None:
        db = tmp_path / "change_total.sqlite"
        CreditBudget(total=100, db_path=db).charge(50, backend="firecrawl")
        # Same DB, but a new instance with a different total
        b = CreditBudget(total=200, db_path=db)
        assert b.used == 50
        assert b.total == 200


class TestCreditBudgetBurndown:
    def test_burndown_by_backend(self, tmp_budget: CreditBudget) -> None:
        tmp_budget.charge(5, backend="firecrawl", purpose="scrape")
        tmp_budget.charge(2, backend="firecrawl", purpose="pre_research")
        tmp_budget.charge(3, backend="zai", purpose="grounding")
        breakdown = tmp_budget.burndown_by_backend()
        assert breakdown == {"firecrawl": 7, "zai": 3}

    def test_recent_charges_limit(self, tmp_budget: CreditBudget) -> None:
        for i in range(20):
            tmp_budget.charge(1, backend="firecrawl", purpose=f"call_{i}")
        charges = tmp_budget.recent_charges(limit=5)
        assert len(charges) == 5
        # Newest first
        assert charges[0]["purpose"] == "call_19"


class TestCreditBudgetReset:
    def test_reset_clears_ledger(self, tmp_budget: CreditBudget) -> None:
        tmp_budget.charge(50, backend="firecrawl")
        assert tmp_budget.used == 50
        tmp_budget.reset()
        assert tmp_budget.used == 0

    def test_reset_does_not_change_total(self, tmp_budget: CreditBudget) -> None:
        tmp_budget.charge(50, backend="firecrawl")
        tmp_budget.reset()
        assert tmp_budget.total == 100


class TestGetBudgetSingleton:
    def test_returns_same_instance(self) -> None:
        a = get_budget()
        b = get_budget()
        assert a is b

    def test_reset_budget_for_tests_clears(self, monkeypatch) -> None:
        # Use a temp DB so we don't clobber the real global ledger
        with tempfile.TemporaryDirectory() as tmp:
            monkeypatch.setenv("BROWSER_CREDIT_DB", str(Path(tmp) / "singleton.sqlite"))
            budget = reset_budget_for_tests(total=42)
            assert budget.total == 42
            budget.charge(7, backend="firecrawl")
            assert budget.used == 7
            # New call to get_budget returns the same singleton
            again = get_budget()
            assert again is budget
            assert again.used == 7


class TestBudgetExhaustedError:
    def test_error_message_includes_all_fields(self) -> None:
        err = BudgetExhaustedError(
            backend="firecrawl",
            cost=10,
            used=19990,
            total=20000,
            purpose="pre_research",
        )
        msg = str(err)
        assert "firecrawl" in msg
        assert "10 credits" in msg
        assert "19990/20000" in msg
        assert "pre_research" in msg

    def test_error_attributes(self) -> None:
        err = BudgetExhaustedError(
            backend="zai",
            cost=5,
            used=20,
            total=20,
        )
        assert err.backend == "zai"
        assert err.cost == 5
        assert err.used == 20
        assert err.total == 20
        assert err.purpose is None
