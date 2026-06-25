---
name: tuatha-achievement-ledger
description: The KCG Phase 6 educational-achievement ledger in `sruth/tuatha/sruth/crypteolas/achievements/`. Covers the 8-field skill-tree badge schema (framework × level × subject × competency × learning_outcome_code × date_earned × agent_issuer × evidence), the 5 cross-framework "Cross-British-Isles Achiever" masteries (one per Pent-Elemental realm), the cryptographic evidence chain (the `evidence` field is signed by the issuing agent's wallet), the cross-quest retrieval via the `sruth/tuatha/knowledge_graph/hybrid_search.py` engine, and the canonical add-a-new-badge workflow. Use when adding a new badge type, wiring the `quest_guide_agent` → crypteolas handoff, implementing the 5 mastery badges per Pent-Elemental realm, or asking "where is the achievement ledger from Phase 6?".
---

# Tuatha Achievement Ledger

## Purpose

The `sruth/tuatha/sruth/crypteolas/achievements/` directory houses the
**educational-achievement ledger** promised by Phase 6 of the
6-phase refactor plan (the `tuatha-formative-assessment-v1` openspec
change, archived 2026-06-24). This skill captures the 8-field
skill-tree badge schema, the 5 cross-framework masteries, the
cryptographic evidence chain, and the add-a-new-badge workflow.

**The ledger is NOT a financial token.** The badges are
skill-tree credentials, not CELT tokens. x402 micropayments
are reserved for gated game features only (cosmetics, premium
quests, paid DLC) — never for educational content.

## When to use this skill

Use when you need to:

- "Add a new badge type"
- "Wire the `quest_guide_agent` → crypteolas handoff"
- "Implement the 5 mastery badges per Pent-Elemental realm"
- "Understand the 8-field badge schema"
- "Issue the first skill-tree badge"
- "Query the ledger for cross-quest retrieval"

## The 8-field badge schema (the core dataclass)

```python
# sruth/tuatha/sruth/crypteolas/achievements/ledger.py
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

class CurriculumFramework(str, Enum):
    NCCA = "NCCA"      # Ireland (Primary / JC / SC)
    CFE = "CFE"        # Scotland (Early / First-Second / Third-Fourth / Senior)
    CFW = "CFW"        # Wales (Foundation / KS3-4 / KS5)
    CCEA = "CCEA"      # Northern Ireland (Foundation / KS1-4 / Post-16)
    SQA = "SQA"        # Scotland post-16 (National 3-5 / Higher / Advanced Higher)

class PentElementalRealm(str, Enum):
    SPIRIT = "spirit"
    WATER = "water"
    FIRE = "fire"
    EARTH = "earth"
    AIR = "air"

@dataclass
class SkillTreeBadge:
    # The 8 fields (per Phase 6 spec):
    framework: CurriculumFramework        # 1
    level: str                            # 2 ("JC3" / "CfE Third Level" / "Progression Step 3")
    subject: str                          # 3 ("Gaeilge" / "Mathematics" / "History")
    competency: str                       # 4 ("Vocabulary" / "Comprehension" / "Problem-solving")
    learning_outcome_code: str            # 5 ("JC-Gaeilge-LO-2.4" / "CfE-MN-2.5")
    date_earned: datetime                 # 6
    agent_issuer: str                     # 7 ("quest_guide_agent" / "celtic_tutor_agent" / etc.)
    evidence: str                         # 8 (a 3-sentence player reflection)

    # Optional metadata:
    player_id: str | None = None
    realm: PentElementalRealm | None = None
    xp_awarded: int = 100
    badge_id: str = field(default_factory=lambda: f"{framework}-{level}-{subject}-{datetime.utcnow().isoformat()}")
```

The 8 fields are the canonical home for the per-quest badge
data, derived from the `.agents/skills/british-isles-formative-assessment/SKILL.md`
pedagogical framework.

## The 5 cross-framework masteries (one per Pent-Elemental realm)

The "Cross-British-Isles Achiever" masteries are awarded when a
player has earned at least 1 badge in **each of the 5 frameworks**
(NCCA + CfE + CfW + CCEA + SQA):

| Mastery | Pent-Elemental realm | Required badges |
|:--|:--|:--|
| `Mastery of Spirit` | `Spirit` (the invisible + the contemplative) | 1 NCCA + 1 CfE + 1 CfW + 1 CCEA + 1 SQA |
| `Mastery of Water` | `Water` (the Celtic + the sea) | 1 NCCA + 1 CfE + 1 CfW + 1 CCEA + 1 SQA |
| `Mastery of Fire` | `Fire` (the transformation + the hero) | 1 NCCA + 1 CfE + 1 CfW + 1 CCEA + 1 SQA |
| `Mastery of Earth` | `Earth` (the language + the land) | 1 NCCA + 1 CfE + 1 CfW + 1 CCEA + 1 SQA |
| `Mastery of Air` | `Air` (the wind + the voice) | 1 NCCA + 1 CfE + 1 CfW + 1 CCEA + 1 SQA |

The 5 masteries are auto-issued by the `AchievementLedger.issue_badge`
method when the player reaches the 5-framework threshold.

## The cryptographic evidence chain

The `evidence` field is **cryptographically signed by the issuing
agent's wallet**. The signature uses the same SIWE (Sign-In With
Ethereum) contract as the player's authentication:

```python
# sruth/tuatha/sruth/crypteolas/achievements/ledger.py
from eth_account import Account
from eth_account.messages import encode_defunct
import hashlib

def _sign_evidence(evidence: str, agent_wallet: str) -> str:
    """Sign the evidence with the agent's wallet (the cryptographic chain)."""
    msg = encode_defunct(text=evidence)
    signed = Account.sign_message(msg, private_key=AGENT_PRIVATE_KEY)
    return signed.signature.hex()

def _verify_evidence(evidence: str, signature: str, expected_address: str) -> bool:
    """Verify the evidence signature (the cryptographic chain)."""
    msg = encode_defunct(text=evidence)
    recovered = Account.recover_message(msg, signature=signature)
    return recovered.lower() == expected_address.lower()
```

The signature is stored in a parallel `SkillTreeBadge.signature`
field. The verification is run on every ledger query.

## The cross-quest retrieval (the knowledge graph hook)

The `sruth/tuatha/sruth/crypteolas/achievements/` ledger integrates with the
`sruth/tuatha/knowledge_graph/hybrid_search.py` engine (the canonical
home for the knowledge graph). The integration:

- The badge's `evidence` field is indexed in the Cognee knowledge
  graph (as an entity with the `SkillTreeBadge` type)
- The cross-quest retrieval returns the 3 most relevant badges
  for any new quest (per the quest's Pent-Elemental realm + the
  player's current framework × level)
- The retrieval is exposed via the `/sruth/crypteolas/achievements/relevant/<player_id>/<realm>`
  endpoint (the FastAPI surface)

## The 4 CLI commands (the canonical ops surface)

```bash
# 1. Issue a badge
uv run python -m tuatha.crypteolas.achievements.cli issue \
  --framework=NCCA --level=JC3 --subject=Gaeilge \
  --competency=Vocabulary --lo=JC-Gaeilge-LO-2.4 \
  --agent-issuer=quest_guide_agent \
  --player=demo_user_001 \
  --evidence="I learned 50 new Irish words across 3 quests."

# 2. Query a player's badges
uv run python -m tuatha.crypteolas.achievements.cli list \
  --player=demo_user_001

# 3. Verify a badge signature
uv run python -m tuatha.crypteolas.achievements.cli verify \
  --badge-id=NCCA-JC3-Gaeilge-2026-06-24T10-30-00Z

# 4. Issue a Cross-British-Isles Achiever mastery
uv run python -m tuatha.crypteolas.achievements.cli mastery \
  --player=demo_user_001 --realm=earth
```

## The LanceDB storage

The badges are stored in LanceDB (the canonical vector + table
store) at table `crypteolas_achievements`. The schema:

```python
# sruth/tuatha/sruth/crypteolas/achievements/storage.py
import lancedb
from lancedb.pydantic import LanceModel

class SkillTreeBadgeRecord(LanceModel):
    badge_id: str
    framework: str
    level: str
    subject: str
    competency: str
    learning_outcome_code: str
    date_earned: str  # ISO 8601
    agent_issuer: str
    evidence: str
    evidence_signature: str
    player_id: str
    realm: str | None = None
    xp_awarded: int = 100
    vector: list[float]  # 1024-dim BAAI/bge-m3 embedding
```

The `vector` field is the BGE-m3 embedding of the concatenated
`evidence + subject + competency` text, used for semantic
retrieval.

## Worked example: add a new badge type

1. Add the badge class to `sruth/tuatha/sruth/crypteolas/achievements/ledger.py`:

   ```python
   @dataclass
   class ReadingComprehensionBadge(SkillTreeBadge):
       """A reading-comprehension badge (extends SkillTreeBadge)."""
       cefr_level: str = "B1"  # the CEFR reading level
       words_read: int = 0
       comprehension_score: float = 0.0
   ```

2. Add the BAML extraction at
   `sruth/tuatha/baml_src/achievement_extraction.baml`:

   ```baml
   class ReadingComprehensionBadge {
       framework string
       level string
       subject string
       cefr_level string
       words_read int
       comprehension_score float
       evidence string
   }

   function ExtractReadingComprehensionBadge(text: string) -> ReadingComprehensionBadge {
       client ExtractEn
       prompt #"Extract the reading-comprehension badge from: {{ text }}"#
   }
   ```

3. Wire the `quest_guide_agent` → crypteolas handoff in
   `sruth/oideachais/agents/adk/quest_guide_agent.py`:

   ```python
   async def issue_badge_tool(player_id: str, evidence: str):
       badge = SkillTreeBadge(
           framework="NCCA",
           level="JC3",
           subject="Gaeilge",
           competency="Reading",
           learning_outcome_code="JC-Gaeilge-LO-2.4",
           date_earned=datetime.utcnow(),
           agent_issuer="quest_guide_agent",
           evidence=evidence,
       )
       await AchievementLedger.issue(badge)
       return {"badge_id": badge.badge_id}
   ```

4. Update the knowledge graph hook at
   `sruth/tuatha/knowledge_graph/hybrid_search.py` to index the new
   badge type.

## Common failure modes

| Symptom | Cause | Fix |
|:--|:--|:--|
| The badge signature verification fails | The agent's private key is wrong | Rotate the agent's key + re-sign the badge |
| The Cross-British-Isles Achiever is not issued | The player has 4 frameworks but not 5 | Issue at least 1 badge in the 5th framework |
| The LanceDB table is missing | The storage initialisation was never run | Run `AchievementLedger.init_storage()` on first use |
| The BAML extraction returns the wrong framework | The prompt is ambiguous | Make the prompt more explicit about the framework |
| The Cognee integration is stale | The hybrid_search engine needs re-indexing | Run `sruth/tuatha/knowledge_graph/hybrid_search.py:reindex()` |

## Cross-references

- `.agents/skills/tuatha-mmo/SKILL.md` — the MMO tech stack
- `.agents/skills/british-isles-formative-assessment/SKILL.md` — the pedagogical framework
- `.agents/skills/pent-elemental-cosmology/SKILL.md` — the 5 realms
- `.agents/skills/tuatha-mcp-server-tools/SKILL.md` — the 5 MCP tools
- `sruth/tuatha/sruth/crypteolas/achievements/ledger.py` — the 8-field badge schema
- `sruth/tuatha/sruth/crypteolas/achievements/storage.py` — the LanceDB storage
- `sruth/tuatha/sruth/crypteolas/achievements/cli.py` — the 4 CLI commands
- `sruth/tuatha/knowledge_graph/hybrid_search.py` — the cross-quest retrieval
- `sruth/oideachais/agents/adk/quest_guide_agent.py` — the badge-issuing agent
- `sruth/oideachais/baml_src/achievement_extraction.baml` — the BAML extraction
- `openspec/specs/tuatha-platform/spec.md` — the canonical spec (the "Crypteolas educational-achievement ledger" MODIFIED Requirement)
