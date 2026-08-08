"""Speedrun MMO per-tab overview helpers.

Per the 2026-08-10-marimo-v14-tier3-grouped-dashboards-consolidation-v1
change — this module provides the 5 per-tab overview helpers for the
`notebooks/speedrun_mmo.py` grouped dashboard, which consolidates:
- `16_speedrun_mmo_00_celtic_nft.py`
- `16_speedrun_mmo_01_mission_control.py`
- `16_speedrun_mmo_01_language_staking.py`
- `16_speedrun_mmo_02_cianfhoghlaim_mmo_progress.py`
- `16_speedrun_mmo_02_token_shop.py`
- `16_speedrun_mmo_03_quest_randomness.py`
- `16_speedrun_mmo_04_item_exchange.py`
- `16_speedrun_mmo_05..08_*.py`
"""
from __future__ import annotations


def celtic_nft_overview() -> str:
    """Celtic NFT overview (from 16_00)."""
    return """
    ## 🎨 Celtic NFT Collection

    The Túatha Celtic NFT collection — 216 unique Celtic-themed NFTs
    (one per Leabharlann document). Stake to earn tokens + unlock quests.
    """


def mission_control_overview() -> str:
    """Mission control overview (from 16_01_mission)."""
    return """
    ## 🎯 Mission Control

    The central mission tracker — 100+ missions across 6 themed seasons.
    Real-time progress + leaderboards.
    """


def language_staking_overview() -> str:
    """Language staking overview (from 16_01_language)."""
    return """
    ## 💰 Language Staking

    Stake your language tokens (Irish / Welsh / Scottish Gaelic / Breton)
    to earn APY + governance rights. 4 currency pairs supported.
    """


def mmo_progress_overview() -> str:
    """Cianfhoghlaim MMO progress overview (from 16_02_mmo)."""
    return """
    ## 📊 Cianfhoghlaim MMO Progress

    The cross-jurisdiction learning MMO — students from 8 British Isles
    jurisdictions learn together via the BIEP syllabus.
    """


def token_shop_overview() -> str:
    """Token shop overview (from 16_02_token)."""
    return """
    ## 🛒 Token Shop

    Spend your tokens on cosmetics, avatars, skill trees, and access to
    premium learning content.
    """


def quest_randomness_overview() -> str:
    """Quest randomness overview (from 16_03_quest)."""
    return """
    ## 🎲 Quest Randomness

    The procedural quest generator — combines Celtic mythology + the
    student's current subject + their cohort's RAGAS score to produce
    personalised learning quests.
    """


def item_exchange_overview() -> str:
    """Item exchange overview (from 16_04_item)."""
    return """
    ## 🔄 Item Exchange

    P2P item trading — students can swap their earned artifacts with
    peers across the 8 jurisdictions.
    """


SPEEDRUN_MMO_TABS = [
    ("Celtic NFT", celtic_nft_overview),
    ("Mission Control", mission_control_overview),
    ("Language Staking", language_staking_overview),
    ("MMO Progress", mmo_progress_overview),
    ("Token Shop", token_shop_overview),
    ("Quest Randomness", quest_randomness_overview),
    ("Item Exchange", item_exchange_overview),
]


__all__ = [
    "celtic_nft_overview",
    "mission_control_overview",
    "language_staking_overview",
    "mmo_progress_overview",
    "token_shop_overview",
    "quest_randomness_overview",
    "item_exchange_overview",
    "SPEEDRUN_MMO_TABS",
]