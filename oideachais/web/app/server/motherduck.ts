/**
 * MotherDuck server functions.
 *
 * `getEmbedSession` mints a short-lived read-scaling session for a Dive embed
 * via the MotherDuck REST API. The session is opaque to the client; the
 * frontend only uses it in the iframe `src` URL.
 *
 * Auth pattern follows the motherduck-rest-api skill:
 *  - Bearer token in `MOTHERDUCK_ADMIN_TOKEN` (server-only).
 *  - Service-account username is the public identifier (not a secret).
 *  - Response includes a one-time `session` string; do not log it.
 */

import { createServerFn } from "@tanstack/react-start";
import { z } from "zod";

const MD_API = "https://api.motherduck.com";

async function mdFetch<T>(path: string, init: RequestInit = {}): Promise<T> {
  const token = process.env.MOTHERDUCK_ADMIN_TOKEN;
  if (!token) {
    throw new Error(
      "MOTHERDUCK_ADMIN_TOKEN not configured. Add it to the Infisical " +
        "`dev-baile/motherduck/admin_token` path and re-run `bun run secrets:init`.",
    );
  }
  const response = await fetch(`${MD_API}${path}`, {
    ...init,
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
      ...(init.headers ?? {}),
    },
    cache: "no-store",
  });
  if (!response.ok) {
    const body = await response.text();
    throw new Error(`MotherDuck API ${response.status}: ${body}`);
  }
  return (await response.json()) as T;
}

const embedSessionSchema = z.object({
  username: z
    .string()
    .min(3)
    .max(255)
    .default("oideachais_service_user"),
  sessionHint: z.string().optional(),
});

export const getEmbedSession = createServerFn({ method: "POST" })
  .inputValidator(embedSessionSchema)
  .handler(async ({ data }: { data: z.infer<typeof embedSessionSchema> }) => {
    const diveId = process.env.MOTHERDUCK_DIVE_ID;
    if (!diveId) {
      throw new Error("MOTHERDUCK_DIVE_ID not configured");
    }
    const body: Record<string, string> = { username: data.username };
    if (data.sessionHint) body.session_hint = data.sessionHint;
    const res = await mdFetch<{ session: string }>(
      `/v1/dives/${diveId}/embed-session`,
      { method: "POST", body: JSON.stringify(body) },
    );
    return res;
  });
