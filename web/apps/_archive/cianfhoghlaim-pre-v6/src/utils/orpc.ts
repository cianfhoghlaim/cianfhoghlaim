import { createORPCClient } from "@orpc/client";
import { RPCLink } from "@orpc/client/fetch";

const link = new RPCLink({
  url: "/rpc",
  headers: () => ({ "Content-Type": "application/json" }),
});

// The oRPC type-safe client generated from the AppRouter type.
// Type parameter uses `any` to avoid strict NestedClient constraints
// that differ between oRPC v1.12 and v1.14. The runtime `.call()` works.
export const client = createORPCClient<any>(link) as {
  health: { call: (input: Record<string, unknown>) => Promise<{ status: string }> };
  lakehouse: {
    health: { call: (input: Record<string, unknown>) => Promise<{ status: string }> };
    query: {
      call: (input: { sql: string; limit?: number }) => Promise<Record<string, unknown>[]>;
    };
    listBuckets: {
      call: (input: Record<string, unknown>) => Promise<{ buckets: string[] }>;
    };
  };
  exams: {
    list: {
      call: (input: {
        subject: string;
        year: number;
        level?: string;
        materialType?: string;
      }) => Promise<Record<string, unknown>[]>;
    };
    summary: {
      call: (input: { subject: string }) => Promise<{
        subject: string;
        rubric: string;
        recentYears: Array<{ year: number; schemes: number }>;
      }>;
    };
  };
  motherduck: {
    embedSession: {
      call: (input: { username: string; sessionHint?: string }) => Promise<{
        session: string;
      }>;
    };
  };
  me: { call: (input: Record<string, unknown>) => Promise<{ user: Record<string, unknown> | null }> };
};
