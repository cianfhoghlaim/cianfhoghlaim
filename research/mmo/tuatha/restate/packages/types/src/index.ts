import z from 'zod';

export const Entry = z.object({
  role: z.union([z.literal('agent'), z.literal('user')]),
  message: z.string(),
  artifactRef: z.string().optional(), // optionally link to file in S3
});
export type Entry = z.infer<typeof Entry>;

export const AgentTask = z.object({
  prompt: z.string(),
  context: z.array(Entry),
  maxIterations: z.number(),
  agentId: z.string(),
});
export type AgentTask = z.infer<typeof AgentTask>;

export const ContextArtifact = z.object({
  text: z.string(),
  reference: z.string().optional(),
});
export type ContextArtifact = z.infer<typeof ContextArtifact>;

export const PlanStep = z.object({
  id: z.string(),
  title: z.string(),
  status: z.enum(['pending', 'running', 'completed', 'error']),
  description: z.string(),
  prompt: z.string(),
});

export type PlanStep = z.infer<typeof PlanStep>;

export type StepInput = {
  taskId: string;
  stepId: string;
  sandboxId: string;
  task: AgentTask;
  step: PlanStep;
  s3prefix: string;
  planetScaleUrl: string;
  tempDirectory: string;
  topic: string;
  stepResults: string[];
};

export type StepResult = string;

export type StreamUIMessages =
  | {
      type: "planStart";
    }
  | {
      type: "plan";
      plan: PlanStep[];
    }
  | {
      type: "stepStreamStart";
      stepId: string;
    }
  | { type: "stepStreamEnd"; stepId: string }
  | { type: "stepStart"; stepId: string }
  | { type: "stepEnd"; stepId: string }
  | {
      type: "text";
      stepId: string;
      text: string;
    };
    

export type CommonResult =
  | { type: "starting" }
  | { type: "failed"; error: any }
  | { type: "unknown" }
  | { type: "stopped" };

export type ProvisionResult =
  | {
      type: "ok";
    }
  | CommonResult;

export type ExecResult =
  | {
      type: "result";
      result: {
        statusCode: number;
        output: string;
        error: string;
      };
    }
  | CommonResult;

export type WriteFileResult = { type: "ok" } | CommonResult;