/** GraphSurface — A2UI surface wrapper for the corpus_agent knowledge graph output.

Per the 2026-09-30-mega-3b-cocoindex-and-copilotkit-v1 change: this
is a thin wrapper around the canonical A2UISurfaceGenerator.

Replaces the hand-written graph implementation in
`web/apps/cianfhoghlaim/components/KnowledgeGraphPanel.tsx`.
*/

"use client";

import { type FC } from "react";
import { A2UISurfaceGenerator, type GraphData } from "../_shared/A2UISurfaceGenerator";

export const GraphSurface: FC<{ data: GraphData }> = ({ data }) => (
  <A2UISurfaceGenerator surface="graph" data={data} />
);

export default GraphSurface;