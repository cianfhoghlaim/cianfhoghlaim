// apps/web/src/components/chat/GlobalChat.tsx
// Per openspec/changes/cianfhoghlaim-website-rewrite/specs/.../spec.md
// Requirement R3 + R4. The global CopilotKit chat panel visible on every
// page — the cianfhoghlaim operator agent.
//
// Uses the a2ui-renderer skill pattern (per
// /Users/cianmacandeisigh/dev/cianfhoghlaim/.agents/skills/copilotkit/skills/a2ui-renderer/SKILL.md)
// to render A2UI surfaces from the agent chat.

"use client";

import * as React from "react";
import { CopilotKit } from "@copilotkit/react-core/v2";
import { CopilotSidebar, CopilotChat } from "@copilotkit/react-core/v2";
import "@copilotkit/react-ui/styles.css";
import { useChat } from "@copilotkit/react-core/v2";

import { listAllAgents } from "@/lib/agents";
import { AGENTS } from "@/lib/registry";

export interface GlobalChatProps {
  runtimeUrl?: string;
  initialOpen?: boolean;
}

export function GlobalChat({ runtimeUrl = "/api/copilotkit", initialOpen = false }: GlobalChatProps) {
  const [open, setOpen] = React.useState(initialOpen);
  const [selectedAgent, setSelectedAgent] = React.useState("cianfhoghlaim");

  const allAgents = listAllAgents();

  return (
    <CopilotKit
      runtimeUrl={runtimeUrl}
      agent="cianfhoghlaim" // default agent = cianfhoghlaim operator
    >
      {/* Floating chat button */}
      <button
        onClick={() => setOpen(!open)}
        className="fixed bottom-4 right-4 z-40 w-14 h-14 rounded-full bg-amber-600 text-white shadow-lg hover:bg-amber-500 transition-colors flex items-center justify-center text-2xl"
        aria-label="Toggle cianfhoghlaim chat"
      >
        💬
      </button>

      {/* Chat sidebar */}
      {open && (
        <div className="fixed bottom-20 right-4 z-40 w-96 h-[600px] bg-slate-900 border border-amber-700 rounded-xl shadow-2xl flex flex-col">
          <div className="px-4 py-2 border-b border-amber-700 flex items-center justify-between">
            <span className="font-bold text-amber-400">cianfhoghlaim</span>
            <select
              className="bg-slate-950 text-amber-400 text-xs rounded px-2 py-1"
              value={selectedAgent}
              onChange={(e) => setSelectedAgent(e.target.value)}
              aria-label="Switch ADK agent"
            >
              {allAgents.map((a) => (
                <option key={a.id} value={a.id}>
                  {a.name}
                </option>
              ))}
            </select>
          </div>
          <div className="flex-1 overflow-y-auto p-3 text-sm">
            <CopilotChat
              labels={{
                title: AGENTS.find((a) => a.id === selectedAgent)?.name ?? "cianfhoghlaim Operator",
                initial: `Hi! I'm the ${AGENTS.find((a) => a.id === selectedAgent)?.name ?? "cianfhoghlaim Operator"}. How can I help?`,
              }}
            />
          </div>
          <div className="px-3 py-2 border-t border-amber-700 text-xs text-slate-400">
            A2UI surfaces render automatically. Powered by{" "}
            <code className="text-amber-400">@copilotkit/a2ui-renderer</code>.
          </div>
        </div>
      )}
    </CopilotKit>
  );
}