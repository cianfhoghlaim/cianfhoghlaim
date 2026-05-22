"""
Tests for DeFi analytics functionality.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from decimal import Decimal


class TestTVLCalculations:
    """Test TVL (Total Value Locked) calculations."""

    def test_aggregate_protocol_tvl(self):
        """Test aggregating TVL across chains."""
        protocol_tvl = {
            "ethereum": 5_000_000_000,
            "arbitrum": 1_500_000_000,
            "optimism": 800_000_000,
            "polygon": 500_000_000,
        }

        total_tvl = sum(protocol_tvl.values())
        assert total_tvl == 7_800_000_000

    def test_tvl_change_calculation(self):
        """Test TVL change percentage calculation."""
        tvl_yesterday = 10_000_000_000
        tvl_today = 10_500_000_000

        change_pct = ((tvl_today - tvl_yesterday) / tvl_yesterday) * 100
        assert change_pct == 5.0

    def test_tvl_dominance_calculation(self):
        """Test protocol TVL dominance."""
        protocols = [
            {"name": "Aave", "tvl": 10_000_000_000},
            {"name": "Compound", "tvl": 5_000_000_000},
            {"name": "MakerDAO", "tvl": 8_000_000_000},
        ]

        total_tvl = sum(p["tvl"] for p in protocols)
        dominance = {p["name"]: (p["tvl"] / total_tvl) * 100 for p in protocols}

        assert abs(dominance["Aave"] - 43.48) < 0.01
        assert abs(dominance["Compound"] - 21.74) < 0.01
        assert abs(dominance["MakerDAO"] - 34.78) < 0.01


class TestYieldCalculations:
    """Test yield/APY calculations."""

    def test_simple_apy_calculation(self):
        """Test simple APY calculation."""
        # APY from daily rate
        daily_rate = 0.01  # 1% daily
        apy = ((1 + daily_rate) ** 365 - 1) * 100

        assert apy > 3600  # Should be very high with 1% daily

    def test_compound_apy_calculation(self):
        """Test compound APY from base rate."""
        base_apy = 5.0  # 5% base APY
        compound_frequency = 365  # Daily compounding

        # Convert to effective APY
        rate_per_period = base_apy / 100 / compound_frequency
        effective_apy = ((1 + rate_per_period) ** compound_frequency - 1) * 100

        # Compound APY should be slightly higher than base
        assert effective_apy > base_apy
        assert abs(effective_apy - 5.13) < 0.1

    def test_yield_farming_rewards(self):
        """Test yield farming reward calculations."""
        # Pool parameters
        staked_amount = 10000  # $10,000
        base_apy = 5.0  # 5%
        reward_apy = 10.0  # 10% in reward tokens

        # Calculate rewards
        base_yearly = staked_amount * (base_apy / 100)
        reward_yearly = staked_amount * (reward_apy / 100)
        total_yearly = base_yearly + reward_yearly

        assert base_yearly == 500
        assert reward_yearly == 1000
        assert total_yearly == 1500

    def test_impermanent_loss_calculation(self):
        """Test impermanent loss calculation for AMM pools."""

        def calculate_il(price_ratio: float) -> float:
            """Calculate impermanent loss given price ratio change."""
            # IL formula: IL = 2 * sqrt(price_ratio) / (1 + price_ratio) - 1
            import math

            sqrt_ratio = math.sqrt(price_ratio)
            il = (2 * sqrt_ratio / (1 + price_ratio)) - 1
            return il * 100  # Return as percentage

        # No price change = no IL
        assert abs(calculate_il(1.0)) < 0.001

        # 2x price increase
        il_2x = calculate_il(2.0)
        assert abs(il_2x - (-5.72)) < 0.1  # ~5.72% loss

        # 4x price increase
        il_4x = calculate_il(4.0)
        assert abs(il_4x - (-20.0)) < 0.1  # ~20% loss


class TestPoolAnalysis:
    """Test DeFi pool analysis."""

    def test_pool_utilization_rate(self):
        """Test lending pool utilization calculation."""
        total_supplied = 100_000_000
        total_borrowed = 65_000_000

        utilization = (total_borrowed / total_supplied) * 100
        assert utilization == 65.0

    def test_pool_health_factor(self):
        """Test collateral health factor calculation."""
        collateral_value = 15000
        debt_value = 10000
        liquidation_threshold = 0.8

        health_factor = (collateral_value * liquidation_threshold) / debt_value
        assert health_factor == 1.2  # Healthy (>1)

    def test_pool_liquidity_depth(self):
        """Test pool liquidity depth analysis."""
        reserves = {
            "ETH": {"amount": 1000, "price": 3000},
            "USDC": {"amount": 3_000_000, "price": 1},
        }

        # Total liquidity
        total_liquidity = sum(
            r["amount"] * r["price"] for r in reserves.values()
        )
        assert total_liquidity == 6_000_000

        # Check if pool can handle large swap
        swap_size = 100_000  # $100k swap
        can_handle = total_liquidity > swap_size * 10  # 10x buffer
        assert can_handle is True


class TestRiskMetrics:
    """Test DeFi risk metric calculations."""

    def test_protocol_risk_score(self):
        """Test protocol risk score calculation."""

        def calculate_risk_score(metrics: dict) -> float:
            """Calculate risk score 0-100 (lower is better)."""
            score = 0

            # TVL factor (higher TVL = lower risk)
            if metrics["tvl"] < 10_000_000:
                score += 30
            elif metrics["tvl"] < 100_000_000:
                score += 20
            elif metrics["tvl"] < 1_000_000_000:
                score += 10

            # Audit factor
            if not metrics["audited"]:
                score += 25
            elif metrics["audit_age_days"] > 180:
                score += 10

            # Age factor (newer = riskier)
            if metrics["age_days"] < 30:
                score += 25
            elif metrics["age_days"] < 90:
                score += 15
            elif metrics["age_days"] < 365:
                score += 5

            # Bug bounty factor
            if not metrics["has_bug_bounty"]:
                score += 10

            return min(score, 100)

        established_protocol = {
            "tvl": 5_000_000_000,
            "audited": True,
            "audit_age_days": 30,
            "age_days": 730,
            "has_bug_bounty": True,
        }

        new_protocol = {
            "tvl": 5_000_000,
            "audited": False,
            "audit_age_days": 0,
            "age_days": 15,
            "has_bug_bounty": False,
        }

        established_risk = calculate_risk_score(established_protocol)
        new_risk = calculate_risk_score(new_protocol)

        assert established_risk < new_risk
        assert established_risk < 20
        assert new_risk > 80

    def test_chain_concentration_risk(self):
        """Test chain concentration risk calculation."""
        protocol_distribution = {
            "ethereum": 80,  # 80% on Ethereum
            "arbitrum": 15,
            "optimism": 5,
        }

        # High concentration on single chain = higher risk
        max_concentration = max(protocol_distribution.values())
        concentration_risk = "high" if max_concentration > 70 else (
            "medium" if max_concentration > 50 else "low"
        )

        assert concentration_risk == "high"


class TestMarketAnalysis:
    """Test DeFi market analysis."""

    def test_category_tvl_breakdown(self):
        """Test TVL breakdown by category."""
        protocols = [
            {"category": "lending", "tvl": 30_000_000_000},
            {"category": "dex", "tvl": 25_000_000_000},
            {"category": "derivatives", "tvl": 10_000_000_000},
            {"category": "yield", "tvl": 15_000_000_000},
            {"category": "lending", "tvl": 20_000_000_000},
        ]

        # Aggregate by category
        category_tvl = {}
        for p in protocols:
            cat = p["category"]
            category_tvl[cat] = category_tvl.get(cat, 0) + p["tvl"]

        assert category_tvl["lending"] == 50_000_000_000
        assert category_tvl["dex"] == 25_000_000_000

    def test_chain_tvl_ranking(self):
        """Test chain ranking by TVL."""
        chains = [
            {"name": "ethereum", "tvl": 50_000_000_000},
            {"name": "arbitrum", "tvl": 3_000_000_000},
            {"name": "optimism", "tvl": 1_500_000_000},
            {"name": "polygon", "tvl": 1_000_000_000},
            {"name": "bsc", "tvl": 4_000_000_000},
        ]

        # Sort by TVL
        ranked = sorted(chains, key=lambda x: x["tvl"], reverse=True)

        assert ranked[0]["name"] == "ethereum"
        assert ranked[1]["name"] == "bsc"
        assert ranked[2]["name"] == "arbitrum"
