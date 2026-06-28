# Crypteolas Agent Integration Guide

Based on the exploration of CopilotKit and Agent OS implementations, this guide provides specific patterns for integrating agents into the crypteolas application.

---

## Overview

Crypteolas can leverage agent architectures for:
1. **Portfolio Analysis** - AI-driven insights into holdings
2. **Market Monitoring** - Real-time price/volatility tracking
3. **Trade Execution** - AI-suggested trades with user confirmation
4. **Risk Assessment** - Portfolio risk analysis and rebalancing suggestions
5. **News Synthesis** - Crypto news aggregation and analysis

---

## Architecture Recommendation

### Hybrid Approach: CopilotKit + Agent OS Pattern

```
┌─────────────────────────────────────────┐
│     Crypteolas React Frontend           │
├─────────────────────────────────────────┤
│                                          │
│  ┌────────────────────────────────────┐ │
│  │    CopilotKit (Generative UI)      │ │
│  │  - Portfolio analysis actions      │ │
│  │  - Trade execution flows           │ │
│  │  - Interactive confirmations       │ │
│  └────────────────────────────────────┘ │
│                                          │
│  ┌────────────────────────────────────┐ │
│  │  Market Data Stream (Agent OS)     │ │
│  │  - Real-time price feeds           │ │
│  │  - Reasoning/analysis steps        │ │
│  │  - Tool execution transparency     │ │
│  └────────────────────────────────────┘ │
│                                          │
└─────────────────────────────────────────┘
         ↑                              ↑
         │                              │
    CopilotKit                    Agno Platform
    Runtime API                   AgentOS Instance
```

---

## 1. State Management Setup

### Use Zustand for Crypto State

Combine CopilotKit's context with Zustand for domain-specific state:

```typescript
// src/store/crypto-store.ts
import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';

interface Portfolio {
  assets: {
    symbol: string;
    amount: number;
    entryPrice: number;
    currentPrice: number;
  }[];
  totalValue: number;
  unrealizedGain: number;
}

interface MarketData {
  [symbol: string]: {
    price: number;
    change24h: number;
    volume24h: number;
    lastUpdated: number;
  };
}

interface CryptoStore {
  // Portfolio state
  portfolio: Portfolio | null;
  setPortfolio: (portfolio: Portfolio) => void;
  
  // Market data
  marketData: MarketData;
  setMarketData: (data: MarketData) => void;
  updateAssetPrice: (symbol: string, price: number, change24h: number) => void;
  
  // Streaming state
  isStreamingMarketData: boolean;
  setIsStreamingMarketData: (streaming: boolean) => void;
  
  // Pending transactions
  pendingTransactions: Array<{
    id: string;
    action: 'buy' | 'sell';
    symbol: string;
    amount: number;
    targetPrice: number;
    status: 'pending' | 'confirmed' | 'cancelled';
  }>;
  addPendingTransaction: (tx: any) => void;
  updateTransactionStatus: (id: string, status: string) => void;
}

export const useCryptoStore = create<CryptoStore>()(
  persist(
    (set) => ({
      portfolio: null,
      setPortfolio: (portfolio) => set({ portfolio }),
      
      marketData: {},
      setMarketData: (data) => set({ marketData: data }),
      updateAssetPrice: (symbol, price, change24h) =>
        set((state) => ({
          marketData: {
            ...state.marketData,
            [symbol]: {
              price,
              change24h,
              volume24h: state.marketData[symbol]?.volume24h || 0,
              lastUpdated: Date.now(),
            },
          },
        })),
      
      isStreamingMarketData: false,
      setIsStreamingMarketData: (streaming) =>
        set({ isStreamingMarketData: streaming }),
      
      pendingTransactions: [],
      addPendingTransaction: (tx) =>
        set((state) => ({
          pendingTransactions: [...state.pendingTransactions, tx],
        })),
      updateTransactionStatus: (id, status) =>
        set((state) => ({
          pendingTransactions: state.pendingTransactions.map((tx) =>
            tx.id === id ? { ...tx, status } : tx
          ),
        })),
    }),
    {
      name: 'crypteolas-store',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        portfolio: state.portfolio,
      }),
    }
  )
);
```

---

## 2. CopilotKit Integration

### 2.1 Layout Setup

```typescript
// app/layout.tsx
import { CopilotKit } from "@copilotkit/react-core";

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <CopilotKit
          runtimeUrl={process.env.NEXT_PUBLIC_COPILOTKIT_RUNTIME_URL || "/api/copilotkit"}
          publicApiKey={process.env.NEXT_PUBLIC_COPILOTKIT_API_KEY}
        >
          {children}
        </CopilotKit>
      </body>
    </html>
  );
}
```

### 2.2 Portfolio Analysis Action

```typescript
// hooks/usePortfolioAnalysisAction.ts
import { useCopilotAction } from "@copilotkit/react-core";
import { useCryptoStore } from "@/store/crypto-store";

export function usePortfolioAnalysisAction() {
  const portfolio = useCryptoStore((state) => state.portfolio);
  
  useCopilotAction({
    name: "analyzePortfolio",
    description: "Analyze your crypto portfolio for risk and performance",
    parameters: [
      {
        name: "timeframe",
        type: "string",
        description: "Analysis timeframe: day, week, month, year",
        enum: ["day", "week", "month", "year"],
      },
      {
        name: "riskLevel",
        type: "string",
        description: "Acceptable risk level",
        enum: ["conservative", "moderate", "aggressive"],
      },
    ],
    handler: async ({ timeframe, riskLevel }) => {
      // Send analysis request to backend
      const response = await fetch("/api/portfolio/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          portfolio,
          timeframe,
          riskLevel,
        }),
      });
      return response.json();
    },
  });
}
```

### 2.3 Trade Execution Action (Interactive)

```typescript
// hooks/useTradeExecutionAction.ts
import { useCopilotAction } from "@copilotkit/react-core";
import { useCryptoStore } from "@/store/crypto-store";
import { TradeConfirmation } from "@/components/TradeConfirmation";

export function useTradeExecutionAction() {
  const { addPendingTransaction } = useCryptoStore();
  
  useCopilotAction({
    name: "executeTrade",
    description: "Execute a cryptocurrency trade",
    parameters: [
      {
        name: "action",
        type: "string",
        description: "Buy or sell",
        enum: ["buy", "sell"],
        required: true,
      },
      {
        name: "symbol",
        type: "string",
        description: "Cryptocurrency symbol (BTC, ETH, etc)",
        required: true,
      },
      {
        name: "amount",
        type: "number",
        description: "Amount to trade",
        required: true,
      },
      {
        name: "targetPrice",
        type: "number",
        description: "Target execution price",
      },
      {
        name: "reason",
        type: "string",
        description: "AI reasoning for the trade",
      },
    ],
    renderAndWaitForResponse: ({ args, respond, status }) => {
      if (status === "complete") {
        return <div>Trade {status}!</div>;
      }
      
      return (
        <TradeConfirmation
          action={args.action}
          symbol={args.symbol}
          amount={args.amount}
          targetPrice={args.targetPrice}
          reason={args.reason}
          onConfirm={() => respond("confirmed")}
          onCancel={() => respond("cancelled")}
          onModify={(modified) => respond(`modified:${JSON.stringify(modified)}`)}
        />
      );
    },
  });
}
```

### 2.4 Risk Assessment CoAgent

```typescript
// hooks/useRiskAssessmentCoAgent.ts
import { useCoAgent } from "@copilotkit/react-core";

interface RiskAssessmentState {
  currentVAR: number; // Value at Risk
  correlationRisk: number;
  concentrationRisk: number;
  liquidityRisk: number;
  rebalancingSuggestions: Array<{
    asset: string;
    currentAllocation: number;
    suggestedAllocation: number;
  }>;
  overallRiskScore: number; // 0-100
}

export function useRiskAssessmentCoAgent() {
  const portfolio = useCryptoStore((state) => state.portfolio);
  
  const { state, setState, running } = useCoAgent<RiskAssessmentState>({
    name: "risk-assessor",
    initialState: {
      currentVAR: 0,
      correlationRisk: 0,
      concentrationRisk: 0,
      liquidityRisk: 0,
      rebalancingSuggestions: [],
      overallRiskScore: 0,
    },
  });
  
  return { state, setState, running };
}
```

---

## 3. Agent OS Pattern for Market Data Streaming

### 3.1 Market Stream Hook

```typescript
// hooks/useMarketDataStream.ts
import { useEffect, useRef } from 'react';
import { useCryptoStore } from '@/store/crypto-store';

interface MarketStreamEvent {
  event: string;
  symbol: string;
  price: number;
  change24h: number;
  volume24h: number;
  timestamp: number;
}

export function useMarketDataStream(symbols: string[]) {
  const { updateAssetPrice, setIsStreamingMarketData } = useCryptoStore();
  const eventSourceRef = useRef<EventSource | null>(null);
  
  useEffect(() => {
    if (!symbols.length) return;
    
    const queryParams = new URLSearchParams({
      symbols: symbols.join(','),
    });
    
    const eventSource = new EventSource(
      `/api/market-stream?${queryParams}`
    );
    eventSourceRef.current = eventSource;
    
    setIsStreamingMarketData(true);
    
    eventSource.onmessage = (event) => {
      try {
        const data: MarketStreamEvent = JSON.parse(event.data);
        
        switch (data.event) {
          case 'PRICE_UPDATE':
            updateAssetPrice(data.symbol, data.price, data.change24h);
            break;
          case 'VOLUME_SPIKE':
            // Handle volume spike event
            console.log(`Volume spike on ${data.symbol}`);
            break;
          case 'VOLATILITY_WARNING':
            // Handle volatility warning
            console.log(`Volatility warning on ${data.symbol}`);
            break;
        }
      } catch (error) {
        console.error('Failed to parse market stream event:', error);
      }
    };
    
    eventSource.onerror = (error) => {
      console.error('Market stream error:', error);
      setIsStreamingMarketData(false);
      eventSource.close();
    };
    
    return () => {
      eventSource.close();
      setIsStreamingMarketData(false);
    };
  }, [symbols, updateAssetPrice, setIsStreamingMarketData]);
}
```

### 3.2 Agent Stream Handler (like Agent OS)

```typescript
// api/market-stream/route.ts
import { NextRequest } from 'next/server';

export async function GET(request: NextRequest) {
  const symbols = request.nextUrl.searchParams.get('symbols')?.split(',') || [];
  
  const stream = new ReadableStream({
    async start(controller) {
      try {
        // Connect to Agno AgentOS instance
        const agentResponse = await fetch(
          `${process.env.AGENT_OS_ENDPOINT}/run`,
          {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${process.env.AGENT_OS_API_KEY}`,
            },
            body: JSON.stringify({
              agent_id: 'market-analyzer',
              session_id: request.headers.get('x-session-id'),
              message: `Monitor these symbols: ${symbols.join(', ')}`,
            }),
          }
        );
        
        if (!agentResponse.body) {
          throw new Error('No response body');
        }
        
        const reader = agentResponse.body.getReader();
        
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          
          const text = new TextDecoder().decode(value);
          const lines = text.split('\n');
          
          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const eventData = JSON.parse(line.slice(6));
              
              // Transform Agent OS RunResponseContent to MarketStreamEvent
              const marketEvent = transformAgentEvent(eventData);
              if (marketEvent) {
                controller.enqueue(
                  `data: ${JSON.stringify(marketEvent)}\n\n`
                );
              }
            }
          }
        }
        
        controller.close();
      } catch (error) {
        console.error('Stream error:', error);
        controller.error(error);
      }
    },
  });
  
  return new Response(stream, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive',
    },
  });
}

function transformAgentEvent(agentEvent: any) {
  // Map Agent OS RunResponseContent to market event
  switch (agentEvent.event) {
    case 'ToolCallCompleted':
      if (agentEvent.tool?.tool_name === 'get_price_data') {
        return {
          event: 'PRICE_UPDATE',
          symbol: agentEvent.tool.tool_args.symbol,
          price: agentEvent.tool.tool_args.price,
          change24h: agentEvent.tool.tool_args.change24h,
          volume24h: agentEvent.tool.tool_args.volume24h,
          timestamp: agentEvent.created_at,
        };
      }
      break;
      
    case 'RunContent':
      if (agentEvent.content?.includes('volume spike')) {
        return {
          event: 'VOLUME_SPIKE',
          message: agentEvent.content,
          timestamp: agentEvent.created_at,
        };
      }
      break;
      
    case 'ReasoningStep':
      if (agentEvent.event_data?.reasoning?.includes('volatility')) {
        return {
          event: 'VOLATILITY_WARNING',
          reasoning: agentEvent.event_data.reasoning,
          timestamp: agentEvent.created_at,
        };
      }
      break;
  }
  
  return null;
}
```

---

## 4. UI Components

### 4.1 Portfolio Dashboard with Agent Insights

```typescript
// components/PortfolioDashboard.tsx
'use client';

import { usePortfolioAnalysisAction } from '@/hooks/usePortfolioAnalysisAction';
import { useRiskAssessmentCoAgent } from '@/hooks/useRiskAssessmentCoAgent';
import { useTradeExecutionAction } from '@/hooks/useTradeExecutionAction';
import { useCryptoStore } from '@/store/crypto-store';
import { CopilotChat } from '@copilotkit/react-ui';

export function PortfolioDashboard() {
  const portfolio = useCryptoStore((state) => state.portfolio);
  const marketData = useCryptoStore((state) => state.marketData);
  const { state: riskState } = useRiskAssessmentCoAgent();
  
  usePortfolioAnalysisAction();
  useTradeExecutionAction();
  
  return (
    <div className="grid grid-cols-3 gap-6">
      {/* Portfolio Overview */}
      <div className="col-span-2">
        <PortfolioCards portfolio={portfolio} marketData={marketData} />
        
        {/* Risk Assessment CoAgent */}
        <RiskAssessmentPanel riskState={riskState} />
      </div>
      
      {/* Agent Chat Sidebar */}
      <div className="border-l">
        <CopilotChat
          labels={{
            initial: 'Analyze my portfolio',
          }}
          instructions="You are a crypto portfolio advisor. Help users understand their holdings, suggest rebalancing, and execute trades with confirmation."
        />
      </div>
    </div>
  );
}
```

### 4.2 Market Data Stream Display

```typescript
// components/MarketDataStream.tsx
'use client';

import { useMarketDataStream } from '@/hooks/useMarketDataStream';
import { useCryptoStore } from '@/store/crypto-store';
import { useEffect, useState } from 'react';

export function MarketDataStream() {
  const portfolio = useCryptoStore((state) => state.portfolio);
  const marketData = useCryptoStore((state) => state.marketData);
  const isStreaming = useCryptoStore((state) => state.isStreamingMarketData);
  const [priceAlerts, setPriceAlerts] = useState<Array<{
    symbol: string;
    event: string;
    timestamp: number;
  }>>([]);
  
  const symbols = portfolio?.assets.map((a) => a.symbol) || [];
  useMarketDataStream(symbols);
  
  useEffect(() => {
    // Show toast notifications for price changes
    Object.entries(marketData).forEach(([symbol, data]) => {
      if (Math.abs(data.change24h) > 5) {
        setPriceAlerts((prev) => [
          ...prev.slice(-4),
          {
            symbol,
            event: data.change24h > 0 ? 'spike' : 'drop',
            timestamp: Date.now(),
          },
        ]);
      }
    });
  }, [marketData]);
  
  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <div className={`h-3 w-3 rounded-full ${isStreaming ? 'bg-green-500 animate-pulse' : 'bg-gray-400'}`} />
        <span>{isStreaming ? 'Live updates' : 'No stream'}</span>
      </div>
      
      <div className="grid grid-cols-1 gap-2">
        {priceAlerts.map((alert, i) => (
          <div key={i} className={`p-3 rounded text-sm ${alert.event === 'spike' ? 'bg-red-100' : 'bg-green-100'}`}>
            {alert.symbol}: {alert.event === 'spike' ? 'Price spike' : 'Price drop'}
          </div>
        ))}
      </div>
    </div>
  );
}
```

---

## 5. Backend Agent Implementation (Node.js + LangChain)

### 5.1 Portfolio Analysis Agent

```typescript
// server/agents/portfolio-analyzer.ts
import { defineAgent } from "@langchain/langgraph";
import { Tool } from "langchain/tools";

class GetPortfolioTool extends Tool {
  name = "get_portfolio";
  description = "Get user's current portfolio holdings";
  
  async _call(input: string) {
    const userId = input;
    const portfolio = await db.portfolio.findUnique({
      where: { userId },
      include: { assets: true },
    });
    return JSON.stringify(portfolio);
  }
}

class AnalyzePriceDataTool extends Tool {
  name = "analyze_prices";
  description = "Analyze price movements and trends";
  
  async _call(input: string) {
    const { symbols, timeframe } = JSON.parse(input);
    const priceData = await coingecko.getPriceHistory(symbols, timeframe);
    return JSON.stringify(priceData);
  }
}

export const portfolioAnalyzerAgent = defineAgent({
  name: "portfolio-analyzer",
  tools: [new GetPortfolioTool(), new AnalyzePriceDataTool()],
  systemPrompt: `You are a cryptocurrency portfolio analyst. Analyze user portfolios using available tools and provide:
1. Performance analysis
2. Risk assessment
3. Rebalancing suggestions
4. Market opportunity insights`,
});
```

### 5.2 Market Stream Agent

```typescript
// server/agents/market-streamer.ts
import { Readable } from "stream";
import { RunEvent } from "@/types/os";

export async function streamMarketData(
  agentOsEndpoint: string,
  symbols: string[],
): Promise<Readable> {
  const stream = new Readable();
  
  (async () => {
    try {
      const response = await fetch(`${agentOsEndpoint}/run`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${process.env.AGENT_OS_KEY}`,
        },
        body: JSON.stringify({
          agent_id: "market-monitor",
          message: `Monitor real-time data for: ${symbols.join(", ")}`,
        }),
      });
      
      if (!response.body) throw new Error("No response body");
      
      const reader = response.body.getReader();
      
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const text = new TextDecoder().decode(value);
        const events = parseServerSentEvents(text);
        
        for (const event of events) {
          // Filter for price updates
          if (event.event === RunEvent.ToolCallCompleted) {
            stream.push(
              `data: ${JSON.stringify({
                event: 'PRICE_UPDATE',
                ...event,
              })}\n\n`
            );
          }
          
          // Filter for reasoning steps
          if (event.event === RunEvent.ReasoningStep) {
            stream.push(
              `data: ${JSON.stringify({
                event: 'REASONING',
                ...event,
              })}\n\n`
            );
          }
        }
      }
      
      stream.push(null);
    } catch (error) {
      stream.destroy(error);
    }
  })();
  
  return stream;
}

function parseServerSentEvents(text: string) {
  return text
    .split('\n')
    .filter(line => line.startsWith('data: '))
    .map(line => JSON.parse(line.slice(6)));
}
```

---

## 6. Authentication & Security

### 6.1 Protected Agent Endpoints

```typescript
// app/api/copilotkit/route.ts
import { CopilotBackend } from "@copilotkit/backend";
import { authMiddleware } from "@/lib/auth";

const copilotBackend = new CopilotBackend({
  actions: [
    {
      name: "executeTrade",
      description: "Execute a cryptocurrency trade",
      handler: async (input: any, context: any) => {
        // Verify user authentication
        const user = await authMiddleware(context);
        if (!user) throw new Error("Unauthorized");
        
        // Verify trade limits
        const tradeAmount = input.amount * input.targetPrice;
        const userLimits = await db.tradeLimits.findUnique({
          where: { userId: user.id },
        });
        
        if (tradeAmount > userLimits.dailyLimit) {
          throw new Error("Trade exceeds daily limit");
        }
        
        // Process trade
        return await processTradeWithAPI(input, user);
      },
    },
  ],
});

export async function POST(request: Request) {
  return copilotBackend.handleRequest(request);
}
```

### 6.2 API Key Management

```typescript
// Environment variables
NEXT_PUBLIC_COPILOTKIT_RUNTIME_URL=http://localhost:3001/api/copilotkit
NEXT_PUBLIC_COPILOTKIT_API_KEY=pk_xxx_xxx
AGENT_OS_ENDPOINT=http://localhost:7777
AGENT_OS_API_KEY=sk_xxx_xxx
COINGECKO_API_KEY=cg_xxx_xxx
```

---

## 7. Error Handling & Observability

### 7.1 Error Boundaries

```typescript
// hooks/useAgentErrorHandler.ts
import { useCopilotKit } from "@copilotkit/react-core";

export function useAgentErrorHandler() {
  const { onError } = useCopilotKit();
  
  return {
    handleActionError: (error: Error, actionName: string) => {
      onError(error, {
        message: `Error in ${actionName}: ${error.message}`,
        severity: "error",
      });
      
      // Log to monitoring service
      logToMonitoring({
        event: "agent_action_error",
        action: actionName,
        error: error.message,
        timestamp: Date.now(),
      });
    },
    
    handleStreamError: (error: Error) => {
      onError(error, {
        message: "Market stream disconnected",
        severity: "warning",
      });
      
      // Attempt reconnection
      setTimeout(() => {
        // Reconnect logic
      }, 5000);
    },
  };
}
```

### 7.2 Monitoring & Logging

```typescript
// lib/monitoring.ts
export async function logToMonitoring(event: any) {
  if (process.env.NEXT_PUBLIC_MONITORING_ENABLED !== 'true') return;
  
  await fetch(process.env.NEXT_PUBLIC_MONITORING_ENDPOINT!, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      ...event,
      environment: process.env.NODE_ENV,
      version: process.env.NEXT_PUBLIC_APP_VERSION,
    }),
  });
}
```

---

## 8. Testing Agents

### 8.1 Unit Tests

```typescript
// __tests__/agents/portfolio-analyzer.test.ts
import { portfolioAnalyzerAgent } from '@/server/agents/portfolio-analyzer';

describe('Portfolio Analyzer Agent', () => {
  it('should analyze portfolio correctly', async () => {
    const portfolio = {
      assets: [
        { symbol: 'BTC', amount: 1, entryPrice: 50000 },
        { symbol: 'ETH', amount: 10, entryPrice: 3000 },
      ],
    };
    
    const analysis = await portfolioAnalyzerAgent.run({
      input: `Analyze this portfolio: ${JSON.stringify(portfolio)}`,
    });
    
    expect(analysis).toContain('risk');
    expect(analysis).toContain('recommendation');
  });
  
  it('should suggest rebalancing', async () => {
    // Test rebalancing logic
  });
});
```

### 8.2 Integration Tests

```typescript
// __tests__/integration/market-stream.test.ts
import { streamMarketData } from '@/server/agents/market-streamer';

describe('Market Stream Integration', () => {
  it('should stream market data correctly', async () => {
    const stream = await streamMarketData(
      'http://localhost:7777',
      ['BTC', 'ETH']
    );
    
    const events = [];
    for await (const chunk of stream) {
      events.push(JSON.parse(chunk.toString()));
    }
    
    expect(events).toHaveLength(greaterThan(0));
    expect(events[0]).toHaveProperty('event');
  });
});
```

---

## Summary

This integration guide combines:

1. **CopilotKit** for intelligent action orchestration and generative UI
2. **Zustand** for crypto-specific state management
3. **Agent OS pattern** for real-time data streaming and event-driven architecture
4. **SSE/EventSource** for market data subscriptions
5. **Type-safe interfaces** for all agent communications

The architecture is scalable, maintainable, and provides excellent UX for crypto trading and portfolio management.

