// /api/r2 — Hono routes for issuing signed R2 URLs (no Worker needed)
//
// Per openspec/changes/2026-07-18-british-isles-portal-activation-v3/
// R14: Cloudflare R2 + Hono-issued signed URLs (free tier; no Workers Paid).
//
// Why Hono-issued and not Worker-issued:
//   - Cloudflare Workers free tier is sufficient for the static site + the
//     per-subject marimo notebooks (deployed via Workers + Container)
//   - Workers Paid ($5/mo) is needed for Cloudflare Workers that issue
//     signed R2 URLs (because of the R2 binding bundling); Hono-issued
//     URLs from the existing `hono-api` service (which already has S3
//     credentials via the Garage S3 backend) are FREE — no extra tier
//     required
//   - The signed URL has a 15-minute TTL; this is fine for PDF assets
//
// Endpoints:
//   GET  /api/r2/sign?key=<r2-key>            → 200 with { url, expires_at, key }
//   GET  /api/r2/health                       → 200 OK
//
// R2 keys follow the pattern:
//   oideachais/leaving_cert/<subject>/<lang>/<year>/<file>.pdf

import { Hono } from "hono";
import { createS3Client, presignGetObject } from "@cianfhoghlaim/api";

// ---------------------------------------------------------------------------
// Configuration (from environment)
// ---------------------------------------------------------------------------

const R2_BUCKET       = process.env.R2_BUCKET       || "oideachais-pdfs";
const R2_ENDPOINT     = process.env.R2_ENDPOINT     || "https://<accountid>.r2.cloudflarestorage.com";
const R2_ACCESS_KEY   = process.env.R2_ACCESS_KEY   || process.env.AWS_ACCESS_KEY_ID   || "";
const R2_SECRET_KEY   = process.env.R2_SECRET_KEY   || process.env.AWS_SECRET_ACCESS_KEY || "";
const R2_REGION       = process.env.R2_REGION       || "auto";
const R2_PRESIGN_TTL  = Number(process.env.R2_PRESIGN_TTL) || 900;  // 15 minutes

// ---------------------------------------------------------------------------
// Allow-list of R2 key prefixes (defense-in-depth)
// ---------------------------------------------------------------------------

const ALLOWED_PREFIXES: readonly string[] = [
  "oideachais/leaving_cert/",
  "oideachais/primary/",
  "oideachais/junior_cycle/",
  "oideachais/tertiary/",
  "oideachais/aistear/",
  "marimo/",
];

function isKeyAllowed(key: string): boolean {
  if (!key || key.includes("..") || key.startsWith("/")) return false;
  return ALLOWED_PREFIXES.some((p) => key.startsWith(p));
}

// ---------------------------------------------------------------------------
// Lazy S3 client (compatible with R2 via the S3 API)
// ---------------------------------------------------------------------------

let _s3 = null as ReturnType<typeof createS3Client> | null;
function getS3() {
  if (_s3) return _s3;
  if (!R2_ACCESS_KEY || !R2_SECRET_KEY) {
    throw new Error("R2 credentials missing — set R2_ACCESS_KEY + R2_SECRET_KEY");
  }
  _s3 = createS3Client({
    endpoint: R2_ENDPOINT,
    region: R2_REGION,
    credentials: { accessKeyId: R2_ACCESS_KEY, secretAccessKey: R2_SECRET_KEY },
  });
  return _s3;
}

// ---------------------------------------------------------------------------
// Hono router
// ---------------------------------------------------------------------------

export const r2Sign = new Hono();

// Liveness probe
r2Sign.get("/health", (c) =>
  c.json({ ok: true, bucket: R2_BUCKET, ttl_seconds: R2_PRESIGN_TTL }),
);

// GET /api/r2/sign?key=<r2-key>
// Returns { url, expires_at, key, ttl_seconds }
r2Sign.get("/sign", async (c) => {
  const key = c.req.query("key");
  if (!key) {
    return c.json({ error: "missing_key", message: "Pass ?key=<r2-key>" }, 400);
  }
  if (!isKeyAllowed(key)) {
    return c.json(
      {
        error: "disallowed_key",
        message: `Key must start with one of: ${ALLOWED_PREFIXES.join(", ")}`,
      },
      403,
    );
  }

  try {
    const s3 = getS3();
    const url = await presignGetObject(s3, R2_BUCKET, key, R2_PRESIGN_TTL);
    const expires_at = new Date(Date.now() + R2_PRESIGN_TTL * 1000).toISOString();
    return c.json({ url, expires_at, key, ttl_seconds: R2_PRESIGN_TTL });
  } catch (e) {
    console.error("[r2-sign] failed:", e);
    return c.json(
      { error: "sign_failed", message: e instanceof Error ? e.message : String(e) },
      500,
    );
  }
});

// GET /api/r2/list?prefix=<prefix>&limit=N
// Optional helper — list available R2 keys under an allowed prefix
r2Sign.get("/list", async (c) => {
  const prefix = c.req.query("prefix") || "oideachais/leaving_cert/";
  const limit = Math.min(Number(c.req.query("limit")) || 100, 1000);
  if (!isKeyAllowed(prefix)) {
    return c.json({ error: "disallowed_prefix" }, 403);
  }
  try {
    const s3 = getS3();
    // Lazy import to avoid pulling aws-sdk on cold start if not needed
    const { listObjects } = await import("@cianfhoghlaim/api");
    const items = await listObjects(s3, R2_BUCKET, prefix, limit);
    return c.json({ items, count: items.length });
  } catch (e) {
    console.error("[r2-list] failed:", e);
    return c.json(
      { error: "list_failed", message: e instanceof Error ? e.message : String(e) },
      500,
    );
  }
});
