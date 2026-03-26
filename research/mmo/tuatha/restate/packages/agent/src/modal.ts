import { ExecResult, WriteFileResult } from "@coding-agent-monorepo/types";
import {
  InvocationId,
  object,
  ObjectContext,
  rpc,
  TerminalError,
} from "@restatedev/restate-sdk";
import { AlreadyExistsError, App, Image, NotFoundError, Sandbox } from "modal";

export type State =
  | {
      type: "unknown";
    }
  | {
      type: "created";
      name: string;
      restartTask: InvocationId;
    };

export type ModalContext = ObjectContext<{ state: State }>;

// Helper functions

const getState = async (ctx: ModalContext) =>
  (await ctx.get("state")) ?? { type: "unknown" };

const setState = (ctx: ModalContext, state: State) => ctx.set("state", state);

const runStep = async <T>(
  ctx: ModalContext,
  stepName: string,
  fn: () => Promise<T>
): Promise<T> => {
  return await ctx.run(stepName, fn, {
    maxRetryAttempts: 5,
    initialRetryInterval: { seconds: 10 },
  });
};

// Constants
const APP_NAME = "agent47";
const SANDBOX_TIMEOUT_MS = 1000 * 60 * 60; // 1 hour
const SANDBOX_RESTART_INTERVAL_MS = 1000 * 60 * 55; // 55 minutes

// Modal Virtual Object

export const modal = object({
  name: "modal",
  handlers: {
    /**
     * Create a new modal sandbox.
     * @param ctx The restate context.
     * @returns A promise that resolves when the sandbox is created.
     */
    create: async (ctx: ModalContext): Promise<void> => {
      const state = await getState(ctx);

      switch (state.type) {
        // create the sandbox at the first time.
        // how exciting!
        case "unknown": {
          const name = `snd_${ctx.rand.uuidv4()}`;

          await runStep(ctx, `create ${name}`, () => createModalSandbox(name, SANDBOX_TIMEOUT_MS));

          const restartTask = ctx
            .objectSendClient(modal, ctx.key)
            .restart(
              rpc.sendOpts({
                delay: { milliseconds: SANDBOX_RESTART_INTERVAL_MS },
              })
            );

          setState(ctx, {
            type: "created",
            name,
            restartTask: await restartTask.invocationId,
          });

          return;
        }
        case "created": {
          throw new TerminalError("Sandbox already provisioned");
        }
      }
    },

    /**
     * Restart the modal sandbox to extend its lifetime. Use a snapshot to preserve state.
     *
     * @param ctx The restate context.
     * @returns A promise that resolves when the sandbox is restarted.
     */
    restart: async (ctx: ModalContext): Promise<void> => {
      const state = await getState(ctx);
      if (state.type !== "created") {
        throw new TerminalError("unexpected state");
      }

      const { name } = state;

      const snapshotId = await ctx.run("take snapshot", () =>
        snapshotModalSandbox(name)
      );

      await runStep(ctx, "terminate sandbox", () =>
        terminateModalSandbox(name)
      );

      await runStep(ctx, "restart from snapshot", () =>
        startModalSandbox(name, snapshotId, SANDBOX_TIMEOUT_MS)
      );

      const restartTask = ctx
        .objectSendClient(modal, ctx.key)
        .restart(
          rpc.sendOpts({ delay: { milliseconds: SANDBOX_RESTART_INTERVAL_MS } })
        );

      setState(ctx, {
        type: "created",
        name,
        restartTask: await restartTask.invocationId,
      });
    },

    /**
     * Release the modal sandbox
     * @param ctx The restate context.
     */
    release: async (ctx: ModalContext): Promise<void> => {
      const state = await getState(ctx);
      if (state.type !== "created") {
        throw new TerminalError("Already released");
      }

      const { name, restartTask } = state;
      ctx.cancel(restartTask);

      await runStep(ctx, "release sandbox", async () => {
        try {
          const sb = await Sandbox.fromName(APP_NAME, name);
          await sb.terminate();
        } catch (e) {
          if (!(e instanceof NotFoundError)) {
            throw e;
          }
        }
      });

      ctx.clearAll();
    },

    /**
     * Execute a command in the modal sandbox.
     *  
     * @param ctx The restate context.
     * @param command a shell command to execute in the sandbox.
     * @returns A promise that resolves with the result of the command execution.
     */
    execute: async (
      ctx: ModalContext,
      command: string
    ): Promise<ExecResult> => {
      const state = await getState(ctx);
      if (state.type !== "created") {
        throw new TerminalError("Sandbox not created");
      }

      const { name } = state;

      return await runStep(ctx, command, async () => {
        const sb = await Sandbox.fromName(APP_NAME, name);
        const args = ["sh", "-c", command];
        const res = await sb.exec(args);
        const statusCode = await res.wait();
        const [output, error] = await Promise.all([
          res.stdout.readText(),
          res.stderr.readText(),
        ]);

        return {
          type: "result",
          result: {
            statusCode,
            output,
            error,
          },
        };
      });
    },

    /**
     * Write a file in the modal sandbox.
     * @param ctx The restate context.
     * @param arg The file write arguments.
     * @returns A promise that resolves with the result of the file write operation.
     */
    writeFile: async (
      ctx: ModalContext,
      arg: { filePath: string; content: string }
    ): Promise<WriteFileResult> => {
      const state = await getState(ctx);
      if (state.type !== "created") {
        throw new TerminalError("Sandbox not created");
      }

      const { name } = state;

      return await runStep(ctx, "write file", async () => {
        const sb = await Sandbox.fromName(APP_NAME, name);
        const res = await sb.open(arg.filePath, "w+");
        await res.write(new TextEncoder().encode(arg.content));
        await res.flush();
        await res.close();
        return { type: "ok" };
      });
    },
  } ,
  options: {
    journalRetention: { hours: 1 },
    idempotencyRetention: { hours: 1 },
    inactivityTimeout: { minutes: 10 },
    abortTimeout: { minutes: 10 },
  },
});

export type Modal = typeof modal;

// Modal Sandbox Management

const createModalSandbox = async (name: string, timeout: number) => {
  const image = Image.fromRegistry("debian:latest");
  const app = await App.lookup(APP_NAME, { createIfMissing: true });
  try {
    const sb = await app.createSandbox(image, {
      name,
      workdir: "/project",
      command: ["cat"],
      timeout,
    });
    const res = await sb.exec(["apt-get", "update"]);
    const code = await res.wait();
    if (code !== 0) {
      throw new TerminalError("Failed to provision sandbox");
    }
  } catch (e) {
    if (e instanceof AlreadyExistsError) {
      return;
    }
    throw e;
  }
};

const snapshotModalSandbox = async (name: string) => {
  try {
    const sb = await Sandbox.fromName(APP_NAME, name);
    const snapshot = await sb.snapshotFilesystem();
    return snapshot.imageId;
  } catch (e) {
    if (e instanceof NotFoundError) {
      throw new TerminalError("Sandbox not found, cannot snapshot");
    }
    throw e;
  }
};

const terminateModalSandbox = async (name: string) => {
  try {
    const sb = await Sandbox.fromName(APP_NAME, name);
    await sb.terminate();
    await sb.wait();
  } catch (e) {
    if (!(e instanceof NotFoundError)) {
      throw e;
    }
  }
};

const startModalSandbox = async (name: string, snapshotId: string, timeout: number) => {
  const app = await App.lookup(APP_NAME, { createIfMissing: true });
  const image = Image.fromId(snapshotId);
  try {
    await app.createSandbox(image, {
      name,
      workdir: "/project",
      command: ["cat"],
      timeout,
    });
  } catch (e) {
    if (e instanceof AlreadyExistsError) {
      // sometimes it takes a moment for the sandbox to terminate, so
      // the api might report it still exists.
      // No big deal, we will bubble up and restate will retry it,
      // The power of durable execution for the rescue!.
    }
    throw e;
  }
};
