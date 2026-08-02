---
title: "Vision MCP Server"
source: "https://docs.z.ai/devpack/mcp/vision-mcp-server"
author:
  - "[[Overview - Z.AI DEVELOPER DOCUMENT]]"
published:
created: 2025-12-28
description:
tags:
  - "clippings"
---
Vision MCP Server is a Z.AI capability implementation based on the Model Context Protocol (MCP), providing powerful Z.AI GLM-4.6V capabilities for MCP-compatible clients such as Claude Code and Cline, including image analysis, video understanding, and other features.

**NPM Package**: [@z\_ai/mcp-server](https://www.npmjs.com/package/@z_ai/mcp-server)  
**Prerequisites**: [Node.js >= v22.0.0](https://nodejs.org/en/download/)

Please install the latest version(>= 0.1.2) of the vision mcp server to experience the GLM-4.6V capability.  
Existing users might still be using a cached older version. Please clear the npx cache, or append the `@latest` tag to `z_ai/mcp-server` to force-install the newest version (i.e., `z_ai/mcp-server@latest`).

## Product Overview

This Local MCP Server is an exclusive server developed by Z.AI for **GLM Coding Plan users**, empowering your Code Agent with eyes and limitless vision understanding.

Except in Claude Code, pasting an image directly into the client cannot call this MCP Server, as the client will by default transcode the image and call the model interface directly.  
The best practice is to place the image in a local directory and invoke the MCP Server by specifying the image name or path in the conversation.  
For example: `What does demo.png describe?`

## Features

## Image Analysis

Supports intelligent analysis and content understanding of multiple image formats, giving your AI Agent visual capabilities

## Video Understanding

Supports visual understanding of both local and remote videos

## Easy Integration

One-click installation, quick integration with Claude Code and other MCP-compatible clients

## Supported Tools

This server implements the Model Context Protocol and can be used with any MCP-compatible client. Currently provides the following tools:
- **`ui_to_artifact`** - Turn UI screenshots into code, prompts, specs, or descriptions.
- **`extract_text_from_screenshot`** - OCR screenshots for code, terminals, docs, and general text.
- **`diagnose_error_screenshot`** - Analyze error snapshots and propose actionable fixes.
- **`understand_technical_diagram`** - Interpret architecture, flow, UML, ER, and system diagrams.
- **`analyze_data_visualization`** - Read charts and dashboards to surface insights and trends.
- **`ui_diff_check`** - Compare two UI shots to flag visual or implementation drift.
- **`image_analysis`** - General-purpose image understanding when other tools don’t fit.
- **`video_analysis`** - Inspect videos (local/remote ≤8 MB; MP4/MOV/M4V) to describe scenes, moments, and entities.

## Environment Variable Configuration

### Detailed Configuration

## Installation and Usage

### Quick Start

### Supported Clients

- Claude Desktop
- Cline (VS Code)
- OpenCode
- Crush
- Roo Code, Kilo Code and Other MCP Clients

**Method A: One-click Installation Command** Be sure to replace `your_api_key` with the API Key you obtained.If you forgot to replace the API Key, you need to uninstall the old MCP Server before re-executing the installation command:**Method B: Manual Configuration** Edit Claude Desktop’s configuration file `.claude.json` `mcpServers` content:  
Be sure to replace `your_api_key` with the API Key you obtained.

## Usage Example

Except in Claude Code, pasting an image directly into the client cannot call this MCP Server, as the client will by default transcode the image and call the model interface directly.  
The best practice is to place the image in a local directory and invoke the MCP Server by specifying the image name or path in the conversation.  
For example: `What does demo.png describe?`

Through the previous step of installing the Vision MCP server to the client, you can directly use MCP in your Coding client.  
For example, in Claude Code, inputting `hi describe this xx.png` in the conversation, the MCP Server will process the image and return the description result. (The prerequisite is that you have the image in your current directory)![Description](https://cdn.bigmodel.cn/markdown/1760501186683image.png?attname=image.png)

Description

## Troubleshooting

Run the following command in your local terminal to verify if it can be installed locally, to troubleshoot environment, permission, and other issues:
- If installed successfully, it indicates that the environment is correct, and the issue may be with the client configuration. Please check the client’s MCP configuration.
- If installation fails, please troubleshoot based on the error message. It is recommended to paste the error message to a large model for analysis and resolution.
Other common issues:

Connection Closed

**Issue：** Mcp server connection closed **Solutions：**
1. Check whether Node.js 22 or a newer version is installed locally.
2. Run `node -v` and `npx -v` to verify that the execution environment is available.
3. Check the environment variable `Z_AI_API_KEY` is configured correctly.

**Issue:** Receiving invalid API Key error **Solutions:**
1. Confirm the API Key is correctly copied
2. Check if the API Key is activated
3. Confirm the selected platform (`Z_AI_MODE`) matches the API Key
4. Check if the API Key has sufficient balance

Connection Timeout

**Issue:** MCP server connection timeout **Solutions:**
1. Check network connection
2. Confirm firewall settings
3. Increase timeout settings

## Quota

The MCP quotas for the Lite, Pro and Max plans are as follows:
- **Lite:** Include a total of 100 web searches and web readers, along with the 5-hour maximum prompt resource pool of the package for vision understanding.
- **Pro:** Include a total of 1,000 web searches and web readers, along with the 5-hour maximum prompt resource pool of the package for vision understanding.
- **Max:** Include a total of 4,000 web searches and web readers, along with the 5-hour maximum prompt resource pool of the package for vision understanding.

- [Model Context Protocol (MCP) Official Documentation](https://modelcontextprotocol.io/)
- [Claude Desktop MCP Configuration Guide](https://docs.anthropic.com/en/docs/claude-code/mcp)
- [Z.AI API Reference](https://docs.z.ai/api-reference/introduction)
- [Vision Model Introduction](https://docs.z.ai/guides/vlm/glm-4.6v)

[FAQs](https://docs.z.ai/devpack/faq) [Web Search MCP Server](https://docs.z.ai/devpack/mcp/search-mcp-server)