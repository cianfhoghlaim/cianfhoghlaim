Implementation Plan for Crypto Analytics & ML

System

Infrastructure Provisioning

•

Cloud Resources (Cloudflare & Compute):  Use  Pulumi (TypeScript)  to provision core cloud

resources and isolate environments. For example, define a Pulumi stack for  development  and

another for production, each creating a Cloudflare D1 database and R2 bucket

1

. In code, use

Pulumi’s   Cloudflare   provider   to   instantiate   a   D1   database   and   R2   bucket   and   export   their

identifiers for use by applications

2

3

. This provides a serverless SQLite (D1) for lightweight

transactional data and an S3-compatible object store (R2) for data lake storage. Pulumi outputs

(like the D1 database UUID, R2 bucket name, and API tokens) are securely stored in 1Password

via the 1Password Node.js SDK

4

 – ensuring secrets (API keys, database IDs) never appear in

plaintext in code or CI logs. Each Pulumi stack uses config values (Cloudflare account, etc.) pulled
from   1Password,   enabling   consistent   provisioning   across   dev/staging/prod   with   separate

credentials.

•

Server Provisioning (OCI/Hetzner): Provision compute instances on Oracle Cloud (OCI) and/or

Hetzner   via   infrastructure-as-code   (Pulumi   or   Ansible).   These   servers   will   host   containerized

services.   Using  Ansible,   automate   base   setup:   OS   updates,   Docker   engine   installation,   and

firewall rules. The goal is a repeatable environment setup that can be re-run for new servers or

disaster recovery. Keep cloud provider credentials and SSH keys in 1Password, retrieving them

during provisioning. By managing servers as code, you ensure environment drift is minimized

and deployments are reproducible.

•

Container   Orchestration   with   Komodo:  Deploy  Komodo  on   the   provisioned   server(s)   to

manage  containers  via  GitOps.  Komodo  acts  as  a  lightweight,  self-hosted  PaaS:  it  can  pull  a

Docker Compose file from a Git repository and orchestrate the defined services. We will maintain
a  central   docker-compose.yml   in the repo that declares all microservices (databases, APIs,

frontends)

5

. Komodo continuously monitors this and deploys updates, providing a declarative

deployment model. Each service runs as a Docker container on the host, networked together.

Komodo’s   web   UI   and   API   will   be   used   for   observing   deployments   and   manually   triggering

redeployments if needed.

•

Core Infrastructure Services (Docker Containers): Using the Compose/Komodo setup, define

containers for each core service in the Infrastructure Stack and Storage Stack:

•

DragonflyDB: An in-memory datastore (Redis-compatible) for caching and fast lookups. Launch

a DragonflyDB container for ephemeral data like caching API responses or interim results. This

speeds up repeated queries and offloads frequent reads from the primary database.

•

Memgraph (Cognee Graph DB): Deploy Memgraph to serve as the graph database backing the

Cognee knowledge base. Cognee will use this for storing entities and relationships (e.g. linking

tokens, addresses, protocols to events)

6

. The container should mount a volume for

persistence (so the knowledge graph isn’t lost on restart).

1

•

Vector Store (LanceDB): For semantic search, include a vector database. We can use LanceDB

(an embeddable vector store) or an alternative like Qdrant. If LanceDB is library-embedded, we

may not need a standalone service – but for scaling, consider a small vector DB container that

Cognee can query for similarity search. This will index embedding vectors produced by

CocoIndex.

•

DuckDB + DuckLake: DuckDB itself runs embedded in pipelines or the frontend, so no long-

running container is needed solely for DuckDB. Instead, ensure the R2 bucket and metadata

(DuckLake catalog) are accessible. If needed for concurrency, we might run a DuckDB SQL rest

server, but in this design we lean on client-side DuckDB or ephemeral use in jobs.

•

Supabase (Postgres) [Optional]: If a heavier relational backend or user auth store is required

(for example, to store user profiles or to support Langfuse telemetry), a Supabase stack can be

deployed. Supabase’s Docker setup would provide a Postgres database and APIs. This can back

features like user login, or serve as the database for Langfuse (observability) if not using D1 for

that. (Supabase can be omitted if D1 and DuckDB suffice for structured storage).

•

Convex: Deploy a self-hosted Convex server if available (Convex is a hosted service by default,

but we assume a self-hosted option for this stack). Convex will act as a state synchronization

service for the frontend – enabling real-time updates or collaborative features. It will be

containerized and require a storage directory or small disk for its state. If self-hosting Convex is

not feasible, we will rely on the managed Convex service or replace this with a lightweight

alternative (like a simple WebSocket server with Redis/Dragonfly for pub-sub).

•

Langfuse: For LLM telemetry and monitoring, run Langfuse in a container (likely with a

connection string to a Postgres database). Langfuse will collect logs, prompts, responses, and

metadata from our ML components, which can be viewed in its web UI. We’ll configure Langfuse

to write to either the Supabase Postgres or an external database. This container should be

protected (e.g. behind Pangolin or basic auth) since it contains sensitive prompt/response data.

•

LiteLLM: Integrate LiteLLM as a microservice or library for LLM calls. If LiteLLM offers a server

mode (for caching or proxying requests to providers like OpenAI), containerize it and provide it

with API keys via environment variables. Otherwise, incorporate it as a library within agent code

to handle retries and caching of LLM responses. Using LiteLLM ensures that repeated or similar

prompts can be served from cache, reducing latency and cost.

•

Networking & Zero-Trust Access (Pangolin):  Deploy  Pangolin, a tunneled reverse proxy, as a

container to secure access to services. Pangolin will expose our various services (frontend UI, API

endpoints, monitoring UIs like Langfuse/Dozzle) on custom subdomains with optional access
control. We’ll configure Pangolin with our domain (e.g.   *.example.com ) so that it can route

traffic   to   the   appropriate   internal   container   based   on   subdomain
.   For   example,
analytics.example.com   might   point   to   the   production   frontend,   api.example.com   to
backend   APIs,   and   pr-123.example.com   to   a   PR   preview   environment.   Pangolin   supports

7

8

integration with identity providers (like PocketID/TinyAuth, which are in our stack) for SSO – we

will integrate one of these lightweight auth services to enforce login for internal or preview sites.

In   production,   Pangolin   can   still   be   used   as   an   additional   security   layer   (IP   filtering,   TLS

termination, and as a single point to enable 2FA or token-based access if desired). All Pangolin

secrets (API tokens, admin credentials) are stored in 1Password and provided to Pangolin via

environment variables or its config file at runtime.

•

Secrets Management: 1Password is the single source of truth for secrets. During deployment,

Komodo or our CI pipeline will retrieve sensitive values (Cloudflare API keys, Pangolin API token,

OpenAI/HuggingFace   keys,   database   passwords)   from   1Password   and   inject   them   into   the

container environments. For Komodo-managed deployments, we leverage Komodo’s ability to

mount secrets on the deployment agent (so that secrets are available locally on the server but

2

not   exposed   elsewhere)

9

.   For   example,   the   Pangolin   API   token   used   by   the   CI   script

(described below) will be fetched at runtime from 1Password rather than hard-coded. We will

also   use  scoped   API   keys  whenever   possible   (Cloudflare   tokens   limited   to   specific   resources,

Pangolin keys limited to one site, etc.) to minimize blast radius

10

. All secret access in CI/CD is

done with masked environment variables or the 1Password Connect API to ensure they never

leak in logs. This approach provides strong security while keeping deployments fully automated.

Pipeline Orchestration

•

Structured Data Ingestion (DLT): Build ingestion pipelines using DLT (Data Load Tool) to fetch

both historical and streaming crypto data. We maintain a registry of data sources (e.g. a
crypto_sources.json  defining APIs, subgraph endpoints, and file feeds for various

protocols) with schema definitions for each

11

. For example, we configure DLT to pull:

•

On-chain Metrics: using Ethereum JSON-RPC or explorer APIs for blockchain data (e.g. contract

events, validator stats)

12

.

•

DeFi Protocol Stats: via The Graph subgraphs (GraphQL APIs) for protocols like Aave and Pendle

to get high-level metrics (TVL, interest rates, user counts) without parsing raw chain data

13

.

•

Market Data APIs: such as CoinGecko for token prices, DeFiLlama for TVL and yield rates, etc.,

to collect time-series of market indicators
Social/News Feeds: (Structured part) via APIs like alternative.me for the Fear & Greed Index or

14

15

.

•

Twitter APIs for sentiment scores, which provide numeric or categorical data relevant to market

sentiment.

Each   DLT   pipeline   normalizes   the   data   into   our   unified   schema   (as   defined   in   the   registry)   so   that

disparate sources (e.g. different DeFi protocols) produce comparable tables

16

. DLT handles scheduling

these extractions at defined intervals. For example, prices and on-chain metrics might be fetched every

5   minutes,   while   broader   metrics   daily.   We   implement  incremental   loading  so   that   each   run   only

appends new records (with timestamps or sequence IDs) without duplicating data

17

. Historic backfills

(large initial loads) are handled by separate one-time DLT jobs that populate the archives.

•

Unstructured Data Ingestion (crawl4ai & Files): Set up crawl4ai to scrape qualitative data

sources:

•

News Articles & Blogs: Use crawl4ai’s web crawling capabilities to scrape relevant crypto news

sites, forums, and blogs for articles and posts. We will maintain a list of URLs or RSS feeds to

monitor. Crawl4ai can fetch HTML pages and PDFs; we schedule it to run daily or near real-time

for sources like CoinDesk, protocol governance forums, developer blogs, etc.

18

. The scraped

content (HTML text, PDF text) is fed into the pipeline as unstructured documents.

•

Documentation & Research PDFs: Similarly, crawl4ai can fetch documentation pages or

research papers (e.g. whitepapers, regulatory reports). These are ingested periodically to

capture any updates or new documents.

•

GitHub Repositories:  For code-centric data (like protocol smart contracts or SDKs), we use a

combination of DLT’s filesystem connector and Repomix. If the repositories are local or can be

mirrored locally, DLT can ingest the file tree (treating the repo as a filesystem data source)

19

20

. We also have the option to run  Repomix  (a Node CLI) directly on a cloned repository to

pack the entire repo into an AI-consumable format. This is useful for large codebases: Repomix

condenses a repository into one or a few files that an LLM can more easily consume for analysis

(by concatenating critical parts, summarizing others)

21

. We will use this for key repositories (for

instance,   analyzing   an   open-source   DeFi   protocol’s   code   to   understand   its   architecture).   The

output from Repomix (an “AI-friendly” text of the repo) will be stored for later LLM processing by

agents.

3

•

Data Lake Storage (Parquet + R2): All raw and processed data is stored in columnar Parquet

files on Cloudflare R2 for a cost-efficient, durable data lake

22

. Structured data from DLT (time-

series metrics, API results) accumulates in partitioned Parquet files (e.g. partitioned by date or by

protocol).   Each   micro-batch   of   real-time   data   is   appended   as   a   new   Parquet   file   (to   avoid

. Unstructured text data (scraped articles, documents) is
contention and allow easy appends)
also saved, either as raw text files or as Parquet records with fields like  source, date, text .

23

By   using   an   object   store   with   zero   egress   fees,   we   can   freely   query   this   data   from   various

environments. On top of this, implement a DuckLake layer – essentially DuckDB with an Iceberg

or   similar   catalog   –   to   treat   the   R2   bucket   as   a  Lakehouse

24

.   DuckDB   will   maintain   a

lightweight catalog of table schemas and partitions

25

, allowing us to run analytical SQL queries

over  the  data  lake  directly.  This  gives  the  team  a  uniform  SQL  interface  to  all  historical  and

current data without loading it into a separate data warehouse. The  Separation of Concerns

principle   is   applied:   R2   holds   the   storage,   DuckDB   provides   compute   for   analytics,   and   the

DuckLake catalog holds metadata

26

.

•

Transformations and Quality Control: Use Ibis and sqlmesh to define transformation logic in a

high-level, maintainable way. Ibis allows writing Python code that compiles to SQL, which we can

use to create derived tables (for example, computing a Fear & Greed Index time-series average,

or   normalizing   metrics   across   protocols).  sqlmesh  is   employed   to   version   and   test   these

transformations   –   we   define   data   models   (as   SQL   or   Ibis   pipelines)   for   important   derived

datasets,   and   sqlmesh   helps   validate   changes   to   these   models.   Before   deploying   a

transformation   update,   sqlmesh   can   simulate   it   on   a   subset   of   data   or   compare   outputs,

ensuring we don’t accidentally break a metric calculation. This provides data CI/CD: any change in

transformation   logic   can   be   checked   for   consistency   with   historical   results.   Additionally,

incorporate Dagster as an orchestration layer that schedules and coordinates all the pipelines.

Dagster   will   manage   dependencies   between   jobs   (e.g.,   first   run   DLT   ingestion,   then   run

CocoIndex indexing) and handle retries if a job fails. We will create Dagster assets for each data

source   and   each   processing   step,   which   gives   a   clear   DAG   of   the   entire   pipeline.   During

execution, Dagster can also perform simple validations – e.g., alert if a daily data volume is 90%

lower than previous (which might indicate a source outage or ingestion bug).

•

Semantic Indexing (CocoIndex): Once new data (structured or unstructured) lands in the lake,

CocoIndex  comes   into   play.   CocoIndex   continuously   monitors   for   new   or   updated   data   and

processes it to generate search indices

27

. We configure CocoIndex with different pipelines for

different data types:

•

For text documents (news articles, blog posts, code documentation): CocoIndex will chunk the text

into semantic units and embed each chunk into a vector representation

28

. For example, an

article might be split into paragraphs or sentences, and code repositories might be split by

function or file using Tree-sitter
Transformer model (e.g.  all-MiniLM-L6-v2  as shown in our example)

. Each chunk gets an embedding via a HuggingFace

30

. CocoIndex

30

29

collects these embeddings and associated metadata (document ID, chunk text) incrementally –

meaning if only one new article appears or one file changes in a repo, it only processes that,

rather than reprocessing everything

31

. The output is an up-to-date vector index of all textual

content in the system.

•

For structured data (metrics, time-series): We may not embed raw numbers, but we use CocoIndex

for derived indexing. For instance, CocoIndex can compute technical indicators from price series

(like moving averages, volatility indices) and treat those as new data points to index or trigger

alerts

32

. Additionally, we might represent a time-series trend as a short natural language

description and embed that. (This way, semantic search can retrieve a trend based on a query

4

like "sudden drop in TVL in July"). These representations would also be stored as vectors in the

index.

•

For code content: CocoIndex integrates with our repository ingestion: after DLT ingests files,

CocoIndex can parse code, generate docstrings or summaries for each function, and embed

code snippets. The example in the Git repo workflow shows using Tree-sitter via CocoIndex to

chunk code and then embed each chunk

29

30

. We follow a similar approach for smart

contracts or other code – enabling semantic code search (e.g., find where a certain function or

concept is implemented across repos).

CocoIndex’s incremental and pluggable design lets us attach  storage targets  for the index. We will

implement a target that sends the indexed data into Cognee – either by calling Cognee’s API or writing

directly   to   its   database

6

.   This   means   every   time   CocoIndex   generates   new   embeddings   or

relationships, they are ingested by Cognee.

•

Knowledge Graph & Search (Cognee): Cognee serves as the unified knowledge base for the

project, combining a graph database with the semantic index. When CocoIndex exports new

items, Cognee will:

•

Graph storage: Insert entities and relations into its graph store (backed by Memgraph). For
example, if CocoIndex processed a news article about Aave, Cognee might create a  Protocol
node for Aave (if not exists) and relate it to a  Document  node for that article with an edge

"mentions" or "about". Similarly, a metric data point (e.g., TVL for Aave on a date) could be a
node that links to the  Protocol  entity and to a  Metric  entity type. We configure these

schemas so that as data flows in, the graph grows with meaningful links (e.g. Token—Price—Date,

or Article—mentions→Protocol). The knowledge graph captures both entities (tokens, protocols,
addresses, concepts) and events or facts (price at time, article published)

.

6

•

Vector index: Store embedding vectors for text and code chunks in a vector index (backed by a

vector DB or internally via Memgraph if it supports vectors). Cognee retains these vectors to

enable semantic similarity search over content

33

34

. The hybrid of graph + vectors allows

queries like: find articles semantically related to a given piece of text and filter by those that

involve a specific token or date range (using graph constraints)

35

. Cognee essentially acts as

the “brain” of the system – a long-term memory that can be queried structurally or semantically.

We will expose an API (or use Cognee’s built-in one) to allow other components (like our agents
or UI) to query this knowledge base. Over time, as new data comes in, Cognee incrementally

updates the graph and index without reloading everything (CocoIndex ensures only new data is

processed, and Cognee upserts or merges it)

36

.

•

Indexing Example: As a concrete example, suppose a new DeFi exploit happened: DLT logs the

on-chain data (fund transfers, etc.) and crawl4ai pulls a blog post about it. CocoIndex embeds

the blog content. Cognee then links the blog post node to the protocol or contracts involved in

the exploit, and stores the text embeddings. A query for “exploit affecting TVL drop” could then

find that blog via semantic match and confirm via graph that it’s about the protocol whose TVL

dropped, yielding a rich result.

By establishing this ingestion-to-index pipeline, we ensure data flows from raw sources to an enriched,

queryable knowledge graph in a modular way. Each layer (ingestion, storage, indexing) is decoupled by

clearly defined interfaces (Parquet files, SQL, API calls)

37

. This means we can swap out components if

needed   (e.g.   change   the   vector   DB,   or   replace   crawl4ai   with   another   crawler)   without   breaking   the

overall system, improving maintainability and future-proofing

38

.

5

Frontend

•

Architecture   and   Framework:  The   front-end   is   implemented   as   a   modern   web   application

using   the  TanStack  suite   (e.g.   React   with   TanStack   Router   and   Query   for   data   fetching).   We
scaffold the project possibly with a starter like TanStack Start, ensuring a clean separation of UI

components, state management, and data-access hooks. The goal for the UI is to provide a rich

Discovery & Search interface for the crypto data

39

, following a library-like exploration model.

Users   should   be   able   to   run   structured   queries,   browse   metrics,   and   also   perform   semantic

searches over the knowledge base.

•

Client-Side Query Engine: To maximize scalability and minimize server dependencies, we plan

to leverage DuckDB-Wasm in the browser for certain analytics. For example, if a user wants to

run a custom SQL query on price or metric data, the front-end can fetch the relevant Parquet file

from R2 (using a pre-signed URL or public access to specific data files) and execute the query

locally via DuckDB compiled to WebAssembly

40

. This approach (inspired by the Harvard LIL

data exploration philosophy) means that even if our backend is down, the static app + data files

can deliver value, and it reduces load on servers for analytical queries

41

42

. We will carefully

partition and format data so that queries remain efficient (e.g. yearly Parquet files or separate

files per protocol to limit download size). The UI will present query results in interactive tables or

charts, and TanStack Table can be used for tabular displays.

•

Search and Semantic Query UI: For searching documents and knowledge, the front-end offers

a unified search bar with filters. This search interface will integrate with our Cognee index:

•

A user query can be either keyword-based or natural language. When submitted, the front-end

will call our backend search API (described below) which runs the query against Cognee’s vector

index and graph.

•

Results (e.g. relevant articles, data points, or entities) are returned with context, which the UI

displays in a list. The UI allows the user to filter or facet results (for example, restrict to a date

range, or a specific protocol). These filters map to graph queries (e.g. filter by protocol entity or

time) on the backend.

•

Each result can be expanded to show details: if it’s a metric, show a small chart; if an article, show

an excerpt with highlighted matching terms or similar embeddings.

•

APIs   via   Hono   (Edge   Functions):  We   implement   a   minimal   backend   for   the   frontend   using

Hono, a lightweight TypeScript web framework that can run on Bun or as a Cloudflare Worker.

Hono will be used to create HTTP endpoints for operations that cannot be done purely on the

client:

•

A search API that accepts a query and filter parameters, then queries Cognee. This API will live

on an edge function (for low latency global access) or on the same server as Cognee. It will use

Cognee’s client library or HTTP API to perform a vector search and return results. We could

deploy this as a Cloudflare Worker hitting Cognee’s endpoint (secured by an API token), since

Cloudflare’s network is close to our R2 data and likely our Cognee host.

•

An agent query API (for LLM-backed queries, described in ML Integration) to handle questions

that require reasoning, not just retrieval. The front-end will POST a question, and this API will

invoke the Agno agent and stream back the answer.

•

Other utility endpoints: e.g. an endpoint to fetch pre-signed URLs or temporary tokens for R2 (if

we restrict direct access), or to fetch summary stats (like “top 5 movers this week”) which the

backend can compute via DuckDB or using cached results.

6

Hono’s   small   footprint   and   compatibility   with   Bun   make   it   a   great   choice   to   write   these   serverless

functions in our existing TypeScript codebase. We’ll integrate 1Password for any secrets needed in these

functions  (like  Cognee  API  keys)  by  using  environment  variables  or  KV  storage  populated  from  our

Pulumi outputs.

•

Real-time Features with Convex: For an enhanced UX, integrate Convex in the front-end.

Convex provides a realtime state synchronization and serverless data platform. We will use it for

features that benefit from push updates or collaborative state:

•

Notifications & Live Data: Use Convex to push notifications to the UI when new data arrives or

when an agent completes a long-running analysis. For example, if a new daily report is

generated by an agent, Convex can notify the client to display a “New insight available” message.

•

Collaborative Annotations: If users can annotate or comment on findings (say, add notes to a

chart or bookmark a result), those can be stored in Convex and updated live for all viewers (if

multi-user).

•

Edge caching of queries: Convex functions could also cache results of expensive operations (like

a heavy query or an agent answer) so that if another user asks the same thing, they get a fast

response. Convex’s internal storage (which is based on SQLite and is strongly consistent) can

serve as a short-term cache or state store for such ephemeral data.

We will deploy Convex either by self-hosting (if possible) or by using their cloud and treating it as an
external dependency. If self-hosted, ensure it runs close to our data (maybe on the same server or

region as Cognee to reduce latency) and secure it via Pangolin (Convex has its own auth tokens for

clients). The front-end will use the Convex client library to subscribe to any necessary query or to call

Convex functions for these features.

•

User Interface and Experience: The UI will be designed with a dashboard-like feel for metrics

and a search console for exploration. Key components:

•

Dashboard pages: showing current market metrics (price indices, volatility, sentiment gauges) –

pulling data via either direct DuckDB queries or Convex functions that aggregate recent data. For

instance, the Fear & Greed index could be displayed along with historical trend, fetched directly

from D1 or DuckDB.

•

Search page: with a search bar and results list, as described. Users can toggle between Data

(structured results like metrics, tables), Documents (news, PDFs), and QA (direct answers from

agents).

•

Detail modals or pages: when clicking on a specific result (e.g. a particular protocol), the UI can

show a profile – e.g. a page with that protocol’s recent metrics, related news, and an option to

ask an agent a question about it.

•

Integration of ML outputs: If an agent produces a summary (like “summarize this week’s

market events”), the UI will present that in a report format – possibly with sections and graphs

inserted. Because we emphasize structured output from the LLM (via BAML), the frontend can

render agent outputs into rich HTML (e.g. if the agent returns a JSON with keys "summary",

"top_events", the UI knows to format those accordingly).

Throughout the front-end, focus on responsiveness and clarity: use TanStack Table for interactive tables

(sortable, filterable), TanStack Charts for time-series visualizations, and ensure the app can work as a

static bundle (for archive or if deployed to Cloudflare Pages for instance). The design will follow the

principle of  faceted discovery  – users can either follow their nose via filters and links or ask direct

questions, with the interface supporting both modes seamlessly

43

.

7

ML Integration (Agents & AI Analysis)

•

Agent Orchestration with Agno: We incorporate an Agno multi-agent orchestration layer to

enable advanced analysis on top of the data. Agno will manage one or more LLM-powered
agents that can perform tasks like generating reports, answering natural language questions, or

detecting anomalies in the data

44

45

. Each agent is configured with:

•

A specific role and prompt defining its behavior. For example, a “Trend Summarizer” agent

might have a system prompt like: “You are an analyst AI that summarizes the past week’s crypto

market events, given relevant data.” A “Q&A” agent will be geared to answer user queries precisely

46

.

•

Access to tools/memory: using Agno’s framework, agents can call external tools. The primary

tool is our Cognee knowledge base – agents can query Cognee via a tool interface to retrieve up-

to-date facts or documents

47

. For example, if the Q&A agent is asked, “What caused the spike

in ETH price last week?”, it can use a CogneeSearch tool to find related news or on-chain events

around that date, then use that as context for its answer

48

. We can also define other tools: e.g.,

an HTTP fetcher if the agent needs to get the latest price (if not in our DB) or a calculator for

numeric analysis.

•

A target LLM model: Agno is model-agnostic, so we can configure agents to use OpenAI GPT-4,

Anthropic Claude, or a local HuggingFace model. Initially, we’ll use high-accuracy models like

GPT-4 via API (with keys stored in 1Password). For cost control or data privacy, we can later

incorporate an open-source model (maybe fine-tuned on crypto data) hosted locally. The

LiteLLM library will be used here to interface with the chosen LLM, providing features like

request caching and failover. Agno’s design allows swapping the model by changing a config, so

we could even use different models for different agents (e.g. a smaller, faster model for simple

questions and a more powerful one for deep analysis)

49

50

.

We will run the Agno orchestrator as a background service (which could be a Python process or a Bun

TS process, depending on the implementation language we choose for Agno and BAML). It might be

packaged   as   a   Docker   container   for   Komodo   to   manage.   Agents   can   be   invoked   on-demand   (for

interactive queries) or on a schedule. For instance, every Monday the Trend Summarizer agent might

auto-generate a “Weekly Report” by querying Cognee for the past week’s notable data and writing up a

summary. Those results would be stored (perhaps in D1 or as a file in R2) and surfaced in the UI.

•

Memory Integration: Agno is configured to treat Cognee as its long-term memory store

51

.

Thanks to Cognee’s hybrid nature, agents get the best of both worlds: they can do precise

lookups (via graph queries, like “find all hacks in the last 24h affecting DEXes”) and broad

semantic searches (“find anything similar to this incident”)

52

. We implement an Agno memory

adapter that uses Cognee’s API. When an agent runs, the sequence is:

•

Agent receives a task (user question or scheduled job) via Agno.

•

Agent formulates internal queries to Cognee (Agno may do this automatically for relevant

context). For example, it might search for the top 5 related items in Cognee and retrieve their

content.

•

The relevant context data is fed into the agent’s prompt. We take care to keep this within token

limits – e.g., by retrieving only short summaries or facts (Cognee can store pre-summarized

versions of lengthy docs).

•

The agent LLM produces an output (answer/analysis), which Agno returns to the caller or post-

processes.

Agno supports multi-agent workflows, meaning agents can call other agents or work in a team

53

54

.

We might design a workflow where the Q&A agent, if unsure, delegates to a specialized “Data Checker”

8

agent that double-checks a calculation by querying the database. In Agno, this could be done via tool

invocation or an agent asking another agent through the orchestrator.

•

Structured Prompting with BAML: We use Boundary AI Markup Language (BAML) to define

our prompts and expected outputs in a structured way. BAML allows us to specify input

parameters and output schema for LLM prompts, bringing reliability to LLM responses

55

56

.

In practice:

•

We create BAML templates for each agent’s task. For example, a BAML definition for the

repository analysis (from the Git workflow example) might look like a function signature:
function summarizeRepo(repoContext) -> {summary: string, architecture:

string, issues: string[]} . The prompt text would instruct the LLM to fill in that JSON

structure

57

.

•

For our crypto analytics, we define BAML schemas like
summarizeWeek(dataPoints, events) -> { marketSummary: string, topEvents:

Event[], outlook: string }  or for Q&A:  answerQuestion(query) -> { answer:
string, sources: string[] } . By doing this, we ensure the LLM’s output is well-structured

JSON or YAML that we can easily parse and display. It prevents the model from rambling or

missing crucial parts, as the schema acts as a contract.

•

BAML also supports multi-step prompts and conditional logic, which we can use for complex

tasks

58

. For instance, if we ask the agent to provide a recommendation (e.g., “What data

should I look at to understand today’s BTC move?”), the BAML prompt can include an optional

field for a suggested query or chart. The agent might then output a SQL query or a snippet of a

Docker Compose for a simulation environment as part of its structured answer (as was

demonstrated in the repo analysis example with an Arduino simulation snippet)

59

60

.

Using BAML, every agent result will adhere to a known format, making it far easier to integrate with the

frontend and to validate. We will test prompts iteratively, using BAML’s schema enforcement to catch

cases where the LLM’s response doesn’t fit the expected format. This significantly improves reliability

and consistency of LLM outputs

61

.

•

HuggingFace & Model Management: Incorporate HuggingFace ecosystem for model selection

and fine-tuning:

•

For embeddings, as noted, we use pre-trained Transformer models from HuggingFace via

CocoIndex (Sentence Transformers like MiniLM)

30

. We may host these models locally (to avoid

external API calls and speed up processing) – Bun or Python can load them with ONNX or
transformers  library. If needed, we can fine-tune an embedding model on our corpus (e.g.,

to better capture financial text nuances) and save it in the pipeline.

•

For LLMs, while initial use relies on external APIs, we will explore deploying a smaller model
locally using HuggingFace’s  text-generation-inference  server or similar. This could be a

fine-tuned Llama-2 or other model specializing in financial text. We can track these experiments

with MLflow – using MLflow to log different model versions, prompt variants, and their

performance on validation questions. For instance, we might have a set of test queries and

expected answer quality; MLflow can help record which model/prompt configuration performs

best, along with metrics like accuracy or token usage.

•

mlnr (if referring to a specific ML orchestrator or “ML Runner”) can be integrated if it exists as a

tool   for   running   model   pipelines   or   managing   models   in   production.   It’s   possible   that  mlnr

refers to a custom internal tool for model deployment. In our plan, we ensure any custom ML

deployment  (like  hosting  a  model  on  OCI  with  GPU)  is  scripted  (using  Pulumi  or  Ansible  for

provisioning and Docker for serving the model). If mlflow and huggingface handling suffice, we

9

might   not   need   an   extra   component,   but   we   remain   open   to   incorporating   specialized   ML

orchestrators to handle model lifecycle.

•

Observability and Logging: Employ Langfuse to log all agent interactions and LLM calls. Each

request to the LLM (prompt and response) will be sent to Langfuse, along with metadata like

agent   name,   request   ID,   timing,   and   whether   it   was   a   success   or   had   an   error.   Langfuse’s

dashboard will let us see, for example, how many questions were asked today, what the average

response time is, and inspect specific failures or hallucinations. This is invaluable for debugging

and improving prompts. We configure the agents to use Langfuse’s client library (with an API key

stored in 1Password) so that logging is non-intrusive. Langfuse will store data in its database (we

will use the Supabase Postgres for this if we deployed Supabase, or alternatively a Cloudflare D1

if volume is low, though Postgres is preferred for larger data). By monitoring these logs, we can

iteratively refine our BAML prompts and even detect drifts in model performance (e.g., if a model

update by OpenAI changes behavior, we’ll see changes in the logs).

•

Agent Outputs and Integration: The outputs from the agents feed back into the system:

•

Key insights or summaries generated by agents can be stored in the knowledge base as new

data. For instance, if the weekly report agent concludes “Protocol X had a security breach
causing TVL to drop 20%,” we might insert that as a  Insight  node in Cognee linked to

Protocol X and to the time/week. This way, the AI-generated knowledge becomes part of what

subsequent queries can use (with appropriate tagging that it’s an AI-generated insight).

•

If any critical alerts or anomalies are detected by agents (say an anomaly detector agent flags a

sudden deviation), we can push those to the front-end (perhaps via Convex notifications or as a

banner on the dashboard).

•

Maintain a history of reports and Q&A in the application (maybe in D1 or Supabase). This allows

users to review past outputs and also provides training data if we later fine-tune models on our

domain (though careful with feedback loops – we’d validate any self-generated data before

training on it).

By integrating Agno and BAML, we add a powerful AI reasoning layer on top of our data. The system

isn’t   just   storing   and   searching   information;   it’s   capable   of   producing  context-aware   analyses

automatically

62

63

. This aligns with our AI-native approach – moving beyond static dashboards to an

intelligent assistant that can explain and contextualize the crypto data for the users.

Deployment and Secret Handling

•

GitOps   Workflow:  All   infrastructure   and   application   code   is   managed   via   Git   repositories,

enabling a  GitOps  deployment model

5

. We use a mono-repo or a set of tightly coordinated

repos for different parts (infrastructure, pipeline code, frontend, etc.), but in all cases changes

are made via pull requests (following the OpenSpec proposal process for major changes). Thanks

to Komodo, any merge to main (for, say, the docker-compose or a service Dockerfile) triggers an

automated deployment of the updated containers. We have configured CI (GitHub Actions or

similar) to run tests and then invoke Komodo’s deploy API for the main branch. For example,

pushing a new version of the frontend will result in CI building the Docker image, pushing it to a

registry,   and   calling   Komodo   to   deploy   that   image   tag   to   the   production   service.   Komodo

ensures zero-downtime restarts (by using container health checks and pulling the new image

before swapping). The Compose file in Git defines the desired state (services, their images and

env vars), and is the single source of configuration truth for the runtime environment, which

fosters reproducibility.

10

•

Preview Environments: For each feature branch or PR, we utilize Komodo + Pangolin to stand
up an isolated preview. The  komodo-pr-deploy  workflow is set up in our GitHub Actions: on

each   PR,   the   action   uses   the   Komodo   SDK   to   build   and   deploy   the   branch’s   containers   to   a

Komodo-managed   host
*.dev.example.com ) so that the PR app will be accessible at a unique subdomain

.   Pangolin   is   configured   with   a   wildcard   domain   (e.g.

66

. The

64

65

GitHub Action, after deploying via Komodo, calls Pangolin’s API to register a new site that maps

the   subdomain   to   the   container’s   internal   address

67

.   This   automated   Pangolin   registration

uses credentials stored in GitHub Secrets (which are loaded from 1Password, as we prefer to only

update 1Password and have a CI step populate GH secrets). As a result, each PR (say feature-X)
gets   a   live   URL   like   feature-X.dev.example.com   for   engineers   or   stakeholders   to   test.

Pangolin’s  zero-trust  capabilities  mean  these  preview  URLs  can  be  password-protected  or  IP-

restricted   easily,   preventing   random   outsiders   from   accessing   pre-production   deployments.

When the PR is merged or closed, we can have automation tear down the preview container and

deregister the Pangolin route to conserve resources.

•

Pangolin–Komodo   Integration   Approach:  We   implement   the   Pangolin   registration   in   code

(TypeScript) rather than manual scripts, aligning with our maintainability goals. Specifically, we

choose Approach 2 from the design comparison – using Komodo’s TypeScript API and Pangolin’s

TypeScript client in a unified script

68

69

. This script (run in CI or as a Komodo Action) handles

deploying the compose stack and then calls Pangolin’s API to expose it

70

71

. By keeping this

logic in TypeScript, we benefit from robust error handling and logging. For example, the script

can   catch   any   failure   in   Pangolin   registration   and   automatically   rollback   the   Komodo

deployment, or vice versa, ensuring partial deployments don’t linger

72

. Logs and outcomes of

this   process   are   visible   either   in   CI   or   in   Komodo’s   action   logs,   giving   a   clear   audit   trail   of

deployment and exposure steps. Security-wise, the Pangolin API token needed for this is pulled

from 1Password at runtime (or stored as an encrypted GH secret) so it’s not hard-coded. We also

utilize Pangolin’s scoped API key feature (a token that only has rights to manage the specific

domain/site   for   previews)

73

.   This   integration   strategy   means   that   adding   new   services   or

changing the deployment process only requires updating our TypeScript code – a single, version-

controlled source – rather than numerous shell scripts across environments, thereby reducing

maintenance effort

74

.

•

Environment Configuration and Secrets: Our deployment pipeline distinguishes configuration

per   environment.   Using   Pulumi   stacks   and   Komodo’s   config   layering,   we   inject   different

environment   variables   for   dev,   staging,   prod.   Secrets   like   database   URLs,   API   keys,   etc.,   are

referenced   via   environment   variable   placeholders   that   Komodo/CI   fills   from   1Password.   For
instance,   the   Compose   file   might   reference   ${PANGOLIN_API_TOKEN} ;   in   Komodo,   we

configure that variable to be retrieved securely (Komodo might support direct integration with

1Password or we supply it through its CLI at deploy time). 1Password acts as the central vault –

developers do not hardcode secrets anywhere; they request access or use our tooling to pull

needed secrets locally when running things. In CI, we employ the 1Password GitHub Action (or a
small script with  op  CLI) to fetch secrets on the fly. This ensures that rotating a secret (say an

API key) is as simple as updating it in 1Password; all pipelines will automatically use the new

value on the next run. We enforce that no secret is printed in logs or error messages (1Password

and CI masks them). Additionally, our Pulumi code not only creates cloud resources but can also

populate initial secrets into 1Password. For example, after creating the Cloudflare D1 database,

the Pulumi stack outputs the DB ID and we then call 1Password SDK to store that ID under a

known   secret   name

75

76

.   This   way,   the   output   of   one   IaC   step   (new   infrastructure)

immediately becomes input to our apps, without manual copy-paste.

11

•

Modular Deployment Units:  We structure the project into modular components that can be

deployed   independently   if   needed.   For   instance,   the   data   ingestion   pipelines   (Python   scripts

using DLT, etc.) are containerized separately. They can be run on a schedule via Dagster or Cron

on the server. We might deploy them as Docker containers that exit after completion (for batch

jobs) or as a long-running scheduler. Komodo will manage those containers as well, or we use

Dagster’s own scheduler outside Docker. The front-end and API are separate containers. This

microservice   approach,   all   defined   in   Compose,   means   we   can   scale   or   update   parts   of   the

system without affecting others – e.g. deploy a new version of the frontend without redeploying

the ingestion pipeline container, etc. It also means if a component fails, it can be restarted in

isolation.

•

Testing   and   CI/CD:  We   incorporate   a   comprehensive   test   suite   to   ensure   deployments   are

reliable.   Unit   tests   cover   functions   like   data   parsing,   BAML   prompt   formatting,   etc.   More

importantly,  end-to-end tests are run in CI to validate the entire pipeline on a small scale

77

.

For example, we spin up DuckDB in memory, use DLT to ingest a tiny sample, run CocoIndex,

simulate an agent query, and verify the output shape. We also test our Pulumi deployments in a

sandbox environment (Pulumi has the concept of a preview – we use that in CI to ensure our IaC

changes don’t contain errors). The CI pipeline will only proceed to deployment if tests pass. We

treat   the  Docker   images  as   artifacts   –   tagging   them   with   git   SHAs   and   scanning   them   for

vulnerabilities on build.

•

Monitoring and Logging:  Deploy  Dozzle  as part of the stack (accessible via Pangolin on an

admin   subdomain)   to   monitor   container   logs   in   real-time.   This   helps   during   debugging   of

production issues – one can securely view logs of any service through the browser

78

  (with

Pangolin ensuring only authorized users can access this log interface). For resource monitoring,

we rely on the cloud provider (OCI/Hetzner) metrics and plan to add lightweight checks – e.g., a

Cron  job  that  pings  each  service’s  health  endpoint  and  alerts  if  down.  In  the  future,  we  can

integrate a full monitoring stack (Prometheus/Grafana) but initially, the focus is on keeping the

system   simple   and   using   the   tools   at   hand   (Komodo’s   UI   for   container   status,   Cloudflare

analytics for R2 usage, Langfuse for ML performance metrics).

•

Maintainability Practices: The deployment and integration choices emphasize maintainability:

•

All changes go through code review (via PRs and OpenSpec proposals)

79

, ensuring

architectural modifications are discussed and documented.

•

Configurations are declarative and stored in git (Pulumi code for infra, Compose for services),

making recreation or migration of the stack straightforward.

•

The team can spin up a local version of the system using Docker Compose as well (perhaps a

slightly modified compose for local that uses local MinIO instead of R2, etc.). This is documented

so that development and testing are convenient.

•

We periodically back up critical data (the R2 Parquet data, the Cognee graph state, etc.) to an

additional location (perhaps R2 itself is durable, but we could version snapshots).

•

Because the stack avoids proprietary lock-in and uses open formats (Parquet, DuckDB, etc.), even

if we need to migrate cloud providers or replace components, we can do so with minimal pain

38

. For example, if Cloudflare R2 became untenable, we could shift to S3 or another object

store with just config changes in Pulumi, thanks to our use of open standards.

•

Security   and   Access   Control:  Use   Pangolin’s   zero-trust   model   to   limit   access   to   non-public

services. The production frontend might be public, but admin interfaces (like Dozzle, Langfuse

UI) are behind Pangolin requiring login (via PocketID/TinyAuth OAuth, for instance). Cloudflare

12

provides   an   additional   layer   of   security   and   performance   for   public   endpoints:   we   can   put

Cloudflare   proxy/CDN   in   front   of   Pangolin’s   public   sites,   or   even   use   Cloudflare   Tunnel   as   a

fallback   if   needed   (though   Pangolin   covers   much   of   that   need).   1Password   audit   logs   are

monitored to ensure only the service account and authorized devs access secrets.

By   following   this   phased   implementation   plan,   we   cover   everything   from   provisioning   the   cloud

foundations   to   delivering   a   feature-rich   application,   all   while   keeping   the   deployment   process

reproducible   and   secure.   Each   phase   (infrastructure,   pipelines,   frontend,   ML   agents,   and   devops)   is

designed  to  be  modular  and  maintainable,  so  the  project  can  evolve  with  new  requirements.  The

result will be a robust cryptocurrency analytics platform with strong infrastructure-as-code discipline

and AI-driven capabilities, aligned with the OpenSpec guidelines and best practices we’ve set out.

Sources: Key guidance and best practices were drawn from the project’s specification documents and

relevant tool documentation – for example, using Pulumi with 1Password for secret management

1

4

,   adopting   a   layered   data   architecture   with   DuckLake,   CocoIndex,   and   Cognee

40

38

,   and

orchestrating   AI   agents   via   Agno   and   BAML   for   structured   outputs

62

56

.   These   informed   our

approach to ensure the system is cutting-edge yet reliable and easy to manage.

1

2

3

4

75

76

Pulumi TypeScript Guide_ Provisioning Cloudflare D1 & R2 with 1Password

Integration.pdf

file://file_000000000fd472469514e1d7721f8c6c

5

18

26

77

79

project.md

file://file_000000006de472439e50e84e818d9ef3

6

27

28

31

34

36

44

45

46

47

48

49

50

51

52

53

54

Crypto Analysis AI Agent System

Architecture.pdf

file://file_0000000067887243a733737d190a90ed

7

8

64

65

66

67

78

Extending __komodo-pr-deploy__ for Pangolin Integration via Komodo

Actions.pdf

file://file_00000000b48471f4b41f4842a896d9c6

9

10

68

69

70

71

72

73

74

Comparing Approaches for Pangolin Registration after Komodo

Deployment.pdf

file://file_0000000060d471f48c9b81924ecb3375

11

16

17

22

23

24

25

35

37

38

39

40

41

42

43

Integration Plan for a Crypto Analytics & Discovery

System.pdf

file://file_000000002298724688bc83761e3a610b

12

13

14

15

Ingesting Ethereum & DeFi Data Using DLT Hub.pdf

file://file_000000008f447246963bf74fd31b99ad

19

20

21

29

30

55

56

57

58

59

60

61

63

End-to-End Workflow for Analyzing Local Git Repositories

with DLT, CocoIndex, Repomix, Agno, and BAM.pdf

file://file_0000000030947243a1577c6b13b3ee49

32

33

62

Crypto Analytics Project – Document Summaries and Spec Update.pdf

file://file_00000000437071f4b809667ff1225616

13

