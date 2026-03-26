Building a Modern Data Stack: GraphQL,

LanceDB, DuckDB, Cognee & More

Overview: From Havona to a New Stack

Your friend's  Havona  platform is a  trade contract management  system built with cutting-edge tech

like Dgraph (GraphQL database) and blockchain. It features  dual persistence  (fast GraphQL queries via

Dgraph   plus   immutability   via   blockchain),   a  schema-first  approach   (GraphQL   schema   drives   code),

multi-tenancy, and a React/Flask web stack. In Havona, all data is defined in a large GraphQL schema

(~6k lines) and stored in Dgraph for real-time querying, with critical records also written to a blockchain

for audit trails

1

.

The proposed new stack aims to achieve the same goals – multi-tenant contract management with fast

queries and auditability – but by leveraging modern data tools and AI capabilities:

•

Graph Database: Replace Dgraph with an open Cypher-based graph DB (like Memgraph or

Neo4j) for structured relationships, due to Kùzu’s archival (more on this below).

•

Vector Database: Introduce LanceDB for semantic vector search over unstructured content

(e.g. contract text, communications).

•

Analytical DB: Use DuckDB (or PostgreSQL) for relational queries and analytics on tabular data

(e.g. reporting, aggregations).

•

AI Memory Engine: Integrate Cognee (with BAML for structured LLM output) to build a self-

updating knowledge graph and memory layer from raw documents.

•

Indexing Pipeline: Utilize CocoIndex and DLT (Data Load Tool) to ingest and transform data

from various sources into the above stores.

•

Auth & Full-Stack: Transition from Auth0 + Flask backend to BetterAuth (self-hosted auth) with

a TanStack Start + Hono TypeScript stack (React, Hono server, TanStack Router/Query, tRPC) for

a modern, type-safe frontend/backend architecture.

The goal is to show that this AI-powered, unified stack can cover Havona’s features while being more

intelligent (via semantic search and automated graph building) and more developer-friendly (with type-

safe TS and open-source tools).

Graph Databases: Dgraph vs. Kùzu vs. Memgraph (Neo4j)

Dgraph (used in Havona) is a distributed graph database with a native GraphQL interface. Its appeal is

that you define a GraphQL schema and Dgraph automatically provides a GraphQL API for querying and

mutating   data,   which   made   it   easy   to   build   Havona’s   schema-first,   real-time   API

1

.   Dgraph   also

supports multi-tenancy (namespacing) and is optimized for fast graph queries.

Kùzu was an embedded graph database (C++), often dubbed “the SQLite of graphs,” that implemented

the Cypher query language (the same query language as Neo4j)

2

. It came from academic research

and   boasted   features   like   full-text   search   and   vector   indexes   built-in

3

.   Unfortunately,   as   you

discovered, Kùzu’s open-source project was suddenly archived in Oct 2025 (the creators hinted they’re

“working   on   something   new”)

4

.   The   community   is   now   considering   forks   or   alternatives;   one

1

company forked it as  Bighorn, and another alternative mentioned is  FalkorDB

5

. The abrupt end of

Kùzu makes it risky to adopt for a new project.

Memgraph emerges as a strong alternative. It’s an in-memory graph database, fully Neo4j-compatible

(supports Cypher and the Bolt protocol). In fact, Memgraph’s goal is high-performance graph analytics

with the familiarity of Neo4j. Since it speaks Cypher, you can use Neo4j client libraries and even the

Neo4j GraphQL integration on Memgraph. Memgraph also has a focus on real-time graph updates and

features   like   triggers   and   custom   procedures   (via   Cypher   or   embedded   Python).   Importantly,

Memgraph has been  actively exploring AI use-cases  – their recent blog posts and community calls

show integrations with LLM-based systems (like Cognee) and even GraphQL bridges:

•

GraphQL Integration: Memgraph can be paired with the Neo4j GraphQL Library in a Node.js

server. This allows you to expose a GraphQL API on top of Memgraph, where GraphQL queries

get translated to Cypher under the hood

6

7

. For example, Apollo Server + Neo4j GraphQL

can connect to Memgraph and serve the same GraphQL schema that was used in Dgraph. This is

how you could retain Havona’s schema-first GraphQL approach: define the types (Contract, Party,

etc.) and use the library to handle data fetching from Memgraph.

•

Multi-Tenancy: While Memgraph (and Neo4j) don’t natively have tenant isolation like Dgraph’s
namespaces, a common strategy is to include an  orgId  field on nodes/relationships and apply

filters. The Neo4j GraphQL library supports auth rules where you can inject the tenant context
(e.g., only return nodes where  orgId = JWT.orgId ). Thus, you can achieve a secure

separation of data per organization similar to Havona’s design.

•

Performance: Memgraph is built in C++ and optimized for in-memory operation (with durability

options). It should handle the “fast, searchable” needs just as Dgraph did

8

. Cypher query

performance is generally good for well-indexed graph patterns. If needed, you can also use

Memgraph’s openCypher extensions or even write custom procedures in C/C++ for heavy logic.

In summary, Dgraph vs. Memgraph: Dgraph gave you GraphQL out-of-the-box and a great developer

experience   for   schema-driven   development,   whereas   Memgraph   gives   you   Cypher   and   integration

compatibility with Neo4j’s ecosystem. With a bit of additional setup (Apollo + Neo4j GraphQL library),

you can get the best of both worlds – a GraphQL API backed by Memgraph’s graph store. This approach

has been demonstrated in community examples (e.g., building a secure multi-tenant GraphQL API on

Memgraph

7

).

Additionally, using Memgraph means you align with  property graph standards  (Cypher/OpenCypher,

Bolt protocol), making your solution interoperable with Neo4j and other tools. This is advantageous

long-term, given Dgraph is a more niche technology and Kùzu is no longer maintained.

LanceDB & DuckDB: Vectors Meet Analytics

LanceDB  is an open-source embedded database optimized for  vector search  (similar to Pinecone or

Milvus, but lightweight). It uses an Apache Arrow-based columnar format (“Lance”) under the hood to

store embeddings efficiently

9

. Key features of LanceDB include:

•

Local Persistence: Data (embeddings, metadata) is stored in  .lance  files (columnar format),

enabling fast reads and writes, plus ACID properties for transactions.

•

Vector Indexing: It can build indices (like IVF, HNSW) for similarity search on embedding

vectors, for quick nearest-neighbor queries.

•

DataFrame-like Queries: You can treat LanceDB tables like dataframes or Arrow tables –

meaning you can filter by metadata, do vector similarity search, etc., using a Python or JS API.

2

•

Integration with Analytics Engines: Notably, LanceDB was built to integrate with tools like

DuckDB. Through the Arrow memory format, DuckDB can query LanceDB tables as if they

were regular tables

10

. DuckDB will push down projections and filters to LanceDB, minimizing

data copy, and can even stream results for large tables

10

. This means you could, for example,

run an SQL query that includes a vector search condition or join LanceDB results with other

relational data in DuckDB.

DuckDB is an in-process OLAP (analytical) relational database. Think of it as “SQLite for analytics” – it’s a

single-file DB you can embed in your app, optimized for large analytical queries (scans, aggregates,

joins on millions of rows)

11

12

. Some highlights of DuckDB relevant to our case:

•

It uses columnar storage and vectorized execution for speed on analytical workloads

13

.

•

Supports standard SQL (very close to PostgreSQL syntax) and can handle complex queries

efficiently.

•

Extremely versatile data integration: DuckDB can query data from many formats: Parquet,

CSV, JSON, even directly query remote data (S3, Google Cloud) or other databases. It also has an

Arrow integration to seamlessly interchange data with Pandas, Polars, and LanceDB

14

.

•

Because it’s embedded, there’s no separate server – your application or pipeline can instantiate

DuckDB and use it within the same process. This is great for running analytical tasks or

transformations as part of an ETL (which is why DuckDB is often used with tools like DLT).

In the new stack, LanceDB and DuckDB work hand-in-hand:

•

Semantic Vector Search: When a user needs to find relevant documents or passages (e.g. “find

all contracts mentioning force majeure”), LanceDB can be used to store embeddings of contract

texts. A similarity search in LanceDB will return, say, the top N relevant chunks with a similarity

score.

•

Hybrid Querying: By exposing LanceDB data to DuckDB, you could perform hybrid searches –

e.g., “find relevant contract clauses via embedding, but filter to those from 2023 and sort by

contract value”. The embedding similarity could be computed first, and then a DuckDB SQL

query can filter by a metadata field (year = 2023) on the Lance table

10

. DuckDB’s ability to push

down filters to Lance means this is efficient.

•

Analytics & Reports: Any structured data (like contract metadata, user info, transaction logs)

can reside in DuckDB or be loaded into DuckDB on the fly. You can then run analytical queries

(number of contracts per region, average contract value, etc.). DuckDB’s performance on large

scans is excellent

13

, and it can even handle fairly large data volumes on a single machine

(many millions of rows).

•

Graph + SQL: While Memgraph will handle graph traversal queries, sometimes you might want

to do set-wide operations that are easier in SQL. DuckDB could be used to run queries on data

exported from the graph. For instance, if you export nodes and edges to CSV or use Memgraph’s

CSV loading, DuckDB can crunch those. Conversely, DuckDB query results (like a list of contracts

matching certain criteria) could be used to drive a graph query or visualization.

Finally,  GraphQL  can be layered on these as needed. For instance,  Hasura  (a GraphQL engine) has a

DuckDB   connector   that   provides   instant   GraphQL   APIs   on   DuckDB   data

15

.   This   means   you   could

expose   any   DuckDB   tables   (or   even   DuckDB   “views”   that   query   LanceDB   or   Parquet)   via   GraphQL

without writing resolvers. For the graph DB, you’d use the Neo4j GraphQL library approach. If needed,

you can even federate these GraphQL schemas (though that adds complexity) or call one from the

other.   But   even   without   Hasura,   you   can   write   custom   resolvers   in   your   GraphQL   server   to   query

DuckDB using SQL. The key point: LanceDB + DuckDB gives you powerful data retrieval and can be

made GraphQL-accessible (or accessed via a TypeScript backend using an ORM/SQL client).

3

Cognee: AI Memory Engine for Knowledge Graphs

A centerpiece of the new stack is Cognee, an open-source AI memory engine

16

. Cognee is designed

to   address   a   critical   limitation   of   vanilla   RAG   (Retrieval-Augmented   Generation)   systems:  the   lack   of
persistent, structured memory. Traditional RAG (embed chunks -> vector search -> feed to LLM) often fails

to   be   reliable   and   misses   deeper   context

17

18

.   Cognee’s   approach   introduces   a  memory-first

architecture that marries vector embeddings with a knowledge graph:

•

Ingestion & Enrichment: Cognee can ingest data from 30+ sources (text files, PDFs, databases,

etc.) via its pipeline. For each document or data source, it performs two parallel enrichments:

•

Semantic Embeddings: It generates vector embeddings for chunks of the content (for broad

semantic search).

•

Graph Extraction (Memification): It uses LLMs to extract structured facts in the form of triplets

(Subject–Relation–Object). Essentially, it’s turning unstructured text into nodes and relationships

for a knowledge graph

19

. For example, a contract document might yield triples like (Company

A) —[signed]→ (Contract X) or (Contract X) —[hasClause]→ (ForceMajeureClause).
Knowledge Graph Storage: These extracted entities and relations are stored in a graph

•

database (Cognee supports Neo4j, Memgraph, or even an in-memory NetworkX graph). The

graph provides structured, precise memory – you can query it for specific connections (e.g.,

find all contracts between Company A and B, or get the chain of related contracts).

•

Vector Store Integration: Cognee pairs the graph with a vector store for embeddings. While

Cognee originally demonstrated with vector DBs like Pinecone or simple in-memory indices, in

our stack we can use LanceDB for this. Cognee treats vectors and knowledge graphs as

complementary

20

: vectors give semantic similarity (recall), and graphs give factual relational

recall (precision).

•

Querying: Cognee provides a developer-friendly API to search this memory. A query can

combine time filtering, graph traversal, and vector similarity

21

. For instance, when you ask a

question, Cognee might first find relevant nodes via vector search, then traverse the graph

around those nodes to gather connected information, and even apply reasoning.

•

Reasoning Layer: Notably, Cognee has a natural language query layer that hides the complexity

of languages like Cypher

22

. This means a user (or developer) can pose a question in plain

English, and Cognee will translate that into the appropriate graph + vector operations to retrieve

an answer. This is ideal for building an AI assistant on your data.

•

Persistent Memory & Learning: Cognee’s philosophy is to make AI memory persistent and

self-improving. Over time, as more queries are answered, Cognee can use feedback to adjust

which nodes are connected or how it interprets data. The Memgraph integration in particular

has shown auto-optimizations: e.g., Cognee can prune unused nodes or optimize the graph

(“Memphis” algorithms)

23

.

•

BAML Integration: BAML (from BoundaryML) stands for “Build, Analyze, Model, and Learn”, but in

context here it specifically refers to structured output for LLMs. BAML provides a DSL to

enforce type-safe, validated outputs from LLMs

24

. Cognee + BAML means when Cognee

prompts an LLM to extract a knowledge graph from text, the LLM’s output is constrained to a

schema/format (like JSON with specific fields)
hallucinations in the graph creation process – ensuring that, say, an  Agreement  node has the

. This dramatically reduces errors and

25

required properties, or that relationships use allowed types. In practice, BAML gives you compile-

time or runtime validation of the AI’s output, so you don’t blindly trust the LLM. This is crucial for

production quality: it “validates schemas, cuts errors at scale”

24

 when building the AI-

enriched knowledge graph.

•

Example: If Cognee is ingesting a contract, it might use an LLM (with a prompt crafted to extract

parties, dates, terms, etc.) to produce a JSON of entities. BAML can enforce that the JSON
matches a Pydantic or TypeScript type definition for, say,  Contract { id, parties:

4

[Party], effectiveDate, clauses: [Clause] } . If the LLM output doesn’t conform,

BAML will flag it or try to correct via few-shot examples. This is akin to how Havona used

Pydantic for validation, but here the validation is happening on AI-generated content.

By integrating Cognee, your system gains an  intelligent memory layer  that Havona lacked. Havona

would store what users entered (structured data) and could query it via GraphQL, but it wouldn’t infer

new knowledge  or handle unstructured text well. With Cognee, you can ingest not just form data but

entire documents and have the system understand and interlink them. For example, Cognee could take

a PDF of a contract and automatically populate the graph with its key entities and relationships. This

could   save   manual   data   entry   and   reveal   connections   (like   “these   two   contracts   involve   the   same

supplier”) that might not be obvious.

Key Benefits of Cognee for your use-case:

•

Better Recall & Precision: Cognee’s approach yields ~90% accuracy on QA in tests, versus ~60% for

standard RAG

26

. Users can ask complex questions (even follow-ups) and get reliable answers

that consider both relevant text (via vector search) and factual links (via graph traversal).

•

Dynamic Updates: The knowledge graph updates as data changes. Cognee’s pipelines support re-

ingestion and even partial updates. It treats memory as dynamic – exactly what a frequently

evolving trade platform needs (contracts get amended, new parties join, etc.).

•

Interoperability: Cognee can work with Memgraph (as proven in their Memgraph community

demo) and can also connect to your LanceDB vectors. It’s a glue that ties together our chosen

components into a cohesive “brain”.

•

Developer Experience: As a Python SDK, Cognee might run as a microservice or background job in
your system. You can script  cognify.add()  to ingest data and  cognify.search()  to query

27

. There’s also a local UI ( cognee ui ) for visualizing the graph and memory if needed

28

.

This means during development, you can quickly test how the memory is building up.

To   summarize,  Cognee   will   elevate   your   platform   from   a   CRUD-style   system   to   an   intelligent

assistant for trade contracts. It will enable features like natural language querying, automated knowledge

base   creation,   and  self-healing   data   links  that   can   significantly   improve   user   experience   and   insight

generation. And by using BAML with Cognee, you ensure the AI’s contributions remain reliable and

schema-consistent, which is critical in a domain like contracts where correctness matters.

CocoIndex and DLT: Ingestion & Indexing Pipelines

Getting data into this new stack is a challenge in itself – you have multiple target stores (graph, vector,

relational). This is where  CocoIndex  and  DLT  come in, to automate and streamline the ingestion and

indexing process:

•

CocoIndex (from cocoindex.io) is described as an “ultra-performant data transformation framework

for AI”

29

. It’s like an ETL toolkit specialized for building AI indexes. Some key points:

•

It’s written in Rust (with Python bindings), so it’s very fast at processing data streams.

•

It supports real-time, incremental indexing – meaning it can watch a source (like a folder or

database) and update the index in low-latency as things change

30

.

•

It has built-in components for common tasks: e.g., code indexing (using tree-sitter to parse

code, as mentioned in their blog

31

), document chunking, and connecting to vector stores or

knowledge graphs

32

.

•

CocoIndex can be seen as complementary to Cognee: while Cognee focuses on the AI

interpretation (embeddings, graph from text), CocoIndex focuses on the plumbing – it will take

data from source A, transform it with function B (which could be an LLM call or embedding

5

model), and send it to storage C. For instance, CocoIndex could manage a pipeline that reads

new documents from an S3 bucket, splits them into sections, calls an embedding model for each,

and upserts those into LanceDB (and simultaneously could call Cognee for graph extraction).

•

Using CocoIndex ensures your indexes (vector and graph) remain in sync with the source data.

It   addresses   one   pain   of   many   AI   apps:   when   source   data   updates,   re-indexing   is   needed.

CocoIndex can do  incremental updates  rather than rebuilding from scratch, which is a huge

time saver for large data.

•

DLT   (Data   Load   Tool)  is   an   open-source   Python   library   for   data   loading   (by  dlthub).   It   is

essentially an easy-to-use framework for building ELT pipelines, supporting sources like APIs,

databases, files, etc., and destinations like data warehouses or lakes. Why DLT in our context?

•

Simple Pipeline Definition: In a few lines of Python, you can define a pipeline that reads from a

source and writes to a destination. For example, the DLT docs show creating a pipeline that loads

a list of Python dicts into DuckDB in just a couple of lines

33

34

. You can incrementally load and

even handle schema evolution.

•

Destinations: DLT natively supports writing to DuckDB (as well as BigQuery, Redshift, Postgres,

etc.)

35

. So you could use it to populate DuckDB with structured data (like initial contract

records, or reference data like country lists). It can also call custom loading logic – for instance,

writing to Memgraph via its Bolt protocol, or calling LanceDB’s Python API.

•

Orchestration: DLT can serve as the orchestrator that ties CocoIndex and Cognee together. You

might write a DLT pipeline with steps such as:

1.

Extract: Pull data from an external source. This could be reading existing contracts from a

legacy database or CSV (for initial seeding), or connecting to an API (if, say, contracts

come from a SaaS).

2.

Load to Staging: Insert the raw data into DuckDB (staging tables). DLT will manage this
easily (e.g.,  pipeline.run(data)  as in the docs

).

33

3.

Transform & Index: Now call out to CocoIndex/Cognee. For each new or updated item,

invoke Cognee’s ingestion with BAML to update the knowledge graph and LanceDB. This

could be done in Python inside the DLT pipeline, since Cognee has a Python SDK.

Similarly, use CocoIndex if needed for things like code or more complex transformations.

Essentially, this step is where unstructured data becomes embeddings and graph entries.

4.

Load to Graph/Vector: The output of the above (embeddings, triples) needs to be

persisted. You can use LanceDB’s Python API to upsert vectors, and Memgraph’s client

(e.g., Neo4j Python driver pointed at Memgraph) to write the triples as Cypher

statements. This is custom, but straightforward: Cognee might even do the graph
insertion for you when you call  add_data_points()

36

.

5.

Verification: Optionally, the pipeline can verify that the data in Memgraph and LanceDB

is consistent, or run a quick query (like ask Cognee a sample question) to ensure things

are wired correctly.

•

Scheduling/Automation: DLT can be run on a schedule or triggered by events, making it easy to

keep data fresh. For example, run nightly to pick up any new contracts or modifications, or

trigger it via a webhook when a new document is uploaded.

6

In essence, CocoIndex + DLT = your AI-aware ETL/ELT system. Instead of writing a bunch of custom

scripts or manual upload processes (which can be error-prone), you define pipelines that ensure data

flows where it needs to:

•

New structured data (like a new trade entered via a form) can go into Memgraph (as graph

nodes) and DuckDB (as a relational record for analysis) immediately via an API call, and could

also be sent through Cognee for any textual fields that need embedding.

•

New unstructured data (like an attached PDF contract or an email thread) can be picked up by

CocoIndex, processed by an LLM for relevant info, and inserted into both LanceDB and

Memgraph so it’s instantly searchable.

•

Because DLT and CocoIndex are both open-source and have active communities, you will find

tutorials for common tasks. For instance, CocoIndex has a tutorial for indexing a codebase

37

or documents. DLT has guides for loading from APIs, databases, etc. Using these, you can speed

up development (no need to reinvent data ingestion).

Is GraphQL needed for indexing? Not really – GraphQL shines as a query language for clients, but for

the back-end ingestion, tools like DLT and CocoIndex are more appropriate. They’ll operate through

Python/Rust and connect directly to the databases. GraphQL could be used to trigger an ingestion (e.g.,
a mutation like  ingestContract(id: X)  that kicks off a pipeline), but the heavy lifting will be done

by the pipeline code. In fact, since Cognee and CocoIndex handle the index building, you might only use

GraphQL on the retrieval side, not on the ingestion side.

Do We Still Need GraphQL? How It Fits In

Given this new architecture, it’s natural to question the role of GraphQL. On one hand, Havona was

heavily   centered   on   GraphQL   (every   data   access   was   GraphQL,   with   Dgraph   auto-resolving   those

queries). On the other hand, we now have powerful indexing and search capabilities that could bypass

traditional queries (e.g., a user might just ask a question and get an answer via Cognee, without writing

a GraphQL query). Let’s consider where GraphQL is useful vs optional:

•

Structured Data Access: For many app features, you still need to retrieve structured data to

display in a UI (think of a contract details page, or a list of contracts). GraphQL excels here by

allowing clients to specify exactly what fields they need. You can absolutely retain a GraphQL API

for these operations:

•

Use the Neo4j GraphQL Library with Apollo Server to map GraphQL queries to Memgraph (which
stores most structured data). For example, a GraphQL query  { contract(id: "123")
{ title, parties { name }, value } }  could be resolved by Cypher on Memgraph,

returning those fields. The Neo4j GraphQL integration can auto-generate the Cypher for basic

queries and even support filters, pagination, etc., similar to Dgraph’s GraphQL (with a bit more

configuration)

6

.

•

Hasura or a custom GraphQL schema can cover any relational data in DuckDB/Postgres. If you

have some data in Postgres (say user profiles or org settings), Hasura can expose that instantly.

For DuckDB, Hasura’s DuckDB connector can even expose Parquet or in-memory tables via

GraphQL

15

. This means even if some analysis result is materialized as a DuckDB view, you

could query it from the frontend with GraphQL.

•

AI/Vector Queries: GraphQL isn’t the best language to express “find me similar vectors” or “do a

natural language search”. Those queries are better handled by Cognee’s API or a dedicated

endpoint. However, you can still integrate the results into GraphQL if needed. For instance, you
could have a GraphQL query field like  searchContracts(query: String!):
[ContractSnippet]  which under the hood calls a LanceDB similarity search (and maybe

Cognee) and returns a list of snippets or contract references. The resolver for this field would be

7

custom code (not auto-generated) – it might call  lancedb.search(queryEmbedding)  and

then fetch the corresponding contract info from Memgraph or DuckDB. This way, the front-end

gets a structured response (an array of results with contract ids and snippet text) via GraphQL,

even though the logic used embedding search.

•

Direct GraphQL vs tRPC/REST: Since you are considering a TanStack-based full-stack, an

alternative to GraphQL is tRPC (procedural calls with type safety) or simple REST+React Query.

TanStack Query will work with any API. If you feel GraphQL adds complexity, you could

•

implement the data fetching as REST endpoints or tRPC functions:
e.g.,  GET /contracts?orgId=X  returns list of contracts,  GET /contract/123  returns
details,  GET /search?query=...  returns search results. This is straightforward with Hono (a

lightweight server) and you can still ensure type safety using something like zod or tRPC.

•

tRPC would allow you to call backend functions directly from the front-end with full TypeScript

type matching (no need to manually write fetch calls or GraphQL queries). It’s great for

developer productivity in a monorepo setting.

•

The downside of dropping GraphQL entirely: you lose the powerful querying capability on the

client side. If the UI needs to flexibly get nested related data, you’d have to create specific

endpoints for those cases, or do multiple calls. GraphQL, especially with the auto-generated

resolvers on Memgraph, can handle arbitrary queries (within what the schema allows) without

additional backend code for each pattern.

•

GraphQL with Cognee: Interestingly, Cognee itself doesn’t expose GraphQL (it has its own API/

CLI), but you might not need it to. You could have your GraphQL layer call Cognee’s Python

functions internally. Another idea: if you want to expose the knowledge graph in GraphQL, you

could map parts of Cognee’s output to GraphQL types. For example, define a GraphQL type
Entity  with fields that correspond to properties in the Cognee graph. However, this may be

unnecessary given Cognee’s focus on semantic retrieval rather than user-driven querying of the

raw graph.

Bottom   line:  GraphQL   is   still   very   useful   for   building   your   application’s   API,   especially   to   leverage

existing   front-end   components   and   to   maintain   a   clean   separation   of   concerns.   You   can   absolutely

incorporate it by using libraries that connect it to Memgraph (for graph data) and DuckDB/Postgres (for

relational   data).   The   fact   that   Memgraph   is   Neo4j-compatible   means   you   inherit   the   robust  Neo4j

GraphQL ecosystem  – e.g., the Neo4j GraphQL toolbox can even auto-generate filtering, pagination,

and has support for @authorization directives to implement auth rules at the schema level.

However, GraphQL is not mandatory if you prefer an alternative. Since you plan to use TanStack Start

(which often pairs with tRPC), you might choose to implement a pure TypeScript RPC layer. This could

simplify development (no need to maintain a separate GraphQL schema if you define TS types and

reuse them). It’s a matter of preference and the expected client usage. If you want to reuse the existing

React app’s GraphQL queries, it might be faster to provide a compatible GraphQL API. But if you’re

doing a fresh front-end, tRPC/REST could be equally effective.

One   scenario:   you   could   even   have  both  –   use   GraphQL   for   data-intensive   querying   (search   and

complex filters via Hasura or Apollo), and use tRPC for simpler or highly interactive operations (like a

form submission that triggers multiple actions). This is more complex, so likely you’d pick one primary

approach.

To  directly  answer  “with  indexing,  is  GraphQL   still   necessary?”  –  If   your  UI   will   benefit   from  the

structured data queries (which it likely will, for things like lists, detail views, etc.), GraphQL is still very

useful. The indexing enhancements (Cognee, vector search) operate mostly behind the scenes or via

specialized   endpoints;   they   don’t   eliminate   the   need   for   an   API   layer   to   get   data   to   the   front-end.

GraphQL can coexist with these, often acting as the aggregator of results (e.g., one GraphQL query

8

could combine graph data and a vector-search result). On the other hand, if your vision is an AI-driven

interface where users primarily ask questions to a chatbot agent, then GraphQL becomes less central –

the agent would use internal APIs to fetch info. But for a typical web app interface, you’ll likely have a

mix of both: traditional GraphQL/tRPC queries for structured data and new AI endpoints for semantic

queries.

Authentication & Full-Stack Modernization (BetterAuth,

TanStack, Hono)

Havona uses Auth0 for auth with organization-based access control. Auth0 is convenient but introduces

external   dependencies   and   costs,   and   might   not   fit   well   with   a   self-hosted   stack.   The   proposed

alternative   is  Better   Auth  integrated   with   a  TanStack   Start  monorepo   and  Hono  server,   which

dramatically changes the stack from Flask/React to full-stack TypeScript.

Better   Auth  is   a   headless   authentication   solution   that   provides   the   building   blocks   for   auth   (user

accounts,   sessions,   OAuth,   etc.)   that   you   can   host   yourself.   It’s   designed   to   integrate   with   modern

frameworks: React, Next.js, and indeed TanStack Start + Hono are explicitly supported

38

. Essentially,

BetterAuth offers an API and client library for all common auth flows (signup, login, forgot password,

token   refresh)   without   locking   you   into   a   particular   UI   –   you   can   use   your   own   forms   or   their

components.

Key advantages of BetterAuth in this context: - Self-Hosted: You control the user data (likely stored in a

database you choose, e.g., Postgres or even SQLite). This can be important for on-prem deployments of

your app. -  Framework Integrations: It has middleware for Hono (to protect routes, check sessions)

and hooks for React. So instead of the Auth0 SDK, you’d use BetterAuth’s hooks to get the current user,

etc. - Multi-Tenancy: BetterAuth can be extended to include organization info in the user profile or JWT.
You   might   issue   JWTs   that   have   a   claim   like   orgId ,   which   you   then   use   in   your   GraphQL/tRPC

authorization logic. This is similar to how Auth0 would include custom claims for a user’s organization.

TanStack   Start  isn’t   a   single   library   but   rather   an   example   stack   that   uses   the  TanStack  family   of

libraries to create a full-stack app. Typically, this includes: - TanStack Router: A new type-safe router for

React  (an  alternative  to  React  Router)  that  plays  well  with  data-loading  and  SSR.  -  TanStack  Query

(formerly React Query): for data fetching and caching on the client. It can work with GraphQL, REST,

tRPC – any async source. - tRPC: A typesafe RPC framework to call backend functions directly from the

front-end, using TypeScript type inference. This removes the need to manually define a REST schema or

GraphQL for those calls. -  Hono: A ultrafast web framework that can run on Deno, Bun, Cloudflare

Workers,   etc.,   as   well   as   Node.   It’s   like   Express.js   but   with   a   focus   on   performance   and   modern   JS

runtime support. Hono can serve as your backend server (handling HTTP requests, including tRPC calls,

GraphQL if you mount an Apollo server, static file serving for the frontend, etc.). -  Drizzle ORM with

libSQL: Many TanStack Start templates use Drizzle (a typesafe SQL query builder/ORM) with libSQL (an

updated, cloud-friendly fork of SQLite). This gives you a lightweight database for the backend to use

(which could store auth data, and any other small tables). LibSQL with something like  Lightning  (for

replication) can even serve as a serverless DB. In our case, we might use Postgres instead, but Drizzle

can work with Postgres as well.

There’s a community template called  Better-T-Stack  (by AmanVarshney01) which combines  TanStack

Router + Hono + tRPC + React/Vite + Tailwind + BetterAuth + Drizzle/libSQL

39

40

. This is essentially what

you   described:   a   monorepo   where   both   frontend   and   backend   are   in   one   codebase,   written   in

TypeScript, sharing code where appropriate (like model definitions, validation schemas, etc.). Adopting

this template or a similar setup would give you a huge head start in scaffolding the new application.

9

Transitioning from the old stack to this:

•

Frontend: The existing front-end is React/Vite with Apollo (GraphQL) and Auth0. The new front-

end will still be React (so you can potentially reuse UI components) but will use TanStack Router

for navigation and TanStack Query (or tRPC hooks) for data. Instead of Auth0’s SDK, you’ll use

BetterAuth’s React hooks to manage auth state. This means some rewiring of the context

providers at the app level, but conceptually it’s similar (Auth0 gave you a context with user, login/

logout methods; BetterAuth will do likewise).

•

Backend: The Flask Python backend’s responsibilities (GraphQL server, business logic, calling

Dgraph, calling blockchain, etc.) will be reimplemented in Node/TypeScript:

•

If you use GraphQL, you might spin up an Apollo Server in the Hono app (Hono can mount any

standard Node request handler). Apollo would use the Neo4j GraphQL library to interface with

Memgraph, plus custom resolvers for LanceDB or others.

•

In addition, you’ll implement any non-GraphQL endpoints (for example, file upload endpoints, or

a webhook to trigger DLT pipeline runs) in Hono.

•

The blockchain writing logic from Havona can likely be dropped initially (since you’re not

focusing on crypto). If needed, you could later introduce an on-chain component or simulate it

by using a tamper-evident log in Postgres. But given you lack blockchain knowledge and it’s not

central to the new features, it’s reasonable to omit it at first.

•

One important piece is Pydantic validation was used in Havona for type-safe processing. In the

TS world, you can achieve similar safety using TypeScript types and possibly Zod schemas or io-

ts. If using tRPC, you’d define input schemas for each procedure (often with Zod) which ensure

the data matches the expected shape. If using GraphQL, the GraphQL schema’s types plus

maybe runtime checks serve that role. So you will replicate the strong validation in a different

form.

•

Auth integration: BetterAuth will require a backend component (BetterAuth server or functions)

that interfaces with a database. You might run a small BetterAuth server (or possibly it can run

within Hono, depending on the deployment mode) which handles the heavy lifting of verifying

passwords, sending emails (if needed), etc. Then Hono can protect routes by verifying the

session token. On the front-end, after login, you’ll have a session cookie or JWT that TanStack

Query/tRPC will automatically include in requests (BetterAuth likely handles this via cookie or

header).

Overall Benefits of this Full-Stack approach:

•

Unified Language & Types: Everything is in TypeScript now. This means you can share types
between frontend and backend (e.g., define a  Contract  type once and use it for GraphQL

schema or tRPC and for frontend props). This reduces mismatch errors and the cognitive load of

switching between Python and JS.

•

Performance: Running on Hono (which can leverage edge runtimes) and an in-memory graph

DB (Memgraph) can be extremely fast. React with TanStack Query will give a snappy UX with

efficient caching. You might also deploy the frontend as a static bundle (since Vite can produce

that) served by a CDN, with the Hono API on edge functions for low latency global access.

•

Developer Experience: Hot reloading, a single dev server for full stack, and the rich TanStack

ecosystem (which includes devtools for queries, router introspection, etc.) make building and

debugging easier. BetterAuth removes the need to go to an external portal (Auth0) to manage

users – you could build your own admin panel for user/org management if needed.

One   thing   to   plan   is  data   storage   for   BetterAuth:   It   will   need   a   place   to   store   user   accounts,

passwords (hashed), and possibly session info. A simple approach is to use SQLite/libSQL via Drizzle (as

the template does). If you anticipate many users or want stronger consistency, using PostgreSQL for

BetterAuth would be fine too. Since you already consider using Postgres for some parts, you could

10

consolidate on Postgres: Memgraph for graph, LanceDB (files) for vectors, and Postgres for auth and

any miscellaneous data (analytics could still go to DuckDB, or you might choose to use Postgres for that

too, though DuckDB is much faster for heavy reads).

Migration: You won’t directly “migrate” Auth0 users easily (unless you export them and import into

BetterAuth, which might be possible if you can get a CSV of users from Auth0). If you can’t migrate, you

might have users re-register in the new system. Since this is a prototype to convince your friend, that’s

not a big issue initially (just use test accounts).

In summary,  BetterAuth + TanStack + Hono  will give your project a  modern, modular foundation.

This aligns with the “Modern Stack” point of Havona, but pushes it even further (fully open-source stack,

no external auth, no Python backend). It’s a significant shift, but the result is a more maintainable and

scalable codebase.

The React/Vite UI can be largely reused, but adapted from Apollo GraphQL to TanStack Query or tRPC

hooks. You’ll also integrate new UI elements to showcase the AI features (e.g., a search bar that uses

Cognee, or a Q&A chat widget). Fortunately, the React ecosystem has many components for chat UIs or

you can build a simple one.

By following patterns from the Better-T-Stack template

40

, you ensure that BetterAuth, Hono, React,

tRPC, and Tailwind all work nicely together from day one, saving setup time and letting you focus on

implementing features specific to your domain.

How the Pieces Work Together

Let’s paint a picture of an end-to-end flow in the new system, demonstrating how these technologies

interact:

1.

Data Ingestion Example: Suppose a new trade contract is added.

2.

The user uploads a contract document (PDF) and fills a form with key metadata (parties, dates,

values) in the React app.

3.

Frontend: The form submission goes through BetterAuth’s session (so we know the org/user).

The data is sent via tRPC or GraphQL to the backend.

4.

Backend (Hono): Receives the request. It first stores the structured metadata:

◦

◦

Perhaps a Cypher query is executed to create a  Contract  node in Memgraph with
properties from the form (and link it to  Party  nodes for each counterparty, etc.).
Also, an entry is added to DuckDB/Postgres (e.g., an append to a  contracts  table) for

analytical use.

◦

If using a blockchain or audit log, that could be invoked here too (but we assume not for

now).

5.

Next, the document file is passed to the ingestion pipeline:

◦

You might enqueue a background task (like calling a DLT pipeline or Cognee ingestion

asynchronously). This task would use CocoIndex/Cognee to process the PDF. For

example, use a PDF parser to extract text, then Cognee with LLM to find structured facts

in it.

◦

Cognee (with BAML) processes the text and identifies, say, clauses and obligations,
adding those as nodes/edges in Memgraph connected to the  Contract  node

41

. It

also generates embeddings for each section of text and stores them in LanceDB.

11

◦

CocoIndex could help here by splitting the PDF into chunks and calling an embedding

model (like OpenAI or Cohere via LanceDB’s integration)

42

. It ensures all chunks get

indexed in LanceDB with metadata (like contract ID, page number).

6.

When this pipeline completes, the knowledge graph and vector index are updated with the new

contract’s data.

7.

Data   Retrieval   Example   –   Structured:   Now   the   user   wants   to   view   a   list   of   contracts   or   a

contract detail.

8.

The React app calls the appropriate API (GraphQL query or tRPC function) for
getContracts(orgId) .

9.

Hono verifies the JWT (via BetterAuth middleware) to ensure the user has access, then executes:
If GraphQL: Apollo resolves the query by fetching from Memgraph (e.g.,  MATCH
(c:Contract { orgId: X }) RETURN ...  for list, or a specific contract by ID). The

◦

Neo4j GraphQL library can auto-generate this logic for basic filters.

◦

If tRPC: Your handler might query Memgraph via its TypeScript client (Memgraph can be

accessed with the Neo4j JavaScript driver since it’s Bolt protocol compatible). Or, if you

stored a copy in Postgres, you could just query that. But Memgraph will have the latest,

richest representation.

10.

The result is sent back as JSON, and the frontend displays the contract list or details.

11.

Data Retrieval Example – Semantic Search: The user uses a search bar to find contracts related

to   “force   majeure”   or   asks,  “Which   contracts   signed   in   2023   have   a   clause   about   pandemic

response?”.

12.

The query goes to a specialized endpoint (maybe a GraphQL query
searchContracts(query)  or a REST endpoint  /search ).

13.

Backend logic:

◦

First, the LanceDB vector index is queried for the embeddings of “force majeure” or

related terms. LanceDB returns, say, the top N clause texts or contract snippets that are

similar

19

.

◦

◦

Those results contain references (like contract IDs and clause IDs stored as metadata).

Next, the logic might query Memgraph: for each contract that came up, fetch the

contract’s metadata (title, date, parties) and maybe traverse one hop out to get related

info (e.g., if the question involves a date filter, check the contract’s date property; if it

involves a concept like “pandemic response”, maybe the graph has that tagged).

◦

Alternatively, you hand the whole query to Cognee’s reasoning layer: Cognee can parse

the natural language question, realize it needs to filter by year = 2023 and concept =

pandemic, and do a combined graph+vector query internally

21

. It could return a direct

answer or a set of relevant nodes.

◦

Suppose Cognee returns a set of relevant contract nodes (with some score or reasoning).

The backend then formats that into a response.

14.

Frontend: Receives a list of matching contracts or even a composed answer (like “Contract

ACME-2021 includes a pandemic clause on page 5…”). The UI shows the results, possibly with

confidence scores or highlights of why it matched (thanks to the snippet text from LanceDB).

15.

The user clicks a result, which then loads the contract detail via the structured API as usual.

16.

Auth and Org Control: All the above queries and mutations are automatically scoped to the

user’s organization:

12

17.

18.

When the user logged in via BetterAuth, they got a JWT with their  orgId .
The backend uses this  orgId  in queries (either via GraphQL auth rules or manually in Cypher/
SQL  WHERE  clauses). For example, the Memgraph query might ensure  MATCH (c:Contract
{orgId: 123})  so only that org’s contracts are returned. This mirrors Havona’s namespace

isolation

43

, but implemented at the application level.

19.

BetterAuth also provides user role info if needed (e.g., admin vs viewer) so you could enforce

that certain mutations (like deleting a contract) are only allowed for certain roles.

20.

Audit & History: Without blockchain, you still want an audit trail of changes.

21.

Each time a contract is edited, you can record the old version either in the graph (e.g., keep an
archival node or a version property) or in DuckDB/Postgres (a  contracts_history  table with

timestamp, changed fields, etc.). This approach can satisfy regulatory compliance for change

tracking

8

. It’s simpler than on-chain storage but can be made tamper-evident by, say, hashing

the records or writing periodic hashes to a public ledger if really needed.

22.

If needed, Cognee could even be used to store these events in a graph form (like an Event node

connected to the Contract). The advantage is you could ask the system questions like “When was

this field last changed and by whom?” and get an answer by traversing those event nodes.

Through this example, you can see every component working in concert: -  Memgraph  holds the core

structured   data   and   relationships   (quick   retrieval   via   GraphQL/Cypher).   -  LanceDB  holds   semantic

embeddings for deep search. - DuckDB/Postgres holds any structured tabular data and can be used for

heavy analytics or auditing. -  Cognee  ties Memgraph and LanceDB together to provide an intelligent

query  interface  and  continuously  enriches  the  graph  with  new  insights  from  text.  -  DLT/CocoIndex

ensure   data   flows   into   those   systems   reliably   whenever   new   input   arrives.   -  BetterAuth   +   Hono   +

TanStack  provide   the   scaffolding   to   glue   the   front-end   and   back-end,   handle   auth,   and   deliver   a

responsive UI.

Conclusion: A Blueprint for the Enhanced System

This deep dive has outlined a vision for a  next-generation software stack  that is both  feature-rich

and  future-proof. Here’s a brief summary of how it improves upon your friend’s Havona system and

some guidance on moving forward:

Improvements & Key Features:

•

Unified Knowledge Base – By combining a property graph (Memgraph/Neo4j) with a vector

store (LanceDB), the platform can handle both explicit facts and fuzzy semantic search. This

dual capability means users can retrieve exact structured data and discover hidden connections

or relevant documents by context

20

19

. In contrast, Havona’s pure GraphQL+Dgraph

approach required knowing the exact query structure upfront.

•

AI-Driven Insights – Cognee’s memory engine transforms how the system deals with

documents and history. Instead of just storing data, the system now understands it – extracting

entities, relations, and meaning. This can power advanced features like natural language Q&A,

automated summarization of contract corpora, and proactive alerts (e.g., “These two contracts

have overlapping clauses that might conflict”) which were not feasible before.

•

Type-Safe and Maintainable – The move to a TypeScript monorepo (TanStack Start) with

shared types and modern libraries improves developer velocity and reduces bugs. The use of

BetterAuth and Better patterns (tRPC/GraphQL) means security and auth are consistently

enforced across the stack. We’ve effectively removed the complexity of blockchain (for now) and

13

replaced it with simpler, more familiar components (databases and logs), which you noted is

preferable given the team’s blockchain expertise is limited.

•

Scalability and Performance – Each component is built to scale: Memgraph can handle large,

complex graphs in-memory; DuckDB can crunch millions of rows on a single machine; LanceDB’s

vector index format is optimized for both memory and disk performance; Hono can scale

horizontally or deploy to edge networks. You can start small (develop locally with these

embedded DBs) and scale up as needed (e.g., move DuckDB to MotherDuck for cloud, or swap

Memgraph with Neo4j Aura if a managed service is desired).

•

Open-Source and Flexibility – All proposed components are open-source (or have open-source

cores). This avoids vendor lock-in (Auth0 was proprietary; Dgraph, while open-source, was a

niche; blockchain integration was custom). The new stack can be extended or modified freely –

for instance, if one day you want to reintroduce an immutable ledger, you could integrate

something like ProvenDB or blockchain at the periphery without touching the core logic.

•

Aligns with Original Goals – Importantly, nothing critical from Havona is lost: we still ensure

multi-tenant isolation (handled via auth and query filters), we still have audit trails (via

versioning and logs), we maintain a schema-first philosophy (GraphQL schema or TypeScript

interfaces driving data models), and we enable real-time data access (thanks to fast databases

and possibly subscriptions via GraphQL or live queries). We’ve only dropped the explicit

blockchain requirement, but that trade-off yields a simpler system while still meeting audit

needs in most cases.

Next Steps & Priorities:

1.

Prototype the Data Layer – Start by setting up the databases and verifying basic operations:

2.

Get Memgraph running (Docker or local). Use a small subset of your schema to create nodes
(e.g., create a couple of  Organization  and  Contract  nodes with relationships). Try

querying them with Cypher and, if possible, set up a quick GraphQL using Neo4j’s GraphQL

library to ensure Memgraph responds to GraphQL queries.

3.

Initialize LanceDB (it’s just a folder). Write a short script to add a few example vectors and query

them. This could be as simple as embedding a few sentences with a sentence-transformer model

and querying for similarity, just to ensure you understand the LanceDB Python/JS API.

4.

If you choose DuckDB, create a DuckDB file and see if you can query a LanceDB dataset through

DuckDB (using the Arrow integration) – the LanceDB docs show how DuckDB can select from a

Lance dataset

10

. This will confirm the interoperability.

5.

Set up a Postgres database if needed (for BetterAuth or if you prefer it over DuckDB for certain

data). Or use a libSQL database with Drizzle as in the template.

6.

Integrate Cognee on Sample Data  – Pick a sample contract or a few pages of text and run it

through Cognee:

7.

Install Cognee and an OpenAI API key (or use a local LLM if possible). Define a simple schema for

Cognee (you might start with Cognee’s default behavior which auto-infers triples, then later

enforce an ontology).

8.

Use Memgraph as the graph store for Cognee (their documentation and demo notebooks

provide guidance

41

44

). Ingest the sample text and then query the Cognee memory (e.g., ask

a question that the text can answer) to see the result.

9.

This will help you calibrate prompts and understand how to use BAML. Perhaps run the Cognee

+ Memgraph HackerNews demo if available

45

 to see a working example of ingesting data

and querying it.

14

10.

Verify that the triples created in Memgraph by Cognee make sense for your domain. You might

need to adjust the prompt or provide a custom extraction template (Cognee likely allows custom

prompt engineering for domain-specific info).

11.

Set Up the Dev Environment – Scaffold the TanStack Start app:

12.

Use the Better-T-Stack template or a similar starter to get Hono, React, BetterAuth integrated.

Ensure you can register a user and log in via BetterAuth (possibly just using email/password to

start).

13.

Add a protected route and test that BetterAuth’s session works (e.g., a dummy “Hello, {user}”

page that only shows if logged in).

14.

This gives you the skeleton to start adding features. Also, configure environment sharing (you’ll

have env vars for Memgraph connection string, etc., in the Hono backend).

15.

Implement Core GraphQL/tRPC Schema  – Translate key parts of the GraphQL schema from

Havona into your new backend:

16.

Define types like  Contract ,  Party ,  User , etc., either as GraphQL types or TypeScript

interfaces/classes. This could be a good time to trim or simplify – Havona’s schema was large,

but perhaps focus on crucial fields to get started.

17.

If using Apollo/GraphQL: set up the schema and use Neo4jGraphQL to generate resolvers for

Memgraph. Write custom resolvers for any fields that involve LanceDB (for example, a field like
snippets: [TextSnippet]  on Contract that fetches from LanceDB).
If using tRPC: define router procedures for things like  listContracts ,  getContract(id) ,
searchContracts(query) . Use the Memgraph JS driver or call out to Python (for Cognee) as

18.

needed inside these procedures.

19.

Ensure   multi-tenancy   by   scoping   queries   in   these   resolvers/procedures   to   the   orgId   from

BetterAuth’s session.

20.

Incremental Feature Development – Build out features one by one, testing end-to-end:

21.

List & View Contracts – front-end page to list contracts, detail page to view one. Backed by

GraphQL/tRPC queries. This uses Memgraph/DuckDB data.

22.

Add/Edit Contract – a form to create a new contract record. On submit, write to Memgraph (and

DuckDB). Also trigger the ingestion pipeline for any attached document or description (this

might initially be a manual trigger or a simplified function call).

23.

Search – a page or component to search across contracts. Hook this up to a backend call that

uses LanceDB (and possibly Cognee). Start with simple vector search results; later integrate

Cognee’s reasoning for more complex queries.

24.

Insights/QA (if applicable) – if one goal is convincing your friend of AI benefits, a demo where

you ask a question in natural language and get an answer with cited sources could be powerful.

This would use Cognee’s full pipeline. For example, “Which contract contains a clause about

pandemics and what does it say?” Cognee could retrieve the clause text and you display it.

25.

Audit Log – display change history for a contract. You could log changes in a Postgres table and

retrieve them, or show the previous versions stored in the graph. Implement a simple versioning
approach: e.g., each contract node in Memgraph could have a  currentVersion  property and
old versions as separate nodes linked via   PREVIOUS   relationship. Then a GraphQL query or

Cypher can pull the chain of versions.

15

26.

Testing & Hardening – As you build, write tests for the critical parts:

27.

Test that unauthorized access is blocked (BetterAuth is correctly protecting data – try querying

data with a different org’s token, etc.).

28.

Test the Cognee pipeline on various inputs to ensure it consistently produces good data (you

don’t want it creating junk nodes on a weirdly phrased contract – this might involve refining

BAML schemas or adding ontology rules).

29.

Benchmark search and queries on a reasonable data volume (maybe load a few hundred

contracts and see that everything remains snappy). This will surface any performance issues

early (for instance, if LanceDB needs an index built or if a particular GraphQL query is slow and

needs an index/hint in Memgraph).

Finally, prepare a presentation or document for your friend that compares the two architectures: - A

table or diagram of Havona Stack vs. Your Stack, highlighting improvements (e.g., “GraphQL+Dgraph” vs

“GraphQL+Memgraph+Cognee (with AI)”, “Auth0” vs “BetterAuth”, etc.). - Perhaps a live demo of the

prototype,   showing   a   user   query   that   Havona   cannot   do   (like   a   semantic   search   or   cross-contract

question)  which  your  system  handles  gracefully.   -   Outline   how   each   Havona   requirement   is   met   or

exceeded. For example,  “Field history tracking”  – Havona did it via blockchain logs, we do it via an

audit table and can even query it in natural language using Cognee (e.g., “show changes to Contract X

over time”). “Regulatory compliance” – Havona relied on immutability; our system ensures no deletion
of history and provides complete traceability in an easier-to-query form. - Also mention that by reducing

complexity (no need for maintaining a blockchain network, no Dgraph instances to manage), the ops

overhead is lower.

By taking these steps, you’ll incrementally build up the new stack and gather confidence in each piece. It

is indeed a complex project, but by breaking it down and leveraging the tutorials and docs for each

technology   (Cognee’s   guides,   Memgraph’s   quick-starts,   LanceDB   examples,   TanStack   template,   etc.),

you can accelerate development. Each of these tools was designed to solve hard problems in a plug-

and-play manner – together, they form a powerful, synergistic system. Good luck with your build, and

I’m   confident   that   this   approach   will   demonstrate   significant   long-term   benefits   and   innovative

capabilities to your friend!

Sources:

•

Havona project summary – GraphQL/Dgraph, dual persistence design

1

•

Kùzu database archival news (Oct 2025)

4

46

; Neo4j/Cypher support

2

•

Memgraph & Neo4j GraphQL integration (using Apollo + Neo4j GraphQL Library)

6

7

•

LanceDB overview – vector DB with DuckDB integration

9

10

•

DuckDB features – high-performance embedded analytics SQL engine

13

14

•

Hasura DuckDB connector – instant GraphQL on DuckDB

15

•

Cognee memory engine – combines vector search with knowledge graphs for AI memory

19

20

•

Cognee vs. RAG performance (90% vs 60% accuracy)

26

; natural language query layer hiding

Cypher

22

•

BAML (BoundaryML) – type-safe, structured outputs for LLMs to enforce schemas

24

•

CocoIndex – ETL framework for building vector indexes and knowledge graphs (Rust-powered)

47

48

•

DLT (Data Load Tool) – pipeline to load data into DuckDB (example pipeline)

33

34

•

BetterAuth with TanStack and Hono – modern monorepo template for auth and full-stack TS

40

38

•

Havona’s Auth0, Pydantic, multi-tenant setup for comparison

43

.

16

1

8

43

HAVONA_REPOSITORY_SUMMARY.md

file://file_00000000fafc6243845373520c1790d4

2

11

12

13

14

Embedded databases (1): The harmony of DuckDB, Kùzu and LanceDB • The Data

Quarry

https://thedataquarry.com/blog/embedded-db-1/

3

4

46

KuzuDB graph database abandoned, community mulls options • The Register

https://www.theregister.com/2025/10/14/kuzudb_abandoned/

5

The Weekly Edge: Adieu Kuzu, State of the Graph, NetworkX on ...

https://gdotv.com/blog/weekly-edge-adieu-kuzu-state-of-the-graph-17-october-2025/

6

GraphQL quick start - Memgraph

https://memgraph.com/docs/client-libraries/graphql

7

How to Build Secure Multi-Tenant Graphql API on Top of Memgraph

https://memgraph.com/blog/how-to-build-secure-multi-tenant-graphql-api-on-top-of-memgraph

9

Embedded databases (1): The harmony of DuckDB, Kùzu and ...

https://thedataquarry.com/blog/embedded-db-1

10

42

DuckDB - LanceDB

https://lancedb.github.io/lancedb/python/duckdb/

15

Instant GraphQL APIs on DuckDB

https://hasura.io/blog/instant-graphql-apis-on-duckdb

16

17

18

19

21

22

23

26

27

28

41

From RAG to Graphs: How Cognee is Building Self-Improving AI

Memory

https://memgraph.com/blog/from-rag-to-graphs-cognee-ai-memory

20

36

Cognee - Knowledge Graphs: Understand Misconceptions for Smarter Insights

https://www.cognee.ai/blog/fundamentals/knowledge-graph-myths

24

BAML

https://boundaryml.com/

25

BAML x cognee: Structured Output & AI Memory in Production

https://www.cognee.ai/blog/integrations/structured-outputs-with-baml-and-cognee

29

CocoIndex

https://cocoindex.io/

30

CocoIndex ETL with Document AI - GitHub

https://github.com/cocoindex-io/cocoindex-etl-with-document-ai

31

Large codebase context with tree-sitter and Cocoindex for coding ...

https://cocoindexio.substack.com/p/index-codebase-with-tree-sitter-and

32

CocoIndex Settings

https://cocoindex.io/docs/core/initialization/

33

34

35

Build a dlt pipeline | dlt Docs

https://dlthub.com/docs/tutorial/load-data-from-an-api

37

Build Real-Time Codebase Indexing for AI Code Generation

https://cocoindex.io/blogs/index-code-base-for-rag

38

Better Auth

https://www.better-auth.com/

17

39

AmanVarshney01/Better-T-Stack: Tanstack Router, Hono ... - GitHub

https://github.com/AmanVarshney01/Better-T-Stack

40

An open-source deno monorepo template with Hono, React + Vite ...

https://www.reddit.com/r/Deno/comments/1i2tn3a/an_opensource_deno_monorepo_template_with_hono/

44

Cognee + Memgraph: How To Build An Intelligent Knowledge Graph ...

https://memgraph.com/blog/cognee-memgraph-integration-demo

45

Memgraph blog

https://memgraph.com/blog

47

CocoIndex Indexing Basics

https://cocoindex.io/docs/core/basics

48

introducing cocoindex - super simple to prepare data for ai agents ...

https://www.reddit.com/r/Rag/comments/1lop239/introducing_cocoindex_super_simple_to_prepare/

18

