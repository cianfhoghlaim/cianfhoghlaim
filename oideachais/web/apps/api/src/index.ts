import "dotenv/config";
import { Hono } from "hono";
import { cors } from "hono/cors";
import { logger } from "hono/logger";
import { OpenAPIHandler } from "@orpc/openapi/fetch";
import { RPCHandler } from "@orpc/server/fetch";
import { onError } from "@orpc/server";
import { appRouter } from "@oideachais/api/routers";
import { createContext } from "@oideachais/api/context";
import { auth } from "@oideachais/auth";
import { serve } from "@hono/node-server";

const app = new Hono();

app.use(logger());
app.use("/*", cors({
  origin: process.env.CORS_ORIGIN || "http://localhost:3001",
  allowMethods: ["GET", "POST", "OPTIONS"],
  allowHeaders: ["Content-Type", "Authorization"],
  credentials: true,
}));

// Better Auth handler
app.on(["POST", "GET"], "/api/auth/*", (c) => auth.handler(c.req.raw));

// oRPC RPC handler
const rpcHandler = new RPCHandler(appRouter, {
  interceptors: [onError((error) => console.error("[rpc]", error))],
});

app.use("/rpc/*", async (c, next) => {
  const ctx = await createContext({ context: c });
  const result = await rpcHandler.handle(c.req.raw, {
    prefix: "/rpc",
    context: ctx,
  });
  if (result.matched) {
    return c.newResponse(result.response.body, result.response);
  }
  await next();
});

// oRPC OpenAPI handler (Swagger at /api-reference)
const openapiHandler = new OpenAPIHandler(appRouter, {
  interceptors: [onError((error) => console.error("[openapi]", error))],
});

app.use("/api-reference/*", async (c, next) => {
  const result = await openapiHandler.handle(c.req.raw, {
    prefix: "/api-reference",
    context: { session: null },
  });
  if (result.matched) {
    return c.newResponse(result.response.body, result.response);
  }
  await next();
});

// Health
app.get("/", (c) => c.text("OK"));

const port = Number(process.env.PORT) || 8787;
console.log(`oRPC+Hono API server listening on http://localhost:${port}`);
console.log(`  RPC: http://localhost:${port}/rpc`);
console.log(`  API docs: http://localhost:${port}/api-reference`);

serve({ fetch: app.fetch, port });
