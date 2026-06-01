# Browserbase MCP + Google Vertex AI Patch Notes

To get the Browserbase MCP server to route its AI requests through Google Cloud Vertex AI (instead of Browserbase's proprietary AI API or standard Google AI Studio), two manual patches were applied to the cached NPM package.

This was necessary because the `@browserbasehq/mcp` package does not currently expose the underlying `disableAPI` flag in its CLI, nor does it pass MCP environment variables down to the AI SDK reliably.

## 1. Environment Variable Injection Patch
The MCP entry script was patched to forcefully set the Google Vertex environment variables before the AI SDK loads.

**File Patched:**
`~/.npm/_npx/b11ce842e30bd76e/node_modules/@browserbasehq/mcp/cli.js`

**Changes Made:**
Injected the following lines at the top of the file:
```javascript
process.env.GOOGLE_VERTEX_LOCATION = "global";
process.env.GOOGLE_VERTEX_PROJECT = "588312781610";
```

**How to update/undo:**
If you change your Google Cloud Project ID or Location, you must edit this file to update the hardcoded values. To undo the patch entirely, delete those two lines.

## 2. Stagehand Constructor Patch
The MCP session manager was patched to forcefully set the `disableAPI: true` flag in the Stagehand constructor. Without this flag, Stagehand assumes you are using Browserbase's proprietary backend API, which rejects the `vertex/` provider prefix.

**File Patched:**
`~/.npm/_npx/b11ce842e30bd76e/node_modules/@browserbasehq/mcp/dist/sessionManager.js`

**Changes Made:**
In the `new Stagehand({ ... })` constructor payload (around line 20), injected `disableAPI: true,`:
```javascript
        experimental: config.experimental ?? false,
        disableAPI: true, // <-- INJECTED LINE
        browserbaseSessionCreateParams: {
```

**How to update/undo:**
To revert this, open the file and remove the `disableAPI: true,` line.

## 3. Configuration Update
The `opencode.json` file in your project root was updated to pass the necessary arguments to the MCP server.

**File Updated:**
`/Users/cianmacandeisigh/dev/kings_college_galway/opencode.json`

**Changes Made:**
Updated the `args` array for the `browserbase` MCP server to explicitly include `--experimental` and a dummy `--modelApiKey` (required by the CLI validation logic, even though Vertex AI handles auth natively):
```json
"args": [
  "npx",
  "-y",
  "@browserbasehq/mcp",
  "--modelName", "vertex/gemini-2.5-flash",
  "--experimental",
  "--modelApiKey", "dummy"
]
```

---

*Note: Because these patches were made to a cached `npx` execution folder (`b11ce842e30bd76e`), they will be lost if you clear your npm cache or if the MCP server updates to a new version and creates a new npx cache folder. If that happens, you will need to re-apply the patches to the new cache folder.*
