import type { ActionCtx } from "../_generated/server";

export interface LoggedActionMeta {
  function: string;
  project: string;
}

export function loggedAction<Args, Returns>(
  fn: (ctx: ActionCtx, args: Args) => Promise<Returns>,
  meta: LoggedActionMeta,
): (ctx: ActionCtx, args: Args) => Promise<Returns> {
  return async (ctx, args) => {
    const t0 = Date.now();
    let ok = true;
    let error: string | undefined;
    try {
      return await fn(ctx, args);
    } catch (e) {
      ok = false;
      error = e instanceof Error ? e.message.slice(0, 1024) : String(e).slice(0, 1024);
      throw e;
    } finally {
      const durationMs = Date.now() - t0;
      try {
        await ctx.db.insert("convexFunctionCalls", {
          function: meta.function,
          kind: "action",
          project: meta.project,
          args: JSON.stringify(args).slice(0, 1024),
          durationMs,
          ok,
          error,
          calledAt: Date.now(),
        });
      } catch {
        // never let logging failure break the action
      }
    }
  };
}
