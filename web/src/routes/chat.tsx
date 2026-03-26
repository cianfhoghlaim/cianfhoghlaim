import { createFileRoute } from "@tanstack/react-router";
import { useState, useRef, useEffect } from "react";
import {
  Send,
  Bot,
  User,
  Loader2,
  RefreshCw,
  Wrench,
  AlertCircle,
  CheckCircle,
  PanelRightOpen,
  PanelRightClose,
} from "lucide-react";
import { toast } from "sonner";
import { cn } from "../lib/utils";
import { usePipelineStream, ToolCall, RenderedComponent } from "../hooks/use-pipeline-stream";
import { AgentComponent, GenerativeUIEvent } from "../components/agui/ComponentRegistry";

export const Route = createFileRoute("/chat")({
  component: ChatPage,
});

interface CurriculumUIState {
  selected_nations: string[];
  selected_subjects: string[];
  selected_level: string | null;
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

function ChatPage() {
  const [input, setInput] = useState("");
  const [uiState, setUiState] = useState<CurriculumUIState>({
    selected_nations: [],
    selected_subjects: [],
    selected_level: null,
    comparison_results: [],
    search_results: [],
    pending_translations: [],
  });
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Sidebar visibility toggle
  const [sidebarOpen, setSidebarOpen] = useState(true);

  // Use the AG-UI pipeline stream hook
  const {
    messages,
    isStreaming,
    sessionId,
    sendMessage,
    stopStream,
    clearMessages,
    clearSession,
    error,
    currentToolCalls,
    // Generative UI
    renderedComponents,
    removeComponent,
    clearComponents,
  } = usePipelineStream({
    apiPath: "/api/agent",
    onStateSnapshot: (snapshot) => {
      setUiState((prev) => ({ ...prev, ...snapshot } as CurriculumUIState));
    },
    onStateDelta: (delta) => {
      setUiState((prev) => ({ ...prev, ...delta } as CurriculumUIState));
    },
    onToolCall: (toolCall) => {
      toast.info(`Using tool: ${toolCall.name}`, {
        icon: <Wrench className="h-4 w-4" />,
      });
    },
    onGenerativeUI: (component) => {
      // Auto-open sidebar when sidebar components arrive
      if (component.slot === "sidebar") {
        setSidebarOpen(true);
      }
    },
    onError: (errorMsg) => {
      toast.error(errorMsg);
    },
  });

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isStreaming) return;

    const message = input.trim();
    setInput("");

    await sendMessage(message, {
      language: "en", // Could be made dynamic
    });
  };

  const handleSuggestionClick = (suggestion: string) => {
    setInput(suggestion);
  };

  const handleReset = async () => {
    await clearSession();
    clearComponents(); // Clear all generative UI components
    setUiState({
      selected_nations: [],
      selected_subjects: [],
      selected_level: null,
      comparison_results: [],
      search_results: [],
      pending_translations: [],
    });
  };

  // Filter components for sidebar toggle visibility
  const hasSidebarComponents = renderedComponents.some((c) => c.slot === "sidebar");

  return (
    <div className="flex h-[calc(100vh-10rem)] gap-4">
      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b">
          <div>
            <h1 className="text-2xl font-bold">Curriculum Chat</h1>
            <p className="text-sm text-muted-foreground">
              Ask questions about curricula across Celtic nations
              {sessionId && (
                <span className="ml-2 text-xs opacity-50">
                  Session: {sessionId.slice(0, 8)}...
                </span>
              )}
            </p>
          </div>
          <div className="flex items-center gap-2">
            {/* Sidebar Toggle */}
            {hasSidebarComponents && (
              <button
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className={cn(
                  "inline-flex items-center justify-center rounded-md text-sm font-medium",
                  "border border-input bg-background hover:bg-accent",
                  "h-9 w-9"
                )}
                title={sidebarOpen ? "Hide panel" : "Show panel"}
              >
                {sidebarOpen ? (
                  <PanelRightClose className="h-4 w-4" />
                ) : (
                  <PanelRightOpen className="h-4 w-4" />
                )}
              </button>
            )}
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
        </div>

        {/* Error Banner */}
        {error && (
          <div className="mt-2 p-3 rounded-md bg-destructive/10 text-destructive flex items-center gap-2">
            <AlertCircle className="h-4 w-4" />
            <span className="text-sm">{error}</span>
          </div>
        )}

        {/* Main Content Area with Inline Components */}
        <div className="flex-1 overflow-y-auto py-4 space-y-4">
          {messages.length === 0 ? (
            <div className="text-center py-12 space-y-6">
              <Bot className="h-12 w-12 mx-auto text-muted-foreground" />
              <div>
                <h2 className="text-lg font-medium">Welcome to Curriculum Chat</h2>
                <p className="text-sm text-muted-foreground">
                  Ask me about curricula from Ireland, England, Scotland, Wales, or
                  Northern Ireland
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
            <>
              {messages.map((message) => (
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
                  <div className="flex flex-col gap-2 max-w-[80%]">
                    {/* Tool Calls */}
                    {message.role === "assistant" &&
                      message.toolCalls &&
                      message.toolCalls.length > 0 && (
                        <div className="flex flex-wrap gap-1">
                          {message.toolCalls.map((toolCall) => (
                            <ToolCallBadge key={toolCall.id} toolCall={toolCall} />
                          ))}
                        </div>
                      )}

                    {/* Message Content */}
                    <div
                      className={cn(
                        "rounded-lg px-4 py-2",
                        message.role === "user"
                          ? "bg-primary text-primary-foreground"
                          : "bg-muted"
                      )}
                    >
                      <p className="whitespace-pre-wrap">{message.content}</p>
                      {message.role === "assistant" &&
                        !message.content &&
                        message.isStreaming && (
                          <Loader2 className="h-4 w-4 animate-spin" />
                        )}
                    </div>
                  </div>
                  {message.role === "user" && (
                    <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary flex items-center justify-center">
                      <User className="h-5 w-5 text-primary-foreground" />
                    </div>
                  )}
                </div>
              ))}

              {/* Inline Main Slot Components */}
              {renderedComponents
                .filter((c) => c.slot === "main")
                .map((component) => (
                  <div key={component.id} className="relative group">
                    <AgentComponent
                      event={{
                        type: "GENERATIVE_UI",
                        component: component.component,
                        props: component.props,
                        slot: component.slot,
                        component_id: component.id,
                      }}
                    />
                    <button
                      onClick={() => removeComponent(component.id)}
                      className={cn(
                        "absolute -top-2 -right-2 h-6 w-6 rounded-full",
                        "bg-muted hover:bg-destructive hover:text-destructive-foreground",
                        "opacity-0 group-hover:opacity-100 transition-opacity",
                        "flex items-center justify-center text-xs"
                      )}
                    >
                      ×
                    </button>
                  </div>
                ))}
            </>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Active Tool Calls */}
        {currentToolCalls.length > 0 && (
          <div className="border-t py-2">
            <div className="flex flex-wrap gap-2">
              {currentToolCalls.map((toolCall) => (
                <ToolCallBadge key={toolCall.id} toolCall={toolCall} />
              ))}
            </div>
          </div>
        )}

        {/* UI State Panel (if has results) */}
        {(uiState.search_results.length > 0 ||
          uiState.selected_subjects.length > 0) && (
          <div className="border-t py-4">
            <h3 className="text-sm font-medium mb-2">Context</h3>
            <div className="flex flex-wrap gap-2">
              {uiState.selected_subjects.map((subject) => (
                <span
                  key={subject}
                  className="text-xs bg-primary/10 text-primary px-2 py-1 rounded"
                >
                  {subject}
                </span>
              ))}
              {uiState.selected_level && (
                <span className="text-xs bg-secondary/10 text-secondary-foreground px-2 py-1 rounded">
                  {uiState.selected_level}
                </span>
              )}
              {uiState.search_results.length > 0 && (
                <span className="text-xs bg-muted text-muted-foreground px-2 py-1 rounded">
                  {uiState.search_results.length} results
                </span>
              )}
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
                onClick={stopStream}
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

      {/* Sidebar Panel for Generative UI Components */}
      {sidebarOpen && hasSidebarComponents && (
        <div className="w-80 flex-shrink-0 border-l pl-4 overflow-y-auto">
          <div className="flex items-center justify-between pb-2 mb-4 border-b">
            <h2 className="text-sm font-medium">Results</h2>
            <button
              onClick={() => clearComponents("sidebar")}
              className="text-xs text-muted-foreground hover:text-foreground"
            >
              Clear all
            </button>
          </div>
          <div className="space-y-4">
            {renderedComponents
              .filter((c) => c.slot === "sidebar")
              .map((component) => (
                <div key={component.id} className="relative group">
                  <AgentComponent
                    event={{
                      type: "GENERATIVE_UI",
                      component: component.component,
                      props: component.props,
                      slot: component.slot,
                      component_id: component.id,
                    }}
                  />
                  <button
                    onClick={() => removeComponent(component.id)}
                    className={cn(
                      "absolute -top-2 -right-2 h-5 w-5 rounded-full",
                      "bg-muted hover:bg-destructive hover:text-destructive-foreground",
                      "opacity-0 group-hover:opacity-100 transition-opacity",
                      "flex items-center justify-center text-xs"
                    )}
                  >
                    ×
                  </button>
                </div>
              ))}
          </div>
        </div>
      )}

      {/* Overlay for Modal Components */}
      {renderedComponents.some((c) => c.slot === "overlay") && (
        <div
          className="fixed inset-0 z-50 bg-background/80 backdrop-blur-sm flex items-center justify-center p-4"
          onClick={() => clearComponents("overlay")}
        >
          <div
            className="max-w-2xl w-full max-h-[80vh] overflow-auto bg-background rounded-lg border shadow-lg"
            onClick={(e) => e.stopPropagation()}
          >
            {renderedComponents
              .filter((c) => c.slot === "overlay")
              .map((component) => (
                <div key={component.id} className="relative">
                  <AgentComponent
                    event={{
                      type: "GENERATIVE_UI",
                      component: component.component,
                      props: component.props,
                      slot: component.slot,
                      component_id: component.id,
                    }}
                  />
                  <button
                    onClick={() => removeComponent(component.id)}
                    className={cn(
                      "absolute top-2 right-2 h-6 w-6 rounded-full",
                      "bg-muted hover:bg-destructive hover:text-destructive-foreground",
                      "flex items-center justify-center text-sm"
                    )}
                  >
                    ×
                  </button>
                </div>
              ))}
          </div>
        </div>
      )}
    </div>
  );
}

/**
 * Tool call status badge component.
 */
function ToolCallBadge({ toolCall }: { toolCall: ToolCall }) {
  const statusStyles = {
    pending: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300",
    executing:
      "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300",
    completed:
      "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300",
    error: "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300",
  };

  const StatusIcon = () => {
    switch (toolCall.status) {
      case "executing":
        return <Loader2 className="h-3 w-3 animate-spin" />;
      case "completed":
        return <CheckCircle className="h-3 w-3" />;
      case "error":
        return <AlertCircle className="h-3 w-3" />;
      default:
        return <Wrench className="h-3 w-3" />;
    }
  };

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 text-xs px-2 py-0.5 rounded-full",
        statusStyles[toolCall.status]
      )}
    >
      <StatusIcon />
      <span className="font-medium">{toolCall.name}</span>
    </span>
  );
}
