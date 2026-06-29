# 103 - Hugging Face JS libraries (deferred site)

**Status:** Researched 2026-06-29 via firecrawl MCP
**Canonical source:** https://huggingface.co/docs/huggingface.js/index
**Cianfhoghlaim footprint:** HF Hub is used for OCR model verification
(per the OCR VLM registry change) + the 4 sub-projects in
`spaces/{anti-phish,data-engineering,...}` (HF Space publishing per
the `spaces-cicd-pipeline` spec).

## TL;DR

Hugging Face JS is a collection of 10 TypeScript-first libraries
that interact with the HF Hub, Inference Providers, MCP servers,
and agent orchestration. The 5 most relevant for cianfhoghlaim:

1. **@huggingface/hub** — create/delete repos, commit/download
   files (used by `spaces-cicd-pipeline`)
2. **@huggingface/inference** — call 100,000+ models via the
   serverless Inference Providers (Sambanova, Together, Replicate,
   Fal.ai, Cohere) or dedicated Inference Endpoints
3. **@huggingface/mcp-client** — Agent library that connects to
   MCP servers (Playwright, etc.) and calls LLM tools
4. **@huggingface/gguf** — parse remotely hosted GGUF model files
5. **@huggingface/tiny-agents** — model-agnostic agent builder

## Code

```ts
// 1. Create + upload to a Space (used by spaces-cicd-pipeline)
import { createRepo, uploadFile } from "@huggingface/hub";
await createRepo({
  repo: { type: "space", name: "my-user/my-space" },
  accessToken: HF_TOKEN,
  sdk: "static",
});
await uploadFile({
  repo: "my-user/my-space",
  accessToken: HF_TOKEN,
  file: { path: "index.html", content: new Blob(["<h1>Hi</h1>"]) },
});

// 2. Inference via third-party provider (100,000+ models)
import { InferenceClient } from "@huggingface/inference";
const client = new InferenceClient(HF_TOKEN);
const out = await client.chatCompletion({
  model: "meta-llama/Llama-3.1-8B-Instruct",
  provider: "sambanova", // or together, fal-ai, replicate, cohere
  messages: [{ role: "user", content: "Hello!" }],
  max_tokens: 512,
});

// 3. MCP agent (Playwright tool + LLM)
import { Agent } from "@huggingface/mcp-client";
const agent = new Agent({
  provider: "auto",
  model: "Qwen/Qwen2.5-72B-Instruct",
  apiKey: HF_TOKEN,
  servers: [{ command: "npx", args: ["@playwright/mcp@latest"] }],
});
for await (const chunk of agent.run("Top 5 trending HF models?")) {
  console.log(chunk.choices[0]?.delta?.content);
}
```

## Env

- `HF_TOKEN` — set in `.infisical.env` to
  `infisical://dev-baile/huggingface/token` (used by the 4
  `spaces/*/` sub-projects for Space publishing)

## ccc anchors

- `huggingface` skill at `.agents/skills/huggingface/SKILL.md`
- `spaces-cicd-pipeline` spec (the 4 sub-projects use HF Hub to
  publish Spaces)
- `oideachais-cocoindex-v1` skill (HF model verification)

## Anti-patterns

- **Using `@huggingface/inference` for batch jobs** — the
  serverless API has rate limits; use dedicated Inference Endpoints
  for >1K requests/min
- **Hardcoding `model: "Qwen/..."`** — omit `model` to use the
  recommended model for the task
- **Skipping `provider: "auto"`** — explicit providers fail when
  the model is unavailable on that provider
- **Mixing `InferenceClient` with raw `fetch`** — use the client
  for all HF API calls (handles auth + retries + streaming)

## Decision matrix

| Use `@huggingface/inference` when | Use BAML when | Use Firecrawl when |
|:--|:--|:--|
| Calling HF models directly | Calling any LLM (incl. HF) | Web scraping (not ML) |
| 100,000+ model catalog | Structured extraction | Public website data |
| Multimodal (image, audio) | BAML schema validation | PDF/DOCX parsing |
| Provider failover (auto) | Type-safe Pydantic/TS Zod | Change monitoring |

The cianfhoghlaim OCR VLM registry uses HF Hub API directly via
the `huggingface_hub` Python client (not the JS one), but the
JS client is the canonical pattern for the 4 `spaces/*/`
sub-projects and any future browser-side inference.
