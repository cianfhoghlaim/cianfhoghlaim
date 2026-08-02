import { create } from "zustand";
import { persist } from "zustand/middleware";

export interface Message {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  timestamp: Date;
  sources?: {
    title: string;
    type: "Document" | "API" | "Graph" | "Protocol";
    url?: string;
  }[];
  toolCalls?: {
    name: string;
    args: Record<string, unknown>;
    result?: unknown;
  }[];
}

export interface Session {
  id: string;
  title: string;
  messages: Message[];
  createdAt: Date;
  updatedAt: Date;
}

interface ChatState {
  sessions: Session[];
  activeSessionId: string | null;
  isStreaming: boolean;

  // Actions
  createSession: (title?: string) => string;
  deleteSession: (id: string) => void;
  setActiveSession: (id: string | null) => void;
  addMessage: (sessionId: string, message: Omit<Message, "id" | "timestamp">) => void;
  updateMessage: (sessionId: string, messageId: string, content: string) => void;
  setStreaming: (streaming: boolean) => void;
  getActiveSession: () => Session | undefined;
}

export const useChatStore = create<ChatState>()(
  persist(
    (set, get) => ({
      sessions: [],
      activeSessionId: null,
      isStreaming: false,

      createSession: (title?: string) => {
        const id = crypto.randomUUID();
        const session: Session = {
          id,
          title: title || `Chat ${new Date().toLocaleDateString()}`,
          messages: [
            {
              id: crypto.randomUUID(),
              role: "assistant",
              content:
                "Hello! I'm your crypto research assistant. I can help you analyze DeFi protocols, understand tokenomics, review audit reports, and explore the knowledge graph. What would you like to know?",
              timestamp: new Date(),
            },
          ],
          createdAt: new Date(),
          updatedAt: new Date(),
        };

        set((state) => ({
          sessions: [session, ...state.sessions],
          activeSessionId: id,
        }));

        return id;
      },

      deleteSession: (id) => {
        set((state) => {
          const sessions = state.sessions.filter((s) => s.id !== id);
          const activeSessionId =
            state.activeSessionId === id
              ? sessions[0]?.id || null
              : state.activeSessionId;
          return { sessions, activeSessionId };
        });
      },

      setActiveSession: (id) => set({ activeSessionId: id }),

      addMessage: (sessionId, message) => {
        set((state) => ({
          sessions: state.sessions.map((session) =>
            session.id === sessionId
              ? {
                  ...session,
                  messages: [
                    ...session.messages,
                    {
                      ...message,
                      id: crypto.randomUUID(),
                      timestamp: new Date(),
                    },
                  ],
                  updatedAt: new Date(),
                }
              : session
          ),
        }));
      },

      updateMessage: (sessionId, messageId, content) => {
        set((state) => ({
          sessions: state.sessions.map((session) =>
            session.id === sessionId
              ? {
                  ...session,
                  messages: session.messages.map((msg) =>
                    msg.id === messageId ? { ...msg, content } : msg
                  ),
                  updatedAt: new Date(),
                }
              : session
          ),
        }));
      },

      setStreaming: (streaming) => set({ isStreaming: streaming }),

      getActiveSession: () => {
        const { sessions, activeSessionId } = get();
        return sessions.find((s) => s.id === activeSessionId);
      },
    }),
    {
      name: "chat-storage",
      partialize: (state) => ({
        sessions: state.sessions.map((s) => ({
          ...s,
          // Convert dates to ISO strings for storage
          createdAt: s.createdAt,
          updatedAt: s.updatedAt,
          messages: s.messages.map((m) => ({
            ...m,
            timestamp: m.timestamp,
          })),
        })),
        activeSessionId: state.activeSessionId,
      }),
    }
  )
);
