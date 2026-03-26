# **The Architecture of Autonomous Value: Replicating SaaS Metering and Tiered Billing in the Agentic Economy via x402 and AP2**

## **1\. Introduction: The Structural Transformation of Digital Monetization**

The digital economy stands at a precipice of a structural transformation that is fundamentally altering the mechanics of value exchange. For the past decade, the "API Economy" has been underpinned by robust, fiat-centric infrastructure—exemplified by platforms like Stripe and its emergent orchestration layers such as Autumn.dev. These systems have successfully abstracted the immense complexity of metering, entitlement management, and recurring billing for human-initiated transactions. They have allowed developers to seamlessly "measure and arrange" API tiers, creating the frictionless Software-as-a-Service (SaaS) models that dominate the web today. However, the emergence of the "Agentic Economy"—a paradigm where autonomous Artificial Intelligence (AI) agents perform tasks, execute complex workflows, and transact value without direct human intervention—has exposed the critical limitations of these legacy rails.  
Traditional payment infrastructures are predicated on human identity, banking relationships, and credit card authorization flows that are fundamentally incompatible with the stateless, high-frequency, and permissionless nature of AI agents. Agents lack biometric identities for Know Your Customer (KYC) checks, cannot physically hold credit cards, and often require micro-transaction capabilities (e.g., paying $0.0005 per inference) that are economically unviable on traditional settlement networks due to fixed transaction fees. Consequently, a new stack is required—one that mirrors the sophisticated logic of Autumn.dev but is built upon the cryptographic certainties of blockchain technology.  
This report provides an exhaustive architectural analysis of the infrastructure required to replicate the functionality of Autumn.dev—specifically API metering, dynamic tier management, and billing orchestration—within a cryptocurrency context. We explore the Google Agent Payments Protocol (AP2) and the x402 protocol not merely as payment methods, but as the foundational communication layers for a new "Machine Commerce" stack. Furthermore, we identify and evaluate specific "Autumn-like" middleware platforms and protocols that operate across **Ethereum (ETH)**, **Solana (SOL)**, and **Cronos**, providing a comparative analysis of their capabilities in enabling sophisticated SaaS billing models compatible with the emerging x402 standard.  
The analysis is structured to guide a technical architect from the theoretical underpinnings of agentic protocols to the practical selection of vendor infrastructure. We examine how the static "subscription" model is evolving into dynamic "resource metering," and how the interaction between an AI agent's "intent" (managed by AP2) and the "settlement" (managed by x402) creates a closed-loop system for autonomous commerce. By dissecting the capabilities of providers like Sphere, Helio, and the emerging Cronos ecosystem, we construct a blueprint for a "Web3 Revenue Operations Stack" that is resilient, scalable, and future-proof.

## ---

**2\. The Protocol Layer: Standardizing Machine-to-Machine Negotiation**

To effectively replicate the "Autumn" experience in a decentralized environment, one must first understand the underlying communication protocols that replace the traditional HTTP API calls to centralized payment processors. Unlike the Web2 stack, where a single provider (like Stripe) often handles both the interface and the settlement, the Web3 stack is modular. It separates the *expression of intent* from the *execution of payment*.

### **2.1 Google Agent Payments Protocol (AP2): The Trust and Intent Architecture**

The **Agent Payments Protocol (AP2)**, spearheaded by Google in collaboration with a consortium of over 60 financial and technological organizations—including Mastercard, PayPal, Adyen, and Coinbase—represents the industry's consensus on solving the "trust gap" in agentic commerce.1 In the context of a SaaS platform looking to manage API tiers, AP2 serves as the high-level governance layer. It is the digital equivalent of a signed contract or a purchase order system, but designed for non-human actors.

#### **2.1.1 The Mechanism of Mandates**

The core innovation of AP2 is the introduction of "Mandates"—cryptographically signed Verifiable Credentials (VCs) that act as tamper-proof digital contracts. These mandates function similarly to the "Plan Definitions" in Autumn.dev but are portable and user-sovereign.

* **Intent Mandate:** This credential captures the user's high-level instructions and constraints. For a SaaS application, an Intent Mandate might encode a directive such as: *"I authorize my research agent to subscribe to the 'Pro' tier of the Data Analytics API, provided the cost does not exceed $50 per month."* This effectively replaces the "subscription agreement" in Web2. It is signed by the human user's private key, granting the agent the authority to negotiate within those bounds.1  
* **Cart Mandate:** Once the agent interacts with the SaaS provider, a Cart Mandate is generated. This creates a secure, immutable record of the specific items (e.g., "10,000 API Credits") and their price. In an Autumn-like context, this ensures that the tier structure presented to the agent cannot be bait-and-switched during checkout. It locks in the "arrangement" of the tier.2  
* **Payment Mandate:** This final credential signals to the payment network that the transaction is authorized. It provides the necessary visibility for risk management, allowing the payment processor (or smart contract) to verify that the agent is acting within the scope of the original Intent Mandate.3

#### **2.1.2 Relevance to SaaS Tier Management**

For a SaaS website, implementing AP2 provides a critical layer of **auditability** and **dispute resolution**. If an autonomous agent consumes a high volume of API calls, triggering a tier upgrade, the SaaS provider can cryptographically prove that this action was authorized by the human owner via the Intent Mandate. This replaces the "Terms of Service" acceptance click-through in traditional checkout flows with a cryptographic signature, essential for automated systems where no human is present to click "I Agree."  
Furthermore, AP2 is designed to be payment-rail agnostic. It orchestrates the *instruction* to pay but relies on underlying rails for settlement. Crucially, the protocol includes the **A2A x402 extension**, a specific component developed in partnership with Coinbase and the Ethereum Foundation to support stablecoins and cryptocurrency payments.4 This extension bridges the gap between the high-level intent (AP2) and the low-level blockchain execution (x402).

### **2.2 The x402 Protocol: The Native Payment Execution Layer**

While AP2 handles the *why* and *what* of a transaction, **x402** handles the *how*. It is the execution layer that enables resources to be exchanged for value over the internet without intermediaries. Developed largely by Coinbase, Cloudflare, and partners, x402 resurrects the dormant HTTP 402 "Payment Required" status code to create a standardized flow for machine-native payments.5

#### **2.2.1 The x402 Workflow: Turning APIs into Vending Machines**

The architecture of x402 is fundamentally different from the session-based, account-heavy model of Stripe or Autumn. It operates on a request-response basis, making it ideal for stateless API metering.

1. **The Resource Request:** A client (e.g., an AI agent) sends a standard HTTP request to a protected endpoint (e.g., POST /api/v1/complex-calculation).  
2. **The Challenge (402 Payment Required):** The SaaS server identifies that the request requires payment (either because the user has no credits or is on a pay-as-you-go tier). Instead of redirecting to a checkout page—which an agent cannot navigate—the server returns a 402 Payment Required status code.5  
3. **The Payment Instruction:** Crucially, the body of this 402 response contains a standardized JSON object, the **Payment Instruction**. This object details exactly what is required to proceed:  
   * **Amount:** e.g., "0.05 USDC" or "10 CRO".  
   * **Recipient:** The wallet address of the SaaS provider.  
   * **Network:** The required blockchain (e.g., base-mainnet, solana-mainnet, cronos-mainnet).7  
   * **Metadata:** Specific tier identifiers or invoice IDs.  
4. **The Settlement & Signing:** The agent parses this JSON, constructs a blockchain transaction matching the requirements, and signs it. In advanced implementations using EIP-3009 (Transfer with Authorization), the agent signs a message authorizing the transfer without needing to broadcast it and pay gas itself (gasless transactions).5  
5. **The Proof & Retry:** The agent resends the original request, this time attaching an X-PAYMENT header containing the signed transaction hash or authorization proof.  
6. **The Facilitator Verification:** The server receives the proof. Instead of running a full blockchain node to verify it (which is heavy), the server calls a **Facilitator**—a specialized infrastructure provider (like Coinbase Commerce or Cronos Labs' service) that indexes the blockchain. The Facilitator confirms the payment is valid and final.8  
7. **Access Granted:** The server processes the request and returns the data.

#### **2.2.2 The "Autumn" Implication: Granular Metering**

This workflow enables a level of metering granularity that Autumn.dev approximates but x402 perfects. With x402, every single API call can be a discrete financial transaction. There is no need to "measure" usage over a month and bill later (risking non-payment); the measurement and the payment are atomic. The payment *is* the access.  
For the user's specific requirement of "arranging API tiers," x402 allows for dynamic pricing. The "Payment Instruction" for a basic query might request $0.01, while a complex query requests $0.10. The agent automatically adjusts its payment based on the instruction, creating a seamless, tier-aware consumption model without the friction of upgrading subscriptions manually.

## ---

**3\. Infrastructure Analysis: The "Autumn" Alternatives for Web3**

While x402 provides the protocol for payment, it does not inherently manage the *logic* of billing—the "Revenue Operations" layer that Autumn.dev provides (e.g., "User X is on the Enterprise Plan," "User Y has used 80% of their quota"). To replicate this, we must look to **Web3 Monetization Platforms** that sit on top of the blockchain layer.  
The following analysis evaluates the top contenders capable of delivering this logic across **Ethereum (ETH)**, **Solana (SOL)**, and **Cronos (CRO)**, assessing their ability to measure usage and arrange tiers.

### **3.1 Sphere (SpherePay): The Usage-Based Billing Specialist**

**Sphere** emerges from the analysis as the closest functional equivalent to Autumn.dev for the EVM and Solana ecosystems. It positions itself specifically as a "payments API for digital currencies," with a strong architectural focus on usage-based billing—the precise feature set requested.9

* **Metering Logic (The "Measure" Requirement):** Sphere's API includes a dedicated Usage Records endpoint. This allows a SaaS developer to decouple the service delivery from the billing calculation.  
  * *Mechanism:* When a user consumes a resource (e.g., processes a file), the SaaS backend sends a "Usage Record" to Sphere (e.g., { "customer": "0x123...", "quantity": 50, "action": "file\_process" }).  
  * *Calculation:* Sphere aggregates these records over a billing period and calculates the total due based on the "Price" object defined for that customer's tier.10 This is identical to the Autumn/Stripe metering model.  
* **Tier Arrangement:** Sphere allows for the creation of sophisticated "Products" and "Prices" (e.g., Flat fee \+ Overage, Graduated pricing). This satisfies the requirement to "arrange API tiers" easily.  
* **Multi-Chain Support:** Sphere demonstrates robust multi-chain capabilities, supporting **Solana** and major EVM chains like **Ethereum**, **Base**, **Optimism**, and **Polygon**. Crucially, it integrates the **Pyth** oracle network to ensure that crypto-to-fiat conversions (e.g., pricing a tier at $50 USD but accepting payment in ETH) are accurate and resistant to volatility.10  
* **x402 Synergy:** Sphere acts as the logic layer behind the x402 interface. A developer can use x402 to collect the initial authorization (the "Intent Mandate" or subscription approval), and then use Sphere's infrastructure to execute the recurring or metered charges against that authorization.

### **3.2 Helio: The Multi-Chain Payment Orchestrator**

**Helio** (recently acquired by MoonPay) is a dominant infrastructure provider, particularly strong on Solana but with full EVM support. While its roots are in creator economy payments, it has evolved into a powerful SaaS billing engine.11

* **Key Feature: Pay Streams (Time-Based Metering):** Helio introduces a primitive called "Pay Streams" which offers a different approach to metering than Autumn. Instead of counting *events* (API calls), it meters *time*.  
  * *Mechanism:* A user sets up a stream that pays, for example, 0.0001 SOL per minute to the SaaS provider.  
  * *Application:* This is ideal for access-based SaaS (e.g., "Premium Dashboard Access"). The SaaS provider checks if the stream is active. If the user stops the stream, access is revoked instantly via webhook.13 This provides "real-time" metering that is arguably superior to monthly billing for certain use cases.  
* **Tier Management:** Helio's dashboard allows merchants to define distinct "Payment Links" or "Plans" (e.g., Basic Plan, Pro Stream, Enterprise Annual). This provides a "Stripe-like" experience for arranging tiers that users can subscribe to.14  
* **Chain Support:** Helio is natively multi-chain, with exceptional support for **Solana**, **Ethereum**, **Polygon**, and **Base**. It abstracts the complexity of different token standards (SPL vs. ERC-20), allowing a SaaS to accept SOL, USDC, ETH, or MATIC through a single integration.  
* **Developer Experience:** Helio provides a robust API and webhooks. A SaaS platform would listen for the payment\_success or stream\_active webhook to automatically provision API keys or update entitlement tables in the backend.15

### **3.3 Superfluid: The Real-Time Finance Primitive (EVM Focused)**

**Superfluid** offers a paradigm unique to Web3 called **Asset Streaming**, representing a radical departure from the discrete payment model of Autumn/Stripe.16

* **The Concept:** Money flows like water. A subscription is not a monthly event but a continuous flow of tokens every second.  
* **SaaS Application:** This allows for extreme "Micro-SaaS" models. A user opens a stream to the SaaS smart contract. The backend checks the "Flow Rate" (e.g., 10 USDCx/month). If the flow is active, the API key is valid. If the user runs out of funds, the stream dries up, and the API key is instantly disabled by the protocol itself.  
* **Pros & Cons:**  
  * *Pros:* Extremely capital efficient for users (no pre-payment), zero "dunning" costs for merchants (no chasing failed credit cards), and strictly "pay-as-you-go."  
  * *Cons:* It currently requires users to "wrap" tokens (e.g., converting USDC to USDCx) to enable streaming properties.18 Furthermore, it is primarily an **EVM-native** solution (Ethereum, Polygon, Base, Avalanche, BNB Chain), and lacks native support for **Solana** or the Cosmos-side of **Cronos** (though it may function on Cronos EVM).  
* **x402 Alignment:** Superfluid acts as the ultimate settlement layer for an x402 interaction. An agent could hit an endpoint, receive a 402, and respond by opening a Superfluid stream, effectively automating the "subscription" process.

### **3.4 Request Network: The Compliance and Invoicing Layer**

For B2B SaaS where "metering" results in a monthly invoice rather than instant micropayments (e.g., Enterprise tiers), **Request Network** is the industry standard.19

* **Functionality:** It generates on-chain invoices that serve as immutable requests for payment. It supports "Req-to-Pay," where a payer detects a pending invoice and pays it in one click.  
* **Metering Integration:** Unlike Sphere, Request Network does not *count* the usage itself. You would need an internal meter (or a tool like Moesif) to aggregate usage. At the end of the billing cycle, your system calls the Request Network API to generate a crypto-invoice for that usage amount.20  
* **Compliance:** It excels in providing audit trails compliant with accounting standards (IFRS/GAAP), solving the "receipt" problem in crypto billing.21

## ---

**4\. Chain-Specific Implementation Strategy**

To satisfy the specific requirement of supporting **ETH**, **SOL**, and **Cronos** simultaneously, a "Universal Payment Gateway" architecture is required. The ecosystem is fragmented, so the implementation strategy must adapt to the strengths of each chain.

### **4.1 Ethereum (ETH) & L2s (Base, Polygon)**

This is the home turf of the standard x402 implementation.

* **Facilitator:** **Coinbase Commerce (CDP) Facilitator**. This is the default, production-grade facilitator for USDC on Base and Ethereum. It handles the indexing and verification of payments for free or low cost.8  
* **Logic Layer (Autumn Replacement):** **Sphere**.  
  * Use Sphere's API to create "Products" mirroring your SaaS tiers.  
  * Use Sphere's webhook infrastructure to listen for payments on ETH/Base.  
  * *Why:* Sphere's "Usage Records" on EVM are robust and directly replace Autumn's metering.

### **4.2 Solana (SOL)**

Solana's high speed and low cost make it the ideal environment for the "micropayment" aspect of x402 (paying per API call).

* **Facilitator:** **Corbits**. The research explicitly identifies Corbits as a production-grade facilitator for x402 on Solana.22 It is designed to handle high-frequency "pay-per-RPC call" or "pay-per-compute" models.  
* **Logic Layer (Autumn Replacement):** **Helio**.  
  * Helio is the "Stripe for Solana." Its "Pay Streams" are natively optimized for Solana's architecture.  
  * *Why:* The combination of Corbits (for agentic 402 negotiation) and Helio (for recurring stream management) provides complete coverage for Solana billing.

### **4.3 Cronos (CRO)**

Cronos is an emerging frontier in this domain. While it lacks the mature SaaS tooling of Solana (Helio) or Base (Coinbase), it is aggressively investing in AI-native payments.

* **Ecosystem Context:** Cronos Labs has launched a **$42,000 x402 PayTech Hackathon**, signaling a strategic pivot to becoming a hub for agentic payments. This creates a "greenfield" opportunity where developers can access grants and support.24  
* **Facilitator:** Cronos has deployed a dedicated **Cronos x402 Facilitator**.  
  * **Endpoint:** https://facilitator.cronoslabs.org.  
  * **Functionality:** This service enables sellers to accept on-chain stablecoin payments (USDC, CRO) via a simple HTTP API, abstracting the need to run Cronos nodes.26  
* **SDKs:** The **Crypto.com AI Agent SDK** is available to help developers integrate these payments into agent workflows. This SDK allows agents to "read" the blockchain and "execute" payments programmatically.25  
* **Logic Layer Gap:** There is no direct "Autumn" equivalent on Cronos yet.  
  * *Strategic Recommendation:* Developers on Cronos should use the **Cronos x402 Facilitator** for the payment handshake and build a lightweight metering database (using PostgreSQL/Redis) or adapt a generic API analytics tool like **Moesif** (see Section 5\) to track usage, utilizing the facilitator's webhooks to reconcile payments.

## ---

**5\. Architectural Blueprint: The "Web3 Autumn" Stack**

To fully answer the request for a system that "measures/arranges API tiers" across these specific chains, we propose a composite architecture. This stack replaces Autumn's monolithic service with best-in-class modular Web3 components.

### **5.1 The "Moesif \+ x402" Strategy**

For developers who want granular "measurement" of API tiers (e.g., 1,000 calls \= $5) and need to support *all* chains including Cronos, the most powerful combination is **Moesif** combined with x402 payment gateways.

* **The Meter (Autumn Replacement):** **Moesif**.  
  * Moesif is a dedicated API analytics platform. While primarily Web2, it has deep "Metered Billing" features. It tracks API usage by user ID, company, or wallet address.28  
  * *Why:* It allows you to define complex billing rules (e.g., "First 1k calls free, then $0.01/call") independent of the payment rail.  
* **The Payment Rail (Stripe Replacement):** **x402 Facilitators**.  
  * You use x402 to collect the funds (in CRO, SOL, ETH).  
* **The Middleware (The Glue):** **Zuplo** or Custom Gateway.  
  * Zuplo is an API gateway that has native plugins for metering and can easily integrate with x402 flows.29

### **5.2 Step-by-Step Implementation Flow**

1. **Track:** The user (Agent) makes an API request. The Gateway (Zuplo) logs this event to **Moesif**.  
2. **Gate:** The Gateway checks Moesif: *"Has Wallet 0x123... exceeded their paid quota?"*  
3. **Charge (x402):**  
   * If the quota is exceeded, the Gateway returns 402 Payment Required.  
   * The response body includes the **Payment Instruction**: *"Send 10 CRO to \[Cronos Address\] OR 5 USDC to."*  
4. **Settle:** The Agent signs and broadcasts the transaction on their preferred chain (Cronos, SOL, or ETH).  
5. **Reconcile:** The chain-specific **Facilitator** (Cronos Labs Facilitator or Corbits) detects the confirmed transaction.  
6. **Credit:** The Facilitator fires a webhook to your backend. Your backend calls the Moesif API to "Credit" the user's balance with the purchased quota.  
7. **Access:** The Agent retries the request. The Gateway checks Moesif again, sees the new balance, and allows the request through.

This architecture replicates the *exact* "measure/arrange API tiers" capability of Autumn but decouples it from fiat, allowing you to use native crypto rails across any supported blockchain.

## ---

**6\. Comparative Overview of Solutions**

The following table summarizes the capabilities of the discussed platforms against the requirements of the "Web3 Autumn."

| Feature | Autumn.dev (Web2 Standard) | Sphere (Web3 Native) | Helio (Web3 Native) | Superfluid (Streaming) | Moesif \+ x402 (Hybrid Stack) |
| :---- | :---- | :---- | :---- | :---- | :---- |
| **Core Function** | Metering/Billing Logic | Payments API & Metering | Payment Dashboard | Asset Streaming | Analytics & Metering |
| **Chain Support** | Fiat Only | SOL, EVM (Base/Poly) | SOL, EVM (Base/Poly) | EVM Only | **Any** (Chain Agnostic) |
| **Metering Model** | Event-based (Native) | "Usage Records" (Native) | Time-based (Streams) | Time-based (Real-time) | **Deep Event-based** |
| **x402 Ready?** | No | Conceptually Aligned | API Compatible | Settlement Layer | **Yes (via Middleware)** |
| **Cronos Support** | No | Generic EVM | Generic EVM | Generic EVM | **Yes (via Facilitator)** |
| **Tier Management** | High (Drag & Drop) | High (API-driven) | High (Dashboard) | Low (Protocol level) | **High (Analytics driven)** |
| **Best For...** | Traditional SaaS | Usage-based Web3 SaaS | Creators & Subscriptions | High-frequency Access | **Complex/Enterprise SaaS** |

## ---

**7\. Conclusion & Strategic Recommendation**

The transition to an agent-native SaaS model requires a fundamental rethinking of billing infrastructure. While no single "Web3 Stripe" currently offers a unified dashboard for ETH, SOL, and Cronos with built-in metering, the components to build this exist today.  
**For your SaaS website, the recommended path forward is:**

1. **Adopt a Hybrid "Moesif \+ x402" Architecture:** This is the only robust way to support **Cronos** alongside ETH and SOL without waiting for ecosystem maturity. Moesif handles the "measurement" and "tier arrangement" (the Autumn role) seamlessly, while x402 facilitators handle the settlement on each respective chain.  
2. **Leverage Chain-Specific Facilitators:**  
   * Use **Coinbase CDP** for Base/ETH payments.  
   * Use **Corbits** for Solana payments.  
   * Use the **Cronos x402 Facilitator** for Cronos payments.  
3. **Implement Google AP2 for Governance:** Use AP2 "Intent Mandates" to allow users to pre-authorize these payments. This builds trust, ensuring that when your system sends a 402 Payment Required challenge, the user's agent is already authorized to pay it, creating a frictionless, invisible checkout experience.

By decoupling the *metering logic* (Moesif) from the *payment execution* (x402), you effectively future-proof your platform. You gain the sophisticated tier management of Autumn.dev while unlocking the permissionless, automated revenue streams of the Agentic Economy.

#### **Works cited**

1. Google's AP2: A new protocol for AI agent payments, accessed December 12, 2025, [https://www.vellum.ai/blog/googles-ap2-a-new-protocol-for-ai-agent-payments](https://www.vellum.ai/blog/googles-ap2-a-new-protocol-for-ai-agent-payments)  
2. How Google's AP2 Sets New Standards for Agentic Payments \- Technology Magazine, accessed December 12, 2025, [https://technologymagazine.com/news/agentic-pay-systems-googles-agent-payments-protocol](https://technologymagazine.com/news/agentic-pay-systems-googles-agent-payments-protocol)  
3. Google's AP2 Gives Developers New Tools to Build Agentic Payments \- DeepLearning.AI, accessed December 12, 2025, [https://www.deeplearning.ai/the-batch/googles-ap2-gives-developers-new-tools-to-build-agentic-payments/](https://www.deeplearning.ai/the-batch/googles-ap2-gives-developers-new-tools-to-build-agentic-payments/)  
4. Hong Kong's first financial "influencer" sentenced to imprisonment for operating an unlicensed, paid social media group to provide investment advice. | MEXC News, accessed December 12, 2025, [https://www.mexc.com/en-NG/news/hong-kongs-first-financial-influencer-sentenced-to-imprisonment-for-operating-an-unlicensed-paid-social-media-group-to-provide-investment-advice/158769](https://www.mexc.com/en-NG/news/hong-kongs-first-financial-influencer-sentenced-to-imprisonment-for-operating-an-unlicensed-paid-social-media-group-to-provide-investment-advice/158769)  
5. How to Implement a Crypto Paywall with x402 Payment Protocol | Quicknode Guides, accessed December 12, 2025, [https://www.quicknode.com/guides/infrastructure/how-to-use-x402-payment-required](https://www.quicknode.com/guides/infrastructure/how-to-use-x402-payment-required)  
6. x402: An AI-Native Payment Protocol for the Web | by Jung-Hua Liu | Oct, 2025 | Medium, accessed December 12, 2025, [https://medium.com/@gwrx2005/x402-an-ai-native-payment-protocol-for-the-web-419358450936](https://medium.com/@gwrx2005/x402-an-ai-native-payment-protocol-for-the-web-419358450936)  
7. coinbase/x402: A payments protocol for the internet. Built on HTTP. \- GitHub, accessed December 12, 2025, [https://github.com/coinbase/x402](https://github.com/coinbase/x402)  
8. How x402 Works \- Coinbase Developer Documentation, accessed December 12, 2025, [https://docs.cdp.coinbase.com/x402/core-concepts/how-it-works](https://docs.cdp.coinbase.com/x402/core-concepts/how-it-works)  
9. SpherePay Subscription: Seamless Recurring Payments for SaaS & Consumption-Based Businesses | Sphere Knowledgebase \- Intercom, accessed December 12, 2025, [https://intercom.help/spherepay/en/articles/10514242-spherepay-subscription-seamless-recurring-payments-for-saas-consumption-based-businesses](https://intercom.help/spherepay/en/articles/10514242-spherepay-subscription-seamless-recurring-payments-for-saas-consumption-based-businesses)  
10. Introduction, accessed December 12, 2025, [https://spherepay.readme.io/reference/introduction](https://spherepay.readme.io/reference/introduction)  
11. Loop Crypto vs. Helio, accessed December 12, 2025, [https://www.loopcrypto.xyz/blog/loop-crypto-vs-helio](https://www.loopcrypto.xyz/blog/loop-crypto-vs-helio)  
12. The PayFi Report 2025 (Jan & Feb) by PolyFlow \- Medium, accessed December 12, 2025, [https://polyflow.medium.com/the-payfi-report-2025-jan-feb-by-polyflow-98fe4527d6bd](https://polyflow.medium.com/the-payfi-report-2025-jan-feb-by-polyflow-98fe4527d6bd)  
13. Introducing Pay Streams…. Today we shipped Pay Streams, recurring… | by Stijn | Helio | Medium, accessed December 12, 2025, [https://medium.com/helio-fintech/introducing-pay-streams-2a8e1944e5c6](https://medium.com/helio-fintech/introducing-pay-streams-2a8e1944e5c6)  
14. Merchant onboarding guide — Web3 payments | by Stijn | Helio \- Medium, accessed December 12, 2025, [https://medium.com/helio-fintech/merchant-onboarding-guide-web3-payments-94f08328cc75](https://medium.com/helio-fintech/merchant-onboarding-guide-web3-payments-94f08328cc75)  
15. heliopay/README.md at main \- GitHub, accessed December 12, 2025, [https://github.com/heliofi/heliopay/blob/main/README.md](https://github.com/heliofi/heliopay/blob/main/README.md)  
16. Paywall | ETHGlobal, accessed December 12, 2025, [https://ethglobal.com/showcase/paywall-e9ewg](https://ethglobal.com/showcase/paywall-e9ewg)  
17. Superfluid | Stream Money Every Second, accessed December 12, 2025, [https://superfluid.org/](https://superfluid.org/)  
18. Superfluid — Real-time Token Streaming Protocol (Great for DeFi Hacks) \- Medium, accessed December 12, 2025, [https://medium.com/@BizthonOfficial/superfluid-real-time-token-streaming-protocol-great-for-defi-hacks-df0dbbb5d11b](https://medium.com/@BizthonOfficial/superfluid-real-time-token-streaming-protocol-great-for-defi-hacks-df0dbbb5d11b)  
19. Onchain invoicing \- Request Network, accessed December 12, 2025, [https://request.network/onchain-invoicing](https://request.network/onchain-invoicing)  
20. Request Network \- Avalanche Builder Hub, accessed December 12, 2025, [https://build.avax.network/integrations/request](https://build.avax.network/integrations/request)  
21. Request Finance 2025 Pricing, Features, Reviews & Alternatives \- GetApp, accessed December 12, 2025, [https://www.getapp.com/finance-accounting-software/a/request-finance/](https://www.getapp.com/finance-accounting-software/a/request-finance/)  
22. Ecosystem \- x402, accessed December 12, 2025, [https://www.x402.org/ecosystem](https://www.x402.org/ecosystem)  
23. How to get started with x402 on Solana, accessed December 12, 2025, [https://solana.com/developers/guides/getstarted/intro-to-x402](https://solana.com/developers/guides/getstarted/intro-to-x402)  
24. Can AI Agents Pay Each Other? How Cronos Is Testing the Next Frontier with x402 PayTech Hackathon | HackerNoon, accessed December 12, 2025, [https://hackernoon.com/can-ai-agents-pay-each-other-how-cronos-is-testing-the-next-frontier-with-x402-paytech-hackathon](https://hackernoon.com/can-ai-agents-pay-each-other-how-cronos-is-testing-the-next-frontier-with-x402-paytech-hackathon)  
25. Cronos x402 Paytech Hackathon \- DoraHacks, accessed December 12, 2025, [https://dorahacks.io/hackathon/cronos-x402/detail](https://dorahacks.io/hackathon/cronos-x402/detail)  
26. Resources & Next Steps \- Cronos EVM Docs, accessed December 12, 2025, [https://docs.cronos.org/cronos-x402-facilitator/resources-and-next-steps](https://docs.cronos.org/cronos-x402-facilitator/resources-and-next-steps)  
27. Chainwire's Profile | Binance Square, accessed December 12, 2025, [https://www.binance.com/en-NG/square/profile/chainwire](https://www.binance.com/en-NG/square/profile/chainwire)  
28. Moesif, accessed December 12, 2025, [https://www.moesif.com/](https://www.moesif.com/)  
29. Pickaxe Actions & MCP Servers | Build AI Tools, accessed December 12, 2025, [https://pickaxe.co/ai/actions](https://pickaxe.co/ai/actions)  
30. Rewiring America deploys Zuplo to accelerate their API program, accessed December 12, 2025, [https://zuplo.com/blog/rewiring-america-accelerates-api-program-with-zuplo](https://zuplo.com/blog/rewiring-america-accelerates-api-program-with-zuplo)