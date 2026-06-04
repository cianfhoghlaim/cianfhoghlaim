import { z } from "zod";
import { publicProcedure, protectedProcedure, o } from "../index";

const MD_API = "https://api.motherduck.com";

async function mdFetch<T>(path: string, init: RequestInit = {}): Promise<T> {
  const token = process.env.MOTHERDUCK_ADMIN_TOKEN;
  if (!token) {
    throw new Error("MOTHERDUCK_ADMIN_TOKEN not configured");
  }
  const res = await fetch(`${MD_API}${path}`, {
    ...init,
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
      ...(init.headers ?? {}),
    },
  });
  if (!res.ok) {
    throw new Error(`MotherDuck API ${res.status}`);
  }
  return (await res.json()) as T;
}

export const motherduckRouter = o.router({
  embedSession: protectedProcedure
    .input(
      z.object({
        username: z.string().default("oideachais_service_user"),
        sessionHint: z.string().optional(),
      }),
    )
    .handler(async ({ input }) => {
      const diveId = process.env.MOTHERDUCK_DIVE_ID;
      if (!diveId) throw new Error("MOTHERDUCK_DIVE_ID not configured");
      const body: Record<string, string> = { username: input.username };
      if (input.sessionHint) body.session_hint = input.sessionHint;
      return mdFetch<{ session: string }>(`/v1/dives/${diveId}/embed-session`, {
        method: "POST",
        body: JSON.stringify(body),
      });
    }),
});
