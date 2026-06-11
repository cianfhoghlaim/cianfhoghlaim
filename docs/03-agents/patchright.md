---
title: 'Patchright — Stealth Browser Automation'
domain: 'agents'
status: 'stable'
description: 'Patchright is a stealth browser automation library based on Playwright, designed to evade bot detection. It patches Playwright''''s default fingerprints (WebDriver flags, user agent strings, JavaScript navigator properties) to make automated browsers indistinguishable from real user'
read_when:
  - looking for documentation on this topic
updated: '2026-06-10'
supersedes:
  - docs/patchright.md
ccc_query_hints:
  - patchright — stealth browser automation
---

# Patchright — Stealth Browser Automation

## Overview

Patchright is a stealth browser automation library based on Playwright, designed to evade bot detection. It patches Playwright's default fingerprints (WebDriver flags, user agent strings, JavaScript navigator properties) to make automated browsers indistinguishable from real user browsers. Maintained as an open-source alternative to commercial anti-detection solutions.

## Why This Matters for Kings' College Galway

Government education websites increasingly deploy anti-bot measures that detect and block Playwright/Puppeteer-based scrapers by checking `navigator.webdriver`, `window.chrome` objects, and Canvas fingerprinting. Patchright modifies these detection surfaces so the browser appears as a normal Chrome/Safari/Firefox installation. For SEC exam paper downloads and NCCA syllabus access — where CAPTCHA or IP blocking would interrupt the curriculum pipeline — Patchright ensures the scraper is not identified as a bot before it even reaches the content.

## Key Features

- **WebDriver evasion** — Hides `navigator.webdriver === true`
- **Fingerprint patching** — Modifies Canvas, WebGL, and audio fingerprints
- **User agent consistency** — Ensures UA matches the browser's JS environment
- **Playwright-compatible** — Drop-in replacement for Playwright APIs
- **Open-source** — No commercial license required

## Installation

```bash
uv add patchright
```

## Integration with Our Stack

Patchright is the "stealth" layer in the browser automation stack. It wraps Playwright-based DLT scrapers for government education websites. Used alongside Stagehand (for AI-driven interaction) and Crawl4AI (for high-throughput crawling) as the anti-detection backbone.

## Upstream

- **Repository**: <https://github.com/patchright/patchright>
- **Latest**: Active development — Playwright version tracking, new fingerprint patches, anti-detection improvements

## Screenshot

Patchright is a programmatic library. Usage is identical to Playwright: `browser = patchright.chromium.launch()`. The effectiveness is measured by whether scrapers succeed on previously-blocked websites. DLT pipeline logs show Patchright-enabled runs as "stealth mode" with the modified fingerprint configuration.
