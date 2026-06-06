# Crawl4AI — AI-Powered Web Crawling SDK

## Overview

Crawl4AI is an open-source Python library for AI-powered web crawling and data extraction. It combines traditional web crawling with LLM-based content understanding — crawling websites, extracting clean markdown, and structuring data using AI prompts. Designed for high-throughput crawling with built-in caching, rate limiting, and JavaScript rendering support.

## Why This Matters for Kings' College Galway

Curriculum content is scattered across dozens of websites: NCCA curriculum pages, SEC exam archives, Department of Education circulars, EUR-Lex education directives, and academic repositories. Crawl4AI provides the "Gatherer" role in the browser automation stack — it crawls these sites systematically, extracts clean markdown content, and feeds it into the BAML extraction pipeline. Its LLM-powered extraction means it can identify and structure curriculum-relevant pages from noisy education websites without per-site CSS selector configuration.

## Key Features

- **LLM extraction** — Structure crawled content using AI prompts
- **JavaScript rendering** — Handles SPAs and dynamic content
- **Caching** — Built-in request caching for efficient recrawls
- **Rate limiting** — Configurable delays and concurrency
- **Markdown output** — Clean, LLM-optimised content extraction

## Installation

```bash
uv add crawl4ai
```

## Integration with Our Stack

Crawl4AI is the "Gatherer" in the browser automation stack (Stagehand → Crawl4AI → Skyvern). It handles high-throughput curriculum website crawling. The Docker stack at `infrastructure/stacks/engineering/crawl4ai/` provides the API service. DLT sources integrate with Crawl4AI for web-based curriculum ingestion.

## Upstream

- **Repository**: <https://github.com/unclecode/crawl4ai>
- **Documentation**: <https://crawl4ai.com>
- **Latest**: Active development — LLM extraction v2, improved JS rendering, caching improvements

## Screenshot

Crawl4AI provides a Python API and a Docker service. The `crawl4ai.com` docs site shows code examples with the async crawling API. The Docker service at port 11235 exposes a REST API for crawl jobs. Crawl results appear as structured JSON with markdown content, metadata, and extraction results.
