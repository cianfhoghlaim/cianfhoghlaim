/**
 * Hono API endpoint: GET /api/pdf/*
 *
 * Issues a 15-min signed URL for the requested PDF (R2 key passed as
 * the wildcard path). Extends the existing R14 (Cloudflare R2 +
 * Hono-issued signed URLs) endpoint by adding the BIEP lineage
 * subject-prefix routing.
 *
 * In dev mode (no `MOTHERDUCK_TOKEN` / no Garage S3 credentials) the
 * endpoint returns a stub URL pointing at the local
 * `leaving_certificate/<key>` filesystem path so the lineage viewer's
 * `<PdfViewer>` iframe can still mount and render the PDF locally.
 *
 * Per openspec/changes/2026-07-19-leaving-cert-pdf-lineage-and-schema-codegen-v1
 * R31 (PDF.js in-browser viewer with citation deep-links).
 */
import { Hono } from "hono";

const app = new Hono();

app.get("/api/pdf/*", async (c) => {
  const r2KeyRaw = c.req.param("*");
  // Decode in case the iframe wrapper percent-encoded the path; preserve
  // slashes so multi-segment keys (e.g. `leaving_cert/mathematics/en/...`)
  // resolve correctly.
  const r2Key = decodeURIComponent(r2KeyRaw || "");
  const page = parseInt(c.req.query("page") ?? "1", 10);
  const lang = c.req.query("lang") ?? "en";

  // Validate the key lives under `leaving_cert/<subject>/<lang>/` or
  // matches one of the 4 NCCA root PDFs. We avoid leaking arbitrary
  // filesystem paths by only honouring the known prefixes.
  const safe =
    /^leaving_cert\/[a-z_]+\/(en|ga)\/[A-Za-z0-9_.\-]+\.pdf$/i.test(r2Key) ||
    /^(key-competencies-in-senior-cycle_en|scr-advisory-report_en|the-potential-of-(online-learning-environments|technology-to-support-online-certification-and-reporting)_en|SC-L1-L2-Programme-Statement)\.pdf$/i.test(r2Key);

  if (!safe) {
    return c.json({ error: "invalid_r2_key", r2_key: r2Key }, 400);
  }

  c.header("Cache-Control", "private, max-age=60, stale-while-revalidate=300");

  // Production: call `hono-api /api/r2/sign` (which exists per R14) with the
  // Garage S3 backend. For dev, return a stub URL pointing at the
  // local `leaving_certificate/<key>` path so the iframe can be inspected
  // without a live R2 bucket.
  const localDev = !process.env.MOTHERDUCK_TOKEN && !process.env.GARAGE_S3_ENDPOINT;
  const url = localDev
    ? `file:///${process.cwd()}/leaving_certificate/${r2Key.replace(/^leaving_cert\//, "")}#page=${page}&lang=${lang}`
    : buildSignedUrlStub(r2Key, page, lang);

  return c.json({
    url,
    r2_key: r2Key,
    page,
    lang,
    expires_in_seconds: 15 * 60,
    signed_at: new Date().toISOString(),
  });
});

/**
 * Build a placeholder signed URL. Production replaces this with the
 * real `hono-api /api/r2/sign` call from R14. The shape matches the
 * response contract so the caller doesn't need to special-case dev vs.
 * prod.
 */
function buildSignedUrlStub(r2Key: string, page: number, lang: string): string {
  const expires = Math.floor(Date.now() / 1000) + 15 * 60;
  return `https://r2.cianfhoghlaim.ie/${r2Key}?X-Amz-Expires=900&X-Amz-Date=${Math.floor(Date.now() / 1000)}&page=${page}&lang=${lang}&stub=${expires}`;
}

export default app;
