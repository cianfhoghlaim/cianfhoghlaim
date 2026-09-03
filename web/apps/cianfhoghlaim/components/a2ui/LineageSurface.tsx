/** LineageSurface — A2UI surface wrapper for the curriculum_agent per-page PDF.js lineage.

Per the 2026-09-30-mega-3b-cocoindex-and-copilotkit-v1 change: this
is a thin wrapper around the canonical A2UISurfaceGenerator.

Replaces the hand-written lineage implementation in the BIEP v3
lineage viewer.
*/

"use client";

import { type FC } from "react";
import { A2UISurfaceGenerator, type LineageData } from "../_shared/A2UISurfaceGenerator";

export const LineageSurface: FC<{ data: LineageData }> = ({ data }) => (
  <A2UISurfaceGenerator surface="lineage" data={data} />
);

export default LineageSurface;