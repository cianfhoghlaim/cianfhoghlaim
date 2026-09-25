/**
 * /en/agents/$agent route — per the 2026-08-10-copilotkit-action-wiring-v1 change.
 *
 * Replaces the previous metadata-only display with an inline
 * `<CopilotKit agent={$agent}>` chat surface, using the 9 ADK agents
 * registered in `apps/api/src/registry.ts`.
 *
 * Usage: visit `/en/agents/math_agent` to chat with the math_agent ADK agent.
 */

import { createFileRoute, useParams } from "@tanstack/react-router";
import { CopilotChat } from "@copilotkit/react-ui";
import { CopilotKit } from "@copilotkit/react-core/v2";
import { useAgent } from "@copilotkit/react-core/v2";
import { useEffect } from "react";

export const Route = createFileRoute("/en/agents/$agent")({
  component: AgentChat,
});

const RUNTIME_URL =
  import.meta.env.VITE_COPILOTKIT_RUNTIME_URL ||
  (typeof window !== "undefined"
    ? `${window.location.protocol}//${window.location.host}/api/copilotkit`
    : "http://localhost:3082/api/copilotkit");

function AgentChat() {
  const { agent } = useParams({ from: "/en/agents/$agent" });
  const { setAgent, run } = useAgent({ agentId: agent });

  useEffect(() => {
    if (agent && setAgent) {
      setAgent(agent);
    }
  }, [agent, setAgent]);

  return (
    <div style={{ padding: "2rem", maxWidth: "900px", margin: "0 auto" }}>
      <header style={{ marginBottom: "2rem" }}>
        <h1 style={{ fontSize: "2rem", marginBottom: "0.5rem" }}>
          {agent.replace(/_/g, " ").toUpperCase()}
        </h1>
        <p style={{ color: "#666" }}>
          ADK agent for the {agent.replace(/_/g, " ")} curriculum. Streams responses via the AG-UI SSE endpoint.
        </p>
      </header>

      <CopilotKit runtimeUrl={RUNTIME_URL} agent={agent}>
        <div
          style={{
            border: "1px solid #ddd",
            borderRadius: "0.5rem",
            minHeight: "60vh",
            padding: "1rem",
          }}
        >
          <CopilotChat
            labels={{
              title: `${agent.replace(/_/g, " ")} Specialist`,
              initial: `Hello! I'm your ${agent.replace(/_/g, " ")} specialist. Ask me anything about the Irish curriculum.`,
            }}
            onSubmitMessage={(msg) => run(msg)}
          />
        </div>

        <footer style={{ marginTop: "1rem", fontSize: "0.875rem", color: "#888" }}>
          <p>
            The 9 ADK agents (8 NCCA subject specialists + 1 cianfhoghlaim operator) are registered in
            <code>apps/api/src/registry.ts</code>. All 14 CopilotKit actions are wired to real backends
            per the 2026-08-10-copilotkit-action-wiring-v1 change.
          </p>
        </footer>
      </CopilotKit>
    </div>
  );
}