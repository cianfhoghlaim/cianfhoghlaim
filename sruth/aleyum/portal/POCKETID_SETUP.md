# PocketID Authentication Setup for Aleyum Portal

This guide walks you through setting up PocketID as the OIDC authentication provider for the Aleyum Portal.

## Overview

PocketID is a passkey-first OpenID Connect (OIDC) provider deployed as part of the Pangolin stack. It provides secure, passwordless authentication using WebAuthn/passkeys.

### Architecture

```
┌─────────────────┐     OIDC       ┌──────────────────┐
│  Aleyum Portal  │<──────────────>│     PocketID     │
│  (better-auth)  │                 │   (Passkeys)     │
└─────────────────┘                 └──────────────────┘
        │                                     │
        │                                     │
        v                                     v
┌─────────────────┐                 ┌──────────────────┐
│   PostgreSQL    │                 │   PostgreSQL     │
│ (Session Store) │                 │  (PocketID DB)   │
└─────────────────┘                 └──────────────────┘
```

## Prerequisites

1. **PocketID Server Running**: Ensure PocketID is deployed in the Pangolin stack
   ```bash
   cd bonneagar/pangolin
   docker compose ps pocket-id
   ```

2. **PocketID Admin Access**: Access to https://auth.cianfhoghlaim.ie/admin

3. **Portal Domain**: Aleyum portal accessible at https://aleyum.cianfhoghlaim.ie

## Step 1: Register OIDC Application in PocketID

1. **Access PocketID Admin**
   - Navigate to: https://auth.cianfhoghlaim.ie/admin
   - Sign in with your passkey

2. **Create New OIDC Application**
   - Go to: **Settings** → **OIDC Applications**
   - Click: **Create Application**

3. **Configure Application Settings**

   | Field | Value | Notes |
   |-------|-------|-------|
   | Application Name | Aleyum Portal | Display name for users |
   | Redirect URI | `https://aleyum.cianfhoghlaim.ie/api/auth/callback/oidc` | Must match exactly |
   | Post Logout Redirect URI | `https://aleyum.cianfhoghlaim.ie/login` | Optional but recommended |
   | Scopes | `openid email profile groups` | Required for user info |

4. **Save Credentials**
   After creating the application, you'll receive:
   - **Client ID**: Copy this (e.g., `pocketid_client_xxxxx`)
   - **Client Secret**: Copy this (e.g., `pocketid_secret_xxxxx`)

   **⚠️ IMPORTANT**: Store these securely. You'll need them for environment configuration.

## Step 2: Configure Environment Variables

Create a `.env` file in the portal directory with the following variables:

```bash
# =============================================================================
# PocketID OIDC Configuration
# =============================================================================
POCKETID_CLIENT_ID=pocketid_client_xxxxx
POCKETID_CLIENT_SECRET=pocketid_secret_xxxxx
POCKETID_ISSUER=https://auth.cianfhoghlaim.ie

# =============================================================================
# Better Auth Configuration
# =============================================================================
# Generate with: openssl rand -base64 32
BETTER_AUTH_SECRET=your-better-auth-secret-min-32-chars

# =============================================================================
# Application URLs
# =============================================================================
AUTH_BASE_URL=https://aleyum.cianfhoghlaim.ie

# =============================================================================
# Database (for session storage)
# =============================================================================
DATABASE_URL=postgresql://postgres:your-password@postgres:5432/aleyum_portal
```

### Required Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `POCKETID_CLIENT_ID` | ✅ | Client ID from PocketID admin |
| `POCKETID_CLIENT_SECRET` | ✅ | Client secret from PocketID admin |
| `POCKETID_ISSUER` | ✅ | OIDC issuer URL (default: `https://auth.cianfhoghlaim.ie`) |
| `BETTER_AUTH_SECRET` | ✅ | Secret for session signing (min 32 chars) |
| `AUTH_BASE_URL` | ✅ | Public URL of the portal |
| `DATABASE_URL` | ✅ | PostgreSQL connection string for sessions |

## Step 3: Database Setup

The portal uses PostgreSQL for session storage via better-auth.

### Using Docker Compose (Production)

The `compose.yaml` includes a PostgreSQL service:

```bash
# Start the portal with database
docker compose up -d

# Run database migrations (if applicable)
docker compose exec aleyum-portal npm run db:push
```

### Local Development

```bash
# Start PostgreSQL locally
docker run -d \
  --name aleyum-postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=devpassword \
  -e POSTGRES_DB=aleyum_portal \
  -p 5432:5432 \
  postgres:16-alpine

# Set DATABASE_URL in .env
DATABASE_URL=postgresql://postgres:devpassword@localhost:5432/aleyum_portal
```

## Step 4: Configure Network Access

Ensure the portal can reach PocketID over the network.

### Docker Network Configuration

If both PocketID and the portal are running in Docker:

1. **Check Networks**
   ```bash
   docker network ls | grep pangolin
   docker network ls | grep tools
   ```

2. **Connect to Shared Network** (if needed)
   ```bash
   docker network connect pangolin aleyum-portal
   ```

3. **DNS Resolution**
   - Ensure `auth.cianfhoghlaim.ie` resolves correctly
   - For local development, add to `/etc/hosts`:
     ```
     127.0.0.1 auth.cianfhoghlaim.ie aleyum.cianfhoghlaim.ie
     ```

## Step 5: Test Authentication Flow

### 1. Start the Portal

```bash
# Development
npm run dev

# Production (Docker)
docker compose up -d
```

### 2. Access Login Page

Navigate to: https://aleyum.cianfhoghlaim.ie/login

You should see:
- **"Sign in with PocketID"** button
- **Email/password fallback** option

### 3. Test OIDC Login

1. Click "Sign in with PocketID"
2. You should be redirected to PocketID: `https://auth.cianfhoghlaim.ie/authorize`
3. Sign in with your passkey
4. You should be redirected back to the portal
5. You should be logged in and see the dashboard

### 4. Check Session

Once logged in, verify the session:

```javascript
// In browser console
localStorage.getItem('better-auth.session_token')
// Should show a valid session token
```

## Troubleshooting

### Issue: "redirect_uri_mismatch" Error

**Cause**: Redirect URI in PocketID doesn't match the request.

**Solution**:
1. Check the exact URL in the error message
2. Update PocketID OIDC application with exact redirect URI:
   ```
   https://aleyum.cianfhoghlaim.ie/api/auth/callback/oidc
   ```
3. Include trailing slashes and protocol exactly

### Issue: "client_id_invalid" or "client_secret_invalid"

**Cause**: Incorrect credentials in environment variables.

**Solution**:
1. Re-check PocketID admin panel for exact Client ID and Secret
2. Verify `.env` file has correct values (no extra spaces)
3. Restart the portal after updating `.env`:
   ```bash
   docker compose restart aleyum-portal
   ```

### Issue: PocketID Not Reachable

**Cause**: Network connectivity or DNS issues.

**Solution**:
1. Test from portal container:
   ```bash
   docker exec -it aleyum-portal wget -O- https://auth.cianfhoghlaim.ie/healthz
   ```
2. Check if both services are on the same network
3. Verify DNS resolution:
   ```bash
   docker exec -it aleyum-portal nslookup auth.cianfhoghlaim.ie
   ```

### Issue: Session Not Persisting

**Cause**: Database connection issue or missing BETTER_AUTH_SECRET.

**Solution**:
1. Verify PostgreSQL is running:
   ```bash
   docker compose ps aleyum-db
   ```
2. Test database connection:
   ```bash
   docker exec -it aleyum-portal psql $DATABASE_URL -c "SELECT 1"
   ```
3. Ensure `BETTER_AUTH_SECRET` is set (min 32 characters)

### Issue: CORS Errors

**Cause**: PocketID CORS configuration blocking requests.

**Solution**:
1. Check PocketID admin settings
2. Add portal origin to allowed origins:
   ```
   https://aleyum.cianfhoghlaim.ie
   ```

### Issue: "invalid_scope" Error

**Cause**: Requested scopes not enabled in PocketID.

**Solution**:
1. Verify PocketID OIDC application has these scopes:
   - `openid` (required)
   - `email` (recommended)
   - `profile` (recommended)
   - `groups` (optional, for role-based access)

2. Check `lib/auth.ts` has matching scope configuration:
   ```typescript
   scope: "openid email profile groups"
   ```

## Security Best Practices

### 1. Secret Management

**Never commit secrets to git.** Use environment-specific secrets:

```bash
# Generate secrets
openssl rand -base64 32 > secrets/better-auth-secret
openssl rand -base64 32 > secrets/pocketid-client-secret

# Load in compose.yaml
BETTER_AUTH_SECRET_FILE=/run/secrets/better-auth-secret
POCKETID_CLIENT_SECRET_FILE=/run/secrets/pocketid-client-secret
```

### 2. HTTPS Only

- Always use HTTPS in production
- PocketID requires HTTPS for passkey support
- Set secure cookie flags:
  ```typescript
  // In lib/auth.ts
  advanced: {
    cookiePrefix: "cianfhoghlaim",
    crossSubDomainCookies: {
      enabled: false,
    },
  }
  ```

### 3. Redirect URI Validation

- Use exact, hardcoded redirect URIs
- Avoid wildcards in production
- Validate against allowed origins

### 4. Token Storage

- Session tokens stored in httpOnly cookies
- No localStorage for sensitive tokens
- Implement token rotation for long-lived sessions

### 5. Logout Flow

Implement proper logout:

```typescript
// In signOut handler
await signOut({
  fetchOptions: {
    onSuccess: () => {
      // Redirect to PocketID logout
      window.location.href = "https://auth.cianfhoghlaim.ie/logout";
    }
  }
});
```

## Advanced Configuration

### Custom Claims

Add custom claims from PocketID:

```typescript
// lib/auth.ts
export const auth = betterAuth({
  // ... existing config
  socialProviders: {
    oidc({
      providerId: "pocketid",
      clientId: process.env.POCKETID_CLIENT_ID!,
      clientSecret: process.env.POCKETID_CLIENT_SECRET!,
      issuer: process.env.POCKETID_ISSUER!,
      redirectURI: `${process.env.AUTH_BASE_URL}/api/auth/callback/oidc`,
      scope: "openid email profile groups",
      // Map PocketID groups to user roles
      mapProfileToUser: (profile) => ({
        email: profile.email,
        name: profile.name,
        image: profile.picture,
        // Custom role mapping from PocketID groups
        role: profile.groups?.includes('admin') ? 'admin' : 'user',
      }),
    }),
  },
});
```

### Session Management

Configure session expiration:

```typescript
// lib/auth.ts
session: {
  expiresIn: 60 * 60 * 24 * 7, // 7 days
  updateAge: 60 * 60 * 24, // Update every 24 hours
  cookieCache: {
    enabled: true,
    maxAge: 5 * 60, // 5 minutes
  },
}
```

### Multi-Factor Authentication (MFA)

PocketID natively supports passkeys as a second factor. To enforce:

1. Enable in PocketID admin:
   - Settings → Security → Require passkey for all users

2. The portal automatically inherits this setting via OIDC

## Verification Checklist

Before going live, verify:

- [ ] PocketID is accessible at `https://auth.cianfhoghlaim.ie`
- [ ] OIDC application registered in PocketID admin
- [ ] Client ID and Secret configured in `.env`
- [ ] `BETTER_AUTH_SECRET` is set (32+ chars)
- [ ] PostgreSQL database is running and accessible
- [ ] Redirect URI matches exactly (no trailing slash differences)
- [ ] DNS resolves for both `auth.cianfhoghlaim.ie` and `aleyum.cianfhoghlaim.ie`
- [ ] HTTPS is enabled for both domains
- [ ] Login flow works end-to-end
- [ ] Session persists across page reloads
- [ ] Logout redirects to PocketID logout
- [ ] Session cookie is httpOnly and secure

## Related Documentation

- **PocketID Documentation**: https://pocketid.org/docs
- **better-auth Documentation**: https://better-auth.com
- **OIDC Specification**: https://openid.net/connect/
- **Pangolin Setup**: `/bonneagar/pangolin/README.md`
- **TinyAuth Integration**: `/bonneagar/pangolin/compose.yaml` (TinyAuth section)

## Support

For issues or questions:

1. Check PocketID logs: `docker compose -f bonneagar/pangolin/compose.yaml logs pocket-id`
2. Check portal logs: `docker compose logs aleyum-portal`
3. Verify network connectivity: `docker network inspect pangolin`
4. Review OIDC flows in PocketID admin under "Audit Logs"

## Appendix: Environment Variable Reference

### PocketID Configuration

```bash
# PocketID Server Location
POCKETID_ISSUER=https://auth.cianfhoghlaim.ie

# OIDC Client Credentials
POCKETID_CLIENT_ID=pocketid_client_xxxxx
POCKETID_CLIENT_SECRET=pocketid_secret_xxxxx

# OIDC Endpoints (auto-discovered from issuer)
# Authorization: https://auth.cianfhoghlaim.ie/authorize
# Token: https://auth.cianfhoghlaim.ie/api/oidc/token
# UserInfo: https://auth.cianfhoghlaim.ie/api/oidc/userinfo
```

### Portal Configuration

```bash
# Portal Base URL
AUTH_BASE_URL=https://aleyum.cianfhoghlaim.ie

# Better Auth Secret (min 32 chars)
BETTER_AUTH_SECRET=$(openssl rand -base64 32)

# Database URL
DATABASE_URL=postgresql://postgres:password@postgres:5432/aleyum_portal
```

### Debug Mode

```bash
# Enable better-auth debug logging
BETTER_AUTH_DEBUG=true

# Enable OIDC debug logging
OIDC_DEBUG=true
```
