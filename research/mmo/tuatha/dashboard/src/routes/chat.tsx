import { createFileRoute } from "@tanstack/react-router";
import { useCopilotChat } from "@copilotkit/react-core";
import { CopilotChat } from "@copilotkit/react-ui";
import { Bot, Sparkles, Server, Layers, Terminal } from "lucide-react";

export const Route = createFileRoute("/chat")({
  component: ChatPage,
});

function ChatPage() {
  return (
    <div className="container mx-auto px-4 py-12">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-primary/10 mb-4">
            <Bot className="h-8 w-8 text-primary" />
          </div>
          <h1 className="text-4xl font-bold mb-2">Selfhost Assistant</h1>
          <p className="text-muted-foreground max-w-xl mx-auto">
            AI-powered assistant for managing your homelab. Ask about stacks,
            deployments, infrastructure, or get help with configuration.
          </p>
        </div>

        {/* Capabilities */}
        <div className="grid md:grid-cols-3 gap-4 mb-8">
          <CapabilityCard
            icon={<Layers className="h-5 w-5" />}
            title="Stack Recommendations"
            description="Get personalized suggestions for self-hosted software"
          />
          <CapabilityCard
            icon={<Server className="h-5 w-5" />}
            title="Deployment Help"
            description="Step-by-step guidance for deploying to Komodo"
          />
          <CapabilityCard
            icon={<Terminal className="h-5 w-5" />}
            title="Config Generation"
            description="Generate Docker Compose and Ansible configs"
          />
        </div>

        {/* Chat Interface */}
        <div className="rounded-xl bg-card border border-border overflow-hidden">
          <div className="h-[500px]">
            <CopilotChat
              labels={{
                title: "Selfhost Assistant",
                initial: "Hi! I'm your selfhost assistant. I can help you:\n\n- Find and compare self-hosted software\n- Deploy stacks to your Komodo cluster\n- Generate configuration files\n- Troubleshoot issues\n\nWhat would you like help with?",
                placeholder: "Ask about stacks, deployments, or infrastructure...",
              }}
              className="h-full"
            />
          </div>
        </div>

        {/* Example Prompts */}
        <div className="mt-8">
          <h3 className="text-sm font-medium text-muted-foreground mb-4">
            Try asking:
          </h3>
          <div className="flex flex-wrap gap-2">
            {[
              "What analytics tools can I self-host?",
              "How do I deploy Langfuse to my cluster?",
              "Compare Excalidraw vs alternatives",
              "Generate a compose file for Glance",
              "What's the best LLM proxy solution?",
            ].map((prompt) => (
              <button
                key={prompt}
                className="px-4 py-2 rounded-lg bg-muted hover:bg-muted/80 text-sm transition-colors"
              >
                <Sparkles className="h-3 w-3 inline mr-2 text-primary" />
                {prompt}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

interface CapabilityCardProps {
  icon: React.ReactNode;
  title: string;
  description: string;
}

function CapabilityCard({ icon, title, description }: CapabilityCardProps) {
  return (
    <div className="rounded-lg bg-muted/50 p-4">
      <div className="flex items-center gap-2 text-primary mb-2">
        {icon}
        <span className="font-medium">{title}</span>
      </div>
      <p className="text-sm text-muted-foreground">{description}</p>
    </div>
  );
}
