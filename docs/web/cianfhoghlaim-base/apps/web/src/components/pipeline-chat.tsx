/**
 * Pipeline Chat Component
 *
 * Interactive chat interface for FastAPI agent conversations.
 * Uses SSE streaming for real-time responses.
 */

import { useState } from "react";
import { Send, StopCircle, Trash2 } from "lucide-react";
import { Streamdown } from "streamdown";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { usePipelineStream } from "@/hooks/use-pipeline-stream";
import type { Message, ToolCall } from "@/hooks/use-pipeline-stream";

// =============================================================================
// Sub-components
// =============================================================================

function MessageBubble({
  message,
  isStreaming,
}: {
  message: Message;
  isStreaming: boolean;
}) {
  const isUser = message.role === "user";

  return (
    <div
      className={`flex ${isUser ? "justify-end" : "justify-start"} mb-4`}
    >
      <div
        className={`max-w-[80%] rounded-lg p-3 ${
          isUser
            ? "bg-primary text-primary-foreground"
            : "bg-muted"
        }`}
      >
        <div className="text-sm font-semibold mb-1">
          {isUser ? "You" : "AI Assistant"}
        </div>

        {message.content ? (
          <Streamdown
            isAnimating={isStreaming && message.isStreaming}
          >
            {message.content}
          </Streamdown>
        ) : message.isStreaming ? (
          <span className="animate-pulse">Thinking...</span>
        ) : null}

        {message.toolCalls && message.toolCalls.length > 0 && (
          <div className="mt-2 border-t pt-2">
            <div className="text-xs font-semibold text-muted-foreground mb-1">
              Tools Used:
            </div>
            {message.toolCalls.map((tool) => (
              <ToolCallBadge key={tool.id} toolCall={tool} />
            ))}
          </div>
        )}

        {message.sources && message.sources.length > 0 && (
          <div className="mt-2 border-t pt-2">
            <div className="text-xs font-semibold text-muted-foreground mb-1">
              Sources:
            </div>
            <div className="space-y-1">
              {message.sources.map((source) => (
                <a
                  key={source.id}
                  href={source.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="block text-xs text-blue-600 hover:underline"
                >
                  {source.title}
                </a>
              ))}
            </div>
          </div>
        )}

        <div className="text-xs text-muted-foreground mt-1">
          {message.timestamp.toLocaleTimeString()}
        </div>
      </div>
    </div>
  );
}

function ToolCallBadge({ toolCall }: { toolCall: ToolCall }) {
  return (
    <span
      className={`inline-flex items-center gap-1 px-2 py-0.5 text-xs rounded-full mr-1 ${
        toolCall.isError
          ? "bg-red-100 text-red-800"
          : toolCall.result !== undefined
            ? "bg-green-100 text-green-800"
            : "bg-yellow-100 text-yellow-800"
      }`}
    >
      {toolCall.name}
      {toolCall.isError && " (error)"}
    </span>
  );
}

// =============================================================================
// Main Component
// =============================================================================

export interface PipelineChatProps {
  /** Default language */
  defaultLanguage?: "en" | "ga";
  /** Available agents to filter */
  availableAgents?: string[];
  /** Placeholder text */
  placeholder?: string;
}

export function PipelineChat({
  defaultLanguage = "en",
  availableAgents = ["curriculum", "research", "code_search", "memory"],
  placeholder = "Ask about Irish curriculum, search code, or query knowledge graphs...",
}: PipelineChatProps) {
  const [input, setInput] = useState("");
  const [language, setLanguage] = useState<"en" | "ga">(defaultLanguage);
  const [selectedAgents, setSelectedAgents] = useState<string[]>([]);

  const {
    messages,
    isStreaming,
    sessionId,
    sendMessage,
    stopStream,
    clearSession,
    error,
  } = usePipelineStream({
    onError: (err) => console.error("Pipeline error:", err),
    onDone: (agents) => console.log("Completed with agents:", agents),
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const text = input.trim();
    if (!text || isStreaming) return;

    setInput("");
    await sendMessage(text, {
      language,
      agents: selectedAgents.length > 0 ? selectedAgents : undefined,
    });
  };

  const toggleAgent = (agent: string) => {
    setSelectedAgents((prev) =>
      prev.includes(agent)
        ? prev.filter((a) => a !== agent)
        : [...prev, agent]
    );
  };

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b">
        <div className="flex items-center gap-2">
          <h2 className="font-semibold">Pipeline Chat</h2>
          {sessionId && (
            <span className="text-xs text-muted-foreground">
              Session: {sessionId.slice(0, 8)}...
            </span>
          )}
        </div>

        <div className="flex items-center gap-2">
          <select
            value={language}
            onChange={(e) => setLanguage(e.target.value as "en" | "ga")}
            className="h-8 w-24 rounded border border-input bg-background px-2 text-sm focus:outline-none focus:ring-1 focus:ring-ring"
          >
            <option value="en">English</option>
            <option value="ga">Gaeilge</option>
          </select>

          <Button
            variant="ghost"
            size="icon"
            onClick={() => clearSession()}
            disabled={isStreaming}
            title="Clear session"
          >
            <Trash2 size={18} />
          </Button>
        </div>
      </div>

      {/* Agent Filter */}
      <div className="flex flex-wrap gap-2 p-2 border-b bg-muted/50">
        <span className="text-xs text-muted-foreground self-center">Agents:</span>
        {availableAgents.map((agent) => (
          <button
            key={agent}
            onClick={() => toggleAgent(agent)}
            className={`px-2 py-0.5 text-xs rounded-full transition-colors ${
              selectedAgents.includes(agent)
                ? "bg-primary text-primary-foreground"
                : "bg-background border hover:bg-muted"
            }`}
          >
            {agent}
          </button>
        ))}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4">
        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-full text-muted-foreground">
            <p>{placeholder}</p>
          </div>
        ) : (
          messages.map((message) => (
            <MessageBubble
              key={message.id}
              message={message}
              isStreaming={isStreaming}
            />
          ))
        )}
      </div>

      {/* Error Banner */}
      {error && (
        <div className="px-4 py-2 bg-destructive/10 text-destructive text-sm">
          {error}
        </div>
      )}

      {/* Input */}
      <form
        onSubmit={handleSubmit}
        className="flex items-center gap-2 p-4 border-t"
      >
        <Input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder={placeholder}
          disabled={isStreaming}
          className="flex-1"
        />

        {isStreaming ? (
          <Button
            type="button"
            size="icon"
            variant="destructive"
            onClick={stopStream}
          >
            <StopCircle size={18} />
          </Button>
        ) : (
          <Button type="submit" size="icon" disabled={!input.trim()}>
            <Send size={18} />
          </Button>
        )}
      </form>
    </div>
  );
}
