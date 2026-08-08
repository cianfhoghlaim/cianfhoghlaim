"""badges.achievement_token_client — async bridge from `ledger.py` to the
deployed `AchievementToken` contract.

`tuatha/contracts/achievement_token.py` is a synchronous, web3.py-based
module (mirroring `cred_anchor.py`'s style); `ledger.py::issue_badge()`
is async. This thin wrapper reads the deployed contract address from env
config and runs the synchronous mint call in a thread, so a slow/blocked
RPC call never stalls the badge-issuance event loop.

Per `2026-08-08-learn-to-earn-x402-credential-pipeline-v1`.
"""
from __future__ import annotations

import asyncio
import os


async def mint_for_badge(student_wallet_address: str, evidence_hash: str) -> str | None:
    """Mint achievement tokens for a badge's evidence_hash.

    Returns the transaction hash on success, or None if minting is not
    configured (no deployed contract address / no minter key / web3.py
    not installed) — all of which are legitimate, expected states in
    dev/test environments, not errors.
    """
    contract_address = os.environ.get("CIANFHOGHLAIM_ACHIEVEMENT_TOKEN_ADDRESS")
    if not contract_address:
        return None

    evidence_hash_hex = evidence_hash if evidence_hash.startswith("0x") else f"0x{evidence_hash}"

    def _mint() -> str:
        from tuatha.contracts.achievement_token import mint_achievement

        return mint_achievement(
            contract_address=contract_address,
            student_address=student_wallet_address,
            evidence_hash_hex=evidence_hash_hex,
        )

    return await asyncio.to_thread(_mint)
