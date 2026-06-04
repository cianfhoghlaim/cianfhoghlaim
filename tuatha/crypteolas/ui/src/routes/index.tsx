/**
 * Crypteolas Agent - Human-in-the-Loop RAG Interface.
 *
 * Split layout with chunk approval panel and chat sidebar.
 * Integrates with AG-UI protocol for bidirectional state sync.
 */

import { createFileRoute } from "@tanstack/react-router";
import {
  Bot,
  Clock,
  PanelLeftClose,
  PanelLeftOpen,
  RefreshCw,
  Send,
  User,
  Wifi,
  WifiOff,
} from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { ChunkApproval } from "../components/copilot/ChunkApproval";
import { CitationList, InlineCitations } from "../components/copilot/CitationCard";
import { SearchConfigPanel } from "../components/copilot/SearchConfigPanel";
import { useCoAgentRest } from "../lib/hooks/useCoAgent";
import type { Citation } from "../lib/types";

export const Route = createFileRoute("/")({
  component: CrypteolasAgentPage,
});

// Available protocols for filtering
const AVAILABLE_PROTOCOLS = [
  "uniswap",
  "aave",
  "compound",
  "curve",
  "balancer",
  "lido",
  "makerdao",
  "yearn",
  "convex",
];

const AVAILABLE_LANGUAGES = [
  "python",
  "typescript",
  "solidity",
  "rust",
  "go",
];

function CrypteolasAgentPage() {
  const [isPanelCollapsed, setIsPanelCollapsed] = useState(false);
  const [input, setInput] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // AG-UI agent hook - using REST fallback for demo
  const {
    state,
    messages,
    isConnected,
    isLoading,
    error,
    sendMessage,
    approveChunk,
    rejectChunk,
    approveAll,
    updateSearchConfig,
    clearSearch,
    reconnect,
  } = useCoAgentRest({
    agentUrl: import.meta.env.VITE_API_URL || "http://localhost:8001",
    agentName: "crypteolas",
    onStateChange: (newState) => {
      console.log("State changed:", newState);
    },
    onError: (err) => {
      console.error("Agent error:", err);
    },
  });

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    await sendMessage(input);
    setInput("");
  };

  const handleCitationClick = (citation: Citation) => {
    // Scroll to and highlight the chunk in the panel
    const chunkElement = document.getElementById("chunk-" + citation.chunk_id);
    if (chunkElement) {
      chunkElement.scrollIntoView({ behavior: "smooth" });
      chunkElement.classList.add("ring-2", "ring-primary");
      setTimeout(() => {
        chunkElement.classList.remove("ring-2", "ring-primary");
      }, 2000);
    }
  };

  return (
    <div className="flex h-screen">
      {/* Left Panel - Chunks & Config */}
      <div
        className={"border-r bg-background flex flex-col transition-all duration-300 " +
          (isPanelCollapsed ? "w-0 overflow-hidden" : "w-[400px]")
        }
      >
        {/* Search config */}
        <div className="p-3 border-b">
          <SearchConfigPanel
            config={state.searchConfig}
            onChange={updateSearchConfig}
            availableProtocols={AVAILABLE_PROTOCOLS}
            availableLanguages={AVAILABLE_LANGUAGES}
            collapsed={true}
          />
        </div>

        {/* Chunk approval */}
        <div className="flex-1 overflow-hidden">
          <ChunkApproval
            chunks={state.chunks}
            approvedChunks={state.approvedChunks}
            rejectedChunks={state.rejectedChunks}
            awaitingApproval={state.awaitingApproval}
            onApprove={approveChunk}
            onReject={rejectChunk}
            onApproveAll={approveAll}
            onClear={clearSearch}
          />
        </div>

        {/* Search stats */}
        {state.searchLatencyMs && (
          <div className="px-3 py-2 border-t text-xs text-muted-foreground flex items-center gap-2">
            <Clock size={12} />
            Search: {state.searchLatencyMs.toFixed(0)}ms
            <span className="mx-1">|</span>
            {state.totalChunksFound} results
          </div>
        )}
      </div>

      {/* Right Panel - Chat */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between border-b p-4">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setIsPanelCollapsed(!isPanelCollapsed)}
              className="p-2 hover:bg-muted rounded-lg"
              title={isPanelCollapsed ? "Show chunks panel" : "Hide chunks panel"}
            >
              {isPanelCollapsed ? (
                <PanelLeftOpen size={18} />
              ) : (
                <PanelLeftClose size={18} />
              )}
            </button>
            <div className="w-10 h-10 bg-primary/10 rounded-full flex items-center justify-center">
              <Bot className="text-primary" size={20} />
            </div>
            <div>
              <h1 className="font-semibold">Crypteolas</h1>
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                {isConnected ? (
                  <>
                    <Wifi size={12} className="text-green-500" />
                    <span>Connected</span>
                  </>
                ) : (
                  <>
                    <WifiOff size={12} className="text-red-500" />
                    <span>Disconnected</span>
                    <button
                      onClick={reconnect}
                      className="text-primary hover:underline"
                    >
                      <RefreshCw size={12} />
                    </button>
                  </>
                )}
              </div>
            </div>
          </div>

          {error && (
            <div className="px-3 py-1 text-xs text-red-500 bg-red-500/10 rounded">
              {error.message}
            </div>
          )}
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-auto p-4 space-y-4">
          {/* Welcome message */}
          {messages.length === 0 && (
            <div className="flex gap-3">
              <div className="w-8 h-8 bg-primary/10 rounded-full flex items-center justify-center shrink-0">
                <Bot className="text-primary" size={16} />
              </div>
              <div className="chat-message assistant">
                <p>
                  Welcome to the Crypteolas research agent! I can help you explore
                  DeFi protocols, analyze smart contracts, and research crypto
                  documentation.
                </p>
                <p className="mt-2">
                  When I search the knowledge base, you will see retrieved chunks in
                  the left panel. <strong>Approve</strong> the relevant ones, then
                  I will use only those sources to answer your question.
                </p>
                <p className="mt-2 text-muted-foreground text-sm">
                  Try asking: How does Uniswap v4 hook system work? or Explain
                  Aave flash loan mechanism
                </p>
              </div>
            </div>
          )}

          {messages.map((message) => (
            <div
              key={message.id}
              className={"flex gap-3 " + (message.role === "user" ? "justify-end" : "")}
            >
              {message.role === "assistant" && (
                <div className="w-8 h-8 bg-primary/10 rounded-full flex items-center justify-center shrink-0">
                  <Bot className="text-primary" size={16} />
                </div>
              )}
              <div className={"chat-message " + message.role}>
                <div className="whitespace-pre-wrap">{message.content}</div>
                {/* Show inline citations for assistant messages */}
                {message.role === "assistant" && state.citations.length > 0 && (
                  <InlineCitations
                    citations={state.citations}
                    onCitationClick={handleCitationClick}
                  />
                )}
              </div>
              {message.role === "user" && (
                <div className="w-8 h-8 bg-secondary rounded-full flex items-center justify-center shrink-0">
                  <User size={16} />
                </div>
              )}
            </div>
          ))}

          {/* Loading indicator */}
          {isLoading && (
            <div className="flex gap-3">
              <div className="w-8 h-8 bg-primary/10 rounded-full flex items-center justify-center shrink-0">
                <Bot className="text-primary" size={16} />
              </div>
              <div className="chat-message assistant">
                <div className="flex gap-1">
                  <span className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" />
                  <span className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce [animation-delay:0.1s]" />
                  <span className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce [animation-delay:0.2s]" />
                </div>
              </div>
            </div>
          )}

          {/* HITL waiting indicator */}
          {state.awaitingApproval && !isLoading && (
            <div className="flex items-center justify-center py-4">
              <div className="flex items-center gap-2 px-4 py-2 bg-amber-500/10 text-amber-600 dark:text-amber-400 rounded-full text-sm">
                <RefreshCw size={14} className="animate-spin" />
                Waiting for chunk approval...
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Citations panel (collapsed by default) */}
        {state.citations.length > 0 && !state.awaitingApproval && (
          <div className="border-t p-4 max-h-48 overflow-auto">
            <CitationList
              citations={state.citations}
              onCitationClick={handleCitationClick}
            />
          </div>
        )}

        {/* Input */}
        <form onSubmit={handleSubmit} className="border-t p-4">
          <div className="flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={
                state.awaitingApproval
                  ? "Approve chunks above to continue..."
                  : "Ask about DeFi protocols, smart contracts..."
              }
              className="flex-1 bg-secondary rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary disabled:opacity-50"
              disabled={isLoading || state.awaitingApproval}
            />
            <button
              type="submit"
              disabled={isLoading || !input.trim() || state.awaitingApproval}
              className="bg-primary text-primary-foreground px-4 py-2 rounded-lg hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Send size={18} />
            </button>
          </div>
          {state.query && (
            <div className="mt-2 text-xs text-muted-foreground">
              Current query: {state.query}
            </div>
          )}
        </form>
      </div>
    </div>
  );
}
