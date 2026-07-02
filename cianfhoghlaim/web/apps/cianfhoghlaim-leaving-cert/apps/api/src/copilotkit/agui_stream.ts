// AG-UI stream — wraps a CopilotKit BuiltInAgent into the
// 5 AG-UI event types (text, tool_call, tool_result, agent_handoff, done).
// See docs/CIANFHLOGHLAIM_LORE.md and docs/BROWN_AJAH_THEMING.md for the lore
// and theming context.

export interface StageContext {
  stage: "aistear" | "primary" | "junior_cycle" | "senior_cycle" | "tertiary";
  subject: string;
  language: "en" | "ga";
}

export async function streamAGUI(
  request: Request,
  team: unknown,
  context: StageContext,
): Promise<Response> {
  const body = (await request.json()) as {
    messages: Array<{ role: "user" | "assistant" | "system"; content: string }>;
  };

  // Real implementation:
  //   for await (const event of team.arun({ messages: body.messages, stream: true })) {
  //     yield { type: "text", content: event.content }          // text
  //     yield { type: "tool_call", name: ..., args: ... }       // tool_call
  //     yield { type: "tool_result", result: ... }              // tool_result
  //     yield { type: "agent_handoff", from: ..., to: ... }     // agent_handoff
  //     yield { type: "done" }                                   // done
  //   }
  //
  // For now we return a stub SSE stream that emits one text event + done.
  const encoder = new TextEncoder();
  const stream = new ReadableStream({
    start(controller) {
      const hello = {
        type: "text",
        content:
          context.language === "ga"
            ? `Fáilte — is ag an bhfoireann ${context.stage} Cianfhoghlaim mé. Conas is féidir liom cabhrú leat?`
            : `Welcome — I'm the ${context.subject || context.stage} Cianfhoghlaim agent. How can I help you?`,
      };
      const done = { type: "done" };
      controller.enqueue(encoder.encode(`data: ${JSON.stringify(hello)}\n\n`));
      controller.enqueue(encoder.encode(`data: ${JSON.stringify(done)}\n\n`));
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