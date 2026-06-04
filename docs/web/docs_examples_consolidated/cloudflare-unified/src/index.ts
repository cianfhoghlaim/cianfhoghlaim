import { Hono } from "hono";
import { cors } from "hono/cors";
import type { D1Database, KVNamespace, R2Bucket, Ai, IncomingRequestCfProperties } from "@cloudflare/workers-types";
import { createAuth } from "./lib/auth";
import { extractGeolocation, formatLocation } from "./lib/geo";
import { getFromCache, setInCache } from "./storage/kv";
import { uploadFile, downloadFile, listFiles, getFileMetadata } from "./storage/r2";

/**
 * Cloudflare Bindings
 */
export interface CloudflareBindings {
  DATABASE: D1Database;
  CACHE: KVNamespace;
  FILES: R2Bucket;
  AI?: Ai; // Optional - requires Cloudflare auth
}

/**
 * Hono Variables
 */
type Variables = {
  auth: ReturnType<typeof createAuth>;
  cf: IncomingRequestCfProperties;
};

const app = new Hono<{ Bindings: CloudflareBindings; Variables: Variables }>();

// CORS configuration for auth routes
app.use(
  "/api/auth/**",
  cors({
    origin: "*", // In production, replace with your actual domain
    allowHeaders: ["Content-Type", "Authorization"],
    allowMethods: ["POST", "GET", "OPTIONS"],
    exposeHeaders: ["Content-Length"],
    maxAge: 600,
    credentials: true,
  })
);

// Middleware to initialize auth and cf context for each request
app.use("*", async (c, next) => {
  const cf = (c.req.raw as any).cf || {};
  const auth = createAuth({ DATABASE: c.env.DATABASE, CACHE: c.env.CACHE }, cf);

  c.set("auth", auth);
  c.set("cf", cf);

  await next();
});

// Auth routes - handle all Better Auth endpoints
app.all("/api/auth/*", async (c) => {
  const auth = c.get("auth");
  return auth.handler(c.req.raw);
});

// Home page with dashboard
app.get("/", async (c) => {
  const html = `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Cloudflare Unified - All Services Demo</title>
  <style>
    body {
      font-family: system-ui, -apple-system, sans-serif;
      max-width: 900px;
      margin: 0 auto;
      padding: 20px;
      background: #f9fafb;
    }
    .card {
      background: white;
      border: 1px solid #e5e7eb;
      border-radius: 8px;
      padding: 24px;
      margin: 20px 0;
      box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .header {
      text-align: center;
      margin-bottom: 24px;
    }
    .title {
      font-size: 2rem;
      font-weight: bold;
      margin: 0;
      color: #1f2937;
    }
    .subtitle {
      color: #6b7280;
      font-size: 0.875rem;
      margin: 8px 0 0 0;
    }
    .badge {
      display: inline-block;
      padding: 4px 12px;
      margin: 4px;
      border-radius: 12px;
      font-size: 0.75rem;
      font-weight: 600;
    }
    .badge-d1 { background: #dbeafe; color: #1e40af; }
    .badge-kv { background: #fef3c7; color: #92400e; }
    .badge-r2 { background: #dcfce7; color: #166534; }
    .badge-ai { background: #fce7f3; color: #9f1239; }
    button {
      padding: 10px 20px;
      margin: 8px 4px;
      border: 1px solid #d1d5db;
      border-radius: 6px;
      cursor: pointer;
      font-size: 0.875rem;
      font-weight: 500;
      transition: all 0.2s;
    }
    button:hover { background: #f3f4f6; }
    .primary-btn {
      background: #3b82f6;
      color: white;
      border-color: #3b82f6;
    }
    .primary-btn:hover {
      background: #2563eb;
    }
    .info-row {
      margin: 12px 0;
      padding: 8px 0;
      border-bottom: 1px solid #f3f4f6;
    }
    .info-row:last-child { border-bottom: none; }
    .info-row strong {
      display: inline-block;
      width: 140px;
      color: #4b5563;
    }
    #status { font-weight: 600; color: #059669; }
    .section-title {
      font-size: 1.25rem;
      font-weight: 600;
      margin: 24px 0 12px 0;
      color: #1f2937;
    }
  </style>
</head>
<body>
  <div class="card">
    <div class="header">
      <h1 class="title">Cloudflare Unified</h1>
      <p class="subtitle">Complete Cloudflare Workers Platform Demo</p>
      <div>
        <span class="badge badge-d1">D1 Database</span>
        <span class="badge badge-kv">KV Cache</span>
        <span class="badge badge-r2">R2 Storage</span>
        <span class="badge badge-ai">Workers AI</span>
      </div>
    </div>

    <div id="status">Loading...</div>

    <div id="not-logged-in" style="display:none;">
      <h3 class="section-title">Authentication</h3>
      <button onclick="loginAnonymously()" class="primary-btn">Login Anonymously</button>
    </div>

    <div id="logged-in" style="display:none;">
      <h3 class="section-title">User Information</h3>
      <div id="user-info"></div>

      <h3 class="section-title">Geolocation (Cloudflare CF Object)</h3>
      <div id="geo-info"></div>

      <h3 class="section-title">Actions</h3>
      <button onclick="testAI()" class="primary-btn">Test Workers AI</button>
      <button onclick="testCache()">Test KV Cache</button>
      <button onclick="testR2()">Test R2 Storage</button>
      <button onclick="logout()">Logout</button>

      <div id="result-area"></div>
    </div>
  </div>

  <script>
    let currentUser = null;

    async function checkStatus() {
      try {
        const response = await fetch('/api/auth/get-session', {
          credentials: 'include'
        });

        if (!response.ok) {
          showNotLoggedIn();
          return;
        }

        const text = await response.text();
        if (!text || text.trim() === '') {
          showNotLoggedIn();
          return;
        }

        const result = JSON.parse(text);
        if (result?.session) {
          currentUser = result.user;
          await showLoggedIn();
        } else {
          showNotLoggedIn();
        }
      } catch (error) {
        console.error('Error checking status:', error);
        showNotLoggedIn();
      }
    }

    async function loginAnonymously() {
      try {
        const response = await fetch('/api/auth/sign-in/anonymous', {
          method: 'POST',
          credentials: 'include',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({})
        });

        if (!response.ok) {
          const text = await response.text();
          if (text.includes('ANONYMOUS_USERS_CANNOT_SIGN_IN_AGAIN_ANONYMOUSLY')) {
            alert('Already logged in anonymously!');
            await checkStatus();
            return;
          }
          alert('Login failed: ' + text);
          return;
        }

        const result = await response.json();
        if (result.user) {
          currentUser = result.user;
          await showLoggedIn();
        }
      } catch (error) {
        alert('Login failed: ' + error.message);
      }
    }

    async function logout() {
      try {
        await fetch('/api/auth/sign-out', {
          method: 'POST',
          credentials: 'include',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({})
        });
        currentUser = null;
        showNotLoggedIn();
        document.getElementById('result-area').innerHTML = '';
      } catch (error) {
        alert('Logout failed: ' + error.message);
      }
    }

    async function testAI() {
      showResult('Testing Workers AI...');
      try {
        const response = await fetch('/api/ai/summarize', {
          method: 'POST',
          credentials: 'include',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            text: 'Cloudflare Workers is a serverless platform that runs JavaScript code at the edge.'
          })
        });
        const result = await response.json();
        showResult('<strong>AI Result:</strong><br>' + JSON.stringify(result, null, 2));
      } catch (error) {
        showResult('<strong>AI Error:</strong> ' + error.message);
      }
    }

    async function testCache() {
      showResult('Testing KV Cache...');
      try {
        const response = await fetch('/api/cache/test', { credentials: 'include' });
        const result = await response.json();
        showResult('<strong>Cache Result:</strong><br>' + JSON.stringify(result, null, 2));
      } catch (error) {
        showResult('<strong>Cache Error:</strong> ' + error.message);
      }
    }

    async function testR2() {
      showResult('Testing R2 Storage...');
      try {
        const response = await fetch('/api/files/list', { credentials: 'include' });
        const result = await response.json();
        showResult('<strong>R2 Result:</strong><br>' + JSON.stringify(result, null, 2));
      } catch (error) {
        showResult('<strong>R2 Error:</strong> ' + error.message);
      }
    }

    function showResult(html) {
      document.getElementById('result-area').innerHTML =
        '<div class="card" style="margin-top: 20px;"><pre style="white-space: pre-wrap;">' + html + '</pre></div>';
    }

    async function showLoggedIn() {
      document.getElementById('status').innerHTML = 'Status: Logged In';
      document.getElementById('not-logged-in').style.display = 'none';
      document.getElementById('logged-in').style.display = 'block';

      if (currentUser) {
        document.getElementById('user-info').innerHTML =
          '<div class="info-row"><strong>User ID:</strong> ' + currentUser.id + '</div>' +
          '<div class="info-row"><strong>Email:</strong> ' + (currentUser.email || 'Anonymous') + '</div>' +
          '<div class="info-row"><strong>Name:</strong> ' + (currentUser.name || 'Anonymous User') + '</div>';

        try {
          const geoResponse = await fetch('/api/geo', { credentials: 'include' });
          const geoData = await geoResponse.json();

          let geoHtml = '';
          if (geoData.city) geoHtml += '<div class="info-row"><strong>Location:</strong> ' + geoData.city + ', ' + (geoData.country || '') + '</div>';
          if (geoData.timezone) geoHtml += '<div class="info-row"><strong>Timezone:</strong> ' + geoData.timezone + '</div>';
          if (geoData.colo) geoHtml += '<div class="info-row"><strong>Data Center:</strong> ' + geoData.colo + '</div>';
          if (geoData.latitude) geoHtml += '<div class="info-row"><strong>Coordinates:</strong> ' + geoData.latitude + ', ' + geoData.longitude + '</div>';

          document.getElementById('geo-info').innerHTML = geoHtml || '<div class="info-row">Geolocation unavailable</div>';
        } catch (error) {
          document.getElementById('geo-info').innerHTML = '<div class="info-row">Error fetching geolocation</div>';
        }
      }
    }

    function showNotLoggedIn() {
      document.getElementById('status').innerHTML = 'Status: Not Logged In';
      document.getElementById('not-logged-in').style.display = 'block';
      document.getElementById('logged-in').style.display = 'none';
    }

    checkStatus();
  </script>
</body>
</html>
  `;
  return c.html(html);
});

// Geolocation API endpoint
app.get("/api/geo", async (c) => {
  const cf = c.get("cf");
  const geo = extractGeolocation(cf);

  return c.json({
    ...geo,
    formatted: formatLocation(geo),
  });
});

// AI endpoint - text summarization
app.post("/api/ai/summarize", async (c) => {
  const auth = c.get("auth");

  // Check authentication
  const session = await auth.api.getSession({ headers: c.req.raw.headers });
  if (!session?.session) {
    return c.json({ error: "Unauthorized" }, 401);
  }

  try {
    const { text } = await c.req.json();

    // Check if AI binding is available (requires Cloudflare auth)
    if (!c.env.AI) {
      return c.json({
        summary: `[AI not available - requires Cloudflare login] Original text: "${text.substring(0, 100)}..."`,
        note: "Run 'npx wrangler login' and uncomment AI binding in wrangler.jsonc",
        cached: false,
      });
    }

    const result = await c.env.AI.run("@cf/facebook/bart-large-cnn", {
      input_text: text,
      max_length: 1024,
    });

    return c.json({
      summary: result,
      cached: false,
    });
  } catch (error) {
    return c.json({ error: (error as Error).message }, 500);
  }
});

// KV Cache endpoint - test cache functionality
app.get("/api/cache/test", async (c) => {
  const auth = c.get("auth");

  // Check authentication
  const session = await auth.api.getSession({ headers: c.req.raw.headers });
  if (!session?.session) {
    return c.json({ error: "Unauthorized" }, 401);
  }

  const cacheKey = "test-cache-key";

  // Try to get from cache
  let cached = await getFromCache<{ value: string; timestamp: string }>(c.env.CACHE, cacheKey);

  if (cached) {
    return c.json({
      cached: true,
      data: cached,
    });
  }

  // Set new value in cache
  const newValue = {
    value: "Hello from KV Cache!",
    timestamp: new Date().toISOString(),
  };

  await setInCache(c.env.CACHE, cacheKey, newValue, { ttl: 300 });

  return c.json({
    cached: false,
    data: newValue,
  });
});

// R2 File Storage endpoints
app.get("/api/files/list", async (c) => {
  const auth = c.get("auth");

  // Check authentication
  const session = await auth.api.getSession({ headers: c.req.raw.headers });
  if (!session?.session) {
    return c.json({ error: "Unauthorized" }, 401);
  }

  try {
    const files = await listFiles(c.env.FILES, undefined, 100);

    return c.json({
      files,
      count: files.length,
    });
  } catch (error) {
    return c.json({ error: (error as Error).message }, 500);
  }
});

app.post("/api/files/upload", async (c) => {
  const auth = c.get("auth");

  // Check authentication
  const session = await auth.api.getSession({ headers: c.req.raw.headers });
  if (!session?.session) {
    return c.json({ error: "Unauthorized" }, 401);
  }

  try {
    const formData = await c.req.formData();
    const file = formData.get("file") as File;

    if (!file) {
      return c.json({ error: "No file provided" }, 400);
    }

    const key = `uploads/${session.user.id}/${Date.now()}-${file.name}`;
    const arrayBuffer = await file.arrayBuffer();

    await uploadFile(c.env.FILES, key, arrayBuffer, {
      contentType: file.type,
      customMetadata: {
        uploadedBy: session.user.id,
        uploadedAt: new Date().toISOString(),
      },
    });

    return c.json({
      success: true,
      key,
      size: file.size,
      type: file.type,
    });
  } catch (error) {
    return c.json({ error: (error as Error).message }, 500);
  }
});

app.get("/api/files/:key", async (c) => {
  const auth = c.get("auth");

  // Check authentication
  const session = await auth.api.getSession({ headers: c.req.raw.headers });
  if (!session?.session) {
    return c.json({ error: "Unauthorized" }, 401);
  }

  try {
    const key = c.req.param("key");
    const metadata = await getFileMetadata(c.env.FILES, key);

    if (!metadata) {
      return c.json({ error: "File not found" }, 404);
    }

    const stream = await downloadFile(c.env.FILES, key);

    if (!stream) {
      return c.json({ error: "File not found" }, 404);
    }

    return new Response(stream, {
      headers: {
        "Content-Type": metadata.contentType || "application/octet-stream",
        "Content-Length": metadata.size.toString(),
      },
    });
  } catch (error) {
    return c.json({ error: (error as Error).message }, 500);
  }
});

// Health check endpoint
app.get("/health", (c) => {
  return c.json({
    status: "ok",
    timestamp: new Date().toISOString(),
    services: {
      d1: "✓",
      kv: "✓",
      r2: "✓",
      ai: "✓",
    },
  });
});

export default app;
