"""
Dagster resources for blockchain interactions.

Provides Web3 connection and contract interfaces for:
- TuathToken (ERC20)
- CuchulainnNFT (Dynamic NFT)
- AnamCaraDAO (Mentorship)
"""

from typing import Optional
import os

from dagster import ConfigurableResource, InitResourceContext
from pydantic import Field


class Web3Resource(ConfigurableResource):
    """
    Web3 provider resource for blockchain interactions.

    Supports Arbitrum and Base networks (mainnet and testnet).
    """

    rpc_url: str = Field(
        default_factory=lambda: os.getenv(
            "ARBITRUM_RPC_URL",
            "https://sepolia-rollup.arbitrum.io/rpc"
        ),
        description="RPC URL for the blockchain network"
    )
    chain_id: int = Field(
        default=421614,  # Arbitrum Sepolia
        description="Chain ID for the network"
    )
    private_key: Optional[str] = Field(
        default=None,
        description="Private key for signing transactions (optional)"
    )

    _web3: Optional[object] = None

    def setup_for_execution(self, context: InitResourceContext) -> None:
        """Initialize Web3 connection."""
        try:
            from web3 import Web3
            self._web3 = Web3(Web3.HTTPProvider(self.rpc_url))
            context.log.info(f"Connected to chain {self.chain_id}")
        except ImportError:
            context.log.warning("web3 not installed, using mock connection")
            self._web3 = None

    @property
    def web3(self):
        """Get the Web3 instance."""
        return self._web3

    def get_balance(self, address: str) -> int:
        """Get ETH balance for an address."""
        if self._web3:
            return self._web3.eth.get_balance(address)
        return 0


class ContractResource(ConfigurableResource):
    """
    Resource for interacting with Anam smart contracts.

    Provides interfaces for:
    - TuathToken: ERC20 utility token
    - CuchulainnNFT: Dynamic avatar NFT
    - AnamCaraDAO: Mentorship system
    """

    tuath_token_address: str = Field(
        default="",
        description="Address of TuathToken contract"
    )
    cuchulainn_nft_address: str = Field(
        default="",
        description="Address of CuchulainnNFT contract"
    )
    anam_cara_dao_address: str = Field(
        default="",
        description="Address of AnamCaraDAO contract"
    )

    # ABIs would be loaded from compiled contracts
    _tuath_abi: list = []
    _nft_abi: list = []
    _dao_abi: list = []

    def get_tuath_balance(self, web3_resource: Web3Resource, address: str) -> int:
        """Get Tuath token balance for an address."""
        if not web3_resource.web3 or not self.tuath_token_address:
            return 0

        # Would use actual ABI here
        # contract = web3_resource.web3.eth.contract(
        #     address=self.tuath_token_address,
        #     abi=self._tuath_abi
        # )
        # return contract.functions.balanceOf(address).call()
        return 0

    def get_warrior_stats(self, web3_resource: Web3Resource, token_id: int) -> dict:
        """Get warrior stats from CuchulainnNFT."""
        if not web3_resource.web3 or not self.cuchulainn_nft_address:
            return {}

        # Would query contract for warrior data
        return {
            "token_id": token_id,
            "level": 1,
            "xp": 0,
            "element": "Spirit",
            "warp_spasm": False,
        }

    def get_mentor_profile(self, web3_resource: Web3Resource, address: str) -> dict:
        """Get mentor profile from AnamCaraDAO."""
        if not web3_resource.web3 or not self.anam_cara_dao_address:
            return {}

        return {
            "address": address,
            "soul_level": 0,
            "total_acolytes": 0,
            "active_acolytes": 0,
            "is_active": False,
        }
