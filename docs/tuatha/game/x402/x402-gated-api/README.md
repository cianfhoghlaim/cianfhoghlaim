# x402 - Payment Gated API Demo

A Next.js application demonstrating a payment-gated API using the x402 protocol.

General flow:
- User connects their wallet
- User requests backend API
- API responds with 402 response code
- User is prompted to sign an authorization
- Server uses thirdweb x402 facilitator to verify and settle payment on abstract testnet
- API returns premium content if payment is successful (HTTP 200)

## Setup

## Installation

1. Clone the repository:
```bash
git clone https://github.com/jarrodwatts/x402-gated-api.git
cd x402-gated-api
```

2. Install dependencies:
```bash
pnpm install
```

3. Configure environment variables:

Copy [env.example](env.example) to `.env.local`:
```bash
cp env.example .env.local
```

Edit `.env.local` and add your credentials:
```env
NEXT_PUBLIC_THIRDWEB_CLIENT_ID=your_client_id_here
THIRDWEB_SECRET_KEY=your_secret_key_here
SERVER_WALLET_ADDRESS=your_server_wallet_address_here
```

You can get these values from your [Thirdweb dashboard](https://thirdweb.com/dashboard).

**Important**: Ensure you fund the server wallet address with some ETH on the network of your choice.

4. Run the development server:
```bash
pnpm dev
```

5. Open [http://localhost:3000](http://localhost:3000) in your browser.

## How It Works

### Client Side ([app/page.tsx](app/page.tsx))

- Users connect their wallet using Thirdweb's `ConnectButton`
- The `wrapFetchWithPayment` function wraps standard fetch to automatically handle payment requests
- When accessing premium content, the client sends payment data with the request

### Server Side ([app/api/route.ts](app/api/route.ts))

- The API route receives requests with payment data in the `x-payment` header
- `settlePayment` validates and processes the payment on Abstract Testnet
- Returns premium content if payment is successful (HTTP 200)
- Returns payment request details if payment is required (HTTP 402)

## Project Structure

```
x402/
├── app/
│   ├── api/
│   │   └── route.ts        # Payment-gated API endpoint
│   ├── layout.tsx          # Root layout
│   ├── page.tsx            # Main page with wallet connection
│   └── globals.css         # Global styles
├── components/
│   └── ui/                 # shadcn/ui components
├── lib/
│   └── utils.ts            # Utility functions
└── env.example             # Environment variables template
```
