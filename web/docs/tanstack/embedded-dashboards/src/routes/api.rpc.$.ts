import { RPCHandler } from "@orpc/server/fetch";
import { createAPIFileRoute } from "@tanstack/react-start/api";
import { router } from "@/orpc/router";

const handler = new RPCHandler(router);

async function handle({ request }: { request: Request }) {
  const { response } = await handler.handle(request, {
    prefix: "/api/rpc",
    context: {},
  });

  return response ?? new Response("Not Found", { status: 404 });
}

export const APIRoute = createAPIFileRoute("/api/rpc/$")({
  GET: handle,
  POST: handle,
  PUT: handle,
  PATCH: handle,
  DELETE: handle,
});
