import { useCallback, useRef, useMemo } from "react";
import ForceGraph2D from "react-force-graph-2d";

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

interface KnowledgeGraphProps {
  nodes?: GraphNode[];
  links?: GraphLink[];
  onNodeClick?: (node: GraphNode) => void;
  width?: number;
  height?: number;
}

// Mock data for demonstration
const mockNodes: GraphNode[] = [
  { id: "ethena", label: "Ethena", type: "Protocol" },
  { id: "usde", label: "USDe", type: "Token" },
  { id: "susde", label: "sUSDe", type: "Token" },
  { id: "aave", label: "Aave v3", type: "Protocol" },
  { id: "pendle", label: "Pendle", type: "Protocol" },
  { id: "binance", label: "Binance", type: "Exchange" },
  { id: "uniswap", label: "Uniswap", type: "Exchange" },
  { id: "audit-zellic", label: "Zellic Audit", type: "Document" },
];

const mockLinks: GraphLink[] = [
  { source: "ethena", target: "usde", type: "ISSUES" },
  { source: "ethena", target: "susde", type: "ISSUES" },
  { source: "usde", target: "binance", type: "TRADES_ON" },
  { source: "usde", target: "uniswap", type: "TRADES_ON" },
  { source: "susde", target: "aave", type: "INTEGRATES" },
  { source: "susde", target: "pendle", type: "INTEGRATES" },
  { source: "ethena", target: "audit-zellic", type: "AUDITED_BY" },
];

export function KnowledgeGraph({
  nodes = mockNodes,
  links = mockLinks,
  onNodeClick,
  width = 800,
  height = 600,
}: KnowledgeGraphProps) {
  const graphRef = useRef<any>();

  const nodeColorMap: Record<GraphNode["type"], string> = {
    Token: "#3b82f6",      // blue
    Protocol: "#10b981",   // green
    Exchange: "#f59e0b",   // amber
    LiquidityPool: "#8b5cf6", // purple
    Document: "#6b7280",   // gray
    Risk: "#ef4444",       // red
  };

  const graphData = useMemo(
    () => ({
      nodes: nodes.map((n) => ({ ...n, color: nodeColorMap[n.type] })),
      links,
    }),
    [nodes, links]
  );

  const handleNodeClick = useCallback(
    (node: any) => {
      if (onNodeClick) {
        onNodeClick(node);
      }
      // Center on node
      if (graphRef.current) {
        graphRef.current.centerAt(node.x, node.y, 1000);
        graphRef.current.zoom(2, 1000);
      }
    },
    [onNodeClick]
  );

  return (
    <div className="rounded-lg border bg-card">
      <ForceGraph2D
        ref={graphRef}
        graphData={graphData}
        width={width}
        height={height}
        nodeLabel={(node: any) => `${node.type}: ${node.label}`}
        nodeColor={(node: any) => node.color}
        nodeRelSize={6}
        linkLabel={(link: any) => link.type}
        linkColor={() => "#666"}
        linkDirectionalArrowLength={4}
        linkDirectionalArrowRelPos={1}
        onNodeClick={handleNodeClick}
        cooldownTicks={100}
        nodeCanvasObject={(node: any, ctx, globalScale) => {
          const label = node.label;
          const fontSize = 12 / globalScale;
          ctx.font = `${fontSize}px Sans-Serif`;
          ctx.fillStyle = node.color;
          ctx.beginPath();
          ctx.arc(node.x, node.y, 5, 0, 2 * Math.PI);
          ctx.fill();
          ctx.fillStyle = "#fff";
          ctx.textAlign = "center";
          ctx.textBaseline = "middle";
          ctx.fillText(label, node.x, node.y + 12);
        }}
      />
    </div>
  );
}
