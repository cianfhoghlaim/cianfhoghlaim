# Comprehensive Crypto & Payment Integration Summary for Crypteolas

## Executive Overview

The crypto hackathon directory contains multiple production-ready implementations and reference architectures for:
- **x402 Protocol**: Open standard for internet-native payments (crypto + fiat)
- **MCPay**: Payment infrastructure for MCP (Model Context Protocol) servers
- **AP2 Protocol**: Agent Payments Protocol for autonomous agent commerce
- **Web3 UI Components**: Wallet integration and crypto dashboard implementations
- **Payment Processing**: Multi-chain payment settlement and verification

---

## 1. X402 Payment Protocol Implementation

### Core Protocol Overview
**Location**: `/Users/cliste/dev/bonneagar/hackathon/examples/crypto/hackathon/x402/`

The x402 protocol is a standardized HTTP-based payment system supporting:
- **Multi-chain Support**: EVM (Ethereum, Base, Polygon, Avalanche), SVM (Solana), Sui
- **Token Agnostic**: USDC, stablecoins, native tokens
- **Payment Schemes**: Exact amount (primary), Upto amount (future)
- **Three Key Roles**:
  - **Client**: Initiates payment request
  - **Resource Server**: HTTP endpoint requiring payment
  - **Facilitator**: Verifies and settles payments

### Typical x402 Payment Flow

```
1. Client → Resource Server: Initial HTTP request
2. Resource Server → Client: 402 Payment Required + PaymentRequired header
3. Client → Client Wallet: Create payment payload (signs with wallet)
4. Client → Resource Server: Retry with PAYMENT-SIGNATURE header
5. Resource Server → Facilitator: Verify payment (POST /verify)
6. Facilitator → Blockchain: Execute payment if valid
7. Resource Server → Client: 200 OK + protected resource
```

### x402 TypeScript Packages Structure

```
x402/typescript/packages/
├── core/                    # Core x402 types and interfaces
├── mechanisms/
│   ├── evm/                # EVM implementation (Ethereum, Base, etc.)
│   │   └── src/exact/
│   │       ├── client/     # Client-side signing and payment creation
│   │       ├── server/     # Server-side verification
│   │       └── facilitator/# Payment settlement
│   └── svm/                # SVM implementation (Solana)
│       └── src/exact/
│           ├── client/     # Solana wallet integration
│           ├── server/     # Payment verification
│           └── facilitator/# On-chain settlement
├── extensions/             # Additional features
├── http/                   # HTTP transport layer
└── legacy/                 # Previous SDK versions
```

### Key Files for Integration

**Core Types** (`x402/typescript/packages/core/src/types/`):
- `payments.ts` - Payment data structures and enums
- Wallet interfaces and signing mechanisms
- Payment requirement and verification schemas

**Client Implementation** (`x402/typescript/packages/mechanisms/svm/src/exact/client/`):
- `index.ts` - Main client export
- `scheme.ts` - Solana-specific payment scheme implementation
- Creates signed payment payloads from wallet

**Server Implementation** (`x402/typescript/packages/mechanisms/evm/src/exact/server/`):
- `index.ts` - Server integration
- `scheme.ts` - EVM-specific verification logic
- `register.ts` - Middleware registration

**Facilitator** (`x402/typescript/packages/mechanisms/evm/src/exact/facilitator/`):
- Verifies payment signatures
- Executes on-chain transactions
- Returns settlement confirmation

---

## 2. React Paywall Component (x402-solana-react)

**Location**: `/Users/cliste/dev/bonneagar/hackathon/examples/crypto/hackathon/x402-solana-react/`

### Package Details
- **Name**: `@payai/x402-solana-react`
- **Version**: 1.0.6
- **Purpose**: Drop-in React components for Solana-based payments

### Core Components

#### Main Component: `X402Paywall`
```typescript
interface X402PaywallProps {
  // Payment Configuration
  amount: number;                    // Payment amount in USDC
  description: string;               // Payment description
  network?: 'solana' | 'solana-devnet';
  rpcUrl?: string;                   // Custom RPC endpoint
  apiEndpoint?: string;              // Custom API endpoint
  facilitatorUrl?: string;
  
  // Wallet Setup
  wallet?: WalletAdapter;            // Optional wallet
  autoSetupProviders?: boolean;      // Default: true
  
  // UI Configuration
  theme?: ThemePreset;               // light, dark, solana-light, solana-dark, seeker, terminal
  showBalance?: boolean;
  showNetworkInfo?: boolean;
  showPaymentDetails?: boolean;
  
  // Callbacks
  onPaymentSuccess?: (txId: string) => void;
  onPaymentError?: (error: Error) => void;
  onWalletConnect?: (publicKey: string) => void;
  
  // Content
  children: ReactNode;
}
```

#### Key Hook: `useX402Payment`
```typescript
interface PaymentConfig {
  wallet: WalletAdapter;
  network: SolanaNetwork;
  rpcUrl?: string;
  apiEndpoint?: string;
  facilitatorUrl?: string;
  maxPaymentAmount?: number;
}

const {
  pay,                  // (amount, description) => Promise<string>
  isLoading,
  status,               // 'idle' | 'connecting' | 'pending' | 'success' | 'error'
  error,
  transactionId,
  reset
} = useX402Payment(config);
```

### Implementation Details

**Wallet Integration**:
- Compatible with Phantom, Solflare, and Solana Wallet Adapter ecosystem
- Auto-configures providers if not already wrapped
- Manages wallet connection state

**Payment Flow** (from `src/hooks/useX402Payment.ts`):
1. Create x402 client with wallet and network config
2. Make initial fetch request (returns 402 with payment requirements)
3. Client automatically creates signed payment payload
4. Retry request with X-PAYMENT header
5. Merchant verifies, settles, and returns resource
6. Extract transaction ID from X-PAYMENT-RESPONSE header

**Default Endpoints**:
```typescript
// Mainnet
https://x402.payai.network/api/solana/paid-content

// Devnet
https://x402.payai.network/api/solana-devnet/paid-content
```

### Available Themes
- `light` - Clean light with gradients
- `dark` - Dark theme with pink/purple/blue
- `solana-light` - Official Solana light (default)
- `solana-dark` - Official Solana dark
- `seeker` - Emerald/teal gradient
- `seeker-2` - Enhanced with backdrop blur
- `terminal` - Retro green-on-black

### Peer Dependencies
```json
{
  "@solana/spl-token": "^0.4.0",
  "@solana/wallet-adapter-base": "^0.9.0",
  "@solana/wallet-adapter-react": "^0.15.0",
  "@solana/wallet-adapter-react-ui": "^0.9.0",
  "@solana/wallet-adapter-wallets": "^0.19.0",
  "@solana/web3.js": "^1.0.0",
  "react": "^18.0.0 || ^19.0.0",
  "react-dom": "^18.0.0 || ^19.0.0"
}
```

---

## 3. MCPay - Payment Infrastructure for MCP Servers

**Location**: `/Users/cliste/dev/bonneagar/hackathon/examples/crypto/hackathon/MCPay/`

### Overview
MCPay adds on-chain payment capabilities to Model Context Protocol (MCP) servers using x402. Enables:
- Pay-per-call model for MCP tools
- Automatic 402 handling
- Multi-chain payments (EVM + SVM)
- Agent-to-service micropayments

### Core Components

#### MCPay SDK
**Features**:
- Automatic `402 Payment Required` handling
- Works with plain HTTP and MCP servers
- Pluggable wallet/transport
- Support for: Base, Avalanche, IoTeX, Sei (EVM), Solana (SVM)

#### MCPay CLI
```bash
# Using API key
npx mcpay connect --urls https://mcpay.tech/v1/mcp/SERVER_ID --api-key mcpay_YOUR_API_KEY

# Using EVM wallet
npx mcpay connect --urls https://mcpay.tech/v1/mcp/SERVER_ID \
  --evm 0xYOUR_PRIVATE_KEY \
  --evm-network base-sepolia

# Using SVM wallet
npx mcpay connect --urls https://mcpay.tech/v1/mcp/SERVER_ID \
  --svm YOUR_SECRET_KEY \
  --svm-network solana-devnet
```

### Programmatic Integration

#### MCP Client with Payments
```typescript
import { Client } from '@modelcontextprotocol/sdk/client/index.js'
import { StreamableHTTPClientTransport } from '@modelcontextprotocol/sdk/client/streamableHttp.js'
import { withX402Client } from 'mcpay/client'
import { createSigner } from 'x402/types'

// Create signer for network
const evmSigner = await createSigner('base-sepolia', process.env.EVM_PRIVATE_KEY!)
const url = new URL('https://mcpay.tech/v1/mcp/SERVER_ID')

// Create transport and client
const transport = new StreamableHTTPClientTransport(url)
const client = new Client({ name: 'my-client', version: '1.0.0' })
await client.connect(transport)

// Wrap with x402 payment capabilities
const paymentClient = withX402Client(client, {
  wallet: { evm: evmSigner },
  maxPaymentValue: BigInt(0.1 * 10 ** 6)  // 0.1 USDC max
})

const tools = await paymentClient.listTools()
```

#### Creating Paid MCP Server (Hono)
```typescript
import { Hono } from "hono"
import { createMcpPaidHandler } from "mcpay/handler"
import { z } from "zod"

const handler = createMcpPaidHandler(
  (server) => {
    // Paid tool with "$0.001" price
    server.paidTool(
      "weather",
      "Get weather data",
      "$0.001",
      { city: z.string() },
      {},
      async ({ city }) => ({
        content: [{
          type: "text",
          text: `The weather in ${city} is sunny`
        }]
      })
    )

    // Free tool
    server.tool(
      "free_tool",
      "Free to use",
      { city: z.string() },
      async ({ city }) => ({
        content: [{
          type: "text",
          text: `We support ${city}`
        }]
      })
    )
  },
  {
    facilitator: { url: "https://facilitator.mcpay.tech" },
    recipient: {
      "evm": { address: "0xYourAddress", isTestnet: true },
      "svm": { address: "YourSolanaAddress", isTestnet: true }
    }
  }
)

app.use("*", (c) => handler(c.req.raw))
export default app
```

### Database Schema (MCPay)
**File**: `MCPay/apps/mcp-data/src/db/schema.ts`

```typescript
// MCP Servers Table
export const mcpServers = pgTable('mcp_servers', {
  id: uuid('id').defaultRandom().primaryKey(),
  originRaw: text('origin_raw').notNull().unique(),  // Full URL
  origin: text('origin').notNull(),                   // Sanitized
  data: jsonb('data').$type<unknown>().default({}),  // Server metadata
  status: text('status'),
  moderationStatus: serverModerationStatus('moderation_status')
    .notNull()
    .default('pending'),
  moderationNotes: text('moderation_notes'),
  verifiedAt: timestamp('verified_at', { withTimezone: true }),
  qualityScore: integer('quality_score').notNull().default(0),
  lastSeenAt: timestamp('last_seen_at', { withTimezone: true }),
  createdAt: timestamp('created_at', { withTimezone: true }).defaultNow(),
  updatedAt: timestamp('updated_at', { withTimezone: true }).defaultNow(),
})

// RPC Logs Table
export const rpcLogs = pgTable('rpc_logs', {
  id: uuid('id').defaultRandom().primaryKey(),
  ts: timestamp('ts', { withTimezone: true }).defaultNow(),
  serverId: uuid('server_id').references(() => mcpServers.id),
  method: text('method'),
  request: jsonb('request').$type<unknown>().default({}),
  response: jsonb('response').$type<unknown>().default({}),
  meta: jsonb('meta').$type<unknown>().default({}),
})
```

---

## 4. Agent Payments Protocol (AP2)

**Location**: `/Users/cliste/dev/bonneagar/hackathon/examples/crypto/hackathon/AP2/`

### Overview
AP2 enables autonomous agent-to-service commerce with agent development kit (ADK) and Gemini 2.5 Flash.

### Architecture Components
- **Shopping Agent**: Main agent orchestrating purchases
- **Payment Method Collector**: Collects payment info from user
- **Shipping Address Collector**: Collects delivery address
- **Merchant Payment Processor Agent**: Processes payments
- **Credentials Provider Agent**: Manages payment credentials

### Sample Scenarios
```
samples/
├── python/scenarios/
│   ├── a2a/human-present/
│   │   ├── cards/        # Card payment scenario
│   │   └── x402/         # x402 payment scenario
│   └── shopping_agent/   # Main shopping workflow
└── android/scenarios/
    └── digital-payment-credentials/
```

### Database Schema (for AP2 - Bindu)
**File**: `Bindu/bindu/server/storage/schema.py`

```python
# Tasks Table (A2A protocol execution)
tasks_table = Table(
  "tasks",
  metadata,
  Column("id", PG_UUID(as_uuid=True), primary_key=True),
  Column("context_id", PG_UUID(as_uuid=True), ForeignKey("contexts.id")),
  Column("kind", String(50), default="task"),
  Column("state", String(50)),
  Column("state_timestamp", TIMESTAMP(timezone=True)),
  Column("history", JSONB, server_default="[]"),
  Column("artifacts", JSONB, server_default="[]"),
  Column("metadata", JSONB, server_default="{}"),
  Column("created_at", TIMESTAMP(timezone=True), server_default=func.now()),
  Column("updated_at", TIMESTAMP(timezone=True), server_default=func.now()),
  Index("idx_tasks_context_id", "context_id"),
  Index("idx_tasks_state", "state"),
  Index("idx_tasks_history_gin", "history", postgresql_using="gin"),
)

# Contexts Table (Conversation state)
contexts_table = Table(
  "contexts",
  metadata,
  Column("id", PG_UUID(as_uuid=True), primary_key=True),
  Column("context_data", JSONB, server_default="{}"),
  Column("message_history", JSONB, server_default="[]"),
  Column("created_at", TIMESTAMP(timezone=True), server_default=func.now()),
  Column("updated_at", TIMESTAMP(timezone=True), server_default=func.now()),
)

# Task Feedback Table
task_feedback_table = Table(
  "task_feedback",
  metadata,
  Column("id", Integer, primary_key=True, autoincrement=True),
  Column("task_id", PG_UUID(as_uuid=True), ForeignKey("tasks.id")),
  Column("feedback_data", JSONB),
  Column("created_at", TIMESTAMP(timezone=True), server_default=func.now()),
)
```

---

## 5. Reference Implementations

### 5.1 x402 Echo Merchant (Free Test Server)
**Location**: `/Users/cliste/dev/bonneagar/hackathon/examples/crypto/hackathon/x402-echo-merchant/`

**Features**:
- Demo payment server that refunds all payments
- Multi-chain support: Base, Solana, Polygon, Avalanche, xLayer, IoTeX
- Shows rizzler GIF reward after payment
- Perfect for testing x402 flow
- Live at: https://x402.payai.network/

**API Routes**:
```
GET  /api/base/paid-content
GET  /api/base-sepolia/paid-content
GET  /api/solana/paid-content
GET  /api/solana-devnet/paid-content
GET  /api/polygon/paid-content
GET  /api/avalanche/paid-content
GET  /api/xlayer/paid-content
GET  /api/xlayer-testnet/paid-content
```

**Payment Flow** (from `src/app/api/solana/paid-content/route.ts`):
```typescript
// Check for payment in headers
const paymentResponseHeader = request.headers.get('x-payment-response');

if (paymentResponseHeader) {
  // Payment verified, parse response
  const paymentInfo = JSON.parse(atob(paymentResponseHeader));
  
  // Render success page with:
  // - Transaction details
  // - Network info
  // - Payer address
  // - Refund transaction link
}

// No payment or verification failed - return 402 response
```

### 5.2 x402 Starter Kit (Production Ready)
**Location**: `/Users/cliste/dev/bonneagar/hackathon/examples/crypto/hackathon/x402-starter-kit/`

**Architecture**:
- Express HTTP server with x402 middleware
- ExampleService (customizable logic)
- MerchantExecutor (facilitator integration)
- Payment settlement and verification

**Configuration** (`.env`):
```env
PORT=3000

# Payment recipient
PAY_TO_ADDRESS=0xYourWalletAddress

# Network (base, base-sepolia, polygon, avalanche, solana, etc.)
NETWORK=base-sepolia

# AI Provider (if using AI services)
AI_PROVIDER=openai
OPENAI_API_KEY=your_key

# Facilitator
FACILITATOR_URL=https://x402.org/facilitator

# RPC Endpoints
BASE_RPC_URL=https://base-sepolia.g.alchemy.com/v2/your-key
SOLANA_RPC_URL=https://api.devnet.solana.com
```

### 5.3 x402 AI Inference (Pay-Per-Token)
**Location**: `/Users/cliste/dev/bonneagar/hackathon/examples/crypto/hackathon/x402-ai-inference/`

**Features**:
- Dynamic pricing based on actual tokens used
- Streams AI responses in real-time
- Asynchronous settlement (doesn't block response)
- Per-token cost display
- Uses Vercel AI SDK for token counting

**Pricing Configuration** (`lib/constants.ts`):
```typescript
export const PRICE_PER_INFERENCE_TOKEN_WEI = 1; // Wei per token
export const MAX_INFERENCE_TOKENS_PER_CALL = 1000000;
```

**Payment Flow**:
1. Client signs authorization with max amount
2. Server verifies signature before processing
3. Stream AI response to user (non-blocking)
4. Extract token usage from AI response
5. Calculate final price: `PRICE_PER_TOKEN × actualTokens`
6. Settle payment on-chain asynchronously

---

## 6. x402 Gated API (Thirdweb Integration)
**Location**: `/Users/cliste/dev/bonneagar/hackathon/examples/crypto/hackathon/x402-gated-api/`

**Tech Stack**:
- Next.js with App Router
- Thirdweb x402 SDK
- Abstract Testnet

**Implementation** (`app/api/route.ts`):
```typescript
import { settlePayment, facilitator } from "thirdweb/x402";
import { createThirdwebClient } from "thirdweb";

const client = createThirdwebClient({
  secretKey: process.env.THIRDWEB_SECRET_KEY!,
});

const thirdwebFacilitator = facilitator({
  client,
  serverWalletAddress: process.env.THIRDWEB_SERVER_WALLET_ADDRESS!,
});

export async function GET(request: Request) {
  const paymentData = request.headers.get("x-payment");

  // Verify and settle payment
  const result = await settlePayment({
    resourceUrl: "http://localhost:3000/api",
    method: "GET",
    paymentData,
    payTo: process.env.THIRDWEB_SERVER_WALLET_ADDRESS!,
    network: abstractTestnet,
    price: {
      amount: "10000",  // Price in atomic units
      asset: {
        address: "0xe4C7fBB0a626ed208021ccabA6Be1566905E2dFc", // USDC
      },
    },
    facilitator: thirdwebFacilitator,
  });

  if (result.status === 200) {
    return Response.json({ data: "premium content" });
  } else {
    return Response.json(result.responseBody, {
      status: result.status,
      headers: result.responseHeaders,
    });
  }
}
```

---

## 7. Authentication Patterns

### 7.1 Traditional Auth (Express)
**Location**: `frontend/cryptodashe/api/src/routes/auth.ts`

```typescript
router.post("/register", registerUser);
router.post("/login", loginUser);
router.get("/logout", logoutUser);
router.post("/reset-password", resetPassword);
router.post("/request-password-reset", requestPasswordReset);
router.post("/refresh-token", refreshToken);
router.get("/check-auth", checkAuth);
```

**Middleware** (`authMiddleware.ts`):
- JWT token validation
- User session management
- Permission checks

### 7.2 Crypto-Native Auth (SIWE)
**Reference**: `Sign In With Ethereum (SIWE) _ Better Auth.md`

Key concepts:
- Sign messages with crypto wallet instead of passwords
- Verify wallet ownership via signature
- Session management with signed messages
- No private keys shared with server

---

## 8. Wallet Integration Patterns

### Multi-Wallet Support
**Reference**: `frontend/ant-design-web3/packages/wagmi/src/wallets/`

Supported wallets:
- Phantom (Solana)
- MetaMask (EVM)
- Solflare (Solana)
- Coinbase Wallet (EVM)
- OKX Wallet
- Rainbow Wallet
- WalletConnect (Multi-chain)

### Solana Wallet Adapter
```typescript
import {
  ConnectionProvider,
  WalletProvider,
} from "@solana/wallet-adapter-react";
import { WalletModalProvider } from "@solana/wallet-adapter-react-ui";
import {
  PhantomWalletAdapter,
  SolflareWalletAdapter,
} from "@solana/wallet-adapter-wallets";

// Setup providers
const wallets = [
  new PhantomWalletAdapter(),
  new SolflareWalletAdapter(),
];

<ConnectionProvider endpoint={endpoint}>
  <WalletProvider wallets={wallets}>
    <WalletModalProvider>
      {/* Your app */}
    </WalletModalProvider>
  </WalletProvider>
</ConnectionProvider>
```

---

## 9. Supported Networks & Chains

### EVM Networks
- Base (mainnet & Sepolia testnet)
- Polygon (mainnet & Amoy testnet)
- Avalanche (mainnet & Fuji testnet)
- Ethereum (via Coinbase CDP)
- IoTeX
- Sei
- xLayer
- Peaq
- Abstract

### SVM Networks
- Solana (mainnet & devnet)

### Token Support
- USDC (primary)
- EUROe
- Native tokens
- Custom tokens (via configuration)

---

## 10. Integration Recommendations for Crypteolas

### Architecture Layers

#### 1. **Payment Layer**
```
Use: x402 Protocol + MCPay SDK
- Implement x402 server-side middleware
- Create payment requirement handlers
- Integrate with chosen facilitator (PayAI, Thirdweb, or custom)
- Support multiple networks via configuration
```

#### 2. **Frontend Layer**
```
Use: x402-solana-react component library
- Drop-in paywall components
- Auto-wallet setup
- Customizable themes
- Transaction tracking
Alternative: Build custom using x402 client SDK
```

#### 3. **Wallet Integration**
```
Use: Solana Wallet Adapter + EVM providers
- Phantom/Solflare for Solana
- MetaMask for EVM chains
- WalletConnect for cross-chain
- Session management with JWT/SIWE
```

#### 4. **Database Schema**
```
Use: PostgreSQL with Drizzle ORM
Tables to create:
- users (with wallet addresses)
- payment_transactions (x402 settlement records)
- payment_requirements (per resource/endpoint)
- usage_logs (for metering/analytics)
- subscriptions (if subscription model)
```

#### 5. **Server Implementation**
```
Framework: Express, Hono, or Next.js API routes
Pattern:
1. Authentication middleware (JWT or SIWE)
2. x402 payment middleware
3. Resource handler
4. Payment settlement handler
```

### Database Schema Template

```typescript
import { pgTable, text, uuid, jsonb, timestamp, integer, bigint, index } from 'drizzle-orm/pg-core';

// Users with wallet addresses
export const users = pgTable('users', {
  id: uuid('id').defaultRandom().primaryKey(),
  wallet_address: text('wallet_address').unique(),
  chain: text('chain').default('solana'), // 'solana', 'ethereum', 'polygon', etc.
  display_name: text('display_name'),
  metadata: jsonb('metadata').$type<Record<string, any>>().default({}),
  created_at: timestamp('created_at', { withTimezone: true }).defaultNow(),
  updated_at: timestamp('updated_at', { withTimezone: true }).defaultNow(),
});

// Payment requirements per resource
export const payment_requirements = pgTable('payment_requirements', {
  id: uuid('id').defaultRandom().primaryKey(),
  resource_path: text('resource_path').notNull(),
  price_amount: bigint('price_amount', { mode: 'bigint' }).notNull(), // In atomic units
  price_asset: text('price_asset').notNull(), // Token address or symbol
  network: text('network').notNull(), // 'solana', 'base', 'polygon', etc.
  description: text('description'),
  max_amount: bigint('max_amount', { mode: 'bigint' }), // Maximum client can be charged
  created_at: timestamp('created_at', { withTimezone: true }).defaultNow(),
  updated_at: timestamp('updated_at', { withTimezone: true }).defaultNow(),
});

// Completed transactions
export const payment_transactions = pgTable('payment_transactions', {
  id: uuid('id').defaultRandom().primaryKey(),
  user_id: uuid('user_id').references(() => users.id),
  resource_path: text('resource_path').notNull(),
  transaction_id: text('transaction_id').notNull().unique(), // On-chain tx hash
  amount: bigint('amount', { mode: 'bigint' }).notNull(),
  asset: text('asset').notNull(),
  network: text('network').notNull(),
  payer_address: text('payer_address').notNull(),
  recipient_address: text('recipient_address').notNull(),
  status: text('status').default('settled'), // 'pending', 'settled', 'failed'
  payment_payload: jsonb('payment_payload').$type<Record<string, any>>(),
  settlement_response: jsonb('settlement_response').$type<Record<string, any>>(),
  created_at: timestamp('created_at', { withTimezone: true }).defaultNow(),
  settled_at: timestamp('settled_at', { withTimezone: true }),
  index('idx_user_id', 'user_id'),
  index('idx_resource_path', 'resource_path'),
  index('idx_network', 'network'),
  index('idx_settled_at', 'settled_at'),
});

// Usage metrics for pay-per-use/token models
export const usage_logs = pgTable('usage_logs', {
  id: uuid('id').defaultRandom().primaryKey(),
  user_id: uuid('user_id').references(() => users.id),
  transaction_id: uuid('transaction_id').references(() => payment_transactions.id),
  resource_path: text('resource_path').notNull(),
  metric_type: text('metric_type').notNull(), // 'tokens', 'api_calls', 'compute_units', etc.
  metric_value: integer('metric_value').notNull(),
  calculated_cost: bigint('calculated_cost', { mode: 'bigint' }),
  created_at: timestamp('created_at', { withTimezone: true }).defaultNow(),
  index('idx_user_transaction', 'user_id', 'transaction_id'),
  index('idx_resource_metric', 'resource_path', 'metric_type'),
});
```

---

## 11. Key APIs & Functions to Implement

### Client-Side
```typescript
// From x402 client SDK
const x402Client = createX402Client({
  wallet: walletAdapter,
  network: 'solana-devnet',
  rpcUrl: customRpcUrl,
});

// Make authenticated request with auto-payment
const response = await x402Client.fetch(endpoint, {
  method: 'POST',
  body: JSON.stringify(payload),
});

// Extract payment response
const paymentResponse = response.headers.get('x-payment-response');
```

### Server-Side
```typescript
// Verify payment
const isValid = await facilitator.verify({
  paymentPayload: paymentData,
  paymentRequirements: requirements,
});

// Settle payment on-chain
const settlementResult = await facilitator.settle({
  paymentPayload: paymentData,
  paymentRequirements: requirements,
  amount: finalPrice,
});

// Create payment requirement header
const paymentRequired = base64Encode({
  price: { amount: '100000', asset: 'USDC' },
  description: 'Premium API Access',
  scheme: 'exact',
  network: 'solana',
  recipient: recipientAddress,
});
```

---

## 12. Environment Variables Template

```env
# Server Configuration
PORT=3000
NODE_ENV=development
LOG_LEVEL=info

# Payment Configuration
# Recipient wallet addresses
PAY_TO_ADDRESS_EVM=0x...
PAY_TO_ADDRESS_SVM=...

# Facilitator (choose one or multiple)
FACILITATOR_URL=https://facilitator.mcpay.tech
FACILITATOR_API_KEY=optional_api_key

# x402 Configuration
X402_MAX_PAYMENT_AMOUNT=1000000  # In atomic units
SETTLEMENT_MODE=facilitator      # or 'local' for direct settlement

# Thirdweb (if using Thirdweb facilitator)
THIRDWEB_SECRET_KEY=
THIRDWEB_CLIENT_ID=
THIRDWEB_SERVER_WALLET_ADDRESS=

# Network RPC Endpoints
SOLANA_RPC_URL=https://api.devnet.solana.com
SOLANA_DEVNET_RPC_URL=https://api.devnet.solana.com
BASE_RPC_URL=https://base-sepolia.g.alchemy.com/v2/YOUR_KEY
POLYGON_RPC_URL=https://polygon.g.alchemy.com/v2/YOUR_KEY
AVALANCHE_RPC_URL=https://avalanche-fuji.g.alchemy.com/v2/YOUR_KEY

# Local Settlement (if SETTLEMENT_MODE=local)
PRIVATE_KEY_EVM=0x...          # For EVM settlement
PRIVATE_KEY_SVM=...            # For Solana settlement

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/crypteolas

# JWT/Auth
JWT_SECRET=your_jwt_secret
SIWE_DOMAIN=crypteolas.com

# Optional: AI Provider (for AI inference pricing)
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
PRICE_PER_TOKEN_WEI=1

# UI Configuration
NEXT_PUBLIC_APP_URL=http://localhost:3000
NEXT_PUBLIC_SOLANA_RPC=https://api.devnet.solana.com
NEXT_PUBLIC_THIRDWEB_CLIENT_ID=
```

---

## 13. Testing Checklist

### Payment Flow Testing
- [ ] Create unsigned payment request (verify 402 response)
- [ ] Sign payment with wallet
- [ ] Submit signed payment
- [ ] Verify payment processing
- [ ] Confirm settlement on-chain
- [ ] Retrieve payment response headers
- [ ] Parse and validate payment confirmation

### Multi-Chain Testing
- [ ] Solana mainnet payment
- [ ] Solana devnet payment
- [ ] EVM (Base/Polygon) payment
- [ ] Cross-chain payment switching
- [ ] Network mismatch error handling

### Integration Testing
- [ ] Wallet connection
- [ ] Auto-payment flow
- [ ] Manual payment approval
- [ ] Payment cancellation
- [ ] Insufficient balance handling
- [ ] RPC endpoint fallbacks

---

## 14. Security Considerations

1. **Never log private keys** - Use environment variables
2. **Validate signatures server-side** - Don't trust client-side verification
3. **Set max payment amounts** - Prevent user overpayment
4. **Use HTTPS in production** - Payment headers contain sensitive data
5. **Implement rate limiting** - Prevent payment spam
6. **Audit facilitator** - Verify integration before production
7. **Test on testnet first** - Use devnet/Sepolia before mainnet
8. **Implement refund mechanisms** - For failed or unauthorized payments

---

## 15. Performance Optimization

### Caching
- Cache payment requirements (they rarely change)
- Store verified signatures temporarily
- Pre-compute common payment amounts

### Async Operations
- Settle payments asynchronously (don't block response)
- Queue facilitator calls during high load
- Implement retry logic with exponential backoff

### RPC Management
- Use custom RPC endpoints (avoid public rate limits)
- Implement connection pooling
- Fallback to alternative RPC providers

---

## Quick Reference: Useful File Paths

### Core Implementations
- `/Users/cliste/dev/bonneagar/hackathon/examples/crypto/hackathon/x402/typescript/` - x402 SDK
- `/Users/cliste/dev/bonneagar/hackathon/examples/crypto/hackathon/x402-solana-react/` - React Components
- `/Users/cliste/dev/bonneagar/hackathon/examples/crypto/hackathon/MCPay/packages/js-sdk/` - MCPay SDK

### Reference Implementations
- `/Users/cliste/dev/bonneagar/hackathon/examples/crypto/hackathon/x402-starter-kit/` - Production template
- `/Users/cliste/dev/bonneagar/hackathon/examples/crypto/hackathon/x402-echo-merchant/` - Demo server
- `/Users/cliste/dev/bonneagar/hackathon/examples/crypto/hackathon/x402-ai-inference/` - Pay-per-token example

### Specifications
- `/Users/cliste/dev/bonneagar/hackathon/examples/crypto/hackathon/x402/specs/` - x402 specification docs

---

## Summary: Integration Path for Crypteolas

1. **Start with x402 Starter Kit** as foundation
2. **Add x402-solana-react** for frontend paywall
3. **Choose facilitator**: PayAI (default), Thirdweb, or self-hosted
4. **Implement database schema** with payment tracking
5. **Add wallet integration** (Solana Adapter + MetaMask)
6. **Deploy to testnet** first (Solana Devnet, Base Sepolia)
7. **Test payment flows** thoroughly
8. **Move to mainnet** with production keys
9. **Implement analytics** for usage tracking
10. **Add refund mechanisms** if needed

This architecture provides a complete, production-ready payment system with multi-chain support and flexible pricing models.
