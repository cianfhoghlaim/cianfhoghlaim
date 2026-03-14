import { env } from "node:process";

import { serve  } from "@restatedev/restate-sdk";
import { agent } from "./agent.js";
import { agentExecutor } from "./agent_executor.js";
import { sandbox } from "./sandbox.js";
import { modal } from "./modal.js";


if (env.OPENAI_API_KEY === undefined) {
  console.warn(`
    -------------------------------------------------------------
    | ❌ WARNING: OPENAI_API_KEY is not set in the environment. |
    -------------------------------------------------------------
    `);
}

serve({
  services: [agent, agentExecutor, sandbox, modal],
  port: 9080,
});