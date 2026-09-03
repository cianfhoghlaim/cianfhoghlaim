---
title: "Web Search MCP Server"
source: "https://docs.z.ai/devpack/mcp/search-mcp-server"
author:
  - "[[Overview - Z.AI DEVELOPER DOCUMENT]]"
published:
created: 2025-12-28
description:
tags:
  - "clippings"
---
Web Search MCP Server is a Z.AI search capability implementation based on the Model Context Protocol (MCP), providing powerful Z.AI search capabilities for MCP-compatible clients such as Claude Code and Cline, including web search, real-time information retrieval, and other features.

## Product Overview

This Remote MCP Server with search capabilities is an exclusive server developed by Z.AI for **GLM Coding Plan users**, empowering your Code Agent with search capabilities and unlimited access to real-time information and web resources.

## Features

## Web Search

Supports comprehensive web search to retrieve the latest web information and resources

## Real-time Information

Retrieves real-time updated information including news, stock prices, weather, and more

## Remote Service

HTTP protocol-based remote MCP service, no local installation required

## Supported Tools

This server implements the Model Context Protocol and can be used with any MCP-compatible client. Currently provides the following tools:
- **`webSearchPrime`** - Search web information, returning results including page titles, URLs, summaries, site names, site icons, and more.

## Installation and Usage

### Quick Start

### Supported Clients

- Claude Code
- Cline (VS Code)
- OpenCode
- Crush
- Goose
- Roo Code, Kilo Code and Other MCP Clients

**One-click Installation Command** Be sure to replace `your_api_key` with the API Key you obtained.**Manual Configuration** Edit Claude Code’s configuration file `.claude.json` in the user directory, MCP section:

## Usage Example

Through the previous step of installing the Search MCP server to the client, you can directly use MCP in your Coding client.  
You can directly use search functionality in conversations:
- “Help me search for the latest AI technology developments”
- “Find best practices for Python asynchronous programming”

## Troubleshooting

Connection Timeout

**Issue:** MCP server connection timeout **Solutions:**
1. Check network connection
2. Confirm firewall settings
3. Verify the server URL is correct
4. Increase timeout settings

## Quota

The MCP quotas for the Lite, Pro and Max plans are as follows:
- **Lite:** Include a total of 100 web searches and web readers, along with the 5-hour maximum prompt resource pool of the package for vision understanding.
- **Pro:** Include a total of 1,000 web searches and web readers, along with the 5-hour maximum prompt resource pool of the package for vision understanding.
- **Max:** Include a total of 4,000 web searches and web readers, along with the 5-hour maximum prompt resource pool of the package for vision understanding.

- [Model Context Protocol (MCP) Official Documentation](https://modelcontextprotocol.io/)
- [Claude Code MCP Configuration Guide](https://docs.anthropic.com/en/docs/claude-code/mcp)
- [Z.AI API Reference](https://docs.z.ai/api-reference/introduction)
- [GLM Coding Plan Overview](https://docs.z.ai/devpack/overview)

[Vision MCP Server](https://docs.z.ai/devpack/mcp/vision-mcp-server) [Web Reader MCP Server](https://docs.z.ai/devpack/mcp/reader-mcp-server)