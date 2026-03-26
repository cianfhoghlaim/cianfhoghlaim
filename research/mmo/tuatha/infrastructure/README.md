# Infrastructure

This directory contains deployment and infrastructure research.

## Contents

- `scaffold-eth-setup.md` - SpeedRunEthereum development environment
- `hardhat-config.md` - Smart contract tooling
- `arbitrum-deployment.md` - L2 deployment strategy
- `spacetimedb-backend.md` - Real-time game state

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (TanStack Start)            │
├─────────────────────────────────────────────────────────┤
│                    SpacetimeDB (Game State)             │
├─────────────────────────────────────────────────────────┤
│  Dagster (Orchestration)  │  LiteLLM (Model Gateway)   │
├─────────────────────────────────────────────────────────┤
│  Arbitrum/Base (Contracts) │ IPFS/Arweave (NFT Data)   │
└─────────────────────────────────────────────────────────┘
```

## Networks

| Network | Chain ID | Purpose |
|---------|----------|---------|
| Arbitrum Sepolia | 421614 | Testnet deployment |
| Base Sepolia | 84532 | Alternative testnet |
| Arbitrum One | 42161 | Production |
| Base | 8453 | Production (x402) |

## Development Setup

### Prerequisites
- Foundry (forge, cast, anvil)
- Scaffold-ETH 2
- Bun / Node.js
- Docker (optional)

### Quick Start
```bash
# Install Foundry
curl -L https://foundry.paradigm.xyz | bash
foundryup

# Create Scaffold-ETH project
npx create-eth@latest anam-scaffold
cd anam-scaffold && bun install
```

## Self-Hosted Services

- **Komodo** - Container orchestration
- **Pangolin** - Zero-trust networking
- **Forgejo** - Git + package registry
- **LiteLLM** - LLM gateway
