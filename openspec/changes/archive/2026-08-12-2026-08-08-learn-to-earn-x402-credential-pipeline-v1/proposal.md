# Change: Learn-to-earn x402 credential pipeline

## Why

`tuatha/badges/` (the `SkillTreeBadge` schema, Merkle-anchor math,
FalkorDB/LanceDB mirrors) and `tuatha/contracts/CredAnchor.sol`
("Educational, NOT financial") are real, substantial, and consistent
with each other — but broken at small, concrete points rather than
architecturally incomplete. Every one of the 8 subject agents' scoring
tools imports `from cianfhoghlaim.badges import issue_badge` — a path
that has never resolved (the real module installs as
`cianfhoghlaim.tuatha.badges`), silently swallowed by a bare `except
ImportError`, so no badge has ever actually issued through this path.
`tuatha/badges/anchor.py`'s own on-chain publish helper has the
identical wrong-path bug. `tuatha/contracts/cred_anchor.py`'s
`CONTRACT_SOURCE_PATH` pointed at `infrastructure/contracts/
CredAnchor.sol` via `parents[3]` — a path that has never existed;
`CredAnchor.sol` actually lives as this module's own sibling. The
`daily_credential_anchor` Dagster asset that would publish Merkle
roots to Base L2 is referenced in three docstrings and defined
nowhere. Real x402 payment routes already exist and work
(`agents/api/routes/routes/payments.py` — HTTP 402 flow, on-chain
verification via web3, Chainlink ETH/USD price feed, USDC/ETH on
Base) but stored all payment state in an in-memory dict, lost on
every process restart, with a placeholder receiver address.

Separately, the "learn-to-earn" research this repo already has
(`docs/research/game/Learn-to-Earn Blockchain and AI.md` and
related) has no concrete, non-speculative implementation. A large,
separate, orphaned prototype track (`notebooks/16_speedrun_mmo_*`,
~9,600 lines, plus a full Foundry Solidity project at `sruth/shared/
blockchain/ethereum/contracts/`) prototypes a genuine fungible-
currency economy — an ERC20 "CelticUSD" stablecoin, staking, lending,
a DEX, prediction markets, NFT creatures. `CredAnchor.sol`'s own
"Educational, NOT financial" framing reads as a direct rebuttal to
that track, and this change deliberately does not resurrect it — see
Dependencies below for the explicit scoping confirmation this
decision rests on.

The NCCA's own commissioned research grounds the credential design
directly: `leaving_certificate/the-potential-of-technology-to-support-
online-certification-and-reporting.pdf` (H2 Learning for NCCA, Aug
2024) reviews digital badges, digital credentials, and
micro-credentials as an established pattern for presenting verified
learning achievement — the framing this change's `AchievementToken`
implements concretely, not a bolted-on cryptocurrency feature.

## What Changes

- Fix the dead badge-issuance import in all 8
  `agents/tuatha/tools/<subject>_response_score.py` files (and the
  identical bug in `tuatha/badges/anchor.py`'s on-chain publish
  helper, and `tuatha/badges/README.md`'s own incorrect example).
- Fix `tuatha/contracts/cred_anchor.py`'s `CONTRACT_SOURCE_PATH` to
  point at the contract's real location.
- Write the missing `daily_credential_anchor` Dagster asset + a
  02:00 UTC schedule (`orchestration/defs/5_agent_ops/
  credential_assets.py`, new) — the scheduler referenced in 3
  docstrings but defined nowhere before this change.
- New `tuatha/contracts/AchievementToken.sol` — a capped (100M),
  non-transferable (`transfer`/`transferFrom`/`approve` all revert),
  badge-gated (`mint()` is `onlyMinter`, idempotent per
  `evidenceHash`) ERC20-shaped token: 10 units minted per verified
  badge, no staking/lending/trading/prediction-market surface
  anywhere in the contract. Generically named per the operator's own
  stated sequencing (Celtic re-theming deferred to a later, separate
  change). Companion `tuatha/contracts/achievement_token.py` (compile/
  deploy/mint/balance, mirroring `cred_anchor.py`'s structure) and
  `tuatha/badges/achievement_token_client.py` (async bridge run via
  `asyncio.to_thread`).
- Wire `AchievementToken.mint()` into `tuatha/badges/ledger.py`'s
  `issue_badge()` as an additive, best-effort step 6 — only fires
  when a `student_wallet_address` is supplied (the common case today
  is no wallet on file, since Convex's `students` table has no
  `walletAddress` field until this change adds one); a failed or
  skipped mint never blocks badge issuance.
- Harden `agents/api/routes/routes/payments.py`: durable Convex-backed
  payment state (`_ConvexPaymentStore`, new `x402Payments` Convex
  table) replacing the in-memory `_payment_requests`/
  `_completed_payments` dicts across every route handler
  (`request_payment`, `verify_payment`, `get_payment_status`,
  `create_402_response`, `check_payment_or_free`); `RECEIVER_ADDRESS`
  now reads from `CIANFHOGHLAIM_X402_RECEIVER_ADDRESS` instead of a
  placeholder constant.
- Add `walletAddress` (optional) to the Convex `students` table.

## Dependencies

`Blocked by: 2026-08-08-docs-informed-quest-and-credential-generation-v1`
(the achievement token should mint against real quest completions —
Proposal 1's fixed generation layer — not stub/placeholder ones).

**Scoping decision this change rests on, surfaced explicitly rather
than re-litigated per-message**: "learn-to-earn... elaborate
cryptocurrency features" is implemented here as a capped,
non-transferable, badge-gated achievement token — not as a
resurrection of the orphaned stablecoin/staking/lending/DEX/
prediction-market track. This reading was established across two
rounds of the operator's own direction plus `CredAnchor.sol`'s
pre-existing "Educational, NOT financial" framing; it is flagged here
as the explicit fork in the road rather than assumed silently, so a
correction is cheap if this reading is wrong — no code in this change
implements a spendable or tradeable balance.

`Affected repos: cianfhoghlaim (single repo)`

## Impact

- Capabilities: MODIFIED `cianfhoghlaim-educational-mmo` (the "Hybrid
  x402 educational credential" requirement — fixes the badge-issuance
  and anchor-scheduling paths it already specifies); NEW
  `learn-to-earn-token-credential` (the achievement-token contract).
- Code: 8× `agents/tuatha/tools/*_response_score.py`,
  `tuatha/badges/{anchor,ledger,README}.{py,md}`,
  `tuatha/contracts/cred_anchor.py`, new
  `tuatha/contracts/{AchievementToken.sol,achievement_token.py}`, new
  `tuatha/badges/achievement_token_client.py`, new
  `orchestration/defs/5_agent_ops/credential_assets.py`,
  `agents/api/routes/routes/payments.py`, new
  `web/apps/cianfhoghlaim-mmo/convex/x402Payments.ts`,
  `web/apps/cianfhoghlaim-mmo/convex/schema.ts`.
