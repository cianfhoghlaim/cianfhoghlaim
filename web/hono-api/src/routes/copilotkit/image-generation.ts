/**
 * Image Generation CopilotKit Actions — Phase L
 *
 * The canonical Hono API surface for the `image_generation_agent` (the
 * 13th main ADK agent in `agents/agent_registry.py:AGENT_REGISTRY`).
 *
 * This module exposes the 5 image_gen tools as CopilotKit actions
 * + an AG-UI streaming endpoint for the central Cianfhoghlaim homepage.
 *
 * Routes:
 * - POST /api/copilotkit/image-gen/list-models      → list_image_models
 * - POST /api/copilotkit/image-gen/generate-2d     → generate_2d_asset
 * - POST /api/copilotkit/image-gen/generate-texture → generate_texture
 * - POST /api/copilotkit/image-gen/style-match      → style_match
 * - POST /api/copilotkit/image-gen/register         → cocoindex_register
 * - GET  /api/copilotkit/image-gen/health          → health check
 *
 * Reference:
 *   openspec/changes/2026-08-13-web-monorepo-consolidation-and-agent-integration-v1/
 *   specs/image-generation-agent/spec.md
 */
import { Hono } from "hono";

type ImageGenRole = "default" | "fast" | "bilingual" | "legacy" | "diagrams";

type Generate2dAssetRequest = {
  prompt: string;
  role?: ImageGenRole;
  style?: string;
  width?: number;
  height?: number;
};

type GenerateTextureRequest = {
  name: string;
  pattern?: string;
  width?: number;
  height?: number;
};

type StyleMatchRequest = {
  reference_prompt: string;
  target_prompt: string;
  count?: number;
  role?: ImageGenRole;
};

type CocoIndexRegisterRequest = {
  asset_url: string;
  asset_kind?: "image_2d" | "texture" | "diagram" | "sprite" | "avatar";
  metadata?: Record<string, unknown>;
};

/**
 * The CopilotKit action runtime — wraps each tool as a POST endpoint.
 * The actual tool implementations live in
 * `agents/adk/tools/image_generation.py` (Python); the Hono gateway
 * is the HTTP boundary that the web (TanStack Start + CopilotKit v2 +
 * AG-UI) calls.
 *
 * In production, the gateway forwards the request to the Python
 * `image_generation_agent` via the AG-UI SSE protocol
 * (per https://ag-ui.com). In dev (no GPU), the gateway returns a
 * stub response so the UI can be developed without the full stack.
 */
const imageGenApp = new Hono();

imageGenApp.get("/health", (c) =>
  c.json({
    status: "ok",
    service: "hono-api-image-gen",
    agent: "image_generation_agent",
    tools: [
      "list_image_models",
      "generate_2d_asset",
      "generate_texture",
      "style_match",
      "cocoindex_register",
    ],
    image_gen_models: [
      "local/image/flux2-dev",
      "local/image/z-image-turbo",
      "local/image/qwen-image",
      "local/image/sdxl",
      "local/image/fibo",
    ],
    timestamp: new Date().toISOString(),
  }),
);

imageGenApp.post("/list-models", async (c) => {
  // Forward to agents/adk/tools/image_generation.py:list_image_models()
  // In production, the Python service responds with the MODEL_REGISTRY
  // filter(family='image_gen') list. In dev, we stub.
  return c.json({
    stub: true,
    count: 5,
    available_count: 5,
    models: [
      {
        key: "local/image/flux2-dev",
        role: "default",
        upstream_id: "black-forest-labs/flux2-dev",
        litellm_alias: "local/image/flux2-dev",
        available: true,
      },
      {
        key: "local/image/z-image-turbo",
        role: "fast",
        upstream_id: "stabilityai/z-image-turbo",
        litellm_alias: "local/image/z-image-turbo",
        available: true,
      },
      {
        key: "local/image/qwen-image",
        role: "bilingual",
        upstream_id: "qwenlm/qwen-image",
        litellm_alias: "local/image/qwen-image",
        available: true,
      },
      {
        key: "local/image/sdxl",
        role: "legacy",
        upstream_id: "stabilityai/sdxl",
        litellm_alias: "local/image/sdxl",
        available: true,
      },
      {
        key: "local/image/fibo",
        role: "diagrams",
        upstream_id: "fibonet/fibo",
        litellm_alias: "local/image/fibo",
        available: true,
      },
    ],
    generated_at: new Date().toISOString(),
  });
});

imageGenApp.post("/generate-2d", async (c) => {
  const body = (await c.req.json()) as Generate2dAssetRequest;
  const {
    prompt,
    role = "default",
    style = null,
    width = 1024,
    height = 1024,
  } = body;

  // Forward to agents/adk/tools/image_generation.py:generate_2d_asset()
  // Stubbed response in dev; production response from the Python service.
  return c.json({
    stub: true,
    asset_id: crypto.randomUUID(),
    model: `local/image/${roleToModel(role)}`,
    role,
    prompt,
    style,
    width,
    height,
    file_path: `/tmp/cianfhoghlaim/assets/image_gen/${crypto.randomUUID()}.png`,
    url: `/assets/image_gen/${crypto.randomUUID()}.png`,
    sha256: "stub-sha256-hash",
    size_bytes: 0,
    created_at: new Date().toISOString(),
    duration_ms: 0,
  });
});

imageGenApp.post("/generate-texture", async (c) => {
  const body = (await c.req.json()) as GenerateTextureRequest;
  const { name, pattern = "default", width = 512, height = 512 } = body;

  return c.json({
    stub: true,
    texture_id: crypto.randomUUID(),
    name,
    pattern,
    model: "local/image/fibo", // diagrams role
    file_path: `/tmp/cianfhoghlaim/assets/textures/${crypto.randomUUID()}.png`,
    url: `/assets/textures/${crypto.randomUUID()}.png`,
    sha256: "stub-sha256-hash",
    size_bytes: 0,
    width,
    height,
    created_at: new Date().toISOString(),
    duration_ms: 0,
  });
});

imageGenApp.post("/style-match", async (c) => {
  const body = (await c.req.json()) as StyleMatchRequest;
  const {
    reference_prompt,
    target_prompt,
    count = 3,
    role = "default",
  } = body;

  return c.json({
    stub: true,
    reference_prompt,
    target_prompt,
    model: `local/image/${roleToModel(role)}`,
    role,
    count,
    variants: Array.from({ length: count }, (_, i) => ({
      variant_id: crypto.randomUUID(),
      variant_index: i,
      file_path: `/tmp/cianfhoghlaim/assets/image_gen/${crypto.randomUUID()}.png`,
      url: `/assets/image_gen/${crypto.randomUUID()}.png`,
      sha256: "stub-sha256-hash",
    })),
    duration_ms: 0,
  });
});

imageGenApp.post("/register", async (c) => {
  const body = (await c.req.json()) as CocoIndexRegisterRequest;
  const { asset_url, asset_kind = "image_2d", metadata = null } = body;

  return c.json({
    stub: true,
    registered: false,
    asset_url,
    asset_kind,
    flow: "image_generation",
    indexed_at: new Date().toISOString(),
    record_id: hashStub(asset_url),
    error:
      "cocoindex_flows.media.image_generation_flow not yet plumbed through Hono (PR 5 in mega-change)",
    metadata,
  });
});

/**
 * Helper: map an image_gen role to its canonical MODEL_REGISTRY key.
 */
function roleToModel(role: ImageGenRole): string {
  switch (role) {
    case "fast":
      return "z-image-turbo";
    case "bilingual":
      return "qwen-image";
    case "legacy":
      return "sdxl";
    case "diagrams":
      return "fibo";
    case "default":
    default:
      return "flux2-dev";
  }
}

/**
 * Stub SHA-256 hash (deterministic from input).
 */
function hashStub(input: string): string {
  let h = 0;
  for (let i = 0; i < input.length; i++) {
    h = (h * 31 + input.charCodeAt(i)) | 0;
  }
  return Math.abs(h).toString(16).padStart(16, "0").slice(0, 16);
}

export default imageGenApp;
