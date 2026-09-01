import { createFileRoute, Link } from "@tanstack/react-router";
import { Bot, ChevronRight, MessageSquare, Wrench } from "lucide-react";

export const Route = createFileRoute("/admin/agents/")({
  component: AgentsPage,
});

const agents = [
  {
    id: "tuath",
    name: "Tuath Agent",
    description: "Celtic language learning & mythology exploration for the educational MMO",
    status: "active" as const,
    model: "claude-opus-4-20250514",
    subAgents: [
      { id: "celtic_tutor", name: "Celtic Tutor", description: "Language learning support" },
      { id: "mythology_narrator", name: "Mythology Narrator", description: "Celtic folklore and stories" },
      { id: "quest_guide", name: "Quest Guide", description: "Game quest assistance" },
      { id: "research_assistant", name: "Research Assistant", description: "Deep curriculum research" },
    ],
    tools: ["curriculum_search", "mythology_query", "translation", "player_progress", "spatial_query"],
    endpoint: "http://localhost:8000/copilotkit",
    conversations24h: 145,
  },
  {
    id: "crypteolas",
    name: "Crypteolas Agent",
    description: "GitHub intelligence & DeFi analytics for crypto protocol research",
    status: "active" as const,
    model: "claude-opus-4-20250514",
    subAgents: [
      { id: "protocol_research", name: "Protocol Research", description: "DeFi protocol analysis" },
      { id: "code_analysis", name: "Code Analysis", description: "GitHub code search" },
      { id: "defi_analytics", name: "DeFi Analytics", description: "TVL and yield metrics" },
      { id: "documentation_agent", name: "Documentation", description: "Whitepaper and docs search" },
    ],
    tools: ["code_search", "document_search", "defi_metrics", "github_repository"],
    endpoint: "http://localhost:8001/api/agent",
    conversations24h: 78,
  },
  {
    id: "portal",
    name: "Portal Agent",
    description: "Infrastructure management and monitoring assistance",
    status: "inactive" as const,
    model: "claude-sonnet-4-20250514",
    subAgents: [
      { id: "stack_manager", name: "Stack Manager", description: "Manage bonneagar stacks" },
      { id: "pipeline_runner", name: "Pipeline Runner", description: "Run Dagster pipelines" },
    ],
    tools: ["stack_status", "stack_restart", "run_pipeline", "query_metrics"],
    endpoint: null,
    conversations24h: 0,
  },
];

function AgentsPage() {
  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold">Agent Registry</h1>
          <p className="text-muted-foreground">Manage ADK agents and their capabilities</p>
        </div>
        <Link
          to="/agents/chat"
          search={{ agent: "portal" }}
          className="flex items-center gap-2 bg-primary text-primary-foreground px-4 py-2 rounded-md hover:bg-primary/90"
        >
          <MessageSquare size={16} />
          Open Chat
        </Link>
      </div>

      {/* Agent Cards */}
      <div className="space-y-4">
        {agents.map((agent) => (
          <AgentCard key={agent.id} agent={agent} />
        ))}
      </div>
    </div>
  );
}

function AgentCard({ agent }: { agent: (typeof agents)[0] }) {
  return (
    <div className="bg-card rounded-lg border p-6">
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-start gap-4">
          <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center">
            <Bot className="text-primary" size={24} />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-lg font-semibold">{agent.name}</h2>
              <span
                className={`text-xs px-2 py-0.5 rounded ${
                  agent.status === "active"
                    ? "bg-status-healthy/20 text-status-healthy"
                    : "bg-muted text-muted-foreground"
                }`}
              >
                {agent.status}
              </span>
            </div>
            <p className="text-muted-foreground">{agent.description}</p>
          </div>
        </div>
        <div className="text-right text-sm">
          <div className="text-muted-foreground">24h Conversations</div>
          <div className="text-2xl font-bold">{agent.conversations24h}</div>
        </div>
      </div>

      {/* Sub-agents */}
      <div className="mb-4">
        <h3 className="text-sm font-medium mb-2 flex items-center gap-1">
          <Bot size={14} />
          Sub-agents
        </h3>
        <div className="grid grid-cols-4 gap-2">
          {agent.subAgents.map((sub) => (
            <div key={sub.id} className="bg-secondary/50 rounded p-2">
              <div className="text-sm font-medium">{sub.name}</div>
              <div className="text-xs text-muted-foreground">{sub.description}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Tools */}
      <div className="mb-4">
        <h3 className="text-sm font-medium mb-2 flex items-center gap-1">
          <Wrench size={14} />
          Tools
        </h3>
        <div className="flex flex-wrap gap-2">
          {agent.tools.map((tool) => (
            <span
              key={tool}
              className="text-xs bg-secondary px-2 py-1 rounded font-mono"
            >
              {tool}
            </span>
          ))}
        </div>
      </div>

      {/* Footer */}
      <div className="flex items-center justify-between pt-4 border-t">
        <div className="text-sm">
          <span className="text-muted-foreground">Model: </span>
          <span className="font-mono">{agent.model}</span>
        </div>
        {agent.endpoint && (
          <Link
            to="/agents/chat"
            search={{ agent: agent.id }}
            className="flex items-center gap-1 text-sm text-primary hover:underline"
          >
            Start Chat
            <ChevronRight size={14} />
          </Link>
        )}
      </div>
    </div>
  );
}
