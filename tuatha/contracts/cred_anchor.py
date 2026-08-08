"""infrastructure.contracts.cred_anchor — Deploy + verify the CredAnchor contract.

Companion to `infrastructure/contracts/CredAnchor.sol` (Solidity source).
Provides a Python wrapper for:

1. Compiling the Solidity source (via `py-solc-x` or `solc`)
2. Deploying to Base L2 (via `web3.py`)
3. Calling `publish(batchId, merkleRoot, leafCount)` from the daily
   `daily_credential_anchor` Dagster asset
4. Calling `getAnchor(batchId)` for verification

Production usage requires:
- `web3>=6.0`
- A funded Base L2 wallet (the contract owner)
- The deployed `CredAnchor` address in `CIANFHOGHLAIM_CREDANCHOR_ADDRESS`
- The RPC URL in `CIANFHOGHLAIM_BASE_L2_RPC_URL`

Reference:
    openspec/changes/cianfhoghlaim-educational-mmo-v1/proposal.md (D4)
    cianfhoghlaim/badges/anchor.py
    infrastructure/contracts/CredAnchor.sol
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Optional

# ABI mirrors the events + functions in CredAnchor.sol
CREEDANCHOR_ABI = [
    {
        "inputs": [
            {"internalType": "string", "name": "batchId", "type": "string"},
            {"internalType": "bytes32", "name": "merkleRoot", "type": "bytes32"},
            {"internalType": "uint256", "name": "leafCount", "type": "uint256"},
        ],
        "name": "publish",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "string", "name": "batchId", "type": "string"}],
        "name": "getAnchor",
        "outputs": [
            {"internalType": "bytes32", "name": "merkleRoot", "type": "bytes32"},
            {"internalType": "uint256", "name": "timestamp", "type": "uint256"},
            {"internalType": "uint256", "name": "leafCount", "type": "uint256"},
        ],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "owner",
        "outputs": [{"internalType": "address", "name": "", "type": "address"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "address", "name": "newOwner", "type": "address"}],
        "name": "rotateOwner",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "internalType": "string", "name": "batchId", "type": "string"},
            {"indexed": False, "internalType": "bytes32", "name": "merkleRoot", "type": "bytes32"},
            {"indexed": False, "internalType": "uint256", "name": "leafCount", "type": "uint256"},
            {"indexed": False, "internalType": "uint256", "name": "timestamp", "type": "uint256"},
        ],
        "name": "AnchorPublished",
        "type": "event",
    },
]

# Fixed 2026-08-08 (docs-informed-quest-and-credential-generation-v1 /
# learn-to-earn-x402-credential-pipeline-v1): this previously pointed at
# `infrastructure/contracts/CredAnchor.sol` (parents[3]), a path that
# doesn't exist anywhere in the repo — same bug class as the
# `cianfhoghlaim.badges` import-path bugs fixed elsewhere in this
# change. `CredAnchor.sol` is a sibling of this file.
CONTRACT_SOURCE_PATH = Path(__file__).resolve().parent / "CredAnchor.sol"


def load_contract_source() -> str:
    """Load the Solidity source for compilation."""
    if not CONTRACT_SOURCE_PATH.exists():
        raise FileNotFoundError(f"CredAnchor.sol not found at {CONTRACT_SOURCE_PATH}")
    return CONTRACT_SOURCE_PATH.read_text()


def compile_contract() -> dict[str, Any]:
    """Compile CredAnchor.sol via py-solc-x (if installed).

    Returns:
        A dict with 'abi' and 'bytecode' keys, ready for web3.py deployment.

    Raises:
        RuntimeError: if py-solc-x is not installed or solc is missing.
    """
    try:
        import solcx  # type: ignore[import-not-found]
    except ImportError as exc:
        raise RuntimeError(
            "py-solc-x is required to compile CredAnchor.sol. "
            "Install with `uv add py-solc-x`."
        ) from exc

    solcx.install_solc("0.8.20")
    solcx.set_solc_version("0.8.20")
    source = load_contract_source()
    compiled = solcx.compile_source(
        source,
        output_values=["abi", "bin"],
        solc_version="0.8.20",
    )
    contract_id, contract_interface = compiled.popitem()
    return {
        "abi": contract_interface["abi"],
        "bytecode": contract_interface["bin"],
        "contract_id": contract_id,
    }


def deploy_to_base_l2(
    rpc_url: Optional[str] = None,
    private_key: Optional[str] = None,
) -> str:
    """Deploy the CredAnchor contract to Base L2.

    Args:
        rpc_url: Base L2 RPC URL (default: $CIANFHOGHLAIM_BASE_L2_RPC_URL).
        private_key: Deployer private key (default: $CIANFHOGHLAIM_DEPLOYER_PRIVATE_KEY).

    Returns:
        The deployed contract address (0x-prefixed hex).
    """
    try:
        from web3 import Web3  # type: ignore[import-not-found]
    except ImportError as exc:
        raise RuntimeError("web3.py is required to deploy. Install with `uv add web3`.") from exc

    rpc_url = rpc_url or os.environ.get("CIANFHOGHLAIM_BASE_L2_RPC_URL")
    private_key = private_key or os.environ.get("CIANFHOGHLAIM_DEPLOYER_PRIVATE_KEY")
    if not rpc_url:
        raise ValueError("CIANFHOGHLAIM_BASE_L2_RPC_URL not set")
    if not private_key:
        raise ValueError("CIANFHOGHLAIM_DEPLOYER_PRIVATE_KEY not set")

    w3 = Web3(Web3.HTTPProvider(rpc_url))
    if not w3.is_connected():
        raise RuntimeError(f"Cannot connect to Base L2 RPC: {rpc_url}")

    compiled = compile_contract()
    contract = w3.eth.contract(abi=compiled["abi"], bytecode=compiled["bytecode"])
    account = w3.eth.account.from_key(private_key)

    tx = contract.constructor().transact({"from": account.address})
    receipt = w3.eth.wait_for_transaction_receipt(tx)
    if receipt.status != 1:
        raise RuntimeError(f"Deployment transaction failed (status={receipt.status})")

    return receipt.contractAddress


def publish_anchor(
    contract_address: str,
    batch_id: str,
    merkle_root_hex: str,
    leaf_count: int,
    rpc_url: Optional[str] = None,
    private_key: Optional[str] = None,
) -> str:
    """Publish a daily Merkle root anchor to the deployed CredAnchor contract.

    Args:
        contract_address: The deployed CredAnchor address.
        batch_id: YYYY-MM-DD batch identifier.
        merkle_root_hex: Hex-encoded 32-byte Merkle root (0x-prefixed).
        leaf_count: Number of badges in this batch.
        rpc_url: Base L2 RPC URL.
        private_key: Owner private key.

    Returns:
        The transaction hash (0x-prefixed hex).
    """
    try:
        from web3 import Web3  # type: ignore[import-not-found]
    except ImportError as exc:
        raise RuntimeError("web3.py is required. Install with `uv add web3`.") from exc

    rpc_url = rpc_url or os.environ.get("CIANFHOGHLAIM_BASE_L2_RPC_URL")
    private_key = private_key or os.environ.get("CIANFHOGHLAIM_DEPLOYER_PRIVATE_KEY")
    if not rpc_url:
        raise ValueError("CIANFHOGHLAIM_BASE_L2_RPC_URL not set")
    if not private_key:
        raise ValueError("CIANFHOGHLAIM_DEPLOYER_PRIVATE_KEY not set")

    w3 = Web3(Web3.HTTPProvider(rpc_url))
    contract = w3.eth.contract(address=contract_address, abi=CREEDANCHOR_ABI)
    account = w3.eth.account.from_key(private_key)

    tx = contract.functions.publish(batch_id, merkle_root_hex, leaf_count).transact(
        {"from": account.address}
    )
    receipt = w3.eth.wait_for_transaction_receipt(tx)
    if receipt.status != 1:
        raise RuntimeError(f"Publish transaction failed (status={receipt.status})")
    return receipt.transactionHash.hex()


def get_anchor(
    contract_address: str,
    batch_id: str,
    rpc_url: Optional[str] = None,
) -> dict[str, Any]:
    """Look up a published anchor from the contract.

    Returns:
        A dict with `merkleRoot` (0x-hex), `timestamp` (int), `leafCount` (int).
    """
    try:
        from web3 import Web3  # type: ignore[import-not-found]
    except ImportError as exc:
        raise RuntimeError("web3.py is required. Install with `uv add web3`.") from exc

    rpc_url = rpc_url or os.environ.get("CIANFHOGHLAIM_BASE_L2_RPC_URL")
    if not rpc_url:
        raise ValueError("CIANFHOGHLAIM_BASE_L2_RPC_URL not set")

    w3 = Web3(Web3.HTTPProvider(rpc_url))
    contract = w3.eth.contract(address=contract_address, abi=CREEDANCHOR_ABI)
    merkle_root, timestamp, leaf_count = contract.functions.getAnchor(batch_id).call()
    return {
        "merkleRoot": "0x" + merkle_root.hex(),
        "timestamp": int(timestamp),
        "leafCount": int(leaf_count),
    }