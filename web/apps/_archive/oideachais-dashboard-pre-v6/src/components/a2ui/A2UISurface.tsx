/**
 * A2UI surface — the BIEP v3 dashboard declarative UI surface.
 *
 * Per the **2026-08-24-wave-6-frontend-tanstack-modernisation-v1** openspec
 * change (Wave 6.5). Mounts the `<CopilotKit a2ui={{ theme, schema }}>`
 * provider so the agent can emit createSurface / updateComponents /
 * updateDataModel operations that get rendered in-place.
 *
 * Usage:
 *   <A2UISurface threadId="biep-v3-task-123" />
 */

import { CopilotKit, CopilotSidebar } from "@copilotkit/react-core/v2";
import type { ReactNode } from "react";
import {
  BIEP_DASHBOARD_CATALOG,
  CIANFHOGHLAIM_THEME,
} from "./a2ui-renderer";

export interface A2UISurfaceProps {
  readonly threadId: string;
  readonly runtimeBase?: string;
  readonly children?: ReactNode;
}

export function A2UISurface({
  threadId,
  runtimeBase = "/api/copilotkit",
  children,
}: A2UISurfaceProps) {
  return (
    <CopilotKit
      runtimeUrl={`${runtimeBase}/${threadId}`}
      a2ui={{
        theme: CIANFHOGHLAIM_THEME,
        catalog: BIEP_DASHBOARD_CATALOG as never,
      }}
    >
      {children}
      <CopilotSidebar
        labels={{
          chatInputPlaceholder:
            "Ask the BIEP v3 dashboard agent (e.g. render the OCR confidence chart)",
          welcomeMessageText:
            "I can render A2UI surfaces for the BIEP v3 dashboards. Ask me to chart OCR confidence, comparison matrices, or model leaderboards.",
        }}
      />
    </CopilotKit>
  );
}

export { BIEP_DASHBOARD_CATALOG, CIANFHOGHLAIM_THEME };
