# x402 — KCG Summary

## What It Is
x402 is an open protocol for micropayments over HTTP, enabling per-request cryptocurrency payments for API access. It allows AI agents and services to charge for usage at the individual request level using stablecoins and blockchain verification.

## Why This Matters for Kings' College Galway
The `tuatha/` educational MMO uses x402 for in-game microtransactions — students earn tokens by completing learning objectives and spend them on premium study assets, AI tutoring sessions, or cosmetic items. The protocol's low-fee model (using stablecoins on L2 networks) makes per-request billing viable for educational content where individual transactions may be fractions of a cent.

## Key Patterns
- HTTP 402 Payment Required with blockchain verification
- Stablecoin-based micropayments (USDC on Base/Arbitrum)
- SIWE (Sign-In With Ethereum) for wallet authentication
- MCPay integration for MCP server monetization

## Source Files
Full source code and TypeScript examples removed (2026-06-05). Available at <https://github.com/coinbase/x402>. Live implementation in `tuatha/apps/crypteolas_demo/`.
