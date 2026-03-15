import * as restate from "@restatedev/restate-sdk"
import { serde } from "@restatedev/restate-sdk-zod"
import { z } from "zod";
import {
  Entry,
  type AgentTask,
  type ContextArtifact,
} from '@coding-agent-monorepo/types';
import { AgentExecutor } from "./agent_executor.js";
import { jsonPassThroughSerde } from "./utils.js";

// aliases / shortcuts
const binarySerDe = restate.serde.binary;
const opts = restate.rpc.sendOpts;

type Artifacts = {
    [key: `a_${string}`]: ContextArtifact;
};

type State = Artifacts & {
    messages: Entry[],
    currentTaskId: restate.InvocationId | null
};

/**
 * The agent object is the orchestrator that receives messages from the user,
 * tracks the state of the agent, and kicks off workflows.
 */
export const agent = restate.object({
  name: "agent",
  handlers: {
    /**
     * Handler for all messages (user prompts, GitHub webhooks)
     * Could also have specialized handlers for different types of input.
     */
    newMessage: restate.createObjectHandler(
      {
        journalRetention: { days: 1 },
        input: serde.zod(z.string()),
        output: serde.zod(z.object({ currentTaskId: z.string() })),
      },
      async (restate: restate.ObjectContext<State>, message) => {
        // get the current messages
        const messages = (await restate.get("messages")) ?? [];

        // abort ongoing task, if there is one
        const ongoingTask = await restate.get("currentTaskId");
        if (ongoingTask) {
          await cancelTask(restate, ongoingTask, { seconds: 30 });
          restate.clear("currentTaskId");
          messages.push({
            role: "agent",
            message: "The ongoing task was cancelled due to a new user message",
          });
        }

        messages.push({ role: "user", message });
        restate.set("messages", messages);

        const task: AgentTask = {
          agentId: restate.key,
          prompt: message,
          context: messages,
          maxIterations: 10,
        };

        // kick off the agent workflow for the prompt
        const handle = restate
          .serviceSendClient<AgentExecutor>({ name: "agent_executor" })
          .runTask(task, opts({ idempotencyKey: restate.rand.uuidv4() }));
        // note that the idempotency key is not actually needed for idempotency, but it is a
        // current limitation that re-attaching to handlers only works when an idempotency key is present

        const invocationId = await handle.invocationId;
        restate.set("currentTaskId", invocationId);

        return { currentTaskId: invocationId };
      }
    ),

    /**
     * Handler for when a task is complete, called by the agent_executor service.
     */
    taskComplete: restate.createObjectHandler(
      {
        // we don't define a schema here, to show you can also use just TS type
        // system, but then you don't get runtime type checking

        ingressPrivate: true, // not part of public API, only callable from other Restate services
      },
      async (
        restate: restate.ObjectContext<State>,
        req: { message: string; taskId: string }
      ) => {
        // we double check that this was not received after we sent a
        // cancellation and started a new new task
        const ongoingTask = await restate.get("currentTaskId");
        if (ongoingTask !== req.taskId) {
          return;
        }
        restate.clear("currentTaskId");

        const messages = (await restate.get("messages"))!;
        messages.push({ role: "agent", message: req.message });
        restate.set("messages", messages);

        await restate.run("notify task done", () => {
          // some API call, if necessary
          console.log("🥳🥳🥳 Task complete!");
        });
      }
    ),

    /**
     * This handler receives the intermediate results of an ongoing task
     */
    addUpdate: restate.createObjectHandler(
      {
        input: serde.zod(
          z.object({ taskId: z.string(), entries: z.array(Entry) })
        ),
        ingressPrivate: true, // not part of public API
      },
      async (restate: restate.ObjectContext<State>, { taskId, entries }) => {
        // we double check that this was not a message enqueued by a handler that
        // has since been cancelled
        const ongoingTask = await restate.get("currentTaskId");
        if (ongoingTask !== taskId) {
          return;
        }

        // store message
        const messages = (await restate.get("messages")) ?? [];
        messages.push(...entries);
        restate.set("messages", messages);
      }
    ),

    getMessages: restate.createObjectSharedHandler(
      {
        input: restate.serde.empty,
        output: jsonPassThroughSerde, // advanced patter: pass binary through, but declare as JSON
        journalRetention: { days: 0 }, // no need to keep a history of this handler
      },
      async (restate: restate.ObjectSharedContext) => {
        // we get the state as bytes and pass the bytes back
        // no need to parse and then re-encode JSON
        return await restate.get("messages", binarySerDe);
      }
    ),

    cancelTask: async (restate: restate.ObjectContext<State>) => {
      // abort ongoing task, if there is one
      const ongoingTask = await restate.get("currentTaskId");
      if (ongoingTask) {
        await cancelTask(restate, ongoingTask, { seconds: 30 });
        restate.clear("currentTaskId");

        const messages = (await restate.get("messages")) ?? [];
        messages.push({
          role: "agent",
          message: "The ongoing task was cancelled",
        });
        restate.set("messages", messages);
      }
    },
  },
  options: {
    // default retention, unless overridden at the handler level
    // most methods are simple and don't need to be retained for observability
    journalRetention: { days: 0 },
    idempotencyRetention: { days: 1 },
  },
});

export type Agent = typeof agent;

// ----------------------------
// Helper functions
// ----------------------------

async function cancelTask(
        ctx: restate.Context,
        invocationId: restate.InvocationId,
        timeout: restate.Duration) {

    // cancel ongoing invocation
    ctx.cancel(invocationId);

    // wait for it to gracefully complete for a bit
    const donePromise = ctx.attach(invocationId);
    try {
        await donePromise.orTimeout(timeout);
    } catch (e) {
        if (e instanceof restate.TerminalError && e.code === 409) {
            // cancelled
            return
        }
        if (e instanceof restate.TimeoutError) {
            // did not complete in time, we keep it running, it will still do its cleanup
            ctx.console.warn(`Cancelled agent task taking longer to complete than ${JSON.stringify(timeout)}`)
            return;
        }
        // otherwise, re-throw the error
        throw e;
    }
}