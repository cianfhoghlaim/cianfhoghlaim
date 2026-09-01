// apps/web/src/components/chat/SubjectChat.tsx
// Per openspec/changes/cianfhoghlaim-website-rewrite/specs/.../spec.md
// Requirement R3. The per-subject CopilotKit chat — the 8 NCCA subject
// agents. Embedded on each subject's /practice page.

"use client";

import * as React from "react";
import { CopilotKit, useChat } from "@copilotkit/react-core/v2";
import { CopilotChat } from "@copilotkit/react-core/v2";
import "@copilotkit/react-ui/styles.css";

import { AGENTS, getAgentById } from "@/lib/registry";
import { getSystemPrompt } from "@/lib/agents";

export interface SubjectChatProps {
  subject: string;
  topic?: string;
}

export function SubjectChat({ subject, topic }: SubjectChatProps) {
  const agentId = subject as keyof typeof AGENTS;
  const agent = getAgentById(agentId);
  if (!agent) {
    return <div className="text-red-500">Unknown subject: {subject}</div>;
  }

  return (
    <CopilotKit runtimeUrl="/api/copilotkit" agent={subject}>
      <div className="flex flex-col gap-2">
        <div className="flex items-center gap-2">
          <span
            className="w-8 h-8 rounded-full flex items-center justify-center text-white font-bold"
            style={{ background: agent.color }}
          >
            {agent.name.charAt(0)}
          </span>
          <div>
            <div className="text-sm font-bold" style={{ color: agent.color }}>
              {agent.name} Agent
            </div>
              <div className="text-xs text-slate-400">
                NCCA Leaving Certificate · Éraic tier {agent.eiraic_tier}/13
                {topic ? ` · ${topic}` : ""}
              </div>
          </div>
        </div>
        <CopilotChat
          labels={{
            title: agent.name,
            initial: `Hi! I'm the ${agent.name} subject specialist${topic ? ` for ${topic}` : ""}. Use the 5×8 mastery matrix + the BAML schema + the CocoIndex embeddings + the dlt extraction. Ask me anything.`,
          }}
        />
      </div>
    </CopilotKit>
  );
}