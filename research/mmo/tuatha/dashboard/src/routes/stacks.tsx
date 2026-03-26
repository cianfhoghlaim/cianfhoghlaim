import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import {
  Search,
  Filter,
  ExternalLink,
  Github,
  Cpu,
  MemoryStick,
  Plus,
} from "lucide-react";

export const Route = createFileRoute("/stacks")({
  component: StacksPage,
});

// Stack data from config
const stacks = [
  {
    name: "rybbit",
    category: "engineering",
    subCategory: "analytics",
    description: "Privacy-focused analytics platform",
    repo: "rybbit-io/rybbit",
    memory: "512Mi",
    cpu: 0.5,
  },
  {
    name: "excalidraw",
    category: "engineering",
    subCategory: "collaboration",
    description: "Virtual whiteboard for sketching diagrams",
    repo: "excalidraw/excalidraw",
    memory: "256Mi",
    cpu: 0.25,
  },
  {
    name: "chartdb",
    category: "engineering",
    subCategory: "database",
    description: "Database diagram designer",
    repo: "chartdb/chartdb",
    memory: "256Mi",
    cpu: 0.25,
  },
  {
    name: "langfuse",
    category: "machine_learning",
    subCategory: "observability",
    description: "LLM observability and analytics",
    repo: "langfuse/langfuse",
    memory: "1Gi",
    cpu: 1.0,
  },
  {
    name: "agno",
    category: "machine_learning",
    subCategory: "agents",
    description: "Agent operating system",
    repo: "agno-agi/agno",
    memory: "512Mi",
    cpu: 0.5,
  },
  {
    name: "glance",
    category: "tools",
    subCategory: "dashboard",
    description: "Self-hosted dashboard",
    repo: "glanceapp/glance",
    memory: "128Mi",
    cpu: 0.1,
  },
  {
    name: "actual",
    category: "tools",
    subCategory: "finance",
    description: "Privacy-focused budgeting app",
    repo: "actualbudget/actual",
    memory: "256Mi",
    cpu: 0.25,
  },
  {
    name: "marimo",
    category: "engineering",
    subCategory: "notebooks",
    description: "Reactive Python notebooks",
    repo: "marimo-team/marimo",
    memory: "1Gi",
    cpu: 1.0,
  },
];

const categories = ["All", "engineering", "machine_learning", "tools"];

function StacksPage() {
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("All");

  const filteredStacks = stacks.filter((stack) => {
    const matchesSearch =
      search === "" ||
      stack.name.toLowerCase().includes(search.toLowerCase()) ||
      stack.description.toLowerCase().includes(search.toLowerCase());

    const matchesCategory =
      category === "All" || stack.category === category;

    return matchesSearch && matchesCategory;
  });

  return (
    <div className="container mx-auto px-4 py-12">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2">Stack Catalog</h1>
          <p className="text-muted-foreground">
            Browse self-hosted software options for your homelab
          </p>
        </div>

        {/* Filters */}
        <div className="flex flex-col md:flex-row gap-4 mb-8">
          {/* Search */}
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <input
              type="text"
              placeholder="Search stacks..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-10 pr-4 py-2 rounded-lg bg-muted border border-border focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>

          {/* Category Filter */}
          <div className="flex items-center gap-2">
            <Filter className="h-4 w-4 text-muted-foreground" />
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="px-4 py-2 rounded-lg bg-muted border border-border focus:outline-none focus:ring-2 focus:ring-primary"
            >
              {categories.map((cat) => (
                <option key={cat} value={cat}>
                  {cat === "All" ? "All Categories" : cat.replace("_", " ")}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Results Count */}
        <p className="text-sm text-muted-foreground mb-4">
          Showing {filteredStacks.length} of {stacks.length} stacks
        </p>

        {/* Stack Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredStacks.map((stack) => (
            <StackCard key={stack.name} stack={stack} />
          ))}
        </div>

        {filteredStacks.length === 0 && (
          <div className="text-center py-12 text-muted-foreground">
            No stacks found matching your criteria
          </div>
        )}
      </div>
    </div>
  );
}

interface Stack {
  name: string;
  category: string;
  subCategory: string;
  description: string;
  repo: string;
  memory: string;
  cpu: number;
}

function StackCard({ stack }: { stack: Stack }) {
  const categoryColors: Record<string, string> = {
    engineering: "bg-blue-500/10 text-blue-500",
    machine_learning: "bg-purple-500/10 text-purple-500",
    tools: "bg-green-500/10 text-green-500",
  };

  return (
    <div className="rounded-xl bg-card border border-border p-6 hover:border-primary/50 transition-colors">
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div>
          <h3 className="font-semibold text-lg">{stack.name}</h3>
          <span
            className={`inline-block px-2 py-0.5 text-xs rounded-full ${
              categoryColors[stack.category] || "bg-muted text-muted-foreground"
            }`}
          >
            {stack.subCategory}
          </span>
        </div>
        <a
          href={`https://github.com/${stack.repo}`}
          target="_blank"
          rel="noopener noreferrer"
          className="p-1.5 rounded-md hover:bg-muted transition-colors"
        >
          <Github className="h-4 w-4 text-muted-foreground" />
        </a>
      </div>

      {/* Description */}
      <p className="text-sm text-muted-foreground mb-4">{stack.description}</p>

      {/* Resources */}
      <div className="flex items-center gap-4 text-xs text-muted-foreground mb-4">
        <span className="flex items-center gap-1">
          <MemoryStick className="h-3 w-3" />
          {stack.memory}
        </span>
        <span className="flex items-center gap-1">
          <Cpu className="h-3 w-3" />
          {stack.cpu} CPU
        </span>
      </div>

      {/* Actions */}
      <div className="flex items-center gap-2">
        <button className="flex-1 flex items-center justify-center gap-2 px-4 py-2 rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 transition-colors text-sm font-medium">
          <Plus className="h-4 w-4" />
          Deploy
        </button>
        <a
          href={`https://github.com/${stack.repo}`}
          target="_blank"
          rel="noopener noreferrer"
          className="px-4 py-2 rounded-lg bg-muted hover:bg-muted/80 transition-colors text-sm"
        >
          <ExternalLink className="h-4 w-4" />
        </a>
      </div>
    </div>
  );
}
