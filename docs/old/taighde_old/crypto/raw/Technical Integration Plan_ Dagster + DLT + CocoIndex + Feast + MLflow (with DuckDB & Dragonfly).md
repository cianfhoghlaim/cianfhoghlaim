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

