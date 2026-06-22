// TODO: implement the CopilotKit runtime that connects the React chat
// interface to the Python Agno agent team. The runtime reads the
// LITELLM_BASE_URL + OPENAI_API_KEY env vars and proxies chat messages
// to the agent endpoints.

import type { ReactNode } from "react";

export interface CopilotRuntimeConfig {
  litellmBaseUrl: string;
  apiKey?: string;
  agentEndpoint: string;
}

export interface CopilotProviderProps {
  config: CopilotRuntimeConfig;
  children: ReactNode;
}

export function CopilotProvider(_props: CopilotProviderProps): JSX.Element {
  throw new Error("copilot/runtime: not yet implemented");
}
