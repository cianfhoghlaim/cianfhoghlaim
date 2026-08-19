/** ChartSurface — A2UI surface wrapper for the statistics_agent chart output.

Per the 2026-09-30-mega-3b-cocoindex-and-copilotkit-v1 + the
2026-11-25-mega-3c-marimo-and-integration-v1 change: this is a thin
wrapper around the canonical A2UISurfaceGenerator.

Replaces the hand-written chart implementation in
`web/apps/cianfhoghlaim/components/PipelineStatus.tsx` (P5).
*/

"use client";

import { type FC } from "react";
import { A2UISurfaceGenerator, type ChartData } from "../_shared/A2UISurfaceGenerator";

export const ChartSurface: FC<{ data: ChartData }> = ({ data }) => (
  <A2UISurfaceGenerator surface="chart" data={data} />
);

export default ChartSurface;