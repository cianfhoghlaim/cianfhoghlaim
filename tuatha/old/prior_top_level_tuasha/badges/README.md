# Badges — Hybrid x402 educational credential subsystem

The `cianfhoghlaim.tuatha.badges` subsystem implements the hybrid
educational credential for the Cianfhoghlaim Educational MMO.

## Design

**Off-chain `SkillTreeBadge`** (the student-facing record):
- Stored in **Convex** (the `badges` table) — fast reads, real-time UI
- Mirrored to **FalkorDB** as a `SkillTreeBadge` node — cross-realm mastery
- Mirrored to **LanceDB** with BGE-M3 1024-dim embedding of
  `competency_text_en + competency_text_ga + subject + competency_code`

**On-chain Merkle anchor** (the third-party-verifiable proof):
- Daily Merkle root of new badges published to **Base L2** via `CredAnchor.sol`
- Any third party (employer, university) can verify a badge by
  recomputing the Merkle path against the on-chain anchor
- The x402 protocol pays the gas from the platform's treasury (≈$0.01/anchor)

## Schema

```python
class SkillTreeBadge(BaseModel):
    id: str                                  # UUID
    student_id: str                          # Hash of student pseudonym + salt
    framework: str                           # 'ncca-lc' or 'ncca-jc'
    level: str                               # 'hl', 'ol', 'fl', or 'jc'
    subject: str                             # e.g. 'mathematics', 'gaeilge'
    competency_code: str                     # e.g. 'LC-MATHS-LO-2.4'
    competency_text: BilingualText
    date_earned: datetime
    agent_issuer: str                        # e.g. 'math_agent'
    evidence: EvidenceLink
    evidence_hash: str                       # SHA-256 of evidence, used as Merkle leaf
    signature: str                           # ETH signature from agent wallet
    on_chain_anchor: Optional[str]           # Base L2 tx_hash (when published)
    anchor_date: Optional[str]               # YYYY-MM-DD of the daily anchor batch
```

## Usage

```python
from cianfhoghlaim.tuatha.badges import issue_badge, fetch_badges_for_student

# Issue a new badge after quest completion
badge = await issue_badge(
    student_id="hash-of-pseudonym+salt",
    framework="ncca-lc",
    level="hl",
    subject="mathematics",
    competency_code="LC-MATHS-LO-2.4",
    agent_issuer="math_agent",
    evidence=EvidenceLink(
        item_id="...",
        response="...",
        score_pct=85.0,
        feedback_en="...",
    ),
)

# Fetch all badges for a student (mastery wallet)
badges = await fetch_badges_for_student("hash-of-pseudonym+salt")
```

## Verification (third party)

A third party (employer, university) can verify a badge by:

1. Navigate to `https://cianfhoghlaim-mmo.cianfhoghlaim.ie/anchor/<date>`
2. Read the Merkle root published on Base L2 for that date
3. Enter the badge `id + evidence_hash` into the verifier
4. Recompute the Merkle path against the on-chain root
5. Get a clear pass/fail indicator

## Reference

- `openspec/specs/cianfhoghlaim-educational-mmo/spec.md`
- `openspec/changes/cianfhoghlaim-educational-mmo-v1/proposal.md` (D4)
- `cianfhoghlaim/badges/schema.py` (canonical types)
- `infrastructure/contracts/CredAnchor.sol` (Solidity source)