import { createFileRoute } from "@tanstack/react-router";
import {
  Bot,
  Send,
  User,
  Square,
  Trash2,
  Wrench,
  CheckCircle2,
  XCircle,
  Loader2,
  AlertCircle,
} from "lucide-react";
import { useState } from "react";
import { useAgentChat } from "@/hooks/useAgentChat";
import type { ToolCall } from "@/lib/agui/types";

export const Route = createFileRoute("/admin/agents/chat")({
  component: ChatPage,
  validateSearch: (search: Record<string, unknown>) => ({
    agent: (search.agent as string) || "portal",
  }),
});

function ChatPage() {
  const { agent } = Route.useSearch();
  const [input, setInput] = useState("");

  const {
    messages,
    currentText,
    toolCalls,
    state,
    error,
    sendMessage,
    stop,
    clearMessages,
    isRunning,
  } = useAgentChat({
    endpoint: "/api/agent",
  });

  const agentNames: Record<string, string> = {
    portal: "Portal Agent",
    tuath: "Tuath Agent",
    crypteolas: "Crypteolas Agent",
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isRunning) return;

    sendMessage(input);
    setInput("");
  };

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="border-b p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-primary/10 rounded-full flex items-center justify-center">
              <Bot className="text-primary" size={20} />
            </div>
            <div>
              <h1 className="font-semibold">{agentNames[agent] || "Agent"}</h1>
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <span
                  className={`w-2 h-2 rounded-full ${isRunning ? "bg-yellow-500 animate-pulse" : "bg-status-healthy"}`}
                />
                {isRunning ? "Processing..." : "Connected"}
                {state.currentStep && (
                  <span className="text-xs">({state.currentStep.name})</span>
                )}
              </div>
            </div>
          </div>
          <button
            onClick={clearMessages}
            className="p-2 hover:bg-secondary rounded-lg"
            title="Clear chat"
          >
            <Trash2 size={18} />
          </button>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-auto p-4 space-y-4">
        {messages.length === 0 && !currentText && (
          <div className="text-center text-muted-foreground py-8">
            <Bot size={48} className="mx-auto mb-4 opacity-50" />
            <p>Start a conversation with the {agentNames[agent]}</p>
            <p className="text-sm mt-2">
              Try asking about stacks, searching data, or extracting web content
            </p>
          </div>
        )}

        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex gap-3 ${message.role === "user" ? "justify-end" : ""}`}
          >
            {message.role === "assistant" && (
              <div className="w-8 h-8 bg-primary/10 rounded-full flex items-center justify-center shrink-0">
                <Bot className="text-primary" size={16} />
              </div>
            )}
            <div className="flex flex-col gap-2 max-w-[80%]">
              <div className={`chat-message ${message.role}`}>
                {message.content}
              </div>
              {message.toolCalls && message.toolCalls.length > 0 && (
                <div className="space-y-1">
                  {message.toolCalls.map((tool) => (
                    <ToolCallDisplay key={tool.id} tool={tool} />
                  ))}
                </div>
              )}
            </div>
            {message.role === "user" && (
              <div className="w-8 h-8 bg-secondary rounded-full flex items-center justify-center shrink-0">
                <User size={16} />
              </div>
            )}
          </div>
        ))}

        {/* Currently streaming text */}
        {currentText && (
          <div className="flex gap-3">
            <div className="w-8 h-8 bg-primary/10 rounded-full flex items-center justify-center shrink-0">
              <Bot className="text-primary" size={16} />
            </div>
            <div className="chat-message assistant">
              {currentText}
              <span className="inline-block w-1 h-4 bg-primary ml-1 animate-pulse" />
            </div>
          </div>
        )}

        {/* Active tool calls */}
        {toolCalls.length > 0 && (
          <div className="flex gap-3">
            <div className="w-8 h-8 bg-primary/10 rounded-full flex items-center justify-center shrink-0">
              <Wrench className="text-primary" size={16} />
            </div>
            <div className="space-y-1">
              {toolCalls.map((tool) => (
                <ToolCallDisplay key={tool.id} tool={tool} />
              ))}
            </div>
          </div>
        )}

        {/* Loading indicator when running but no text yet */}
        {isRunning && !currentText && toolCalls.length === 0 && (
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

        {/* Error display */}
        {error && (
          <div className="flex gap-3">
            <div className="w-8 h-8 bg-red-500/10 rounded-full flex items-center justify-center shrink-0">
              <AlertCircle className="text-red-500" size={16} />
            </div>
            <div className="chat-message bg-red-500/10 text-red-500">
              Error: {error}
            </div>
          </div>
        )}
      </div>

      {/* Input */}
      <form onSubmit={handleSubmit} className="border-t p-4">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your message..."
            className="flex-1 bg-secondary rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary"
            disabled={isRunning}
          />
          {isRunning ? (
            <button
              type="button"
              onClick={stop}
              className="bg-red-500 text-white px-4 py-2 rounded-lg hover:bg-red-600"
            >
              <Square size={18} />
            </button>
          ) : (
            <button
              type="submit"
              disabled={!input.trim()}
              className="bg-primary text-primary-foreground px-4 py-2 rounded-lg hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Send size={18} />
            </button>
          )}
        </div>
      </form>
    </div>
  );
}

function ToolCallDisplay({ tool }: { tool: ToolCall }) {
  const statusIcon = {
    pending: <Loader2 size={14} className="animate-spin" />,
    running: <Loader2 size={14} className="animate-spin text-yellow-500" />,
    completed: <CheckCircle2 size={14} className="text-green-500" />,
    error: <XCircle size={14} className="text-red-500" />,
  };

  return (
    <div className="flex items-center gap-2 text-sm bg-secondary/50 rounded px-2 py-1">
      {statusIcon[tool.status]}
      <span className="font-mono">{tool.name}</span>
      {tool.arguments && (
        <span className="text-muted-foreground truncate max-w-[200px]">
          ({JSON.stringify(tool.arguments).slice(0, 50)}...)
        </span>
      )}
    </div>
  );
}
