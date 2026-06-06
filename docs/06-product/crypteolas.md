---
domain: product
title: Crypteolas — Crypto & Web3
description: Consolidated x402 micopayment protocol, SIWE authentication, tokenomics, Web3, NFT, DAO, Learn-to-Earn model, and crypto agent architecture for the Celtic educational ecosystem.
supersedes:
  - docs/tuatha/CRYPTEOLAS_INTEGRATION_GUIDE.md
  - docs/tuatha/CRYPTO_INTEGRATION_SUMMARY.md
  - docs/tuatha/CRYPTO_INTEGRATION_SUMMARY.md
  - docs/tuatha/Crypto Analysis AI Agent System Architecture.md
  - docs/tuatha/Comparing the Top 6 Agent-Native Rails for the Agentic Internet_ MCP, A2A, AP2, ACP, x402, and Kite.md
  - docs/tuatha/x402-payments.md
  - docs/tuatha/PAYMENT_GUIDE.md
  - docs/tuatha/tokenomics-README.md
  - docs/tuatha/learn-to-earn-model.md
  - docs/tuatha/Learn-to-Earn Blockchain and AI.md
  - docs/tuatha/ERC-4361_ Sign-In with Ethereum.md
  - docs/tuatha/Sign In With Ethereum (SIWE) _ Better Auth.md
  - docs/tuatha/game_siwe-auth.md
  - docs/tuatha/repo-x402.md
  - docs/tuatha/Crypteolas_ Federated Learning & Crypto Payments.md
  - docs/tuatha/Web3 Classroom Response System Design.md
  - docs/tuatha/Web3 Gamified Education & Asset Generation.md
  - docs/tuatha/federated-marketplace.md
  - docs/tuatha/Federated AI Marketplace on iPhone.md
cognee_entities:
  - entity: x402Protocol
    type: PaymentProtocol
    relationships:
      - revives: HTTP402
      - uses: EIP712
      - uses: EIP2612
      - settles_on: Base
      - settles_on: Arbitrum
  - entity: TuathToken
    type: UtilityToken
    relationships:
      - standard: ERC20
      - standard: ERC2612
      - powers: LearnToEarn
  - entity: SIWE
    type: AuthStandard
    relationships:
      - standard: ERC4361
      - integrates_with: BetterAuth
ccc_query_hints:
  - "x402 HTTP 402 payment required"
  - "SIWE sign-in with ethereum"
  - "Learn-to-Earn tokenomics"
  - "crypto agent architecture"
  - "Tuath utility token"
updated: 2026-06-06
---

# Crypteolas — Crypto & Web3

Crypteolas (Irish: "crypto knowledge") is the Web3 layer of the Celtic educational ecosystem. It provides the payment infrastructure, tokenomics, identity, and agentic economy that powers the Learn-to-Earn model.

## 1. Architecture Overview

```
┌──────────────────────────────────────────────────────┐
│                Crypteolas Platform                    │
├───────────────────┬──────────────────┬───────────────┤
│  x402 Payments    │  SIWE Identity   │  Learn-to-Earn│
│  (HTTP 402)       │  (ERC-4361)      │  Tokenomics   │
├───────────────────┴──────────────────┴───────────────┤
│              Blockchain Settlement                   │
│        (Base / Arbitrum — EVM-compatible)            │
├──────────────────────────────────────────────────────┤
│             Tuath Utility Token                      │
│    (ERC-20 + EIP-2612 Permit + EIP-3009 Transfer)   │
└──────────────────────────────────────────────────────┘
```

## 2. x402 Payment Protocol

x402 revives the dormant HTTP 402 "Payment Required" status code, creating a universal standard for machine-to-machine and agent-to-agent micropayments without traditional payment infrastructure.

### The Payment Flow

```
   Client                API Server              Facilitator           Blockchain
     │                       │                       │                     │
     ├── GET /resource ──────▶                       │                     │
     │                       │                       │                     │
     │◄── 402 Payment Req ───┤                       │                     │
     │    {amount, address,  │                       │                     │
     │     network, expires} │                       │                     │
     │                       │                       │                     │
     ├── GET /resource ──────▶                       │                     │
     │   X-Payment: <sig>    │                       │                     │
     │                       ├── Verify Payment ────▶│                     │
     │                       │                       ├── Submit TX ───────▶
     │                       │                       │◄── TX Hash ────────┤
     │                       │◄── Confirmation ──────┤                     │
     │                       │                       │                     │
     │◄── 200 OK + Resource ─┤                       │                     │
```

### Protocol Steps

1. **Resource Request**: Client requests a protected resource
2. **402 Challenge**: Server returns `402 Payment Required` with payment terms (amount, beneficiary address, network, expiration)
3. **Agentic Authorization**: Agent signs with EIP-712 (Typed Data Signing) or EIP-3009 (Transfer with Authorization)
4. **Header Injection**: Client retries with `X-PAYMENT` header containing signed authorization
5. **Facilitator Settlement**: Server forwards to Facilitator service, which verifies signature and submits transaction to blockchain, acting as gas paymaster
6. **Resource Delivery**: Server returns 200 OK with the content

### Server Implementation (Axum/Rust)

```rust
use axum::{
    extract::{Request, State},
    http::{HeaderMap, StatusCode},
    middleware::Next,
    response::Response,
};

pub async fn x402_middleware(
    State(state): State<AppState>,
    req: Request,
    next: Next,
) -> Result<Response, StatusCode> {
    let payment_header = req.headers().get("X-PAYMENT");

    match payment_header {
        Some(signature) => {
            // Verify payment via Facilitator
            let verified = state.facilitator.verify_payment(&signature).await
                .map_err(|_| StatusCode::PAYMENT_REQUIRED)?;

            if verified.valid {
                Ok(next.run(req).await)
            } else {
                Err(StatusCode::PAYMENT_REQUIRED)
            }
        }
        None => {
            // Return 402 with payment terms
            let payment_terms = PaymentTerms {
                amount: "5".into(),
                currency: "KN",  // Knowledge Knots
                beneficiary: state.treasury_address.clone(),
                network: "eip155:8453".into(), // Base
                expires: now() + 300, // 5 minutes
            };
            Err(StatusCode::PAYMENT_REQUIRED)
        }
    }
}
```

### Use Cases in the Ecosystem

| Use Case | Example | Payment Unit |
|----------|---------|-------------|
| **AI Inference** | Pay per token/request for AI tutor | 0.001 USDC per session |
| **Content Access** | Unlock premium mythology chapters | 5 KN per chapter |
| **Agent-to-Agent** | AI agents paying for data services | Micro USDC |
| **Game Items** | Purchase cosmetic items without app store fees | 10-100 KN |
| **Curriculum Nodes** | Access advanced learning modules | Variable KN based on difficulty |
| **Streaming Content** | Pay-as-you-go for video/audio lessons | Per-second micropayments |

### Multi-Language Support

| Language | Package | Integration |
|----------|---------|-------------|
| **TypeScript** | `x402` | Express, Hono, Next.js middleware |
| **Rust** | `x402-rs` | Axum middleware |
| **Go** | `x402-go` | Facilitator and server |
| **Python** | `x402-python` | FastAPI, Flask |
| **A2A** | `a2a-x402` | Agent-to-Agent payments |

## 3. Tuath Utility Token

The **Tuath** token (representing "tribe" or "people") functions as a utility token rather than a speculative asset. Its design discourages hoarding and incentivizes participation.

### Technical Standards

| Standard | Purpose |
|----------|---------|
| **ERC-20** | Base fungible token standard |
| **ERC-2612 (Permit)** | Gasless approvals via signatures — enables meta-transactions |
| **EIP-3009** | Transfer with Authorization — user signs a message, Facilitator pays gas |
| **EIP-712** | Typed Data Signing — structured, human-readable messages for signing |

### Token Design Principles

1. **Not speculative**: Tuath is a "knowledge energy" measurement, not a tradeable asset
2. **Gasless UX**: Players don't need ETH for gas — they sign intents, Facilitator pays
3. **Soul-bound elements**: Some achievements are non-transferable reputation markers
4. **Learn-to-Earn**: Tokens are earned through demonstrated competence, not grinding
5. **Spend-to-Learn**: Tokens unlock premium content, funding content creators

### Settlement

| Parameter | Value |
|-----------|-------|
| **Networks** | Base (primary), Arbitrum (fallback) |
| **Facilitator** | Self-hosted Rust/Go service |
| **Treasury** | Multi-sig DAO wallet |
| **Gas Strategy** | Facilitator as Paymaster, ERC-4337 compatible |

## 4. SIWE: Sign-In with Ethereum

### ERC-4361 Standard

Sign-In with Ethereum enables wallet-based authentication where users prove ownership of an Ethereum address by signing a structured message.

### Integration with BetterAuth

```typescript
import { betterAuth } from "better-auth"
import { siwe } from "better-auth/plugins"

export const auth = betterAuth({
  database: drizzleAdapter(db, { provider: "pg", schema }),
  plugins: [
    siwe({
      // Siwe-specific configuration
    })
  ],
  socialProviders: {
    github: { clientId: "...", clientSecret: "..." },
    google: { clientId: "...", clientSecret: "..." },
  },
})
```

### Client Flow

```typescript
import { signIn } from "~/lib/auth-client"

// SIWE sign-in
await signIn.social({
  provider: "siwe",
  callbackURL: "/dashboard",
})

// Standard OAuth
await signIn.social({ provider: "github" })
```

### Agentic Authorization

The combination of SIWE + x402 enables autonomous agents to:
1. Authenticate via SIWE (prove identity)
2. Pay via x402 (prove willingness)
3. Access resources as a fully autonomous entity

## 5. Learn-to-Earn Model

The Learn-to-Earn economy replaces speculative Play-to-Earn models with a knowledge-based reward system.

### Core Principles

| Principle | Implementation |
|-----------|----------------|
| **Proof of Knowledge** | Tokens awarded for verified learning outcomes |
| **Proof of Teaching** | Content creators earn when their materials are consumed |
| **Proof of Curation** | Reviewers earn for quality assessment |
| **Anti-grinding** | Diminishing returns on repeated easy content |

### Earning Mechanisms

| Activity | Reward | Verification |
|----------|--------|-------------|
| **Complete quiz with >80%** | 5 KN | On-chain quiz result hash |
| **Complete quest chain** | 50 KN | SpacetimeDB state proof |
| **Help another player** | 2 KN | Anam Cara bond activity |
| **Contribute content** | 100 KN + streaming royalties | DAO approval |
| **Review content** | 10 KN | Reviewer consensus |

### Spending Mechanisms

| Activity | Cost | Beneficiary |
|----------|------|-------------|
| **Premium zone unlock** | 100 KN | Content creator (80%) + DAO (20%) |
| **AI tutor session** | 1 KN/min | AI infrastructure costs |
| **Cosmetic items** | 10-500 KN | Artist + DAO |
| **Private chat channel** | 50 KN/month | Server costs |

## 6. Web3 Gamified Education

### Classroom Response System

A blockchain-verified classroom response system:
- Students answer questions on-chain (zk-proofs for privacy)
- Answers verified without revealing individual responses
- Aggregate statistics available to teachers
- Token rewards for participation and correct answers

### NFT Achievement System

- **Dynamic Cúchulainn Avatars**: NFTs that evolve based on player progress
- **Artifact Collection**: Unique items found through exploration
- **Achievement Badges**: Non-transferable soul-bound tokens
- **Celtic Art**: AI-generated art in La Tène, Ogham, and illumination styles

## 7. Crypto Agent System

### Architecture

```typescript
// src/store/crypto-store.ts
import { create } from 'zustand'

interface Portfolio {
  assets: {
    symbol: string
    amount: number
    entryPrice: number
    currentPrice: number
  }[]
  totalValue: number
}

interface MarketData {
  [symbol: string]: {
    price: number
    change24h: number
    volume24h: number
    lastUpdated: number
  }
}

const useCryptoStore = create<CryptoStore>((set) => ({
  portfolio: { assets: [], totalValue: 0 },
  marketData: {},
  updatePrice: (symbol, data) =>
    set((state) => ({
      marketData: { ...state.marketData, [symbol]: data }
    })),
}))
```

### Agent Capabilities
- **Portfolio Analysis**: AI-driven insights into token holdings
- **Market Monitoring**: Real-time price/volatility tracking
- **Risk Assessment**: Portfolio risk analysis and rebalancing suggestions
- **Trade Execution**: AI-suggested trades with user confirmation via CopilotKit

## 8. Federated AI Marketplace

A decentralized marketplace for AI model training using federated learning:

- **iPhone as Edge Node**: Apple Silicon optimized models (MLX, Core ML)
- **Privacy-Preserving**: Data stays on-device; only gradients shared
- **Swarm Learning**: Syft + Flower federated learning framework
- **Token Rewards**: Contributors earn Tuath for providing compute and data
- **Model Registry**: MLflow for experiment tracking, Langfuse for observability

## 9. Agent-Native Protocol Comparison

| Protocol | Purpose | Status in Stack |
|----------|---------|-----------------|
| **MCP** | Model Context Protocol — AI↔Tool communication | Used for curriculum and mythology tools |
| **A2A** | Agent-to-Agent — inter-agent communication | Future for multi-agent coordination |
| **x402** | HTTP 402 — agentic payments | Core payment rail |
| **AG-UI** | Agent User Interaction — streaming UI | CopilotKit implementation |
| **ACP** | Agent Communication Protocol | Evaluated, not adopted |
| **Kite** | Agent connectivity framework | Evaluated, not adopted |
