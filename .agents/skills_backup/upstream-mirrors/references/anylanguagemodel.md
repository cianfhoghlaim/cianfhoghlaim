# AnyLanguageModel — KCG Summary

## What It Is
AnyLanguageModel is a Swift package providing a drop-in replacement for Apple's Foundation Models framework with support for 9 language model backends: Apple Foundation Models, Core ML, MLX, llama.cpp (GGUF), Ollama, Anthropic, OpenAI (Chat Completions + Responses API), and Google Gemini. It uses Swift 6.1 package traits to conditionally include heavy dependencies, keeping binary sizes small.

## Why This Matters for Kings' College Galway
The `sruth/tuatha/` educational MMO targets iOS/macOS via the `sruth/tuatha/ui` React Native frontend. AnyLanguageModel's unified API surface is the reference pattern for our LLM provider abstraction layer — the same tool-calling API that works across Anthropic, OpenAI, and Gemini informs how we route AI tutor/NPC requests through the LiteLLM gateway. The MLX support is directly relevant to on-device Irish language model inference for offline learning scenarios. The BYOK (Bring Your Own Key) proxy server pattern also mirrors our x402-based micropayment architecture for AI tutoring sessions.

## Key Patterns Preserved
- **README.md** — Full documentation: providers, setup, usage, testing, security guidance

## Source Files
Full source code removed (2026-06-06). The 54 deleted files include Swift source (`*.swift`, `Package.swift`, `Package.resolved`), CI workflow (`.github/workflows/ci.yml`), `.gitignore`, and the `LICENSE` file. Available at <https://github.com/mattt/AnyLanguageModel>.

## What Was Removed
- Swift source: `*.swift`, `Package.swift`, `Package.resolved`
- CI: `.github/workflows/ci.yml`
- Repo config: `.gitignore`
- License file (MIT — see upstream for full text)
