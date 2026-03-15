# Crypteolas Demo

A DeFi analytics platform with AI-powered research assistant, pay-per-use API access via x402, and Web3 authentication.

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | TanStack Start, React 19, TailwindCSS |
| **Auth** | Better Auth with SIWE (Sign In With Ethereum) |
| **Database** | PostgreSQL + Drizzle ORM |
| **Payments** | x402 Protocol (Cronos/Base) |
| **AI Chat** | CopilotKit + LiteLLM |
| **State** | TanStack Query + Zustand |
| **Web3** | Wagmi + Viem |

## Prerequisites

- [Bun](https://bun.sh) v1.0+
- [Docker](https://docker.com) (for PostgreSQL and services)
- Node.js 20+ (for compatibility)

## Quick Start

```bash
# Install dependencies
bun install

# Copy environment file
cp .env.example .env
# Edit .env with your configuration

# Start PostgreSQL
docker compose up -d postgres

# Run database migrations
bun run db:push

# Start development server
bun run dev
```

The app will be available at `http://localhost:3000`

## Environment Setup

Copy `.env.example` to `.env` and configure:

### Required

```bash
# Database
DATABASE_URL="postgresql://crypteolas:crypteolas@localhost:5432/crypteolas"

# Auth secret (generate with: openssl rand -base64 32)
BETTER_AUTH_SECRET="your-secret-key"

# Payment recipient wallet
PAYMENT_RECIPIENT="0xYourWalletAddress"
```

### Optional (for full functionality)

```bash
# LLM (for AI chat)
OPENAI_API_KEY="sk-..."
# or use LiteLLM proxy
LITELLM_BASE_URL="http://localhost:4000"

# WalletConnect (for wallet connection)
NEXT_PUBLIC_WALLETCONNECT_PROJECT_ID="your-project-id"
```

## Scripts

```bash
bun run dev        # Start development server
bun run build      # Build for production
bun run start      # Start production server
bun run typecheck  # Run TypeScript checks
bun run lint       # Run ESLint

# Database
bun run db:generate  # Generate migrations
bun run db:push      # Push schema to database
bun run db:migrate   # Run migrations
bun run db:studio    # Open Drizzle Studio
```

## Docker Services

Start all services:

```bash
docker compose up -d
```

Individual services:

```bash
docker compose up -d postgres   # PostgreSQL database
docker compose up -d litellm    # LLM proxy
docker compose up -d redis      # Cache (optional)
docker compose up -d agno       # Agent backend
```

## Project Structure

```
src/
├── db/
│   ├── schema.ts        # Drizzle schema (auth, payments, usage)
│   └── index.ts         # Database client
├── lib/
│   ├── auth/
│   │   ├── server.ts    # Better Auth config with SIWE
│   │   └── client.ts    # Auth client hooks
│   ├── x402/
│   │   ├── middleware.ts    # Payment middleware
│   │   ├── payment-service.ts  # DB operations
│   │   ├── pricing.ts       # Feature pricing
│   │   └── networks.ts      # Chain configs
│   ├── copilot/
│   │   └── runtime.ts   # CopilotKit setup
│   ├── query/
│   │   ├── client.ts    # TanStack Query config
│   │   └── hooks.ts     # Data fetching hooks
│   └── mcp/
│       └── copilot-actions.ts  # AI tool definitions
├── routes/
│   ├── __root.tsx       # Root layout
│   ├── index.tsx        # Dashboard
│   ├── chat.tsx         # AI chat interface
│   ├── analytics.tsx    # Analytics page
│   ├── portfolio.tsx    # Portfolio tracker
│   ├── knowledge.tsx    # Knowledge graph explorer
│   └── api/
│       ├── auth.$.ts    # Auth API routes
│       ├── copilot.ts   # AI chat endpoint
│       ├── graph.ts     # Knowledge graph API
│       └── analytics/   # Analytics endpoints
├── components/          # UI components
└── stores/             # Zustand stores
```

## Features

### Web3 Authentication
- Sign In With Ethereum (SIWE)
- Multi-chain support (Ethereum, Cronos, Base, Polygon)
- ENS name/avatar resolution
- Optional GitHub OAuth fallback

### x402 Payments
- Pay-per-use API access
- Free tier with daily limits
- USDC payments on Cronos/Base
- Usage tracking and analytics

### AI Research Assistant
- Crypto-specific knowledge
- Real-time price data
- Protocol analysis
- Yield strategy recommendations
- Risk assessments

### Data Sources
- CoinGecko / Crypto.com prices
- DeFiLlama TVL data
- Knowledge graph (protocols, audits, risks)

## API Endpoints

| Endpoint | Description | Payment |
|----------|-------------|---------|
| `POST /api/copilot` | AI chat | 5 free/day, then $0.01 |
| `GET /api/tokens` | Token prices | Free |
| `GET /api/protocols` | Protocol data | Free |
| `GET /api/analytics/yield` | Yield strategies | 3 free/day, then $0.05 |
| `GET /api/analytics/risk` | Risk analysis | 3 free/day, then $0.05 |
| `GET /api/graph` | Knowledge search | 3 free/day, then $0.02 |

## Database Schema

Core tables managed by Drizzle:

- **user, session, account, verification** - Better Auth
- **payment** - x402 payment tracking
- **usageRecord, usageQuota** - Usage metering
- **conversation, message** - Chat history
- **priceCache, protocolCache** - Data caching

Run migrations:

```bash
bun run db:push
```

View/edit data:

```bash
bun run db:studio
```

## Development

### Adding a new API endpoint

```typescript
// src/routes/api/my-endpoint.ts
import { createAPIFileRoute } from "@tanstack/start/api";
import { withPayment } from "../../lib/x402/middleware";

export const Route = createAPIFileRoute("/api/my-endpoint")({
  GET: withPayment({
    featureId: "my_feature",
    description: "My feature description",
  }, async (request, paymentInfo) => {
    // Your logic here
    return Response.json({ data: "..." });
  }),
});
```

### Adding a TanStack Query hook

```typescript
// src/lib/query/hooks.ts
export function useMyData() {
  return useQuery({
    queryKey: ["myData"],
    queryFn: async () => {
      const res = await fetch("/api/my-endpoint");
      return res.json();
    },
  });
}
```

## License

MIT
