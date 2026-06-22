"""
Blockchain assets for the Anam learn-to-earn platform.

This module provides Dagster assets for:
- Reading on-chain data (token balances, NFT metadata)
- Computing XP rewards from learning activities
- Minting tokens and updating NFTs
"""

from .assets import (
    user_learning_activity,
    computed_xp_rewards,
    pending_token_mints,
    nft_evolution_queue,
)
from .resources import (
    Web3Resource,
    ContractResource,
)

__all__ = [
    "user_learning_activity",
    "computed_xp_rewards",
    "pending_token_mints",
    "nft_evolution_queue",
    "Web3Resource",
    "ContractResource",
]
