// AG-UI stream — wraps an Agno Team's `team.run(stream=True, ...)` into the
// 5 AG-UI event types (text, tool_call, tool_result, agent_handoff, done).
// See docs/tuatha/AGENTS.md for the AG-UI event protocol.
import type { Team } from "agno/team";

export interface StageContext {
  stage: "aistear" | "primary" | "junior_cycle" | "senior_cycle" | "tertiary";
  subject: string;
  language: "en" | "ga";
}

export async function streamAGUI(
  request: Request,
  team: Team,
  context: StageContext,
): Promise<Response> {
  const body = (await request.json()) as {
    messages: Array<{ role: "user" | "assistant" | "system"; content: string }>;
  };

  // The real implementation:
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
            ? `Fáilte — is ag an bhfoireann ${context.stage} Oideachais mé. Conas is féidir liom cabhrú leat?`
            : `Welcome — I'm the ${context.stage} Cianfhoghlaim Oideachais team. How can I help you?`,
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
