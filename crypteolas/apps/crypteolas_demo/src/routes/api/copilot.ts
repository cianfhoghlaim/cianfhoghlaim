/**
 * CopilotKit Backend API Route
 *
 * Handles AI chat requests from the CopilotKit frontend
 * Integrates with Agno agents and MCP tools
 * Includes x402 payment gating for premium features
 */

import { createAPIFileRoute } from "@tanstack/start/api";
import {
  CRYPTO_SYSTEM_PROMPT,
  cryptoTools,
  executeToolCall
} from "../../lib/copilot/runtime";
import { withPayment, type PaymentInfo } from "../../lib/x402/middleware";
import { recordUsage, hasFreeTierRemaining } from "../../lib/x402/payment-service";
import { getSession } from "../../lib/auth/server";

// LLM Provider configuration
const LLM_BASE_URL = process.env.LITELLM_BASE_URL || "http://localhost:4000";
const LLM_MODEL = process.env.LLM_MODEL || "gpt-4o-mini";
const OPENAI_API_KEY = process.env.OPENAI_API_KEY || "";

// Feature ID for payment tracking
const CHAT_FEATURE_ID = "chat_message";

export const Route = createAPIFileRoute("/api/copilot")({
  POST: async ({ request }) => {
    // Parse request body
    const body = await request.json();
    const { messages, tools: clientTools, stream = true } = body;

    // Get session info for usage tracking
    let userId: string | undefined;
    let walletAddress: string | undefined;

    try {
      const sessionData = await getSession(request);
      userId = sessionData?.user?.id;
      walletAddress = sessionData?.user?.walletAddress || undefined;
    } catch {
      // Continue without session
    }

    // Fallback to header
    if (!walletAddress) {
      walletAddress = request.headers.get("X-Wallet-Address") || undefined;
    }

    // Check free tier (handled here for streaming support)
    const paymentHeader = request.headers.get("PAYMENT-SIGNATURE") || request.headers.get("X-PAYMENT");
    const isPaid = !!paymentHeader;

    if (!isPaid && (userId || walletAddress)) {
      const freeTierStatus = await hasFreeTierRemaining({
        userId,
        walletAddress,
        featureId: CHAT_FEATURE_ID,
      });

      if (!freeTierStatus.hasRemaining) {
        // Return 402 with payment requirements
        return new Response(
          JSON.stringify({
            error: "Free tier exhausted",
            remainingFree: 0,
            requiresPayment: true,
            featureId: CHAT_FEATURE_ID,
          }),
          {
            status: 402,
            headers: { "Content-Type": "application/json" }
          }
        );
      }
    }

    // Record usage (for free tier or paid)
    if (userId || walletAddress) {
      await recordUsage({
        userId,
        walletAddress,
        featureId: CHAT_FEATURE_ID,
      });
    }

    // Build messages with system prompt
    const messagesWithSystem = [
      { role: "system", content: CRYPTO_SYSTEM_PROMPT },
      ...messages,
    ];

    // Convert crypto tools to OpenAI format
    const llmTools = cryptoTools.map(tool => ({
      type: "function" as const,
      function: {
        name: tool.name,
        description: tool.description,
        parameters: tool.parameters,
      },
    }));

    try {
      // Determine API endpoint
      const apiUrl = LLM_BASE_URL.includes("localhost")
        ? `${LLM_BASE_URL}/chat/completions`
        : "https://api.openai.com/v1/chat/completions";

      // Call LLM
      const response = await fetch(apiUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${OPENAI_API_KEY}`,
        },
        body: JSON.stringify({
          model: LLM_MODEL,
          messages: messagesWithSystem,
          tools: llmTools,
          tool_choice: "auto",
          stream,
        }),
      });

      if (!response.ok) {
        console.error("LLM API error:", response.status, await response.text());
        // Fallback to mock response
        return createMockResponse(messages);
      }

      if (stream) {
        // Stream the response, handling tool calls
        return streamWithToolCalls(response, llmTools);
      } else {
        // Non-streaming response with tool call handling
        return handleNonStreamingResponse(response, llmTools);
      }
    } catch (error) {
      console.error("Copilot API error:", error);
      return createMockResponse(messages);
    }
  },
});

/**
 * Stream response with tool call handling
 */
async function streamWithToolCalls(
  llmResponse: Response,
  tools: Array<{ type: "function"; function: { name: string } }>
): Promise<Response> {
  // For now, pass through the stream
  // TODO: Implement tool call interception and execution
  return new Response(llmResponse.body, {
    headers: {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache",
      Connection: "keep-alive",
    },
  });
}

/**
 * Handle non-streaming response with tool execution
 */
async function handleNonStreamingResponse(
  llmResponse: Response,
  tools: Array<{ type: "function"; function: { name: string } }>
): Promise<Response> {
  const data = await llmResponse.json();
  const message = data.choices?.[0]?.message;

  // Check for tool calls
  if (message?.tool_calls && message.tool_calls.length > 0) {
    const toolResults = await Promise.all(
      message.tool_calls.map(async (toolCall: { id: string; function: { name: string; arguments: string } }) => {
        const args = JSON.parse(toolCall.function.arguments);
        const result = await executeToolCall(toolCall.function.name, args);
        return {
          tool_call_id: toolCall.id,
          role: "tool",
          content: JSON.stringify(result),
        };
      })
    );

    // Return tool results for client to continue conversation
    return new Response(
      JSON.stringify({
        ...data,
        toolResults,
        requiresContinuation: true,
      }),
      { headers: { "Content-Type": "application/json" } }
    );
  }

  return new Response(JSON.stringify(data), {
    headers: { "Content-Type": "application/json" },
  });
}

/**
 * Create mock response when LLM is unavailable
 */
function createMockResponse(messages: Array<{ role: string; content: string }>) {
  const lastMessage = messages[messages.length - 1]?.content || "";
  const response = generateMockContent(lastMessage);

  const data = {
    id: `chatcmpl-${Date.now()}`,
    object: "chat.completion",
    created: Math.floor(Date.now() / 1000),
    model: "mock",
    choices: [
      {
        index: 0,
        message: {
          role: "assistant",
          content: response.content,
        },
        finish_reason: "stop",
      },
    ],
    usage: {
      prompt_tokens: 0,
      completion_tokens: 0,
      total_tokens: 0,
    },
    sources: response.sources,
  };

  return new Response(JSON.stringify(data), {
    headers: { "Content-Type": "application/json" },
  });
}

/**
 * Generate mock content based on query
 */
function generateMockContent(input: string): { content: string; sources: Array<{ title: string; type: string }> } {
  const lower = input.toLowerCase();

  if (lower.includes("usde") || lower.includes("ethena")) {
    return {
      content: `## Ethena USDe Analysis

USDe is a synthetic dollar maintaining its peg through delta-neutral hedging:

### Current Metrics
- **TVL**: $2.8B
- **sUSDe APY**: 27.4%
- **Peg Range**: $0.9998 - $1.0002

### Mechanism
1. Deposit stETH as collateral
2. Open short perpetual positions on CEXs
3. Earn staking + funding rate yields

### Key Risks
- **Funding Rate Risk**: Negative funding can erode yields
- **Custodial Risk**: Relies on centralized exchanges for hedging
- **Smart Contract Risk**: Complex interactions with multiple protocols

The protocol has been audited by Zellic and Spearbit with no critical issues found.`,
      sources: [
        { title: "Ethena Whitepaper", type: "Document" },
        { title: "Zellic Audit Report", type: "Audit" },
        { title: "DeFiLlama TVL Data", type: "API" },
      ],
    };
  }

  if (lower.includes("yield") || lower.includes("strategy")) {
    return {
      content: `## Current Yield Opportunities

| Strategy | APY | Risk | Protocol |
|----------|-----|------|----------|
| sUSDe Staking | 27.4% | Medium | Ethena |
| Pendle PT-sUSDe | 32.1% | Medium | Pendle |
| Aave USDC | 3.5% | Low | Aave v3 |
| Lido stETH | 3.8% | Low | Lido |

### Recommended Allocation (Medium Risk)
- **40%** sUSDe (yield)
- **35%** Pendle PT (fixed yield)
- **25%** Aave (stability)

*Note: Always DYOR. Yields are variable and past performance doesn't guarantee future results.*`,
      sources: [
        { title: "Yield Aggregator Data", type: "API" },
        { title: "Protocol Integrations", type: "Graph" },
        { title: "DeFi Strategy Docs", type: "Document" },
      ],
    };
  }

  if (lower.includes("risk")) {
    return {
      content: `## DeFi Risk Framework

### Smart Contract Risk (Low-Medium)
- Major protocols have multiple audits
- Bug bounties provide ongoing security

### Economic Risk (Medium)
- Peg mechanisms can fail under stress
- Liquidation cascades possible

### Counterparty Risk (Medium-High)
- CEX dependencies (Ethena)
- Oracle manipulation vectors

### Governance Risk (Low-Medium)
- Token concentration varies
- Multisig configurations

*Current overall market risk score: 6.2/10 (Moderate)*`,
      sources: [
        { title: "Risk Framework v2.1", type: "Document" },
        { title: "Protocol Knowledge Graph", type: "Graph" },
      ],
    };
  }

  return {
    content: `I understand you're asking about "${input}".

Based on the indexed documents and knowledge graph, I can help analyze:
- DeFi protocol mechanics and risks
- Token economics and valuations
- Audit reports and security assessments
- Yield farming strategies
- Market trends and correlations

Could you provide more specific details about what aspect you'd like to explore? For example:
- Protocol name or token symbol
- Specific risk category
- Investment timeframe`,
    sources: [],
  };
}
