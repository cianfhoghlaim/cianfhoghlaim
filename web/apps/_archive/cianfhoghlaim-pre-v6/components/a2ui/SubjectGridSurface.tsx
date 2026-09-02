/** SubjectGridSurface — A2UI surface wrapper for the root_agent 8 NCCA JC subjects grid.

Per the 2026-09-30-mega-3b-cocoindex-and-copilotkit-v1 change: this
is a thin wrapper around the canonical A2UISurfaceGenerator.

Replaces the hand-written subject grid in
`web/apps/cianfhoghlaim/components/SubjectAgentGrid.tsx`.
*/

"use client";

import { type FC } from "react";
import { A2UISurfaceGenerator, type SubjectGridData } from "../_shared/A2UISurfaceGenerator";

export const SubjectGridSurface: FC<{ data: SubjectGridData }> = ({ data }) => (
  <A2UISurfaceGenerator surface="subject_grid" data={data} />
);

export default SubjectGridSurface;