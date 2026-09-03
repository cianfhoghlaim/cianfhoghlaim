/** TranslatorSurface — A2UI surface wrapper for the translation_agent EN ↔ GA translation.

Per the 2026-09-30-mega-3b-cocoindex-and-copilotkit-v1 change: this
is a thin wrapper around the canonical A2UISurfaceGenerator.
*/

"use client";

import { type FC } from "react";
import { A2UISurfaceGenerator, type TranslatorData } from "../_shared/A2UISurfaceGenerator";

export const TranslatorSurface: FC<{ data: TranslatorData }> = ({ data }) => (
  <A2UISurfaceGenerator surface="translator" data={data} />
);

export default TranslatorSurface;