import { z } from "zod";
import { publicProcedure, o } from "../index";
import { runDuckLakeQuery } from "../queries";

export const lakehouseRouter = o.router({
  health: publicProcedure.handler(() => ({ status: "ok" })),

  query: publicProcedure
    .input(
      z.object({
        sql: z.string().min(1).max(10_000),
        limit: z.number().int().default(200),
      }),
    )
    .handler(async ({ input }) => runDuckLakeQuery(input.sql, input.limit)),

  listBuckets: publicProcedure.handler(async () => {
    const endpoint = process.env.AWS_ENDPOINT_URL ?? "http://localhost:3900";
    try {
      const res = await fetch(`${endpoint}/`);
      const body = await res.text();
      const names: string[] = [];
      for (const m of body.matchAll(/<Name>([^<]+)<\/Name>/g)) {
        names.push(m[1]);
      }
      return { buckets: names };
    } catch {
      return { buckets: [] };
    }
  }),
});
