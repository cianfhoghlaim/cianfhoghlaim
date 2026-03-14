---
title: "Zread MCP Server"
source: "https://docs.z.ai/devpack/mcp/zread-mcp-server#repository-access-failed"
author:
  - "[[Overview - Z.AI DEVELOPER DOCUMENT]]"
published:
created: 2025-12-28
description:
tags:
  - "clippings"
---
The Zread MCP Server is a Z.AI implementation based on the Model Context Protocol (MCP). Powered by [zread.ai](https://zread.ai/), it provides Claude Code, Cline, and other MCP-compatible clients with knowledge documentation and code access capabilities for open source repositories.

## Overview

This remote MCP server with open source repository Q&A capability is available to users on **GLM Coding Plan**, enabling your code agent to deeply understand open source projects and efficiently fetch documentation, code structure, and file content.

## Features

## Tools

This server implements the Model Context Protocol and works with any MCP-compatible client. Currently, it provides the following tools:
- **`search_doc`** — Search for knowledge documentation corresponding to the GitHub repository, quickly understanding repository knowledge, news, recent issues, PRs, and contributors.
- **`get_repo_structure`** — Get the directory structure and file list of the GitHub repository to understand project module splitting and directory organization.
- **`read_file`** — Read the complete code content of specified files in the GitHub repository to deeply analyze the implementation details of the file code.

## Example Scenarios

Quickly understand the core concepts, installation steps, and code organization of open source libraries by searching documentation and obtaining repository structures, accelerating the learning curve.

When encountering problems, search the repository’s Issue and Commit history to find solutions or fix records for similar problems.

Directly read the code content of core files, analyze implementation logic, and assist in secondary development or Debugging.

Before introducing a new dependency library, evaluate its activity, code quality, and maintenance status by viewing its repository structure and documentation.

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

**Issue:** Unable to search or read specified repository content **Solutions:**
1. Confirm the repository exists and is open source (public)
2. Check if the repository name is spelled correctly (owner/repo)
3. Visit zread.ai to search if this open source repository is supported

## Quota

The MCP quotas for the Lite, Pro and Max plans are as follows:
- **Lite:** Include a total of 100 web searches, web readers and ZRead MCP calls, along with the 5-hour maximum prompt resource pool of the package for vision understanding.
- **Pro:** Include a total of 1,000 web searches, web readers and ZRead MCP calls, along with the 5-hour maximum prompt resource pool of the package for vision understanding.
- **Max:** Include a total of 4,000 web searches, web readers and ZRead MCP calls, along with the 5-hour maximum prompt resource pool of the package for vision understanding.

## Resources

- [Model Context Protocol (MCP) Documentation](https://modelcontextprotocol.io/)
- [Claude Code MCP Configuration Guide](https://docs.anthropic.com/en/docs/claude-code/mcp)
- [Z.AI API Reference](https://docs.z.ai/api-reference/introduction)
- [GLM Coding Plan Overview](https://docs.z.ai/devpack/overview)

[Web Reader MCP Server](https://docs.z.ai/devpack/mcp/reader-mcp-server) [Coding Tool Helper](https://docs.z.ai/devpack/extension/coding-tool-helper)