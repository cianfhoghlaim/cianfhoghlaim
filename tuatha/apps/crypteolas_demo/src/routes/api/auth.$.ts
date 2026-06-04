/**
 * Better Auth API Route Handler
 *
 * Handles all /api/auth/* requests including:
 * - /api/auth/siwe/nonce - Generate nonce for SIWE
 * - /api/auth/siwe/verify - Verify SIWE signature
 * - /api/auth/session - Get current session
 * - /api/auth/sign-out - Sign out
 */

import { createAPIFileRoute } from "@tanstack/start/api";
import { auth } from "../../lib/auth/server";

export const Route = createAPIFileRoute("/api/auth/$")({
  GET: async ({ request }) => {
    return auth.handler(request);
  },
  POST: async ({ request }) => {
    return auth.handler(request);
  },
});
