Ingesting Ethereum & DeFi Data Using DLT Hub

Key Data Sources for Ethereum & DeFi Metrics

To comprehensively cover Ethereum and DeFi protocol metrics, we combine on-chain data with external

aggregator APIs and subgraphs:

•

On-Chain Blockchain Data (RPC/Explorer) – Ethereum mainnet (and L2s like Arbitrum) provide

raw data on smart contract deployments, transactions, and events. For example, Etherscan’s API

allows   retrieving   contract   ABIs   and   creation   transactions   for   verified   contracts

1

.   Such

endpoints can be polled via JSON-RPC or REST to track new contract deployments, function call

counts, or event logs. Beaconcha.in (an Ethereum 2.0 explorer) offers a rich API for consensus-

layer metrics (e.g. validator counts, staking yields) with both historical and real-time data

2

.

These   sources   ensure   low-level   smart   contract  usage  data   (calls,   events,   deployments)   is

available directly from the blockchain.

•

The Graph Subgraphs (Protocol Indexes) – Many DeFi protocols expose subgraphs that index

their   contract   events   and   state,   queryable   via   GraphQL.   For   instance,   Aave   maintains   official

subgraphs   mapping   lending   pool   events   to   a   GraphQL   API

3

,   and   Pendle’s   community

subgraph indexes its yield markets

4

. Using these, we can pull structured  protocol metrics

like total deposits, borrows, user positions, or Pendle’s traded yield volumes. Subgraphs abstract

away raw on-chain parsing by providing high-level entities (e.g. Aave reserves with liquidity rates,

Pendle   pools   with   volumes).   This   is   ideal   for   historical  usage   statistics  and   state   (e.g.   Aave

reserve utilization over time) without running a full node.

•

DeFi  &  Market  Data  APIs  –  External  aggregator  APIs  provide  protocol-level  metrics  such  as

prices, TVL, and interest rates. Key sources include CoinGecko for token price history, DeFiLlama

for TVL and yield data, and project-specific APIs:

•

CoinGecko: Offers historical price charts for tokens. For example, Ethena’s USDe and sUSDe prices
can be fetched via CoinGecko’s API (e.g.  coins/ethena-usde/market_chart ) with daily

historical data

5

6

. This helps compute peg deviation (difference from $1.00) by comparing

USDe price to 1 USD

7

.

•

DeFiLlama: Provides up-to-date TVL and yield metrics across DeFi. It has endpoints for stablecoin

supply by chain (e.g. USDe circulating supply on each chain)【23†】, protocol TVL (Ethena,
Pendle, etc.), and yield rates. For instance, Ethena’s total USDe supply and chain breakdown

come from DeFiLlama’s stablecoin API

8

, and Aave’s lending APY can be pulled from

DeFiLlama’s yield database using a pool ID【21†】. Data on DeFiLlama is typically updated
hourly

, balancing freshness with load.

9

•

Aave & Ecosystem APIs: The Aave ecosystem has specialized APIs like Aavescan, which provides

live and historical lending rates, market sizes, and even cross-protocol yields. Aavescan’s
endpoints (e.g.  /v2/reserves/latest ) return current supply/borrow APRs and totals for all

Aave markets

10

. It also offers historical snapshot endpoints for hourly or daily data

11

12

.

Notably, Aavescan covers related protocols (Ethena’s sUSDe, Morpho, Compound, etc.) via its

“ecosystem” feeds

13

. This gives a one-stop source for interest rates (APY/APR) and market

size metrics across multiple platforms, sourced directly from on-chain data

14

.

1

•

Pendle API: Pendle Finance provides a REST API for its V2 protocol (e.g. endpoints to get yield

token prices, pool info, etc.). This can complement the subgraph for real-time rates. For example,

Pendle’s API can return current principal token (PT) prices and implied yields as mentioned in

their docs

15

. By using Pendle’s API or subgraph, we can track fixed vs floating yield rates (e.g.

implied yield from PTs vs actual lending APY).

•

Beaconcha.in: As mentioned, the Beaconcha.in API can supply staking metrics like validator

counts, staking APR%, etc., which are useful for context (e.g. Ethena’s yield partly relies on

staking yields and perp funding rates). Beaconcha.in’s comprehensive API allows pulling

historical series (e.g. daily active validators) and real-time updates on the Ethereum beacon chain

2

.

By   prioritizing   these   sources,   we   ensure   coverage   of   both  smart   contract   metrics  (deployments,

usage, calls) from on-chain data and  protocol performance metrics  (TVL, APY, prices, funding rates)

from indexers and aggregators.

Integrating Sources with DLT Hub Connectors

DLT Hub (the   dlt   data loading toolkit) supports multiple connector types to ingest the above data

sources in a unified pipeline:

•

REST API Source Integration:  DLT provides a generic REST connector ( rest_api   source) to

declaratively fetch data from HTTP endpoints

16

. We can define each API in the registry with its

URL,   HTTP   method,   params,   and   JSON   parsing   logic.   For   example,   the   registry   entry   for
CoinGecko USDe price uses   resource_type: "api"   with a GET URL and query params for

5

currency and date range
. The  parser  section then specifies how to extract and transform
fields: e.g. explode the returned price array and map it into our schema’s fields ( timestamp
and  value ), then set static fields like  protocol = Ethena ,  asset = USDe ,  metric =
price

. This declarative approach simplifies pulling JSON data and mapping it into rows.

6

Similarly, DeFiLlama and Beaconcha.in endpoints can be integrated by providing the URL and
parsing   the   JSON   response.   For   instance,   a   DeFiLlama   yield   endpoint   returning   {apy,
apyPct1D, ...}  can be mapped to a single-row update of APY values. DLT’s REST client also

supports pagination and rate-limit handling, which we would use for endpoints returning time-

series (e.g. historical TVL charts). Each such source in DLT can run on a schedule (e.g. daily for
historical backfill, and every few minutes for incremental updates as defined by the  cadence )

17

.

•

GraphQL   Source   Integration:  For   The   Graph   subgraphs   and   other   GraphQL   APIs,   DLT’s

GraphQL source allows sending queries and retrieving JSON results similarly. In the registry, we
define  resource_type: "graphql"  and provide the query or query template. For example,
an   Aave   v3   subgraph   query   could   request   reserve   data   ( symbol,   liquidityRate,
totalATokenSupply,   etc. )   across   all   reserves.   The   registry   indicates   using   The   Graph’s

endpoint for “Aave v3 mainnet” and a query that pulls reserve rates and totals. At runtime, DLT

will POST this GraphQL query and capture the response. We then parse it by specifying JSON

paths   to   the   fields   of   interest   (much   like   REST).   This   yields   structured   tables   like
aave_reserves   with   fields   for   each   reserve’s   utilization   and   rates.   Likewise,   the   Pendle

subgraph   on   mainnet   can   be   queried   for   entities   like   YieldContracts   or   Pairs   (which   contain

volumes,   prices,   etc.

18

19

).   Using   GraphQL   sources   ensures   we   get  up-to-date   on-chain

metrics (subgraphs index new blocks within minutes) and can pull multiple related fields in one

request. If a protocol offers its own GraphQL (e.g. Aave’s official GraphQL API for market data

2

3

), we can integrate it the same way by pointing to the GraphQL endpoint and writing the

appropriate query.

•

OpenAPI-Based   Integration:  DLT   Hub   includes   an   OpenAPI   client   generator   ( dlt-init-
openapi ) that can bootstrap multiple endpoints from an API’s OpenAPI (Swagger) specification

16

. This is useful for large APIs like Aave’s or others that provide a JSON spec of all routes. For

instance, if Aave’s backend API or Pendle’s API has an OpenAPI spec, we could feed it to the

generator   to   automatically   produce   DLT   source   definitions   for   each   endpoint   (with   paths,

parameters,   and   default   parsing).   This   greatly   speeds   up   integration   by  bulk-generating

pipelines  from   the   spec.   We   would   then   review   and   customize   any   complex   endpoints   (e.g.

adding auth keys or tweaking pagination as needed). The OpenAPI generator ensures we don’t

miss useful endpoints – for example, it could generate sources for Aave’s rate history, pools list,

etc., in one go. After generation, we can selectively enable the resources we need (such as only

the rates history and assets metadata endpoints from Aavescan or Aave API). In summary, this

approach provides a quick way to integrate comprehensive APIs by leveraging their published

specs, which is easier than hand-coding each endpoint.

Using   these   DLT   connectors,   we   can   set   up   a  unified   pipeline  that   pulls   from   all   sources   –   REST,

GraphQL, and even RPC (treated as REST POST calls) – on a schedule. Each source’s integration pattern
(GET   vs   GraphQL   query)   is   defined   in   the   registry,   and   DLT   will   handle   authentication   (API   keys   in
secrets.toml   if needed), paging, and incremental cursors. The output from all connectors will be

normalized into our target schema automatically.

Metrics Coverage and Source Mapping

With the data sources integrated, we can gather a wide range of metrics vital for DeFi research. Below

we map specific metrics to their sources and how DLT pipelines would gather them:

•

Smart Contract Deployments & ABIs: To track new contract deployments (e.g. new versions of

protocols or new tokens), we can query Ethereum logs for contract creation or use explorer APIs.

Etherscan’s  Contracts  API  provides  the  creation  transaction  hash  and  timestamp  for  a  given

contract   address,   which   can   be   used   to   build   a   timeline   of   deployments
Etherscan’s  getabi  endpoint returns the ABI for verified contracts

1

20

.   Additionally,

, allowing us to decode

method call frequencies if needed. In DLT, we can set up an Etherscan REST source with the
appropriate module/action params (e.g.   module=contract&action=getabi&address=... )

to fetch and store contract metadata. This could be coupled with an on-chain data stream (via

Web3   RPC   subscriptions   or   polling   new   blocks)   to   detect  usage  of   specific   contracts   (e.g.

counting transactions to Aave’s addresses to gauge usage outside of subgraphs).

•

Smart   Contract   Usage   Metrics:  For   detailed   usage   (method   call   counts,   event   counts),   The

Graph   subgraphs   are   invaluable.   The   Aave   subgraph   can   provide   metrics   like   number   of

deposits, borrows, liquidations, and unique users over time by querying event entities (e.g. count
of   Deposit   events per day). Similarly, Pendle’s subgraph tracks volume of yield trades and

liquidity provided

18

. We will use GraphQL queries in DLT to extract these aggregated usage

metrics on a schedule (e.g. daily aggregation of events). Where subgraphs are not available (or
for cross-checking), we could fall back to RPC: for instance, use  eth_getLogs  via an Ethereum

node RPC to count specific event signatures in a block range. DLT can call an Infura/Alchemy

JSON-RPC endpoint by a POST request with a JSON body (treated as a REST call). However, for

efficiency and historical depth, subgraphs are the preferred source of usage statistics.

3

•

Total Value Locked (TVL):  TVL for each protocol (Ethena, Aave, Pendle) can be obtained from
DeFiLlama’s   API.   We   will   configure   a   REST   source   pointing   to   https://api.llama.fi/
protocol/<name>   which returns TVL over time and by chain. For example, Ethena’s entry on

DeFiLlama yields its total TVL and breakdown (likely mostly on Ethereum)【18†】. DLT will parse
the returned time-series (dates and TVL values) into our schema ( metric = TVL, value   in

USD). If needed, we supplement this with on-chain computed TVL (e.g. summing Aave reserves

from subgraph data for validation). DeFiLlama updates TVL data roughly every hour

9

, and our

pipeline can fetch it daily or more frequently for near-real-time monitoring.

•

Interest Rates and APY: For lending protocols like Aave, interest rates (supply APY, borrow APR)

are key. We have multiple sources:

•

The Aave subgraph (v3) provides current liquidity and borrow rates for each asset in real time
(fields like  liquidityRate  in ray units). We can query those and convert to APY percentages.

•

Aavescan API provides already-calculated APRs/APYs for Aave and even other markets. Using
the  reserves/latest  endpoint yields the live supply/borrow APR for every Aave asset on

10

. We can ingest that for instantaneous rates, and use the  hourly-snapshots

each market
or  daily-snapshots  endpoints for historical rate time-series
. This covers Ethereum
mainnet and L2 deployments (by specifying  market=aave-v3-arbitrum  etc. in the query) to

12

11

capture Aave on Arbitrum, Polygon, etc.

•

DeFiLlama Yields: As an alternative or supplement, the DeFiLlama yields API tracks specific

pools’ APYs. We have integrated, for example, the Aave v3 USDC (Ethereum) supply APY via a

pool ID. This gives a live APY and 1-day/30-day APY change for that asset, which serves as a

proxy for the protocol’s rate. Similarly, Ethena’s sUSDe yield (which represents the stablecoin’s

savings rate) is tracked as a yield pool on DeFiLlama. Ingesting that via DLT provides the current
yield on sUSDe and its historical trend (via the  .../chart/<pool-id>  endpoint returning APY

over time).

•

Pendle Yields: Pendle’s implied yield (from PT discount) can be derived from either the subgraph

or Pendle’s own API. The subgraph contains entities for each yield token and its exchange rate,

so we can compute implied APY. Pendle’s API might directly provide the current implied yield for

a given market (e.g. an endpoint for PT price or yield). We will gather Pendle’s fixed yield rates

(PT APYs) and compare them to floating rates (e.g. Aave’s APY) for metrics like the fixed vs float

spread

21

.

•

Peg Deviation: For Ethena’s stablecoin USDe, maintaining the $1 peg is crucial. We calculate peg

deviation by comparing the market price of USDe to 1.00 USD

7

. The market price comes from

CoinGecko’s historical price feed (which we ingest every 5 minutes as per our cadence)

17

. DLT

will store a time-series of USDe price; from that we can derive a metric for deviation (perhaps

computed in queries or as a derived field in our registry). Similarly, for sUSDe (the yield-bearing

variant), we can monitor its price relative to USDe (it should slowly appreciate if yield is accruing).

Both price series are in our pipeline via CoinGecko

22

23

.

•

Funding Rates: Ethena’s protocol yield is influenced by perpetual swap funding rates on external

markets (since Ethena employs delta-neutral hedging). While there isn’t a direct on-chain feed for

“funding   rate,”   we   aim   to   include   data   from   sources   like  exchange   APIs   or   indexers.   For

example,  if  Ethena  uses  ETH  perpetuals,  we  can  use  an  exchange’s  API  (Binance,  Bybit,  or  a

decentralized perp like dYdX/GMX if applicable) to fetch the current funding rate for ETH. DLT can

integrate such REST endpoints (many exchanges have public endpoints for funding rates every 8

hours). We would set up a source for “funding_rate” that queries the rate periodically and tags it
with   protocol = Ethena, metric = funding_rate . Additionally, we can use  Messari’s

4

API or other analytics platforms if available; e.g. Messari provides a profile on USDe with a recent

funding rate metric

24

. Given funding rates can be volatile, we’d schedule this more frequently

(perhaps hourly). This data helps measure carry trade yields and risks for Ethena.

By mapping each metric to the best source, our DLT Hub pipelines ensure comprehensive coverage. We

prefer official or high-quality sources (e.g. subgraphs for exact on-chain data, or well-known APIs like

CoinGecko/DeFiLlama for market data) to maximize accuracy and completeness.

Multi-Chain Data Ingestion (Mainnet & L2)

Since some protocols operate on multiple chains, the pipelines will be designed to ingest data from

each relevant network:

•

Ethereum   Mainnet:  Most   sources   (Ethena’s   contracts,   Pendle   mainnet,   Aave   Ethereum)

naturally focus on chainId 1. Our registry entries (CoinGecko prices, mainnet subgraphs, etc.)
have   chain: Ethereum   in their metadata to reflect this. For instance, Ethena’s USDe supply

and price are primarily on Ethereum (though our DeFiLlama source will also reveal if any USDe

exists on other chains)【23†】.

•

Arbitrum   (and   other   L2s   for   Aave):  Aave   v3   is   deployed   on   various   networks   (Arbitrum,

Optimism, Polygon, etc.). To ingest Aave’s data on Arbitrum, we can either:

•

Use Aave’s Arbitrum subgraph – by pointing the GraphQL endpoint to the Arbitrum subgraph

deployment ID (the query structure remains the same). We would create a separate source entry
(e.g.  aave_v3_arbitrum_subgraph ) differing only in the subgraph endpoint and perhaps
chain: Arbitrum  in the metadata.
Use Aavescan’s API with the  market  parameter set to  aave-v3-arbitrum . For example,
calling  /v2/reserves/latest?market=aave-v3-arbitrum  yields live rates for Arbitrum

•

Aave markets

25

. Similarly, historical endpoints accept the market slug. We will incorporate

these by parameterizing the API calls for each network.

We ensure the data is tagged by  chain  (so Ethereum vs Arbitrum metrics are distinguishable). In the
global schema,  chain  is a common field

, so the pipeline will fill this accordingly (e.g. “Ethereum”,

26

“Arbitrum”) for each record.

•

Pendle on Other Chains: Pendle launched initially on Ethereum, but if Pendle is multi-chain (say

also on Arbitrum or BSC), we would replicate the subgraph or API calls for those chains.

DeFiLlama’s Pendle TVL or volume would automatically sum across chains if present. Our system

can either store aggregated metrics (total TVL) or break down by chain using multiple sources.

Given the registry’s design, we could have one source per chain or a unified source that iterates

through chains.

In summary, DLT pipelines can be configured per network. We use the same connector but different

endpoints or parameters for each chain’s data. The result is a multi-chain dataset where each record’s
chain  field lets analysts filter by network. This approach captures L2 activity (e.g. Aave on Arbitrum)

which is crucial for a full picture of protocol usage.

5

Archival Storage with DuckLake/MotherDuck

All   ingested   data   —   whether   real-time   streams   or   historical   backfills   —   is   persisted   for   long-term

analysis using a DuckDB-based lakehouse (DuckLake/MotherDuck). DLT Hub can load data directly into
DuckDB tables, and our integration leverages that for an append-only historical archive:

•

DuckDB   as   Destination:  The   DLT   pipeline   is   configured   to   use   DuckDB   (or   MotherDuck,   its

cloud-hosted counterpart) as the destination for all sources. This means each run of the pipeline

will batch-load new data into DuckDB. DuckDB’s columnar storage is well-suited for analytical

queries on time-series data. We organize each dataset (source) as a table or set of tables within
  coingecko_usde_price   might   load   into   a   table   named
DuckDB.   For   example,
coingecko_usde_price   or a unified   prices   table partitioned by asset. DLT takes care of

schema creation and can  merge or append  based on primary keys defined in the registry

17

(ensuring no duplicates if rerunning incremental loads).

•

Cloud Data Lake Integration: For scalable storage, we use the DuckLake approach – treating an

object store (like Cloudflare R2 or S3) as the backing store for DuckDB tables

27

. In practice,

after DLT loads data into DuckDB, the data can be exported to Parquet files on Cloud storage.

DuckLake (a DuckDB extension) maintains a lightweight catalog of these files and table schemas.

This gives us the benefits of a data lakehouse: the data is stored durably as partitioned Parquet

(efficient   for   long-term   retention   and   big   queries),   while   DuckDB/MotherDuck   provides   a

convenient SQL query layer on top. MotherDuck in particular can keep the metadata and small

recent fragments, while offloading large historical batches to cloud storage, combining the two

seamlessly.

•

Historical + Real-Time Merge:  Our ingestion strategy backfills historical data once and then

continually appends new data (micro-batches). For instance, when a source is first added, we pull

the full history (e.g. all past TVL or price data) and load that. Thereafter, we schedule frequent

incremental fetches (every 5 minutes for prices, hourly for TVL, etc.) to get new records. These

new records are appended as new rows in DuckDB. Using a unified timestamp index and primary

keys as per the registry, the pipeline can  deduplicate or merge  if needed

28

17

. We avoid

rewriting  large  tables;  instead,  each   batch  is   a   new   Parquet   file   partition   (e.g.   by   date).   This

design ensures that the archive grows over time, capturing a complete timeline of data. It also

means we can query across the entire history or just the latest state easily in DuckDB.

•

Querying   and   Analysis:  With   MotherDuck,   authorized   users   can   run   SQL   queries   on   the

archived   data   (potentially   via   a   web   UI   or   API)   without   needing   to   download   everything.

DuckDB’s   performance   allows   interactive   slicing   of   large   datasets   (millions   of   price   points   or

events). Analysts can, for example, join Ethena’s USDe price history with Aave’s historical borrow

rate to compute the net carry spread on any given day (one of our derived metrics)

21

. Because

all data adheres to the global schema, tables can be unioned or joined on common fields (e.g.

join by timestamp/protocol). The lakehouse approach also facilitates time-travel analysis – since

we append data rather than overwrite, one could reconstruct past states or see how metrics

evolved.

In   summary,   DuckLake/MotherDuck   integration   provides  robust   archival   storage  for   all   ingested

blockchain data. Every metric and event we pull via DLT ends up in a queryable, persistent format. This

supports both the immediate research needs (e.g. analyzing current peg stability or yield spreads) and

long-term studies (trends over months/years), all from the same unified dataset stored in DuckDB.

6

Schema Alignment and Global Registry Structure

A crucial aspect of our approach is enforcing a consistent schema across all data sources, guided by
the  global  registry  ( crypto_sources.json ).  Each  source’s  data  is  mapped  into  a  set  of  common

fields   so   that   disparate   metrics   can   coexist   and   be   compared   easily

26

.   Key   points   of   this   schema

alignment include:

•

Common Fields:  All records use standardized fields such as   timestamp ,   source ,   chain ,
protocol ,   asset ,   metric ,   value ,   and   units
.   For   example,   when   ingesting
CoinGecko   prices,   the   JSON   timestamp   and   price   are   transformed   to   our   timestamp   and
value , and fields like  asset = USDe ,  protocol = Ethena ,  units = USD  are attached to

26

each   record

6

.   This   uniform   structure   means   a   price   data   point   from   CoinGecko   looks

structurally similar to a TVL data point from DeFiLlama or a rate from Aavescan (each will have a

timestamp, metric name, value, etc.). It simplifies loading into DuckDB (one coherent schema)

and allows joining different metrics by time or protocol.

•

Primary Keys and Deduplication: The registry defines primary key fields for each source (often

a   combination   of   timestamp,   protocol,   metric,   etc.)

29

17

.   DLT   uses   these   to   ensure

idempotency – if the same data is fetched twice, it won’t create duplicates in the target table. For
instance, for a daily TVL series,  date + protocol  could be the key; for event streams, maybe

a unique event ID or block number. By aligning on these keys, we can merge streaming data with

historical data confidently (any overlap will be reconciled). It also helps when we derive new

metrics: they can use the same keys so that they integrate with base data.

•

Global   Metric   Definitions:  We   maintain   a   consistent   naming   for   metric   values   (e.g.   use
price   for all token prices,   tvl   for total value locked,   supply_apr   vs   borrow_apr   for

rates, etc.). This consistency is important for comparability and for calculating derived metrics.

The   registry   documentation   provides   examples   like  net_carry_spread   =   sUSDe_APY   –

Aave_borrow_APR

21

,   which   assumes   those   metrics   exist   and   are   named   predictably.   By

adhering to the registry’s metric naming, we ensure that once data is loaded, analysts can easily

pick the fields to plug into such formulas. Similarly, units are standardized (e.g. all dollar values
labeled  USD , all percentage yields perhaps stored as fractions or %).

•

Quality   and   Provenance   Fields:  The   schema   also   anticipates   confidence   or
provenance_url   fields

, which we populate when available. For example, if we scrape a

30

value from a website or use an API that provides a confidence interval, we could store that. Or
we might include a  provenance_url  linking back to the source (like a specific CoinGecko page

or Etherscan link for a contract event) for traceability. Ensuring these fields exist for all sources

means we can later filter out low-confidence data or audit a particular data point’s origin, which

is important in research settings.

Overall, the global registry acts as the  blueprint  for integration: every new source is added with a

mapping   into   this   common   schema,   and   tested   for   compatibility.   This   yields   a   harmonized   dataset

where, for instance, an Ethena metric and an Aave metric can be aligned on the same timeline and

directly compared. The DLT pipeline, guided by the registry, automates this schema mapping so that

data lands in our lakehouse already clean and standardized

31

. This structure greatly enhances the

utility of the data for DeFi research needs.

7

Data Freshness, Completeness, and Research Alignment

Finally, we evaluate the data pipeline in terms of how up-to-date and comprehensive the information is,

and how it serves our research objectives:

•

Real-Time vs Historical Freshness:  Our integration captures both historical backfill and real-

time updates. Historical completeness is achieved by one-time backfills: e.g. pulling  full price

history from CoinGecko (max history)

32

, or all past TVL from DeFiLlama. These provide context

and long-term trends (e.g. how peg stability held over months, how Aave’s TVL grew). For real-

time   data,   many   sources   update   frequently.   CoinGecko   prices   are   near   real-time   (within

minutes),   Aave   subgraphs   update   with   each   new   block   (sub-minute   delays),   and   Aavescan

streams   live   rates   with   minimal   lag

14

.   DeFiLlama   updates   key   metrics   hourly

9

,   which   is

usually sufficient for metrics like TVL or supply (they don’t swing wildly minute to minute). We

configure the DLT pipeline schedule accordingly – critical high-frequency metrics (prices, interest

rates) are fetched every few minutes, whereas slower metrics (TVL, supply) update hourly or

daily. This ensures that our dataset is  fresh  enough to alert us to rapid changes (like a depeg

event or a rate spike) while not overloading with redundant pulls.

•

Data Completeness and Coverage:  By leveraging multiple sources, we mitigate gaps in any

single source. The Graph subgraphs give complete on-chain event history for their protocols

(unless a subgraph has indexing issues, which we monitor). External APIs often aggregate data

we might not easily get from the chain (e.g. an index of all stablecoins by chain). In cases where

one source might miss something, another can fill in – for example, if a subgraph is lagging,

Aavescan’s API can provide the latest rates. We have also included documentation sources (like

protocol docs and risk analyses) in the registry for qualitative context, though those are outside

the scope of metrics ingestion. The result is an  all-around view: from low-level contract data

(deployments, calls) to high-level protocol health metrics (TVL, APY, peg) across Ethena, Aave,

Pendle, and the surrounding ecosystem. This comprehensive coverage aligns well with research

needs to analyze things like yield dynamics (we have both sides of the carry trade: borrow rates

from Aave and yield rates from Ethena/Pendle) and risk factors (we track peg deviations and can

correlate them with market events or funding rate changes).

•

Data Quality and Alignment with Needs:  Each integrated source is reputable and/or directly

sourced from the protocol, which ensures data quality. For example, CoinGecko and DeFiLlama

are widely used in the community for reliable stats, and subgraphs are official or community-

verified. We also respect each source’s usage policies (rate limits noted in the registry to avoid

oversampling

32

). The data is structured in a way that researchers can easily query it for specific

analyses. Need the current leverage ratio of Ethena? – Combine USDe supply (from DeFiLlama)

and reserve fund data (from Ethena’s on-chain info, if available) in DuckDB. Want to examine

utilization   rates  on   Aave?   –   Use   the   subgraph   data   (total   supplied/borrowed)   to   compute

utilization percentages per our derived metric formula

7

. All these are straightforward because

the   pipeline   has   already   collected   and   organized   the   necessary   data.   Moreover,   by   archiving

everything historically, we enable analyses like “how did Aave’s APY react to the last Fed rate hike?”

or “has USDe’s peg deviation correlated with funding rate trends?” – questions that require looking

back in time, which our dataset can answer.

In conclusion, using DLT Hub we have set up a robust, extensible data pipeline that ingests historical

and streaming blockchain data from Ethereum and related DeFi protocols. By prioritizing high-value

sources   (smart   contract   subgraphs,   DeFi   aggregator   APIs,   and   direct   RPC   where   needed)   and

standardizing   the   data   into   a   lakehouse,   we   ensure   that   metrics   like   deployments,   TVL,   APY,   peg

8

stability, and funding rates are readily available for analysis. The integration techniques (REST, GraphQL,

OpenAPI)   allow   direct   plugging   of   these   sources   into   DLT’s   workflows,   and   the   alignment   with   our

global schema means the data is immediately useful for cross-protocol research. This pipeline not only

provides immediate insights (with fresh data updated continuously) but also builds an enduring archive

in DuckDB/MotherDuck for long-term DeFi analytics and research, fully in line with our needs.

Sources: The above approach references the Ethena/Aave/Pendle data registry structure

26

6

, uses

known   blockchain   data   APIs   (CoinGecko,   DeFiLlama,   Aave   subgraphs,   Beaconcha.in)

2

14

,   and

follows best practices from DLT Hub documentation for integrating REST and GraphQL sources

16

.

Each integrated source’s documentation (CoinGecko, Etherscan, Aave, etc.) was considered to ensure

data accuracy and completeness in the pipeline. The system design aligns with the described DuckLake

lakehouse architecture for persistent storage, enabling efficient analysis of the collected data over time.

1

20

Get Contract ABI - Etherscan

https://docs.etherscan.io/api-reference/endpoint/getabi

2

Data Sources | Treehouse Protocol

https://docs.treehouse.finance/protocol/tesr/data-sources

3

GraphQL - Aave

https://aave.com/docs/developers/aave-v3/getting-started/graphql

4

Pendle V2 Mainnet Subgraph | Graph Explorer

https://thegraph.com/explorer/subgraphs/ExXGU3ub2nrT5stPk5cH4hSk2qunJcMcP8eX5GAhrZhe?

view=Query&chain=arbitrum-one

5

6

7

8

17

21

22

23

26

29

30

32

crypto_sources.json

file://file_0000000044ec71f48b4a18b6ea61fe9e

9

Frequently Asked Questions - DefiLlama

https://docs.llama.fi/faqs/frequently-asked-questions

10

11

12

13

14

25

Aave Ecosystem API | Aavescan

https://aavescan.com/api

15

Frequently Asked Questions | Pendle Documentation

https://docs.pendle.finance/Developers/FAQ/

16

README.md

https://github.com/dlt-hub/dlt_demos/blob/e703774d3dd266c7cec3480abb6aacf307c95986/dlt-init-openapi-demo/

README.md

18

19

GitHub - pendle-finance/subgraph-v3

https://github.com/pendle-finance/subgraph-v3

24

Ethena: Delving into the Mechanics and Risks of USDe - Chorus One

https://chorus.one/reports-research/ethena-delving-into-the-mechanics-and-risks-of-usde

27

28

31

Integration Plan for a Crypto Analytics & Discovery System.pdf

file://file_0000000094447243a41896800137c4f6

9

