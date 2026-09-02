/** AskMyArchive — a CopilotKit chat panel that talks to the
 * user's personal UoG archive (the 3 UoG courses' artefacts +
 * transcript).
 *
 * Per the 2026-08-23-uog-personal-archive-tertiary-modules-v1 change
 * (WS10 — Convex + CopilotKit + Genie + ADK). The component renders a
 * thin chat panel that calls the 5 Convex actions / queries defined
 * in `web/apps/cianfhoghlaim/convex/personalArchive.ts`:
 *
 *   - `chatOverMyArchive`         (LLM + vector search)
 *   - `getModuleDossier`          (per-module dossier)
 *   - `getQuestionsForTopic`      (cross-module question lookup)
 *   - `getMyAnswerForQuestion`    (per-question answer)
 *   - `searchSimilarQuestions`    (semantic F-granularity search)
 *
 * The Convex React hooks (`useQuery` / `useAction`) come from the
 * project's generated `./_generated/react` path; the panel renders
 * without them when Convex is not configured (CI / first-launch
 * fallback).
 */

"use client";

import { type FC, useEffect, useState } from "react";

// Lazy-loaded Convex hooks. The panel renders without them when the
// Convex client is not yet configured (CI / first-launch fallback).
let _useConvexHooks: (() => {
  useQuery: <T extends (...args: any[]) => any>(
    query: T,
    args?: Parameters<T>[0]
  ) => unknown;
  useAction: <T extends (...args: any[]) => any>(
    action: T,
    args?: Parameters<T>[0]
  ) => unknown;
}) | null = null;

function _try_load_convex_hooks(): void {
  try {
    // eslint-disable-next-line @typescript-eslint/no-require-imports
    _useConvexHooks = require("convex/react").useConvexHooks as typeof _useConvexHooks;
  } catch (_e) {
    _useConvexHooks = null;
  }
}

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface AskMyArchiveMessage {
  readonly id: string;
  readonly role: "user" | "assistant" | "system";
  readonly content: string;
  readonly created_at: number;
  readonly hits?: ReadonlyArray<Record<string, unknown>>;
  readonly module_code?: string | null;
}

export interface AskMyArchiveProps {
  readonly thread_id: string;
  readonly initial_messages?: ReadonlyArray<AskMyArchiveMessage>;
  readonly default_module_code?: string;
  readonly on_module_code_change?: (module_code: string | null) => void;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export const AskMyArchive: FC<AskMyArchiveProps> = ({
  thread_id,
  initial_messages = [],
  default_module_code,
  on_module_code_change,
}) => {
  useEffect(() => {
    _try_load_convex_hooks();
  }, []);

  const [messages, set_messages] = useState<AskMyArchiveMessage[]>(
    [...initial_messages]
  );
  const [input, set_input] = useState<string>("");
  const [module_code, set_module_code] = useState<string | null>(
    default_module_code ?? null
  );
  const [busy, set_busy] = useState<boolean>(false);

  async function _send(): Promise<void> {
    const text = input.trim();
    if (!text || busy) return;
    set_busy(true);
    const user_msg: AskMyArchiveMessage = {
      id: `${Date.now()}-user`,
      role: "user",
      content: text,
      created_at: Date.now(),
    };
    set_messages((prev) => [...prev, user_msg]);
    set_input("");
    try {
      // Convex actions must be invoked through the generated client.
      // We resolve them lazily via `require` so the component still
      // compiles even before `npx convex dev` has generated the
      // client stubs.
      // eslint-disable-next-line @typescript-eslint/no-require-imports
      const mod = require("../convex/_generated/api") as {
        personalArchive: {
          chatOverMyArchive: (...args: unknown[]) => Promise<unknown>;
        };
      };
      const args = {
        thread_id,
        user_message: text,
        module_code: module_code ?? undefined,
      };
      const resp = (await mod.personalArchive.chatOverMyArchive(
        args
      )) as {
        assistant_message?: string;
        hits?: Array<Record<string, unknown>>;
      };
      const assistant_msg: AskMyArchiveMessage = {
        id: `${Date.now()}-assistant`,
        role: "assistant",
        content: resp.assistant_message ?? "(no answer)",
        created_at: Date.now(),
        hits: resp.hits ?? [],
        module_code: module_code ?? null,
      };
      set_messages((prev) => [...prev, assistant_msg]);
    } catch (_e) {
      const assistant_msg: AskMyArchiveMessage = {
        id: `${Date.now()}-error`,
        role: "assistant",
        content:
          "Could not reach the Convex backend. Make sure `convex dev` " +
          "is running and the personalArchive functions are deployed.",
        created_at: Date.now(),
      };
      set_messages((prev) => [...prev, assistant_msg]);
    } finally {
      set_busy(false);
    }
  }

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-2xl font-bold text-slate-900">
            Ask My UoG Archive
          </h2>
          <p className="text-sm text-slate-600">
            Chat over your 3 UoG courses' artefacts + transcript.
          </p>
        </div>
        <select
          value={module_code ?? ""}
          onChange={(e) => {
            const next = e.target.value || null;
            set_module_code(next);
            on_module_code_change?.(next);
          }}
          className="text-sm border border-slate-300 rounded px-3 py-1.5"
        >
          <option value="">All modules</option>
          <option value="CS4423">CS4423 — Numerical Analysis 2</option>
          <option value="MP491">MP491 — Mathematics Project</option>
          <option value="MA344">MA344 — Differential Equations</option>
          <option value="GA201">GA201 — Irish Language C1</option>
        </select>
      </div>

      <div
        className="space-y-3 mb-4 max-h-96 overflow-y-auto"
        aria-live="polite"
      >
        {messages.length === 0 ? (
          <p className="text-sm text-slate-500 text-center py-6">
            Try: "Which CS4423 questions are about numerical stability?"
          </p>
        ) : (
          messages.map((m) => (
            <MessageRow key={m.id} message={m} />
          ))
        )}
      </div>

      <div className="flex items-center gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => set_input(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") void _send();
          }}
          placeholder={
            module_code
              ? `Ask about ${module_code}…`
              : "Ask about your UoG archive…"
          }
          className="flex-1 border border-slate-300 rounded px-3 py-2 text-sm"
        />
        <button
          type="button"
          disabled={busy || !input.trim()}
          onClick={() => void _send()}
          className="bg-blue-600 text-white text-sm px-4 py-2 rounded disabled:bg-slate-300"
        >
          {busy ? "Thinking…" : "Send"}
        </button>
      </div>
    </div>
  );
};

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

const MessageRow: FC<{ message: AskMyArchiveMessage }> = ({ message }) => {
  const is_user = message.role === "user";
  return (
    <div
      className={
        "rounded-lg p-3 text-sm border " +
        (is_user
          ? "bg-blue-50 border-blue-100 ml-auto max-w-[80%]"
          : "bg-slate-50 border-slate-100 mr-auto max-w-[80%]")
      }
    >
      <div className="text-slate-900 whitespace-pre-wrap">
        {message.content}
      </div>
      {message.hits && message.hits.length > 0 && (
        <details className="mt-2 text-xs text-slate-500">
          <summary>{message.hits.length} source hits</summary>
          <pre className="mt-1 overflow-x-auto">
            {JSON.stringify(message.hits, null, 2)}
          </pre>
        </details>
      )}
      <div className="mt-1 text-[10px] text-slate-400">
        {new Date(message.created_at).toLocaleTimeString()}
        {message.module_code ? ` · ${message.module_code}` : ""}
      </div>
    </div>
  );
};

export default AskMyArchive;
