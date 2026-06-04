import { createFileRoute } from "@tanstack/react-router";
import { useCopilotChat } from "@copilotkit/react-core";
import { useState, useRef, useEffect } from "react";
import { cn } from "../lib/utils";
import { useX402 } from "../lib/x402/provider";
import { useUsageStore } from "../stores/usage";
import { getFeaturePricing } from "../lib/x402/pricing";
import { MessageSquare, Coins, AlertTriangle } from "lucide-react";

export const Route = createFileRoute("/chat")({
  component: ChatPage,
});

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  sources?: { title: string; type: string }[];
}

function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      role: "assistant",
      content:
        "Hello! I'm your crypto research assistant. I can help you analyze DeFi protocols, understand tokenomics, review audit reports, and explore the knowledge graph. What would you like to know?",
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [paymentPending, setPaymentPending] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // x402 payment integration
  const { requestPayment, needsPayment } = useX402();
  const { getRemainingFree, incrementUsage } = useUsageStore();

  const chatPricing = getFeaturePricing("chat_message");
  const remainingFree = getRemainingFree("chat_message");
  const requiresPayment = needsPayment("chat_message");

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    // Check if payment is required
    if (requiresPayment) {
      setPaymentPending(true);
      requestPayment({
        featureId: "chat_message",
        resourceUrl: "/api/copilot",
        description: "Send a message to the AI assistant",
        onSuccess: (txHash) => {
          setPaymentPending(false);
          // Continue with message send after payment
          sendMessage(input);
        },
        onError: (error) => {
          setPaymentPending(false);
          // Show error - could add toast notification here
          console.error("Payment failed:", error);
        },
      });
      return;
    }

    // Free tier - send directly
    sendMessage(input);
  };

  const sendMessage = async (messageContent: string) => {
    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: "user",
      content: messageContent,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    // Increment usage for free tier tracking
    if (!requiresPayment) {
      incrementUsage("chat_message");
    }

    // Simulate AI response (replace with actual CopilotKit integration)
    setTimeout(() => {
      const assistantMessage: Message = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: getMockResponse(messageContent),
        timestamp: new Date(),
        sources: getMockSources(messageContent),
      };
      setMessages((prev) => [...prev, assistantMessage]);
      setIsLoading(false);
    }, 1500);
  };

  return (
    <div className="flex h-[calc(100vh-4rem)] flex-col">
      {/* Chat Header */}
      <div className="border-b p-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold">Research Assistant</h1>
            <p className="text-sm text-muted-foreground">
              Ask questions about DeFi protocols, audits, and market analysis
            </p>
          </div>
          {/* Usage indicator */}
          <div className="flex items-center gap-4">
            <div className={cn(
              "flex items-center gap-2 rounded-full px-3 py-1 text-sm",
              remainingFree > 0
                ? "bg-green-500/10 text-green-600"
                : "bg-yellow-500/10 text-yellow-600"
            )}>
              <MessageSquare className="h-4 w-4" />
              {remainingFree > 0 ? (
                <span>{remainingFree} free messages left</span>
              ) : (
                <span className="flex items-center gap-1">
                  <Coins className="h-3 w-3" />
                  {chatPricing?.priceUsd}/message
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Payment warning banner */}
        {requiresPayment && (
          <div className="mt-3 flex items-center gap-2 rounded-lg border border-yellow-500/50 bg-yellow-500/10 p-3 text-sm">
            <AlertTriangle className="h-4 w-4 text-yellow-500" />
            <span>
              Free tier exhausted. Messages now cost {chatPricing?.priceUsd} each (paid via x402 on Cronos).
            </span>
          </div>
        )}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={cn(
              "flex",
              message.role === "user" ? "justify-end" : "justify-start"
            )}
          >
            <div
              className={cn(
                "max-w-[80%] rounded-lg p-4",
                message.role === "user"
                  ? "bg-primary text-primary-foreground"
                  : "bg-muted"
              )}
            >
              <p className="whitespace-pre-wrap">{message.content}</p>
              {message.sources && message.sources.length > 0 && (
                <div className="mt-3 pt-3 border-t border-border/50">
                  <p className="text-xs font-medium mb-2">Sources:</p>
                  <div className="flex flex-wrap gap-2">
                    {message.sources.map((source, i) => (
                      <span
                        key={i}
                        className="inline-flex items-center gap-1 rounded bg-background/50 px-2 py-1 text-xs"
                      >
                        <span className="text-muted-foreground">
                          {source.type}:
                        </span>
                        {source.title}
                      </span>
                    ))}
                  </div>
                </div>
              )}
              <p className="mt-2 text-xs opacity-50">
                {message.timestamp.toLocaleTimeString()}
              </p>
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-muted rounded-lg p-4">
              <div className="flex gap-1">
                <span className="animate-bounce">.</span>
                <span className="animate-bounce delay-100">.</span>
                <span className="animate-bounce delay-200">.</span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <form onSubmit={handleSubmit} className="border-t p-4">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about protocols, audits, or market trends..."
            className="flex-1 rounded-lg border bg-background px-4 py-2 focus:outline-none focus:ring-2 focus:ring-ring"
            disabled={paymentPending}
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim() || paymentPending}
            className={cn(
              "rounded-lg px-6 py-2 font-medium transition-colors disabled:opacity-50",
              requiresPayment
                ? "bg-yellow-500 text-black hover:bg-yellow-400"
                : "bg-primary text-primary-foreground hover:bg-primary/90"
            )}
          >
            {paymentPending ? (
              "Awaiting Payment..."
            ) : requiresPayment ? (
              <span className="flex items-center gap-1">
                <Coins className="h-4 w-4" />
                Pay & Send
              </span>
            ) : (
              "Send"
            )}
          </button>
        </div>
        <div className="mt-2 flex gap-2">
          {["Explain USDe", "Ethena risks", "Best yield strategies"].map(
            (suggestion) => (
              <button
                key={suggestion}
                type="button"
                onClick={() => setInput(suggestion)}
                className="rounded-full border px-3 py-1 text-sm hover:bg-muted"
              >
                {suggestion}
              </button>
            )
          )}
        </div>
      </form>
    </div>
  );
}

function getMockResponse(input: string): string {
  const lower = input.toLowerCase();

  if (lower.includes("usde") || lower.includes("ethena")) {
    return `**Ethena USDe Overview**

USDe is a synthetic dollar protocol by Ethena Labs that maintains its peg through delta-neutral hedging:

**Mechanism:**
- Users deposit stETH or other LSTs as collateral
- Protocol opens corresponding short perpetual positions
- The combination creates a delta-neutral position yielding ~25-35% APY

**Key Risks:**
1. **Funding Rate Risk**: Negative funding can erode yields
2. **Custodial Risk**: Relies on centralized exchanges for hedging
3. **Smart Contract Risk**: Complex interactions with multiple protocols

**Current Metrics:**
- TVL: $2.8B
- sUSDe APY: 27.4%
- Peg stability: 0.9998 - 1.0002 range

The protocol has been audited by Zellic and Spearbit with no critical issues found.`;
  }

  if (lower.includes("risk")) {
    return `**DeFi Risk Assessment Framework**

When evaluating protocol risks, consider these categories:

**1. Smart Contract Risk**
- Audit coverage and quality
- Time in production
- Bug bounty programs

**2. Economic/Mechanism Risk**
- Peg stability mechanisms
- Liquidation cascades
- Oracle dependencies

**3. Governance Risk**
- Token distribution
- Multisig configuration
- Upgrade mechanisms

**4. Counterparty Risk**
- Centralized dependencies
- Bridge risks
- Custodial exposure

For Ethena specifically, the main risks are funding rate volatility and CEX counterparty exposure.`;
  }

  if (lower.includes("yield") || lower.includes("strategy")) {
    return `**Current High-Yield Strategies**

Based on our knowledge graph analysis:

**1. sUSDe Staking (27.4% APY)**
- Protocol: Ethena
- Risk: Medium-High
- Lock: None

**2. Pendle PT-sUSDe (32.1% APY)**
- Fixed yield until maturity
- Risk: Medium
- Maturity: March 2025

**3. Aave sUSDe Looping**
- Leveraged sUSDe position
- APY: 40-60% (variable)
- Risk: High (liquidation)

**4. Curve USDe-USDC LP**
- APY: 8-12%
- Risk: Low-Medium
- IL exposure minimal

Always assess your risk tolerance and diversify across strategies.`;
  }

  return `I understand you're asking about "${input}".

Based on the indexed documents and knowledge graph, I can help analyze:
- DeFi protocol mechanics and risks
- Token economics and valuations
- Audit reports and security assessments
- Yield farming strategies
- Market trends and correlations

Could you provide more specific details about what aspect you'd like to explore? For example:
- Protocol name or token symbol
- Specific risk category
- Investment timeframe`;
}

function getMockSources(input: string): { title: string; type: string }[] {
  const lower = input.toLowerCase();

  if (lower.includes("usde") || lower.includes("ethena")) {
    return [
      { title: "Ethena Whitepaper", type: "Document" },
      { title: "Zellic Audit Report", type: "Audit" },
      { title: "DeFiLlama TVL Data", type: "API" },
    ];
  }

  if (lower.includes("risk")) {
    return [
      { title: "Risk Framework v2.1", type: "Document" },
      { title: "Protocol Knowledge Graph", type: "Graph" },
    ];
  }

  if (lower.includes("yield") || lower.includes("strategy")) {
    return [
      { title: "Yield Aggregator Data", type: "API" },
      { title: "Protocol Integrations", type: "Graph" },
      { title: "DeFi Strategy Docs", type: "Document" },
    ];
  }

  return [];
}
