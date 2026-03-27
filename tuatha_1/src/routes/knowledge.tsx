import { createFileRoute } from "@tanstack/react-router";
import { KnowledgeGraph } from "../components/graph/KnowledgeGraph";
import { useState, useMemo } from "react";
import { cn } from "../lib/utils";

export const Route = createFileRoute("/knowledge")({
  component: KnowledgePage,
});

interface GraphNode {
  id: string;
  label: string;
  type: "Token" | "Protocol" | "Exchange" | "LiquidityPool" | "Document" | "Risk";
}

interface GraphLink {
  source: string;
  target: string;
  type: string;
}

// Extended graph data
const allNodes: GraphNode[] = [
  // Protocols
  { id: "ethena", label: "Ethena", type: "Protocol" },
  { id: "aave", label: "Aave v3", type: "Protocol" },
  { id: "pendle", label: "Pendle", type: "Protocol" },
  { id: "lido", label: "Lido", type: "Protocol" },
  { id: "curve", label: "Curve", type: "Protocol" },
  { id: "compound", label: "Compound", type: "Protocol" },
  { id: "makerdao", label: "MakerDAO", type: "Protocol" },

  // Tokens
  { id: "usde", label: "USDe", type: "Token" },
  { id: "susde", label: "sUSDe", type: "Token" },
  { id: "steth", label: "stETH", type: "Token" },
  { id: "weth", label: "WETH", type: "Token" },
  { id: "usdc", label: "USDC", type: "Token" },
  { id: "dai", label: "DAI", type: "Token" },
  { id: "crv", label: "CRV", type: "Token" },

  // Exchanges
  { id: "binance", label: "Binance", type: "Exchange" },
  { id: "uniswap", label: "Uniswap", type: "Exchange" },
  { id: "bybit", label: "Bybit", type: "Exchange" },

  // Documents
  { id: "audit-zellic", label: "Zellic Audit", type: "Document" },
  { id: "audit-spearbit", label: "Spearbit Audit", type: "Document" },
  { id: "whitepaper-ethena", label: "Ethena Whitepaper", type: "Document" },

  // Risks
  { id: "risk-funding", label: "Funding Rate Risk", type: "Risk" },
  { id: "risk-custodial", label: "Custodial Risk", type: "Risk" },
];

const allLinks: GraphLink[] = [
  // Ethena ecosystem
  { source: "ethena", target: "usde", type: "ISSUES" },
  { source: "ethena", target: "susde", type: "ISSUES" },
  { source: "ethena", target: "steth", type: "USES_COLLATERAL" },
  { source: "ethena", target: "audit-zellic", type: "AUDITED_BY" },
  { source: "ethena", target: "audit-spearbit", type: "AUDITED_BY" },
  { source: "ethena", target: "whitepaper-ethena", type: "DOCUMENTED_IN" },
  { source: "ethena", target: "risk-funding", type: "HAS_RISK" },
  { source: "ethena", target: "risk-custodial", type: "HAS_RISK" },

  // Token trading
  { source: "usde", target: "binance", type: "TRADES_ON" },
  { source: "usde", target: "uniswap", type: "TRADES_ON" },
  { source: "usde", target: "bybit", type: "TRADES_ON" },
  { source: "susde", target: "uniswap", type: "TRADES_ON" },

  // Protocol integrations
  { source: "susde", target: "aave", type: "INTEGRATES" },
  { source: "susde", target: "pendle", type: "INTEGRATES" },
  { source: "steth", target: "lido", type: "ISSUED_BY" },
  { source: "steth", target: "aave", type: "COLLATERAL_IN" },
  { source: "steth", target: "curve", type: "LIQUIDITY_IN" },

  // Lido ecosystem
  { source: "lido", target: "steth", type: "ISSUES" },
  { source: "lido", target: "weth", type: "USES_COLLATERAL" },

  // Curve ecosystem
  { source: "curve", target: "crv", type: "ISSUES" },
  { source: "curve", target: "usdc", type: "LIQUIDITY_IN" },
  { source: "curve", target: "dai", type: "LIQUIDITY_IN" },

  // MakerDAO
  { source: "makerdao", target: "dai", type: "ISSUES" },
  { source: "makerdao", target: "weth", type: "USES_COLLATERAL" },
];

const nodeTypes = ["All", "Token", "Protocol", "Exchange", "Document", "Risk"] as const;

export default function KnowledgePage() {
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [filterType, setFilterType] = useState<string>("All");
  const [searchQuery, setSearchQuery] = useState("");

  const filteredData = useMemo(() => {
    let nodes = allNodes;
    let links = allLinks;

    // Filter by type
    if (filterType !== "All") {
      nodes = nodes.filter((n) => n.type === filterType);
      const nodeIds = new Set(nodes.map((n) => n.id));
      links = links.filter(
        (l) => nodeIds.has(l.source) && nodeIds.has(l.target)
      );
    }

    // Filter by search
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      nodes = nodes.filter(
        (n) =>
          n.label.toLowerCase().includes(query) ||
          n.type.toLowerCase().includes(query)
      );
      const nodeIds = new Set(nodes.map((n) => n.id));
      links = links.filter(
        (l) => nodeIds.has(l.source) && nodeIds.has(l.target)
      );
    }

    return { nodes, links };
  }, [filterType, searchQuery]);

  const getConnectedNodes = (nodeId: string) => {
    const connected: { node: GraphNode; relationship: string }[] = [];

    allLinks.forEach((link) => {
      if (link.source === nodeId) {
        const targetNode = allNodes.find((n) => n.id === link.target);
        if (targetNode) {
          connected.push({ node: targetNode, relationship: link.type });
        }
      }
      if (link.target === nodeId) {
        const sourceNode = allNodes.find((n) => n.id === link.source);
        if (sourceNode) {
          connected.push({ node: sourceNode, relationship: link.type });
        }
      }
    });

    return connected;
  };

  return (
    <div className="flex h-[calc(100vh-4rem)]">
      {/* Sidebar */}
      <div className="w-80 border-r bg-card overflow-y-auto">
        <div className="p-4 border-b">
          <h2 className="font-semibold mb-3">Knowledge Graph</h2>
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search entities..."
            className="w-full rounded-lg border bg-background px-3 py-2 text-sm"
          />
        </div>

        <div className="p-4 border-b">
          <p className="text-sm text-muted-foreground mb-2">Filter by type</p>
          <div className="flex flex-wrap gap-2">
            {nodeTypes.map((type) => (
              <button
                key={type}
                onClick={() => setFilterType(type)}
                className={cn(
                  "rounded-full px-3 py-1 text-sm transition-colors",
                  filterType === type
                    ? "bg-primary text-primary-foreground"
                    : "bg-muted hover:bg-muted/80"
                )}
              >
                {type}
              </button>
            ))}
          </div>
        </div>

        {/* Stats */}
        <div className="p-4 border-b">
          <div className="grid grid-cols-2 gap-4 text-center">
            <div>
              <p className="text-2xl font-bold">{filteredData.nodes.length}</p>
              <p className="text-xs text-muted-foreground">Entities</p>
            </div>
            <div>
              <p className="text-2xl font-bold">{filteredData.links.length}</p>
              <p className="text-xs text-muted-foreground">Relationships</p>
            </div>
          </div>
        </div>

        {/* Selected Node Details */}
        {selectedNode ? (
          <div className="p-4">
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-semibold">{selectedNode.label}</h3>
              <button
                onClick={() => setSelectedNode(null)}
                className="text-muted-foreground hover:text-foreground"
              >
                ✕
              </button>
            </div>
            <span
              className={cn(
                "inline-block rounded-full px-2 py-0.5 text-xs mb-4",
                selectedNode.type === "Token" && "bg-blue-500/10 text-blue-500",
                selectedNode.type === "Protocol" &&
                  "bg-green-500/10 text-green-500",
                selectedNode.type === "Exchange" &&
                  "bg-amber-500/10 text-amber-500",
                selectedNode.type === "Document" &&
                  "bg-gray-500/10 text-gray-500",
                selectedNode.type === "Risk" && "bg-red-500/10 text-red-500"
              )}
            >
              {selectedNode.type}
            </span>

            <p className="text-sm font-medium mb-2">Connections</p>
            <div className="space-y-2">
              {getConnectedNodes(selectedNode.id).map(
                ({ node, relationship }, i) => (
                  <div
                    key={i}
                    onClick={() => setSelectedNode(node)}
                    className="flex items-center gap-2 rounded-lg border p-2 text-sm cursor-pointer hover:bg-muted"
                  >
                    <span
                      className={cn(
                        "h-2 w-2 rounded-full",
                        node.type === "Token" && "bg-blue-500",
                        node.type === "Protocol" && "bg-green-500",
                        node.type === "Exchange" && "bg-amber-500",
                        node.type === "Document" && "bg-gray-500",
                        node.type === "Risk" && "bg-red-500"
                      )}
                    />
                    <div className="flex-1 min-w-0">
                      <p className="font-medium truncate">{node.label}</p>
                      <p className="text-xs text-muted-foreground">
                        {relationship}
                      </p>
                    </div>
                  </div>
                )
              )}
            </div>
          </div>
        ) : (
          <div className="p-4">
            <p className="text-sm text-muted-foreground">
              Click on a node in the graph to view its connections and details.
            </p>
          </div>
        )}
      </div>

      {/* Graph */}
      <div className="flex-1 relative">
        <KnowledgeGraph
          nodes={filteredData.nodes}
          links={filteredData.links}
          onNodeClick={(node) => setSelectedNode(node as GraphNode)}
          width={800}
          height={600}
        />

        {/* Legend */}
        <div className="absolute bottom-4 left-4 rounded-lg border bg-card/90 backdrop-blur p-3">
          <p className="text-xs font-medium mb-2">Legend</p>
          <div className="flex flex-wrap gap-3">
            {[
              { type: "Token", color: "bg-blue-500" },
              { type: "Protocol", color: "bg-green-500" },
              { type: "Exchange", color: "bg-amber-500" },
              { type: "Document", color: "bg-gray-500" },
              { type: "Risk", color: "bg-red-500" },
            ].map((item) => (
              <div key={item.type} className="flex items-center gap-1">
                <span className={cn("h-2 w-2 rounded-full", item.color)} />
                <span className="text-xs">{item.type}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
