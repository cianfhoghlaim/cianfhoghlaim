Technical Integration Plan: Dagster + DLT +

CocoIndex + Feast + MLflow (with DuckDB &

Dragonfly)

1. Ingestion and Indexing

Data Ingestion with DLT: We will use the dlt (Data Load Tool) Python library to ETL both structured and

unstructured sources (Ethereum blockchain data, DeFi API feeds, Git repository content, etc.) into a

DuckDB-based   lakehouse.   DLT   simplifies   extraction   and   loading   by   auto-inferring   schemas   and

handling schema evolution. For example, a DLT pipeline can ingest JSON or CSV data and load it into

DuckDB in one call

1

2

. We configure a pipeline per data source (e.g. one for Ethereum on-chain

data, one for DeFi API metrics, one for Git text data), each writing to DuckDB. DuckDB can be used in
two   modes:   as   a   standalone   analytical   DB   (single-file   .duckdb )   or   via  DuckLake,   DuckDB’s   new

lakehouse format. DuckLake stores tables in Parquet with ACID metadata in a SQL catalog (Postgres,

SQLite, etc.), enabling multi-client concurrency and features like time-travel

3

4

. For simplicity, we

might start with vanilla DuckDB (single-writer pipeline) and later adopt DuckLake if concurrent access or

snapshotting is needed.

Ingestion Implementation: Using DLT, each pipeline will incrementally upsert new data into DuckDB

tables, avoiding full reloads. For example:

import dlt

pipeline = dlt.pipeline(destination="duckdb", dataset_name="onchain_data")

new_blocks = fetch_new_blocks()

# your function to get new Ethereum block

data

pipeline.run(new_blocks, table_name="ethereum_blocks",

write_disposition="merge", primary_key="block_number")

The above ensures new Ethereum blocks are appended while existing ones (if any) are updated in the

DuckDB  table. Similar pipelines would ingest DeFi API data (e.g. daily market stats) and Git data (e.g.
repository files or commit messages). By using   write_disposition="merge"   with a primary key,

DLT ensures idempotent, incremental loads

5

6

 – a best practice for streaming updates.

Incremental   Indexing   with   CocoIndex:  Once   data   lands   in   DuckDB,  CocoIndex  will   maintain   a

semantic index over it. CocoIndex is a data transformation framework that can track upstream data

changes and update downstream indexes incrementally

7

8

. We will define CocoIndex  flows  for

each domain of data:

•

Structured data (Ethereum/DeFi): A flow might source new rows from a table like
ethereum_blocks  or  defi_stats  and produce transformed outputs (e.g. augmenting data

with computed fields or summaries) and embeddings for text fields.

1

•

Unstructured text (Git repos, proposals): A flow will read documents (code files, Markdown

proposals, etc.), split them into chunks, embed the text, and index those embeddings for

semantic search.

Each flow uses CocoIndex’s “live update” capability: it can continuously listen for new or changed data

and only reprocess the minimum needed pieces
. For example, if using a Postgres table as the
source,   CocoIndex   can   enable   a   PostgresNotification   to   capture   changes   via   LISTEN/NOTIFY

8

7

triggers

9

. In our plan, we have two options to trigger CocoIndex updates:

•

Via Postgres Triggers: We can mirror the DuckDB data into a Postgres table (or use DuckLake

with a Postgres catalog) so that inserts/updates issue notifications. CocoIndex’s Postgres source

integration will then catch these and immediately trigger an incremental flow run for the specific

new/updated rows
. This means as soon as, say, a new Ethereum block is ingested, a Postgres
trigger can  NOTIFY  a channel that CocoIndex listens on, prompting it to index that block’s data

8

without re-indexing the entire dataset.

•

Via   Pipeline   Events:  Alternatively,   if   direct   triggers   aren’t   feasible   (e.g.   using   pure   DuckDB

storage), we orchestrate updates in Dagster. After DLT finishes loading new data, Dagster can
call CocoIndex programmatically (e.g. using CocoIndex’s Python API or CLI to  update  the flow)

to   index   new   data.   This   “event-driven”   approach   ties   the   CocoIndex   update   to   the   ingestion

pipeline’s success. Dagster sensors can detect the arrival of new data (or the completion of an

ingestion run) and launch the indexing job.

CocoIndex Flow Design:  Each CocoIndex flow is defined with a series of operations: an  import  (data

source),   transformations   (both   traditional   and   AI-based),   and   an  export  to   a   target
.   For
instance,   a   flow   for  Ethereum   transactions  might   import   from   a   transactions   table,   compute

11

10

additional   fields   (e.g.   USD   value   =   price   *   amount),   and   then   generate   a   descriptive   text   for   each

transaction   that   can   be   embedded.   CocoIndex   allows   in-flow   Python   functions   and   integrated   AI

transforms. For example:

@cocoindex.flow_def(name="EthereumTxIndex")

def ethereum_index_flow(flow_builder: cocoindex.FlowBuilder, data_scope:

cocoindex.DataScope):

# Source: read from Postgres or DuckDB table of transactions

data_scope["tx"] = flow_builder.add_source(

cocoindex.sources.Postgres(table_name="transactions",

ordinal_column="updated_at",

notification=cocoindex.sources.PostgresNotification())

)

with data_scope["tx"].row() as tx:

# Traditional transformation: compute USD value of transaction

tx["usd_value"] = flow_builder.transform(lambda price, qty: price *

qty, tx["token_price"], tx["quantity"])

# AI transformation: create text summary and embed it

tx["summary"] = flow_builder.transform(make_tx_summary,

tx["from_addr"], tx["to_addr"], tx["usd_value"])

tx["embedding"] = tx["summary"].transform(

cocoindex.functions.SentenceTransformerEmbed(model="sentence-

transformers/all-MiniLM-L6-v2")

2

)

indexed = tx.collect(

from_addr=tx["from_addr"], to_addr=tx["to_addr"],

usd_value=tx["usd_value"], summary=tx["summary"],

embedding=tx["embedding"]

)

indexed.export(

"eth_tx_index", cocoindex.targets.LanceDB(db_uri="./vector_index",

table_name="eth_transactions"),

primary_key_fields=["tx_hash"],

vector_indexes=[cocoindex.VectorIndexDef(field_name="embedding",

index_type="IVF_PQ")]

)

In the above conceptual flow, CocoIndex will: ingest new  transactions , compute a summary per tx,

embed it into a vector, and export the results. We choose LanceDB as the export target for embeddings

(more on LanceDB below). The flow’s incremental nature means if new rows appear or existing ones

change, only those will get reprocessed and the LanceDB index updated, while untouched data and

embeddings remain intact

8

. This achieves efficient incremental processing and keeps the index up-

to-date with minimal work.

Postgres vs DuckDB for sources: Note that CocoIndex currently uses Postgres for its internal state and

excels with a Postgres source

12

. In practice, we might use Postgres as an ingestion landing zone (with

triggers) or use connectors (CocoIndex supports sources like files, APIs, etc. if needed). But the end-goal

is all ingested data ends up queryable in DuckDB for analytics, while CocoIndex ensures any textual

content is indexed for semantic search.

Example from CocoIndex: The diagram above (from CocoIndex docs) illustrates how data from structured

sources   (left,   e.g.   Postgres   or   APIs)   flows   through   transformations   (including   AI   embedding)   and   is

written   to   both   a   relational   store   and   a   vector   index.   In   our   case,   DuckDB/DuckLake   serves   as   the

analytical store for structured outputs, and LanceDB serves as the vector index for semantic search.

CocoIndex’s live pipeline ensures changes in source data propagate to these targets automatically

8

.

2. Semantic Index and Vector Store (CocoIndex + LanceDB)

Embedding Storage with LanceDB: We will use LanceDB as the vector database to store embeddings

computed by CocoIndex. LanceDB is an embeddable vector store built on Apache Arrow, allowing fast

similarity search with on-disk indices. In the CocoIndex flow export (see above), we specify a LanceDB
target with a local path (e.g.   ./vector_index ) and a table name. CocoIndex will create a LanceDB

table where each row contains the embedded vector along with metadata (like an ID and any fields we

collected, such as filenames, transaction details, etc.)

13

14

. LanceDB requires a primary key for each

row (CocoIndex uses this to avoid duplicate entries and LanceDB builds a B-Tree index on it)

15

. For

example,
repo_name+file_path+line_range , and for Ethereum transactions it could be the  tx_hash .

the   primary   key   might

  be   a   composite   of

  code   files

for

Vector   Index   Construction:  After   initial   data   is   loaded   into   LanceDB,   we   can   build   an   ANN

(approximate   nearest   neighbors)   index   on   the   embedding   column   for   efficient   similarity   search.

(LanceDB cannot create a vector index on an empty table, so we run the flow once to populate data,

then   create   the   index)
.   We   can   automate   this   by   having   CocoIndex   export   define
vector_indexes   as in the example (e.g. use an IVF or HNSW index on   embedding ). Alternatively,

16

3

we run LanceDB Python API to create an index post-hoc. The result is an optimized vector store where

queries are fast even as data grows.

Using Vectors for Semantic Search: The stored embeddings enable semantic operations: - Semantic

code search: For a given natural language query or code snippet, we compute its embedding (using the

same model as the index, e.g. MiniLM or CodeBERT) and query LanceDB for nearest neighbors in the

code index table. This returns the most similar code chunks or documentation, which can be used to

answer questions or provide relevant context. - Prompt retrieval for LLMs: When building prompts for

GPT-OSS or other models, we can fetch relevant facts or proposals by querying the LanceDB index with

the   current   query’s   embedding.   For   instance,   if   the   user’s   question   is   about   a   specific   Ethereum

improvement proposal, we embed the question and find the closest proposal texts or discussions from

LanceDB to include in the prompt (this is a Retrieval-Augmented Generation approach). -  Semantic

filtering: In analytics scenarios, we could use the vectors to cluster or filter data by semantic similarity

(e.g. find transactions with similar descriptions or DeFi projects with similar docs).

Under the hood, LanceDB’s integration with CocoIndex ensures embeddings stay in sync with source

data. As new documents are ingested (or updated), CocoIndex will recompute embeddings for those

items and update the LanceDB table. Because CocoIndex knows which source items changed, it avoids

re-embedding everything—only new/changed entries are processed, which is crucial for efficiency with
. This incremental vector indexing is a key best practice: it provides up-to-date
large data streams

7

semantic search without re-indexing the entire corpus for every update.

Example – Indexing Source Code: For a Git repository source, the CocoIndex flow might: 1. Import files
(via a  LocalFile  or Git source plugin) and break each file into smaller chunks (using a built-in splitter

operation). 2. Embed each chunk’s text using a sentence-transformer or code model. (CocoIndex has
ops like  SentenceTransformerEmbed  to do this in-line
.) 3. Collect fields like repository, file path,
and   chunk   text   +   the   embedding.   4.   Export   to   LanceDB   (table   e.g.   code_index ,   primary   key   =

17

file+chunk_id).   After   this,   given   a   search   query   (natural   language   or   code),   an   embedding   can   be
computed and nearest neighbors in  code_index  retrieved, yielding relevant code snippets.

Example – Indexing Proposals/Docs:  For Ethereum improvement proposals or DeFi protocol docs (if

those are ingested from Git or APIs), a similar flow would chunk the text of each proposal, embed the

chunks, and store them in LanceDB. The semantic index can then answer questions like “Find proposals

related to gas optimizations” by vector similarity instead of keyword search.

In   summary,  CocoIndex   +   LanceDB  provides   a   continuously   updated   semantic   index:   CocoIndex

handles the incremental embedding generation and data mapping, and LanceDB provides the vector

storage and fast similarity search. This decoupled approach (structured data in DuckDB, embeddings

in   LanceDB)   is   a   best   practice   for   modular   design,   letting   us   scale   or   swap   out   the   vector   DB

independently of the analytics DB.

3. Feature Store Integration with Feast (DuckDB & DragonflyDB)

With raw data ingested and indexed, the next step is to turn raw data into features for ML models. We

will   use  Feast,   an   open-source   feature   store,   to   manage   feature   definitions   and   serve   features   for

training and inference. Our plan is to use DuckDB as Feast’s offline store and DragonflyDB (a fast Redis-

compatible cache) as the online store, leveraging a recent integration pattern

18

19

.

Feature   Engineering   and   Storage:  Processed   features   can   be   derived   via   DuckDB   queries   or   dbt

models on the ingested data. For example, we might compute features like “average gas fee over last N

4

blocks” for an address, “total value locked” for a DeFi protocol, or user-specific activity counts. These

features can be materialized as tables in DuckDB or as Parquet files on disk. DuckDB can directly query

Parquet,   so   we   can   choose   to   store   features   either   within   DuckDB   or   as   external   Parquet   files   for

flexibility

20

21

.

Once   features   are   computed,   we  expose   them   to   Feast  by   defining  data   sources,   entities,   and
feature  views:  -  Entity:  a  primary  key  for  the  feature  (e.g.   address_id   for  Ethereum  addresses,
repo_name  for Git projects, etc.). - Data source: where the feature data lives offline (DuckDB table or

Parquet file). - Feature View: a logical grouping of features for an entity, with schema and an associated

data source.

For example, suppose we have a DuckDB table   address_features   with columns:   address_id ,
avg_gas_fee_7d ,   total_tx_count_30d ,   last_active_timestamp . We would define in Feast

(via Python API):

from feast import Entity, FeatureView, Field, ValueType, FileSource,

DuckDBSource

address = Entity(name="address", join_keys=["address_id"],

value_type=ValueType.STRING)

# If using Parquet files:

addr_feature_source = FileSource(path="data/address_features.parquet",

timestamp_field="last_active_timestamp")

# If using DuckDB directly, we could use DuckDBSource (Feast supports DuckDB

as well):

# addr_feature_source = DuckDBSource(database="features.duckdb",

table="address_features", timestamp_field="last_active_timestamp")

address_features_view = FeatureView(

name="address_features",

entities=[address],

schema=[

Field(name="avg_gas_fee_7d", dtype=ValueType.FLOAT),

Field(name="total_tx_count_30d", dtype=ValueType.INT32),

# ... other feature fields

],

source=addr_feature_source,

ttl=86400*30

# 30-day TTL for feature freshness (Feast will consider

data within 30 days for online serving)

)

We then run  feast apply  to register these definitions. Feast will store the metadata in its registry (a
local file or a PostgreSQL, but in our  feature_store.yaml  we’ll keep it simple with a local file). We

configure  Feast’s   offline   store   as   DuckDB   and   online   store   as   Redis/Dragonfly
feature_store.yaml :

in

project: crypto_ai_project

registry: data/registry.db

provider: local

5

offline_store:

type: duckdb

online_store:

type: redis

connection_string: "localhost:6379"

18

This tells Feast to use DuckDB for offline feature retrieval and to connect to a Redis-compatible
service at   localhost:6379   for the online store. Since  DragonflyDB  speaks the Redis protocol, we

can point the Feast Redis connector to Dragonfly with no changes

22

. Dragonfly will act as a high-

performance in-memory KV store for serving feature values in production.

Feature View Materialization:  After defining features and populating them in the offline store, we

materialize them to the online store. Materialization is the process of taking the latest feature values

from the offline warehouse (DuckDB) and pushing them to the low-latency online DB (Dragonfly) for

quick access by models

19

. We can run:

feast materialize 2025-01-01T00:00:00 2025-12-31T23:59:59

This CLI (or the equivalent  store.materialize()  in Python) will scan for each feature view, find the

latest values as of now (within the given time range), and write them to Dragonfly with keys composed

19

.   For   example,   after   materialization,   Dragonfly   (Redis)   might   have   keys   like
of   the   entity   IDs
address:0xABC123:address_features  mapping to a hash of feature values  {avg_gas_fee_7d:
X, total_tx_count_30d: Y, ...} . Feast handles this encoding under the hood.

23

We will schedule this materialization to run periodically (say every hour or day) via Dagster (discussed

later), so that the online store is always updated with fresh feature values. This ensures models doing

real-time inference (e.g. a fraud detection model needing the latest user stats) get up-to-date features

with millisecond latency from Dragonfly

24

25

.

Historical Feature Access:  With DuckDB as the offline store, we also get seamless historical feature

retrieval for model training. Feast can use DuckDB’s query engine to join feature tables with training

labels   or   events   using   point-in-time   correct   joins

21

.   For   instance,   if   training   a   model   on   historical

transactions, we can fetch the corresponding feature values (like average fees or past activity) at each
transaction’s   timestamp   via   store.get_historical_features(entity_df,   feature_list) .

DuckDB will directly query Parquet or its internal tables to assemble the training dataframe

21

26

.

This eliminates the need to export data to CSV manually – Feast orchestrates the joins in DuckDB, giving

a consistent view of features in training vs serving.

Entity and Feature Definition Outline:  To summarize the Feast setup: - We define  entities  such as
user_id ,  address ,  protocol_id  depending on what our prediction tasks are. Each corresponds

to a real-world entity for which we have features. - We define feature views grouping related features

for   each   entity.   For   example:   -  UserActivityFeatures:  features   like   number   of   commits,   number   of

transactions, last active time (entity: user_id). - AddressRiskFeatures: features like average gas, total value

transacted, protocol interactions count (entity: address). - MarketFeatures: features of a token or protocol

like volatility, TVL (entity: protocol_id). - Each feature view has an associated  data source  in DuckDB/

Parquet.   We   ensure   each   data   source   has   a   timestamp   field   for   Feast’s   point-in-time   logic   (e.g.
event_timestamp  or last update time). - We use DuckDB as the computation engine for assembling

features, benefiting from its high-performance analytical capabilities on our scale of data (likely GBs to

low TBs)

27

.

6

Online Serving with Dragonfly: At inference time, a model (or a prediction service) can query Feast’s

online store to get feature values for given entity IDs. Because we chose Dragonfly, we inherit its multi-

threaded performance and low latency – a single Dragonfly instance can handle millions of requests

per second with sub-millisecond response

25

. This means even if we deploy multiple model servers or

multiple  Feast  serving  instances,  they  all   hit  the   same   Dragonfly   instance  (or   a   clustered   Swarm,   if

scaled   out)   as   a   shared   cache

28

29

.   This   setup   decouples   feature   computation   (batch   mode   in

DuckDB) from feature serving (real-time in Dragonfly), following Feast’s architecture of an offline source

of truth and an online serving layer

30

31

.

Feature Pipeline Flow:  In practice, after data ingestion and initial processing: 1. We run a  feature

engineering job (could be SQL in DuckDB or a dbt job orchestrated by Dagster) to create/update the
feature tables in DuckDB (or output Parquet). 2. We call  feast apply  (one-time or when definitions
change) to register any new features or sources. 3. We run   feast materialize   on a schedule to

push new feature values to Dragonfly. 4. During model inference, use Feast SDK or Feast server to
get_online_features  for entity IDs, which under the hood queries Dragonfly

33

32

.

This integration ensures our models always use consistent feature values in training and production,

preventing training/serving skew. It also externalizes feature management from the models, aligning

with modular pipeline design (data/features vs. model code separation).

4. MLflow for Model Tracking and Experiment Management

We will incorporate  MLflow  to track all our model training runs, fine-tuning experiments, and data

lineage, ensuring reproducibility of results. MLflow will be used to log models, metrics, parameters, and

references to datasets (feature sets, vector indexes, etc.), and to manage model versions.

Tracking   Fine-Tuning   Runs:  Each   time   we   fine-tune   a   model   (whether   it’s   GPT-OSS,   Qwen3-VL,

CryptoBERT, etc.), we will wrap the training code with MLflow tracking. In a Dagster op or a training

script, we’ll do something like:

import mlflow

mlflow.start_run(run_name="fine_tune_gpt_oss_v1"):

mlflow.log_params({

"model_base": "gpt-oss-20B",

"epochs": 3,

"lr": 1e-4,

"method": "LoRA",

"training_data": "crypto_qa_v1"

})

# ... fine-tuning code ...

mlflow.log_metric("final_loss", final_loss)

mlflow.log_metric("accuracy", eval_accuracy)

mlflow.log_artifact("data/crypto_qa_v1.json")

# dataset used (or use

mlflow.data)

mlflow.pytorch.log_model(trained_model, "model")

We  capture  key  hyperparameters  (base  model  name,  learning  rate,  technique  like  LoRA  or  QLoRA),

performance metrics (loss, accuracy, any domain-specific metrics), and artifacts.  Artifacts  will include

the

trained   model

  weights

(logged   via

  mlflow.pytorch.log_model

or

7

mlflow.huggingface.log_model  depending on framework) and any relevant files such as the exact

training dataset or a link to it. If the dataset is large, instead of logging the whole file, we leverage

MLflow’s  Dataset   tracking  APIs   to   log   a   reference:   for   instance,   we   can   create   an
mlflow.data.Dataset  pointing to our DuckDB or LanceDB data source and log it as an input to the

run

34

35

. This records the dataset’s provenance (e.g. a pointer to a Parquet file path or a query)

without duplicating the data. By tracking datasets in MLflow, we ensure data lineage is preserved – one

can later see exactly which data version was used to train a given model

34

36

. This is crucial for

reproducibility: experiments can be reproduced with identical data and settings if needed.

Linking Feature Store & Vector Index: We will also log references to the  feature tables and vector

indexes  used.   For   example,   if   a   model   training   used   features   from   Feast,   we   could   log   the   Feast

repository   commit   or   the   specific   feature   view   names   and   a   timestamp   as   run   parameters.   If   we

retrieved additional data via LanceDB for training (e.g. fetched similar Q&A context from the vector

index), we log the LanceDB version or a hash of the index contents. In practice, this might be a simple
parameter like  vector_index_commit_id  or an artifact like a dump of the LanceDB metadata. The

goal is that someone examining the MLflow run can trace back exactly which features and semantic data

were used.

Additionally,  MLflow’s  tracking  can  be  integrated   with  our   pipeline   code.   For   instance,   after   feature

engineering, we might log the feature data schema or even profile as part of the run that generates the

training set. MLflow’s new dataset tracking module allows storing dataset schema, profile stats, etc.,

which we can utilize for thorough experiment documentation

35

37

.

Model Registry and Deployment:  We will use  MLflow Model Registry  to manage model versions.
Once  a  fine-tuning  run  produces  a  satisfactory  model,  we  call   mlflow.register_model("runs:/
<run_id>/model", "CryptoBertClassifier")   (for example) to register it under a named entry.

This   creates   a   versioned   record   in   MLflow   (e.g.   Version   1   of  CryptoBertClassifier).   We   can   transition

models through stages (Staging -> Production) as we evaluate them. The registry provides a central,

auditable   log   of   which   model   is   deployed.   It   also   allows   easy   loading   of   models   by   name:   e.g.   a
downsteam   pipeline   can   do   mlflow.pyfunc.load_model("models:/CryptoBertClassifier/
Production")  to get the latest production model.

Reproducibility Best Practices:  To ensure  experiment reproducibility, we adopt these practices: -

Code Versioning:  We configure MLflow to log the source Git commit of the code run (MLflow can do
this   automatically   if   a   git   repo   is   present,   or   we   set   mlflow.set_tag("git_commit",
commit_hash) ).   This   ties   the   run   to   a   specific   code   version.   -  Environment   Logging:  We   use
mlflow.log_artifact("requirements.txt")  or MLflow’s conda environment auto-log to capture

the library dependencies. This, along with the base model name, ensures we know the environment in

which the model was trained. - Data Versioning: As described, we track dataset references instead of

raw data when large. For instance, we might log: the DuckDB database file hash or timestamp, LanceDB

index version, or Feast registry digest. Another approach is integrating a data version control tool (like

DVC   or   LakeFS)   for   the   dataset   and   just   logging   the   dataset   version   ID   in   MLflow.   -  Metrics   &

Evaluation: We log not only training metrics but also evaluation results on validation sets. If we have a

separate evaluation step (like comparing model vs model or computing domain-specific metrics), those

results are also logged to the same run or a linked run. This gives a full picture of model performance.

By following these practices, anyone can later pick a model run from MLflow and know  which data,

code,   parameters,   and   metrics  went   into   it,   fulfilling   reproducibility   requirements.   In   fact,   MLflow

highlights   that   dataset   tracking   is   a   key   to   reproducibility   –   experiments   can   be   reproduced   with

identical datasets, as it tracks the lineage from raw data to model

34

.

8

Artifacts and Links:  We will store the  fine-tuned model weights  as MLflow model artifacts so that

they can be easily loaded for inference or deployment. For large models, we may store just the delta

weights (e.g. LoRA adapters) as artifacts to save space, with instructions to apply them on the base

model. We also log any evaluation artifacts (like confusion matrices, example outputs, or a small JSON

of results). If using any external services (like Hugging Face Hub for model storage or a Weights &

Biases dashboard), we can log the link or ID as an MLflow tag for cross-reference.

Finally, MLflow will be integrated into Dagster orchestration: e.g., the Dagster training job will handle
MLflow context (ensuring   mlflow.start_run   is called at the beginning and   mlflow.end_run   at

end, possibly using a Dagster resource or context manager). This way, every pipeline run that trains or

evaluates a model automatically creates an MLflow experiment entry. Over time, we can compare these

runs in the MLflow UI to track progress and select the best model.

5. Orchestration Flow with Dagster

We will use  Dagster  to orchestrate the entire end-to-end pipeline: from data ingestion to indexing,

feature   engineering,   model   training,   and   deployment.   Dagster’s   job/asset   abstractions   and   sensors

allow us to build a modular, event-driven pipeline where each component is independently managed

but interlinked through well-defined triggers. This promotes a modular design – each stage (ingest,
index, feature store, train, etc.) is an isolated unit (op/job) that can be developed and tested separately,

and Dagster ties them together into a cohesive system.

Pipeline Overview: The high-level orchestration flow is:

1.

Data Ingestion Job – runs the DLT pipelines to fetch new data and load DuckDB. (This could be

broken down by source: e.g. one job for Ethereum data, one for Git data, etc., or a single job that

runs all). When this job succeeds, it yields new or updated tables in DuckDB.

2.

Indexing Job – triggers CocoIndex flows to update the semantic index (LanceDB) and any

structured indexes. This can run immediately after ingestion or even in parallel for different data

sources. For instance, after new Git data is ingested, run the code indexing flow; after new

Ethereum data, run the transaction indexing flow. This job ensures LanceDB and any Postgres-

based index tables are updated.

3.

Feature Engineering Job – computes or updates feature tables in DuckDB based on the latest

raw data. This could be a SQL transformation job or a dbt project triggered by Dagster. For

incremental updates, this job might only recompute features for new data (e.g. if today’s data

arrived, only update features that involve the last day; or maintain a rolling window feature via

insert).

4.

Feast Materialization Job – takes the updated feature data and pushes it to Dragonfly (online

store). This could run on a schedule (e.g. nightly at 00:00 UTC) or be triggered after feature

engineering completes. It ensures the online features reflect the latest offline computations.

5.

Model Training Job – kicks off fine-tuning of models when appropriate. This job uses the latest

feature data (via Feast offline store or DuckDB) and possibly additional data from LanceDB

(retrieved within the job) to train or fine-tune an ML model. It includes evaluation and logs

metrics to MLflow. This might be further split into multiple jobs if we are training different

models (one for GPT-OSS, one for Qwen3-VL, etc.) on different schedules.

6.

Model Evaluation/Registration Job – after training, a separate step can evaluate the new model

against the current production model (e.g. on a hold-out set or via A/B test metrics). If the new

model meets criteria (higher accuracy, etc.), this job can handle promotion: e.g. registering the

model in MLflow Model Registry at Staging or even directly marking it Production, and

9

potentially triggering a deployment workflow (outside the scope of this question). This step

ensures only models that pass quality gates get deployed.

Dagster allows us to wire these with sensors and schedules. We will use event-based sensors where

possible  for  efficiency:  -  A  sensor  on  data  arrival:  Dagster  sensors  can  monitor  external  events  at

intervals

38

39

. For example, a sensor could poll an API or a directory to see if new data is available

(e.g. check if a new block number > last processed block, or if a new Git commit exists). When it detects

new data, it triggers the Data Ingestion job. This can replace a blind schedule (though we could also

schedule ingestion to run every hour as a fallback). - A sensor on ingestion completion: Since Dagster

knows when a job completes, we can chain jobs. However, the more modern approach in Dagster is to

use  assets  and   asset   sensors.   If   we   define   the   ingested   dataset   as   a   Dagster   asset   (e.g.   an   asset

representing the DuckDB table), Dagster can automatically trigger downstream assets that depend on

it. For simplicity, we might use a sensor that looks for a successful run of the ingestion job (or the

presence   of   new   data   in   DuckDB)   and   then   launches   the   Indexing   and   Feature   jobs.   -  Asset

Materialization sensors: We can declare LanceDB index and feature tables as Dagster assets as well.

Then Dagster’s asset dependency graph would naturally ensure the order: e.g. raw data -> index asset -

>   feature   asset   ->   model   asset.   Dagster’s   Asset   sensors   can   trigger   runs   when   a   specific   asset   is

materialized

40

41

, which is a clean way to express “after features are updated, trigger training”. -

Schedule   for   model   retraining:   If   our   data   changes   slowly   or   we   only   retrain   periodically,   we   can

simply use a schedule (e.g. train model every Sunday night). However, if data volume is the trigger, we
could   implement   a   sensor   that   checks   if   enough   new   data   has   accumulated   or   if   concept   drift   is

observed (by monitoring stats in DuckDB) to decide on triggering training.

Conditional Launch and Checks: Dagster sensors allow embedding logic. We can implement a sensor

that, for example, checks if at least N new records were added this week and the current model is older

than X weeks, then triggers the training job. If conditions aren’t met, it can skip the run with a message

38

42

.   This   avoids   retraining   too   often   or   when   unnecessary.   We   can   also   incorporate   evaluation

metrics: e.g. after training, if the new model’s AUC is not at least 1% better, skip the deployment.

Modularity via Ops/Jobs: Each stage of the pipeline (ingest, index, feature, train) will be implemented

as one or more Dagster ops grouped into jobs. This separation is a best practice for maintainability: -

The ingestion job can be run independently to test data loading. - The indexing flows (though largely

handled by CocoIndex internally) are triggered via a lightweight Dagster op (could call a shell command

or function). This op can be retried or isolated if indexing fails without affecting ingestion. - Feature

engineering might be a series of SQL ops or a dbt invocation. Dagster can call dbt jobs or run DuckDB

SQL   via   a   custom   op.   This   decoupling   means   data   scientists   can   adjust   feature   definitions   in   SQL

without touching ingestion or training code. - The training job encapsulates the ML code and can be run

with different parameters (Dagster can even do parameterized runs easily). One could test a training job

on a sample by providing a config, which is easier when it’s a standalone job in Dagster.

Dagster also provides a UI and lineage view. We’ll leverage that for observability: you can trace from a

model back to which data ingestion run and feature computation it came from, giving a holistic view of

the pipeline similar to data lineage.

Error Handling & Recovery: If any step fails (e.g. if the DeFi API is down and ingestion fails), Dagster

will report the error and we can configure alerts. Upstream sensors might retry automatically or we set

up   alerts   for   manual   intervention.   The   modular   design   means   a   failure   in   the   indexing   job   doesn’t

require rerunning ingestion – we can fix the issue (say a model service for embedding was unavailable)

and just rerun the indexing job for the missed data.

10

Example Trigger: Suppose a new commit is pushed to the Git repository we track: - A GitHub webhooks

could hit an endpoint that we connect to Dagster (via the GraphQL triggers API or a simple sensor

polling the repo). This event causes Dagster to start the Git Ingestion job (cloning the repo and loading
new file contents to DuckDB). - Once done, Dagster recognizes the asset   code_index   (LanceDB) is

downstream.   A   sensor   or   asset   dependency   triggers   the  Code   Indexing   job  to   update   CocoIndex

(embedding new code). - After that, if these code embeddings are part of a feature (e.g. “number of

similar past commits” feature for some model), the Feature job runs to update that feature. Otherwise,

the new data might not impact model features and we might not retrain immediately just for a doc

change. - So the pipeline might stop there, with updated semantic search available (for developer Q&A

perhaps). No model retrain is triggered in this case because it’s not needed for model performance. - In

contrast,   if  a   large   batch   of   new   Ethereum   data  arrives  (say   a   week   of   blocks),   the   sensor   triggers

ingestion -> indexing -> feature engineering. After features update, a training sensor sees that we have

a lot of new data and triggers a model retrain (maybe on a schedule aligned with weekly retrains). -

Dagster ensures each stage happens in order and logs the lineage of what ran when.

Using Dagster’s orchestration, we achieve an automated, event-driven pipeline. This means minimal

manual intervention: new data flows through to updated models with appropriate checks. It also means

modularity: the data engineering team can focus on the ingestion & feature jobs in SQL/Python, the ML

team on the training job, and they coordinate via clearly defined data assets (tables, feature views)

rather than one big monolithic script. This modular pipeline design improves maintainability and clarity,

as each component can be developed and tested in isolation, then integrated via Dagster’s declarative

asset dependencies. Dagster’s sensors and asset checks also provide a robust mechanism to ensure

freshness   policies  (e.g.   alert   if   features   haven’t   updated   in   expected   time)   and   thereby   maintain

pipeline health.

(In summary, Dagster acts as the central brain that monitors for new inputs and orchestrates a chain of ops to

incrementally process data, update indexes, refresh features, and retrain models. It embraces best practices of

incremental, event-driven processing

38

 and clean separation of concerns between pipeline stages.)

6. Model Fine-Tuning Integration and Hooks

Finally, we integrate our fine-tuning workflows for models like  GPT-OSS,  Qwen3-VL, and  CryptoBERT

into this pipeline. These models will be fine-tuned using the data and features gathered, and possibly

leveraging   our   semantic   index   during   training.   We’ll   utilize   tools   such   as  Unsloth,   Hugging   Face

libraries, or the DPO method to carry out fine-tuning efficiently.

Using   Pipeline   Data   for   Fine-Tuning:  The   datasets   for   fine-tuning   will   come   from   our   previously

prepared data: - For GPT-OSS (a GPT-style large language model), we might fine-tune it on domain-

specific instructions or Q&A. We can create a dataset of prompts and responses from our knowledge

base. For example, use the LanceDB semantic index to retrieve relevant context for historical Q&As: -

Take common questions about Ethereum/DeFi from forums or docs (if we have them ingested) and

their answers (the ground truth answers from documentation). - Use LanceDB to pull additional related

snippets as extra context, and format this as augmented training data (similar to RAG but as supervised

fine-tuning: the model learns to use context). - Fine-tune GPT-OSS on these Q&A pairs so it learns about

the domain. - For Qwen3-VL (a vision-language model), if our data includes any paired images (maybe

not in this scenario, unless we have charts or screenshots in docs), we could fine-tune it on any available

image-text pairs. If not, Qwen3-VL might not be a focus unless we integrate relevant data (this depends

on scope; we might skip vision fine-tuning if we have no images). - For CryptoBERT (a BERT model pre-

trained on crypto text), we can fine-tune it for specific NLP tasks: e.g., classify if a transaction is illicit or

categorize proposal texts. We’d use the features from DuckDB/Feast to create training labels if available

11

(or   external   labels).   For   instance,   if   we   label   some   addresses   as   scams   vs   legit,   we   can   fine-tune

CryptoBERT on textual features of those addresses (like on-chain activity descriptions or comments) to

predict scam likelihood.

Integrating   Unsloth   for   Efficiency:  We   consider   using  Unsloth  to   fine-tune   LLMs   with   limited

hardware. Unsloth provides optimized training routines (like LoRA, QLoRA) that allow fine-tuning large

models (billions of parameters) with low VRAM and faster speeds

43

44

. For example, we might fine-

tune GPT-OSS (20B+ parameters) using QLoRA 4-bit quantization so that it fits on a single GPU with

24GB memory. Unsloth’s library can be invoked via command-line or Python; we can integrate it in our

Dagster   training   job.   Essentially,   instead   of   writing   the   entire   training   loop   from   scratch,   we   call

Unsloth’s fine-tuning function with our model and dataset, which handles the optimization under the

hood. This accelerates development and ensures best practices (they likely handle things like learning

rate schedules and mixed precision optimally).

Fine-Tuning Workflow Example:  Suppose we want to fine-tune GPT-OSS on an  instruction dataset

derived from our domain (let’s call it CryptoInstruct v1): 1. Prepare Dataset: A Dagster op uses DuckDB

to pull, say, the top 1000 asked questions about Ethereum from our data and their answers (perhaps

curated), forming a QA dataset. We format it in a JSON or CSV as needed (or directly into a HuggingFace
datasets  object). We log this dataset to MLflow (so we know “CryptoInstruct v1” content). 2. Launch

Fine-Tune: The training job (could call an Unsloth CLI or use HuggingFace Trainer) fine-tunes the base

model. We might use LoRA to only train low-rank adapter weights (for speed). Unsloth will allow us to

do this on a single GPU if needed by compressing to 4-bit. We specify hyperparams: e.g., 3 epochs,

batch size 8, learning rate 1e-4. 3. Monitor and Log: As training runs, we evaluate on a validation split

(maybe some held-out QAs) to see how the model is improving. We log metrics like exact match or F1 if

it’s QA. The Dagster job can stream logs or just rely on MLflow. 4. Completion: When done, the model

(possibly just the LoRA weights) is saved and logged as an MLflow model artifact. We also capture that it

was fine-tuned on CryptoInstruct v1 (which in turn came from certain data sources).

By fine-tuning the model on our specific data, we inject new domain knowledge into it and tailor its

behavior

45

46

. For example, the base GPT-OSS might not know details of the latest DeFi protocol, but

after fine-tuning on our dataset (which includes that info), it can produce accurate answers on that

topic. Fine-tuning also allows us to  customize the model’s style and responses  to our needs (more

formal,   more   concise,   etc.,   depending   on   training   signals)

46

.   These   benefits   are   highlighted   by

Unsloth’s documentation: by fine-tuning a pre-trained model on a specialized dataset, we can update it

with new knowledge, adjust its behavior, and optimize it for our specific tasks

46

  – things that prompt

engineering or retrieval alone cannot permanently achieve.

Incorporating DPO (Direct Preference Optimization):  If we have or plan to collect human feedback

(preferences between model responses), we can integrate a RLHF-like step using  DPO. For instance,

after   an   initial   supervised   fine-tune,   we   could   have   humans   rank   some   outputs,   then   run   a   DPO

algorithm  to  further  refine  GPT-OSS  or  Qwen3’s  responses  to  align  with  preferred  style.  Unsloth  or

custom code can handle DPO – this would be another Dagster op in the training pipeline (maybe gated

by availability of preference data). We would track this in MLflow as another stage of training (with its

own   run).   DPO   could   especially   be   useful   for   GPT-OSS   if   we   want   it   to   adhere   to   certain   response

guidelines (like not revealing sensitive info, being extra cautious in financial advice, etc.).

Utilizing Features in Training: The features from Feast/DuckDB can also be used in model training. For

example, if training a model to predict something about an address (scam or not), we might not only

feed raw text but also structured features (like number of transactions, age of account). For an LLM, we

could incorporate those features into the prompt or as metadata. For a smaller model like CryptoBERT

used for classification, we could input features into a simple classifier or even train a separate model on

12

top of BERT embeddings. In our pipeline, this could mean: - Joining feature values into the training

dataset (DuckDB can easily join the feature table to the label table by address, yielding a rich training

set that includes both text and numeric features). - If training an LLM to do something like scoring

addresses, we might convert numeric features to text (e.g. “Address has 1000 transactions, active 2

years”) as part of prompt training data.

Continuous Learning: With Dagster scheduling, we can periodically fine-tune models on new data as it

accumulates, which is a form of continuous learning. For example, a sensor can watch if we have 1000

new QA pairs in LanceDB collected (maybe through community questions) and trigger a new fine-tune

run to update GPT-OSS. This keeps the model on the cutting edge of knowledge.

Validation   and   Deployment:  After   fine-tuning,   the   pipeline   should   include   an   evaluation   step.   We

compare the fine-tuned model’s outputs on a test set or through some automatic metrics (or even

through the semantic search: e.g. does the new model retrieve and use knowledge correctly?). If it

outperforms the previous model, the pipeline can automatically register it (as mentioned) and perhaps

notify   us   or   even   deploy   if   we’re   confident.   Deployment   might   be   as   simple   as   updating   a   serving

endpoint to load the new MLflow model.

To   close   the   loop,   once   a   model   is   deployed,   we   can   monitor   its   performance   (drift   detection).   If
performance   drops   or   when   a   certain   time   passes,   Dagster   can   trigger   the   next   fine-tuning   cycle,

making the whole system a closed-loop learning system.

Best Practices Recap:  Throughout this plan, we’ve emphasized: -  Incremental processing: Only new

data is ingested (DLT merges), only changes are indexed (CocoIndex incremental flows)

8

, and feature

computation can be incremental (using partitioned calculations or filtering by latest timestamp). This

makes the system scalable and timely. -  Experiment reproducibility: Using MLflow to log datasets,

code   versions,   and   model   parameters   ensures   any   model   can   be   reproduced   exactly

34

.   Data   and

feature lineage is tracked via Feast and MLflow, so we know what went into each model. -  Modular

pipeline   design:   Each   component   (ingest,   index,   feature   store,   model   train)   is   separate,   with   clear

interfaces (e.g. data files, DB tables, feature views) rather than entangled code. This modularity aligns

with the single-responsibility principle – easier to maintain and extend. Dagster’s orchestration binds

these   modules,   and   sensors   provide   a   clean   event-driven   trigger   mechanism   (e.g.   new   file   →   run
pipeline)

38

.

By integrating Dagster, DLT, CocoIndex, Feast, and MLflow in this manner, we create a robust pipeline

where   data   flows   continuously   from   raw   sources   to   model   insights.   The   use   of   DuckDB   and

DragonflyDB   ensures   we   have   efficient   offline   analytics   and   lightning-fast   online   feature   serving,

respectively. The addition of semantic search (LanceDB) and modern fine-tuning techniques means our

ML  models  can  leverage  both  structured  features  and  unstructured  knowledge.  Overall,  this  design

achieves an automated, scalable MLOps pipeline ready for real-world data dynamics and continuous

model improvement.

Sources:

•

DLT pipeline to DuckDB example

1

5

•

DuckLake (DuckDB’s lakehouse format) features

3

4

•

CocoIndex incremental update via Postgres notifications

8

9

•

CocoIndex embedding transform example

17

•

LanceDB usage in CocoIndex and vector index creation

47

13

•

Feast config for DuckDB offline & Redis/Dragonfly online

18

19

•

MLflow dataset and reproducibility benefits

34

•

Dagster sensors for event-driven triggers

38

•

Unsloth fine-tuning benefits (domain knowledge, behavior, task optimization)

46

1

2

5

6

Pipeline tutorial | dlt Docs

https://dlthub.com/docs/build-a-pipeline-tutorial

3

4

DuckLake is an integrated data lake and catalog format – DuckLake

https://ducklake.select/

7

10

11

12

Indexing Basics | CocoIndex

https://cocoindex.io/docs/core/basics

8

9

17

Transform Data From Structured Source in PostgreSQL | CocoIndex

https://cocoindex.io/docs/examples/postgres_source

13

14

15

16

47

LanceDB | CocoIndex

https://cocoindex.io/docs/targets/lancedb

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

31

32

33

Building a Feature Store with Feast, DuckDB,

and Dragonfly

https://www.dragonflydb.io/blog/building-a-feature-store-with-feast-duckdb-and-dragonfly

34

35

36

37

MLflow Dataset Tracking | MLflow

https://mlflow.org/docs/3.3.2/ml/dataset/

38

39

42

Sensors | Dagster Docs

https://docs.dagster.io/guides/automate/sensors

40

41

Automate | Dagster Docs

https://docs.dagster.io/guides/automate

43

44

45

46

Fine-tuning LLMs Guide | Unsloth Documentation

https://docs.unsloth.ai/get-started/fine-tuning-llms-guide

14


---

# Part II: Applied Use Case — Crypto Analytics AI Agent System

The preceding part of this document is the **general data platform architecture** for the Tuath Celtic Educational MMO, covering ingestion (DLT), transformation (CocoIndex), feature store (Feast), experiment tracking (MLflow), orchestration (Dagster), and storage (DuckDB + Dragonfly). The following part, originally titled "Crypto Analysis AI Agent System Architecture" (preserved below), applies that architecture to a specific domain: **cryptocurrency analytics** as a worked example of how the data platform serves an AI agent system that reasons over quantitative price data and qualitative news.

Crypto Analysis AI Agent System Architecture

Overview and Data Flow

Goal:  Build a multi-agent crypto analytics system that ingests crypto data, enriches and indexes it for

analysis, and enables AI agents to reason over that data. The high-level architecture involves four layers

(with corresponding tools) and flows data through them (see Figure 1):

•

Data Ingestion (DLT) – fetch raw crypto data (e.g. exchange prices, on-chain metrics, news

feeds).

•

Indexing & Embedding (CocoIndex) – transform and embed the data into an indexable format

(vectors, structured records).

•

Graph Memory & Search (Cognee) – store enriched data in a hybrid knowledge base (graph +

vector store) for semantic search and long-term memory.

•

Agent Orchestration (Agno) – coordinate one or more AI agents (LLM-powered) that use the
knowledge base to answer questions, summarize trends, detect anomalies, and record insights.

Data Flow:

1.

Ingestion: DLT pipelines pull data from various sources on a schedule or in real-time (e.g.

exchange APIs, blockchain node, Twitter/news API)

1

. DLT cleans and normalizes this “messy”

source data into well-structured datasets (e.g. tables of price history, lists of transactions)

1

.

2.

Indexing: CocoIndex monitors new data and processes it through an indexing flow. For example,

as new records arrive, CocoIndex can import them, apply transformations (like computing

technical indicators or splitting text into chunks), and embed textual fields into vectors

2

. The

final enriched data (with embeddings and structured fields) is exported to a target index for

retrieval

3

. CocoIndex’s incremental processing ensures that as source data updates, only new

or changed data is reprocessed and indexed

4

5

. This keeps the index fresh (important for

live crypto feeds) without reprocessing everything.

3.

Knowledge Storage: The target index is managed by Cognee. Cognee ingests the CocoIndex

output (via an API call or custom CocoIndex target) and “cognifies” it into a knowledge graph

with vectors. In practice, Cognee will take the embedded data points and build a graph of

entities (e.g. tokens, addresses, metrics) and relations (e.g. Token has Price, Transaction mentions

Address) while storing text embeddings for semantic similarity search

6

7

. This yields a

hybrid memory that is both semantically rich and structurally connected – combining a vector

index for text/content and a graph database for relationships

7

8

. The result is a persistent,

queryable “brain” of crypto knowledge

9

, where agents can both lookup facts and find relevant

context via similarity search.

4.

Agent Reasoning: On top of this memory, Agno orchestrates AI agents to perform tasks. When

a user query or scheduled task comes in, an agent will retrieve context from Cognee (e.g. the

latest prices, recent notable transactions, related news embeddings) using Cognee’s search API.

The agent (backed by an LLM) then reasons over this context to produce an output – e.g. a trend

summary or question answer. Agno allows agents to use tools and memory: for example, an

agent might call Cognee’s semantic search as a “tool” to get data, or even call external APIs if

needed for fresh info. Multiple specialized agents can be deployed as a team – for instance: a

“Trend Summarizer” agent, an “Anomaly Detector” agent, and a “Q&A” agent – collaborating via

Agno’s multi-agent workflow

10

. Agents can share the same Cognee memory (for context and

1

history) and even update it. For example, if the anomaly detector agent finds a suspicious on-

chain event, it can record that insight back into Cognee (as a new node or annotation), thus

persisting insights over time for others to use. Agno’s framework is designed to easily

incorporate such memory updates and tool usage within agent reasoning loops

11

12

.

Figure 1 – System Architecture: Data flows from sources through the ingestion and indexing pipeline into

a unified knowledge memory. AI agents (orchestrated by Agno) then query the memory and perform analytical

tasks, possibly writing new knowledge back.

(Diagram would illustrate: multiple Data Sources → DLT ingestion → CocoIndex ETL & embedding → Cognee

(graph+vector memory) → Agno multi-agent layer, with arrows for data flow and query flow.)

Data Ingestion Layer (DLT)

The DLT (Data Load Tool) layer handles connectivity to data sources and initial loading of data. DLT is a

Python-based open-source library for building pipelines that pull data from various APIs, databases,

and files into structured datasets

1

. Key aspects of using DLT for the crypto use case:

•

Sources: Configure DLT pipelines for each data source: e.g. a pipeline for price and volume data
from exchange REST APIs, another for on-chain data (via a blockchain indexer or node RPC), and

another for unstructured data like news or social feeds. DLT supports many “verified sources” and

can easily call custom APIs or read files. For real-time streams (WebSockets or Kafka), DLT can

ingest   via   stream   adapters,   or   you   can   schedule   frequent   batch   pulls   for   APIs   that   update

periodically.

•

Destination:  Instead of writing to a typical database or CSV, here the destination will be our

indexing layer (CocoIndex or directly Cognee). In simple setups, DLT can write directly to a vector

database (for example, DLT has integration to send data to Qdrant with embeddings

1

13

).

However, since we want to do additional processing with CocoIndex, a common pattern is for

DLT to dump data into a staging area that CocoIndex can read. For instance, DLT could insert

raw records into a PostgreSQL table, a cloud storage file, or even in-memory Python objects.

CocoIndex can then use that as its source. (DLT and CocoIndex can also run in the same script:

e.g. call a DLT function to fetch data into a Python list, then feed that list into CocoIndex’s flow –

see Integration below.)

•

Schema and Transform:  Define the schema of the data as much as possible in DLT. DLT can

auto-infer schema and handle conversions, giving a clean input to CocoIndex

14

. For example, a

pipeline

  might

DLT
like:
{"timestamp":   ...,   "token":   "...",   "price":   ...,   "volume":   ...}   or   for
  {"source":   "...",   "content":   "news   article   text",

unstructured   sources:
"date": ...} . This structured output becomes the input for the next stage.

dictionaries

output

list

of

a

•

Operational Considerations: DLT pipelines can run anywhere Python runs (Airflow DAGs, cron

jobs, serverless, notebooks)

15

. For a production system, you might schedule these pipelines

(e.g. Airflow or a lightweight scheduler) to keep data up-to-date. DLT also handles things like

incremental loads or state sync (so you can resume where you left off, avoiding duplicate data)

16

. Ensure logging is enabled in DLT to track when data was last ingested and any errors (e.g.

API outages). It’s best to separate pipelines per data source for clarity and maintainability.

2

Data Processing & Indexing Layer (CocoIndex)

CocoIndex  serves as the ETL and indexing engine that takes the raw structured data from DLT and

enriches   it   into   an   index  suitable   for   AI/semantic   queries.   CocoIndex   is   an   ultra-performant   data
.   In   this
transformation   framework   focused   on   building   AI   indexes   with   incremental   updates

3

architecture, CocoIndex is responsible for:

•

Defining the Indexing Flow:  You will create a CocoIndex  flow  that specifies how to transform

incoming data. For example, for price data (structured), the flow might pass it through as-is

(maybe computing additional fields like moving averages or percent changes as a transform).

For unstructured data (text like news or tweets), the flow can include steps to split text into

chunks   and   embed   them   using   an   LLM   or   embedding   model.   CocoIndex   provides   built-in

operations
for   chunking
SentenceTransformerEmbed   or an OpenAI embed function for vectorization)

  SplitRecursively

these

for

(e.g.

text

  and

2

. Multiple

sources can be combined in one flow (CocoIndex allows a top-level data struct with multiple

fields/tables

4

).  For  instance,  you  could  have  one  branch  of  the  flow  ingest  price  data  and

another ingest news articles, then link or join them if needed (or simply index them separately

but within one pipeline).

•

Target Index Storage: CocoIndex flows end by exporting data to a target. Here the target will be

a   Cognee-compatible   store.   CocoIndex   supports   various   targets   (files,   databases,   custom

targets). One approach is to use a  custom target  that calls Cognee’s API (e.g. using Cognee’s
Python   add()   function   to   feed   each   data   point)   –   CocoIndex   recently   added   support   for

custom export operations

17

18

. Another approach is to target a vector database like Qdrant

and a graph DB (Neo4j, etc.) separately, then have Cognee ingest from those. However, using

Cognee’s own adapter is simpler: Cognee can function as a unified target if wrapped properly.

For example, you might write a small function that takes CocoIndex’s output batch and calls
cognee.add()   on   each   record   (to   add   to   memory)   followed   by   cognee.cognify()   to

process them into the graph

19

. This custom target can be plugged into the flow definition

(CocoIndex allows user-defined export functions).

•

Incremental   Updates:  Critically,   CocoIndex   will   run   continuously   or   periodically   to   keep   the

index updated. Once the flow is set up, it can operate in live update mode, where it watches the

source  (the  staging  DB  or  files  that  DLT  updates)  for  changes  and  automatically  triggers  re-

indexing of new or changed data

4

. CocoIndex’s engine will only recompute what’s necessary –

e.g. if a new day of price data arrives, it will just process that day and append/update the index

5

. This ensures the Cognee memory is always up-to-date with minimal processing overhead,

which is important given continuous crypto data streams.

•

Data Enrichment: CocoIndex can integrate AI transformations in the flow. Beyond embeddings,

you could use an LLM to summarize a large on-chain event or classify the sentiment of a news

article. For example, a transform operation could call an LLM (via an API) to output a summary

text, which you then store as part of the index. This enrichment step means the agents later can

retrieve not just raw data but pre-computed insights (like “Summary of yesterday’s on-chain activity

for Token X”). Be mindful to balance what is precomputed (expensive LLM calls) vs. what the agent

can compute on the fly. For frequent tasks (like daily summary), it may be worth doing in the

pipeline and storing the results in Cognee so agents can just read them.

•

Output Schema:  Ensure the indexed data has a schema that Cognee expects. Typically you’ll

have   an  embedding   vector  for   any   text   content   and   metadata   fields   (like   timestamps,

3

identifiers, relationships). CocoIndex’s data model (basic/struct/table) can represent hierarchical

data; for instance, you might model that each  Token has a table of  Price records and a table of

News items. Those relationships can be translated into graph edges in Cognee. Documenting this

schema and transformation logic is important for extensibility.

Knowledge Memory & Semantic Search Layer (Cognee)

Cognee acts as the AI memory, combining a graph database and vector store to enable rich semantic

search and reasoning over the indexed crypto data. In practice, Cognee will interface with an underlying

graph database (e.g. Neo4j, Memgraph, or FalkorDB) and a vector DB (e.g. Qdrant, Redis, LanceDB) to

store the data ingested

20

21

. Key design points for this layer:

•

Hybrid Data Model:  The strength of Cognee is that it stores  entities  and  relationships  explicitly

(like   a   knowledge   graph),  and  stores   embeddings   for   textual   info

20

21

.   For   our   use   case,

define   the   entity   types   and   relations:   e.g.  Token,  Transaction,  Address,  Exchange,  NewsArticle,

Metric.   Relations   might   include  Token mentioned_in NewsArticle,  Token traded_on Exchange,

Address made Transaction,  Token has_metric Metric  (where  Metric  could be a  daily  data point

node with fields like price, volume). Cognee allows flexible schema, so you can adapt it as the

system evolves (new entity types or relations can be added without rigid migrations)

22

.

•

Data   Ingestion   into   Cognee:  As   CocoIndex   exports   data,   use   Cognee’s   API   to   add   it   as

DataPoints in the memory. Each DataPoint in Cognee is an atomic knowledge unit (with content

and   metadata)

23

.   For   example,   a   DataPoint   could   be   “Token=ETH,   Date=2025-10-30,

Price=$1800,   Volume=$1B”   or   “NewsArticle:   title,   content   embedding,   date,   mentions=[ETH]”.

Cognee’s  cognify  process will then incorporate these into the graph: e.g. linking the ETH token

node to that Price metric node for the date, linking the article node to ETH token node, etc. If

using Cognee’s community adapter (like the FalkorDB adapter), a lot of this graph management is

handled automatically once you define how to map fields to relationships.

•

Semantic Search: Cognee enables multiple query modes on the stored knowledge. Agents can

perform pure vector similarity search (e.g. “find documents about DeFi exploits” will retrieve news

articles or transactions with similar embeddings), pure graph queries (e.g. traversing relations:

“get all metrics for Token X in last 7 days”), or hybrid queries combining both
. In practice,
Cognee’s   API   provides   a   search()   method   where   you   can   specify   the   type   of   search.   For

22

24

instance,
  while
SearchType.GRAPH_COMPLETION   or   an  “insights”  mode   could   blend   graph   traversal   with

  SearchType.SIMILARITY   might

the   vector

  use

index,

semantic filtering

25

26

. This is powerful for crypto analytics – an agent’s query can be very

granular   (e.g.  “find   anomalous   spikes   in   volume   in   the   last   month   for   tokens   that   also   had   a

governance   proposal   news”).   Cognee   can   handle   a   query   like   that   by   first   finding   volume

anomalies (if those are flagged as nodes or properties) via graph filters and then checking news

similarity for governance topics via vectors, all in one call.

•

Persistence and Updates: Cognee is long-running – it provides the AI with long-term memory

beyond a single session

9

. This means data stays in the knowledge graph until pruned. We

ensure that as new data comes in, Cognee updates the memory (via the pipeline). Old data can

be archived if necessary (for example, you might periodically prune very old DataPoints to keep

the   working   set   manageable,   depending   on   storage   constraints,   or   rely   on   the   graph   DB’s

capacity). Observability of this layer includes monitoring the graph database (number of nodes/

edges) and vector index size, and watching query performance. Because Cognee is effectively a

server (it can run as a service, especially if using the MCP server mode), you should also track its

4

resource usage. Enabling logs for when   add/cognify/search   operations happen will help

catch any issues (like a malformed data point or slow query).

•

Access for Agents:  The agents in Agno will call Cognee’s functions to retrieve data. If Agno

supports the Model-Context-Protocol (MCP) or similar plugin interface, Cognee can be exposed

as a  tool  to the agents
. Alternatively, the agents can use a Python integration – e.g.
directly calling   cognee.search()   or using Cognee’s MCP client. In either case, the memory

27

9

layer is abstracted behind high-level queries (the agent doesn’t need to know if it’s querying a

vector or a graph or both – the Cognee memory handles it, returning a result set of relevant

knowledge).

•

Example:  Suppose the  Trend Summarizer  agent needs to summarize weekly market trends. It

could   query   Cognee   for  “7-day   price   movement   for   top   10   market   cap   tokens”.   Cognee   would

retrieve the relevant Metric nodes and perhaps any significant news articles attached to those

tokens. The agent then gets structured data (prices) plus contextual data (news text) to craft the

summary.   If   the  Anomaly   Detector  agent   is   running,   it   might   periodically   query   for  “unusual

volume deviations in the last 24h” – if Cognee has a field or flag for anomalies (perhaps computed

by CocoIndex or by a simple outlier detection script that writes into Cognee), it can return those

tokens/metrics. The agent then formulates an alert and could attach supporting info (like linking
the anomaly to a specific event or transaction from the graph). After producing an analysis, an
agent   can   call   cognee.add()   to   store   that   insight   (e.g.   a   node   like  Insight  with   type

AnomalyReport linking to the token and containing a description). Later, another agent or a user

query can find that insight via Cognee as well. This cycle effectively learns over time, building a

knowledge base of not just raw data but AI-generated interpretations.

Agent Orchestration Layer (Agno)

At the top, Agno coordinates the AI agents that utilize this knowledge. Agno (formerly Phi-Data) is an

agent framework for building multi-agent systems with integrated memory and tool use

28

. Within this

architecture:

•

Agent Team Structure: We can design multiple agents, each with a specialty, and a simple

“manager” agent or script to assign tasks. For example, agents could include:

•

Market Summarizer: Gathers market data and news from Cognee to produce human-readable

summaries of trends.

•

Performance Q&A Agent: Answers specific questions (e.g. “What was Token A’s ROI in Q3?”) by

fetching relevant data (price time series, maybe compare start/end values) and responding with

reasoning.

•

On-chain Investigator: Monitors on-chain data for anomalies or patterns (large transfers, contract

exploits) – using Cognee’s graph (which could link addresses and transactions) to find connected

entities.

•

Insight Archivist: A utility agent that takes outputs from others and logs them into Cognee

(though agents can call Cognee directly, it might be useful to centralize how insights are

recorded).

Agno allows these agents to run concurrently and even converse with each other if needed. They can

share   information   through   the   common   memory   (Cognee)   or   by   direct   messaging   orchestrated   by

Agno.

•

LLM Integration:  Each agent is backed by an LLM (or smaller model) for its reasoning. Agno

treats   LLMs   as   a   unified   API   and   gives   them   “superpowers”   like   tools   and   memory

29

.   In

5

practice, we will configure each agent with a prompt (defining its role and task), the model (e.g.

GPT-4   or   a   domain-tuned   model),   and   any   toolkits   it   can   use.   Tools   can   include   the   Cognee

search (as mentioned), web search or calculations, etc. For crypto analysis, one might include a

tool to fetch real-time price if needed (though ideally our memory is up-to-date enough), or a

plotting tool to visualize trends if the output is delivered to users. Agno supports ~80+ toolkits

out-of-the-box

30

, so we likely have what we need (e.g. an HTTP tool, maybe specific finance

APIs).

•

Memory Integration:  We configure Agno to use Cognee as the knowledge source for agents.

According to its design, Agno can connect agents to external knowledge bases like vector DBs

for RAG

12

. In our case, Cognee serves that role. Depending on Agno’s API, this might be as

simple as giving the agent a custom Tool that wraps a Cognee query (the agent can then call it

via its reasoning chain), or using Agno’s memory module if it accepts a vector store connection

string   (if   so,   we   might   point   it   to   Cognee’s   vector   index   backend   or   an   embedding   DB).

Regardless,   the   agent’s   prompts   can   be   designed   to  “always   consult   memory   for   relevant

information before answering”. During runtime, Agno will manage the sequence: the agent LLM

might ask to use the Cognee search tool with a certain query, Agno executes it (retrieving data

from Cognee), and the LLM incorporates that data into its answer. This loop continues until the

agent is satisfied and produces a final answer with sources (if required).

•

Multi-Agent   Orchestration:  Agno   provides   facilities   to   have   agents   collaborate

10

.   For

example, for a complex query like “What caused the sudden spike in Token X’s price yesterday?”, one

strategy is: the question is passed to a “research agent” which decomposes it – perhaps it asks

the knowledge base for price data and finds a spike, then asks Cognee for news around that

time.   If   multiple   potential   causes   appear   (say   a   partnership   announcement   and   a   whale

transaction), the agent could spin up two sub-agents: one to analyze the news impact, another

to analyze on-chain data. Agno’s framework can handle such workflows, where agents message

each other or pass results. This level of complexity might not be needed initially, but Agno’s

support for teams and hierarchical agents means the system can be extended to handle very

sophisticated analytical tasks in the future.

•

User Interaction:  Depending on how this system is delivered, you might have a single entry-

point agent that interacts with the user or a UI. For instance, a chat interface where the user can

ask any question; behind the scenes Agno routes it to the appropriate specialized agent (or a

chain of agents). If building a dashboard, the agents might run on a schedule and update charts

or reports automatically (e.g. every morning the Summarizer agent posts a summary to a Slack

channel). Agno can be run as a service (persisting agents in memory) or invoked on-demand for

each query. Running it as a persistent process means agents can maintain some context (but

since long-term context is mainly in Cognee, even a stateless invocation of agents per request is

fine, as they will fetch context each time).

•

Observability & Control:  Using Agno’s logging or  Playground  is highly recommended during

development

31

. The Playground UI allows you to simulate agent runs and see tool calls in real-

time,   which   helps   in   debugging   prompt   instructions   and   agent   behavior.   In   production,

instrument the agents to log each query, tool invocation, and result (without exposing sensitive

data). This is important for trust and debugging – if an agent produces an incorrect analysis, you

can trace whether it was due to faulty retrieved data, a reasoning error, or an LLM hallucination.

Additionally,   Agno’s   design   emphasizes   speed   and   efficiency

28

32

,   but   in   production   you

should monitor latency of responses. If certain queries are slow, you might need to optimize by

adding caching (e.g. cache recent Cognee query results or have the agent cache its last summary

to avoid recomputation on trivial changes).

6

Integration and Deployment Best Practices

Component   Integration:  The   four   tools   should   interoperate   in   a   pipeline   fashion,   but   you   have

flexibility in how to deploy them:

•

Tight Coupling (Pipeline Mode): For a smaller team or simpler deployment, you could run DLT

and CocoIndex as part of one data pipeline script and then Cognee and Agno in an application

script. For example, a daily cron job could execute a Python script that uses DLT to fetch new

data and immediately calls CocoIndex to update the index, then maybe triggers certain agents

(like the anomaly detector) to evaluate the new data. A separate API server might host an Agno

agent for interactive questions, querying the latest Cognee memory. This approach is easier to

develop   initially   (fewer   moving   parts),   but   be   mindful   of   timing   (ensuring   the   ingestion   job

completes before queries come in), and error isolation (a failure in ingestion shouldn’t crash the

query service).

•

Decoupled Services: In a more robust setup, each layer can run as an independent service:

•

DLT service: Runs continuously or on schedule, writing to a temporary store or message queue.

For example, a container running DLT pipelines every N minutes, outputting to a Postgres DB or

publishing messages of new data.

•

CocoIndex service: A long-lived process that listens for new data (or poll the DB) and runs the

indexing flow to update Cognee. CocoIndex can be run in live update mode – for instance, it

could continuously monitor the Postgres for new entries and process them as they arrive

33

.

This service would encapsulate all the data transformation logic. Running it separately means it

can be scaled or adjusted (e.g. if embedding many documents, give it more CPU/GPUs

independent of others).

•

Cognee server: Deploy Cognee’s own server (MCP Server if using that approach

9

27

, or simply

a FastAPI app that wraps Cognee’s Python calls). This becomes a knowledge service that agents

query via HTTP or RPC. The Cognee server would maintain connections to the graph DB and

vector DB. This separation is useful for observability – you can monitor memory DB performance

distinctly – and for scaling the memory horizontally or upgrading it (e.g. switching the vector

store from one technology to another without affecting agent code, since agents just talk to

Cognee’s API).

•

Agno agent service: This would be the user-facing layer. For instance, a web service that receives

user queries and creates an Agno agent (or uses a pool of pre-initialized agents) to handle them,

returning results. If multi-agent workflows are complex, you might even have an Orchestrator

service that triggers specific agents for certain events (like a scheduler triggering the Summarizer

agent daily, separate from the interactive Q&A agent). Agno itself is a Python framework, so this

service will essentially be a Python app using Agno’s library.

Each component as a service communicates through well-defined interfaces: DLT → CocoIndex via the

DB or data files; CocoIndex → Cognee via API calls or direct DB inserts; Agno → Cognee via Cognee’s
API. Using message queues (like an event after CocoIndex updates could notify agents of new data) can

further loosely couple the system.

•

Extensibility: The modular design ensures you can extend each part:

•

Adding a new data source: Create a new DLT pipeline for it, then add a branch in CocoIndex flow

(or a new flow) to process it into the index. Thanks to CocoIndex’s dataflow model and schema

versioning, this won’t break existing flows – new fields or tables can be integrated as needed

22

.

The graph schema in Cognee can also be extended on the fly (new node or edge types) without

downtime

34

.

7

•

Changing models: If a more accurate embedding model comes out or you train a custom crypto-

specific embedder, you can swap that in CocoIndex’s embedding step (update the operation spec

to use the new model). Then re-run a backfill of the index. Similarly, if you fine-tune an LLM for

the agents (say on financial tone or on prior QA data), you can configure Agno agents to use that

model (just change the model reference in Agno’s config and update API keys). The system is not

hardcoded to one model.

•

New   agent   capabilities:  Agno   makes   it   straightforward   to   add   new   tools   or   new   agents.   For

example, if you want an agent that generates reports in PDF, you can add a “PDFWriter” tool for

it or integrate a reporting library. Or if you want a “Portfolio Rebalancer” agent that takes user’s

holdings   and   suggests   trades,   you   can   create   one   that   uses   the   same   memory   but   with   a

different prompt and additional logic. The other agents remain unaffected.

•

Observability & Monitoring: Each layer should have logging and metrics:

•

DLT: log data ingestion stats (records ingested, time taken, errors). If using Airflow, use its

monitoring; if standalone, consider emitting events or writing logs to a centralized store.

•

CocoIndex: enable debug logging to trace flow execution. CocoIndex, by design, tracks data

lineage, which is useful if something looks off – you can trace which raw source produced a given

index entry

35

36

. You might expose a small dashboard showing the status of the indexing

(e.g. last update timestamp, number of items indexed).

•

Cognee: monitor DB health (e.g. Neo4j’s metrics or FalkorDB’s internal metrics) and vector search

latency. If Cognee’s MCP server is used, turn on any telemetry it offers. Because the agents rely

on Cognee for every query, any slowdown here will affect end-to-end latency – consider caching

frequent query results or using Cognee’s hybrid search efficiently (e.g. use filtered search queries

to limit the scope).

•

Agno/Agents:  use   Agno’s   built-in   logging   to   capture   each   agent’s   thought   process   (chain-of-

thought). For production, possibly pipe these logs to an APM solution. There are emerging tools

(e.g. OpenLLM telemetry) that instrument LLM calls – integrating one can help measure token

usage, response times, etc., for the agents

29

. Also implement error handling in agent logic:

e.g. if Cognee tool returns nothing, have the agent handle it gracefully (maybe respond “no data

available for that period” rather than confusing output).

•

Retrainability   &   Continuous   Improvement:  Over   time,   you   may   improve   the   system   by

retraining models or re-indexing data:

•

Retraining anomaly models: If you use a custom algorithm or model to flag anomalies (maybe

outside the scope of these tools, or done in CocoIndex using an ML function), you’ll want a

pipeline to periodically retrain it on new data. This could be a separate process that accesses the

accumulated data (since all data is stored in Cognee or the source DB, you have the history to

train on). Once retrained, you can update the model and the pipeline will start using the new

model.

•

Refreshing embeddings: As new jargon or token names emerge in crypto, the embedding model

might need updating. With CocoIndex, you can re-run the flow on all data with a newer

embedding model – thanks to incremental design, it can recompute embeddings for all text with

minimal effort, updating the vectors in Cognee. This could be scheduled (e.g. do a full re-index

quarterly with the latest model).

•

Feedback loop: Allow users or analysts to give feedback on agent answers (perhaps a thumbs up/

down). These can be logged and later used to fine-tune the LLM or to add rules. For example, if

the agent made a mistake in attributing a price spike to the wrong event, you could feed that

8

case into future prompt engineering or even store a correction in Cognee (so the agent can find

the corrected info next time).

•

Security & Privacy: Since this system deals with financial data, ensure proper security:

•

Manage API keys (exchange APIs, LLM keys) via secure config (environment variables or a vault,

not hard-coded)

37

38

.

•

If running agents that can execute tools, sandbox their abilities (Agno allows specifying exactly

which tools are available to each agent

39

). E.g. an agent shouldn’t have file system access

unless needed, to prevent accidental or malicious actions.

•

Use authentication and authorization if exposing an interactive Q&A service, especially if it can

perform actions (you don’t want an outsider triggering a trade or something via the agent).

•

Audit trails: For any critical decision made by an agent (like an automated trade suggestion), log

the rationale (which will be in the chain-of-thought) and have a human oversight process in place

initially.

In   summary,   this   architecture   leverages   each   tool’s   strengths:  DLT  reliably   ingests   and   structures

diverse crypto data sources, CocoIndex incrementally transforms and indexes that data (ensuring fresh

embeddings and structured knowledge), Cognee provides a powerful combined memory for semantic

and   relational   queries

20

21

,   and  Agno  enables   a   team   of   LLM-based   agents   to   reason   over   this

knowledge base with memory and tool use

28

12

. By running components as independent services

with clear APIs, the system is scalable and maintainable. Technical teams can extend the pipeline to new

data or analytics easily, observe the data flow at each stage, and retrain or tweak models as the crypto

landscape   evolves.   This   ensures   the   AI   agent   system   remains  extensible,

 observable,   and

continuously learning, providing up-to-date insights in the fast-moving world of cryptocurrency.

Sources:

•

DLT – Data Load Tool for ingesting messy sources into structured datasets

1

.

•

CocoIndex – Dataflow framework for building AI indexes from source data (with incremental

updates)

3

4

.

•

Cognee – Hybrid graph+vector AI memory to store entities, relationships, and enable

semantic+graph queries

20

21

; designed as a persistent “brain” for AI agents

9

.

•

Agno – Open-source framework for multi-agent systems, with support for memory, knowledge

bases, tools, and team orchestration

28

40

.

1

13

14

15

16

DLT - Qdrant

https://qdrant.tech/documentation/data-management/dlt/

2

3

4

5

33

35

36

Indexing Basics | CocoIndex

https://cocoindex.io/docs/core/basics

6

7

8

9

23

24

27

The Ultimate AI Engineer's Guide to the Official Cognee MCP Server

https://skywork.ai/skypage/en/ultimate-ai-engineer-guide-cognee-mcp-server/1977912822261551104

10

11

12

28

29

30

31

32

39

40

Agentic Framework Deep Dive Series (Part 2): Agno | by Devi |

Medium

https://medium.com/@devipriyakaruppiah/agentic-framework-deep-dive-series-part-2-agno-c45da579b7c0

17

Real-Time Markdown to HTML Conversion with CocoIndex Custom ...

https://cocoindexio.substack.com/p/real-time-markdown-to-html-conversion

9

18

r/cocoindex - Reddit

https://www.reddit.com/r/cocoindex/

19

20

21

22

25

26

34

Cognee | FalkorDB Docs

https://docs.falkordb.com/agentic-memory/cognee.html

37

38

How To Build Financial Agent with Agno & Groq

https://dataaspirant.com/building-financial-agent-agno-groq/

10

