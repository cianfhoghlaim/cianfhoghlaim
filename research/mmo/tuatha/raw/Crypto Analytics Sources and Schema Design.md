Crypto Analytics Sources and Schema Design

Crypto Analytics Data Sources Overview

The landscape of crypto analytics relies on a variety of public data sources, each exposing different

types of information (market data, DeFi protocol stats, blockchain explorer data, etc.) through APIs,

subgraphs, documentation, and open-source repositories. Below we highlight key sources – CoinGecko,

DeFiLlama,  Aave,  Beaconcha.in, and  Pendle  – including the types of sources they provide and their

access endpoints:

CoinGecko

•

REST API: CoinGecko provides a comprehensive public REST API (base URL:
api.coingecko.com/api/v3 ) for cryptocurrency market data. It offers a wide range of

. The
endpoints returning JSON data for prices, market charts, exchange info, and more
API covers thousands of crypto assets and exchanges, making it a “reliable crypto market data

1

2

[source] through RESTful JSON endpoints”

1

.

•

Documentation: Official API documentation is available on the CoinGecko docs site

(docs.coingecko.com) which describes usage and endpoints. CoinGecko recently also introduced

WebSocket streams for real-time data (available to paid API tiers)

3

4

.

•

OpenAPI Specification: There is no official Swagger/OpenAPI spec from CoinGecko; however,

the community maintains unofficial OpenAPI 3.0 specifications for the CoinGecko API on GitHub

5

6

. These specs document the endpoints, request/response schemas, and metadata, aiding

developers in integration.

•

Related Repositories: While CoinGecko’s data is primarily accessed via the API, there are

community wrappers and SDKs (e.g. Python, JavaScript libraries) and the aforementioned

OpenAPI spec repo. (CoinGecko’s own platform is not open-sourced, focusing instead on

providing the public API.)

DeFiLlama

•

REST API: DeFiLlama offers an open, free-to-use API for decentralized finance metrics. The base
endpoints (e.g.  https://api.llama.fi ) provide data like Total Value Locked (TVL) for

protocols and chains, historical TVL charts, yield farm rates, etc. According to the team, “Our API

is an open API and is free to use”
API (at  pro-api.llama.fi ) for higher rate limits and additional data, but the core data

 (with attribution appreciated). They also have a hosted Pro

7

remains publicly accessible

8

. The API documentation (listing endpoints such as getting all

protocols’ TVL, historical values, etc.) is available on the DeFiLlama site

9

.

•

Subgraphs & On-Chain Data: Internally, DeFiLlama gathers data from on-chain sources and The

Graph subgraphs. In fact, the project’s contribution guidelines state “The data must be fetched

from on-chain calls or from subgraphs. Centralised API calls are only accepted if there is no other way

of obtaining that data.”

10

. This means DeFiLlama aggregates many protocols’ subgraph data

(for protocols like Aave, Uniswap, etc.) into its own metrics. However, DeFiLlama does not

expose a GraphQL endpoint to end-users – instead it curates and serves the data via its REST

API and front-end.

•

Documentation & Repos: The DeFiLlama docs (docs.llama.fi) include FAQs and developer info.
They also maintain open-source GitHub repositories (e.g.  DefiLlama-Adapters  and  yield-

1

server ) that contain adapters for each protocol’s data collection logic

11

12

. These

repositories are a valuable resource to see how data is pulled (often via subgraph queries or

direct blockchain calls). The combination of open API + open-source adapters makes DeFiLlama a

transparent data source for analytics.

Aave

•

The Graph Subgraphs: Aave, being a DeFi lending protocol, provides subgraph endpoints for

querying its on-chain data. The Aave team maintains subgraphs on The Graph for various Aave

versions (v2, v3) and networks. These subgraphs index Aave’s smart contracts (covering lending

pool reserves, user positions, transactions, etc.) and expose a GraphQL API for developers. For

example, “The Aave Subgraph is a specialized data indexing tool built on The Graph… It indexes on-

chain data related to lending pools, user positions, reserves, and transactions, making it easier for

developers and analytics teams to build dashboards and tools without directly querying the

blockchain.”

13

. By leveraging The Graph’s decentralized indexing, developers can query current

and historical Aave data via GraphQL queries

14

. Access is through The Graph’s endpoints (e.g.

the Graph Explorer lists Aave subgraphs for Ethereum, Polygon, etc.).

•

REST API (Metrics): In addition to subgraphs, Aave has provided a RESTful stats API for certain

aggregated data. For instance, there have been API endpoints (hosted by Aave or third parties)
for getting total TVL, 24h volume, etc. (e.g.  https://aave-api-v2.aave.com/data/tvl  for

combined TVL). Documentation for such endpoints is not prominently published on the main

site, but community guides (like Cryptosheets and others) reference these endpoints

15

. This

API is more limited in scope compared to the subgraphs, focusing on high-level metrics.

•

Documentation and Code: Aave’s official developer docs (docs.aave.com) detail integration

steps and also link to resources like GitHub repositories for Aave’s smart contracts and the

subgraph definitions. For example, Aave’s GitHub contains the subgraph code (under the Aave or
Aave-Grants org) and the core protocol code (e.g.  aave-v3-core ). The docs site provides quick

links: “Resources: ... Subgraphs, JavaScript SDK, Source Code, Whitepaper”

16

. There isn’t an official

OpenAPI spec for Aave’s APIs (since most data is via subgraphs), but the GraphQL schema of the

subgraphs serves as the contract for data structure. In summary, source types for Aave include

The Graph subgraphs (primary), a docs site and SDK, and open-source code repos for reference

implementations.

Beaconcha.in

•

REST API with OpenAPI: Beaconcha.in is an open-source Ethereum 2.0 beacon chain explorer.
It provides a robust RESTful API ( https://beaconcha.in/api/v1/... ) that allows retrieval

of blockchain data such as epochs, slots, blocks, validators, and other consensus layer metrics.

The site explicitly offers an OpenAPI (Swagger) specification for its API: users can download the

spec as JSON or YAML

17

. The documentation introduction describes it as an “advanced and

reliable API for accessing comprehensive Ethereum blockchain data”

18

. This means developers can

programmatically get data on the Ethereum beacon chain similarly to how one would use a block
explorer’s API (with endpoints for things like  GET /block/{block_id} ,  GET /validator/
{validator_id} , etc.).

•

Free & Rate Limits: The API is free to use under a fair-use policy; there may be rate limits to

prevent abuse (the details are likely outlined in the documentation, e.g. a certain number of

requests per minute for free access).

•

Documentation and Tools: Beaconcha.in’s website includes an API docs interface (with the

OpenAPI UI for testing calls) and knowledge base articles. Because it’s an open-source explorer,

the source code for the explorer is on GitHub (Bitfly, the company behind beaconcha.in,

provides a link to “GitHub Explorer” in the footer

19

). This means the community can self-host or

inspect how data is being indexed. For our purposes, the source types from beaconcha.in

2

include the REST API (with a defined schema), the OpenAPI spec (for integration and validation),

and the open-source repo for the explorer.

Pendle

•

REST API: Pendle Finance (a DeFi protocol for yield tokenization) provides a Pendle V2 API for
developers. The base endpoint is  https://api-v2.pendle.finance/core , which offers

programmatic access to Pendle’s data and functionality. According to the docs, the API has a

default rate limit of 100 compute units per minute (to manage load) and supports multiple

categories of endpoints (core protocol data as well as auxiliary services like limit order books) –
for example, there’s a separate path for limit order API under  /limit-order/

. This API

20

allows developers to integrate Pendle’s yield markets (e.g. retrieving available yield pools,

trading data, etc.) into their applications. (The Pendle official docs note that the Pendle V2 API

documentation is forthcoming on their site

21

, but the endpoints are already live as evidenced by

their API base URL.)

•

The Graph Subgraphs: Like many DeFi protocols, Pendle also uses subgraphs for indexing on-

chain data. In fact, Pendle deployed over 40 subgraphs across multiple blockchains to power its

analytics and UI, illustrating the scale of data being indexed

22

. These subgraphs (which can be

self-hosted or accessed via services like Ormi or The Graph’s decentralized network) index

Pendle’s smart contracts for things like pool states, tokenized yield rates, user positions, etc. The
presence of “40+ subgraphs live” highlights that Pendle’s data infrastructure heavily relies on

GraphQL indexing for real-time data needs

22

. Developers could query these subgraphs (e.g.

Pendle’s mainnet subgraph on The Graph Explorer

23

) to get on-chain data if needed for

analytics beyond what the REST API provides.

•

Documentation and Repositories: Pendle’s documentation hub (docs.pendle.finance) provides

an overview of the protocol and an API reference (Pendle V2 API section). Additionally, Pendle’s

team has open-sourced parts of their stack: for instance, the subgraph definitions are available
on GitHub ( pendle-finance/subgraph-v3 )

. Their smart contracts and possibly SDKs are

24

also likely on GitHub. Thus, the source types for Pendle include a REST API (with official docs and

OpenAPI spec available via their endpoints), multiple GraphQL subgraphs, a documentation site

(Pendle Academy and developer guides), and open-source code repositories for both subgraphs

and contracts.

In summary,  these sources span multiple content types: JSON APIs (REST and GraphQL), developer

documentation websites, and code repositories/specifications. We have URLs and references for each:
), DeFiLlama API ( api.llama.fi
e.g. CoinGecko API ( api.coingecko.com/api/v3   with docs

1

with   docs
( beaconcha.in/api/v1  with OpenAPI spec

7

),   Beaconcha.in   API
), and Pendle API ( api-v2.pendle.finance/core

13

17

),   Aave   subgraphs   (accessible   via   The   Graph’s   endpoints

with docs in progress, plus many subgraphs

22

). Each source also involves metadata (like authors or

domains for docs, or code languages for repositories) and potentially semantic content (the topics of

documentation, etc.).

Below,   we   design   a   unified   schema   to   represent   data   from   all   these   heterogeneous   sources   in   a

consistent way for downstream processing.

Unified Data Class Schema Design

To integrate these various sources into a single analytics system, we define structured data classes

capturing the essential fields of each item (whether it’s an API endpoint spec, a documentation page, or

code snippet). We use  Pydantic  (Python data models) for runtime validation and  BAML  (Boundary AI

3

Markup Language) for LLM-friendly schema definitions, ensuring compatibility with our pipelines. The

schema is designed to support:

•

DLT-style loading & incremental updates: The schema can be used in a data loading pipeline

(e.g. Delta Live Tables or similar ETL) that repeatedly ingests new or updated data from each

source. By including identifiers, timestamps, and content length, the system can detect changes

and only process increments.

•

CocoIndex embedding & indexing: CocoIndex (an AI-focused ETL/indexing framework) can take

the structured data to generate embeddings (vector representations) for search. Fields like
topics  and  summary  (semantic enrichment) assist in creating meaningful embeddings and

allow filtering or faceted search in the index.

•

Agno multi-agent workflows: In the Agno agent framework, these structured records provide

context and memory. An agent can query the indexed data by topic or source type, use metadata
to decide which tool to invoke (e.g. if an entry has  openapi_refs , an agent could decide to call

that API), and ensure that responses include source attributions. The schema’s organization

(source, metadata, semantic, technical) gives the agent interpretable hooks to reason about the

information (for example, knowing an item is from “docs” vs “repo” might affect how the agent

uses it).

Below we present the schema in both Pydantic (Python) and BAML formats. These definitions model a

generic “DataItem” that can represent an API endpoint description, a documentation page, a code repo

file, etc., enriched with metadata and analysis.

Pydantic Data Model (Python)

from pydantic import BaseModel

from typing import List, Optional, Literal

from datetime import datetime

class SourceInfo(BaseModel):

url: Optional[str]

# Web URL or API endpoint, if applicable

path: Optional[str]
is from file system or git)

# Local file path or repository path (if data

type: Literal['api', 'repo', 'docs', 'video', 'blog', 'subgraph']

# ^ Type of source e.g. API, code repository, documentation site, video,

blog, subgraph, etc.

class Metadata(BaseModel):

length: Optional[int]

# Content length (e.g. number of

characters or lines)

author: Optional[str]

# Author or contributor (if known, e.g.

docs author or code committer)

domain: Optional[str]

# Domain of the source (e.g.

"coingecko.com" or general category like "DeFi")

date: Optional[datetime]

# Publication or last updated date/time

of the content

class SemanticInfo(BaseModel):

topics: List[str]

# Key topics or tags (e.g. ["DeFi",

"API", "Yield Farming"])

summary: Optional[str]

# A short summary of the content

4

(generated via LLM)

sentiment: Optional[str]

# Sentiment analysis of content (e.g.

"neutral", "positive") – more relevant for social/blog content

associated_software: List[str]

# Names of software/projects mentioned

(e.g. ["Aave", "Ethereum"])

class TechnicalDescriptor(BaseModel):

language: List[str]

# Detected languages in content (human

languages or programming languages)

code_snippets: Optional[List[str]]

# Extracted code snippets (if the

content contains code examples)

openapi_refs: Optional[List[str]]

# References to API endpoints or

OpenAPI spec components in text (e.g. "/v1/markets" or schemas)

compose_templates: Optional[List[str]] # Detected compose templates or

config snippets (e.g. docker-compose YAML fragments), if any

class DataItem(BaseModel):

source: SourceInfo

metadata: Metadata

semantic: SemanticInfo

technical: TechnicalDescriptor

content: Optional[str]

# The raw text content or a pointer to content

(could be the full text of a docs page, code file, etc.)

id: Optional[str]

# Unique identifier for this item (could be a

hash or a composite key, used for DLT incremental tracking)

Notes on the Pydantic model:  This schema is hierarchical. For each data item we store the origin
( source ),   factual   descriptors   ( metadata ),   semantic   annotations   ( semantic ),   and   technical
annotations ( technical ), along with the actual content or a reference to it. Some fields are optional

because they may not apply to all items (e.g. a code file might not have an “author” easily available, or a
piece   of   documentation   might   not   contain   any   code   snippet).   The   type   field   in   SourceInfo
categorizes the item’s origin, which is crucial for routing in pipelines (for example, if   type=="api" ,
the loader might use an HTTP fetcher, if  type=="repo" , use a git loader, etc.). The  date  in metadata

can be used for incremental loading (only pull or re-embed items updated after the last checkpoint).
The  id  field (which could be a combination of source URL or file path and maybe a version/timestamp)

would be used as a primary key in a DLT table or index – allowing updates to be applied idempotently.

This Pydantic model can be directly used in Python to validate incoming data (e.g. after scraping docs or
pulling API specs, we populate a  DataItem  and ensure it fits the schema). It’s also straightforward to

convert these models to dictionaries or DataFrames that CocoIndex can ingest. For instance, CocoIndex
could treat each  DataItem  as a row, and we could configure it to embed either the  content  or the
summary   (or both) for semantic search. The structured fields (topics, tags, source type) can serve as

filters or metadata in a vector database index (allowing an agent to ask, for example, “find documents
about  yield   farming  from  Pendle  docs”   –   which   could   be   matched   via   the   topics   and
associated_software  fields).

BAML Schema Definition

Below  is  the  equivalent  schema  expressed  in  BAML,  which  is  a  compact  schema  language  for  LLM

prompt alignment. This will guide an LLM (within the Agno agent framework) to output data in this

5

structured format or to parse content into this structure. BAML uses a syntax similar to class definitions,
with   optional   fields   denoted   by   ?   and   list   types   by   brackets.   Enums   could   be   used   for   fields   like
SourceInfo.type  for strict validation.

# BAML Schema for the crypto analytics data items:

enum SourceType { api, repo, docs, video, blog, subgraph }

class SourceInfo:

    url: string?

    path: string?

    type: SourceType

class Metadata:

    length: int?

    author: string?

    domain: string?

    date: string?  # ISO 8601 datetime as string

class SemanticInfo:

    topics: [string]       # list of topic tags

    summary: string?       # optional summary of content

    sentiment: string?     # e.g. "positive", "neutral", "negative"

    associated_software: [string]

class TechnicalDescriptor:

    language: [string]         # e.g. ["English"], or

["Solidity","JavaScript"] for code content

    code_snippets: [string]?   # code extracts if present

    openapi_refs: [string]?    # e.g. ["/v1/markets", "/coins/{id}"]

    compose_templates: [string]?  # e.g. docker-compose YAML snippets if any

class DataItem:

    source: SourceInfo

    metadata: Metadata

    semantic: SemanticInfo

    technical: TechnicalDescriptor
    content: string?    # full text or excerpt of the item

    id: string?         # unique identifier for reference

In this BAML schema, we defined   SourceType   as an enum to constrain   source.type   to known

categories (API, repo, docs, etc.). Each class field closely mirrors the Pydantic model. An LLM using this

schema will be  constrained  to output data that fits these classes, which greatly improves reliability

when   extracting   structured   information   from   unstructured   input   (or   when   formatting   answers).   For

example,   if   an   Agno   agent   is   prompted   to   summarize   a   new   piece   of   documentation   and   provide
structured output, BAML ensures the agent returns, say, a   DataItem   object with all fields (filling in
topics , generating a  summary , etc.). This determinism is crucial for robust pipelines – as noted in

discussions, BAML schemas can enforce 100% parseable outputs

25

26

, which the agent framework

can parse into Pydantic models directly.

6

Compatibility with Workflows: This schema design is aligned with the needs of each component:

•

Incremental Loading (DLT): Each  DataItem  can be upserted into a table or object storage. The
id  and  date  help identify new vs updated records. For example, if CoinGecko releases new
API endpoints, they would appear as new  DataItem  entries (perhaps with a unique ID derived

from the endpoint path) – the loader can pick those up and mark older ones as unchanged. The

lightweight nature of these classes means they can be easily serialized to JSON or Parquet for

pipeline use.

•

  DataItem   objects   and   apply
CocoIndex   Embedding:  CocoIndex   can   take   a   list   of
transformations like chunking and embedding. We might configure it to use   content   as the
text   to   embed   for   full-text   search.   Meanwhile,   semantic.topics   and   metadata.domain

can be stored as metadata alongside the vector embeddings (CocoIndex or the downstream

vector DB could use those for filtering). CocoIndex’s incremental indexing feature would benefit
from  date  and  id  – it can avoid re-embedding content that hasn’t changed, using the  id  to

retrieve existing vectors. This is in line with CocoIndex’s design which emphasizes incremental

processing and schema-based data alignment.

•

Agno Agent Usage: With all data indexed and retrievable, an Agno agent can utilize these classes

in multiple ways. The agent could have a tool to query the knowledge base (the CocoIndex) by
keyword   or   by   structured   query   (e.g.,   find   DataItems   where   source.type   ==   "api"   and
semantic.topics   contains   "TVL").   The   results   returned   to   the   agent   would   be   already
structured – the agent can read the  summary  field to quickly understand a document’s content,
or check   technical.openapi_refs   to decide if it should call an API. For instance, if a user

asks “How do I get Aave’s total TVL via API?”, the agent might: search the index for "Aave TVL
API", retrieve a DataItem that has  associated_software=["Aave"]  and topic "TVL" – which

might be the entry describing the Aave API endpoint or DeFiLlama’s relevant endpoint. Seeing
source.type="api"  and perhaps an  openapi_refs="/data/tvl"  in that item, the agent

could either present that info or actually use a tool to call the API (if integrated). The schema

ensures the agent always has context like which project a piece of data is about and what type of

content it is dealing with, which improves decision-making in multi-step workflows.

Finally, by using Pydantic and BAML together, we cover both  validation  in code and  prompt-format

validation for AI. We preserve citations and source attributions in our system as well – for instance, the
source.url  can link back to documentation (allowing an agent to cite the original docs like we did

here, e.g. CoinGecko’s docs

1

 or the Pendle case study

22

). This traceability is crucial in analytics and

AI agents to maintain trust and correctness of the information provided.

References:  The schema and approach are informed by the characteristics of the sources discussed

(CoinGecko API docs

27

, DeFiLlama FAQ

7

, Aave subgraph documentation

13

, Beaconcha.in API spec

17

, Pendle’s use of subgraphs

22

, etc.), ensuring that our design can accommodate data from each.

Each field in the model has a purpose aligned with real-world data points from these sources, making

the schema practical for implementation in a unified crypto analytics platform.

1

2

3

4

27

Introduction - CoinGecko API

https://docs.coingecko.com/

5

CoinGecko API: The Cryptocurrency Data Powerhouse | Zuplo Learning Center

https://zuplo.com/learning-center/coingecko-api

7

6

GitHub - coingecko/coingecko-api-oas: CoinGecko API — OpenAPI Spec (OAS)

https://github.com/coingecko/coingecko-api-oas

7

Frequently Asked Questions | DefiLlama

https://docs.llama.fi/faqs/frequently-asked-questions

8

API Docs - DefiLlama

https://api-docs.defillama.com/

9

DefiLlama API Server | Smithery

https://smithery.ai/server/@nic0xflamel/defillama-mcp

10

11

12

GitHub - DefiLlama/yield-server

https://github.com/DefiLlama/yield-server

13

14

Aave Subgraph by Aave Protocol | QuickNode

https://www.quicknode.com/builders-guide/tools/aave-subgraph-by-aave-protocol?category=subgraphs

15

How to pull AAVE Protocol API data into Excel and Google Sheets

https://docs.cryptosheets.com/providers/aave-protocol-api/

16

Aave V2 | Aave Protocol Documentation

https://aave.com/docs/developers/legacy-versions/v2

17

18

19

API Documentation - Open Source Ethereum Blockchain Explorer

https://beaconcha.in/api/v1/docs

20

Pendle V2 API Docs

https://api-v2.pendle.finance/core/docs

21

Pendle Documentation

https://docs.pendle.finance/

22

Case Study: Pendle Finance - How Ormi Fueled a $6 Billion DeFi Protocol

https://blog.ormilabs.com/how-ormi-powers-pendle-data-infra/

23

Pendle V2 Mainnet Subgraph | Graph Explorer

https://thegraph.com/explorer/subgraphs/ExXGU3ub2nrT5stPk5cH4hSk2qunJcMcP8eX5GAhrZhe?

view=Query&chain=arbitrum-one

24

pendle-finance/subgraph-v3 - GitHub

https://github.com/pendle-finance/subgraph-v3

25

26

Beating OpenAI structured outputs on cost, latency, and accuracy : r/LocalLLaMA

https://www.reddit.com/r/LocalLLaMA/comments/1esd9xc/beating_openai_structured_outputs_on_cost_latency/

8

