import { Hono } from "hono";

const app = new Hono();

app.get("/api/health", (c) => {
  return c.json({ status: "ok", service: "croilar-hono-api", version: "0.1.0" });
});

app.get("/.well-known/openid-configuration", (c) => {
  const issuer = process.env.PUBLIC_AUTH_URL || "https://auth.croilar.cianfhoghlaim.ie";
  return c.json({
    issuer,
    authorization_endpoint: `${issuer}/api/auth/authorize`,
    token_endpoint: `${issuer}/api/auth/token`,
    jwks_uri: `${issuer}/api/auth/jwks`,
    userinfo_endpoint: `${issuer}/api/auth/userinfo`,
    scopes_supported: ["openid", "profile", "email"],
    response_types_supported: ["code"],
    grant_types_supported: ["authorization_code", "refresh_token"],
    subject_types_supported: ["public"],
    id_token_signing_alg_values_supported: ["RS256"],
  });
});

// BetterAuth routes will be mounted at /api/auth/* in PR-2b
// app.route("/api/auth", authHandler);

export default app;
