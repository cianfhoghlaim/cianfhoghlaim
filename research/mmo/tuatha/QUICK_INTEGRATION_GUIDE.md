# Quick Integration Guide for Crypteolas

## 1. Minimal x402 Payment Server Setup (5 minutes)

### Install Dependencies
```bash
npm install @x402/core @x402/evm @x402/svm @x402/express @x402/axios
```

### Express Server Implementation
```typescript
import express from 'express';
import { paymentMiddleware } from '@x402/express';

const app = express();

// Setup payment middleware
app.use(
  paymentMiddleware({
    "GET /api/premium-data": {
      accepts: [
        { network: 'solana', scheme: 'exact' },
        { network: 'base', scheme: 'exact' }
      ],
      description: "Access premium data",
      price: {
        amount: "1000000", // 1 USDC in atomic units
        asset: "USDC"
      }
    }
  })
);

// Protected endpoint
app.get('/api/premium-data', (req, res) => {
  res.json({ data: "sensitive information" });
});

app.listen(3000);
```

---

## 2. React Component Integration (5 minutes)

### Install Paywall Component
```bash
npm install @payai/x402-solana-react @solana/wallet-adapter-react @solana/wallet-adapter-wallets
```

### Usage
```tsx
import { X402Paywall } from '@payai/x402-solana-react';
import '@payai/x402-solana-react/styles';

export function PremiumContent() {
  return (
    <X402Paywall
      amount={0.01}
      description="Premium Content Access"
      network="solana"
      theme="dark"
      onPaymentSuccess={(txId) => {
        console.log('Payment successful:', txId);
      }}
    >
      <div>Your exclusive content here!</div>
    </X402Paywall>
  );
}
```

---

## 3. Database Schema (PostgreSQL + Drizzle)

```typescript
import { pgTable, text, uuid, jsonb, timestamp, bigint, index } from 'drizzle-orm/pg-core';

export const users = pgTable('users', {
  id: uuid('id').defaultRandom().primaryKey(),
  wallet_address: text('wallet_address').unique(),
  chain: text('chain').default('solana'),
  created_at: timestamp('created_at', { withTimezone: true }).defaultNow(),
});

export const payments = pgTable('payments', {
  id: uuid('id').defaultRandom().primaryKey(),
  user_id: uuid('user_id').references(() => users.id),
  resource_path: text('resource_path').notNull(),
  amount: bigint('amount', { mode: 'bigint' }).notNull(),
  network: text('network').notNull(),
  tx_hash: text('tx_hash').unique(),
  status: text('status').default('pending'), // pending, settled, failed
  payment_data: jsonb('payment_data'),
  created_at: timestamp('created_at', { withTimezone: true }).defaultNow(),
  settled_at: timestamp('settled_at', { withTimezone: true }),
  index('idx_user_id', 'user_id'),
  index('idx_resource_path', 'resource_path'),
});
```

---

## 4. MCPay Server Setup (for MCP Tools)

```typescript
import { Hono } from "hono";
import { createMcpPaidHandler } from "mcpay/handler";
import { z } from "zod";

const handler = createMcpPaidHandler(
  (server) => {
    server.paidTool(
      "premium_analysis",
      "Advanced data analysis",
      "$0.001",
      { data: z.string() },
      {},
      async ({ data }) => ({
        content: [{
          type: "text",
          text: `Analysis: ${data}`
        }]
      })
    );
  },
  {
    facilitator: { url: "https://facilitator.mcpay.tech" },
    recipient: {
      "svm": { address: "YOUR_SOL_ADDRESS", isTestnet: true }
    }
  }
);

const app = new Hono();
app.use("*", (c) => handler(c.req.raw));
export default app;
```

---

## 5. Environment Variables

```env
# Server
PORT=3000
NODE_ENV=development

# Wallet Configuration
SOLANA_WALLET_ADDRESS=YourSolanaAddress
EVM_WALLET_ADDRESS=0x...

# x402 Facilitator
FACILITATOR_URL=https://facilitator.mcpay.tech
FACILITATOR_API_KEY=your_api_key_if_needed

# RPC Endpoints
SOLANA_RPC_URL=https://api.devnet.solana.com
BASE_RPC_URL=https://base-sepolia.g.alchemy.com/v2/YOUR_KEY

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/crypteolas

# Private Key (for refunds/direct settlement)
SOLANA_PRIVATE_KEY=your_base58_encoded_key
EVM_PRIVATE_KEY=0x...
```

---

## 6. Testing Payment Flow

### Step 1: Create Payment Request
```bash
curl -X POST http://localhost:3000/api/premium-data
# Returns: 402 Payment Required
# Header: PAYMENT-REQUIRED: {base64 encoded payment requirements}
```

### Step 2: Sign with Wallet & Retry
```typescript
const x402Client = createX402Client({
  wallet: walletAdapter,
  network: 'solana-devnet'
});

const response = await x402Client.fetch(
  'http://localhost:3000/api/premium-data',
  { method: 'POST' }
);

const paymentResponse = response.headers.get('x-payment-response');
// Extract transaction ID from payment response
```

---

## 7. Common Integration Patterns

### Pattern 1: Gated API Endpoint
```typescript
import { paymentMiddleware } from '@x402/express';

app.use(paymentMiddleware({
  "GET /api/data": {
    accepts: [{ network: 'solana', scheme: 'exact' }],
    description: "API Data Access",
    price: { amount: "1000000", asset: "USDC" }
  }
}));

app.get('/api/data', (req, res) => {
  // Only reaches here after payment is verified
  res.json({ success: true });
});
```

### Pattern 2: Per-Token Charging
```typescript
const PRICE_PER_TOKEN = BigInt(1); // 1 wei per token

app.post('/api/chat', async (req, res) => {
  const { message } = req.body;
  
  // Stream AI response
  const stream = await model.stream(message);
  let tokenCount = 0;
  
  stream.on('token', () => tokenCount++);
  
  stream.on('end', async () => {
    const totalPrice = PRICE_PER_TOKEN * BigInt(tokenCount);
    
    // Settle payment asynchronously
    await facilitator.settle({
      amount: totalPrice.toString(),
      // ... other params
    });
  });
});
```

### Pattern 3: Subscription with Crypto
```typescript
// Store subscription status in database
const user = await db.users.findOne({ wallet_address });
const subscription = await db.subscriptions.findOne({ user_id: user.id });

if (!subscription || subscription.expires_at < new Date()) {
  // Return 402 - payment required
  return res.status(402).json({
    error: "subscription_required"
  });
}

// User has active subscription
res.json({ data: "premium content" });
```

---

## 8. Multi-Chain Setup

```typescript
const x402Config = {
  networks: {
    solana: {
      rpcUrl: process.env.SOLANA_RPC_URL,
      facilitator: process.env.SOLANA_FACILITATOR
    },
    base: {
      rpcUrl: process.env.BASE_RPC_URL,
      facilitator: process.env.BASE_FACILITATOR
    },
    polygon: {
      rpcUrl: process.env.POLYGON_RPC_URL,
      facilitator: process.env.POLYGON_FACILITATOR
    }
  }
};

app.use(paymentMiddleware({
  "GET /api/premium": {
    accepts: [
      { network: 'solana', scheme: 'exact' },
      { network: 'base', scheme: 'exact' },
      { network: 'polygon', scheme: 'exact' }
    ],
    description: "Multi-chain premium access",
    price: { amount: "1000000", asset: "USDC" }
  }
}));
```

---

## 9. Error Handling

```typescript
try {
  const response = await x402Client.fetch(endpoint, {
    method: 'POST',
    body: JSON.stringify(data)
  });

  if (response.status === 402) {
    // Payment required - extract requirements
    const requirements = JSON.parse(
      atob(response.headers.get('payment-required'))
    );
    // Show payment UI
  } else if (response.ok) {
    // Payment successful
    const txId = response.headers.get('x-payment-response');
    // Process success
  }
} catch (error) {
  if (error.message.includes('insufficient_balance')) {
    // Show "insufficient USDC" error
  } else if (error.message.includes('signature_invalid')) {
    // Show "invalid signature" error
  }
}
```

---

## 10. Testing with Echo Merchant

Use the free test server for development:

```bash
# Solana Devnet
npx x402 create-client \
  --url https://x402.payai.network/api/solana-devnet/paid-content \
  --amount 0.01 \
  --network solana-devnet \
  --wallet-address YOUR_SOL_ADDRESS

# Base Sepolia
npx x402 create-client \
  --url https://x402.payai.network/api/base-sepolia/paid-content \
  --amount 10000 \
  --network base-sepolia \
  --wallet-address YOUR_ETH_ADDRESS
```

The Echo Merchant will refund all test payments automatically.

---

## 11. Deployment Checklist

- [ ] Set all environment variables in production
- [ ] Use mainnet RPC endpoints (not testnet)
- [ ] Set production wallet addresses
- [ ] Enable HTTPS
- [ ] Configure CORS properly
- [ ] Implement rate limiting
- [ ] Set up error logging
- [ ] Test full payment flow
- [ ] Implement analytics/logging
- [ ] Set up monitoring/alerts
- [ ] Document API for users
- [ ] Create user-facing payment instructions

---

## 12. Useful Commands

```bash
# Start x402 listener for testing
npx x402 listen --port 3000

# Create test payment signature
npx x402 sign \
  --message "test" \
  --private-key YOUR_KEY \
  --network solana

# Verify payment signature
npx x402 verify \
  --signature SIGNATURE \
  --public-key PUBLIC_KEY

# Check facilitator status
curl https://facilitator.mcpay.tech/health

# Get token price (USDC in atomic units)
# 1 USDC = 1,000,000 atomic units
# 0.01 USDC = 10,000 atomic units
```

---

## 13. Quick Troubleshooting

| Issue | Solution |
|-------|----------|
| "Wallet not connected" | Ensure wallet extension is installed and unlocked |
| "Insufficient USDC" | Send USDC to wallet (use faucet for testnet) |
| "RPC rate limit" | Use custom RPC endpoint from Alchemy/QuickNode/Helius |
| "402 response not caught" | Check middleware is registered before routes |
| "Payment never settles" | Verify facilitator URL and API key |
| "Wrong network" | Check wallet network matches server network |
| "Signature invalid" | Ensure wallet hasn't changed, clear cache |

---

## 14. Additional Resources

- x402 Specification: `/x402/specs/x402-specification-v1.md`
- MCPay Docs: `MCPay/README.md`
- API Examples: `/x402-starter-kit/`
- React Components: `/x402-solana-react/README.md`
- Echo Merchant (Testing): https://x402.payai.network/

---

## 15. Support & Community

- x402 GitHub: https://github.com/coinbase/x402
- MCPay: https://mcpay.tech
- PayAI Network: https://payai.network
- Solana Developers: https://solana.com/developers
- Base Blockchain: https://base.org

