# Pipecat

## Overview
Pipecat is an open-source framework for building real-time voice and video AI agents. Created by the Pipecat team and distributed as `pipecat-ai/pipecat:latest`, it provides WebSocket and WebRTC-based voice pipelines with Daily.co transport, Twilio telephony integration, and OpenAI-compatible LLM backends. The stack runs on port 8765 with 8GB memory and 4 CPU cores.

## Why This Matters for Kings' College Galway
Pipecat powers the voice-based Irish language learning interface for the Celtic education platform. Students practicing Gaeilge pronunciation for the Leaving Cert oral exam speak into a browser-based voice interface; Pipecat processes the audio stream through Whisper for transcription, routes the text through LiteLLM for LLM-based pronunciation feedback, and streams TTS responses back — all in real-time with sub-second latency. The integration with Twilio extends this to phone-based Irish language practice sessions. The shared HuggingFace cache provides access to Irish-optimized speech models, making Pipecat the bridge between AI voice processing and Irish language pedagogy.

## Key Features
- Real-time voice AI pipelines with WebRTC and WebSocket transport
- Daily.co video/audio transport integration
- Twilio telephony for phone-based voice agents
- OpenAI-compatible LLM backend for RAG-enhanced voice responses
- 8GB / 4 CPU allocation for real-time streaming performance

## Deployment

### Docker Compose (Local Development)
```bash
cd infrastructure/stacks/engineering/pipecat
docker compose up -d
```

### Docker Compose (Production with Locket Secret Injection)
```bash
cd infrastructure/stacks/engineering/pipecat
docker compose -f compose.yaml -f sidecar.yaml -f pangolin.yaml up -d
```

### Komodo (GitOps)
This stack is deployed via Komodo on the MacBook M4 workload host (bunchloch). Komodo syncs from the Forgejo repository and applies `compose.yaml` + `sidecar.yaml`. No `.env` file is needed — Locket resolves all secrets from the Infisical `dev-baile` vault at runtime.

## Environment Variables
| Variable | Required | Description | Default |
|:--|:--|:--|:--|
| `PIPECAT_PORT` | No | Listen port | `8765` |
| `PIPECAT_TRANSPORT` | No | Transport protocol | `daily` |
| `DAILY_API_KEY` | Yes | Daily.co API key | — |
| `TWILIO_ACCOUNT_SID` | No | Twilio account SID | — |
| `TWILIO_AUTH_TOKEN` | No | Twilio auth token | — |
| `OPENAI_API_KEY` | No | OpenAI API key for LLM backend | — |
| `HF_HOME` | No | HuggingFace home | `/stedding/huggingface` |
| `HF_HUB_CACHE` | No | HuggingFace hub cache | `/stedding/huggingface/hub` |

## Access
- **URL**: `https://pipecat.cianfhoghlaim.ie` (private, Pangolin Member role required)
- **Internal port**: 8765
- **Auth**: API keys for Daily.co and Twilio

## Health Check
```bash
docker ps --filter name=pipecat --format "table {{.Names}}\t{{.Status}}"
```

## Upstream
- **Repository**: https://github.com/pipecat-ai/pipecat
- **Documentation**: https://docs.pipecat.ai
- **Latest release**: Pulls `pipecat-ai/pipecat:latest` — real-time voice AI agent framework.
