---
title: "Web Reader MCP Server"
source: "https://docs.z.ai/devpack/mcp/reader-mcp-server"
author:
  - "[[Overview - Z.AI DEVELOPER DOCUMENT]]"
published:
created: 2025-12-28
description:
tags:
  - "clippings"
---
The Web Reader MCP Server is a Z.AI implementation based on the Model Context Protocol (MCP). It provides Claude Code, Cline, and other MCP-compatible clients with powerful web content extraction capabilities, including full-page content retrieval and structured data extraction.

## Overview

This remote MCP server with web content reading capability is available to users on **GLM Coding Plan**, enabling your code agent to fetch detailed page content and structured data.

## Features

## Web Content Reading

Fetch the complete content of any webpage, including text, and links

## Structured Data

Extract structured data such as title, main body, and metadata

## Remote Service

HTTP-based remote MCP service, no local installation required

## Tools

This server implements the Model Context Protocol and works with any MCP-compatible client. Currently, it provides the following tool:
- **`webReader`** — Fetch webpage content for a specified URL. Returns the page title, main content, metadata, list of links, and more.

## Example Scenarios

Parse project websites or repository pages (such as README, release notes, and usage guides) to extract core information and link lists, assisting evaluation and integration.

Extract steps, commands, and caveats from blogs, tutorials, and guide pages, organizing unstructured content into actionable developer notes and task lists.

For issue remediation, read the publicly available steps on the specified web page and use them as references to resolve the problem.

Convert content from designated web pages into structured data and leverage in-page links for incremental synchronization to build a team technical knowledge base.

## Installation and Usage

### Quick Start

### Supported Clients

- Claude Code
- Cline (VS Code)
- OpenCode
- Crush
- Goose
- Roo Code, Kilo Code, Others

**One-click install command** Replace `your_api_key` with the API key you obtained in the previous step **Manual configuration** Edit the Claude Code configuration file under your home directory, the MCP section of `.claude.json`:

## Troubleshooting

Connection timeout

**Issue:** Connection to the MCP server timed out **Solutions:**
1. Check your network connection
2. Verify firewall settings
3. Ensure the server URL is correct
4. Increase client timeout settings

**Issue:** Web content reading returned empty result or error **Solutions:**
1. Confirm the target URL is accessible
2. Check if the page has anti-scraping mechanisms
3. Try different URLs
4. Ensure network connectivity is normal
5. Contact technical support for assistance

## Quota

The MCP quotas for the Lite, Pro and Max plans are as follows:
- **Lite:** Include a total of 100 web searches and web readers, along with the 5-hour maximum prompt resource pool of the package for vision understanding.
- **Pro:** Include a total of 1,000 web searches and web readers, along with the 5-hour maximum prompt resource pool of the package for vision understanding.
- **Max:** Include a total of 4,000 web searches and web readers, along with the 5-hour maximum prompt resource pool of the package for vision understanding.

## Resources

- [Model Context Protocol (MCP) Documentation](https://modelcontextprotocol.io/)
- [Claude Code MCP Configuration Guide](https://docs.anthropic.com/en/docs/claude-code/mcp)
- [Z.AI API Reference](https://docs.z.ai/api-reference/introduction)
- [GLM Coding Plan Overview](https://docs.z.ai/devpack/overview)

[Web Search MCP Server](https://docs.z.ai/devpack/mcp/search-mcp-server) [Zread MCP Server](https://docs.z.ai/devpack/mcp/zread-mcp-server)