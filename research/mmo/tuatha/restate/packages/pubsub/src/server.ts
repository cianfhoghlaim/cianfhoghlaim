// -------------------------------------------------------------------------------------
// Server State
// -------------------------------------------------------------------------------------

import { serve } from "@hono/node-server";
import { createNodeWebSocket } from "@hono/node-ws";
import { Hono } from "hono";
import { Pubsub } from "./pubsub.js";
import { HOST, PORT } from "./common.js";
import type { StreamUIMessages } from "@coding-agent-monorepo/types";

export const pubsub = new Pubsub();

// -------------------------------------------------------------------------------------
// Hono application
// -------------------------------------------------------------------------------------

const app = new Hono()
  .notFound((c) => c.text("Not Found", 404))
  .onError((error, c) => {
    console.warn(error);
    if (typeof error === "object") {
      return c.json(error, 500);
    } else {
      return c.text("Error processing " + c.req.url, 500);
    }
  });

const { upgradeWebSocket, injectWebSocket } = createNodeWebSocket({ app });

app
  .get(
    "/ws/subscribe/:topic",
    upgradeWebSocket!((c) => {
      const topic = c.req.param("topic");
      return {
        onOpen: (_, ws) => {
          pubsub.subscribe(topic, (message) => {
            ws.send(JSON.stringify(message, null, 2));
          });
        },
        onClose: () => {
          console.log("Client disconnected");
        },
        onError: (err) => {
          console.error("WebSocket error", err);
        },
      };
    })
  )
  .get(
    "/ws/publish/:topic",
    upgradeWebSocket!((c) => {
      const topic = c.req.param("topic");
      return {
        onOpen: (_, ws) => {},
        onMessage: async (message, ws) => {
          let uiMessage;
          if (typeof message.data === "string") {
            uiMessage = JSON.parse(message.data) as StreamUIMessages;
          } else if (message.data instanceof Blob) {
            const txt = await message.data.text();
            uiMessage = JSON.parse(txt) as StreamUIMessages;
          } else {
            throw new Error("Unsupported message type");
          }
          pubsub.publish(topic, uiMessage);
        },
        onClose: () => {
          console.log("Client disconnected");
        },
        onError: (err) => {
          console.error("WebSocket error", err);
        },
      };
    })
  );

const server = serve({ ...app, port: PORT }, (info) => {
  console.log(`Server running at http://${HOST}:${info.port}`);
});

injectWebSocket(server);

process.on("SIGINT", async () => {
  console.log("Shutting down...");
  process.exit(0);
});
