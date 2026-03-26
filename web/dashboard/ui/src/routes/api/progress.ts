import { createAPIFileRoute } from "@tanstack/start/api";

/**
 * Progress SSE endpoint.
 *
 * Streams real-time progress updates from Redis pub/sub.
 */

const REDIS_URL = process.env.REDIS_URL || "redis://localhost:6379";
const PROGRESS_CHANNEL = "dagster:progress:all";

export const ServerRoute = createAPIFileRoute("/api/progress")({
  GET: async ({ request }) => {
    const encoder = new TextEncoder();

    // Create SSE stream
    const stream = new ReadableStream({
      async start(controller) {
        // Send connection message
        controller.enqueue(
          encoder.encode(`data: ${JSON.stringify({ type: "connected" })}\n\n`)
        );

        // Try to connect to Redis for real progress updates
        try {
          // Dynamic import for Redis (server-side only)
          const { createClient } = await import("redis");

          const redis = createClient({ url: REDIS_URL });
          await redis.connect();

          // Subscribe to progress channel
          const subscriber = redis.duplicate();
          await subscriber.connect();

          await subscriber.subscribe(PROGRESS_CHANNEL, (message) => {
            try {
              controller.enqueue(encoder.encode(`data: ${message}\n\n`));
            } catch {
              // Controller closed, unsubscribe
              subscriber.unsubscribe(PROGRESS_CHANNEL);
            }
          });

          // Clean up on close
          request.signal.addEventListener("abort", async () => {
            await subscriber.unsubscribe(PROGRESS_CHANNEL);
            await subscriber.disconnect();
            await redis.disconnect();
            controller.close();
          });
        } catch (error) {
          console.warn("Redis not available, using mock progress:", error);

          // Fallback: Send mock progress for demo purposes
          let mockCurrent = 0;
          const mockTotal = 100;

          const mockInterval = setInterval(() => {
            if (mockCurrent >= mockTotal) {
              controller.enqueue(
                encoder.encode(
                  `data: ${JSON.stringify({
                    asset: "demo",
                    partition: null,
                    stage: "completed",
                    current: mockTotal,
                    total: mockTotal,
                    message: "Demo complete",
                    pct: 100,
                    timestamp: new Date().toISOString(),
                  })}\n\n`
                )
              );
              clearInterval(mockInterval);
              return;
            }

            mockCurrent += 5;
            controller.enqueue(
              encoder.encode(
                `data: ${JSON.stringify({
                  asset: "demo",
                  partition: null,
                  stage: "processing",
                  current: mockCurrent,
                  total: mockTotal,
                  message: `Processing ${mockCurrent}/${mockTotal}`,
                  pct: (mockCurrent / mockTotal) * 100,
                  timestamp: new Date().toISOString(),
                })}\n\n`
              )
            );
          }, 1000);

          request.signal.addEventListener("abort", () => {
            clearInterval(mockInterval);
            controller.close();
          });
        }

        // Keep-alive ping
        const pingInterval = setInterval(() => {
          try {
            controller.enqueue(
              encoder.encode(`data: ${JSON.stringify({ type: "ping" })}\n\n`)
            );
          } catch {
            clearInterval(pingInterval);
          }
        }, 30000);

        request.signal.addEventListener("abort", () => {
          clearInterval(pingInterval);
        });
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
});
