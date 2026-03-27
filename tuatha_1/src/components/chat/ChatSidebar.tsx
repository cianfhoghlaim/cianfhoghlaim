import { useChatStore, Session } from "../../stores/chat";
import { cn } from "../../lib/utils";

export function ChatSidebar() {
  const { sessions, activeSessionId, createSession, deleteSession, setActiveSession } =
    useChatStore();

  const formatDate = (date: Date) => {
    const now = new Date();
    const diff = now.getTime() - new Date(date).getTime();
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));

    if (days === 0) return "Today";
    if (days === 1) return "Yesterday";
    if (days < 7) return `${days} days ago`;
    return new Date(date).toLocaleDateString();
  };

  const getSessionPreview = (session: Session) => {
    const lastUserMessage = [...session.messages]
      .reverse()
      .find((m) => m.role === "user");
    if (!lastUserMessage) return "New conversation";
    return lastUserMessage.content.slice(0, 50) + (lastUserMessage.content.length > 50 ? "..." : "");
  };

  return (
    <div className="flex h-full flex-col">
      {/* Header */}
      <div className="border-b p-4">
        <button
          onClick={() => createSession()}
          className="w-full rounded-lg bg-primary px-4 py-2 font-medium text-primary-foreground hover:bg-primary/90"
        >
          + New Chat
        </button>
      </div>

      {/* Sessions list */}
      <div className="flex-1 overflow-y-auto">
        {sessions.length === 0 ? (
          <div className="p-4 text-center text-sm text-muted-foreground">
            No chat history yet.
            <br />
            Start a new conversation!
          </div>
        ) : (
          <div className="divide-y">
            {sessions.map((session) => (
              <div
                key={session.id}
                onClick={() => setActiveSession(session.id)}
                className={cn(
                  "group flex cursor-pointer items-start justify-between p-4 hover:bg-muted/50",
                  activeSessionId === session.id && "bg-muted"
                )}
              >
                <div className="min-w-0 flex-1">
                  <p className="truncate font-medium">{session.title}</p>
                  <p className="mt-1 truncate text-sm text-muted-foreground">
                    {getSessionPreview(session)}
                  </p>
                  <p className="mt-1 text-xs text-muted-foreground">
                    {formatDate(session.updatedAt)}
                  </p>
                </div>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    deleteSession(session.id);
                  }}
                  className="ml-2 rounded p-1 opacity-0 hover:bg-destructive hover:text-destructive-foreground group-hover:opacity-100"
                  title="Delete session"
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="16"
                    height="16"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  >
                    <path d="M3 6h18" />
                    <path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6" />
                    <path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2" />
                  </svg>
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="border-t p-4">
        <div className="text-xs text-muted-foreground">
          <p>Powered by Agno + CopilotKit</p>
          <p className="mt-1">Knowledge graphs indexed with Cognee</p>
        </div>
      </div>
    </div>
  );
}
