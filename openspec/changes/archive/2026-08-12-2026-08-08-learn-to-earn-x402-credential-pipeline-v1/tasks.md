# Tasks — Learn-to-earn x402 credential pipeline

## Phase 1 — Fix the dead badge trigger — DONE

- [x] 1.1 Fixed `from cianfhoghlaim.badges import issue_badge` →
  `from cianfhoghlaim.tuatha.badges import issue_badge` across all 8
  `agents/tuatha/tools/*_response_score.py` files (`{appm,chem,hist,
  math}_response_score.py` + `{comp,engl,geog}_tools.py`).
- [x] 1.2 Fixed the identical wrong-path bug in
  `tuatha/badges/anchor.py`'s `_call_credanchor_publish()`
  (`cianfhoghlaim.badges.anchor_contract` →
  `cianfhoghlaim.tuatha.badges.anchor_contract`).
- [x] 1.3 Fixed `tuatha/badges/README.md`'s own incorrect import
  example (both the prose line and the code sample).

## Phase 2 — Write + schedule `daily_credential_anchor` — DONE

- [x] 2.1 Wrote `orchestration/defs/5_agent_ops/credential_assets.py`
  — `daily_credential_anchor` asset (calls `fetch_badges_since` +
  `publish_anchor`), `daily_credential_anchor_job`
  (`define_asset_job`), `daily_credential_anchor_at_2am` schedule
  (`cron_schedule="0 2 * * *"`, matching `anchor.py`'s own documented
  intent). No `from __future__ import annotations` — that import
  breaks Dagster's `@asset` context-type-hint validation (confirmed
  against the working `heritage_assets.py` precedent, which omits it
  for the same reason).

## Phase 3 — Deploy `CredAnchor.sol` to Base Sepolia

- [ ] 3.1 **Blocked — real environmental reason, not fabricable.**
  Deployment requires `CIANFHOGHLAIM_BASE_L2_RPC_URL` (a real Base
  Sepolia RPC endpoint) and `CIANFHOGHLAIM_DEPLOYER_PRIVATE_KEY` (a
  funded testnet wallet's private key). Neither exists in this
  environment. `tuatha/contracts/cred_anchor.py`'s
  `compile_contract()`/`deploy_to_base_l2()` were verified compilable
  (see Phase 5) but not run against a live RPC.
- [x] 3.2 Fixed a real, separate bug found while verifying this path:
  `cred_anchor.py`'s `CONTRACT_SOURCE_PATH` pointed at
  `infrastructure/contracts/CredAnchor.sol` via `parents[3]` — a path
  that has never existed in this repo. `CredAnchor.sol` is actually
  this module's own sibling file. Fixed to
  `Path(__file__).resolve().parent / "CredAnchor.sol"`. This means
  `compile_contract()`/`deploy_to_base_l2()` could never have worked
  before this fix, regardless of Phase 3.1's credential blocker.

## Phase 4 — Harden x402 payment persistence — DONE

- [x] 4.1 Added `_ConvexPaymentStore` to
  `agents/api/routes/routes/payments.py` (`create`/`get`/
  `mark_verified`/`mark_failed`), backed by a new Convex
  `x402Payments` table, with transparent fallback to the (now
  fallback-only) in-memory dicts on `ImportError` — mirrors
  `tuatha/badges/ledger.py`'s existing graceful-degradation pattern.
- [x] 4.2 Migrated every route handler that touched the raw dicts
  directly: `request_payment`, `verify_payment`, `get_payment_status`,
  `create_402_response`, `check_payment_or_free`. All 5 now go
  through `_ConvexPaymentStore`.
- [x] 4.3 `RECEIVER_ADDRESS` now reads
  `CIANFHOGHLAIM_X402_RECEIVER_ADDRESS` (falling back to the same
  placeholder value only when unset).
- [x] 4.4 New `web/apps/cianfhoghlaim-mmo/convex/x402Payments.ts` —
  `create`/`getByPaymentId`/`markVerified`/`markFailed`, field-for-
  field matched to what `_ConvexPaymentStore` actually calls.

## Phase 5 — Scoping confirmation gate

- [x] 5.1 **Resolved via the proposal.md Dependencies section**,
  rather than a blocking mid-session question: the operator's
  direction across two rounds plus `CredAnchor.sol`'s pre-existing
  "Educational, NOT financial" framing both point at a capped,
  non-transferable, badge-gated token — not the orphaned stablecoin/
  DeFi track. Surfaced explicitly in `proposal.md` so it's cheap to
  correct if wrong, rather than silently assumed.

## Phase 6 — Achievement-token contract + minter wiring — DONE

- [x] 6.1 Wrote `tuatha/contracts/AchievementToken.sol`: `name`/
  `symbol`/`decimals` read-only per ERC20 convention,
  `MAX_SUPPLY = 100_000_000`, `MINT_AMOUNT_PER_BADGE = 10`,
  `mint(student, evidenceHash)` gated `onlyMinter` and idempotent via
  a `mintedForEvidence` mapping, `transfer`/`transferFrom`/`approve`
  all `revert(...)`, `rotateMinter`/`rotateOwner`. Compiled
  successfully via `solcx` (solc 0.8.20). ASCII hyphens used in
  `revert()` string literals, not em-dashes — a Unicode em-dash inside
  a plain (non-`unicode"..."`) Solidity string literal fails
  compilation with "Invalid character in string."
- [x] 6.2 Wrote `tuatha/contracts/achievement_token.py` — mirrors
  `cred_anchor.py`'s structure: ABI constant, `load_contract_source`/
  `compile_contract`/`deploy_to_base_l2`/`mint_achievement`/
  `get_balance`.
- [x] 6.3 Wrote `tuatha/badges/achievement_token_client.py` — async
  `mint_for_badge()` bridging the sync `web3.py` mint call via
  `asyncio.to_thread`.
- [x] 6.4 Wired into `tuatha/badges/ledger.py::issue_badge()` as step
  6: fires only when `student_wallet_address` is supplied; wrapped in
  a bare `try/except` so a failed/skipped mint never blocks the
  off-chain badge, which remains the source of truth regardless.
- [x] 6.5 Added optional `walletAddress` to the Convex `students`
  table (`schema.ts`) — the field `issue_badge()` callers would read
  from before passing `student_wallet_address`; no caller populates it
  yet (no SIWE auth flow exists in this pass), so minting is
  universally skipped today, which is the documented, expected
  degraded state, not a bug.

## Phase 7 — Verification

- [x] 7.1 `AchievementToken.sol` compiles via `solcx` (solc 0.8.20).
- [x] 7.2 All 8 badge-import fixes verified via `grep` — zero
  remaining `from cianfhoghlaim.badges import` occurrences anywhere
  in the tree.
- [x] 7.3 `agents/api/routes/routes/payments.py` — syntax-checked
  (`ast.parse`); `grep` confirms every remaining direct
  `_payment_requests`/`_completed_payments` reference is inside
  `_ConvexPaymentStore` itself (the documented fallback path), not a
  route handler.
- [ ] 7.4 End-to-end (quest completion → badge → token-mint → daily
  anchor → public verification-page check) against Base Sepolia —
  blocked on Phase 3.1's RPC/wallet credentials.
- [x] 7.5 `openspec validate 2026-08-08-learn-to-earn-x402-credential-
  pipeline-v1 --strict`.
