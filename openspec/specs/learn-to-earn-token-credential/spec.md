# learn-to-earn-token-credential Specification

## Purpose
The Learn-to-Earn token + credential surface covers the x402 payment protocol + the credential issuance flow (token + on-chain credential + revocation list) across the Cianfhoghlaim monorepo. It defines 1 invariant: the canonical token-credential contract that ties the educational activity (notebook completion / LC subject mastery / Celtic language fluency) to a portable credential that third parties can verify.

## Requirements
### Requirement: Badge-gated, non-transferable achievement token

The system SHALL provide `AchievementToken` (`tuatha/contracts/
AchievementToken.sol`), an ERC20-shaped contract with `name`,
`symbol`, `decimals`, `totalSupply`, and `balanceOf` for wallet/
explorer compatibility, that mints `MINT_AMOUNT_PER_BADGE` tokens to a
student's wallet only when triggered by a real, verified badge
issuance (`tuatha/badges/ledger.py::issue_badge()`), capped at
`MAX_SUPPLY`. The contract SHALL be structurally non-transferable —
`transfer`, `transferFrom`, and `approve` SHALL all revert
unconditionally — so the token functions as a soulbound achievement
record, not a spendable or tradeable currency. The contract SHALL NOT
implement staking, lending, a DEX, or prediction-market functionality.

#### Scenario: Token minted on real badge issuance

- **GIVEN** a student with a connected wallet address completes a
  formative item and earns a `SkillTreeBadge` with
  `evidence_hash = "0xabc..."`
- **WHEN** `issue_badge()` completes and a wallet address was supplied
- **THEN** `AchievementToken.mint(student, evidenceHash)` is called
- **AND** the student's on-chain balance increases by
  `MINT_AMOUNT_PER_BADGE`
- **AND** a second `mint()` call with the same `evidenceHash` reverts
  (idempotent against retries)

#### Scenario: Token cannot be transferred

- **GIVEN** a student holds a nonzero `AchievementToken` balance
- **WHEN** any address calls `transfer`, `transferFrom`, or `approve`
  on the contract
- **THEN** the call reverts unconditionally
- **AND** no balance changes as a result

#### Scenario: Mint fails gracefully without a wallet on file

- **GIVEN** a student has earned a badge but has no `walletAddress` on
  their Convex `students` row (no SIWE auth flow exists yet)
- **WHEN** `issue_badge()` runs
- **THEN** the off-chain `SkillTreeBadge` is still created successfully
- **AND** the `AchievementToken.mint()` call is skipped entirely,
  logged as a no-op, and does not raise

