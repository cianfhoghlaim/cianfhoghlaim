# Stagehand Local Server

HTTP server providing Stagehand browser automation with local-first execution and automatic Browserbase fallback.

## Features

- **Local browser first** - CDP/Playwright for $0 cost
- **Automatic cloud fallback** - Browserbase when anti-bot detected
- **Multi-LLM support** - GLM-4.6, GLM-4.6v, Gemini 3 Flash
- **Session management** - LRU cache with TTL expiration
- **Anti-bot detection** - Cloudflare, reCAPTCHA, Turnstile

## Quick Start

```bash
# Install dependencies
npm install

# Copy environment template
cp .env.example .env
# Edit .env with your API keys

# Run in development mode
npm run dev

# Or build and run production
npm run build
npm start
```

## API Endpoints

### Session Management

```bash
# Create session (local)
curl -X POST http://localhost:3100/session/create \
  -H "Content-Type: application/json" \
  -d '{"modelName": "glm-4.6"}'

# Create session (cloud)
curl -X POST http://localhost:3100/session/create \
  -H "Content-Type: application/json" \
  -d '{"useCloud": true}'

# Close session
curl -X POST http://localhost:3100/session/{sessionId}/close

# Upgrade to cloud (fallback)
curl -X POST http://localhost:3100/session/{sessionId}/upgrade-to-cloud
```

### Browser Operations

```bash
# Navigate
curl -X POST http://localhost:3100/navigate \
  -H "Content-Type: application/json" \
  -d '{"sessionId": "...", "url": "https://example.com"}'

# Observe (find elements)
curl -X POST http://localhost:3100/observe \
  -H "Content-Type: application/json" \
  -d '{"sessionId": "...", "instruction": "find the login button"}'

# Act (perform action)
curl -X POST http://localhost:3100/act \
  -H "Content-Type: application/json" \
  -d '{"sessionId": "...", "action": "click the login button"}'

# Extract (structured data)
curl -X POST http://localhost:3100/extract \
  -H "Content-Type: application/json" \
  -d '{"sessionId": "...", "instruction": "extract all product names and prices"}'

# Screenshot
curl -X POST http://localhost:3100/screenshot \
  -H "Content-Type: application/json" \
  -d '{"sessionId": "...", "fullPage": true}'

# Agent (autonomous multi-step)
curl -X POST http://localhost:3100/agent \
  -H "Content-Type: application/json" \
  -d '{"sessionId": "...", "instruction": "Find the cheapest flight from JFK to LAX", "maxSteps": 20}'
```

## Anti-Bot Detection

The server automatically detects:
- Cloudflare challenges (`cf_chl_` cookies, `#cf-wrapper`)
- reCAPTCHA (`grecaptcha`, `.g-recaptcha`)
- Turnstile (`.cf-turnstile`)
- hCaptcha (`.h-captcha`)
- Generic verification prompts

When detected, responses include `shouldFallback: true`. Clients should:
1. Call `/session/{id}/upgrade-to-cloud`
2. Retry the failed operation

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | 3100 | Server port |
| `HEADLESS` | true | Run browser headless |
| `MAX_SESSIONS` | 10 | Maximum concurrent sessions |
| `SESSION_TTL_MS` | 300000 | Session timeout (5 min) |
| `DEFAULT_MODEL` | glm-4.6 | Default LLM model |
| `VISION_MODEL` | glm-4.6v | Model for vision tasks |
| `AGENT_MODEL` | google/gemini-3-flash-preview | Model for agent mode |
| `ZAI_API_KEY` | - | Z.AI API key for GLM models |
| `GOOGLE_API_KEY` | - | Google API key for Gemini |
| `OPENAI_API_KEY` | - | OpenAI API key (fallback) |
| `BROWSERBASE_API_KEY` | - | Browserbase API key |
| `BROWSERBASE_PROJECT_ID` | - | Browserbase project ID |

## Docker

```bash
# Build
docker build -t stagehand-server .

# Run
docker run -p 3100:3100 \
  -e ZAI_API_KEY=... \
  -e GOOGLE_API_KEY=... \
  -e BROWSERBASE_API_KEY=... \
  --cap-add=SYS_ADMIN \
  stagehand-server
```

## Integration with Python Backend

The Python `StagehandLocalBackend` communicates with this server via HTTP:

```python
from sruth.shared.browser.backends.selfhosted.stagehand_backend import StagehandLocalBackend

backend = StagehandLocalBackend()
await backend.initialize()

result = await backend.navigate("https://example.com")
if result.should_fallback:
    await backend.fallback_to_cloud()
```

## Models

| Model | Use Case | Provider |
|-------|----------|----------|
| `glm-4.6` | Navigation decisions, text | Z.AI |
| `glm-4.6v` | Screenshot analysis, UI | Z.AI |
| `google/gemini-3-flash-preview` | Agent mode, CUA | Google |
| `openai/gpt-4o` | Fallback | OpenAI |
