Integration Plan for a Crypto Analytics &

Discovery System

Data Ingestion and Historic Archive Integration

Ingestion Pipeline: Begin with a robust data pipeline (e.g. using the  crypto_sources.json  registry)

to continuously fetch both historical and real-time data. The registry defines structured metrics (time-

series data like prices, yields, TVL) and documents (PDFs, HTML pages) across protocols such as Ethena,

Aave, and Pendle

1

. Each source in the registry has a schema (fields like timestamp, protocol, asset,

metric, value, etc.) and parsing logic, ensuring consistency across datasets. This pipeline can use a tool

like DLT or custom scripts to pull API data at intervals and scrape new documents as they appear.

Historic  vs.  Real-Time  Merge:  To  merge  live  data  with  the  historical  archive,  adopt  a  micro-batch

approach. Real-time streams (from DLT feeds or web scrapers) are collected into short intervals (e.g.

every   5   minutes   or   hourly)   and   written   in   the   same   format   as   historical   batches.   Each   micro-batch

appends   new   records   to   the   archive   without   rewriting   large   files.   For   example,   live   metrics   for   the

current day can be buffered and periodically appended to a daily Parquet file. This ensures that up-to-
date data is continually incorporated while preserving historical records. A unified timestamp key (as

defined   in   the   registry’s   primary   keys)   makes   it   easy   to   merge   or   deduplicate   records

2

3

.   The

pipeline marks each record with source and extraction time, so the system can distinguish truly new

data   from   updates.   By   aligning   on   the   registry’s   global   schema   and   keys,   the   live   pipeline   can

seamlessly extend the historical tables without schema conflicts.

Best Practices: Use idempotent writes or versioned batches for reliability – e.g. write daily snapshot

files and use a version tag (date or increment) in filenames to avoid partial updates. If a record gets

updated or corrected, maintain a version history or an “effective_date” field rather than overwriting,

enabling time-travel queries. This approach will feed both the current state and historical states into the

same unified dataset, supporting analyses over long periods as well as “live” views.

Cloudflare R2 for Parquet Data Lake

Archival Storage: Utilize Cloudflare R2 (an S3-compatible object store) as a long-term data lake for all

metric and document data. When the ingestion pipeline parses data, it stores the structured results as

columnar Parquet files in R2. Parquet provides efficient compression and is optimized for analytical

reads (column pruning, predicate pushdown), which is ideal for our use case. Partition the storage by

logical  keys  –  for  instance,  create  folders  by  protocol/metric  or  by  date  –  to  organize  the  data  and

enable selective access (e.g. fetching one protocol’s data without scanning everything). Each Parquet file

corresponds to a batch of records (daily or hourly for metrics, or one file per document for scraped

texts).

Lakehouse Metadata: We integrate DuckLake (DuckDB with the DuckLake extension) as the interface

to this data lake. In practice, DuckLake treats the R2 bucket as the storage layer for table files while

keeping a lightweight SQL catalog of table schemas and partitions

4

. The catalog (which could be a

small DuckDB or SQLite database, possibly stored on R2 or locally) tracks what tables exist, their schema

versions, and pointers to Parquet files. This metadata enables schema enforcement and SQL querying

1

without needing a large centralized warehouse. It also aids discovery: for example, DuckLake’s catalog

can list all available metrics or documents and their last update time – information the front-end can

use to show available data sources.

Access   Patterns:  Clients   or   analysts   can   query   the   archive   through   DuckDB   SQL.   DuckDB   (either

running on a server or compiled to WebAssembly for browser use) can directly query Parquet over

HTTP(S).   Cloudflare   R2’s   S3   API   and   support   for   range   requests   means   DuckDB   can   fetch   only   the

needed byte ranges from each Parquet file on the fly. Following Harvard LIL’s approach, we store the

data   sorted   by   common   query   fields   (e.g.   by   timestamp   or   protocol)   so   that   DuckDB   can   retrieve
.   For   example,   a   query   filtering   protocol   =   'Aave'   AND
relevant   subsets   with   minimal   I/O
timestamp > 2024-01-01  will prompt DuckDB to fetch only the Parquet row groups matching that

5

filter, rather than downloading entire files. This design keeps query latency low and bandwidth costs

down, even as the archive grows. R2’s durability and geo-replication ensure the historical archive is

preserved long-term, while its low cost (comparable to S3) makes the solution sustainable

6

.

Schema Evolution and Versioning: As new metrics or fields are added over time, update the DuckLake

catalog   or   use   an   open   table   format   (like   Apache   Iceberg/Delta   Lake)   on   R2.   These   formats   track

schema versions and file snapshots, allowing the system to evolve without breaking older queries. For

example, if a new field “maturity” is added for Pendle yields, the table format can add that column in a
new schema version while still retaining backwards compatibility for old files. Ensure that each Parquet

file is tagged or named with a schema version if not using a table format, so the reading engine can
adjust   parsing   logic   accordingly.   Versioning   the  dataset   registry  itself   (with   a   version   field   and

change log) is also crucial – it documents changes in data sources or transformations over time, aiding

reproducibility and audit. All these strategies guarantee that the archive remains  extensible  (easy to

add new data sources) and maintainable over years.

Indexing, Embedding, and Data Linking (CocoIndex & Cognee)

Unified Search Index: To enable powerful search across both structured records and unstructured text,

we introduce an indexing layer that bridges these two data types.  CocoIndex  can be employed as an

ETL/indexing engine that converts raw data into embeddings and other index structures. CocoIndex is a

high-performance   framework   for   transforming   data   for   AI   applications,   with   support   for   real-time

incremental processing

7

. We can configure CocoIndex to watch the R2 buckets (or tap directly into

the   pipeline)   for   new   content:   when   a   new   batch   of   documents   or   a   set   of   metric   records   arrives,

CocoIndex transforms them into vector embeddings suitable for semantic search. For example, each

PDF   or   document   page   might   be   converted   into   one   or   more   embeddings   (using   an   NLP   model)

representing   its   content;   similarly,   important   metric   definitions   or   annotations   (like   “sUSDe_APY”   or

derived metrics explanations) can be embedded as short text descriptions so that users can find metrics

by   concept   (e.g.   a   search   for   “stablecoin   yield   spread”   could   retrieve   the   derived   metric   defined   as

fixed_vs_float_spread  in the registry

8

). CocoIndex’s incremental nature means this process can run

continuously, updating the index with new data without reprocessing everything, which keeps live data

searchable  as soon as it’s ingested. The resulting vector data is stored in a vector database (Qdrant,

Pinecone, etc.) or even in DuckDB if using an extension – CocoIndex natively integrates with Qdrant for

storage

9

, ensuring fast vector search over tens of thousands of documents or data points.

Knowledge Graph and Entity Linking:  In parallel,  Cognee  can be used to build a knowledge graph

that links structured and unstructured information. Cognee is an AI memory framework that allows

loading data from 30+ sources into both graph databases and vector stores

10

. Using Cognee, we can

ingest structured metadata (protocol names, asset identifiers, relationships like “Ethena issues USDe

stablecoin” or “Pendle yield token has maturity date”) into a graph database (e.g. Neo4j). We also load

2

document metadata (titles, authors, topics) and even the connections between metrics and documents

(e.g. a document that discusses a specific metric or event can be linked to that metric’s node in the

graph). This graph of entities and relationships provides context that pure text embeddings might miss

– for instance, Cognee can represent that  Ethena  is related to  Aave  (if one protocol’s yield feeds into

another), or that a PDF report is an audit for a specific protocol. The vector store and graph can be used

together: store text embeddings in the vector index with metadata tags, and store the same metadata

and relationships in the graph. This hybrid setup allows “semantic + symbolic” search. A user query can

first do a  vector similarity search  (find relevant texts by meaning) and then filter or rerank results

based on graph relationships or structured filters (e.g. only show results related to a certain protocol or

date range). For example, if a user searches "Ethena insurance fund risk", the system can use the vector

index to find the Insurance Fund PDF content and any relevant time-series anomalies, then use the

graph to ensure those results are indeed about Ethena and its risk management, not some unrelated

protocol.

Metadata in Index: Both CocoIndex and Cognee support attaching metadata to each indexed item. We

embed key fields from the global schema as metadata attributes on vectors and graph nodes – such as
protocol:   Ethena ,
  timestamp:
2025-10-01 , etc. These attributes enable faceted and filtered search directly on the index. Modern

  category:   risk_docs ,

  metric:   sUSDe_APY ,

vector   databases   like   Qdrant   let   us   do   hybrid   queries   (e.g.   semantic   similarity   constrained   by   a
structured filter). This means the front-end could ask, “find documents similar to this query vector and

where protocol = 'Aave'” – implementing a structured-unstructured hybrid search under the hood. By

linking   the   embeddings   with   the   knowledge   graph,   we   can   even   do  contextual   re-ranking:   for

instance, boost results that connect to entities the user has filtered on, or group results by protocol. The

outcome is an index that treats historic + live data as one knowledge space – newly ingested data is

immediately   embedded   and   linked   to   related   entities,   and   users   can   traverse   from   one   piece   of

information to another (e.g. from a metric’s time-series to a document explaining that metric) easily.

Best Practices: Keep the embedding models and graph schema aligned with domain knowledge. Use a

financial   or   crypto-specific   language   model   for   embeddings   to   capture   domain   jargon.   Update

embeddings periodically if the language/model evolves (ensuring backward compatibility by versioning

the vector index if needed). Also, implement  quality checks  – for example, use confidence scores or
manual curation for critical links in the knowledge graph (as the registry’s  confidence  field suggests

11

). This prevents spurious connections from polluting the search results. By combining CocoIndex

and Cognee, the system gains both  deep semantic search  capability and  intuitive linkages  across

data modalities, which will greatly enhance discovery.

Ducklake-Powered Discovery UI (Search & Metadata Frontend)

Discovery   Interface:  Ducklake   will   serve   as   the   core   of   the   user-facing   discovery   and   search

experience. We propose a web-based UI (e.g. a single-page application or static site) that leverages

DuckDB as a SQL query engine and the pre-built indexes. One proven approach is the  Harvard LIL

client-side model: load a DuckDB-Wasm engine in the browser, which attaches to the Cloudflare R2

Parquet files via HTTP. This allows the user’s browser to directly perform fast SQL queries over the

archived   data  without   a   dedicated   server,   combining   low   operational   cost   with   interactive

performance

5

12

. The UI can present a search bar and filtering options (facets) for users to query

the data. When a query is issued, two things happen in tandem: (1) DuckDB (Ducklake) executes any

structured query components (like filters, aggregations, or time-series retrieval) on the Parquet data,

and   (2)   the   vector   search   (via   an   API   or   WebAssembly-based   vector   search   library)   finds   relevant

unstructured   results   (documents   or   embedded   text).   The   front-end   then   merges   these   results,

displaying them in a unified, user-friendly way.

3

Structured & Unstructured Hybrid Search: Users should be able to seamlessly search across metrics

and documents. For example, a user might search “Aave stablecoin yield last month” – the system could

interpret this to fetch structured data (e.g. Aave’s stablecoin yield metric time-series from last month,

via SQL on the metrics table) and unstructured results (e.g. any research reports or news documents

about Aave yields). The UI could show a chart or summary statistic for the metric alongside a list of

relevant documents. To support such use cases, we design intuitive search affordances: a query parser

can   detect   known   entities   or   keywords   (“Aave”   matches   a   protocol   name,   “yield”   matches   a   metric

category) and automatically apply those as filters. This makes the experience feel intelligent – users can

enter natural queries without manually toggling filters for every field. Under the hood, DuckDB can

perform
query
filtered
( WHERE   protocol='Aave'   AND   metric   CONTAINS   'yield'   AND   timestamp   BETWEEN   ... )

metric

the

while   the   vector   index   (via   Cognee)   retrieves   semantically   similar   text   passages   mentioning   Aave’s

yields.

Intuitive UI Elements:  We incorporate  faceted browsing  and  inline metadata  to guide exploration.

The UI will present clickable facets (e.g. a sidebar or dropdowns for  Protocol,  Data Type,  Date Range,

Metric Category). These facets are powered by the metadata in DuckLake’s catalog or can be fetched via
SQL (e.g.   SELECT DISTINCT protocol FROM metrics_table ). For instance, a user could filter to

only see results related to Ethena or restrict the search to “risk_docs” category to find only audit and
risk analysis PDFs. We ensure that selecting a facet updates both the structured query and the vector

query  filters.  The  interface  should  also  display  inline  metadata  with  each  result:  for  a  metric  data

result, show its source, timestamp, and units; for a document snippet, show its title, date, and protocol

context.   This   echoes   library   discovery   systems   where   each   search   result   is   accompanied   by   key

attributes (author, year, subject tags) to help users evaluate relevance. By storing rich metadata in the

index   and   catalog,   we   can   show,   for   example,  “Ethena   –   Insurance   Fund   Analysis   PDF   (2023,   Risk

Document)” beneath a document result snippet, or “Aave – Stablecoin Yield APY – 2025-10-30: 4.5%” for a

metric point. These cues make the system’s content more transparent and navigable.

Ducklake as Metadata Frontend:  Ducklake’s catalog also serves a  metadata browser  role. We can

build a section of the UI for “Data Catalog” or “Sources”, which directly pulls from the dataset registry

and DuckLake catalog to list what datasets are available. This might look like a list of protocols -> assets

->   metrics,   each   with   descriptions   and   links   to   documentation.   Because   the   registry   JSON   includes

descriptions and even formula notes for derived metrics
, we can expose those in the UI. DuckDB
can query a small table of sources (populated from  crypto_sources.json ) to allow users to discover

8

data by browsing instead of searching. Ducklake, in effect, becomes not just the query engine but the

content index  for all available data. This is analogous to how library portals list collections and allow

filtered search within them. The user could, for example, navigate to “Pendle” in the catalog view and

see all metrics (with definitions) and documents for Pendle, then click a particular metric to view its

historical chart, or enter the search interface pre-filtered to that context.

Performance Considerations: To keep the UX snappy, leverage DuckDB’s strengths and static hosting.

The Harvard LIL experiment demonstrated that a static site with DuckDB-Wasm querying Parquet can

support   interactive   search   and   filtering   entirely   in-browser

13

.   We   will   follow   similar   optimizations:

compress   and   partition   Parquet   data   so   queries   scan   minimal   data,   use   DuckDB’s   full-text   search

extension (if needed) for any simple keyword filtering on text columns, and use caching (e.g. Cloudflare

CDN)   for   frequently   accessed   Parquet   files.   For   the   vector   search   part,   we   can   either   call   out   to   a

lightweight search API (if a server component is acceptable) or use a JavaScript WASM library for vector

search if one is available (some vector DB clients or approximate nearest neighbor libraries can run in-

browser). Even if we use a server-side vector search, it can be a stateless microservice just for queries,

which keeps the overall architecture mostly static. Ducklake’s role here is crucial: it provides the  SQL

4

query layer and metadata backbone, but the heavy lifting is done client-side, aligning with the LIL

philosophy of minimal server infrastructure for discovery.

Schema, Versioning, and Metadata Strategy for Discoverability

Global   Schema   &   Facets:  Adopting   a   consistent  global   schema  across   datasets   (as   seen   in   the
registry’s   fields_common )   is   fundamental   for   hybrid   search
.   Common   fields   like   protocol ,
asset ,   timestamp ,   category , and   metric   are used as  facetable metadata  everywhere. This

14

uniformity   means   the   discovery   UI   can   treat   disparate   data   sources   as   part   of   one   large   table   for

filtering purposes. For instance, whether a data point comes from DeFiLlama or CoinGecko, it will still
have   protocol   =   Ethena   or   Aave   if   relevant,   so   a   filter   for   protocol   will   catch   both.   Define

controlled vocabularies for these fields (perhaps maintained in the registry): e.g. enforce that Ethena’s

stablecoin   is   always   labeled   “USDe”   in   the   asset   field,   not   sometimes   “USDe”   and   other   times

“ETHenaUSD”. This avoids fragmentation in search results and facet counts. Where possible, include

human-readable descriptions for each field and tag. The system can then display tooltips or info icons

next to facets – e.g. hovering over metric: sUSDe_APY could show “Staked USDe APY – the yield rate for

Ethena’s sUSDe token”. Such inline explanations (drawn from the registry notes or a data dictionary)

embody the “intuitive affordances” that help users make sense of data without reading lengthy docs.

They make the discovery experience self-documenting.

Schema   Versioning:  As   new   protocols   or   metrics   are   added,   update   the   schema   in   a   backward-

compatible   way.   If   entirely   new   fields   are   needed,   add   them   as   nullable   columns   so   older   records

remain   valid.   When   deprecating   fields,   retain   them   in   the   archive   but   mark   them   as   deprecated   in

metadata   (so   UI   can   hide   them   by   default).   It’s   wise   to   maintain   a  schema   version   history  in   the

catalog.   For   example,   Ducklake’s   catalog   DB   could   have   a   table   listing   dataset   versions,   with   fields

added/removed and dates. This not only aids internal management but could be exposed on the front-

end (an “About this dataset” page showing its revision history, which is useful for power users and

reproducibility). In the spirit of LIL’s library philosophy, transparency in how the data has changed over

time enhances trust and long-term usability.

Metadata Enrichment:  Build out  rich metadata  to power advanced discovery. Each document can

have metadata like author, publish date, or summary extracted (for PDFs, store the title, headings, etc.,
which the registry’s PDF parser already captures in fields like   doc_title   and   section

). Each

15

metric   or   time-series   might   have   metadata   like   data   source   (CoinGecko,   DeFiLlama   –   already   in
source  field), confidence or quality score, and perhaps links to original source URLs
. By indexing
the  provenance_url  or source notes, we can allow users to trace back to primary data (an important

16

feature for researchers). Additionally, consider adding entity identifiers where possible – e.g. tagging

that “ETH” asset corresponds to a Coingecko coin ID or a contract address. This could later help join with

external datasets or visualize on-chain data. Cognee’s graph can hold these identifiers, making it easier

to merge outside knowledge or support queries like “show me everything related to this Ethereum

address”.

Faceted Navigation & Query Affordances: To build LIL-style discovery, design the schema to support

faceted navigation  out of the box. For example, ensure categorical fields are standardized for easy

grouping (yes/no fields, categorical enums for event types, etc.). If a field is numeric but often used for

range filtering (e.g. dates or values), consider precomputing histogram buckets or summary tables to

aid   the   UI   (the   static   front-end   could   then   show   a   timeline   slider   or   a   value   range   filter).  Query

affordances  like saved searches or example queries can be enabled by storing some preset queries in

the  catalog.  For  instance,  have  a  metadata  table  of  “common  questions”  mapped  to  SQL  or  search

queries (like “Top 5 protocols by TVL last 30d” or “All audits for Pendle”). The UI can surface these as

5

clickable   examples,   helping   users   discover   insights   with   one   click.   This   idea   resonates   with   library

discovery systems offering curated starting points for exploration.

Long-Term Discoverability: To ensure the system remains discoverable long-term, even as technology

evolves, stick to open standards and self-describing data. Parquet and DuckDB are open formats; even

if Ducklake is not maintained in the far future, the data can be read by any Parquet reader and the

schema   understood   from   the   embedded   metadata.   We   will   also  document   the   dataset  (perhaps
publish the  crypto_sources.json  and schema definitions on a project website or Git repo) so that

future   users   can   understand   the   context   of   each   data   field.   Following   Harvard   LIL’s   example,   we

prioritize   solutions   that   minimize   maintenance:   a   static   object   store   for   data,   and   client-side

computation for discovery

17

18

. This reduces dependence on complex servers that could become

obsolete. If we implement the search UI as a static app, it could be archived and served indefinitely (just

like a set of web pages) as long as the data files remain accessible. Embracing this philosophy, our

integration plan yields a layered architecture where each component is loosely coupled and replaceable

– ingestion can swap to a new source, storage could migrate to another S3 service, DuckDB could be

replaced with another query engine – yet the overall system will continue to function and be extensible.

Layered Architecture Summary

To summarize, the system is organized in clear layers for extensibility and longevity:

•

Data Sources & Ingestion Layer: Uses the structured registry to pull both historical and

streaming data (metrics and docs) from multiple crypto platforms. Clean, structured ingestion

with incremental updates feeds the system continuously

1

.

•

Storage & Lakehouse Layer: Cloudflare R2 serves as the durable data lake, storing all data as

Parquet. The Ducklake (DuckDB) engine provides a SQL analytics layer and maintains a catalog of

dataset schemas and partitions

4

. This layer ensures all data (historic and new) is uniformly

accessible via SQL.

•

Indexing & Linking Layer: CocoIndex transforms new data into vector embeddings for

semantic search, and Cognee builds a knowledge graph linking entities across datasets

7

10

.

A vector database and graph database work in tandem to index content, enabling hybrid search

(text + structured filters) and intelligent linkages (e.g. connecting metrics to related documents).

•

Discovery & Search UX Layer: A front-end application (DuckDB-Wasm powered or lightweight

server) allows users to query and explore data. It leverages the Ducklake SQL engine for

structured queries and the embedding/graph index for semantic lookup. The UI provides rich

search with facets, filters, and context, following the Harvard LIL philosophy of an intuitive,

library-like discovery experience (browse, search, filter in one place)

13

.

Each layer is decoupled but integrated through well-defined interfaces (Parquet files, SQL queries, API

calls to the vector/graph index). This modular design means the system can grow (add new protocols or

metrics easily), adapt (swap out components like the vector DB if needed), and persist (data remains

accessible   in   open   formats).   By   combining   the   strengths   of   all   components   –   the   meticulous   data

registry, the Ducklake lakehouse, modern indexing techniques, and user-centric design – the platform

will deliver powerful analytics and discovery capabilities for crypto data, both now and in the long run.

Sources:  The   integration   plan   draws   on   the   Ethena/Aave   data   registry

1

,   DuckLake   lakehouse

architecture

4

,   Harvard   LIL’s   2025   data   discovery   approach

5

13

,   and   modern   AI   indexing

frameworks CocoIndex

7

 and Cognee

10

 to ensure a comprehensive, future-proof solution.

6

1

2

3

8

11

14

15

16

crypto_sources.json

file://file_0000000080bc71f49724a066b6bebdf0

4

ducklake.md

https://github.com/dlt-hub/dlt/blob/4a431d60edca9ecf2bf8a4f4390faa5b37217998/docs/website/docs/dlt-ecosystem/

destinations/ducklake.md

5

6

12

13

17

18

Rethinking Data Discovery for Libraries and Digital Humanities | Library

Innovation Lab

https://lil.law.harvard.edu/blog/2025/10/24/rethinking-data-discovery-for-libraries-and-digital-humanities/

7

9

CocoIndex - Qdrant

https://qdrant.tech/documentation/data-management/cocoindex/

10

Frameworks - Qdrant

https://qdrant.tech/documentation/frameworks/

7

