import { TerminalError, type Context } from '@restatedev/restate-sdk';

import { ModelMessage, streamText, generateObject, tool } from 'ai';
import {
  AgentTask,
  PlanStep,
  StepInput,
  StepResult,
  StreamUIMessages,
} from '@coding-agent-monorepo/types';
import { publisherClient } from '@coding-agent-monorepo/pubsub';
import { openai } from '@ai-sdk/openai';
import { z } from 'zod';

import { modal } from './modal.js';

// --------------------------------------------------------
//  The actual agentic planning and plan step execution
// --------------------------------------------------------

// A set of tools that the LLM can use to execute the steps
const TOOLS = {
  executeCommand: tool({
    inputSchema: z.object({
      command: z.string().describe('The shell command to execute.'),
    }),
    description: `Executes a non-interactive shell command in an Ubuntu Linux environment. 
This tool is designed for performing file system operations, managing dependencies, and running processes.

# Usage Guidelines:
- Use for commands like 'ls -R', 'mkdir -p my-dir', 'npm install', 'cat file.txt'.
- Commands must not require user input or interactive prompts.
- Each command is executed in a stateless, sessionless environment. Ensure the entire operation is encapsulated in a single command string (e.g., 'cd dist && cat app.js').
- Use this tool for tasks such as:
  - Checking versions (e.g., 'node -v').
  - Creating directories or files.
  - Installing dependencies (e.g., 'npm install').
  - Running scripts or inspecting file contents.
- You run as a superuser, so you can perform any operation that requires elevated privileges.
- Do not use 'sudo' in commands, as it is not necessary.

# Expected Output:
- Status Code: The exit code of the command (0 for success, non-zero for failure).
- Output: The standard output of the command.
- Error: Any error message produced by the command.

# Best Practices:
- Always validate the output and handle errors appropriately.
- Be explicit about paths and avoid relying on implicit state (e.g., current working directory).`,
  }),
  createFile: tool({
    inputSchema: z.object({
      filePath: z
        .string()
        .describe(
          "The full path where the file should be created, e.g., 'src/index.js'."
        ),
      content: z.string().describe('The content to write into the file.'),
    }),
    description: `A high-level tool to create a new file with specified content. 
This is often more reliable for writing multi-line code than using 'echo' with 'executeCommand'.
- If the file already exists, it will be completely overwritten.
- Use this for writing source code, configuration files, or documentation.`,
  }),
};

/**
 * Deconstructs a task into a plan of steps.
 * This function prepares a plan for executing a coding task by breaking it down into manageable steps.
 * Each step includes a description, a prompt for the LLM, and a status indicating its
 *
 * @param params - The parameters for preparing a plan.
 * @param params.task - The task for which to prepare the plan.
 * @param params.abortSignal - The signal to abort the operation if needed.
 * @returns A promise that resolves to an array of PlanStep objects representing the plan for the task.
 */
export async function preparePlan(params: {
  topic: string;
  task: AgentTask;
  abortSignal: AbortSignal;
}): Promise<PlanStep[]> {
  const { task, abortSignal } = params;

  const system = `You are an expert coding task planner responsible for breaking down complex programming tasks into executable steps.
      
# You are given the entire context of the conversation so far, including what has been done already.
- The user has provided a task prompt and some context messages.
- You must NOT repeat steps that have already been completed, unless explicitly asked to do so by the user.
- Previous steps that have been attempted and completed are listed below, each completed step has a "Final Result" section with its outcome.

# TASK
${task.prompt}

# EXECUTION ENVIRONMENT
- Ubuntu Linux environment
- Git and npm pre-installed
- All commands must be non-interactive (no user input required)
- Example: Use 'echo "content" > file.txt' instead of 'nano file.txt'

# PLAN REQUIREMENTS
1. Generate logical steps to accomplish the task.
   - Each step should be atomic and focused on a single outcome.
   - Use the provided task prompt to guide the planning.
   - Use the conversation history to learn what has been done so far.
   - DO NOT repeat steps that have already been completed! unless you are explicitly asked to do so by the user.
2. Each step must include:
   - id: A unique identifier (e.g., "step1")
   - title: A concise title
   - description: Detailed explanation of what needs to be accomplished
   - prompt: Specific instructions for the AI to execute this step
   - status: Always set to "pending"

# STEP CATEGORIES TO CONSIDER
- Environment assessment (checking versions, file structure)
- Project setup (creating directories, initializing repos)
- Dependency management (installing packages)
- Code development (writing specific components)
- Testing and validation (verifying functionality)
- Documentation (adding comments, README files)

# BEST PRACTICES
- Make steps atomic and focused on one specific outcome
- Include error handling considerations
- Ensure logical progression between steps
- Be explicit about file paths and naming conventions
- Provide context in each step about its place in the overall task
- Always make sure to operate relative to the path /project

The AI will execute each step exactly as instructed, so be thorough and precise.
`;

  const messages: ModelMessage[] = [];
  messages.push({
    role: 'system',
    content: system,
  });
  for (const entry of task.context) {
    if (entry.role === 'user') {
      messages.push({
        role: 'user',
        content: entry.message,
      });
    } else {
      messages.push({
        role: 'assistant',
        content: entry.message,
      });
    }
  }

  // Call the LLM to generate a plan using streaming with structured output
  // This demonstrates how to use streaming while maintaining structured output with schema validation
  //
  const { publish } = await browserStream({ topic: params.topic });

  await publish({ type: 'planStart' });

  const { object: plan } = await generateObject({
    model: openai('gpt-5'),
    schema: z.object({
      steps: z.array(PlanStep),
    }),
    messages,
    abortSignal,
  });

  await publish({ type: 'plan', plan: plan.steps });

  return plan.steps;
}

/**
 * Executes a PlanStep.
 * This function executes a main coding loop, which involves calling the LLM to generate responses or tool calls.
 *
 * @param restate - The Restate context for service client interactions.
 * @param params - The parameters for executing the step.
 * @param params.taskId - The ID of the task being executed.
 * @param params.task - The task object containing details about the task.
 * @param params.step - The step to be executed.
 * @param params.topic - The topic for updates related to this step.
 * @returns A promise that resolves to a StepResult containing the step ID and messages generated during execution.
 */
export async function agentLoop(
  restate: Context,
  { taskId, task, step, topic, stepResults, sandboxId }: StepInput
): Promise<StepResult> {
  console.log(`
    Executing LLM step for: ${task.agentId} with the task ID: ${taskId}
        Step ID: ${step.id}
        Step Title: ${step.title}
        Step Description: ${step.description}
        Step Prompt: ${step.prompt}
    `);

  const abortSignal = restate.request().attemptCompletedSignal;

  // we always start with an empty history
  // and we will append messages to it as we go

  const history: ModelMessage[] = [
    {
      role: "system",
      content: `You are an expert AI coding assistant executing a specific step in a larger coding task. Your goal is to complete this step efficiently and accurately.

# EXECUTION ENVIRONMENT
- Ubuntu Linux
- You are the root user (no sudo needed)
- You have superuser privileges you can install packages and run commands.
- Commands must be non-interactive only
- Each command runs in a stateless environment

# OVERALL TASK CONTEXT
${task.prompt}

# CURRENT STEP TO EXECUTE
**Title:** ${step.title}
**Description:** ${step.description}
**Instructions:** ${step.prompt}

# PREVIOUS STEPS COMPLETED
${stepResults.length > 0 ? stepResults.map((res, idx) => `${idx + 1}. ${res}`).join("\n") : "None - this is the first step"}

# EXECUTION GUIDELINES
1. **Focus**: Complete ONLY the current step - do not attempt other steps
2. **Tools**: Use createFile for writing code/configs, executeCommand for shell operations
3. **Validation**: Always verify your work by checking outputs and handling errors
4. **Documentation**: Use markdown formatting and explain your reasoning
5. **Error Handling**: If commands fail, analyze errors and try alternative approaches
6. **File Paths**: Be explicit about paths and directory structure
7. **Working Directory**: Always operate relative to the /project directory

# SUCCESS CRITERIA
- The step's specific objective is completed
- All created files are valid and properly formatted
- Any commands execute successfully
- As a final message, provide a clear summary of the final result under a "Final Result" section.
- For the final result use the  '###' markdown header, separated by a new line. 
- use markdown.

Execute the step now, thinking through each action before taking it.`,
    },
  ];

  await restate.run('Notify step start', async () => {
    const { publish } = await browserStream({ topic });
    await publish({ type: 'stepStart', stepId: step.id });
  });

  for (let i = 0; i < 100; i++) {
    // -----------------------------------------------------
    // 1. Call the LLM to generate a response or tool calls
    // -----------------------------------------------------

    const { calls, messages, finished } = await restate.run(
      `execute ${step.title} iteration ${i + 1}`,
      () => streamModel(abortSignal, history, step.id, topic),
      { maxRetryAttempts: 3 }
    );

    history.push(...messages);

    if (finished === 'stop') {
      console.log('LLM finished generating response, exiting loop.');
      await restate.run('Notify step end', async () => {
        const { publish } = await browserStream({ topic });
        await publish({ type: 'stepEnd', stepId: step.id });
      });
      
      return extractFinalResult(messages);
    }
    

    // -----------------------------------------------------
    // 2. Process the actual tool calls
    // -----------------------------------------------------

    for (const call of calls) {
      if (call.toolName === 'createFile') {
        const { filePath, content } = call.input as { filePath: string; content: string };
        const result = await writeFileInSandbox(restate, sandboxId, { filePath, content });

        history.push({
          role: 'tool',
          content: [
            {
              type: 'tool-result',
              toolCallId: call.toolCallId,
              toolName: call.toolName,
              output: { type: 'text', value: result },
            },
          ],
        });
      }

      if (call.toolName === 'executeCommand') {
        const { command } = call.input as { command: string };
        const result = await runInSandbox(restate, sandboxId, command);
        history.push({
          role: 'tool',
          content: [
            {
              type: 'tool-result',
              toolCallId: call.toolCallId,
              toolName: call.toolName,
              output: { type: 'text', value: result },
            },
          ],
        });
      }
    }
  }

  return "<I failed to execute this step within the allowed number of iterations>";
}

async function writeFileInSandbox(
  ctx: Context,
  sandboxId: string,
  args: { filePath: string; content: string }
): Promise<string> {
  const res = await ctx.objectClient(modal, sandboxId).writeFile(args);
  switch (res.type) {
    case 'starting':
      throw new TerminalError('Sandbox is still starting, please retry later.');
    case 'failed':
      throw new TerminalError(`Failed to write file: ${res.error}`);
    case 'unknown':
      throw new TerminalError('Unknown error occurred while writing file.');
    case 'stopped':
      throw new TerminalError('Sandbox execution stopped unexpectedly.');
    case 'ok':
      return 'File written successfully.';
  }
}

async function runInSandbox(
  ctx: Context,
  sandboxId: string,
  command: string
): Promise<string> {
  const res = await ctx.objectClient(modal, sandboxId).execute(command);
  switch (res.type) {
    case 'result': {
      return `
      # Status Code
      ${res.result.statusCode}
      
      # Output
      ${res.result.output}

      # Error
      ${res.result.error}`;
    }
    case 'stopped':
    case 'unknown':
    case 'failed':
      throw new TerminalError(`Sandbox execution failed: ${res.type}`);
    case 'starting':
      throw new Error('Sandbox is still starting, please retry later.');
  }
}

async function streamModel(
  abortSignal: AbortSignal,
  history: ModelMessage[],
  stepId: string,
  topic: string
) {
  const { textStream, toolCalls, response, finishReason } = streamText({
    model: openai('gpt-4o-mini'),
    messages: history,
    abortSignal,
    tools: TOOLS,
  });

  const { publish } = await browserStream({ topic });

  await publish({ type: 'stepStreamStart', stepId });

  for await (const textPart of textStream) {
    await publish({ type: 'text', stepId, text: textPart });
  }

  const { messages } = await response;
  const calls = await toolCalls;
  const finished = await finishReason;

  await publish({ type: 'stepStreamEnd', stepId });

  return {
    finished,
    calls,
    messages, // <-- this might be large, and if we want we can store this off band, for example in S3, and provide a link to it instead.
  };
}

function extractFinalResult(messages: ModelMessage[]): string {
  const message = lastMessageContent(messages);
  const finalResultIndex = message.indexOf("### Final Result\n");
  if (finalResultIndex !== -1) {
    return message
      .substring(finalResultIndex + "### Final Result\n".length)
      .trim();
  }
  return message;
}

// Utility function to get the last message content
// There must be a better way.
function lastMessageContent(messages: ModelMessage[]): string {
  if (messages.length === 0) {
    return '<No messages generated>';
  }
  const lastMessage = messages[messages.length - 1];
  if (lastMessage.role !== 'assistant') {
    return '<Last message was not from the assistant>';
  }
  if (typeof lastMessage.content === 'string') {
    return lastMessage.content;
  }
  if (Array.isArray(lastMessage.content) && lastMessage.content.length > 0) {
    return lastMessage.content[0].type === 'text'
      ? lastMessage.content[0].text
      : '<No text in last message>';
  }
  return '<Last message content is not text>';
}

async function browserStream(opts: { topic: string }) {
  const publisher = await publisherClient(opts);

  const publish = async (message: StreamUIMessages) => {
    // do a few local retries, but never let an error bubble up to not
    // fail the step just if this stream fails
    for (let i = 0; i < 3; i++) {
      try {
        publisher.publish(message);
        return Promise.resolve();
      } catch (error) {
        await new Promise((resolve) => setTimeout(resolve, 250));
      }
    }
    return Promise.reject(new Error('Failed to publish message'));
  };
  return { publish };
}
