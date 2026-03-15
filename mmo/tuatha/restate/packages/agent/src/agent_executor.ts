import * as restate from "@restatedev/restate-sdk"
import { TerminalError } from "@restatedev/restate-sdk";
import { serde } from "@restatedev/restate-sdk-zod"
import { z } from "zod";
import { type Agent } from "./agent.js";
import {
  AgentTask,
  type StepInput,
  StepResult,
} from '@coding-agent-monorepo/types';
import { preparePlan, agentLoop } from "./plan.js";
import { sandbox } from "./sandbox.js";
import { rethrowIfNotTerminal } from "./utils.js";

/**
 * The agent_executor service runs the workflow for a given task
 */
export const agentExecutor = restate.service({
  name: "agent_executor",
  handlers: {
    runTask: restate.createServiceHandler(
      {
        input: serde.zod(AgentTask),
        output: serde.zod(z.void()),
      },
      async (restate: restate.Context, task) => {
        // grab the request's abort signal.
        const abortSignal = restate.request().attemptCompletedSignal;

        // this is our task ID, so we can let the agent know who sent the request
        const taskId = restate.request().id;

        // can we get a handle to the agent, so that we can send updates to it
        const agent = restate.objectSendClient<Agent>(
          { name: "agent" },
          task.agentId
        );

        // here is the place where we can setup various resources
        // like:
        // - an S3 bucket and presigned URLs for storing files,
        // - a database,
        // - a pubsub topic,
        // - a sandboxed environment.
        // - a browser session.
        //
        // we can make sure that they are cleaned up after the task is done.
        // we can compute stable names that will persist across retries.
        // and ephemeral names like a staging area.

        const resourcesToClean = [];

        try {
          // First, let's create a plan of how to approach the task.
          // We will use the LLM to generate a plan based on the task description.
          // We store the plan durably in the Restate journal,
          // because we will acquire resources for each step, and we want to make sure that
          // we can clean them up if the task fails or is canceled.

          const plan = await restate.run(
            "compute a plan",
            () => preparePlan({ task, abortSignal, topic: taskId }),
            { maxRetryAttempts: 3, initialRetryInterval: { seconds: 2 } }
          );

          // notify the agent that we have a plan

          agent.addUpdate({
            taskId,
            entries: [
              {
                role: "agent",
                message: `Will perform the following steps: ${plan.map((step) => step.title).join(", ")}`,
              },
            ],
          });
          

          // In this example, we will use a sandbox environment but you can imagine others.

          const sandboxClient = restate.objectClient(sandbox, task.agentId);
          const { sandboxId } = await sandboxClient.acquire();

          // This is a cleanup saga, we will release all these resources later.
          resourcesToClean.push(() => sandboxClient.release());

          const stepResults: string[] = [];
          
          for (const step of plan) {
            // notify the agent that we are executing the step
            agent.addUpdate({
              taskId,
              entries: [
                {
                  role: "agent",
                  message: `Executing step "${step.title}"`,
                },
              ],
            });

            // Add here any additional stateful resource, like a provisioned db, a browser session, etc.
            const stepInput = {
              taskId,
              stepId: step.id,
              task,
              step,
              sandboxId,
              topic: taskId, // <-- topic for step messages
              s3prefix: `s3://conversation-store-${restate.rand.uuidv4()}`,
              tempDirectory: `task-${taskId}-step-${step.id}`,
              planetScaleUrl: `https://db.example.com/task-${taskId}/step-${step.id}`,
              stepResults, // <-- pass previous step results to the next step
            } satisfies StepInput;

            // the actual step execution (as an agent loop)
            // this could be inline here as `stepPromise = loopAgent(restate, stepInput)`
            // but move it to a separate handler, partially for demo purposes (to show how
            // nested handlers are also automatically cancelled when parent is cancelled),
            // but also because it can be a useful pattern to reduce the retry scope on error (a new
            // handler starts a new journal, think like a sub-workflow)

            const stepResult = await restate
              .serviceClient(agentExecutor)
              .executePlanStep(stepInput);

            // optionally add `.orTimeout({ minutes: 5 });`

            // wait for this step to complete
            // If our parent Agent requests a cancellation, the line below will throw a TerminalError
            stepResults.push(stepResult);
            agent.addUpdate({
              taskId,
              entries: [
              {
                role: "agent",
                message: `Step "${step.title}" completed successfully.\n\nResult: ${stepResult}`,
              },
              ],
            });
            // move on to the next step!
          }

          // notify the agent that the task is done
          resourcesToClean.forEach((fn) => fn());
          agent.taskComplete({ taskId, message: "finished" });

        } catch (error) {
          // non terminal errors are rethrown, so that we don't clean up resources
          // because they lead to retries
          rethrowIfNotTerminal(error);

          const failure = error as TerminalError;
            agent.taskComplete({
              taskId,
              message: `I encountered an error while executing the task and had to stop. Error details: ${failure.message}.`,
            });
          resourcesToClean.forEach((fn) => fn());
          throw failure;
        }
      }
    ),

    /**
     * Executes a single step of the plan, here as a separate service
     * handler, to get its own local journal and retry scope
     */
    executePlanStep: restate.createServiceHandler(
      { ingressPrivate: true },
      async (
        restate: restate.Context,
        stepInput: StepInput
      ): Promise<StepResult> => {
        return agentLoop(restate, stepInput);
      }
    ),
  },
  options: {
    journalRetention: { days: 1 },
    idempotencyRetention: { days: 1 },
    inactivityTimeout: { minutes: 15 }, // inactivity (nor producing restate actions) after which Restate triggers suspension
    abortTimeout: { minutes: 30 }, // inactivity after which invocation is disconnected and retried (from journal)
    ingressPrivate: true, // this cannot be triggered externally via http, only from agent
  },
});

export type AgentExecutor = typeof agentExecutor;



