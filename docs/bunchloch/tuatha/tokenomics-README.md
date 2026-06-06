# Tokenomics

This directory contains research and specifications for the Anam token economy.

## Contents

- `learn-to-earn-model.md` - Core L2E mechanics and reward distribution
- `x402-payments.md` - HTTP 402 payment protocol integration
- `hypercerts-rpgf.md` - Retrospective Public Goods Funding mechanisms
- `dual-token-architecture.md` - ERC20 (Tuath) + Dynamic NFT structure

## Key Concepts

### Tuath Token (ERC20)
- Utility token earned through learning activities ("Proof of Learn")
- Implements EIP-2612 (Permit) and EIP-3009 for gasless transactions
- Five elemental utilities: Spirit, Water, Fire, Earth, Air

### Pent-Elemental Token Utilities

| Element | Utility | Mechanism |
|---------|---------|-----------|
| **Spirit** | Currency/Mentorship | Soul Level reputation |
| **Water** | Liquidity | Cross-language trade pools |
| **Fire** | Burning | NFT crafting/minting |
| **Earth** | Staking | Land sovereignty claims |
| **Air** | Governance | DAO voting, gas fees |

### Economic Design Principles
1. **Circular Economy**: Tokens circulate rather than accumulate
2. **Proof of Learn**: Minting only through verified learning
3. **Sinks over Speculation**: Value from utility, not trading
