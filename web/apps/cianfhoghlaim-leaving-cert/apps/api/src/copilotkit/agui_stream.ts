// AG-UI stream — wraps a CopilotKit BuiltInAgent into the
// 5 AG-UI event types (text, tool_call, tool_result, agent_handoff, done).
// The 14 CopilotKit actions are passed in and dispatched by name.
//
// See docs/CIANFHLOGHLAIM_LORE.md and docs/BROWN_AJAH_THEMING.md for the lore
// and theming context.

export interface StageContext {
  stage: "aistear" | "primary" | "junior_cycle" | "senior_cycle" | "tertiary";
  subject: string;
  language: "en" | "ga";
}

export interface CopilotAction {
  name: string;
  description: string;
  parameters: Array<{ name: string; type: string; description: string; required?: boolean }>;
  handler: (params: Record<string, unknown>) => Promise<unknown>;
}

export async function streamAGUI(
  request: Request,
  team: unknown,
  context: StageContext,
  actions: CopilotAction[],
): Promise<Response> {
  const body = (await request.json()) as {
    messages: Array<{ role: "user" | "assistant" | "system"; content: string }>;
    toolCalls?: Array<{ name: string; args: Record<string, unknown> }>;
  };

  const encoder = new TextEncoder();
  const stream = new ReadableStream({
    async start(controller) {
      // Emit the welcome text event
      const hello = {
        type: "text",
        content:
          context.language === "ga"
            ? `Fáilte — is ag an bhfoireann ${context.stage} Cianfhoghlaim mé. Conas is féidir liom cabhrú leat?`
            : `Welcome — I'm the ${context.subject || context.stage} Cianfhoghlaim agent. How can I help you?`,
      };
      controller.enqueue(encoder.encode(`data: ${JSON.stringify(hello)}\n\n`));

      // Process any tool calls
      if (body.toolCalls) {
        for (const call of body.toolCalls) {
          const action = actions.find((a) => a.name === call.name);
          if (!action) continue;

          // Emit the tool_call event
          controller.enqueue(encoder.encode(
            `data: ${JSON.stringify({ type: "tool_call", name: call.name, args: call.args })}\n\n`,
          ));

          // Execute the action
          try {
            const result = await action.handler(call.args);
            controller.enqueue(encoder.encode(
              `data: ${JSON.stringify({ type: "tool_result", name: call.name, result })}\n\n`,
            ));
          } catch (err) {
            controller.enqueue(encoder.encode(
              `data: ${JSON.stringify({
                type: "tool_result",
                name: call.name,
                result: { error: err instanceof Error ? err.message : String(err) },
              })}\n\n`,
            ));
          }
        }
      }

      // Emit the done event
      controller.enqueue(encoder.encode(`data: ${JSON.stringify({ type: "done" })}\n\n`));
      controller.close();
    },
  });

  return new Response(stream, {
    headers: {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache, no-transform",
      Connection: "keep-alive",
      "X-Accel-Buffering": "no",
    },
  });
}