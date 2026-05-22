import { create } from "zustand";

export interface GraphNode {
  id: string;
  label: string;
  type: "Token" | "Protocol" | "Exchange" | "LiquidityPool" | "Document" | "Risk" | "Wallet";
  properties?: Record<string, unknown>;
}

export interface GraphLink {
  source: string;
  target: string;
  type: string;
  properties?: Record<string, unknown>;
}

export interface GraphData {
  nodes: GraphNode[];
  links: GraphLink[];
}

interface GraphState {
  // Graph data
  graphData: GraphData;
  isLoading: boolean;
  error: string | null;

  // UI state
  selectedNode: GraphNode | null;
  highlightedNodes: Set<string>;
  filterTypes: Set<string>;
  searchQuery: string;
  zoomLevel: number;

  // Actions
  setGraphData: (data: GraphData) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  selectNode: (node: GraphNode | null) => void;
  highlightNodes: (nodeIds: string[]) => void;
  clearHighlight: () => void;
  toggleFilterType: (type: string) => void;
  setSearchQuery: (query: string) => void;
  setZoomLevel: (level: number) => void;
  fetchGraphData: (query?: string) => Promise<void>;
  getFilteredData: () => GraphData;
}

export const useGraphStore = create<GraphState>((set, get) => ({
  graphData: { nodes: [], links: [] },
  isLoading: false,
  error: null,
  selectedNode: null,
  highlightedNodes: new Set(),
  filterTypes: new Set(["Token", "Protocol", "Exchange", "Document", "Risk"]),
  searchQuery: "",
  zoomLevel: 1,

  setGraphData: (data) => set({ graphData: data }),
  setLoading: (loading) => set({ isLoading: loading }),
  setError: (error) => set({ error }),
  selectNode: (node) => set({ selectedNode: node }),

  highlightNodes: (nodeIds) =>
    set({ highlightedNodes: new Set(nodeIds) }),

  clearHighlight: () => set({ highlightedNodes: new Set() }),

  toggleFilterType: (type) =>
    set((state) => {
      const newTypes = new Set(state.filterTypes);
      if (newTypes.has(type)) {
        newTypes.delete(type);
      } else {
        newTypes.add(type);
      }
      return { filterTypes: newTypes };
    }),

  setSearchQuery: (query) => set({ searchQuery: query }),
  setZoomLevel: (level) => set({ zoomLevel: level }),

  fetchGraphData: async (query?: string) => {
    set({ isLoading: true, error: null });

    try {
      // In production, this would call the API
      // const response = await fetch(`/api/graph?q=${encodeURIComponent(query || '')}`);
      // const data = await response.json();

      // Mock data for demo
      const mockData: GraphData = {
        nodes: [
          { id: "ethena", label: "Ethena", type: "Protocol" },
          { id: "usde", label: "USDe", type: "Token" },
          { id: "susde", label: "sUSDe", type: "Token" },
          { id: "aave", label: "Aave v3", type: "Protocol" },
          { id: "pendle", label: "Pendle", type: "Protocol" },
          { id: "binance", label: "Binance", type: "Exchange" },
          { id: "uniswap", label: "Uniswap", type: "Exchange" },
          { id: "audit-zellic", label: "Zellic Audit", type: "Document" },
          { id: "risk-funding", label: "Funding Rate Risk", type: "Risk" },
        ],
        links: [
          { source: "ethena", target: "usde", type: "ISSUES" },
          { source: "ethena", target: "susde", type: "ISSUES" },
          { source: "usde", target: "binance", type: "TRADES_ON" },
          { source: "usde", target: "uniswap", type: "TRADES_ON" },
          { source: "susde", target: "aave", type: "INTEGRATES" },
          { source: "susde", target: "pendle", type: "INTEGRATES" },
          { source: "ethena", target: "audit-zellic", type: "AUDITED_BY" },
          { source: "ethena", target: "risk-funding", type: "HAS_RISK" },
        ],
      };

      // Simulate API delay
      await new Promise((resolve) => setTimeout(resolve, 500));

      set({ graphData: mockData, isLoading: false });
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : "Failed to fetch graph data",
        isLoading: false,
      });
    }
  },

  getFilteredData: () => {
    const { graphData, filterTypes, searchQuery } = get();

    let nodes = graphData.nodes.filter((n) => filterTypes.has(n.type));

    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      nodes = nodes.filter(
        (n) =>
          n.label.toLowerCase().includes(query) ||
          n.type.toLowerCase().includes(query)
      );
    }

    const nodeIds = new Set(nodes.map((n) => n.id));
    const links = graphData.links.filter(
      (l) => nodeIds.has(l.source) && nodeIds.has(l.target)
    );

    return { nodes, links };
  },
}));
