/** PlaybackSurface — A2UI surface wrapper for the research_agent time-based playback.

Per the 2026-09-30-mega-3b-cocoindex-and-copilotkit-v1 change: this
is a thin wrapper around the canonical A2UISurfaceGenerator.
*/

"use client";

import { type FC } from "react";
import { A2UISurfaceGenerator, type PlaybackData } from "../_shared/A2UISurfaceGenerator";

export const PlaybackSurface: FC<{ data: PlaybackData }> = ({ data }) => (
  <A2UISurfaceGenerator surface="playback" data={data} />
);

export default PlaybackSurface;