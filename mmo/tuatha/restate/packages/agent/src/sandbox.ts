import {
  Duration,
  InvocationId,
  object,
  ObjectContext,
  rpc,
  TerminalError,
} from "@restatedev/restate-sdk";

import { modal } from "./modal.js";

export type AcquireSandboxResponse = {
  sandboxId: string;
};

type State = {
  sandboxId: string;
  releaseTask?: InvocationId;
};

const SANDBOX_INACTIVITY_TIMEOUT: Duration = { minutes: 15 };

/**
 * This is a virtual object that manages the provisioning and releasing of code sandboxes.
 * It allows acquiring a sandbox, releasing it, and reusing an existing sandbox if available.
 * The object also handles the release of the sandbox after a period of inactivity.
 */
export const sandbox = object({
  name: "sandbox",
  description:
    "Service to manage the provisioning and releasing of code sandboxes.",
  handlers: {
    /**
     * Acquire a sandbox.
     *
     * @param ctx - the context of the invocation
     * @returns the ID of the acquired sandbox
     */
    acquire: async (
      ctx: ObjectContext<State>
    ): Promise<AcquireSandboxResponse> => {
      const existingSandboxId = await ctx.get("sandboxId");

      if (existingSandboxId) {
        // an existing sandbox is available, we can reuse it.
        // and we should cancel the release task if it exists.
        const releaseTask = await ctx.get("releaseTask");
        cancelTheReleaseTask(releaseTask, ctx);
        return { sandboxId: existingSandboxId };
      }

      // if we don't have a sandbox, we need to provision one.
      const sandboxId = ctx.rand.uuidv4();

      await ctx.objectClient(modal, sandboxId).create();

      ctx.set("sandboxId", sandboxId);

      return {
        sandboxId,
      };
    },
   
    /**
     * Schedule the release of the sandbox.
     *
     * @param ctx - the context of the invocation
     * @returns void
     */
    release: async (ctx: ObjectContext<State>): Promise<void> => {
      const releaseTask = await ctx.get("releaseTask");
      if (releaseTask) {
        cancelTheReleaseTask(releaseTask, ctx);
      }

      // Release the sandbox after some period of inactivity.
      // In reality, you would probably snapshot it so that you can restore it later.
      // We do this by calling a handler with a delay.

      const handle = ctx
        .objectSendClient(sandbox, ctx.key)
        .releaseNow(rpc.sendOpts({ delay: SANDBOX_INACTIVITY_TIMEOUT }));

      const invocationId = await handle.invocationId;
      ctx.set("releaseTask", invocationId);
    },

    releaseNow: async (ctx: ObjectContext<State>): Promise<void> => {
      const sandboxId = await ctx.get("sandboxId");
      if (!sandboxId) {
        return;
      }
      const releaseTask = await ctx.get("releaseTask");
      if (releaseTask === undefined || releaseTask === null) {
        // meanwhile someone else has acquired the sandbox.
        return;
      }
      ctx.clear("sandboxId");
      ctx.clear("releaseTask");
      await ctx.objectClient(modal, sandboxId).release();
    },
  },
  options: {
    journalRetention: { hours: 1 },
    idempotencyRetention: { hours: 1 },
  },
});

function cancelTheReleaseTask(
  releaseTask: InvocationId | undefined | null,
  ctx: ObjectContext<State>
) {
  if (releaseTask === undefined || releaseTask === null) {
    // trying to acquire without a release....
    // someone forgot a little try-catchy release-y?
    // this should not happen and this is a demo bug.
    throw new TerminalError(
      "Cannot acquire a sandbox that is already acquired without releasing it first."
    );
  }
  ctx.cancel(releaseTask);
  ctx.clear("releaseTask");
}