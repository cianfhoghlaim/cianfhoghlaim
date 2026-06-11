---
title: 'Stagehand — AI Browser Operator (Python SDK)'
domain: 'agents'
status: 'stable'
description: 'Stagehand is an open-source AI-powered browser automation framework by Browserbase. It uses natural language instructions to control a web browser — navigating pages, clicking elements, filling forms, and extracting data — powered by LLM reasoning and computer vision. The Python'
read_when:
  - looking for documentation on this topic
updated: '2026-06-10'
supersedes:
  - docs/stagehand.md
ccc_query_hints:
  - stagehand — ai browser operator (python 
---

# Stagehand — AI Browser Operator (Python SDK)

## Overview

Stagehand is an open-source AI-powered browser automation framework by Browserbase. It uses natural language instructions to control a web browser — navigating pages, clicking elements, filling forms, and extracting data — powered by LLM reasoning and computer vision. The Python SDK provides `@browserbasehq/stagehand` for building AI-driven web agents.

## Why This Matters for Kings' College Galway

The curriculum ingestion pipeline's most fragile step is scraping Irish government education websites. The SEC (State Examinations Commission), NCCA (National Council for Curriculum and Assessment), and Department of Education websites have inconsistent structures, JavaScript-rendered content, and CAPTCHA protections. Stagehand replaces brittle CSS-selector-based scrapers with AI-driven navigation — it "sees" the page like a human, finds the "Download Exam Paper" button by visual understanding, and handles multi-step login/download flows that traditional scrapers fail on.

## Key Features

- **Natural language control** — `page.act("click the download button for 2024 exam papers")`
- **Computer vision** — Understands page layout visually, not via selectors
- **Self-healing** — Adapts to website changes without code updates
- **Structured extraction** — `page.extract("list all exam papers with years and subjects")`
- **Browserbase integration** — Cloud browsers with residential proxies and CAPTCHA solving

## Installation

```bash
uv add stagehand-py
```

## Integration with Our Stack

Stagehand is the "Operator" in the browser automation stack (Stagehand → Crawl4AI → Skyvern). It handles complex interactive scraping for curriculum sources. DLT sources use Stagehand for authenticated and JavaScript-heavy government websites. Browserbase provides the cloud browser infrastructure.

## Upstream

- **Repository**: <https://github.com/browserbase/stagehand>
- **Documentation**: <https://docs.stagehand.dev>
- **Latest**: Active development — natural language `act`/`extract`/`observe` methods, improved vision models, Browserbase integration

## Screenshot

Stagehand is a programmatic SDK. The `stagehand.dev` docs show code examples with the `act()`, `extract()`, and `observe()` APIs. The Browserbase session replay shows the browser in action as Stagehand navigates and interacts. DLT pipeline logs show Stagehand extraction results as structured JSON output.
