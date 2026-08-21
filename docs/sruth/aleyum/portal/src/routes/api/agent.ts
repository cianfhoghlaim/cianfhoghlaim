import { createFileRoute } from "@tanstack/react-router";
import { EventType } from "@/lib/agui/types";

// Browser agent backend URL
const BROWSER_AGENT_URL =
  process.env.BROWSER_AGENT_URL || "http://localhost:8002";

// Helper to format SSE events
function formatSSE(event: { type: string; [key: string]: unknown }): string {
  return `data: ${JSON.stringify(event)}\n\n`;
}

export const Route = createFileRoute("/api/agent")({
  server: {
    handlers: {
      POST: async ({ request }) => {
        const body = await request.json();
        const { message, messages } = body;

        // Create a readable stream for SSE
        const stream = new ReadableStream({
          async start(controller) {
            const encoder = new TextEncoder();
            const runId = `run_${Date.now()}`;
            const messageId = `msg_${Date.now()}`;

            try {
              // Emit RUN_STARTED
              controller.enqueue(
                encoder.encode(
                  formatSSE({
                    type: EventType.RUN_STARTED,
                    runId,
                    timestamp: new Date().toISOString(),
                  })
                )
              );

              // Try to connect to browser agent backend
              try {
                const agentResponse = await fetch(
                  `${BROWSER_AGENT_URL}/api/chat`,
                  {
                    method: "POST",
                    headers: {
                      "Content-Type": "application/json",
                      Accept: "text/event-stream",
                    },
                    body: JSON.stringify({ message, messages }),
                  }
                );

                if (agentResponse.ok && agentResponse.body) {
                  // Stream events from backend
                  const reader = agentResponse.body.getReader();
                  const decoder = new TextDecoder();
                  let buffer = "";

                  while (true) {
                    const { done, value } = await reader.read();
                    if (done) break;

                    buffer += decoder.decode(value, { stream: true });
                    const lines = buffer.split("\n");
                    buffer = lines.pop() || "";

                    for (const line of lines) {
                      if (line.startsWith("data: ")) {
                        // Pass through events from backend
                        controller.enqueue(encoder.encode(line + "\n\n"));
                      }
                    }
                  }
                } else {
                  // Fallback to simulated response if backend unavailable
                  await simulateResponse(controller, encoder, message, messageId);
                }
              } catch (err) {
                // Backend not available, use simulated response
                console.warn("Browser agent unavailable, using simulation");
                await simulateResponse(controller, encoder, message, messageId);
              }

              // Emit RUN_FINISHED
              controller.enqueue(
                encoder.encode(
                  formatSSE({
                    type: EventType.RUN_FINISHED,
                    runId,
                    timestamp: new Date().toISOString(),
                  })
                )
              );
            } catch (err) {
              // Emit RUN_ERROR
              controller.enqueue(
                encoder.encode(
                  formatSSE({
                    type: EventType.RUN_ERROR,
                    runId,
                    error: {
                      code: "AGENT_ERROR",
                      message:
                        err instanceof Error ? err.message : "Unknown error",
                    },
                    timestamp: new Date().toISOString(),
                  })
                )
              );
            } finally {
              controller.enqueue(encoder.encode("data: [DONE]\n\n"));
              controller.close();
            }
          },
        });

        return new Response(stream, {
          headers: {
            "Content-Type": "text/event-stream",
            "Cache-Control": "no-cache",
            Connection: "keep-alive",
          },
        });
      },

      GET: () => {
        return Response.json({
          name: "Aleyum Portal Agent",
          version: "1.0.0",
          description: "AG-UI compatible agent endpoint",
          capabilities: ["chat", "tools", "streaming"],
          status: "online",
        });
      },
    },
  },
});

// Simulate AG-UI response when backend is unavailable
async function simulateResponse(
  controller: ReadableStreamDefaultController,
  encoder: TextEncoder,
  message: string,
  messageId: string
) {
  const response = getSimulatedResponse(message);

  // Emit TEXT_MESSAGE_START
  controller.enqueue(
    encoder.encode(
      formatSSE({
        type: EventType.TEXT_MESSAGE_START,
        messageId,
        timestamp: new Date().toISOString(),
      })
    )
  );

  // Stream response character by character
  for (let i = 0; i < response.length; i += 5) {
    await new Promise((resolve) => setTimeout(resolve, 20));
    controller.enqueue(
      encoder.encode(
        formatSSE({
          type: EventType.TEXT_MESSAGE_CONTENT,
          messageId,
          content: response.slice(i, i + 5),
          timestamp: new Date().toISOString(),
        })
      )
    );
  }

  // Emit TEXT_MESSAGE_END
  controller.enqueue(
    encoder.encode(
      formatSSE({
        type: EventType.TEXT_MESSAGE_END,
        messageId,
        timestamp: new Date().toISOString(),
      })
    )
  );
}

function getSimulatedResponse(message: string): string {
  const messageLower = message.toLowerCase();

  if (messageLower.includes("stack") || messageLower.includes("deploy")) {
    return `I can help you manage your infrastructure stacks. Here's what I can do:

- **Check stack status**: View health and metrics of deployed services
- **View logs**: Fetch container logs for debugging
- **Restart services**: Restart individual containers or entire stacks
- **Deploy updates**: Trigger deployments via Komodo

Which stack would you like to work with? You can see all available stacks in the Stacks page.`;
  }

  if (messageLower.includes("search") || messageLower.includes("find")) {
    return `I can search across multiple data sources:

- **Code search (Códeolas)**: Semantic search through your codebase
- **Document search (Paperless)**: Find documents by content
- **Bookmark search (Linkwarden)**: Search your saved bookmarks
- **Artwork search (Aleyum)**: Find similar images using CLIP

What would you like to search for?`;
  }

  if (messageLower.includes("extract") || messageLower.includes("scrape")) {
    return `I can extract content from web pages using multiple backends:

- **Crawl4AI**: Fast bulk extraction with LLM-powered cleaning
- **Stagehand**: Precision selector-based interactions
- **Skyvern**: Vision-based semantic navigation

Just provide a URL and tell me what information you need!`;
  }

  return `I'm the Aleyum Portal agent. I can help you with:

- **Infrastructure**: Manage stacks, view logs, restart services
- **Search**: Find code, documents, bookmarks, and artwork
- **Data flows**: Monitor Dagster pipelines and jobs
- **Web extraction**: Scrape and extract content from websites
- **MCP Tools**: Execute tools from the catalog

What would you like to do?`;
}
