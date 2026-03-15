Crypto Analytics Project – Document Summaries

and Spec Update

Document Summaries

Crypto Analysis AI Agent System Architecture

•

Objective & Focus: This document outlines a multi-agent crypto analytics system

architecture. Its goal is to enable AI agents to ingest, enrich, and reason over crypto data. The

focus is on a layered pipeline that handles data from raw ingestion to intelligent analysis

1

.

•

Key Components & Tools: It proposes four layers, each with specialized tools

1

:

•

Data Ingestion: Use DLT (Data Load Tool) to reliably fetch and normalize raw crypto data from

various sources (exchange prices, on-chain metrics, social/news feeds) into structured datasets.

•

Indexing & Embedding: Apply CocoIndex to transform new data into an indexable format, e.g.

computing technical indicators or chunking text, and generate vector embeddings for textual

content

2

3

. CocoIndex runs incrementally so updates are indexed without full reprocessing.

•

Knowledge Graph & Search: Store enriched data in Cognee, a hybrid knowledge base

combining a graph database with a vector store for semantic search

4

. Cognee builds a graph

of entities (tokens, addresses, metrics) and relations (e.g. Token has Price), while retaining

embeddings for similarity search. This acts as a persistent “brain” of crypto knowledge that

supports both structured queries and semantic lookups.

•

Agent Orchestration: Utilize Agno, an open-source multi-agent orchestration framework, to

coordinate LLM-powered agents that use the Cognee knowledge base. Agents can retrieve

relevant context (latest prices, related news, etc.) via Cognee’s API and then reason over it to

answer questions, summarize trends, detect anomalies, etc.

5

. Agno enables tool use and

multi-agent collaboration (e.g. separate Trend-Summarizer, Anomaly-Detector agents) in

workflows.

•

Integration with Project: This architecture complements the project’s AI-driven goals by

providing a blueprint for how ingested data flows into an intelligent index and agent layer.

In the context of our project, DLT is already the pipeline tool for data extraction, and this

document suggests augmenting the pipeline with CocoIndex and Cognee for continuous

embedding and knowledge graph storage. It also introduces an agent layer (Agno) to allow LLM-

based analysis on top of the data. Incorporating these ideas will enhance our system’s ability to

provide context-aware insights, not just through traditional queries but via AI agents leveraging

a rich memory store. This aligns with the project’s AI-native approach, making the analysis more

automated and scalable.

Pulumi TypeScript Guide: Provisioning Cloudflare D1 & R2 with 1Password

Integration

•

Objective & Focus: This guide demonstrates provisioning key cloud infrastructure (Cloudflare

D1 database and R2 object storage) using Pulumi in TypeScript, with an emphasis on managing

secrets via 1Password

6

. The focus is practical DevOps: deploying a serverless SQL database

alongside storage, then securely storing credentials.

•

Key Components & Tools: It covers:

1

•

Pulumi (TypeScript): Infrastructure-as-Code framework used to define and deploy resources.

The guide walks through writing a Pulumi program that creates a Cloudflare D1 database and an

R2 bucket in one stack

6

.

•

Cloudflare D1: A serverless SQLite-based database. The program provisions a D1 instance,

demonstrating how to retrieve outputs like the database UUID and connection info.

•

Cloudflare R2: S3-compatible object storage (already part of our stack for storing data files). The

guide shows creating an R2 bucket and generating an API access token for it.

•

1Password Integration: Uses the 1Password Node.js SDK to programmatically store sensitive

outputs (like the DB ID and API token) into a 1Password vault

7

8

. Environment-specific vault

entries or vaults are recommended to segregate dev vs prod secrets.

•

Multi-Environment Stacks: It also demonstrates structuring the Pulumi project with multiple

stacks (e.g. development and production) so that different configurations can be deployed easily

using the same codebase, which improves deployment agility and safety across environments

9

10

.

•

Integration with Project: The project’s infrastructure uses Cloudflare R2 for data lake storage,

so this guide’s patterns directly apply to our setup. We will leverage Pulumi for IaC to provision

R2 (and optionally D1 if a lightweight relational store is needed for metadata or caching). By

following this guide’s approach, we ensure cloud resources are created reproducibly in code

and credentials are kept secure (never hard-coded, but stored in 1Password and referenced via

environment variables). This aligns with our security and DevOps practices: using Pulumi to

manage cloud resources, and using a secrets manager (1Password) to protect API keys and IDs.

The multi-stack setup in Pulumi also fits our need to maintain separate dev/test and prod

environments with the same infrastructure definitions, supporting a robust CI/CD pipeline.

Extending  komodo-pr-deploy  for Pangolin Integration via Komodo Actions

•

Objective & Focus: This document describes how to enhance a GitOps deployment workflow

(using Komodo for PR deploys) by integrating Pangolin. The main goal is to automate the

publication of deployed preview environments behind Pangolin’s zero-trust proxy, using

Komodo’s action system.

•

Key Components & Tools: It details a typical PR preview pipeline:

•

Komodo PR Deploy Action: A GitHub Action (with a Node script) that on each pull request build,

uses the Komodo CLI/SDK to build a Docker image from the PR’s code and deploy it on a
Komodo server

. Komodo handles the Docker build and runs the container, creating an

12

11

ephemeral environment for that branch.

•

Pangolin (Zero-Trust Proxy): Pangolin is a secure networking layer that exposes services via a

controlled domain. The integration involves calling Pangolin’s REST API after deployment to

register the new container so it becomes accessible at a unique subdomain (e.g.
pr-123.yourdomain.com )

. Pangolin acts as a zero-trust access layer, meaning each

13

preview environment is behind an authenticated, policy-controlled gateway.

•

Komodo Actions: Instead of letting the GitHub Action call Pangolin directly, the document

suggests creating a Komodo Action (a script running within Komodo’s context) to handle the

Pangolin registration. This would be triggered post-deployment via the Komodo SDK, passing

deployment info to the action which then invokes Pangolin’s API. This approach centralizes the

integration logic in Komodo.

•

Secret Management: The integration highlights handling of credentials (Pangolin API token,

IDs) either via GitHub secrets (already in use) or by storing them on the Komodo server to avoid

exposing them in CI logs

14

15

.

•

Integration with Project: In our project, Komodo is used for GitOps-style deployment (as noted

in our GitOps convention), and Pangolin will be used to securely expose services. This

document’s guidance ensures that whenever we deploy our application (or any microservice) via

2

Komodo, it will automatically be made available through Pangolin’s secure proxy. Practically, this

means our team can stand up isolated preview or production environments and access them

through authorized channels, aligning with a zero-trust security model. We will incorporate

these recommendations by adding a Pangolin registration step to our deployment pipeline,

likely via a Komodo Action or similar hook. This improves our DevOps flow by automating

environment exposure and keeping the process secure

16

. It reinforces our GitOps principle: a

PR deployment is seamlessly integrated into the environment with proper access controls, and

documentation will be updated accordingly so developers know how preview URLs are

generated and secured.

Key Data Types for Ethena/Ethereum Yield Strategies and Their Sources

•

Objective & Focus: This document identifies the critical data types and metrics needed to

analyze Ethena’s stablecoin (USDe) yield strategy on Ethereum, and enumerates where to obtain

each data type. The focus is on financial metrics (on-chain and off-chain) that drive or

measure yield performance, providing guidance on data sources for both real-time monitoring

and historical analysis.

•

Key Data Categories & Sources: It breaks down the data needs into several categories:

•

Price and Peg Metrics: e.g. USDe peg price (should hover ~$1.00) and sUSDe price (staked USDe

value that accrues yield). These can be fetched from public APIs like CoinGecko or
CoinMarketCap for live and historical prices

. On-chain DEX data or subgraphs are also

17

18

mentioned as alternatives for real-time peg verification. Monitoring these prices reveals peg

stability and realized APY (since sUSDe appreciates as yield accumulates).

•

Supply & TVL Metrics: e.g. USDe circulating supply (market cap) and Ethena protocol TVL

(collateral backing). DeFi Llama’s API provides current and historical supply and TVL for USDe

and Ethena, broken down by chain

19

20

. This data helps track adoption (supply growth) and

risk (collateral levels) over time. Other sources like CoinGecko/CoinMarketCap offer similar

market cap data for cross-validation.

•

Yield & Rate Metrics: these directly affect strategy returns:

◦

Ethena’s native yield (sUSDe APY): composed of Ethereum staking rewards and perpetual

futures funding yield. Ethena’s app/dashboard shows the current APY and breakdown,

and DeFi Llama lists a “sUSDe staking” pool with current and 30d APY

21

. Historical yield

series can be built from these or from sUSDe price history. This metric is vital for

evaluating performance under different market conditions (it has ranged from ~4% to

>20% APY depending on market regime).

◦

Perpetual Funding Rates: since part of Ethena’s yield comes from shorting ETH perps, the

funding rate data is crucial. The document suggests pulling funding rates from major
exchanges (e.g. Binance’s API for  fundingRate  on ETHUSDT perpetuals) to see

prevailing funding yields

22

23

. These rates are highly variable and turn negative in

bearish markets (reducing yield), so collecting historical funding data allows backtesting

of Ethena’s yield in various scenarios.

◦

Ethereum Staking Yield: the steady ~3–4% APR from ETH staking (for collateral ETH) –

available from sources like Beaconcha.in or Staking Rewards APIs. This is relatively stable

but can be tracked via APIs for precision

24

25

.

◦

Aave Supply (Deposit) Rates: if the strategy involves looping through Aave (depositing USDe

or other assets), the deposit APYs matter. Aave’s subgraph or API provides real-time

supply rates for assets (e.g. depositing USDe might earn ~5% if borrowers pay interest)

26

. Historical variations can be fetched to see how rates respond to market stress (after

large market moves, rates can drop).

◦

Aave Borrow Rates: the cost of borrowing stablecoins on Aave, since Ethena’s strategy

might borrow USDT/USDC to buy more USDe. This cost must be compared to the yield.

3

Aave APIs give current variable borrow APRs (recently ~5-6% for USDC/USDT, dropping to

~2% after a crash)

27

. Tracking the spread between sUSDe yield and borrow APR is

critical for profitability; a negative spread (borrow cost > yield) signals an unprofitable

loop

28

29

.

◦

Pendle Fixed Yields: if using Pendle (DeFi protocol for yield tokenization) to lock in fixed

yield on USDe, data on Pendle’s PT (Principal Token) markets is needed. The doc notes

Pendle’s subgraph or API can provide current fixed rates for USDe (e.g. a certain maturity

yielding ~6.6% APY)

30

. This helps compare the fixed-rate opportunity vs the variable

sUSDe rate.

•

Summary: In short, the document compiles a data registry for a complex DeFi strategy,

recommending free or open sources for each. It emphasizes combining on-chain metrics,

protocol stats, and market data to get a full picture of performance and risk.

•

Integration with Project: Our project aims at holistic crypto analysis, and this document serves

as a template for the structured data sources we should include. It reinforces the need for a

comprehensive data ingestion strategy: not just general market indicators (like the Fear &

Greed index mentioned in our context), but also protocol-specific metrics and DeFi rates. In

practice, we will integrate many of these suggested data feeds into our DLT ingestion pipeline –

for example, pulling pricing data from CoinGecko, on-chain stats from DeFi Llama or subgraphs,

and exchange rates from public APIs. This will enrich our quantitative dataset beyond simple

price history, allowing analysis of how market sentiment and events correlate with fundamentals

like yields, liquidity, and borrowing costs. By including such diverse data, the system can explore

research questions like “How do shifts in sentiment or news events impact DeFi yields and stablecoin

pegs?” which aligns with our goal of context-aware analysis. Essentially, this document’s content

ensures our data lake includes the key DeFi metrics and reference data needed for advanced

crypto strategy analysis.

Integration Plan for a Crypto Analytics & Discovery System

•

Objective & Focus: This integration plan proposes a layered architecture for a crypto analytics

and discovery platform, emphasizing longevity, maintainability, and open interfaces. It focuses

on how different components (ingestion, storage, indexing, UI) should interconnect in a modular

way so that the system remains extensible and future-proof.

•

Key Components & Architecture: The plan describes four layers, aligned with modern data

engineering practices:

•

Data Sources & Ingestion: A structured registry of data sources drives both historical and

streaming ingestion. The system continuously pulls clean data (both metrics and documents)

from multiple platforms in the crypto ecosystem. The ingestion is incremental, ensuring new

data is added without reprocessing all history

31

.

•

Storage & Lakehouse: Cloudflare R2 is used as a durable data lake to store all raw and

processed data (e.g. as Parquet files). On top of this, a DuckDB-based lakehouse (referred to as

DuckLake) provides a SQL query engine and manages table metadata (using the Apache Iceberg

format for interoperability)

32

. This layer ensures that all data, past and present, can be

accessed uniformly via SQL and analytical queries.

•

Indexing & Linking: New data is fed into an AI-powered indexing layer. CocoIndex generates

vector embeddings for textual content, enabling semantic search, while Cognee builds a

knowledge graph linking entities across datasets

33

. Together, a vector index and graph

database work in tandem to support hybrid queries – e.g. you can search by meaning or context,

while also applying structured filters or traversing relationships (such as linking an on-chain

metric to relevant news articles). This layer adds a semantic “brain” to the system, capturing both

unstructured and structured knowledge.

4

•

Discovery & Search UX: On top of the data/knowledge layers sits a user-facing interface for

discovery. The plan suggests a front-end that could use DuckDB-Wasm (running in-browser SQL

queries on the data files) or a lightweight backend, combined with queries to the vector/graph

index for semantic results

34

. The UI would allow users to search and explore the data with

rich features: free-text search (powered by embeddings), filters and facets (using structured

metadata), and possibly graph-based visualizations. It draws inspiration from library science

(Harvard LIL’s approach) to make exploration intuitive – akin to browsing an archive where one

can seamlessly pivot between data points, documents, and metrics.

•

Integration with Project: This plan essentially blueprints our project’s target architecture. It

validates our current stack choices and suggests how to integrate them:

•

We will maintain a decoupled layering: DLT for ingestion feeding into Cloudflare R2 + DuckDB

(lakehouse) for storage/analytics, then CocoIndex + Cognee for indexing and knowledge linking,

and finally a discovery interface or agent layer on top. Each layer communicates via clear

interfaces (Parquet/CSV files, SQL queries, or API calls), which aligns with our “separation of

concerns” principle.

•

The emphasis on open formats and minimal server dependencies means our system can be kept

lightweight and easy to preserve. For instance, using static object storage and possibly a static

front-end ensures the platform can be archived or scaled without complex microservices. This

supports the project’s resilience and longevity goals.

•

The plan also underlines extensibility: we can swap out any component (e.g., replace the vector

DB or move to another cloud storage) without breaking the whole system, as long as interfaces

remain consistent. This is important in the fast-evolving crypto and AI landscape.

•

Finally, incorporating a dedicated discovery UI layer encourages us to think about how end-users

(or researchers on our team) will interact with the data. While our original project description

focused on the pipeline, this plan reminds us to deliver the insights effectively – possibly by

building a web-based explorer or integrating with an AI assistant that can answer questions

from the data. In summary, the integration plan steers our project to be comprehensive

(covering ingestion to insight delivery) and future-proof, using the latest best practices in data

engineering and AI indexing.

Revised Project Specification

Project Context

Purpose

This   project   aims   to   build   a   sophisticated,  hybrid   data   pipeline   and   knowledge   system  for

cryptocurrency analysis. The system will synthesize a wide range of  quantitative market indicators

(prices, indices, yields, blockchain metrics, etc.) from APIs with qualitative, unstructured data scraped

from web sources (news articles, blogs, research PDFs, social media). The primary objective is to enable

a  holistic, context-aware analysis  of cryptocurrency market trends and sentiment cycles. We move

beyond   simple   price   tracking   to   understand   the   narratives,   events,   and   fundamental   metrics   (e.g.

stablecoin stability, DeFi yields) that drive market behavior and psychology.

The architecture is designed to be  distributed, secure, and resilient, leveraging a modern, AI-driven

technology stack to continuously learn from new data. Ultimately, the platform should not only store

and query data, but also support intelligent agents or tools that can reason over the data to provide

insights in real-time.

5

Tech Stack

•

Developer Environment: mise  (for polyglot tool version management) and Bun (JavaScript

runtime) for a consistent dev setup.
Data Ingestion & Scraping: crawl4ai  for web and document scraping (HTML pages, PDFs) to

•

gather news and text; DLT (Data Load Tool) for managing structured data extraction from APIs

and feeds, performing normalization and loading into our pipeline.

•

Data Pipeline/Orchestration: dlt (Data Load Tool) orchestrates the ETL process, scheduling

fetches from crypto APIs (e.g. fear/greed index, exchange data, DeFi protocol stats) and

integrating with scraping tasks. It ensures data from diverse sources is cleaned and transformed

into well-defined tables or records.

•

Storage:

•

Object Storage: Cloudflare R2 for durable, cost-efficient storage of raw and processed data files

(Parquet, JSON, etc.), benefiting from zero egress fees for data sharing.
Analytical Warehouse: DuckDB  (embedded OLAP database) for in-process SQL analytics on

•

the data lake. DuckDB, paired with the DuckLake approach (DuckDB + Apache Iceberg table

format), serves as our lakehouse, maintaining a catalog of datasets and enabling performant

analytical queries on large data volumes.

•

Metadata & Catalog: Apache Iceberg via DuckLake for table metadata, enabling schema
evolution and partitioning while staying vendor-neutral in data format.

•

Indexing & Knowledge Base: CocoIndex for incremental data indexing and embedding

generation. As new data arrives, CocoIndex will compute vector embeddings for textual content

(for semantic search) and prepare structured indexes. Cognee acts as a hybrid knowledge store,

ingesting CocoIndex outputs to build a graph of entities and relationships enriched with

vector embeddings. This combination allows semantic similarity search and graph queries over

the data (e.g. linking on-chain metrics to related news or connecting entities across articles).
AI & Data Extraction: BAML (Boundary AI Markup Language)  for using large language

•

models to extract structured information from unstructured text (e.g. pulling out key topics,

sentiments, or named entities from articles). This enriches our datasets with AI-extracted

features.

•

AI Agent Orchestration: Agno (Agent Orchestrator) or a similar multi-agent framework to

enable one or more AI agents to analyze data from the knowledge base. This layer allows us to

deploy specialized LLM-based agents (for instance, one for trend summarization, one for

anomaly detection, one for Q&A) that can use tools and retrieve memory (via Cognee) to

perform complex analytical tasks autonomously.
Infrastructure & Deployment: Pulumi  for defining and managing cloud infrastructure as

•

code (provisioning R2 buckets, databases, etc.), and managing configurations for multiple

environments (dev/staging/prod). We use 1Password integration to securely manage secrets

(API keys, database IDs) in our Pulumi workflow, ensuring no plaintext secrets in code.

•

DevOps & Networking: Komodo (GitOps platform) for automated deployment of our services

(e.g. launching a containerized app or data pipeline on updates). Komodo will build and deploy
Docker containers from our repository (using our  docker-compose.yml  for consistency).

Pangolin (zero-trust networking layer) is used in tandem with Komodo to expose these services

securely. When the system is deployed, Pangolin publishes the endpoints behind an

authenticated, organization-controlled domain, providing secure access to dashboards or APIs

without public exposure.

•

Frontend / Discovery UI: (Planned) A search and analytics UI powered by our data backend. This

could involve a web front-end that leverages DuckDB-Wasm (for in-browser SQL queries on

Parquet files) and queries to the Cognee index for semantic search. The aim is to provide users

and researchers with an interactive portal to query the data (both through structured SQL and

natural language search), explore relationships, and visualize findings.

6

Project Conventions

Code Style

•

Write Python code in a clean, consistent style (formatted with  black  and linted with  ruff ).

JavaScript/TypeScript code should likewise follow a formatter/linter (e.g. Prettier, ESLint).
Use clear,  snake_case  naming for variables and functions in Python, and idiomatic naming

•

conventions in TypeScript.

•

Keep functions and modules focused; use comments sparingly and primarily to explain non-

obvious logic. Comments should be short and in lowercase where used.

Architecture & Design Patterns

•

Sovereign & Decoupled Infrastructure: Favor modular, open-standard components to avoid

lock-in. Each layer of the system should be interchangeable if possible. (For example, we use

open formats like Parquet/Iceberg for data, which could be moved to another storage solution;

our vector/graph index can be swapped out with minimal changes as long as it exposes similar

APIs.)

•

Separation of Concerns (DuckLake Pattern): Follow the lakehouse separation between

storage, compute, and metadata. Cloudflare R2 handles storage, DuckDB handles compute/

queries, and the DuckLake catalog (Iceberg) handles metadata. Similarly, separate the concerns

of ingestion, indexing, and querying layers in our architecture.

•

AI-Native Workflows: Integrate AI tools directly into data processing. For example, use
crawl4ai  to fetch content and  BAML  within the pipeline to transform unstructured text into

structured insights. Additionally, employ the AI agent layer (Agno + Cognee) to enable intelligent

automation — e.g. an agent that periodically summarizes new findings or flags anomalies in

•

metrics.
GitOps for Deployment: Treat our operational configurations as code. A central  docker-
compose.yml  (and any Komodo config) defines the services. Deployments are triggered via git

workflows (e.g. pull request merges), automated by Komodo. Each change to the system

(infrastructure or application) goes through version control and CI, ensuring traceability and

reproducibility of environments.

•

Security & Secrets Management: Adhere to zero-trust principles. All service endpoints

(especially internal tools like dashboards or databases) are behind Pangolin’s authenticated

proxy – no direct open ports. Manage secrets through 1Password and inject them at runtime or

deployment; never store credentials in git. Use environment-specific vaults/variables so that, for

instance, production keys are only accessible in production deployments.

•

Scalability & Extensibility: Design each component to handle growing data volumes and new

data sources. Ingestion should support adding new connectors (APIs or scrapers) easily. The

data lake can partition data as it grows. The index should handle increasing vector counts by

scaling out (using a vector DB backend that can scale, if needed). Plan for horizontal scaling in

the deployment (e.g. the ability to run multiple agent instances or query nodes if demand

increases).

Testing Strategy

•

Unit Tests: Develop unit tests for individual pipeline components and utilities. For example, test

data normalization functions, scraping logic, or BAML prompt templates in isolation to ensure

they produce expected outputs.

7

•

Integration Tests: Set up tests for the data pipeline flows, perhaps using a small subset of

sources. This could involve running a mini DLT pipeline that goes from ingestion to storage to

indexing to querying, verifying that each layer receives and processes data correctly.

•

End-to-End Tests: Periodically run the entire pipeline on a controlled input and validate the final

outcomes. For instance, simulate ingesting a known dataset (with known insights) and ensure

the system can scrape, store, and retrieve the correct information through the front-end or

agent queries. Additionally, test the deployment process via Komodo/Pangolin in a staging

environment to ensure that infrastructure changes and service exposures work as expected.

•

Continuous Monitoring: Incorporate runtime checks and logging in the pipeline. If an ingestion

fails or a query service is down, alerts should be raised. This is more of an operational concern,

but it overlaps with testing in that we ensure the system is self-observing and issues can be

caught early.

Git Workflow

•

All changes to the codebase or infrastructure are introduced via an OpenSpec change proposal

(a structured Git-based proposal process). This means major modifications require a design

discussion and consensus before implementation.

•

Use a feature-branching model: each new feature or fix is developed in its own branch, which

goes through code review (via pull request) before merging to the main branch.
Write clear, descriptive commit messages. Begin the message with a concise summary (e.g. "Add

•

CocoIndex integration for vector embedding") and include details if necessary in the body. This

helps in tracing history and understanding the rationale behind changes.

•

Tag releases or significant milestones in the repository to mark stable versions of the system

that correlate with deployed infrastructure states.

Domain Context

We   operate   in   the  cryptocurrency   domain,   with   a   special   focus   on  market   sentiment   and

fundamental analysis. Key domain concepts include: -  Market Sentiment Cycles:  e.g. tracking the

crowd   psychology   from   fear   to   greed.   We   incorporate   sentiment   indices   (like   the   "Fear   and   Greed

Index") and perform textual sentiment analysis on news and social media. Understanding sentiment

helps explain price movements beyond technical indicators. - On-Chain Metrics & DeFi Analytics: We

consider blockchain data such as transaction volumes, stablecoin supply, total value locked (TVL) in

protocols, yield rates, and other metrics. For instance, monitoring a stablecoin’s peg or a yield protocol’s

APY can reveal stress or optimism in the market that sentiment alone might miss. -  Cross-Impact of

Narratives   and   Metrics:  The   goal   is   to   correlate   quantitative   data   with   qualitative   narratives.   For

example, if news of a major hack surfaces, we examine not just the negative sentiment but also on-

chain reactions (withdrawals, price drops). Conversely, if a DeFi yield spikes, we seek the narrative cause

(new investment, market regime shift, etc.). - Examples in Focus: The rise of Ethena’s USDe stablecoin

and its yield strategy is a case study: by combining data on its peg stability, yield components, and

related news, one can analyze how confidence and usage of that stablecoin evolve. Another example is

tracking how major events (regulatory announcements, Bitcoin halvening, etc.) are reflected in both

media sentiment and metrics like market dominance or funding rates.

By grounding our analysis in both human context (what people believe, fear, and speculate) and data

reality  (what on-chain and market numbers show), we aim to produce insights that are robust and

nuanced.

8

Important Constraints

•

Dual Data Nature: The system must handle both structured data (numerical time-series, API

feeds) and unstructured text (articles, posts). This means our pipeline and storage solutions
must be flexible – e.g. storing text embeddings and numerical data side by side, and ensuring

each can be queried or related.

•

Real-Time vs Batch Trade-offs: Some data (like prices or funding rates) updates frequently,

while others (like research reports) come in slower. The architecture should support real-time

streaming for critical metrics without overwhelming the system, while batch-updating slower

datasets. We use incremental indexing to keep the system up-to-date without reprocessing

everything on each update.

•

Scalability: Crypto data can grow quickly (think of every block’s transactions, or a firehose of

tweets). Our choices of DuckDB and vector databases should scale to millions of records. We

must also design for efficient pruning or archiving of data when appropriate (e.g. maybe only

keep embeddings for the last N months of news if storage is a concern, or aggregate older data).

•

Cost Management: Given the open-source, research nature of the project, we choose cost-

efficient solutions: Cloudflare R2 for cheap storage, DuckDB (which is free and in-process) for

analytics, and using serverless or static approaches where possible. We avoid heavy long-

running servers – for example, considering a static front-end with client-side querying means we

can serve the UI on GitHub Pages or similar with minimal cost. We also leverage cloud credits or

free tiers for APIs and carefully monitor usage of any paid API (rate limits, etc.).

•

Security and Privacy: Although the data we handle is mostly public, any keys or accounts (for

API access or deployment) must be protected. Using Pangolin ensures that any internal

dashboards or agent endpoints are not exposed to the open internet. Furthermore, if we

integrate with an LLM API (OpenAI, etc.), we need to be mindful of what data we send (avoiding

sensitive info) and abide by data policies.

External Dependencies

•

Cryptocurrency Data APIs: e.g. Alternative.me (Fear & Greed Index), CoinGecko/CoinMarketCap

(price and market data), DeFi Llama (TVL and yield data), exchange APIs like Binance or Bybit

(funding rates, market depth), Aave/DeFi protocol subgraphs (on-chain lending/borrowing rates).

•

Web Scraping Targets: Various news sites, crypto blogs, forums (like Medium, CoinDesk, Reddit,

etc.), and possibly academic or regulatory PDF sources. These provide the unstructured texts

that our scraping pipeline will fetch and our LLM (BAML) will parse.

•

Cloud Services: Cloudflare R2 (object storage) and D1 (if used for any quick key-value or

relational data needs), Cloudflare Workers or Pages (potentially for hosting the static UI or edge

compute tasks). Our Pulumi configuration will interface with these services, and we rely on their

availability.

•

LLM Provider: An LLM API (such as OpenAI’s GPT-4 or Anthropic’s Claude) is required for BAML’s

extraction tasks and potentially for agent reasoning. We need an API key and must manage

usage limits. The provider’s reliability and the cost of LLM calls are factors to watch.

•

Komodo & Pangolin Platform: As part of our deployment stack, we depend on the Komodo

platform to build/deploy our Docker containers and on Pangolin for secure access. This implies

maintaining our Komodo server (with the necessary build agents and access credentials) and a

Pangolin instance configured with our domain and integration API enabled. Updates or issues in

these platforms could affect our CI/CD pipeline.

By understanding these dependencies and constraints, the project is better positioned to mitigate risks

(like data outages or cost overruns) and ensure a smooth development and deployment lifecycle. With

the above architecture and tools, we aim to deliver a robust crypto analytics and discovery system that

9

can adapt as the crypto landscape evolves, providing valuable insights to researchers and analysts in

real-time.

1

2

3

4

5

Crypto Analysis AI Agent System Architecture.pdf

file://file_00000000ca007243bfa47bcc5ba0e02a

6

7

8

9

10

Pulumi TypeScript Guide_ Provisioning Cloudflare D1 & R2 with 1Password

Integration.pdf

file://file_00000000600072469bea6c76f7d818b9

11

12

13

14

15

16

Extending __komodo-pr-deploy__ for Pangolin Integration via Komodo Actions.pdf

file://file_0000000016e07246aa91906dafcf5791

17

18

19

20

21

22

23

24

25

26

27

28

29

30

__Key Data Types for Ethena_Ethereum Yield

Strategies and Their Sources__.pdf

file://file_000000006cdc71f4a5c9b153c67e8a1e

31

32

33

34

Integration Plan for a Crypto Analytics & Discovery System.pdf

file://file_000000006728720aa64a47dfb7f3c23a

10

