"""infrastructure.contracts — Deployable Solidity contracts for Cianfhoghlaim.

Currently houses:
- `CredAnchor.sol` — the daily Merkle root anchor for the hybrid x402
  educational credential (cianfhoghlaim-educational-mmo-v1 Phase 4).
- `cred_anchor.py` — Python wrapper for compile / deploy / publish / verify.

Reference:
    openspec/changes/cianfhoghlaim-educational-mmo-v1/proposal.md (D4)
    openspec/specs/cianfhoghlaim-educational-mmo/spec.md
"""
from .cred_anchor import (
    CREEDANCHOR_ABI,
    compile_contract,
    deploy_to_base_l2,
    get_anchor,
    publish_anchor,
)

__all__ = [
    "CREEDANCHOR_ABI",
    "compile_contract",
    "deploy_to_base_l2",
    "get_anchor",
    "publish_anchor",
]