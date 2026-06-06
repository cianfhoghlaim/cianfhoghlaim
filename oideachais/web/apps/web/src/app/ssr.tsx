// app/ssr.tsx — TanStack Start server-side renderer
//
// Server entry: render the React tree on the server and stream it to the
// browser. The Hono apps/api (port 8787) handles /rpc, /api/auth, and
// /api/copilotkit for actual data; the SSR pass just hydrates.
import { createStartHandler } from "@tanstack/react-start/server";
import { getRouter } from "./router";

export default createStartHandler({
  getRouter,
});
