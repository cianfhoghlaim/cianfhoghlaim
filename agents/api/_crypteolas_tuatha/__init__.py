"""Tuatha Crypteolas — the educational-achievement ledger + x402 settlement.

Per Phase 6 of the 6-phase refactor plan (see the
`tuatha-formative-assessment-v1` openspec change archived
2026-06-24), the crypteolas directory is now focused on
**educational achievements** (skill-tree badges), not a
financial token. x402 micropayments are reserved for gated
game features only (cosmetics, premium quests, paid DLC) —
never for educational content.

Public surfaces:
- `crypteolas.achievements` — the skill-tree badge ledger
  (the Phase 6 deliverable; 8-field schema + 5 Pent-Elemental
  realm masteries + LanceDB storage + BGE-M3 embeddings)
- `crypteolas.x402` — the x402 payment protocol (for paid
  game features only)
"""
