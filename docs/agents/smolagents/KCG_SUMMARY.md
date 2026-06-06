# Smolagents — KCG Summary

## What It Is
A **multi-agent deep research system** built on HuggingFace's `smolagents` framework with Firecrawl MCP tools for web retrieval. The workflow follows a plan → split → coordinate → research → synthesize pattern: a planner generates a research strategy, a task splitter decomposes it into subtasks, a coordinator spawns specialized sub-agents, and the coordinator synthesizes all findings into a consolidated markdown report. All LLM calls use Hugging Face Inference Providers with open models.

## Why This Matters for Kings' College Galway
The plan-and-orchestrate pattern directly maps to the kind of multi-source curriculum research needed for the oideachais platform — generating a comprehensive Leaving Cert study guide by splitting research across subjects (Irish, English, Maths, etc.) and having specialized sub-agents investigate each topic independently before synthesis. The Firecrawl MCP integration demonstrates how to wire web search/retrieval into agent tool-calling, which is the exact pattern needed for the examinations.ie and curriculum.ie scraping pipelines. Using Hugging Face's open-model inference aligns with the project's commitment to open-source AI models for Irish language education.

## Key Patterns Preserved
- `firecrawl-deepresearch/README.md` — Complete multi-agent deep research workflow: planner, task splitter, coordinator, sub-agents, synthesis, models and providers, how to run
- `firecrawl-deepresearch/docs/blog-post.md` — Written tutorial (from alejandro-ao.com) explaining the multi-agent architecture in depth

## Source Files
Full source removed (2026-06-06), available at:
- Tutorial: https://alejandro-ao.com/posts/agents/multi-agent-deep-research/
- Smolagents: https://github.com/huggingface/smolagents

## What Was Removed
Python source (`.py` — planner, task_splitter, coordinator), license files, `.gitignore`, images (`.png`), and all non-markdown assets.
