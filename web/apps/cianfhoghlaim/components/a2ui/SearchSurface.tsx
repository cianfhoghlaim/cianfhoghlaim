/** SearchSurface — A2UI surface wrapper for the mcp_curriculum_agent curriculum search.

Per the 2026-09-30-mega-3b-cocoindex-and-copilotkit-v1 change: this
is a thin wrapper around the canonical A2UISurfaceGenerator.
*/

"use client";

import { type FC } from "react";
import { A2UISurfaceGenerator, type SearchData } from "../_shared/A2UISurfaceGenerator";

export const SearchSurface: FC<{ data: SearchData }> = ({ data }) => (
  <A2UISurfaceGenerator surface="search" data={data} />
);

export default SearchSurface;