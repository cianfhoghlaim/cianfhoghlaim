# Key Files Reference for Crypteolas Integration

## Core x402 Implementation Files

### x402 TypeScript Packages
```
/Users/cliste/dev/bonneagar/hackathon/examples/crypto/hackathon/x402/typescript/
├── packages/
│   ├── core/src/types/
│   │   ├── payments.ts                    # Core payment types
│   │   └── shared/                        # Shared interfaces
│   ├── mechanisms/
│   │   ├── evm/src/exact/
│   │   │   ├── client/index.ts            # EVM client-side payment creation
│   │   │   ├── server/index.ts            # EVM server-side verification
│   │   │   ├── server/scheme.ts           # EVM payment scheme logic
│   │   │   └── facilitator/index.ts       # EVM payment settlement
│   │   └── svm/src/exact/
│   │       ├── client/index.ts            # Solana client-side signing
│   │       ├── server/index.ts            # Solana verification
│   │       └── facilitator/index.ts       # Solana settlement
│   ├── http/                              # HTTP transport implementation
│   ├── extensions/                        # Payment extensions
│   └── legacy/                            # Previous SDK versions
├── specs/
│   ├── x402-specification-v1.md           # Main protocol specification
│   ├── schemes/exact/
│   │   ├── scheme_exact_evm.md            # EVM exact payment scheme
│   │   ├── scheme_exact_svm.md            # Solana exact payment scheme
│   │   └── scheme_exact.md                # General scheme specification
│   ├── transports-v2/
│   │   ├── http.md                        # HTTP transport spec
│   │   ├── mcp.md                         # MCP transport spec
│   │   └── a2a.md                         # Agent-to-agent transport
│   └── README.md                          # Specs overview
└── README.md                              # x402 main documentation
```

---

## React Component Implementation

### x402-solana-react Package
```
/Users/cliste/dev/bonneagar/hackathon/examples/crypto/hackathon/x402-solana-react/
├── src/
│   ├── hooks/
│   │   └── useX402Payment.ts              # Main payment hook (CRITICAL)
│   ├── components/
│   │   ├── X402Paywall.tsx                # Main paywall component (CRITICAL)
│   │   ├── PaymentButton.tsx              # Payment button
│   │   ├── PaymentStatus.tsx              # Status display
│   │   └── WalletSection.tsx              # Wallet connection UI
│   ├── types/
│   │   ├── paywall.ts                     # Component prop types (CRITICAL)
│   │   ├── index.ts                       # Type exports
│   │   └── theme.ts                       # Theme definitions
│   ├── lib/
│   │   ├── balance.ts                     # USDC balance fetching
│   │   └── utils.ts                       # Utility functions
│   └── index.ts                           # Package exports
├── package.json                           # Dependencies (CRITICAL)
├── README.md                              # Usage documentation
└── examples/
    ├── basic-usage.tsx                    # Basic implementation example
    └── custom-styling.tsx                 # Advanced styling example
```

---

## MCPay Implementation

### MCPay SDK
```
/Users/cliste/dev/bonneagar/hackathon/examples/crypto/hackathon/MCPay/
├── packages/js-sdk/
│   ├── src/
│   │   ├── handler/
│   │   │   ├── proxy/
│   │   │   │   ├── index.ts               # Proxy handler
│   │   │   │   └── hooks/
│   │   │   │       ├── x402-hook.ts       # Payment handling hook
│   │   │   │       ├── auth-headers-hook.ts
│   │   │   │       ├── logging-hook.ts
│   │   │   │       └── analytics-hook.ts
│   │   │   └── mcp/
│   │   │       └── createMcpPaidHandler.ts # MCP server creation
│   │   ├── client/
│   │   │   └── withX402Client.ts          # Client payment wrapper
│   │   ├── types/
│   │   │   ├── payments.ts
│   │   │   └── networks.ts
│   │   └── index.ts
│   ├── README.md                          # SDK documentation (CRITICAL)
│   └── package.json
├── apps/
│   ├── mcp/                               # MCP server example
│   │   ├── src/lib/auth.ts                # Auth implementation
│   │   ├── auth-schema.ts                 # Auth schema
│   │   └── README.md
│   └── mcp-data/
│       ├── src/db/schema.ts               # Database schema (CRITICAL)
│       └── README.md
├── examples/
│   ├── x402-mcp/
│   │   └── example/client.ts              # MCP client example (CRITICAL)
│   ├── auth-example/
│   │   └── auth-client.ts                 # Auth integration example
│   └── chatgpt-apps-sdk-nextjs-starter/   # Next.js integration
└── README.md                              # MCPay main docs (CRITICAL)
```

---

## Reference Implementations

### x402 Starter Kit (Production Template)
```
/Users/cliste/dev/bonneagar/hackathon/examples/crypto/hackathon/x402-starter-kit/
├── src/
│   ├── index.ts                           # Main server entry
│   ├── server.ts                          # Express setup
│   ├── services/
│   │   ├── exampleService.ts              # Business logic
│   │   └── merchantExecutor.ts            # Facilitator integration
│   ├── middleware/
│   │   ├── paymentMiddleware.ts           # Payment verification
│   │   └── errorHandler.ts
│   └── routes/
│       └── paidEndpoint.ts                # Protected endpoint
├── .env.example                           # Configuration template (CRITICAL)
├── package.json
├── README.md                              # Setup instructions (CRITICAL)
└── DEPLOYING_TO_TEE.md                    # Deployment guide
```

### x402 Echo Merchant (Demo/Test Server)
```
/Users/cliste/dev/bonneagar/hackathon/examples/crypto/hackathon/x402-echo-merchant/
├── src/
│   ├── app/
│   │   ├── api/
│   │   │   ├── solana/paid-content/route.ts           # Solana endpoint (CRITICAL)
│   │   │   ├── solana-devnet/paid-content/route.ts   # Solana devnet
│   │   │   ├── base/paid-content/route.ts            # Base mainnet
│   │   │   ├── base-sepolia/paid-content/route.ts    # Base testnet
│   │   │   ├── polygon/paid-content/route.ts         # Polygon
│   │   │   ├── avalanche/paid-content/route.ts       # Avalanche
│   │   │   ├── xlayer/paid-content/route.ts
│   │   │   └── facilitator/verify/route.test.ts      # Verification tests
│   │   └── page.tsx                                   # Home page
│   ├── middleware.ts                                  # x402 middleware setup (CRITICAL)
│   ├── refund.ts                                      # Refund logic
│   ├── lib/
│   │   └── utils.ts                                   # Rizzler UI utilities
│   └── components/                                    # UI components
├── .env.example                                       # Configuration (CRITICAL)
├── package.json
├── README.md                                          # Usage guide (CRITICAL)
└── next.config.ts
```

### x402 AI Inference (Pay-Per-Token)
```
/Users/cliste/dev/bonneagar/hackathon/examples/crypto/hackathon/x402-ai-inference/
├── app/
│   ├── api/
│   │   └── chat/route.ts                  # Chat endpoint with token metering (CRITICAL)
│   ├── components/
│   │   ├── messages.tsx                   # Token cost display (CRITICAL)
│   │   └── chat.tsx
│   └── layout.tsx
├── lib/
│   ├── constants.ts                       # Pricing configuration (CRITICAL)
│   └── openai.ts                          # AI provider integration
├── .env.example                           # Configuration
├── package.json
├── README.md                              # Documentation (CRITICAL)
└── public/
```

### x402 Gated API (Thirdweb Integration)
```
/Users/cliste/dev/bonneagar/hackathon/examples/crypto/hackathon/x402-gated-api/
├── app/
│   ├── api/
│   │   └── route.ts                       # Payment implementation (CRITICAL)
│   ├── page.tsx
│   └── layout.tsx
├── components/
│   └── ui/
│       └── button.tsx
├── lib/utils.ts
├── package.json
├── .env.example
└── README.md
```

---

## Agent Payments Protocol (AP2)

### AP2 Main Implementation
```
/Users/cliste/dev/bonneagar/hackathon/examples/crypto/hackathon/AP2/
├── samples/
│   ├── python/
│   │   ├── src/roles/
│   │   │   ├── shopping_agent/
│   │   │   │   ├── agent.py               # Main shopping agent
│   │   │   │   ├── tools.py               # Agent tools
│   │   │   │   └── remote_agents.py       # Sub-agent management
│   │   │   ├── merchant_payment_processor_agent/
│   │   │   │   ├── agent_executor.py      # Payment processing
│   │   │   │   ├── agent.json             # Agent configuration
│   │   │   │   └── tools.py               # Payment tools
│   │   │   └── [other agent roles]/
│   │   └── scenarios/
│   │       ├── a2a/human-present/
│   │       │   ├── x402/                  # x402 payment scenario (CRITICAL)
│   │       │   ├── cards/                 # Card payment scenario
│   │       │   └── README.md
│   │       └── shopping_agent/
│   ├── README.md                          # AP2 Python setup
│   └── requirements.txt
├── samples/go/                            # Go implementation
│   ├── pkg/roles/
│   └── README.md
├── samples/android/                       # Android app implementation
│   └── scenarios/
│       └── digital-payment-credentials/
├── README.md                              # AP2 main documentation (CRITICAL)
└── src/ap2/types/                         # Protocol type definitions
```

### Bindu (Database/Agent State Management)
```
/Users/cliste/dev/bonneagar/hackathon/examples/crypto/hackathon/Bindu/
├── bindu/
│   ├── server/
│   │   ├── storage/
│   │   │   ├── schema.py                  # Database schema (CRITICAL)
│   │   │   └── db.py
│   │   ├── middleware/
│   │   │   ├── auth/
│   │   │   │   └── auth0.py               # Auth0 integration
│   │   │   └── payment/
│   │   ├── api/
│   │   │   └── routes.py
│   │   └── main.py
│   ├── utils/
│   │   ├── auth_utils.py                  # Authentication utilities
│   │   └── payment_utils.py
│   └── common/
│       └── protocol/types.py              # Protocol type definitions
├── alembic/
│   └── versions/
│       └── 20251207_0001_initial_schema.py # Database migrations
├── requirements.txt
├── README.md
└── .env.example
```

---

## Authentication & Frontend Examples

### Auth Implementation
```
/Users/cliste/dev/bonneagar/hackathon/examples/crypto/hackathon/
├── frontend/
│   ├── cryptodashe/
│   │   ├── api/src/
│   │   │   ├── middleware/
│   │   │   │   └── authMiddleware.ts      # JWT middleware
│   │   │   ├── controllers/
│   │   │   │   └── authController.ts      # Auth handlers (CRITICAL)
│   │   │   └── routes/
│   │   │       └── auth.ts                # Auth routes (CRITICAL)
│   │   └── README.md
│   ├── ant-design-web3/
│   │   ├── packages/
│   │   │   ├── wagmi/src/
│   │   │   │   ├── wallets/               # EVM wallet implementations
│   │   │   │   │   ├── coinbase-wallet.tsx
│   │   │   │   │   ├── universal-wallet.tsx
│   │   │   │   │   └── types.ts
│   │   │   │   └── wagmi-provider/
│   │   │   ├── solana/src/
│   │   │   │   ├── wallets/types.ts       # Solana wallet types
│   │   │   │   └── solana-provider/
│   │   │   ├── sui/src/
│   │   │   └── bitcoin/src/
│   │   └── README.md
│   ├── web3uikit/
│   │   ├── packages/core/src/
│   │   │   └── lib/Illustrations/         # Web3 UI components
│   │   └── README.md
│   └── cryptocurrency-dashboard/          # Crypto dashboard example
├── MCPay/examples/
│   ├── auth-example/
│   │   └── auth-client.ts                 # MCPay auth integration
│   └── chatgpt-apps-sdk-nextjs-starter/   # Next.js starter
```

---

## Documentation Files

### Specifications & Guides
```
/Users/cliste/dev/bonneagar/hackathon/examples/crypto/hackathon/
├── Comparing the Top 6 Agent-Native Rails...md        # Protocol comparison
├── Cronos x402 Paytech Hackathon...md                 # Hackathon info
├── Getting Started _ Crypto.com MCP Server.md         # MCP guide
├── All Dev Tools & Integrations _ Cronos EVM Docs.md # EVM tools
├── TanStack DB Integration...md                       # DB integration
├── Sign In With Ethereum (SIWE)...md                  # SIWE authentication
├── Overview _ TanStack AI Docs.md                     # AI integration
├── Hacker's Getting Started Resources...md            # Dev resources
├── x402/
│   ├── README.md                          # x402 main docs
│   ├── ROADMAP.md
│   ├── PROJECT-IDEAS.md
│   └── specs/README.md
├── MCPay/README.md                        # MCPay docs
├── AP2/README.md                          # AP2 protocol docs
├── x402-solana-react/README.md           # Component library docs
├── x402-starter-kit/README.md            # Starter kit setup
├── x402-echo-merchant/README.md          # Demo server setup
└── x402-ai-inference/README.md           # AI inference example
```

---

## Configuration Files

### Environment Templates
```
/Users/cliste/dev/bonneagar/hackathon/examples/crypto/hackathon/
├── x402-starter-kit/.env.example              # Express server config
├── x402-echo-merchant/.env.example            # Demo server config
├── x402-ai-inference/.env.example             # AI inference config
├── x402-gated-api/.env.example                # Thirdweb integration config
├── MCPay/apps/mcp/.env.example               # MCP server config
├── Bindu/.env.example                         # Agent state management config
└── frontend/cryptodashe/.env.example          # Dashboard config
```

### Package Configuration
```
/Users/cliste/dev/bonneagar/hackathon/examples/crypto/hackathon/
├── x402/typescript/
│   ├── package.json                        # Monorepo root
│   ├── pnpm-workspace.yaml
│   ├── turbo.json
│   └── tsconfig.base.json
├── x402-solana-react/
│   ├── package.json                        # React component package
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── tailwind.config.js
├── MCPay/
│   ├── package.json                        # MCPay monorepo
│   ├── pnpm-workspace.yaml
│   └── turbo.json
└── AP2/
    ├── package.json                        # AP2 Python
    └── pyproject.toml
```

---

## Critical Files for Quick Integration

### ABSOLUTE MUST-READ (in order):
1. **x402-solana-react/src/hooks/useX402Payment.ts** - Payment hook logic
2. **x402-solana-react/src/types/paywall.ts** - Component interfaces
3. **x402-solana-react/package.json** - Dependencies
4. **x402-starter-kit/README.md** - Server setup guide
5. **MCPay/README.md** - Payment infrastructure
6. **MCPay/apps/mcp-data/src/db/schema.ts** - Database design

### ESSENTIAL EXAMPLES:
1. **x402-echo-merchant/src/app/api/solana/paid-content/route.ts** - Payment endpoint
2. **x402-echo-merchant/src/middleware.ts** - Middleware setup
3. **x402-starter-kit/src/services/merchantExecutor.ts** - Facilitator integration
4. **MCPay/examples/x402-mcp/example/client.ts** - MCP client integration
5. **x402-ai-inference/app/api/chat/route.ts** - Pay-per-token implementation

### REFERENCE SPECIFICATIONS:
1. **x402/specs/x402-specification-v1.md** - Protocol spec
2. **x402/specs/schemes/exact/scheme_exact_evm.md** - EVM scheme
3. **x402/specs/schemes/exact/scheme_exact_svm.md** - Solana scheme
4. **AP2/README.md** - Agent payments protocol

---

## File Organization Summary

```
Crypto Hackathon Root
├── x402/                              # Core protocol implementation
│   ├── typescript/                    # Main SDKs and packages
│   └── specs/                         # Protocol specifications
├── x402-solana-react/                 # React paywall component (CRITICAL)
├── x402-starter-kit/                  # Production server template
├── x402-echo-merchant/                # Demo/test server
├── x402-ai-inference/                 # Pay-per-token example
├── x402-gated-api/                    # Thirdweb integration example
├── x402-rs/                           # Rust implementation
├── MCPay/                             # MCP payment infrastructure (CRITICAL)
├── AP2/                               # Agent payments protocol
├── Bindu/                             # Agent state management
├── a2a-x402/                          # Agent-to-agent payments
├── frontend/                          # Web3 UI components & dashboards
│   ├── ant-design-web3/               # Multi-chain UI library
│   ├── cryptodashe/                   # Crypto dashboard
│   └── [other dashboards]/
└── startup-idea-agent/                # Startup idea generation agent
```

---

## How to Use This Reference

1. **For understanding x402 protocol**: Start with `x402/specs/x402-specification-v1.md`
2. **For React integration**: Read `x402-solana-react/README.md` + look at `useX402Payment.ts`
3. **For server setup**: Follow `x402-starter-kit/README.md` + `x402-echo-merchant/`
4. **For MCP integration**: Study `MCPay/README.md` + `MCPay/examples/x402-mcp/`
5. **For database design**: Copy `MCPay/apps/mcp-data/src/db/schema.ts` pattern
6. **For authentication**: Reference `frontend/cryptodashe/api/src/routes/auth.ts`
7. **For pay-per-token**: Follow `x402-ai-inference/app/api/chat/route.ts` pattern
8. **For agent payments**: Study `AP2/samples/python/` + `Bindu/`

