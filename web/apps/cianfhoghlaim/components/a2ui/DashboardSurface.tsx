/** DashboardSurface — A2UI surface wrapper for the curriculum_comparison_agent cross-jurisdiction comparison.

Per the 2026-09-30-mega-3b-cocoindex-and-copilotkit-v1 change: this
is a thin wrapper around the canonical A2UISurfaceGenerator.
*/

"use client";

import { type FC } from "react";
import { A2UISurfaceGenerator, type DashboardData } from "../_shared/A2UISurfaceGenerator";

export const DashboardSurface: FC<{ data: DashboardData }> = ({ data }) => (
  <A2UISurfaceGenerator surface="dashboard" data={data} />
);

export default DashboardSurface;