---
title: "How the Dagster MCP allows you to write better code"
source: "https://dagster.io/blog/dagsters-mcp-server"
author:
published:
created: 2025-12-28
description: "Dagster releases its MCP server, enabling seamless AI assistant integration with data pipelines through Anthropic's Model Context Protocol standard for better automation."
tags:
  - "clippings"
---
### We are announcing the release of our MCP server, enabling AI assistants like Cursor to seamlessly integrate with Dagster projects through Model Context Protocol, unlocking composable workflows across your entire data stack.

When Anthropic [announced MCP in late 2024](https://www.anthropic.com/news/model-context-protocol), the initial reaction was one of cautious optimism. AI was evolving so quickly that it wasn’t immediately clear what MCP would mean in practice. But as its implications became clearer, even competitors like OpenAI adopted the protocol.

Since then, other companies have released their own MCP servers. At Dagster, we built our first MCP server earlier this year but chose to wait before releasing it, ensuring it would integrate seamlessly with our recent platform improvements.

Today, we’re excited to make the Dagster MCP server publicly available. It complements everything we’ve been building over the years and opens up new possibilities for writing better, more maintainable code.

## What is MCP?

The Model Context Protocol (MCP) is an open standard developed by Anthropic to connect large language models (LLMs) with external data sources in a secure, standardized way. In Anthropic’s own words:

> “The Model Context Protocol is an open standard that enables developers to build secure, two-way connections between their data sources and AI-powered tools. It provides a universal, open standard for connecting AI systems with data sources, replacing fragmented integrations with a single protocol. The result is a simpler, more reliable way to give AI systems access to the data they need.”

LLMs are powerful at generating coherent language, but on their own, they:

- Lack real-time, accurate, and domain-specific knowledge.
- Have no native ability to interact with databases, APIs, or tools.  
	Rely entirely on what they were trained on which becomes outdated quickly.

![](https://cdn.prod.website-files.com/681399f654933b29e12fb8e4/68962c883127c0c6df70d873_AD_4nXfZQaVyxL9-C2LWHRqcSF1wG2L73q7kDgjMS49Hg6R9LPEPKB5DmcalW9UHZs6rS-X0UvsKI2lbQFUGjXfdiOOcjND8F-IF4vAwv6uG9bHuo1ooTFmSSy9_5Jvh3fAQKfWa2VTTUw.png)

To remain relevant and useful, LLMs must pull information from external sources. When an LLM “searches the web” or queries a knowledge base, it’s functioning as an AI agent, reasoning about what data it needs, where to get it, and how to integrate it into its output.

This approach is powerful but creates challenges:

- **Complexity:** Each LLM must manage custom integrations for every data source.
- **Fragility:** Data sources change, breaking integrations over time.

![](https://cdn.prod.website-files.com/681399f654933b29e12fb8e4/68962c883127c0c6df70d86a_AD_4nXepjXGDZNBV5stsyCTdshNzZN_EwTmZCTa1MY53NFw7oFvgpXSCn4PgqTjODC1ihOHQQtkuXpl5-Ltlk6JNMPzsKYugl4K4P4OE9g36gG5LFE8FbPK5i2pOQsVKlO3Rr3k3_o7kzA.png)

MCP standardizes the connection between AI agents and external services. Instead of every AI system learning how to talk to every data source, the external service provides an MCP interface.

Benefits of this approach:

- **Interoperability:** Any MCP-compatible AI can instantly integrate with the service.
- **Reduced Maintenance:** The service owner maintains the MCP interface, ensuring accuracy and reliability.
- **Future-proofing:** As AI systems evolve, the MCP layer stays consistent.

MCP shifts the integration burden from the AI agent to the service, making the ecosystem simpler, more reliable, and easier to maintain.

![](https://cdn.prod.website-files.com/681399f654933b29e12fb8e4/68962c883127c0c6df70d870_AD_4nXc4YdjBlCXBGvO5_R4F8gb4K7OKC8VxnQZh3uVPpnr_ePbQBLwDEwiAVfnolbz7EksWA3e_XGe8OONfxAKfmIZUidqOoHqE_FJFLj2HFB7-j89gLc-CI6ZE51Hb-6Uz9ZpfbOmrSQ.png)

## Dagster’s MCP Server

So where does Dagster’s MCP fit into all of this, and why does it work so well with our recent features?

If you’ve been following Dagster this year, you know we’re excited about [dg](https://docs.dagster.io/api/dg/dg-cli) and [Dagster Components](https://docs.dagster.io/guides/build/components). These abstractions sit on top of core Dagster objects (such as assets) and make it much easier to build new features or integrate with tools and workflows, often with minimal code.

This combination, a rich core library that can do just about anything, paired with opinionated tooling, is a perfect match for MCP. With a well-documented, structured library, MCP can gain a deep understanding of Dagster’s capabilities. By exposing streamlined code interfaces with tighter guardrails, you can have more confidence in the quality and safety of the code it returns.

![](https://cdn.prod.website-files.com/681399f654933b29e12fb8e4/68962c883127c0c6df70d867_AD_4nXd41RW_85lr1eUGBVS-NQIpR7NguDV91ohibtpvcpD7OPOWwBVqwtN_5Zrz54dTkACBDR-ELda5PiSjCtfSRyej28aaQ31bkjCKiZFZwZSAOez4uv9VowHxZ2tE_NvTxbcfvsL97A.png)

Let’s look at a real-world example. Say you’re using [Cursor](https://www.cursor.so/) and want to start a new Dagster project.

> “Can you scaffold me a new Dagster project named example-project”

With the Dagster MCP configured, Cursor knows where to route requests and translates them to the correct \` [dg](https://docs.dagster.io/guides/labs/dg) \` CLI commands as needed. In this case Cursor would know that it is more efficient to use \`uvx -U create-dagster\` to generate a project than generating all the code itself.

![](https://cdn.prod.website-files.com/681399f654933b29e12fb8e4/68962c883127c0c6df70d86d_AD_4nXenn0HiF8L2Je5A-Am3fzn1q3ccZUjAupPOnAdS47seq07MNsDvuz-0YzSa4DNPrh9K9iAw7WcMYvaU3oWp2Tht3M4WPTDm30yn1XDv6Rywcj-phOyMz7psO4tDNa-f3k531qNNRA.png)

### Composability

What makes the Dagster MCP exciting is that it’s not a one-off integration, it’s composable. If you’re using other tools in your data stack, like dbt, Snowflake, Airbyte, or any service that exposes an MCP interface, your AI assistant can seamlessly interact with all of them together.

> “Can you add dbt to my Dagster project”

Without \`dg\` and components, many LLMs could handle this request by generating code directly. But that approach comes with higher risk: more potential for errors, plus the added cost of processing large amounts of context.

With Dagster MCP, the AI instead guides you toward simple \`dg\` commands to scaffold an integration for a dbt project. This generates just a few lines of YAML needed to configure what is needed. From there, you can use the AI agent to make any necessary changes at the YAML layer, keeping your code clean, concise, and maintainable.

This interoperability unlocks a powerful new way of working: one where AI agents operate across your entire stack, coordinating multiple tools through a shared, universal protocol. Instead of stitching together brittle point-to-point integrations or ad-hoc scripts, you get a unified, extensible interface for building and automating sophisticated workflows, accelerating development while maintaining flexibility and control.

## Trying it out

The best part? You don’t need to be a Cursor user to benefit from the Dagster MCP. As more AI tools adopt MCP, the value of having an MCP-compatible interface to your project will only grow. Standardization in the AI space means better interoperability, more reliable automation, and faster iteration.

You can install the MCP server right now through the **dg\[mcp\]** package, and easily enable it within your tool using **dg mcp configure**.

## Latest writings

The latest news, technologies, and resources from our team.

[View all posts](https://dagster.io/blog/#)