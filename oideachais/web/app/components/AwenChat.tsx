import { useCopilotChat, useCopilotAction } from "@copilotkit/react-core";
import { useState } from "react";
import { listExamMaterials, getMarkingSchemeSummary, queryLakehouse } from "../server/lakehouse";

/**
 * AwenChat — the persistent chat assistant.
 *
 * The chat is wired with CopilotKit's `useCopilotChat` for streaming and
 * `useCopilotAction` for tool-calling. Each action maps 1:1 to a TanStack
 * Start server function. The component renders the chat as a slide-in
 * CopilotSidebar so it can be opened from any route.
 */
export function AwenChat() {
  const { visibleMessages, appendMessage, isLoading } = useCopilotChat();
  const [open, setOpen] = useState(false);

  useCopilotAction({
    name: "queryDuckLake",
    description: "Run a DuckDB SQL query against the oideachais lakehouse.",
    parameters: [
      {
        name: "sql",
        type: "string",
        description: "DuckDB SQL — use `examinations.all_exam_materials` or `curriculum.*`",
        required: true,
      },
    ],
    handler: async ({ sql }) => {
      const rows = await queryLakehouse({ data: { sql } });
      return JSON.stringify(rows.slice(0, 50));
    },
  });

  useCopilotAction({
    name: "listExamMaterials",
    description: "List exam materials for a subject / year / level.",
    parameters: [
      { name: "subject", type: "string", required: true },
      { name: "year", type: "number", required: true },
      {
        name: "materialType",
        type: "string",
        description: "'exam_papers' or 'marking_schemes'",
        required: false,
      },
    ],
    handler: async ({ subject, year, materialType }) => {
      const rows = await listExamMaterials({
        data: {
          subject,
          year,
          level: "leaving_certificate",
          materialType: (materialType as "exam_papers" | "marking_schemes") ?? "exam_papers",
        },
      });
      return JSON.stringify(rows.slice(0, 30));
    },
  });

  useCopilotAction({
    name: "getMarkingSchemeSummary",
    description: "Return the canonical rubric + recent years for a subject.",
    parameters: [
      { name: "subject", type: "string", required: true },
    ],
    handler: async ({ subject }) => {
      const summary = await getMarkingSchemeSummary({ data: { subject } });
      return JSON.stringify(summary);
    },
  });

  return (
    <>
      {open ? (
        <div className="fixed bottom-4 right-4 w-96 h-[600px] bg-slate-950 border border-slate-800 rounded-xl shadow-2xl flex flex-col z-50">
          <div className="flex items-center justify-between p-3 border-b border-slate-800">
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 rounded-full bg-emerald-600 flex items-center justify-center text-xs font-bold">
                A
              </div>
              <span className="font-cinzel text-emerald-400">Awen Assistant</span>
            </div>
            <button
              onClick={() => setOpen(false)}
              className="text-slate-400 hover:text-slate-200 text-sm"
            >
              ✕
            </button>
          </div>
          <div className="flex-1 overflow-y-auto p-3 space-y-2 text-sm">
            {visibleMessages.length === 0 ? (
              <p className="text-slate-500 italic">
                Fáilte! Ask about exam papers, marking schemes, or syllabi.
              </p>
            ) : (
              visibleMessages.map((m, idx: number) => (
                <div
                  key={m.id ?? idx}
                  className={
                    "p-2 rounded-lg " +
                    ((m as { role?: string }).role === "user"
                      ? "bg-emerald-700/20 text-emerald-100"
                      : "bg-slate-800 text-slate-200")
                  }
                >
                  {String((m as { content?: string }).content ?? "")}
                </div>
              ))
            )}
            {isLoading && (
              <div className="text-slate-500 text-xs italic">typing…</div>
            )}
          </div>
          <form
            className="p-2 border-t border-slate-800"
            onSubmit={async (e) => {
              e.preventDefault();
              const input = e.currentTarget.elements.namedItem(
                "prompt",
              ) as HTMLInputElement;
              const text = input.value.trim();
              if (!text) return;
              await appendMessage({ role: "user", content: text } as never);
              input.value = "";
            }}
          >
            <input
              name="prompt"
              placeholder="Ask Awen…"
              className="w-full bg-slate-900 border border-slate-700 rounded px-2 py-1 text-sm"
            />
          </form>
        </div>
      ) : (
        <button
          onClick={() => setOpen(true)}
          className="fixed bottom-4 right-4 w-14 h-14 rounded-full bg-emerald-600 hover:bg-emerald-500 text-white font-cinzel text-xl font-bold shadow-2xl z-50"
        >
          A
        </button>
      )}
    </>
  );
}
