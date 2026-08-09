"""infrastructure.contracts.achievement_token — Deploy + mint AchievementToken.

Companion to `infrastructure/contracts/AchievementToken.sol` (Solidity
source). Mirrors `cred_anchor.py`'s structure exactly — same compile/
deploy pattern, same env-var conventions — for a second, narrower
contract: a non-transferable, capped, badge-gated learn-to-earn token.

Per `2026-08-08-learn-to-earn-x402-credential-pipeline-v1`.

Production usage requires:
- `web3>=6.0`
- A funded Base L2 wallet (the contract owner + initial minter)
- The deployed `AchievementToken` address in
  `CIANFHOGHLAIM_ACHIEVEMENT_TOKEN_ADDRESS`
- The RPC URL in `CIANFHOGHLAIM_BASE_L2_RPC_URL`

Reference:
    openspec/changes/2026-08-08-learn-to-earn-x402-credential-pipeline-v1/
    tuatha/badges/ledger.py (the minting caller, once wired)
    tuatha/contracts/AchievementToken.sol
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Optional

# ABI mirrors the functions + events in AchievementToken.sol
ACHIEVEMENT_TOKEN_ABI = [
    {
        "inputs": [{"internalType": "address", "name": "initialMinter", "type": "address"}],
        "stateMutability": "nonpayable",
        "type": "constructor",
    },
    {
        "inputs": [
            {"internalType": "address", "name": "student", "type": "address"},
            {"internalType": "bytes32", "name": "evidenceHash", "type": "bytes32"},
        ],
        "name": "mint",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "address", "name": "", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "totalSupply",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "bytes32", "name": "", "type": "bytes32"}],
        "name": "mintedForEvidence",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
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
        "inputs": [],
        "name": "minter",
        "outputs": [{"internalType": "address", "name": "", "type": "address"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "address", "name": "newMinter", "type": "address"}],
        "name": "rotateMinter",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "internalType": "address", "name": "student", "type": "address"},
            {"indexed": False, "internalType": "uint256", "name": "amount", "type": "uint256"},
            {"indexed": True, "internalType": "bytes32", "name": "evidenceHash", "type": "bytes32"},
        ],
        "name": "AchievementMinted",
        "type": "event",
    },
]

CONTRACT_SOURCE_PATH = Path(__file__).resolve().parent / "AchievementToken.sol"


def load_contract_source() -> str:
    """Load the Solidity source for compilation."""
    if not CONTRACT_SOURCE_PATH.exists():
        raise FileNotFoundError(f"AchievementToken.sol not found at {CONTRACT_SOURCE_PATH}")
    return CONTRACT_SOURCE_PATH.read_text()


def compile_contract() -> dict[str, Any]:
    """Compile AchievementToken.sol via py-solc-x (if installed).

    Returns:
        A dict with 'abi', 'bytecode', and 'contract_id' keys, ready for
        web3.py deployment.

    Raises:
        RuntimeError: if py-solc-x is not installed or solc is missing.
    """
    try:
        import solcx  # type: ignore[import-not-found]
    except ImportError as exc:
        raise RuntimeError(
            "py-solc-x is required to compile AchievementToken.sol. "
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
    initial_minter: str,
    rpc_url: Optional[str] = None,
    private_key: Optional[str] = None,
) -> str:
    """Deploy the AchievementToken contract to Base L2.

    Args:
        initial_minter: The address authorized to call mint() — typically
            the same badge-issuance service wallet that signs
            `issue_badge()` calls.
        rpc_url: Base L2 RPC URL (default: $CIANFHOGHLAIM_BASE_L2_RPC_URL).
        private_key: Deployer private key (default:
            $CIANFHOGHLAIM_DEPLOYER_PRIVATE_KEY).

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

    tx = contract.constructor(initial_minter).transact({"from": account.address})
    receipt = w3.eth.wait_for_transaction_receipt(tx)
    if receipt.status != 1:
        raise RuntimeError(f"Deployment transaction failed (status={receipt.status})")

    return receipt.contractAddress


def mint_achievement(
    contract_address: str,
    student_address: str,
    evidence_hash_hex: str,
    rpc_url: Optional[str] = None,
    private_key: Optional[str] = None,
) -> str:
    """Mint achievement tokens for a student on a real badge issuance.

    Args:
        contract_address: The deployed AchievementToken address.
        student_address: The student's wallet address.
        evidence_hash_hex: The badge's evidence_hash (0x-prefixed
            32-byte hex) — the same value anchored via CredAnchor.
        rpc_url: Base L2 RPC URL.
        private_key: Minter private key.

    Returns:
        The transaction hash (0x-prefixed hex).
    """
    try:
        from web3 import Web3  # type: ignore[import-not-found]
    except ImportError as exc:
        raise RuntimeError("web3.py is required. Install with `uv add web3`.") from exc

    rpc_url = rpc_url or os.environ.get("CIANFHOGHLAIM_BASE_L2_RPC_URL")
    private_key = private_key or os.environ.get("CIANFHOGHLAIM_MINTER_PRIVATE_KEY")
    if not rpc_url:
        raise ValueError("CIANFHOGHLAIM_BASE_L2_RPC_URL not set")
    if not private_key:
        raise ValueError("CIANFHOGHLAIM_MINTER_PRIVATE_KEY not set")

    w3 = Web3(Web3.HTTPProvider(rpc_url))
    contract = w3.eth.contract(address=contract_address, abi=ACHIEVEMENT_TOKEN_ABI)
    account = w3.eth.account.from_key(private_key)

    tx = contract.functions.mint(student_address, evidence_hash_hex).transact(
        {"from": account.address}
    )
    receipt = w3.eth.wait_for_transaction_receipt(tx)
    if receipt.status != 1:
        raise RuntimeError(f"Mint transaction failed (status={receipt.status})")
    return receipt.transactionHash.hex()


def get_balance(
    contract_address: str,
    student_address: str,
    rpc_url: Optional[str] = None,
) -> int:
    """Look up a student's achievement-token balance."""
    try:
        from web3 import Web3  # type: ignore[import-not-found]
    except ImportError as exc:
        raise RuntimeError("web3.py is required. Install with `uv add web3`.") from exc

    rpc_url = rpc_url or os.environ.get("CIANFHOGHLAIM_BASE_L2_RPC_URL")
    if not rpc_url:
        raise ValueError("CIANFHOGHLAIM_BASE_L2_RPC_URL not set")

    w3 = Web3(Web3.HTTPProvider(rpc_url))
    contract = w3.eth.contract(address=contract_address, abi=ACHIEVEMENT_TOKEN_ABI)
    return int(contract.functions.balanceOf(student_address).call())
