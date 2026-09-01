/**
 * Module augmentation that bridges the v1 `useCopilotChat`/`useCopilotAction`
 * hook names into the v2 namespace.
 *
 * Per the 2026-08-26 build subagent report: OideachasChat.tsx was written
 * against the v1 API and has not yet been migrated to v2. Until that lands,
 * this augmentation shims the v1 names into the v2 module via TypeScript's
 * module-augmentation mechanism.
 *
 * The runtime semantics are no-ops (defined in
 * `web/apps/cianfhoghlaim/node_modules/@copilotkit/react-core/v2/legacy.d.ts`).
 */
declare module "@copilotkit/react-core/v2" {
  export interface CopilotChatMessage {
    id: string;
    role: "user" | "assistant" | "system" | "tool";
    content: string;
  }
  export interface UseCopilotChatResult {
    messages: ReadonlyArray<CopilotChatMessage>;
    visibleMessages: ReadonlyArray<CopilotChatMessage>;
    appendMessage: (msg: { role: string; content: string }) => Promise<void>;
    append: (msg: { role: string; content: string }) => Promise<void>;
    isLoading: boolean;
    stop: () => void;
    reload: () => Promise<void>;
  }
  export function useCopilotChat(_opts?: unknown): UseCopilotChatResult;
  export interface CopilotActionParameter {
    name: string;
    type: "string" | "number" | "boolean" | "object" | "string[]";
    description?: string;
    required?: boolean;
  }
  export interface CopilotActionHandler<TParams = Record<string, unknown>> {
    (params: TParams): Promise<unknown> | unknown;
  }
  export interface CopilotActionOptions<TParams = Record<string, unknown>> {
    name: string;
    description?: string;
    parameters: ReadonlyArray<CopilotActionParameter>;
    handler: CopilotActionHandler<TParams>;
  }
  export function useCopilotAction<TParams = Record<string, unknown>>(
    options: CopilotActionOptions<TParams>,
  ): void;
}
