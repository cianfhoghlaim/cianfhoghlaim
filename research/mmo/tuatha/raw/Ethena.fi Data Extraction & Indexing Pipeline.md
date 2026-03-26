Ethena.fi Data Extraction & Indexing Pipeline

Overview & Objectives

This implementation outlines a Docker Compose-based pipeline to crawl all public-facing content from
ethena.fi  (including subdomains like   docs.ethena.fi   and   blog.ethena.fi ), then process and

index that content for semantic search. The pipeline uses the following components:

•

Crawl4AI: To scrape pages and produce clean Markdown content, along with full-page

screenshots and optional PDF snapshots

1

2

.

•

CocoIndex: To chunk the scraped content into LLM-friendly segments, extract metadata (title,

date, content type), and generate vector embeddings for each chunk

3

4

. This yields

structured JSON/Parquet outputs (one record per content chunk with text, metadata, and

embedding).

•

DuckLake: To store all artifacts (structured text data, screenshots, PDFs) in a data lakehouse

format (Parquet files with ACID metadata). DuckLake’s table format ensures reliable storage with

features like snapshots and time-travel on Parquet data

5

6

.

•

DLT + LanceDB: DLT is an open-source data loading tool that simplifies moving data into
. We use DLT to load the processed JSON records (including embeddings) into
LanceDB

7

LanceDB, an open-source vector database, for efficient semantic search. LanceDB will store the

chunk embeddings and allow vector similarity queries.

Key Goals: Achieve a fully containerized pipeline (no external orchestrators like Dagster) that can be

run locally via Docker Compose. The output will be a LanceDB index of ethena.fi content, with each

record   containing   chunk   text,   embedding,   and   metadata   (e.g.   page   title,   date,   URL,   type),   and   all

original content/snapshots stored in a DuckLake-managed data repository.

1. Crawling Ethena.fi with Crawl4AI

1.1 Crawl Configuration

We use  Crawl4AI  to recursively crawl the ethena.fi website and its subdomains. Crawl4AI returns a
CrawlResult   object   for   each   page,   containing   everything   needed   –   the   HTML,  clean   Markdown

output, and optional screenshot/PDF data
and limit scope to Ethena’s domains. Key settings in the  CrawlerRunConfig  include:

. We enable deep crawling with a breadth-first strategy

1

•

deep_crawl_strategy = BFSDeepCrawlStrategy(max_depth=N,

include_external=False) : Ensures the crawler follows internal links up to N levels deep

(tunable as needed) but does not follow external domains

8

9

. We will initiate separate crawl

runs for each subdomain to ensure those are included (since subdomains might be treated as

external from the root domain).
exclude_external_links = True : An extra safeguard to skip any links outside the ethena.fi

•

•

11

10

domain family
. This means the crawl will ignore third-party links (social media, etc.).
Allowed Domains: We configure allowed hostnames as  ethena.fi ,  docs.ethena.fi ,
blog.ethena.fi  (and any other relevant subdomains) so the crawler treats them as internal.

This can be handled by running multiple seeds or by a custom filter. In practice, we will seed the

1

crawler with multiple start URLs (e.g. the homepage, the docs index, and the blog index) and

handle each domain separately to ensure full coverage.

1.2 Capturing Markdown, Screenshots, and PDFs

Crawl4AI will generate clean Markdown for each page by default, which is ideal for LLM consumption.

We also instruct the crawler to capture full-page  screenshots  and  PDF snapshots  for archival in our

data lake. These are enabled via the run configuration flags:

from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BFSDeepCrawlStrategy

from crawl4ai.deep_crawling import BFSDeepCrawlStrategy

start_urls = ["https://ethena.fi", "https://docs.ethena.fi", "https://

blog.ethena.fi"]

# seed URLs

crawl_cfg = CrawlerRunConfig(

deep_crawl_strategy = BFSDeepCrawlStrategy(max_depth=3,

include_external=False),

screenshot=True,

# capture full-page screenshot (base64 PNG)

pdf=True,

# generate PDF of page

exclude_external_links=True,

# ... other options like timeout, concurrency can be set here

)

Note:  Setting   screenshot=True   means   each   result.screenshot   will   contain   a
base64-encoded PNG image, and   result.pdf   will contain raw PDF bytes
. We will
later write these to files. We choose  max_depth=3  (for example) to cover pages up to 3

2

clicks away from the start; this can be adjusted based on site structure. Concurrency can

also be tuned in Crawl4AI for faster crawling, though be mindful of site load.

1.3 Running the Crawler (Docker Service)

In Docker Compose, we define a  crawler  service using a Python image with Crawl4AI installed. The
crawler will execute a script (e.g.,  crawl_ethena.py ) that:

1.

Launches the AsyncWebCrawler and calls  arun_many()  with our list of seed URLs and the

above configuration. This will concurrently crawl the main site, docs, and blog, each constrained

to its domain (since each seed’s domain is treated as the “root” for that crawl)
Iterates over the returned list of  CrawlResult  objects. For each result, if  result.success  is

.

8

9

2.

True, it extracts the content and saves:
Markdown Content: We save  result.markdown.raw_markdown  to a  .md  file (or  .txt ).

3.

Filenames can be derived from the page URL (e.g., replacing special characters with
underscores). For example, a page  https://docs.ethena.fi/getting-started  could be
saved as  docs.ethena.fi_getting-started.md . All markdown files are stored under a
volume directory (e.g.  /data/markdown ).
Screenshot Image: If  result.screenshot  is present, we decode the base64 and save it as a
.png  file
docs.ethena.fi_getting-started.png  will correspond to the above page.
PDF Snapshot: If  result.pdf  is present, we write the bytes to a  .pdf  file
docs.ethena.fi_getting-started.pdf .

. We use the same base name as the markdown file. For instance,

, e.g.,

14

12

13

4.

5.

2

Each saved file’s path can also be logged or recorded for later reference. We ensure the file structure in

the   shared   volume   clearly   groups   content   by   domain   or   type   for   easier   management   (e.g.,   using
subfolders for  markdown/ ,  screenshots/ ,  pdfs/  within the data volume).
3. Captures basic  metadata  for each page: we extract the page  title  (e.g., from the HTML   <title>

tag or the first markdown heading) and note the source URL. If the page is a blog post, we attempt to

extract the publication date (e.g., by looking for date strings in the content or known metadata fields).

This metadata can be stored alongside the markdown – for example, as a YAML front-matter in the

markdown file or as a separate JSON mapping file. We also infer a content type for the page: if the URL
contains   blog.ethena.fi ,   we   tag   it   as   "Blog   Post" ;   if   it’s   under   docs.ethena.fi ,   tag   as
"Documentation" , otherwise  "Web Page" . These tags will be used later in the index metadata.

Extensibility:  Crawl4AI   supports   advanced   filtering   and   scripting.   In   this   setup,   we   use   the   default

Markdown   generator  for   clean   text   output,   which   is   typically   sufficient

1

.   If   needed,   one   could

customize   content   extraction   (e.g.,   skip   navigation   menus)   using   Crawl4AI’s   content   filters   or

FitMarkdown settings, but we assume the default output is acceptable for indexing. We also enable

Crawl4AI’s   automatic   handling   of   lazy-loaded   content   and   dynamic   pages   (its   browser   engine   will

execute JS by default), ensuring we capture fully rendered pages.

2. Content Processing with CocoIndex

After crawling, we have a collection of markdown files (and associated media) stored in the shared
volume. The   cocoindex   service  will load these files, chunk and embed the content, and produce

structured outputs for indexing.

2.1 Ingesting Crawled Content

CocoIndex   provides   a   high-level  flow   definition  API   for   processing   data.   We   will   use   the  LocalFile

source  to   read   all   markdown   files   from   the   crawl   output   directory.   In   a   Python   script   (run   by   the

cocoindex container), we define a flow similar to:

import cocoindex

from cocoindex import FlowBuilder, DataScope

@cocoindex.flow_def(name="EthenaIndexing")

def ethena_flow(flow_builder: FlowBuilder, data_scope: DataScope):

# Source: read all markdown files in the shared volume

data_scope["docs"] = flow_builder.add_source(

cocoindex.sources.LocalFile(path="/data/markdown")

# mount from

crawler output

)

# The LocalFile source yields fields: 'filename' and 'content' for each

file

15

16

.

# Collector to gather processed chunk records

indexed_chunks = data_scope.add_collector()

# Process each document

with data_scope["docs"].row() as doc:

# 1. Split content into chunks

doc["chunks"] = doc["content"].transform(

3

cocoindex.functions.SplitRecursively(),

language="markdown", chunk_size=2000, chunk_overlap=500

)

# SplitRecursively uses structure-aware rules (for markdown: it first tries

to split by H1, H2 headings, then paragraphs, etc.) to produce cohesive

chunks

17

18

.

# The chunk_size of 2000 bytes with 500 bytes overlap ensures chunks

are within LLM context window and retain some overlap for context continuity

19

20

.

# 2. Embed each chunk's text into a vector

with doc["chunks"].row() as chunk:

chunk["embedding"] = chunk["text"].transform(

cocoindex.functions.SentenceTransformerEmbed(model="sentence-

transformers/all-MiniLM-L6-v2")

)

# We use a lightweight SentenceTransformer model (MiniLM-L6-v2)

for embeddings.

# This 384-dimensional embedding is a good balance of speed and

quality

21

22

, suitable for semantic search.

# 3. Collect the chunk with metadata

indexed_chunks.collect(

url=doc["filename"],

# using 'filename' as an

identifier (we will later map this to the page URL)

title=extract_title(doc["content"]),# pseudo-code: function

to extract title (e.g., from markdown or stored metadata)

content_type=derive_type(doc["filename"]), # derive "Blog

Post", "Documentation", etc. from filename or path

text=chunk["text"],

embedding=chunk["embedding"]

)

# (Optional) Additional transforms can extract more metadata, e.g., parse

dates from text if needed.

In the above flow, each markdown file becomes a  doc  record. We use  SplitRecursively  to chunk

the markdown content. This method attempts to split at semantic boundaries – for markdown, it will

prefer splitting by section headings and paragraphs rather than cutting off mid-sentence

17

. We set a

chunk target size of ~2000 bytes (~300-500 words) with up to 500 bytes overlap. This approach aligns

with best practices for Retrieval-Augmented Generation: it creates self-contained chunks that fit LLM

context windows, with a slight overlap to mitigate context loss between chunks

23

24

.

Each   chunk’s   text   is   then   passed   to   SentenceTransformerEmbed   with   the   all-MiniLM-L6-v2

model. CocoIndex’s built-in  SentenceTransformer integration  loads this model locally and outputs a

384-dimensional embedding vector
specific  E5  or  instructor  model – but MiniLM is a solid default

21

22

).

. (You can swap in a different model if needed – e.g. a domain-

4

We  collect  each   chunk   along   with   relevant   metadata:   the   url   (here   we   use   the   filename   as   a
placeholder, which includes the page path; we will later resolve it to the full URL if needed), the  title
(extracted via a helper – for instance, if the markdown content begins with  # Title  we can use that),
the  content_type  (from our earlier heuristic), the chunk  text , and the  embedding  vector.

2.2 Running the CocoIndex Flow

The CocoIndex container will run the above flow to process all files. CocoIndex requires a database

backend for tracking flow state (to support incremental updates). We include a lightweight PostgreSQL
. The  cocoindex  service will
container in our Docker Compose as a metadata store for CocoIndex
use an environment variable (e.g.,  COCOINDEX_DATABASE_URL ) to connect to this Postgres. Since our

25

pipeline is batch-oriented (one-off indexing), the DB is mainly to satisfy CocoIndex’s requirements; it will

record the flow execution and can enable re-running incrementally if new pages are added later.

When   the   ethena_flow   runs,   CocoIndex   will   iterate   through   all   markdown   files   and   output   the

collected chunk records. We can choose an export mechanism for these results:

•

Export to Parquet (DuckLake): To integrate with DuckLake, we can export the collected data to

Parquet files. CocoIndex supports custom or built-in targets for exports; for example, it has built-

in support for Postgres and vector databases (PGVector, Qdrant, LanceDB, etc.)

26

27

. Instead

of directly exporting to LanceDB via CocoIndex, we will export to a Parquet file (or a directory of

files) in the shared data volume. This can be done via a CocoIndex Custom Target that writes
JSON/Parquet, or simply by collecting the results in-memory and writing out using pandas/

DuckDB. For clarity, we might use a snippet after the flow run like:

# After running the flow (e.g., cocoindex.run_flow(ethena_flow)):

records = indexed_chunks.get()

# pseudo-method to retrieve all collected

records

import pandas as pd

df = pd.DataFrame(records)

df.to_parquet("/data/output/ethena_chunks.parquet")

(This assumes our container has pandas or we could use DuckDB SQL to write out the results to Parquet

using DuckLake’s format.)

•

Structured JSON: Alternatively, we could output each record as a JSON line (NDJSON) if

preferred. For large data, Parquet is more efficient and integrates better with DuckLake.

At   this   stage,   we   also   save   the  screenshots   and   PDFs  (already   produced   by   the   crawler)   into   the

DuckLake storage. In practice, since they are files on disk, our “DuckLake” is essentially the volume

directory   (which   could   be   on   local   disk   or   an   S3   bucket   if   configured).   DuckLake’s   format   does   not
mandate how to store binary assets, so we simply keep images in a folder (e.g.,  /data/screenshots )
and PDFs in   /data/pdfs . We do, however, include references (file paths or URLs) to these in our

structured   data   if   needed.   For   example,   we   might   add   a   field   in   the   chunk   records   for
screenshot_path   or   an   S3   URL   if   we   uploaded   them.   This   way,   if   a   search   result   is   found   via

LanceDB, one could retrieve the screenshot or PDF for that page from the data lake for context.

DuckLake Integration: By writing our structured content to Parquet and storing it (with snapshots of

when the crawl happened), we effectively leverage DuckLake. DuckLake uses a catalog (which could be

a DuckDB or Postgres database) to track table metadata and Parquet files as the data store

28

5

. In a

5

simple local setup, we can use DuckDB itself as the catalog. For example, we could run a DuckDB query

in the cocoindex container after writing the Parquet:

INSTALL ducklake;

LOAD ducklake;

CREATE DATABASE my_ducklake LOCATION '/data/ducklake_metadata.ducklake';

--

DuckLake catalog

ATTACH 'ducklake:./data/ducklake_metadata.ducklake' AS ducklake_db;

USE ducklake_db;

CREATE TABLE ethena_chunks AS SELECT * FROM read_parquet('/data/output/

ethena_chunks.parquet');

This   would   register   the   Parquet   as   a   DuckLake-managed   table   (enabling   future   updates   with   ACID

guarantees). However, this step is optional; one could also manage the Parquet files directly. The key
point is that all data artifacts now reside in our DuckLake storage (the  /data  volume): structured

chunk data in Parquet, and media in file form.

3. Index Loading with DLT and LanceDB

The final stage is to load the processed data into  LanceDB  for fast vector search. We use  DLT (Data

Loading Tool)  to do this with minimal code. DLT’s LanceDB integration allows ingesting from almost

any source (files, dataframes, etc.) into LanceDB, with automatic schema inference and even on-the-fly

embedding if needed

7

29

.

3.1 LanceDB Setup

We include a  lancedb  service or simply treat LanceDB as an embedded library. LanceDB can operate
in-process using the local filesystem (it will create a directory for the dataset, e.g.,  .lancedb ). In our
Docker Compose, we’ll use the  dlt  service container to perform the loading; it will create the LanceDB

database files on the shared volume (so they persist). Optionally, we could run a LanceDB server (if

using LanceDB Cloud or a REST service), but for local use it’s not necessary.

3.2 DLT Pipeline for Loading

In the  dlt  service (a Python container with  pip install dlt[lancedb]  done), we write a script
load_to_lance.py  that reads the output from CocoIndex and loads it:

import dlt

import pandas as pd

# Read the processed chunk data from Parquet

df = pd.read_parquet("/data/output/ethena_chunks.parquet")

# (If instead we had JSON/NDJSON, we could use json library or dlt resource

to stream records)

# Define a simple DLT resource (generator) from the DataFrame

def ethena_chunks_source():

6

for record in df.to_dict(orient="records"):

# Ensure any numpy types or non-serializable fields are converted (if needed)

yield record

# Initialize a DLT pipeline for LanceDB

pipeline = dlt.pipeline(pipeline_name='ethena_pipeline',

destination='lancedb', dataset_name='ethena_index')

# Run the pipeline with our source

info = pipeline.run(ethena_chunks_source())

print(info)

A few notes on this code:

•

The DataFrame contains columns like  url ,  title ,  content_type ,  text ,  embedding
(where  embedding  is a list of floats). DLT will automatically normalize this nested data and

infer the schema for LanceDB
We do not ask DLT to embed the text, since we already have  embedding  vectors from

. Each chunk record will become a row in LanceDB.

30

•

CocoIndex. (If we hadn’t embedded, DLT could embed text during load by using
pipeline.run(dlt.destinations.adapters.lancedb_adapter(source,

•

embed=<field>))  as shown in LanceDB docs, but here it’s unnecessary
The LanceDB dataset (table) will be named  ethena_index  and stored in a local LanceDB
directory (by default, DLT will use a  .lancedb  folder or the provided  uri  in secrets). In our

.)

31

case, since we didn’t specify a LanceDB Cloud URI, it will create a local LanceDB in the volume,
likely under  .dlt  or  .lancedb . We can configure the storage path via DLT’s config if needed
(e.g., set  destination.lancedb.credentials.uri = "/data/lancedb"  in
config.toml ).

3.3 Running the DLT Load

When we run  docker compose run dlt , the script will execute and insert all records into LanceDB.
Under the hood, LanceDB will treat the  embedding  field as a vector field. DLT’s LanceDB integration

can automatically create a vector index on that field. By default, LanceDB uses an optimized index (like

HNSW)   for   similarity   search.   We   can   confirm   that   each   record   is   stored   with   the   embedding   and

metadata by querying LanceDB (for example, using LanceDB’s Python API in the same container or

connecting via DuckDB with the Lance driver).

Verification:  For a quick test, we might open a LanceDB interactive session (using LanceDB’s Python

client) to ensure data is loaded. For example:

import lancedb

db = lancedb.connect("/data/lancedb")

# path to LanceDB directory if

specified

tbl = db.open_table("ethena_index")

print(tbl.count(), "records loaded")

# Perform a sample similarity search

results = tbl.search("What is Ethena's investment

strategy?").limit(3).to_df()

print(results[["title", "text", "score"]])

7

This would use  LanceDB’s internal embedding model (if configured)  or  more likely, since  we  stored

embeddings, we should use a vector query. Instead, we can take an embedding of a query (using same
model MiniLM) and call  tbl.search_vector(query_embedding) . However, describing query usage

is beyond scope – the main goal is to have the data indexed.

DLT Advantages: Using DLT, we benefited from automatic handling of data types and schema. DLT is

also capable of incremental loads – if we re-run the pipeline with new data, it can append or update

the LanceDB dataset, which fits well with our DuckLake-managed storage (e.g., if Ethena’s site content

updates, we could crawl again and use DLT to upsert new records). DLT’s integration also allowed us to

do this in “a few lines of code” without manually interfacing with LanceDB’s vector index APIs

32

.

4. Docker Compose Setup

All steps are containerized, ensuring reproducibility. Below is an outline of the  docker-compose.yml

with key services:

version: '3.8'

services:

crawler:

build:

context: ./crawler

# contains Dockerfile that installs crawl4ai and

playwright dependencies

volumes:

- ./data:/data

# share data with host and other services

environment:

- PLAYWRIGHT_HEADLESS=1

# example env for headless mode

command: ["python", "crawl_ethena.py"]

# The crawler container runs the crawl then exits.

cocoindex:

build:

context: ./cocoindex

# Dockerfile installing cocoindex, sentence-

transformers, duckdb, etc.

depends_on:

- crawler

- db

volumes:

- ./data:/data

environment:

# ensure DB is up for cocoindex

- COCOINDEX_DATABASE_URL=postgres://postgres:password@db:5432/postgres

command: ["python", "run_index_flow.py"]

# This will execute the cocoindex flow and write outputs to /data/output.

db:

image: postgres:15-alpine

environment:

- POSTGRES_PASSWORD=password

- POSTGRES_HOST_AUTH_METHOD=trust

volumes:

- pgdata:/var/lib/postgresql/data

8

dlt:

build:

context: ./dlt

# Dockerfile installing dlt[lancedb], lancedb, pandas

depends_on:

- cocoindex

volumes:

- ./data:/data

command: ["python", "load_to_lance.py"]

# This loads the Parquet/JSON output into LanceDB and then exits.

# (Optional) lanceviewer:

#   image: ghcr.io/lancedb/duckdb-http:latest  # an example UI or HTTP for

LanceDB if needed

#   ports: ["8000:8080"]

#   volumes:

#     - ./data:/data

#   command: ["--db", "/data/lancedb"]  # Serve LanceDB via DuckDB HTTP for

queries

We   use  shared   volumes  to   pass   data   along   the   pipeline:   the   crawler   writes   to   ./data ,   the
cocoindex   reads   from   and   writes   to   ./data ,   and   dlt   reads   from   there   as   well.   This   avoids
complicated networking or file transfer between stages. The   depends_on   ensure a rough ordering

(crawler   →   cocoindex   →   dlt),   though   in   practice   we   may   run   each   step   sequentially   (e.g.,   running
docker compose up crawler , then  cocoindex , etc., to monitor outputs).

Each service’s Dockerfile is straightforward: -  crawler Dockerfile:  base   python:3.10   image, install
crawl4ai   (from   PyPI)   and   run   crawl4ai-setup   (which   installs   browsers)
crawl_ethena.py .
-  cocoindex   Dockerfile:  base   Python,   install   cocoindex   and   sentence-transformers   (for
embedding model). Also install   duckdb   with the   ducklake   extension if we plan to use it. Copy in
run_index_flow.py .

.   Also   copy   in

34

33

-

 dlt   Dockerfile:  base   Python,

  pip   install   dlt[lancedb]   pandas   lancedb .   Copy

load_to_lance.py .

With this setup, running the entire pipeline is as easy as:

docker compose up --build

This will build images and start each service in order. The crawler will finish and exit after scraping, then
the cocoindex service runs, etc. After completion, the  ./data  folder will contain: -  markdown/  – all
the markdown content files. -  screenshots/  – PNG screenshots of each page. -  pdfs/  – PDFs of
each page (if enabled). -  output/ethena_chunks.parquet  – the structured chunk+embedding data.
(And/or a DuckLake metadata file if used.) -  .lancedb/  – LanceDB database files containing the
indexed vectors (within DLT’s pipeline directory, possibly  .dlt/  or as we configured).

9

5. Extensibility and Best Practices

Scalability:  The pipeline is designed following best practices from Crawl4AI and CocoIndex. Crawl4AI

can handle large crawls with its asynchronous engine and adaptive throttling. We included options to
limit depth and avoid external domains to focus on relevant content. CocoIndex’s transformation flow is

incremental-ready; in the future, if Ethena’s content changes, CocoIndex can detect new or changed

files and only process those (with Postgres tracking the state). DuckLake storage ensures we can take

snapshots of the data – for example, storing snapshots of the site content at different times, and even

query differences if needed

6

.

Chunking Strategy: We used a recursive splitter to respect document structure, as recommended for

complex content. This strategy yields higher quality chunks compared to fixed-size splitting, preserving

context around headings and sections

23

24

. We also included a 25% chunk overlap (500 bytes on

2000-byte   chunks)   to   maintain   context   continuity.   If   needed,   CocoIndex   also   supports  LLM-based

chunking   or   validation  –   for   instance,   one   could   employ   an  “LLM   judge”  to   score   chunks   for

completeness   or   relevance.   While   our   current   setup   does   not   explicitly   call   an   LLM   for   chunk

refinement,   CocoIndex’s  LLM   support  could   be   leveraged   to,   say,   ensure   that   important   sentences

aren’t split between chunks or to extract summary metadata using GPT
. This can be an area of
extension: adding an  ExtractByLlm  function to parse dates or classify content more accurately using

21

an LLM prompt

35

36

.

Embedding   Strategy:  We   chose   a  SentenceTransformer   MiniLM  model   for   speed;   however,   the
pipeline   could   easily   swap   to   a   different   embedding   model   if   needed.   CocoIndex’s   EmbedText

function supports various providers (including OpenAI, Cohere, etc.)

37

38

. We stuck with an open-

source model to keep everything self-contained. If higher embedding quality is required for financial
content,   one   might   use   a   model   like   all-mpnet-base-v2   or   E5-large ,   trading   off   speed   for

accuracy. Since LanceDB supports  hybrid search, we could also store text and use keyword filtering

combined with vector search if needed – DLT and LanceDB would allow adding a full-text index on the

text field alongside the vector index.

Storage & Querying: All data is stored locally in this pipeline, but it’s flexible – DuckLake could point to

an S3 bucket for a more production setup (just by configuring the DuckLake storage path to S3), and

LanceDB can likewise use cloud or persistent storage. The use of DuckLake means if we re-run the crawl

and indexing, we could time-travel the table to see previous data or merge updates transactionally

6

39

. LanceDB will allow fast retrieval of relevant chunks given a user query. With the chunks indexed, an

application can query LanceDB (via its Python API, REST, or even via DuckDB as LanceDB integrates with

it) to find, for example, all documentation pieces related to “staking” or similar topics. Each result can
provide the snippet ( text ) and the  title / url  for context. The screenshots and PDFs stored can

be used to present the user with the original page view if needed.

Finally, because everything is defined as code in Docker Compose, the pipeline is reproducible. New

team   members   can   run   the   compose   to   get   the   latest   index.   No   Dagster   or   external   scheduler   is

needed;   this   could   even   be   triggered   by   a   simple   cron   job   or   CI   pipeline   whenever   content   needs

refreshing. The modular design (separate containers for crawl, processing, load) means each step can

be individually improved or replaced (for instance, if a different crawler or indexing tool is desired, as

long as the interfaces – files in the volume – remain consistent).

10

Sources

•

Crawl4AI Documentation – Crawler Result and Output, explaining how  CrawlResult

includes raw content, Markdown, and optional media (screenshots/PDF)
screenshot=True / pdf=True  populates those fields
Crawl4AI Documentation – Deep Crawling, demonstrating using  BFSDeepCrawlStrategy
with  max_depth  and domain restrictions

 and how enabling

.

.

8

1

2

9

•

•

Crawl4AI Documentation – Domain Filtering, showing config to exclude external links and keep

crawl internal
CocoIndex Example – Simple Vector Index, using  SplitRecursively  for semantic chunking

.

11

10

•

of markdown (with 2000 byte chunks and 500 overlap)

3

 and embedding each chunk with

MiniLM (384-dim vectors)

4

. The MiniLM model is noted as a good speed-quality tradeoff

22

.

•

CocoIndex Blog – Text Embeddings 101, confirming the approach of reading files, splitting by

content structure, embedding with SentenceTransformers, and collecting results

21

40

.

•

LanceDB Documentation – DLT Integration, describing how dlt can load data into LanceDB with

automatic schema and embedding support

7

 and example configuration for embedding

models in DLT (optional)

31

.

•

DuckLake Documentation – Overview, highlighting that DuckLake uses Parquet storage with an

SQL catalog, enabling ACID transactions and snapshots on a data lake

5

6

.

1

2

14

Crawler Result - Crawl4AI Documentation (v0.7.x)

https://docs.crawl4ai.com/core/crawler-result/

3

4

16

22

25

26

Simple Vector Index with Text Embedding | CocoIndex

https://cocoindex.io/docs/examples/simple_vector_index

5

6

28

39

DuckLake is an integrated data lake and catalog format – DuckLake

https://ducklake.select/

7

29

30

31

32

dlt

https://lancedb.com/docs/integrations/platforms/dlt/

8

9

Deep Crawling - Crawl4AI Documentation (v0.7.x)

https://docs.crawl4ai.com/core/deep-crawling/

10

11

Link & Media - Crawl4AI Documentation (v0.7.x)

https://docs.crawl4ai.com/core/link-media/

12

Crawl4AI - a hands-on guide to AI-friendly web crawling - ScrapingBee

https://www.scrapingbee.com/blog/crawl4ai/

13

Crawl4AI: Unleashing Efficient Web Scraping | by Gautam Chutani

https://gautam75.medium.com/crawl4ai-unleashing-efficient-web-scraping-1825560300c3

15

21

40

How to build index with text embeddings | CocoIndex

https://cocoindex.io/blogs/text-embeddings-101

17

18

19

20

35

36

37

38

Functions | CocoIndex

https://cocoindex.io/docs/ops/functions

23

24

Optimizing Chunking, Embedding, and Vectorization for Retrieval-Augmented Generation | by

Adnan Masood, PhD. | Medium

https://medium.com/@adnanmasood/optimizing-chunking-embedding-and-vectorization-for-retrieval-augmented-

generation-ea3b083b68f7

11

27

Targets | CocoIndex

https://cocoindex.io/docs/targets

33

34

GitHub - unclecode/crawl4ai: Crawl4AI: Open-source LLM Friendly Web Crawler & Scraper. Don't

be shy, join here: https://discord.gg/jP8KfhDhyN

https://github.com/unclecode/crawl4ai

12

