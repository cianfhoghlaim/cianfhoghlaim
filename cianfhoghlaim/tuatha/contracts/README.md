# CredAnchor.sol — Cianfhoghlaim Educational MMO Credential Anchor

The `CredAnchor` smart contract is the on-chain anchor for the
Cianfhoghlaim Educational MMO's hybrid x402 educational credential.

## What it does

Every UTC day at 02:00, the `daily_credential_anchor` Dagster asset
(`cianfhoghlaim/dagster/assets/credential_assets.py`):

1. Reads all new `SkillTreeBadge` records from Convex
2. Computes the Merkle root over the `evidence_hash` values
3. Publishes the root to `CredAnchor.publish(batchId, merkleRoot, leafCount)`
   on Base L2 via `cianfhoghlaim/badges/anchor.py`

The on-chain record is then queryable by any third party (employer,
university, parent) via the public `/anchor/<date>` page on the
TanStack Start 2D client
(`cianfhoghlaim/web/apps/cianfhoghlaim-mmo/src/routes/anchor/$date.tsx`).

## Deployment

**Network:** Base L2 (testnet for v1, mainnet when ready)

**Compiler:** `solc 0.8.20+`

**Deploy with Foundry:**

```bash
cd infrastructure/contracts
forge create --rpc-url $BASE_L2_RPC_URL \
              --private-key $DEPLOYER_PRIVATE_KEY \
              --broadcast \
              CredAnchor.sol:CredAnchor
```

After deployment, set the contract address in `dev-baile` Infisical:

```bash
# Add to .infisical.env template:
CIANFHOGHLAIM_CREDANCHOR_ADDRESS=0x...
```

The address is read by `cianfhoghlaim/badges/anchor.py:_call_credanchor_publish()`
on every daily Merkle anchor.

## Verification

Third-party verification (e.g. an employer checking a candidate's badge):

1. Navigate to `https://cianfhoghlaim-mmo.cianfhoghlaim.ie/anchor/2026-07-01`
2. Page reads `CredAnchor.getAnchor("2026-07-01")` → `(merkleRoot, timestamp, leafCount)`
3. Page accepts a `badge_id + evidence_hash` from the candidate
4. Page recomputes the Merkle path against `merkleRoot`
5. If the path matches, the badge is authentic

## Properties

| Property | Value |
|:--|:--|
| Storage cost | ~$0.50 per anchor (one string + bytes32 + uint256) |
| Gas per `publish()` | ~50,000 gas (Base L2 ≈ $0.01) |
| Annual cost | ~$3.65/year (1 anchor/day) |
| Reversibility | Owner can rotate (key rotation without redeploy) |
| Upgradability | Not upgradeable (intentional — anchor is immutable) |

## Educational, Not Financial

**Important:** The `CredAnchor` contract stores only Merkle roots and
batch metadata. No tokens are transferred, no value is held. The
educational credit tokens described in the proposal are issued by the
platform itself as quest-completion rewards; they are NOT financial
instruments. The on-chain anchor is a proof-of-existence mechanism,
not a payment rail.

The x402 protocol pays the gas for the `publish()` call from the
platform's treasury (Base L2 ≈ $0.01 per anchor).

## Reference

- `openspec/changes/cianfhoghlaim-educational-mmo-v1/proposal.md` (D4)
- `openspec/specs/cianfhoghlaim-educational-mmo/spec.md`
- `cianfhoghlaim/badges/anchor.py` — the publishing logic
- `cianfhoghlaim/badges/anchor_contract.py` — the Python ABI wrapper
- `cianfhoghlaim/badges/README.md` — design doc