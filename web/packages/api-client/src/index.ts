/**
 * @cianfhoghlaim/api-client — the canonical 2026 frontend client stack.
 *
 * Per the **2026-08-24-wave-6-frontend-tanstack-modernisation-v1**
 * openspec change. Consolidates:
 *
 *  - TanStack AI (`@tanstack/ai`) — LLM integration
 *  - TanStack DB (`@tanstack/db`) — reactive queries (replaces TanStack Query for many use cases)
 *  - TanStack Form (`@tanstack/react-form`) — form management
 *  - CopilotKit v2 (`@copilotkit/react-core`, `@copilotkit/runtime-client-gql`) — agent chat + generative UI
 *  - AG-UI client (`@ag-ui/client`) — the Agent-User Interaction protocol client
 *
 * The 5 web apps (`cianfhoghlaim`, `oideachais`, `croilar`, `tuatha`,
 * `game_showcase`) all import from this single package — consolidating
 * the 3 previous installs of CopilotKit + AG-UI + TanStack Query.
 *
 * Reference: openspec/changes/2026-08-24-wave-6-frontend-tanstack-modernisation-v1
 */

export * from "./copilotkit";
export * from "./tanstack";
export * from "./agui";
