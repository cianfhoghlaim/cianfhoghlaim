/**
 * Stagehand Local Server
 *
 * HTTP server providing Stagehand browser automation with:
 * - Local browser first (CDP/Playwright) for $0 cost
 * - Automatic Browserbase fallback when anti-bot detected
 * - Multi-LLM support (GLM-4.6, GLM-4.6v, Gemini 3 Flash)
 * - Session management with LRU cache
 */

import "dotenv/config";
import express, { type Request, type Response, type NextFunction } from "express";
import { Stagehand } from "@browserbasehq/stagehand";
import { z } from "zod";
import { SessionStore } from "./session-store.js";
import { detectAntiBotMeasures, isAntiBotError } from "./fallback/detector.js";

// Configuration
const PORT = parseInt(process.env.PORT ?? "3100", 10);
const HEADLESS = process.env.HEADLESS !== "false";
const MAX_SESSIONS = parseInt(process.env.MAX_SESSIONS ?? "10", 10);
const SESSION_TTL_MS = parseInt(process.env.SESSION_TTL_MS ?? "300000", 10);
const DEFAULT_MODEL = process.env.DEFAULT_MODEL ?? "glm-4.6";
const VISION_MODEL = process.env.VISION_MODEL ?? "glm-4.6v";
const AGENT_MODEL = process.env.AGENT_MODEL ?? "google/gemini-3-flash-preview";

// Initialize session store
const sessionStore = new SessionStore({
  maxCapacity: MAX_SESSIONS,
  ttlMs: SESSION_TTL_MS,
});

// Express app
const app = express();
app.use(express.json({ limit: "10mb" }));

// Request logging middleware
app.use((req: Request, res: Response, next: NextFunction) => {
  console.log(`[${new Date().toISOString()}] ${req.method} ${req.path}`);
  next();
});

// Schemas
const CreateSessionSchema = z.object({
  modelName: z.string().optional(),
  useCloud: z.boolean().optional().default(false),
  browserbaseApiKey: z.string().optional(),
  browserbaseProjectId: z.string().optional(),
});

const NavigateSchema = z.object({
  sessionId: z.string(),
  url: z.string().url(),
});

const ActSchema = z.object({
  sessionId: z.string(),
  action: z.string(),
  observedElement: z.any().optional(),
});

const ObserveSchema = z.object({
  sessionId: z.string(),
  instruction: z.string(),
});

const ExtractSchema = z.object({
  sessionId: z.string(),
  instruction: z.string(),
  schema: z.record(z.any()).optional(),
});

const AgentSchema = z.object({
  sessionId: z.string(),
  instruction: z.string(),
  maxSteps: z.number().optional().default(20),
  systemPrompt: z.string().optional(),
});

// Helper: Get API key for model
function getApiKeyForModel(modelName: string): string | undefined {
  if (modelName.startsWith("glm") || modelName.includes("zhipu")) {
    return process.env.ZAI_API_KEY;
  }
  if (modelName.includes("gemini") || modelName.includes("google")) {
    return process.env.GOOGLE_API_KEY;
  }
  if (modelName.includes("openai") || modelName.includes("gpt")) {
    return process.env.OPENAI_API_KEY;
  }
  if (modelName.includes("anthropic") || modelName.includes("claude")) {
    return process.env.ANTHROPIC_API_KEY;
  }
  // Default to OpenAI
  return process.env.OPENAI_API_KEY;
}

// Helper: Create Stagehand instance
async function createStagehand(
  useCloud: boolean,
  modelName: string,
  browserbaseApiKey?: string,
  browserbaseProjectId?: string
): Promise<Stagehand> {
  const apiKey = getApiKeyForModel(modelName);

  if (useCloud) {
    // Cloud (Browserbase) mode
    const stagehand = new Stagehand({
      env: "BROWSERBASE",
      verbose: 1,
      browserbaseSessionCreateParams: {
        projectId: browserbaseProjectId ?? process.env.BROWSERBASE_PROJECT_ID!,
        proxies: true,
        browserSettings: {
          blockAds: true,
          viewport: { width: 1920, height: 1080 },
        },
      },
    });

    await stagehand.init();
    return stagehand;
  }

  // Local mode
  const stagehand = new Stagehand({
    env: "LOCAL",
    verbose: 1,
    localBrowserLaunchOptions: {
      headless: HEADLESS,
      viewport: { width: 1920, height: 1080 },
    },
  });

  await stagehand.init();
  return stagehand;
}

// ============================================================================
// Routes
// ============================================================================

// Health check
app.get("/health", (req: Request, res: Response) => {
  const stats = sessionStore.getStats();
  res.json({
    status: "healthy",
    timestamp: new Date().toISOString(),
    config: {
      headless: HEADLESS,
      defaultModel: DEFAULT_MODEL,
      visionModel: VISION_MODEL,
      agentModel: AGENT_MODEL,
    },
    sessions: stats,
  });
});

// Create session
app.post("/session/create", async (req: Request, res: Response) => {
  try {
    const body = CreateSessionSchema.parse(req.body);
    const modelName = body.modelName ?? DEFAULT_MODEL;

    console.log(`[Session] Creating session (cloud: ${body.useCloud}, model: ${modelName})`);

    const stagehand = await createStagehand(
      body.useCloud,
      modelName,
      body.browserbaseApiKey,
      body.browserbaseProjectId
    );

    const sessionId = await sessionStore.createSession(
      stagehand,
      body.useCloud ? "BROWSERBASE" : "LOCAL",
      modelName
    );

    res.json({
      sessionId,
      env: body.useCloud ? "BROWSERBASE" : "LOCAL",
      modelName,
    });
  } catch (error) {
    console.error("[Session] Create failed:", error);
    res.status(500).json({
      error: "Failed to create session",
      details: String(error),
    });
  }
});

// Close session
app.post("/session/:sessionId/close", async (req: Request, res: Response) => {
  const { sessionId } = req.params;
  const closed = await sessionStore.closeSession(sessionId);

  if (closed) {
    res.json({ success: true, message: "Session closed" });
  } else {
    res.status(404).json({ error: "Session not found" });
  }
});

// Get session info
app.get("/session/:sessionId", (req: Request, res: Response) => {
  const { sessionId } = req.params;
  const session = sessionStore.getSession(sessionId);

  if (!session) {
    res.status(404).json({ error: "Session not found" });
    return;
  }

  res.json({
    sessionId,
    env: session.env,
    modelName: session.modelName,
    createdAt: session.createdAt.toISOString(),
    lastAccessedAt: session.lastAccessedAt.toISOString(),
  });
});

// Navigate
app.post("/navigate", async (req: Request, res: Response) => {
  try {
    const body = NavigateSchema.parse(req.body);
    const stagehand = sessionStore.getStagehand(body.sessionId);

    if (!stagehand) {
      res.status(404).json({ error: "Session not found" });
      return;
    }

    const page = stagehand.context.pages()[0];
    await page.goto(body.url, { waitUntil: "domcontentloaded" });

    // Check for anti-bot measures
    const detection = await detectAntiBotMeasures(page);

    res.json({
      success: true,
      url: page.url(),
      title: await page.title(),
      shouldFallback: detection.shouldFallback,
      signals: detection.signals,
    });
  } catch (error) {
    console.error("[Navigate] Failed:", error);
    res.status(500).json({
      success: false,
      error: String(error),
      shouldFallback: isAntiBotError(error),
    });
  }
});

// Observe (find elements)
app.post("/observe", async (req: Request, res: Response) => {
  try {
    const body = ObserveSchema.parse(req.body);
    const stagehand = sessionStore.getStagehand(body.sessionId);

    if (!stagehand) {
      res.status(404).json({ error: "Session not found" });
      return;
    }

    const elements = await stagehand.observe(body.instruction);

    res.json({
      success: true,
      elements,
      count: elements.length,
    });
  } catch (error) {
    console.error("[Observe] Failed:", error);
    res.status(500).json({
      success: false,
      error: String(error),
      shouldFallback: isAntiBotError(error),
    });
  }
});

// Act (perform action)
app.post("/act", async (req: Request, res: Response) => {
  try {
    const body = ActSchema.parse(req.body);
    const stagehand = sessionStore.getStagehand(body.sessionId);

    if (!stagehand) {
      res.status(404).json({ error: "Session not found" });
      return;
    }

    // Use observed element if provided (recommended pattern)
    if (body.observedElement) {
      await stagehand.act(body.observedElement);
    } else {
      await stagehand.act(body.action);
    }

    // Check for anti-bot after action
    const page = stagehand.context.pages()[0];
    const detection = await detectAntiBotMeasures(page);

    res.json({
      success: true,
      shouldFallback: detection.shouldFallback,
      signals: detection.signals,
    });
  } catch (error) {
    console.error("[Act] Failed:", error);
    res.status(500).json({
      success: false,
      error: String(error),
      shouldFallback: isAntiBotError(error),
    });
  }
});

// Extract (structured data extraction)
app.post("/extract", async (req: Request, res: Response) => {
  try {
    const body = ExtractSchema.parse(req.body);
    const stagehand = sessionStore.getStagehand(body.sessionId);

    if (!stagehand) {
      res.status(404).json({ error: "Session not found" });
      return;
    }

    let result: any;

    if (body.schema) {
      // Build Zod schema dynamically (simplified)
      const zodSchema = z.object(
        Object.fromEntries(
          Object.entries(body.schema).map(([key, value]) => [
            key,
            z.string().optional(),
          ])
        )
      );
      result = await stagehand.extract(body.instruction, zodSchema);
    } else {
      result = await stagehand.extract(body.instruction);
    }

    res.json({
      success: true,
      data: result,
    });
  } catch (error) {
    console.error("[Extract] Failed:", error);
    res.status(500).json({
      success: false,
      error: String(error),
      shouldFallback: isAntiBotError(error),
    });
  }
});

// Screenshot
app.post("/screenshot", async (req: Request, res: Response) => {
  try {
    const { sessionId, fullPage = false } = req.body;
    const stagehand = sessionStore.getStagehand(sessionId);

    if (!stagehand) {
      res.status(404).json({ error: "Session not found" });
      return;
    }

    const page = stagehand.context.pages()[0];
    const screenshot = await page.screenshot({
      fullPage,
      type: "png",
    });

    const base64 = screenshot.toString("base64");

    res.json({
      success: true,
      screenshot: base64,
      format: "png",
      width: 1920,
      height: 1080,
    });
  } catch (error) {
    console.error("[Screenshot] Failed:", error);
    res.status(500).json({
      success: false,
      error: String(error),
    });
  }
});

// Agent (autonomous multi-step execution)
app.post("/agent", async (req: Request, res: Response) => {
  try {
    const body = AgentSchema.parse(req.body);
    const session = sessionStore.getSession(body.sessionId);

    if (!session) {
      res.status(404).json({ error: "Session not found" });
      return;
    }

    const stagehand = session.stagehand;

    // Create agent with appropriate model
    const agent = stagehand.agent({
      model: {
        modelName: AGENT_MODEL,
        apiKey: getApiKeyForModel(AGENT_MODEL),
      },
      systemPrompt: body.systemPrompt ?? `You are a helpful assistant that can use a web browser.
        Do not ask follow up questions, the user will trust your judgement.`,
    });

    console.log(`[Agent] Executing: ${body.instruction.substring(0, 100)}...`);

    const result = await agent.execute({
      instruction: body.instruction,
      maxSteps: body.maxSteps,
      highlightCursor: true,
    });

    res.json({
      success: result.success,
      message: result.message,
      steps: result.steps,
    });
  } catch (error) {
    console.error("[Agent] Failed:", error);
    res.status(500).json({
      success: false,
      error: String(error),
      shouldFallback: isAntiBotError(error),
    });
  }
});

// Fallback upgrade endpoint
app.post("/session/:sessionId/upgrade-to-cloud", async (req: Request, res: Response) => {
  try {
    const { sessionId } = req.params;
    const session = sessionStore.getSession(sessionId);

    if (!session) {
      res.status(404).json({ error: "Session not found" });
      return;
    }

    if (session.env === "BROWSERBASE") {
      res.json({ success: true, message: "Already using cloud" });
      return;
    }

    console.log(`[Session] Upgrading ${sessionId} to BROWSERBASE`);

    const newStagehand = await createStagehand(true, session.modelName);
    await sessionStore.upgradeToCloud(sessionId, newStagehand);

    res.json({
      success: true,
      message: "Upgraded to BROWSERBASE",
      sessionId,
    });
  } catch (error) {
    console.error("[Upgrade] Failed:", error);
    res.status(500).json({
      success: false,
      error: String(error),
    });
  }
});

// ============================================================================
// Server lifecycle
// ============================================================================

const server = app.listen(PORT, () => {
  console.log(`
================================================================================
  Stagehand Local Server
================================================================================
  Port:          ${PORT}
  Headless:      ${HEADLESS}
  Max Sessions:  ${MAX_SESSIONS}
  Session TTL:   ${SESSION_TTL_MS}ms

  Models:
    Default:     ${DEFAULT_MODEL}
    Vision:      ${VISION_MODEL}
    Agent:       ${AGENT_MODEL}

  API Keys:
    Z.AI:        ${process.env.ZAI_API_KEY ? "configured" : "missing"}
    Google:      ${process.env.GOOGLE_API_KEY ? "configured" : "missing"}
    OpenAI:      ${process.env.OPENAI_API_KEY ? "configured" : "missing"}
    Browserbase: ${process.env.BROWSERBASE_API_KEY ? "configured" : "missing"}

  Endpoints:
    GET  /health              - Health check and stats
    POST /session/create      - Create new browser session
    POST /session/:id/close   - Close session
    GET  /session/:id         - Get session info
    POST /navigate            - Navigate to URL
    POST /observe             - Find elements
    POST /act                 - Perform action
    POST /extract             - Extract structured data
    POST /screenshot          - Capture screenshot
    POST /agent               - Autonomous multi-step execution
    POST /session/:id/upgrade-to-cloud - Fallback to Browserbase
================================================================================
`);
});

// Graceful shutdown
async function shutdown(signal: string) {
  console.log(`\n[Server] Received ${signal}, shutting down...`);

  server.close(() => {
    console.log("[Server] HTTP server closed");
  });

  await sessionStore.shutdown();
  process.exit(0);
}

process.on("SIGINT", () => shutdown("SIGINT"));
process.on("SIGTERM", () => shutdown("SIGTERM"));
