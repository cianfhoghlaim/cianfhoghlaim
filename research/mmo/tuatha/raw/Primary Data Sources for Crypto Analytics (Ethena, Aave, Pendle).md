Primary Data Sources for Crypto Analytics

(Ethena, Aave, Pendle)

Below is a structured list of primary data sources relevant to Ethena, Aave, and Pendle, covering core

metrics like price, TVL, APY, and funding rates. Each source definition includes its base URL or OpenAPI

spec,   key   endpoints/paths,   required   parameters   and   HTTP   methods,   response   parsing   details,
suggested DLT Hub integration settings ( data_selector ,   primary_key ,   write_disposition ),

ingestion   cadence,   field   mappings,   and   notes   (including   derived   metrics   that   can   be   computed

downstream   in   DuckDB).   The   sources   are   grouped   by   type:  REST   APIs,  OpenAPI-supported   APIs,

GraphQL (subgraph) APIs, and an additional HTML-scraped source for completeness.

REST API Sources (Manual Integration Required)

•

•

•

CoinGecko – USDe Price History (Ethena) – REST JSON API for Ethena’s USDe stablecoin price
Base URL & Endpoint: https://api.coingecko.com/api/v3  (CoinGecko v3). The specific
endpoint is  /coins/ethena-usde/market_chart  with query params
vs_currency=usd&days=max  to retrieve the full USD price history.
Method & Required Params: HTTP  GET  with required params  vs_currency  (set to "usd")
and  days  (set to "max" for full history). No API key or auth needed (CoinGecko’s free public API;

•

rate limits apply).
Response Format & Parsing: Returns JSON with arrays under keys like  prices ,
market_caps , etc. The  prices  array contains timestamp and price pairs. For integration,
use a JSON list selector on  prices  (e.g.,  data_selector: "prices"  corresponding to JSON
path  $.prices[*] ). Each element is  [timestamp, price] . The pipeline should explode
this list and map  [0] → timestamp  and  [1] → value . The timestamp is in milliseconds

•

•

since epoch – convert to datetime.
Field Mappings: After parsing, assign fields:  timestamp  (parsed from ms epoch),
protocol: "Ethena" ,  asset: "USDe" ,  metric: "price" ,  value: <USD price> ,
units: "USD" . The  source  can be recorded as "CoinGecko".
Suggested  primary_key : ["timestamp", "asset", "metric", "source"]  (to uniquely
identify each price point). Write disposition: use  "append"  for incremental loads (or
"merge"  if re-fetching overlapping time ranges to avoid duplicates).

•

Cadence: Backfill once (full history on initial load), then incremental updates ~every 5 minutes

to append the latest price data. CoinGecko updates price feeds frequently; a 5m polling aligns

with typical data freshness.

•

Derived Metrics: Downstream, the peg deviation can be calculated from USDe’s price (e.g.,
peg_deviation = |USDe_price - 1.00| ) to quantify how far USDe strays from its $1 peg.

•

Notes: CoinGecko’s free API has rate limits (e.g., 50-100 calls/minute globally). This source does

not   require   authentication.   An  OpenAPI   spec  for   CoinGecko   is   unofficially   available   (see

OpenAPI section), but we can integrate this endpoint easily via DLT’s REST API source template.

•

CoinGecko – sUSDe Price History (Ethena) – REST JSON API for Ethena’s staked USDe (sUSDe) price

1

•

Base URL & Endpoint: Same CoinGecko base as above. Endpoint:  /coins/ethena-staked-
usde/market_chart?vs_currency=usd&days=max  (targeting sUSDe token’s price history in

USD).
Method & Params: GET  request with  vs_currency=usd, days=max  (identical structure to

•

•

USDe endpoint). No auth needed.
Response & Parsing: JSON with  prices  array of  [timestamp, price]  points. Use
data_selector: "prices"  (JSON path  $.prices[*] ) to extract the list. Map index 0 to

timestamp  (ms → datetime) and index 1 to  value  (price).
Field Mappings: timestamp ,  protocol: "Ethena" ,  asset: "sUSDe" ,  metric:
"price" ,  value: <USD price> ,  units: "USD" ,  source: "CoinGecko" .
Primary Key: ["timestamp", "asset", "metric", "source"]  (similar to USDe). Write

•

•

disposition: append/merge new records.

•

Cadence: Backfill once, then incremental ~5 minutes interval for new data. sUSDe’s price

changes as yield accrues, but updating every few minutes is sufficient due to its relatively

smooth growth.

•

Derived Metrics: sUSDe’s price history reflects the accrued yield of the staked stablecoin. While

not used directly in a formula, the growth rate of sUSDe price over time could be used to

compute realized APY for sUSDe holders. In practice, we fetch sUSDe APY via other sources (see

DeFiLlama Yields), but this price can cross-verify that APY (the price growth rate should

correspond to the APY).

•

Notes: As with USDe, no auth is required. The sUSDe price approaching USDe’s price over time

indicates yield accrual. This data, combined with USDe price, also helps validate peg stability

(e.g., both should move roughly in tandem near $1).

•

DeFiLlama – USDe Circulating Supply by Chain – REST API for Ethena’s USDe supply and market

cap breakdown

•

Base URL & Endpoint: https://stablecoins.llama.fi  (DeFiLlama’s stablecoin API).
Endpoint:  /stablecoin/USDe?includeChains=true  to retrieve USDe’s total supply and per-

chain distribution.
Method & Params: GET  request; parameter  includeChains=true  requests a breakdown by

•

•

chain in addition to the overall supply. No auth needed (DeFiLlama’s API is open and free).
Response & Parsing: Returns JSON with  peggedSeries.usd_mcap  (historical total market
cap/supply over time) and  chainCirculating.peggedUSD  (current supply by chain). To
ingest the time series, select the list at  $.peggedSeries.usd_mcap[*]  as the data array.
Each element has a  date  (Unix timestamp in seconds) and  total  (USDe total circulation in

USD). Map  date  →  timestamp  and  total  →  value , converting the timestamp from

•

seconds to datetime.
Field Mappings: timestamp ,  protocol: "Ethena" ,  asset: "USDe" ,  metric:
"circulating_supply_usd" ,  value: <total USDe supply in USD> ,  units: "USD" ,
source: "DeFiLlama" . (If needed, the breakdown by chain can be stored in a separate

resource/table; the primary metric here is the total supply.)
Primary Key: ["timestamp", "asset", "metric", "source"]  for the total supply time-

•

series. Write disposition: append new daily records; use merge if re-fetching to update recent

days.

•

Cadence: Backfill full history once (covers all historical daily data), then incremental updates

daily (every 1 day) as DeFiLlama updates stablecoin supply figures typically once per day.

•

Derived Metrics: Tracking USDe’s supply growth helps in analyzing adoption. While no direct

formula in the registry uses supply, it provides context for TVL (since USDe supply could be

compared to Ethena’s TVL to see utilization) and for risk (a growing supply might indicate more

2

loop trades, etc.). No specific downstream metric formula, but this data is foundational for

market cap and dominance calculations.

•

Notes:  DeFiLlama’s stablecoin API aggregates on-chain data for circulating supply. Rate limits

are generous but not explicitly documented; hitting it once daily is trivial. No API key required.

•

DeFiLlama   –   Protocol   TVL   (Ethena,   Aave,   Pendle)  –  REST   API   for   total   value   locked   of   each

protocol

•

Base URL & Endpoint: https://api.llama.fi  (DeFiLlama main API). Use the  /protocol/
{name}  endpoint for each target protocol. For example:  /protocol/ethena ,  /protocol/
aave ,  /protocol/pendle . Each returns that protocol’s TVL data, including a historical TVL

•

time series.
Method & Params: HTTP  GET  with the protocol name in path. No auth or special params
needed. (The API may allow a  chain  param to filter by chain, but by default it returns

•

aggregate and breakdown by chain.)
Response & Parsing: The response JSON contains a  tvl  array of historical TVL data points.
Each element typically has  date  (Unix timestamp in seconds) and  totalLiquidityUSD  (TVL
in USD). Use  data_selector: "tvl"  (JSON path  $.tvl[*]  to get the list). For each item,

•

map  date  →  timestamp  (convert sec to datetime) and  totalLiquidityUSD  →  value .
Field Mappings: timestamp ,  protocol  (e.g., "Ethena"),  metric: "TVL" ,  value: <TVL
in USD> ,  units: "USD" ,  source: "DeFiLlama" . (If needed, include  chain  if breaking

down by chain; the aggregated total is the primary metric.)
Primary Key: ["timestamp", "protocol", "metric", "source"]  (unique TVL value per

•

day per protocol). Write disposition: append daily records (or merge if overlapping).

•

Cadence: Backfill once (historical TVL from inception of protocol), then incremental daily

updates. DeFiLlama updates protocol TVL figures daily (or more frequently for some protocols,

but daily is typical for historical series).

•

Derived Metrics: TVL is a core metric for each protocol’s size. While not directly in a formula,

combined with other data it can yield insights (e.g., utilization percent in Aave can be cross-

checked: utilization = totalBorrow / totalSupply which correlates with TVL for lending pools). For

Pendle, comparing TVL to trading volumes can indicate capital efficiency. For Ethena, TVL vs

USDe supply can show collateralization. No explicit formula, but it’s fundamental for downstream

ratio calculations.

•

Notes: DeFiLlama’s  /protocol  endpoint often includes other info (like breakdown by chain or

tokens). We focus on the TVL timeseries. These endpoints are public and free. Ensure to use the

correct protocol slug (e.g., “ethena”, “aave”, “pendle” in lowercase) as listed on DeFiLlama. Rate

limits are not strict for this usage (once per day per protocol).

•

DeFiLlama – sUSDe Yield (APY) – REST API for Ethena’s sUSDe staking yield (APY over time)

•

Base URL & Endpoint: https://yields.llama.fi . Endpoint:  /chart/
66985a81-9c51-46ca-9977-42b4fe7bc6df  which corresponds to the sUSDe yield pool on

DeFiLlama’s yield database. (This GUID identifies Ethena’s sUSDe staking yield data source in

DeFiLlama.)
Method & Params: GET  with no params needed (the pool ID in the path is fixed). No auth

•

•

needed.
Response & Parsing: Returns JSON with a  data  array (or similar) of yield points. Each element
includes a  timestamp  (Unix seconds) and  apy  (the APY at that time). Use  data_selector:

3

"data"  (JSON path  $.data[*]  – in the JSON it’s shown as  points  array). Map  timestamp

•

→  timestamp  (convert sec to datetime) and  apy  →  value .
Field Mappings: timestamp ,  protocol: "Ethena" ,  asset: "sUSDe" ,  metric:
"sUSDe_APY" ,  value: <APY percentage> ,  units: "percent" ,
source: "DeFiLlama Yields" . The APY is presumably a continuously-updating supply rate

for staked USDe.
Primary Key: ["timestamp", "asset", "metric", "source"]  (unique APY point). Write

•

disposition: append new points.

•

Cadence: Backfill available history once (this yields endpoint likely returns historical data

already). Incremental updates roughly every 30 minutes (DeFiLlama’s yield data is updated

periodically, often hourly; 30m polling ensures we catch updates).

•

Derived Metrics: Net carry spread can be derived using sUSDe’s APY against a borrow APR
from Aave. Specifically,  net_carry_spread = sUSDe_APY -
Aave_borrow_APR(stablecoin) . In our data, we’d take this sUSDe_APY and subtract the Aave

stablecoin borrow APR (from Aave data) to see if the staking yield covers the borrowing cost.

Also, fixed vs float spread uses sUSDe_APY on the floating side (see Pendle below).

•

Notes:  This   DeFiLlama   endpoint   provides   a   convenient   time-series   of   Ethena’s   yield   without
scraping  the  app.  It  is  public  and  free.  Ensure  to  record  units  as  percent  (the   apy   is  likely

already a percentage value). We might also capture a 30d average or other stats (the Ethena UI

shows a 30d avg funding or APY) – those could be computed from this time series if needed.

•

Binance   Futures   –   ETH   Funding   Rate   History  –  REST   API   for   historical   funding   rates   of   ETH
perpetual swaps on Binance

•

Base URL & Endpoint: https://fapi.binance.com  (Binance USD-M futures API). Endpoint:
/fapi/v1/fundingRate?symbol=ETHUSDT&limit=1000  to fetch funding rate records for

•

the ETHUSDT perpetual contract.
Method & Params: GET  with required query params:  symbol=ETHUSDT  (the ETH perpetual)
and  limit=1000  (max records per call). Binance returns the most recent 1000 funding entries

by default; to get older data, you’d iterate with start timestamps. No API key is required for this

•

public endpoint.
Response & Parsing: Returns an array of funding rate entries in JSON. Each entry has fields like
fundingTime  (ms timestamp),  fundingRate  (in decimal) among others. Use a list selector

(e.g.,  $.  root since the response is an array). Each element parsed: map  fundingTime  →

timestamp  (ms → datetime),  fundingRate  →  value . Convert  fundingRate  to numeric

•

(it’s a string in the JSON).
Field Mappings: timestamp ,  exchange: "Binance" ,  asset: "ETH-PERP" ,  metric:
"funding_rate_8h" ,  value: <funding rate per 8h in decimal> ,  units:
"decimal" ,  source: "Binance API" . (Funding rate is typically a decimal representing the

percentage paid/received every 8 hours; e.g., 0.0005 = 0.05%.)
Primary Key: ["timestamp", "exchange", "asset", "metric"] . Write disposition:

•

append; for backfill, multiple calls may be needed (as each call gives up to 1000 data points).

•

Cadence: Backfill by iterating backward or specifying start times until full history is retrieved

(Binance allows queries by start/end time). After backfill, incremental fetch every 8 hours just

after each new funding rate is posted. (Funding rates are determined every 8 hours for perpetual

futures.)

•

Derived Metrics: Funding rate data can be used to gauge carry trade costs. While not directly

part of the net carry or fixed-vs-float formulas above, high funding rates can correlate with

demand to short or long. We could compute average funding over a period or compare across

exchanges (e.g., Binance vs Bybit vs OKX funding for arbitrage opportunities). Funding trends

4

can also be correlated with peg deviation events (e.g., if USDe depeg risk increases, maybe

funding to short ETH changes).

•

Notes:  Binance’s   API   has   rate   limits   (e.g.,   1200   weight   per   minute,   each   fundingRate   call

weight=1). 180 calls (to get ~1000*180 ≈ 180k hours ~ 5k days ~ 15 years) might cover full
history   if   needed.   DLT   can   handle   pagination   by   time   window   (using   startTime   param

iteratively). No auth required for this endpoint.

•

Bybit – ETH Funding Rate History – REST API for historical funding of ETH perpetual on Bybit

•

Endpoint & Base URL: https://api.bybit.com  with endpoint  /v5/market/history-
fund-rate?category=linear&symbol=ETHUSDT . This returns historical funding for linear

•

•

futures (USDT-margined) on Bybit.
Method & Params: GET  with params:  category=linear  (linear futures) and
symbol=ETHUSDT  (ETH perpetual contract). No auth needed (public market data endpoint).
Response & Parsing: Returns JSON with a structure under a  result  object, likely containing a
list of funding entries ( result.list ). The integration uses JSON path  $.result.list[*]  to

select the array of funding records. Each record will have a timestamp and funding rate (and

possibly other fields like funding rate percentage). Parse similarly by mapping timestamp →

•

datetime and rate → value.
Field Mappings: timestamp ,  exchange: "Bybit" ,  asset: "ETH-PERP" ,  metric:
"funding_rate_8h" ,  value: <funding rate per 8h> ,  units: "decimal" ,
source: "Bybit API"  (Bybit’s funding is also typically given as a decimal or bps). Use the

same meaning as Binance’s: funding paid every 8h.
Primary Key: ["timestamp", "exchange", "asset", "metric"] . Write disposition:

•

append records (multiple pages if needed).

•

Cadence: Backfill in multiple calls (Bybit might require specifying start/end times or page tokens

if the result is paginated). Then poll every 8 hours after new funding is settled.

•

Derived Metrics: As with Binance, Bybit’s funding can be compared or averaged. One could

compute a funding spread between exchanges (e.g., Binance vs Bybit funding difference) as a

derived metric, or an average funding rate across major exchanges. In context, if Ethena’s

strategy involves shorting on an exchange, the funding rate (cost of short) is a critical input. We

track it to see if the strategy is profitable (e.g., sUSDe APY vs funding cost could be another

spread analysis, though Ethena likely shorts on decentralized venues or hedges differently).

•

Notes:  Bybit’s API has rate limits (e.g., 50 requests/sec). The endpoint returns a finite recent

history   if   not   given   a   time   range.   DLT   integration   might   involve   a   loop   to   get   older   data   (if
available via  startTime  or since param). If incremental, just fetch the latest page on each run.

No API key needed for public market data.

•

OKX – ETH Funding Rate History – REST API for historical funding of ETH perpetual on OKX

•

Endpoint & Base URL: https://www.okx.com  with endpoint  /api/v5/public/funding-
rate-history?instId=ETH-USDT-SWAP&limit=100 . This fetches funding history for the

•

•

ETH/USDT swap (perpetual) on OKX.
Method & Params: GET  with params:  instId=ETH-USDT-SWAP  (instrument ID for ETH
perpetual) and  limit=100  (max 100 entries per call). No auth required.
Response & Parsing: Returns JSON with a  data  array of funding entries. Use selector
$.data[*] . Each entry has fields like  fundingRate  and  fundingTime  (or similar). Map

those to timestamp and value accordingly (likely timestamp is in ms or ISO8601; convert if

needed).

5

•

•

Field Mappings: timestamp ,  exchange: "OKX" ,  asset: "ETH-PERP" ,  metric:
"funding_rate_8h" ,  value: <funding rate per 8h> ,  units: "decimal" ,
source: "OKX API" .
Primary Key: ["timestamp", "exchange", "asset", "metric"] . Write disposition:

•

append.
Cadence: Backfill by paging (OKX’s  limit=100  may allow a pagination param like  after  or
before  timestamp). Then incremental every 8 hours to get the latest rate after each funding

interval.

•

Derived Metrics: Same context as other funding sources – can compute cross-exchange

comparisons or average funding rates. High funding on one exchange vs another might signal

arbitrage. For Ethena analysis, having funding from multiple venues can show if there’s systemic

stress (e.g., all exchanges have high positive funding when ETH demand to long is high, etc.). No

explicit single-formula metric, but this data can be combined and analyzed in DuckDB.

•

Notes: OKX’s API is public. Rate limits exist (OKX public endpoints typically allow a few dozen

calls per second). Use the pagination to retrieve older data carefully (the API might need a

timestamp or a page index). Ensure timezones are normalized (OKX might return timestamps in

ms or as strings). All funding sources (Binance, Bybit, OKX) should be stored with unified units

(decimal fraction per 8h).

OpenAPI-Enabled API Sources (Can Use DLT’s OpenAPI Generator)

•

CoinGecko API (OpenAPI) – CoinGecko provides a comprehensive REST API for crypto market

data. While CoinGecko doesn’t publish an official spec, an unofficial OpenAPI 3.0 spec is

maintained on GitHub. This means we can use DLT Hub’s OpenAPI generator to ingest

•

endpoints.
Base URL: https://api.coingecko.com/api/v3 . The OpenAPI spec (e.g.,  coingecko-
public-api-v3.json ) covers all endpoints.

•

•

Endpoints & Paths: Key endpoints for our use case include
GET /coins/{id}/market_chart  (used for price history of tokens like USDe and sUSDe) and
others for current prices, etc. For example, the USDe price source above corresponds to  /
coins/ethena-usde/market_chart . These endpoints are defined in the OAS.
Parameters: Endpoints typically require  id  (coin identifier in path) and query params like
vs_currency ,  days . The OAS enumerates these, allowing automatic code generation of

client calls.

•

Data Parsing: The OpenAPI spec will define response schemas. In our integration, we focus on
the JSON paths (e.g.,  .prices  array for market_chart as described above). The OAS approach

would let us generate a Python client, but we’d still map fields similarly (timestamp and price).

•

DLT Settings: Using the OpenAPI generator, each endpoint becomes a resource. For example,
we could generate a  coingecko  source package and then select the  market_chart
endpoint for specific coins. We would specify  data_selector: prices  (if not automatically
handled) and the primary key as noted above.  write_disposition  likely merge or append

depending on how the generator structures incremental loads (we may manage it manually by
adjusting the  days  parameter or just always fetch full and merge).

•

Cadence: As above, daily or 5-min increments for price updates. If using OAS-generated client,
one could use an incremental cursor (if the API had a  from  param – CoinGecko doesn’t for

market_chart, so we fetch and trim already-known data).

•

Field mappings & Derived Metrics: Same as the CoinGecko entries above. The OpenAPI spec

doesn’t change the data content, just the integration method. Peg deviation can be derived from

USDe prices fetched via this API, as noted.

6

•

Notes: Using the OpenAPI generator for CoinGecko can speed up integration of many endpoints

(prices, market data, etc.) in a structured way. The spec is available on CoinGecko’s GitHub. Rate

limits still apply (we must throttle requests). No auth needed for public endpoints.

•

Beaconcha.in API (Ethereum Staking)  – Beaconcha.in (Ethereum 2.0 Beacon Chain explorer)

offers a rich REST API for consensus-layer data (e.g., validator stats, staking APR) and provides

an OpenAPI spec on their docs site. We leverage this for Ethereum staking metrics.

•

Base URL: https://beaconcha.in/api/v1 . The OpenAPI JSON can be downloaded from

their API docs (Swagger UI).

•

Endpoints & Paths: We focus on the staking APR endpoint. Beaconcha.in’s API has an endpoint

for current network APR (and possibly historical values by epoch). For example, an endpoint
might be  /ethstore/metrics  or  /metrics  that includes  apr . (The exact path for APR is

found in their docs/spec; the registry suggests using the docs to find the current APR endpoint.)
Using the OAS, we identify the correct path (likely something like  /ethstaking/apr  or a field

in metrics).

•

Parameters: Likely none for the current APR (it just returns the latest APR). If historical, maybe

•

an epoch or date parameter. The OpenAPI spec will clarify this.
Data Parsing: The JSON response for APR might have a structure with an  apr  field (possibly
nested). The registry uses JSON path  $..apr  to extract it. In integration, we’d capture that

single value. If the endpoint provides a timestamp or if we add one, we’ll timestamp the record

at fetch time (since it’s the current APR).

•

DLT Settings: The OpenAPI generator can create a client for all Beaconcha.in endpoints. We’d
select the APR endpoint as a resource.  data_selector  might not be a list here (it’s a single
object/value), but we can still wrap the result. The  primary_key  could be  timestamp  (date
of observation) plus  metric  and  source .  write_disposition  likely append (or merge if

updating the same day’s value).

•

Cadence: Fetch daily (or per epoch if needed). The registry suggests incremental daily updates

for APR. Historical backfill once (if an endpoint for historical APR by day or epoch exists, we’d

•

retrieve it; otherwise, just start collecting daily).
Field Mappings: timestamp  (when the APR was recorded),  metric: "staking_APR" (or
eth_network_apr) ,  value: <annual % yield on staking> ,  units: "percent" ,
protocol: "Ethereum" ,  source: "Beaconcha.in" . This provides context for the yield

environment.

•

Derived Metrics: Ethereum’s staking APR is an input to understanding Ethena’s yield. For

instance, Ethena’s sUSDe likely sources yield from staked ETH; comparing sUSDe APY to the

Ethereum base staking APR shows efficiency or overhead. No direct arithmetic combination in

our defined formulas, but it’s a contextual baseline.

•

Notes: Beaconcha.in’s API may require an API token for heavy use, but for light use (daily calls)

it’s   typically   fine.   The   OpenAPI   spec   enables   quick   generation   of   the   client   code   for   all   their

endpoints (e.g., validator counts, balances, etc., beyond just APR). We focus on APR here.

•

Pendle V2 API – Pendle Finance provides a REST API (v2) for its yield markets, with an available

OpenAPI   documentation.   The   Pendle   API   delivers   real-time   data   on   Pendle’s   Principal/Yield

Tokens and markets (prices, yields, liquidity, etc.). We can integrate it either via the OpenAPI

generator (if we obtain the JSON spec from their docs site) or via manual definitions if needed.

•

Base URL: https://api-v2.pendle.finance/core . The API has multiple versions (v1, v2)
and supports multiple chains via path parameters (e.g.,  /v2/{chainId}/... ). The docs

7

indicate endpoints like  /v1/sdk/{chainId}/markets  and others. The Pendle docs site allows

•

downloading an OpenAPI spec JSON (the “Download OpenAPI Document” link).
Endpoints & Paths: Important endpoints for analytics include: Markets data – e.g.  GET /v2/
markets  (or  /v1/{chainId}/markets ) to list all markets and their current data (including PT

price, implied yield, LP APR, etc.), Historical data – e.g. an endpoint to retrieve time-series data

for a specific market’s yields or prices (the docs mention “Retrieve historical data for a market in
time-series format”). Also endpoints for specific analytics like  /{chainId}/markets/
{marketId}/...  to get details or APRs. For instance, the Pendle API can return current

principal token prices and implied yields directly, saving us from manual calculation. We will

•

likely use the markets list endpoint and possibly a historical chart endpoint.
Parameters: Most endpoints require a  chainId  path segment (Pendle is multi-chain, but we
focus on Ethereum mainnet, chainId=1). Some endpoints require a  market  identifier or
address. For example, to get APR of Pendle LPs, one might use  GET /v1/1/markets  which

returns a list including APR info for each market (as hinted by a Stake DAO doc snippet).

Historical endpoints might require a market ID and a time range. The OpenAPI spec will detail

these.

•

Data Parsing: The Pendle API returns JSON with structured fields like token addresses, prices,
APRs, etc. For example, a market object may contain  ptPrice ,  ytPrice ,  impliedYield  or

similar. If not directly given, we compute implied fixed APY from PT price and time to maturity (as

shown in the subgraph source). But likely the API provides it or enough info to calculate easily.

When integrating via the OpenAPI generator, each endpoint’s response schema is known. We’ll
choose appropriate  data_selector  if the data is nested (e.g., perhaps  data  or  markets

list in the JSON). For a list of markets, the selector could be the list itself.

•

DLT Settings: Using the OpenAPI spec, we can generate the Pendle source. We might break it
into resources like  markets_current  and  market_history . For  markets_current :
endpoint: {"path": "/v2/1/markets"}  returning an array of market objects; use
data_selector  pointing to that array,  primary_key : a combination like market ID or
underlying asset plus maturity.  write_disposition :  "merge"  if we want to update market
data each run (since current data for each market overwrites previous), or  "append"  if we

store a time series of snapshots. For historical endpoints, we would append time-series points.

•

Cadence: Current market data can be pulled frequently (e.g., every 5–10 minutes) to monitor

real-time implied yields and prices. Historical data endpoints might allow backfilling the past (if

not, we rely on subgraph for history). If available, do a one-time backfill of history for each

market, then incremental updates every ~30 minutes (Pendle yields don’t change too rapidly;

•

30m is consistent with subgraph updates).
Field Mappings: For Pendle’s data, key fields include  protocol: "Pendle" ,  chain:
"Ethereum" ,  asset  (could use the underlying asset or a composite like “PT-{symbol}” to
identify the PT token),  maturity  (maturity date or epoch of the PT),  metric  (e.g.,
"PT_price" ,  "PT_implied_APY" ,  "YT_yield" , etc.),  value ,  units . The Pendle
subgraph example computes  PT_implied_APY  as a percent, and we would similarly capture

that either directly from API or compute it. We also capture raw prices (PT price in underlying

units). If the API provides LP APR (for Pendle LP yield farming), that could be another metric.

•

Derived Metrics: Pendle’s data enables calculating fixed vs floating yield spread. We derive
fixed_vs_float_spread = Pendle_PT_implied_APY - sUSDe_APY . Here, Pendle’s PT

implied APY (fixed yield for the term) minus Ethena’s sUSDe APY (floating yield from staking)

shows the spread between locking in yield vs taking floating yield. This is a core comparison in

Ethena’s context (one side of the trade is fixed yield via Pendle, the other is floating via staking).

Our data (Pendle PT APY and Ethena APY) makes this computation straightforward in DuckDB.

Additionally, Pendle’s data could allow computing things like yield index growth or market

utilization, but the key one is the fixed vs float spread.

8

•

Notes: The Pendle API is a rich source but relatively new (docs “in progress” as of writing). It’s

likely a Hosted SDK that returns data used by Pendle’s frontend. The OpenAPI spec can be

obtained from the docs site, making integration easier. We must mind rate limits (not explicitly

documented; assume reasonable call frequency). No authentication is mentioned for reading

data. If certain endpoints are heavy (e.g., historical queries), we may rely on subgraph for those

to reduce load on their API.

GraphQL Sources (Subgraphs via The Graph)

•

Aave v3 Mainnet Subgraph – The Graph subgraph indexing Aave v3 on Ethereum mainnet; provides

real-time lending protocol data via GraphQL

•

GraphQL Endpoint: Aave’s official subgraph can be queried via The Graph. (The exact URL can

be obtained from The Graph Explorer – at time of integration, find “Aave V3 Mainnet”
deployment. It will be something like  https://api.thegraph.com/subgraphs/name/aave/
protocol-v3  or a decentralized network endpoint with a specific ID.) We store the subgraph

ID/URL and refresh if it’s redeployed.

•

Query & Entities: We query the Reserves data to get interest rates and utilization. For example,

a query template:

{

reserves {

symbol

liquidityRate

variableBorrowRate

totalATokenSupply

totalCurrentVariableDebt

}

}

This returns each asset’s current supply and borrow rates (in Ray units) and aggregates. We

focus on stablecoins (like USDC, DAI) for Ethena’s context, but we can fetch all and filter in code.

•

Parsing & Transformation: The subgraph returns JSON data. We apply transformations: convert
Ray fixed-point rates to decimals by dividing by 1e27 (Aave’s  liquidityRate  and
variableBorrowRate  are scaled by 1e27). Map  liquidityRate/1e27 → supplyAPR  and
variableBorrowRate/1e27 → borrowAPR . Also rename  totalATokenSupply →
totalSupply  and  totalCurrentVariableDebt → totalBorrow  for clarity. Then compute
utilization = totalBorrow / totalSupply. Finally, we emit multiple metrics per asset:  supplyAPR ,
borrowAPR , and  utilization_pct  with their respective units (APR as decimal fraction,

•

•

utilization as ratio).
Field Mappings: Each emitted record will have  timestamp  (we add the query time or block
timestamp if available — The Graph can return a block number/time for queries),  protocol:
"Aave" ,  chain: "Ethereum" ,  asset  (e.g., "USDC", "ETH" depending on reserve symbol),
metric  (one of  "supplyAPR" ,  "borrowAPR" ,  "utilization_pct" ),  value  (e.g., 0.03
for 3% APR),  units  ( "decimal"  for APRs,  "ratio"  for utilization).
Primary Key: A combination like  ["timestamp", "protocol", "chain", "asset",
"metric"]  ensures uniqueness. (Since multiple metrics per timestamp and asset are emitted.)

Write disposition: for time-series of rates, we append snapshots. If The Graph doesn’t support

historical queries directly, we might always fetch current and treat it as a snapshot in time.

Alternatively, if the subgraph has entities for historical rates or if we query at specific block

9

heights, we can reconstruct history. The registry suggests querying historical snapshots if

available; if not, we accumulate our own by polling.

•

Cadence: If treating as near-real-time feed, poll every ~5 minutes for new values. (Aave’s rates

update continuously with blocks, but small interval polling is sufficient to capture changes, and

5m aligns with Ethena’s needs for carry trade monitoring.) For history: we could attempt a

backfill by scanning past blocks (The Graph might allow querying by block number for past rates,

or there may be a “ReserveUpdate” entity to query historical rate changes – not specified here). If

not feasible, at minimum start recording going forward.

•

Derived Metrics: The subgraph output directly gives utilization_pct for each reserve, a key

health metric (also listed as a derived metric in our registry). Additionally, from this data we get

Aave borrow APR for stablecoins (e.g., USDC’s borrowAPR). That is used to compute the net
carry spread with Ethena’s sUSDe APY:  net_carry_spread = sUSDe_APY -
Aave_borrow_APR . For example, if Aave USDC borrow APR is 5% (0.05) and sUSDe APY is 6%,

the net carry is +1%. We also have Aave supply APRs, which could be compared to Pendle yields

or used to check if Ethena’s yield (sUSDe) aligns with base lending yields.

•

Notes:  GraphQL   integration   in   DLT   involves   using   the   graphqldata   format.   We   store   or

periodically update the subgraph deployment ID (since The Graph’s decentralized network uses

IDs). No auth needed. This source ensures high fidelity data from on-chain events (subgraph is

fed by Aave contracts). It’s preferred over scraping Aave’s UI or using less official APIs. If needed,

we could extend to Aave v2 or other networks by adding additional subgraph sources.

•

Pendle Mainnet Subgraph – The Graph subgraph for Pendle v2 on Ethereum; provides data on yield

markets (PTs and YTs) via GraphQL

•

GraphQL Endpoint: Like Aave, Pendle has subgraphs. We identify the Pendle v2 mainnet

subgraph (from Pendle docs or The Graph Explorer). The endpoint would be a GraphQL URL

(either hosted by Pendle or via The Graph). The registry entry indicates using The Graph and

possibly community subgraphs

1

. Assume we have the endpoint URL or ID for mainnet.

•

Query & Entities: A sample query:

{

markets {

id

maturity

underlying { symbol }

pt { price }

// possibly yieldToken (YT) info, e.g., implied yield accrued

}

}

This returns all markets with their PT price, maturity timestamp, and underlying asset. The

subgraph likely also includes data like the redeem value or YT rate accrued, but if not, we

calculate implied yield. The registry note says: “Compute PT implied fixed APY = (redeemValue/

ptPrice - 1) / time_to_maturity”. If each PT represents 1 unit of underlying at maturity, then

redeemValue = 1 (in underlying terms), and we can compute APY from the discount (ptPrice) and

time remaining. We might enhance the query to get current block time or maturity in a date

form.

•

Parsing & Transformation: From the query result, for each market we compute
implied_fixed_apy . The registry uses formula  (1/pt_price - 1) /

10

(days_to_maturity/365) . We’d calculate
days_to_maturity = (maturity_timestamp - now_timestamp)/86400 . The transform
steps: take  pt.price , compute APY as above, and set the metric name to
"PT_implied_APY"  with percent units. (If the subgraph directly gave an implied yield or if

Pendle PT has a known yield measure, we could use that, but calculation is fine.) We could also

•

emit the PT price itself (as context, though the APY is more directly useful).
Field Mappings: For each market’s output:  timestamp  (we’ll timestamp with query time or
block time),  protocol: "Pendle" ,  asset  (could use the underlying symbol or a composite
like  {underlyingSymbol}-PT  to identify the market),  maturity  (timestamp or date of
maturity),  metric: "PT_implied_APY" ,  value: <computed annual yield in %> ,
units: "percent" ,  source: "Pendle Subgraph" . We might also capture floating yield

(YT) metrics if available, but the subgraph data we have focuses on fixed side.
Primary Key: ["timestamp", "protocol", "asset", "maturity", "metric"]  to

•

uniquely identify each data point per market. Write disposition: append new snapshots. (If

subgraph had historical entities like “daily market snapshots”, we could backfill from those;

otherwise, we treat each query as a snapshot in time.)

•

Cadence: Backfill if possible: some subgraphs have entities for historical values (check if Pendle

subgraph has something like daily yields or if one can query at past blocks). If not, we rely on

Pendle’s API or our own gradual history build-up. Incremental: poll every 30 minutes for
updated market data. Pendle’s yields move with market activity, and 30m frequency aligns with

capturing changes without overload.

•

Derived Metrics: The fixed vs floating spread as mentioned earlier:
Pendle_PT_implied_APY - sUSDe_APY  can be calculated once we have PT implied APY

(from this subgraph) and Ethena’s sUSDe APY. This tells us if the fixed yield from Pendle is higher

or lower than the current staking yield – a crucial metric for strategy (if fixed > float, one might

lock in yield, etc.). Additionally, if we had YT yields (floating yield token yields), we could compare

those to underlying (but sUSDe APY essentially is a floating yield from staking). Our dataset

covers the needed pieces for that spread.

•

Notes: Ensure the subgraph’s data is up-to-date; sometimes subgraphs lag a few minutes

behind on-chain. The Pendle subgraph likely captures new markets, PT prices (which come from

AMM trades), etc. Using GraphQL means we can join related data (like underlying symbols, which

we did). If Pendle expands to other chains, we’d replicate sources for those chainIDs (the registry

hints at multi-chain Pendle considerations). No authentication is needed for The Graph’s public

endpoints, but be mindful of query cost (complex queries might hit API limits, though our

queries are simple).

Other Sources (HTML Scraping)

•

Ethena App – Market Data (sUSDe APY & Funding) – HTML source (web UI) for Ethena’s own

dashboard metrics. While most metrics are fetched via APIs above, some derived stats (like 30-

day average funding or instantaneous combined metrics) are displayed on Ethena’s app and not

directly via an API. We have a source to scrape this as a fallback.
URL: https://app.ethena.fi/market-data  (Ethena’s official app page for market data).

•

•

Data & Parsing: The page may contain embedded JSON or just text values showing metrics like

sUSDe APY, 30d avg funding rate, TVL, etc.. The scraper looks for specific text patterns: e.g.,

find text “APY” near “sUSDe” for the sUSDe APY, “Funding ... avg” for the average funding, and

“TVL” for total value locked on Ethena. These give point-in-time metrics (not time series). We

•

parse the HTML to extract those values.
Field Mappings: Each scrape yields a record per metric with fields:  timestamp  (time of
scrape),  metric  (e.g.,  "sUSDe_APY"  or  "funding_avg_30d" ),  value  (e.g., 0.06 meaning

11

6%),  units  (percent for APY/funding, USD for TVL), and perhaps a  notes  field if needed for

context. Protocol is implicitly Ethena, and source is the Ethena app.
Primary Key: ["timestamp", "metric", "source"]  for these app-derived stats (since

•

asset/protocol is implied by metric name here).

•

Cadence: No historical backfill (not applicable, as this requires the app). Incremental: scrape

every 10 minutes for the latest values. This ensures we capture any changes on the dashboard

frequently.

•

Use & Derived Metrics: The 30-day average funding rate (if that’s what “Funding avg” refers

to) is a unique aggregated metric. It might represent the average cost to maintain Ethena’s

hedge (short position) over 30 days. This is not directly provided by our other sources, but we

could compute something similar from the funding rate time series we collected. However,

having it directly from Ethena ensures accuracy. We can use this in analysis of net carry over

longer periods. The sUSDe APY from the app should roughly match the DeFiLlama yield (if

Ethena’s team calculates it similarly); it’s a good validation. TVL on this page likely mirrors

Ethena’s TVL (which we have from DeFiLlama). So this source primarily provides that average

funding metric and a real-time cross-check on APY/TVL.

•

Notes: This is an HTML scrape and should be used sparingly (the registry notes to prefer official

APIs when possible). We included it to cover any gaps (like the funding average). Throttling and

respectful scraping (honoring robots.txt) is important. If Ethena exposes an API or JSON for

these, that would be preferable. Until then, this fills the gap for those composite metrics.

Each of the above sources is defined to be compatible with  DLT Hub ingestion workflows. The REST
and GraphQL sources can be set up via  dlt.sources.rest_api_source  or GraphQL clients, and the
OpenAPI-listed   ones   can   be   onboarded   quickly   with   dlt-init-openapi   using   the   provided   spec

URLs. All sources output data in a  normalized schema  (with common fields like timestamp, protocol,

asset, metric, value, units, etc.), aligning with the project’s global schema. Primary keys are chosen to

support idempotent merges and incremental loading without duplication.

Rate limits & Auth: Most sources are public and do not require auth keys. We have noted where to be

mindful of rate limits (CoinGecko, DeFiLlama, exchange APIs). For high-frequency sources, implement

backoff  and  consider  caching.  If  any  source  provided  an  official  API  key  option  (none  of  the  above

strictly need it), we could supply it via DLT’s secrets for higher limits.

Incremental loading support: For some APIs (Binance, etc.), we use time parameters to page through

history. DLT can maintain cursors (e.g., last timestamp fetched) to only request new data on each run.
The  cadence  settings above guide how often to schedule each pipeline (e.g., funding rates every 8h,

prices 5m, etc.). Many sources naturally align with their data frequency (8h funding, daily TVL, etc.),

simplifying scheduling.

Downstream Derived Metrics in DuckDB:  With all primary data ingested, we can calculate complex

metrics in DuckDB SQL. As highlighted: -  Peg Deviation:  Query USDe price time-series and compute
ABS(price - 1.0)  as  peg_deviation . - Net Carry Spread: Join sUSDe APY and Aave stablecoin
borrow   APR   (by   timestamp,   perhaps   taking   closest   values   in   time)   to   compute   sUSDe_APY   -
borrowAPR .   -  Fixed   vs   Floating   Spread:  Join   Pendle   PT   implied   APY   with   sUSDe   APY   to   compute
PT_implied_APY   -   sUSDe_APY .   -  Utilization   Percent:  Already   computed   in   Aave   subgraph
ingestion as   utilization_pct   per asset, but one could also recompute from raw totals if needed.

This shows how much of the supplied liquidity is borrowed (risk indicator for Aave markets).

12

All source definitions above are structured to feed into a cohesive analytics warehouse. They reflect the
registry entries in  crypto_sources.json  and adhere to the DLT integration architecture guidelines

(e.g., using official APIs over scraping when available, honoring data source T&Cs, and normalizing units

like APR to decimals and timestamps to UTC). This ensures the data can be seamlessly ingested, stored
(with appropriate   write_disposition   such as merge for upserts or append for time-series), and

then leveraged in analysis and dashboards.

1

Ingesting Ethereum & DeFi Data Using DLT Hub.pdf

file://file_00000000b99871f4abbb72b750c7516c

13

