/**
 * CopilotKit Integration
 *
 * Re-exports runtime configuration and provides hooks for frontend integration
 */

export {
  createCopilotRuntime,
  createLLMAdapter,
  executeToolCall,
  cryptoTools,
  CRYPTO_SYSTEM_PROMPT,
} from "./runtime";

// Client-side action definitions
export { cryptoComActions, getCryptoComActionDefinitions, CRYPTO_COM_SYSTEM_PROMPT } from "../mcp/copilot-actions";
