# Payment Integration Guide

Guide to implementing x402 micropayments in the Tuath Celtic MMO.

## Overview

x402 is a protocol for HTTP micropayments using the 402 Payment Required status code. It enables:
- Pay-per-use API access
- Streaming payments for AI chat
- Premium content access
- Seamless blockchain integration

### Reference Materials

| Resource | Path |
|----------|------|
| x402 Library | `taighde/game/x402/` |
| Rust Implementation | `crates/x402/` |
| Axum Middleware | `crates/x402/crates/x402-axum/` |
| Client Library | `crates/x402/crates/x402-reqwest/` |

---

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Client    │────▶│  API (402)  │────▶│  Resource   │
│  (Wallet)   │◀────│  Gateway    │◀────│   Server    │
└─────────────┘     └─────────────┘     └─────────────┘
       │                   │
       │                   ▼
       │            ┌─────────────┐
       └───────────▶│ Blockchain  │
                    │ (Base/ETH)  │
                    └─────────────┘
```

### Payment Flow

1. Client requests protected resource
2. Server responds with `402 Payment Required`
3. Client constructs payment transaction
4. Client retries request with payment proof
5. Server verifies payment and returns resource

---

## Server Implementation

### Axum Middleware

```rust
// src/middleware/x402.rs

use axum::{
    extract::{Request, State},
    http::{HeaderMap, StatusCode},
    middleware::Next,
    response::{IntoResponse, Response},
    Json,
};
use x402_axum::{X402Config, PaymentVerifier, PaymentRequest};
use serde::{Deserialize, Serialize};

#[derive(Clone)]
pub struct PaymentConfig {
    pub receiver_address: String,
    pub chain_id: u64,
    pub supported_tokens: Vec<TokenConfig>,
}

#[derive(Clone)]
pub struct TokenConfig {
    pub symbol: String,
    pub address: String,
    pub decimals: u8,
}

#[derive(Serialize)]
pub struct PaymentRequiredResponse {
    pub error: String,
    pub resource_type: String,
    pub price_usd: f64,
    pub payment_options: Vec<PaymentOption>,
    pub request_url: String,
}

#[derive(Serialize)]
pub struct PaymentOption {
    pub token: String,
    pub amount: String,
    pub receiver: String,
    pub chain_id: u64,
}

pub async fn x402_middleware(
    State(config): State<PaymentConfig>,
    headers: HeaderMap,
    request: Request,
    next: Next,
) -> Response {
    // Check for payment header
    if let Some(payment_header) = headers.get("X-Payment") {
        // Verify payment
        match verify_payment(payment_header.to_str().unwrap_or(""), &config).await {
            Ok(verified) if verified => {
                // Payment valid, continue to handler
                return next.run(request).await;
            }
            Ok(_) => {
                return (
                    StatusCode::PAYMENT_REQUIRED,
                    Json(PaymentRequiredResponse {
                        error: "payment_invalid".to_string(),
                        resource_type: "unknown".to_string(),
                        price_usd: 0.0,
                        payment_options: vec![],
                        request_url: "/payments/request".to_string(),
                    }),
                ).into_response();
            }
            Err(e) => {
                return (
                    StatusCode::INTERNAL_SERVER_ERROR,
                    Json(serde_json::json!({ "error": e.to_string() })),
                ).into_response();
            }
        }
    }

    // No payment header - check if resource requires payment
    let response = next.run(request).await;

    // If handler returned 402, add payment details
    if response.status() == StatusCode::PAYMENT_REQUIRED {
        // Add payment headers
        let mut headers = HeaderMap::new();
        headers.insert("X-Payment-Required", "true".parse().unwrap());
        headers.insert("X-Payment-Address", config.receiver_address.parse().unwrap());

        // Return with payment options
        // (In practice, extract resource info from response)
    }

    response
}

async fn verify_payment(payment_data: &str, config: &PaymentConfig) -> Result<bool, String> {
    // Decode payment proof
    let payment: PaymentProof = serde_json::from_str(payment_data)
        .map_err(|e| format!("Invalid payment data: {}", e))?;

    // Verify on-chain
    let verifier = PaymentVerifier::new(config.chain_id);

    verifier.verify(
        &payment.tx_hash,
        &config.receiver_address,
        &payment.amount,
        &payment.token,
    ).await
}

#[derive(Deserialize)]
struct PaymentProof {
    tx_hash: String,
    amount: String,
    token: String,
    timestamp: u64,
}
```

### Resource Pricing

```rust
// src/pricing.rs

use std::collections::HashMap;

#[derive(Clone)]
pub struct PricingConfig {
    resources: HashMap<String, ResourcePrice>,
    free_daily_limits: HashMap<String, u32>,
}

#[derive(Clone)]
pub struct ResourcePrice {
    pub price_usd: f64,
    pub description: String,
}

impl PricingConfig {
    pub fn new() -> Self {
        let mut resources = HashMap::new();

        resources.insert("chat_message".to_string(), ResourcePrice {
            price_usd: 0.01,
            description: "AI chat message".to_string(),
        });

        resources.insert("knowledge_search".to_string(), ResourcePrice {
            price_usd: 0.02,
            description: "Knowledge base search".to_string(),
        });

        resources.insert("premium_quest".to_string(), ResourcePrice {
            price_usd: 0.05,
            description: "Premium quest access".to_string(),
        });

        resources.insert("extended_chat".to_string(), ResourcePrice {
            price_usd: 0.10,
            description: "Extended AI conversation (10 messages)".to_string(),
        });

        let mut free_limits = HashMap::new();
        free_limits.insert("chat_message".to_string(), 5);
        free_limits.insert("knowledge_search".to_string(), 3);
        free_limits.insert("premium_quest".to_string(), 0);

        Self {
            resources,
            free_daily_limits: free_limits,
        }
    }

    pub fn get_price(&self, resource_type: &str) -> Option<&ResourcePrice> {
        self.resources.get(resource_type)
    }

    pub fn get_free_limit(&self, resource_type: &str) -> u32 {
        self.free_daily_limits.get(resource_type).copied().unwrap_or(0)
    }

    pub fn convert_to_token(&self, usd_amount: f64, token: &str) -> String {
        // Get current token price from oracle
        let token_price = match token {
            "USDC" => 1.0,
            "ETH" => 2500.0,  // Would come from price feed
            _ => 1.0,
        };

        let amount = usd_amount / token_price;

        // Format to appropriate decimals
        match token {
            "USDC" => format!("{:.6}", amount),  // 6 decimals
            "ETH" => format!("{:.18}", amount),  // 18 decimals
            _ => format!("{:.6}", amount),
        }
    }
}
```

### Payment Routes

```rust
// src/routes/payments.rs

use axum::{
    extract::{Path, State},
    http::StatusCode,
    response::IntoResponse,
    routing::{get, post},
    Json, Router,
};
use serde::{Deserialize, Serialize};

pub fn payment_routes() -> Router<AppState> {
    Router::new()
        .route("/pricing", get(get_pricing))
        .route("/request/:resource_type", post(request_payment))
        .route("/verify", post(verify_payment))
}

#[derive(Serialize)]
struct PricingResponse {
    resources: Vec<ResourceInfo>,
    tokens: Vec<String>,
    chain: String,
}

#[derive(Serialize)]
struct ResourceInfo {
    resource_type: String,
    price_usd: f64,
    free_daily_limit: u32,
    description: String,
}

async fn get_pricing(
    State(state): State<AppState>,
) -> impl IntoResponse {
    let pricing = &state.pricing;

    let resources: Vec<ResourceInfo> = pricing.resources
        .iter()
        .map(|(k, v)| ResourceInfo {
            resource_type: k.clone(),
            price_usd: v.price_usd,
            free_daily_limit: pricing.get_free_limit(k),
            description: v.description.clone(),
        })
        .collect();

    Json(PricingResponse {
        resources,
        tokens: vec!["USDC".to_string(), "ETH".to_string()],
        chain: "base".to_string(),
    })
}

#[derive(Deserialize)]
struct PaymentRequestParams {
    token: Option<String>,
}

#[derive(Serialize)]
struct PaymentRequestResponse {
    payment_id: String,
    resource_type: String,
    price_usd: f64,
    price_crypto: String,
    token: String,
    receiver_address: String,
    chain_id: u64,
    expires_at: String,
}

async fn request_payment(
    State(state): State<AppState>,
    Path(resource_type): Path<String>,
    Json(params): Json<PaymentRequestParams>,
) -> Result<impl IntoResponse, (StatusCode, Json<serde_json::Value>)> {
    let pricing = &state.pricing;

    let resource = pricing.get_price(&resource_type)
        .ok_or((
            StatusCode::NOT_FOUND,
            Json(serde_json::json!({ "error": "Unknown resource type" })),
        ))?;

    let token = params.token.unwrap_or_else(|| "USDC".to_string());
    let price_crypto = pricing.convert_to_token(resource.price_usd, &token);

    // Generate payment ID
    let payment_id = format!("pay_{}", uuid::Uuid::new_v4());

    // Store payment request (expires in 15 minutes)
    state.payment_store.create_request(
        &payment_id,
        &resource_type,
        resource.price_usd,
        &token,
    ).await;

    Ok(Json(PaymentRequestResponse {
        payment_id,
        resource_type,
        price_usd: resource.price_usd,
        price_crypto,
        token,
        receiver_address: state.config.receiver_address.clone(),
        chain_id: state.config.chain_id,
        expires_at: chrono::Utc::now()
            .checked_add_signed(chrono::Duration::minutes(15))
            .unwrap()
            .to_rfc3339(),
    }))
}

#[derive(Deserialize)]
struct VerifyRequest {
    payment_id: String,
    tx_hash: String,
}

#[derive(Serialize)]
struct VerifyResponse {
    verified: bool,
    resource_type: String,
    access_token: Option<String>,
}

async fn verify_payment(
    State(state): State<AppState>,
    Json(request): Json<VerifyRequest>,
) -> Result<impl IntoResponse, (StatusCode, Json<serde_json::Value>)> {
    // Get stored payment request
    let payment_request = state.payment_store.get_request(&request.payment_id)
        .await
        .ok_or((
            StatusCode::NOT_FOUND,
            Json(serde_json::json!({ "error": "Payment request not found or expired" })),
        ))?;

    // Verify transaction on-chain
    let verified = state.verifier.verify_transaction(
        &request.tx_hash,
        &state.config.receiver_address,
        &payment_request.amount,
        &payment_request.token,
    ).await.map_err(|e| (
        StatusCode::INTERNAL_SERVER_ERROR,
        Json(serde_json::json!({ "error": e.to_string() })),
    ))?;

    if verified {
        // Generate access token for resource
        let access_token = state.token_service.create_access_token(
            &payment_request.resource_type,
            &request.payment_id,
        );

        // Mark payment as used
        state.payment_store.mark_used(&request.payment_id).await;

        Ok(Json(VerifyResponse {
            verified: true,
            resource_type: payment_request.resource_type,
            access_token: Some(access_token),
        }))
    } else {
        Ok(Json(VerifyResponse {
            verified: false,
            resource_type: payment_request.resource_type,
            access_token: None,
        }))
    }
}
```

---

## Client Implementation

### TypeScript Client

```typescript
// src/lib/x402-client.ts

import { ethers } from 'ethers';

interface PaymentConfig {
  apiBaseUrl: string;
  provider: ethers.providers.Web3Provider;
  signer: ethers.Signer;
}

interface PaymentRequest {
  paymentId: string;
  resourceType: string;
  priceUsd: number;
  priceCrypto: string;
  token: string;
  receiverAddress: string;
  chainId: number;
  expiresAt: string;
}

export class X402Client {
  private config: PaymentConfig;

  constructor(config: PaymentConfig) {
    this.config = config;
  }

  async fetchWithPayment<T>(
    url: string,
    options: RequestInit = {},
  ): Promise<T> {
    // First attempt without payment
    const response = await fetch(url, options);

    if (response.status !== 402) {
      return response.json();
    }

    // Payment required - get payment request
    const resourceType = response.headers.get('X-Resource-Type') || 'unknown';

    const paymentRequest = await this.requestPayment(resourceType);

    // Make payment
    const txHash = await this.makePayment(paymentRequest);

    // Verify payment
    const verification = await this.verifyPayment(
      paymentRequest.paymentId,
      txHash,
    );

    if (!verification.verified) {
      throw new Error('Payment verification failed');
    }

    // Retry with payment token
    const retryOptions = {
      ...options,
      headers: {
        ...options.headers,
        'X-Payment-Token': verification.accessToken,
      },
    };

    const retryResponse = await fetch(url, retryOptions);
    return retryResponse.json();
  }

  private async requestPayment(resourceType: string): Promise<PaymentRequest> {
    const response = await fetch(
      `${this.config.apiBaseUrl}/payments/request/${resourceType}`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token: 'USDC' }),
      },
    );

    return response.json();
  }

  private async makePayment(request: PaymentRequest): Promise<string> {
    // Get USDC contract
    const usdcAddress = '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913'; // Base USDC
    const usdcAbi = [
      'function transfer(address to, uint256 amount) returns (bool)',
    ];

    const usdc = new ethers.Contract(
      usdcAddress,
      usdcAbi,
      this.config.signer,
    );

    // Parse amount (USDC has 6 decimals)
    const amount = ethers.utils.parseUnits(request.priceCrypto, 6);

    // Send transaction
    const tx = await usdc.transfer(request.receiverAddress, amount);
    const receipt = await tx.wait();

    return receipt.transactionHash;
  }

  private async verifyPayment(
    paymentId: string,
    txHash: string,
  ): Promise<{ verified: boolean; accessToken: string }> {
    const response = await fetch(
      `${this.config.apiBaseUrl}/payments/verify`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ payment_id: paymentId, tx_hash: txHash }),
      },
    );

    return response.json();
  }
}
```

### React Hook

```typescript
// src/hooks/usePayment.ts

import { useState, useCallback } from 'react';
import { useAccount, useSigner } from 'wagmi';
import { X402Client } from '@/lib/x402-client';

interface UsePaymentOptions {
  apiBaseUrl: string;
}

export function usePayment({ apiBaseUrl }: UsePaymentOptions) {
  const { address } = useAccount();
  const { data: signer } = useSigner();

  const [isPaying, setIsPaying] = useState(false);
  const [lastPayment, setLastPayment] = useState<string | null>(null);

  const fetchWithPayment = useCallback(
    async <T>(url: string, options?: RequestInit): Promise<T> => {
      if (!signer) {
        throw new Error('Wallet not connected');
      }

      const client = new X402Client({
        apiBaseUrl,
        provider: signer.provider as any,
        signer,
      });

      setIsPaying(true);

      try {
        const result = await client.fetchWithPayment<T>(url, options);
        return result;
      } finally {
        setIsPaying(false);
      }
    },
    [apiBaseUrl, signer],
  );

  const checkFreeUsage = useCallback(
    async (resourceType: string): Promise<{ remaining: number; total: number }> => {
      const response = await fetch(
        `${apiBaseUrl}/auth/session`,
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('session_token')}`,
          },
        },
      );

      const session = await response.json();

      const key = `free_${resourceType}_remaining`;
      return {
        remaining: session[key] ?? 0,
        total: session[`free_${resourceType}_limit`] ?? 0,
      };
    },
    [apiBaseUrl],
  );

  return {
    fetchWithPayment,
    checkFreeUsage,
    isPaying,
    lastPayment,
    isConnected: !!address,
  };
}
```

### Paywall Component

```tsx
// src/components/X402Paywall.tsx

import React, { useState, useEffect } from 'react';
import { usePayment } from '@/hooks/usePayment';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';

interface X402PaywallProps {
  resourceType: string;
  onPaymentComplete: (accessToken: string) => void;
  children: React.ReactNode;
}

export function X402Paywall({
  resourceType,
  onPaymentComplete,
  children,
}: X402PaywallProps) {
  const { checkFreeUsage, isPaying, isConnected } = usePayment({
    apiBaseUrl: '/api',
  });

  const [freeRemaining, setFreeRemaining] = useState<number | null>(null);
  const [showPaywall, setShowPaywall] = useState(false);

  useEffect(() => {
    async function check() {
      const { remaining } = await checkFreeUsage(resourceType);
      setFreeRemaining(remaining);
      setShowPaywall(remaining === 0);
    }
    check();
  }, [resourceType, checkFreeUsage]);

  if (!showPaywall) {
    return <>{children}</>;
  }

  const prices: Record<string, { usd: number; description: string }> = {
    chat_message: { usd: 0.01, description: 'Send an AI chat message' },
    knowledge_search: { usd: 0.02, description: 'Search the knowledge base' },
    premium_quest: { usd: 0.05, description: 'Access premium quest content' },
  };

  const price = prices[resourceType] || { usd: 0.01, description: 'Access resource' };

  return (
    <Card className="max-w-md mx-auto">
      <CardHeader>
        <CardTitle>Payment Required</CardTitle>
        <CardDescription>
          You&apos;ve used all your free {resourceType.replace('_', ' ')} credits today.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="text-center">
          <p className="text-2xl font-bold">${price.usd.toFixed(2)}</p>
          <p className="text-sm text-muted-foreground">{price.description}</p>
        </div>

        {!isConnected ? (
          <Button className="w-full" variant="outline">
            Connect Wallet
          </Button>
        ) : (
          <Button
            className="w-full"
            onClick={() => {
              // Trigger payment flow
            }}
            disabled={isPaying}
          >
            {isPaying ? 'Processing...' : `Pay with USDC`}
          </Button>
        )}

        <p className="text-xs text-center text-muted-foreground">
          Payments are processed on Base L2 for minimal fees
        </p>
      </CardContent>
    </Card>
  );
}
```

---

## Testing

### Local Development

```bash
# Start local blockchain (Anvil/Hardhat)
anvil --fork-url https://mainnet.base.org

# Deploy test USDC
cast send --private-key $PRIVATE_KEY \
  0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913 \
  "transfer(address,uint256)" \
  $TEST_ADDRESS \
  1000000000  # 1000 USDC
```

### Integration Tests

```rust
// tests/payment_integration.rs

#[tokio::test]
async fn test_payment_flow() {
    let app = create_test_app().await;

    // Request payment
    let response = app
        .post("/payments/request/chat_message")
        .json(&json!({ "token": "USDC" }))
        .send()
        .await;

    assert_eq!(response.status(), 200);

    let payment_request: PaymentRequest = response.json().await;
    assert_eq!(payment_request.price_usd, 0.01);

    // Simulate payment on testnet
    let tx_hash = send_test_payment(&payment_request).await;

    // Verify payment
    let verify_response = app
        .post("/payments/verify")
        .json(&json!({
            "payment_id": payment_request.payment_id,
            "tx_hash": tx_hash,
        }))
        .send()
        .await;

    assert_eq!(verify_response.status(), 200);

    let verification: VerifyResponse = verify_response.json().await;
    assert!(verification.verified);
    assert!(verification.access_token.is_some());
}
```

---

## Security Considerations

1. **Transaction Verification**: Always verify on-chain, never trust client-submitted data
2. **Replay Protection**: Mark payments as used immediately after verification
3. **Expiration**: Payment requests should expire (15 minutes recommended)
4. **Amount Validation**: Verify exact amounts, reject overpayments (refund complexity)
5. **Chain Verification**: Verify correct chain ID to prevent cross-chain attacks

---

## Related Documentation

- [Architecture](../../sruth/tuath/docs/ARCHITECTURE.md) - System overview
- [API Reference](../../sruth/tuath/docs/api/README.md) - Payment endpoints
- [x402 Library](../x402/) - Full x402 implementation
