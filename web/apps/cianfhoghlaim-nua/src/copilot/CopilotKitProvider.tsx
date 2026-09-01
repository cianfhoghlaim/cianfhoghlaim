/**
 * CopilotKitProvider — the unified CopilotKit + A2UI provider for
 * the consolidated cianfhoghlaim-nua app.
 *
 * Per the 2026-09-01-cianfhoghlaim-nua-web-consolidation-v1 change.
 * Mounts `createCatalog()` from `@cianfhoghlaim/a2ui` (Phase 2)
 * so all 11 A2UI components are available to every route in the
 * 6 route groups.
 */

import * as React from "react";
import { CopilotKit } from "@copilotkit/react-core";

import { createCatalog } from "@cianfhoghlaim/a2ui";

export interface CopilotKitProviderProps {
  children: React.ReactNode;
  runtimeUrl?: string;
  agent?: string;
}

export function CopilotKitProvider({
  children,
  runtimeUrl = "/api/copilotkit",
  agent = "cianfhoghlaim",
}: CopilotKitProviderProps): React.ReactElement {
  return (
    <CopilotKit runtimeUrl={runtimeUrl} agent={agent}>
      {createCatalog()}
      {children}
    </CopilotKit>
  );
}

export default CopilotKitProvider;