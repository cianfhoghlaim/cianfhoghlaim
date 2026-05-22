import { useState, useRef, useEffect } from "react";
import { Send, Bot, User, Loader2, RefreshCw } from "lucide-react";
import { toast } from "sonner";
import { cn } from "../lib/utils";
import {
  streamAgent,
  AgentEvent,
} from "../lib/agui-client";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: string;
}

interface CurriculumUIState {
  selected_nations: string[];
  selected_subjects: string[];
  comparison_results: unknown[];
  search_results: unknown[];
  pending_translations: unknown[];
}

const SUGGESTIONS = [
  "Compare Junior Cycle and GCSE Mathematics",
  "What are the key differences between Irish and Welsh curricula?",
  "Find learning outcomes for A-Level Physics in England",
  "Show me Scottish Highers equivalent to Leaving Cert",
];

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const [uiState, setUiState] = useState<CurriculumUIState>({
    selected_nations: [],
    selected_subjects: [],
    comparison_results: [],
    search_results: [],
    pending_translations: [],
  });
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isStreaming) return;

    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: "user",
      content: input.trim(),
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsStreaming(true);

    // Create assistant message placeholder
    const assistantId = crypto.randomUUID();
    const assistantMessage: Message = {
      id: assistantId,
      role: "assistant",
      content: "",
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, assistantMessage]);

    abortControllerRef.current = new AbortController();

    try {
      const eventStream = streamAgent(
        userMessage.content,
        abortControllerRef.current.signal
      );

      for await (const event of eventStream) {
        handleAgentEvent(event, assistantId);
      }
    } catch (error) {
      if ((error as Error).name !== "AbortError") {
        toast.error("Failed to get response from agent");
        console.error("Agent error:", error);
      }
    } finally {
      setIsStreaming(false);
      abortControllerRef.current = null;
    }
  };

  const handleAgentEvent = (event: AgentEvent, assistantId: string) => {
    switch (event.type) {
      case "TEXT_MESSAGE_CONTENT":
        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === assistantId
              ? { ...msg, content: msg.content + (event.delta || "") }
              : msg
          )
        );
        break;

      case "STATE_SNAPSHOT":
        if (event.snapshot) {
          setUiState(event.snapshot as CurriculumUIState);
        }
        break;

      case "STATE_DELTA":
        if (event.delta) {
          // Apply JSON Patch delta to state
          // For simplicity, just merge for now
          setUiState((prev) => ({ ...prev, ...event.delta }));
        }
        break;

      case "TOOL_CALL_START":
        toast.info(`Calling: ${event.name}`);
        break;

      case "RUN_ERROR":
        toast.error(event.message || "Agent error occurred");
        break;
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    setInput(suggestion);
  };

  const handleCancel = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
  };

  const handleReset = () => {
    setMessages([]);
    setUiState({
      selected_nations: [],
      selected_subjects: [],
      comparison_results: [],
      search_results: [],
      pending_translations: [],
    });
  };

  return (
    <div className="flex flex-col h-[calc(100vh-10rem)]">
      {/* Header */}
      <div className="flex items-center justify-between pb-4 border-b">
        <div>
          <h1 className="text-2xl font-bold">Curriculum Chat</h1>
          <p className="text-sm text-muted-foreground">
            Ask questions about curricula across Celtic nations
          </p>
        </div>
        <button
          onClick={handleReset}
          className={cn(
            "inline-flex items-center gap-2 rounded-md text-sm font-medium",
            "border border-input bg-background hover:bg-accent",
            "h-9 px-3"
          )}
        >
          <RefreshCw className="h-4 w-4" />
          Reset
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto py-4 space-y-4">
        {messages.length === 0 ? (
          <div className="text-center py-12 space-y-6">
            <Bot className="h-12 w-12 mx-auto text-muted-foreground" />
            <div>
              <h2 className="text-lg font-medium">Welcome to Curriculum Chat</h2>
              <p className="text-sm text-muted-foreground">
                Ask me about curricula from Ireland, England, Scotland, Wales, or Northern Ireland
              </p>
            </div>
            <div className="flex flex-wrap justify-center gap-2 max-w-xl mx-auto">
              {SUGGESTIONS.map((suggestion) => (
                <button
                  key={suggestion}
                  onClick={() => handleSuggestionClick(suggestion)}
                  className={cn(
                    "text-sm rounded-full border px-4 py-2",
                    "hover:bg-primary hover:text-primary-foreground transition-colors"
                  )}
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        ) : (
          messages.map((message) => (
            <div
              key={message.id}
              className={cn(
                "flex gap-3",
                message.role === "user" ? "justify-end" : "justify-start"
              )}
            >
              {message.role === "assistant" && (
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                  <Bot className="h-5 w-5 text-primary" />
                </div>
              )}
              <div
                className={cn(
                  "max-w-[80%] rounded-lg px-4 py-2",
                  message.role === "user"
                    ? "bg-primary text-primary-foreground"
                    : "bg-muted"
                )}
              >
                <p className="whitespace-pre-wrap">{message.content}</p>
                {message.role === "assistant" && !message.content && isStreaming && (
                  <Loader2 className="h-4 w-4 animate-spin" />
                )}
              </div>
              {message.role === "user" && (
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary flex items-center justify-center">
                  <User className="h-5 w-5 text-primary-foreground" />
                </div>
              )}
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* UI State Panel (if has results) */}
      {(uiState.comparison_results.length > 0 || uiState.search_results.length > 0) && (
        <div className="border-t py-4">
          <h3 className="text-sm font-medium mb-2">Results</h3>
          <div className="flex flex-wrap gap-2">
            {uiState.selected_nations.map((nation) => (
              <span key={nation} className="text-xs bg-primary/10 text-primary px-2 py-1 rounded">
                {nation}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Input */}
      <form onSubmit={handleSubmit} className="pt-4 border-t">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about curricula..."
            disabled={isStreaming}
            className={cn(
              "flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm",
              "placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2",
              "focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
            )}
          />
          {isStreaming ? (
            <button
              type="button"
              onClick={handleCancel}
              className={cn(
                "inline-flex items-center justify-center rounded-md text-sm font-medium",
                "bg-destructive text-destructive-foreground hover:bg-destructive/90",
                "h-10 px-4"
              )}
            >
              Cancel
            </button>
          ) : (
            <button
              type="submit"
              disabled={!input.trim()}
              className={cn(
                "inline-flex items-center justify-center rounded-md text-sm font-medium",
                "bg-primary text-primary-foreground hover:bg-primary/90",
                "h-10 px-4 disabled:opacity-50 disabled:cursor-not-allowed"
              )}
            >
              <Send className="h-4 w-4" />
            </button>
          )}
        </div>
      </form>
    </div>
  );
}
