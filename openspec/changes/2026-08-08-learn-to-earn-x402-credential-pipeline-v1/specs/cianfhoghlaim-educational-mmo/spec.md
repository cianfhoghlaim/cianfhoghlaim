## MODIFIED Requirements

### Requirement: Hybrid x402 educational credential

The system SHALL issue educational credentials as off-chain
`SkillTreeBadge`s (Convex + FalkorDB + LanceDB) plus a daily Merkle
root anchored on Base L2 via the `CredAnchor` smart contract. Each
badge SHALL be ETH-signed by the issuing agent's wallet and SHALL
include the NCCA learning outcome code, the agent issuer, the date
earned, the evidence hash, and the bilingual competency text (EN +
GA where applicable). The on-chain anchor SHALL be queryable via a
public verification page that recomputes the Merkle path. Badge
issuance SHALL actually reach Convex — the issuing call path SHALL
NOT depend on an import path that doesn't resolve to the installed
package. The daily Merkle-anchor publish SHALL run on a real
schedule, not merely be described in a docstring with no
corresponding Dagster asset.

#### Scenario: Badge is issued after quest completion

- **GIVEN** a student has completed a Mathematics quest at HL level
  covering `LC-MATHS-LO-2.4`
- **WHEN** the `math_agent` validates the student's final response and
  calls `from cianfhoghlaim.tuatha.badges import issue_badge`
- **THEN** a `SkillTreeBadge` row is created in Convex with
  `framework="ncca-lc"`, `level="hl"`, `subject="mathematics"`,
  `competency_code="LC-MATHS-LO-2.4"`, `agent_issuer="math_agent"`,
  and an ETH signature from the agent's wallet
- **AND** a corresponding FalkorDB `SkillTreeBadge` node is created
  with edges to the player's profile node and to the LO node

#### Scenario: Daily Merkle anchor published on Base L2

- **GIVEN** the `daily_credential_anchor` Dagster asset
  (`orchestration/defs/5_agent_ops/credential_assets.py`) is scheduled
  via `daily_credential_anchor_at_2am` (`cron_schedule="0 2 * * *"`)
- **WHEN** the schedule fires and there are ≥1 new badges since the
  last anchor
- **THEN** the asset computes the Merkle root of the new badges
- **AND** the asset calls `CredAnchor.publish(root, batchId)` on Base L2
- **AND** the asset writes the resulting `tx_hash` back into each
  badge row in Convex

#### Scenario: Third party verifies a badge

- **GIVEN** a badge with `id = "uuid"`, `evidence_hash = "0x..."`,
  `on_chain_anchor = "0x..."` (Base L2 tx_hash), and `anchor_date = "2026-07-01"`
- **WHEN** a third party calls `GET /anchor/2026-07-01`
- **THEN** the page displays the Merkle root published on Base L2
- **AND** the page accepts the badge's `id + evidence_hash` and
  verifies the Merkle path against the on-chain root
- **AND** the verification result is a clear pass/fail indicator

#### Scenario: x402 payment state survives a process restart

- **GIVEN** a student initiates an x402 payment via `POST
  /payments/request` and receives a `payment_id`
- **WHEN** the `agents/api/routes/routes/payments.py` process restarts
  before the payment is verified
- **THEN** `GET /payments/status/{payment_id}` still returns the
  correct pending/expired status, read from the Convex `x402Payments`
  table rather than an in-memory dict that would have been wiped by
  the restart
