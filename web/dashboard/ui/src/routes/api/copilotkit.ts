import { createAPIFileRoute } from "@tanstack/start/api";
import {
  CopilotRuntime,
  copilotRuntimeNodeHttpEndpoint,
  HttpAgent,
} from "@copilotkit/runtime";

/**
 * CopilotKit Runtime API endpoint.
 *
 * Connects to the ADK backend for the education_assistant agent.
 * Uses the AG-UI protocol for streaming responses.
 */

// ADK backend agent configuration
const adkAgent = new HttpAgent({
  url: process.env.ADK_BACKEND_URL || "http://localhost:8000/api/agent",
  name: "education_assistant",
});

// Create CopilotKit runtime with ADK agent
const runtime = new CopilotRuntime({
  agents: {
    education_assistant: adkAgent,
  },
});

export const ServerRoute = createAPIFileRoute("/api/copilotkit")({
  POST: copilotRuntimeNodeHttpEndpoint({
    runtime,
    endpoint: "/api/copilotkit",
  }),
});
