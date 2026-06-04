Scrapable Sources for Ethena/Aave/Pendle Yield

Strategy

Technical APIs and Documentation

•

Aave Developer Hub & APIs:  Aave’s official docs provide a GraphQL API for querying lending

.   For   example,   the   Aave   V3   GraphQL   endpoint
markets,   reserve   APYs,   utilization,   etc
( api.v3.aave.com/graphql ) returns real-time market data (supply/borrow rates, TVL, etc.)

1

and even historical APY trends via SDK hooks

2

3

. Aave also maintains an OpenAPI with REST

. Additionally, on-chain
endpoints (e.g. TVL, volume, rate history) for programmatic access
data   providers   (like   the   UiPoolDataProvider   contract)   can   be   called   via   JSON-RPC   for

4

aggregated pool stats

5

.

•

Ethena Documentation & Public API:  Ethena’s docs (docs.ethena.fi) detail its synthetic dollar
(USDe)   design   and   include   a  public   API  for   minting/redemption   quotes
.   The   API   (at
public.api.ethena.fi ) offers JSON endpoints to stream indicative USDe quotes or RFQs,

6

enabling algorithmic mint/redeem strategies
. (Note: usage is gated to whitelisted users).
Ethena  also  provides  real-time  dashboards  –  e.g.   an   on-chain   positions   dashboard   showing

7

8

collateral across exchanges

9

10

. For data indexing, Ethena has integration with Goldsky to

spin up GraphQL subgraphs or data streams for on-chain metrics

11

12

.

•

Pendle Docs, API & Subgraphs: Pendle’s developer docs outline their yield tokenization protocol

and integration guides

13

. While a Pendle V2 API was announced (REST endpoints for Pendle’s

backend)

14

, much of Pendle’s data is accessible via subgraphs. The official Pendle V2 subgraph

on TheGraph indexes yield market info (OT and YT tokens, APYs) on Ethereum mainnet

15

16

.

Community/partner indexing services like Ormi have also provided real-time subgraph APIs for

Pendle, scaling to high query throughput

17

. These sources allow scraping current yields, pool

TVLs, and users’ yield positions.

•

Plasma  (XPL)  Network  Resources:  Plasma  is  a  stablecoin-optimized  L1  now  integrated  with

Ethena/Pendle   yields
( https://rpc.plasma.to ) for on-chain queries

18

.   The  Plasma   docs  (docs.plasma.to)   list   a   public  RPC   endpoint

19

20

. Because Plasma is EVM-compatible,

developers   can   scrape   chain   data   (transactions,   contract   states)   similar   to   Ethereum.

Plasmascan, the block explorer, offers an Etherscan-like API (called  Routescan API) for account

balances, token transfers, etc., with a free tier (up to 2 req/s)

21

. This makes it possible to pull

data like stablecoin transfers or pool states on Plasma via JSON API calls. (Plasma’s explorer API

endpoints mirror Etherscan’s structure, facilitating easy integration.)

•

Curve   Finance   API   &   Subgraph:  Curve’s   technical   docs   provide   an   official  REST   API  (e.g.
api.curve.fi ) exposing pool data: it returns pool list, liquidity, volume, and APYs (including

combined   base+LST   staking   APY   for   pools   with   liquid   staking   tokens)

22

23

.   The   API   is

documented   via   an   OpenAPI   spec

24

,   and   it’s   updated   for   new   features   like   crvUSD.   For

historical  and  on-chain  data,  Curve  has  community-maintained  subgraphs  on  The  Graph  for

each network (Ethereum, Arbitrum, etc.) tracking pool states. These are scrapable via GraphQL

for time-series of pool yields, volumes, and gauge info

25

26

.

1

•

Balancer   GraphQL   API   &   Subgraphs:  Balancer   offers   a   unified  GraphQL   API  at   api-
v3.balancer.fi

.   This   endpoint   provides   structured   queries   for   Balancer   pools

27

(composition, TVL, swap fees) and their APRs, as well as gauges (liquidity mining rewards)

28

.

For example, one can query all pools’ current APR (trading fees + incentives) or fetch a user’s

pool balances via the API. Balancer’s docs also link to subgraphs – the Balancer V2/V3 subgraphs

index all pool events and are accessible on TheGraph or via Balancer’s hosted GraphQL. These

allow scraping historical pool metrics and tracking new pools in real time

29

30

.

•

Stargate Protocol Docs & API: Stargate (by LayerZero) is a cross-chain liquidity protocol whose

developer docs  describe a RESTful  unified transfer API

31

. This API lets developers initiate

cross-chain token transfers via simple HTTP calls (abstracting the complex messaging under the

hood).   In   practice,   one   could   programmatically   fetch   quotes   for   bridging   (e.g.   USDT   from

Ethereum   to   Avalanche)   and   then   execute   transfers   using   Stargate’s   API   endpoints

32

33

.

Stargate’s documentation emphasizes  comprehensive developer support, including example

guides   and   a   focus   on  native   asset   swaps  (no   wrapped   tokens)

34

35

.   For   monitoring,

Messari subgraphs  exist for Stargate (e.g. Avalanche) to query liquidity and volume stats

36

,

useful for scraping cross-chain TVL and bridge fee data.

•

deBridge   Developer   Portal   (deAPI):  deBridge   is   a   cross-chain   interoperability   protocol   that
. The deBridge Liquidity
offers REST/gRPC APIs and even GraphQL subgraphs for its services

37

Network   (DLN)   exposes   a  “Powerful   API”  for   cross-chain   swaps   with   RFQ-based   pricing

38

.

Developers can, for instance, call deBridge’s API to get a quote and execute a single-transaction

swap   from   an   asset   on   Chain   A   to   Chain   B   without   maintaining   bridge   liquidity.   The   docs

highlight   that   integrators   have   access   to   TypeScript   SDKs,  REST   endpoints,   and  GraphQL

subgraphs for tracking transactions and orders

39

. Thus, one can scrape data like cross-chain

swap rates, execution status, or even subscribe to events via these APIs. (deBridge’s supported

chains & fees  page also provides up-to-date JSON lists of networks and asset fees, useful for

dynamic scraping

40

41

.)

•

Binance Earn Interfaces (Simple Earn API):  Binance Earn (the CeFi yield platform) publishes

yields for various products (flexible savings, locked staking, etc.) on its website. Recently, Binance

enabled   official   API   endpoints  for  Simple   Earn  and   ETH   staking   data

42

.   These   REST

endpoints (documented on Binance’s GitHub) allow programmatic queries of current APRs for

each   Earn   product,   subscription   quotas,   and   even   to   perform   actions   like   subscribing/

redemptions via API

43

. For instance, one can fetch the live interest rate range for USDT flexible

savings (4.2%~7.17% APY) instead of scraping HTML

44

. This structured access to Binance Earn

makes it feasible to include CeFi yield rates in a strategy dashboard. (Note: Access requires Binance

API credentials.)

•

DeFiLlama   Data   API:  DeFiLlama   offers   a   wide   range   of  free   JSON   APIs  aggregating   DeFi

metrics. Developers can query  protocol TVLs, pool yields, token prices, fees,  and more via

simple GET endpoints

45

46

. For example, DeFiLlama’s “yields” API lists yield farms across DeFi

with   APYs   and   TVLs,   and   its  “earnings”   API  provides   historical   yield   rates.   The   API   is   well-

documented and includes historical data endpoints, which is invaluable for back-testing (e.g.

pulling Aave’s TVL or Pendle’s APY over time)

47

. DeFiLlama’s aggregated data (spanning many

protocols) comes in a uniform format, simplifying scraping. (They also have a Pro tier with higher

rate limits and more endpoints, if needed

48

.)

2

On-Chain Subgraphs & Dashboards

•

The Graph Subgraphs: Many protocols in this strategy expose on-chain data via GraphQL

subgraphs:
Aave: Official subgraphs (for V2 and V3 on each network) index all lending pool events. These can

•

be queried for reserve histories, utilization rates, and incentive emissions. For instance, the Aave

v3 Ethereum subgraph provides reserve APY histories and current liquidity indexes per asset.

•

Pendle: The Pendle team deployed subgraphs for yield markets (e.g. on Ethereum mainnet and

Arbitrum). By querying these, one can scrape live and historical yields on pendle’s Yield Tokens

(YTs) and track the notional value of Principal Tokens (PTs) over time

15

49

. This is crucial for

monitoring how Pendle’s markets evolve (e.g. the APY for a USDe yield market).

•

Gearbox & Morpho: These lending aggregators have community subgraphs too. Morpho’s

subgraph can be used to get effective APYs delivered to users (Morpho optimizes Aave/

Compound rates), and Gearbox’s subgraph indexes its credit account usage and pool APYs.

Including these similar platforms ensures comprehensive coverage of leveraged yield sources.

•

Frax & Silo: Frax’s on-chain lending and FraxLend pools have subgraphs providing utilization and

interest rates. Silo Finance (isolated lending markets) exposes a Graph subgraph for each Silo’s

reserves and rates

50

. These can be scraped to compare yields in Ethena/Pendle strategy vs

other stablecoin yield platforms.

•

Liquid Collective: As a liquid staking derivative (LSD) platform, Liquid Collective likely provides an

API or subgraph for staked ETH yield rates. For example, one might retrieve the current staking

APR   for   Liquid   Staked   ETH   to   compare   against   Ethena’s   synthetic   dollar   yield.  (If   no   official

subgraph, LSD rates can be pulled from DeFiLlama’s “LSD yields” aggregator API.)

•

DeFi Dashboards & Aggregators:

•

Dune Analytics: Dune’s community dashboards often track metrics for these protocols (e.g.

Ethena’s supply growth or Pendle trading volume). While Dune doesn’t have a public API without

running queries, one can export data from existing queries or use the Dune API (with an API key)

to fetch updated metrics. For example, Chaos Labs and others have published Dune boards

visualizing Aave’s risk metrics or Pendle’s volume. These dashboards are useful references and

sometimes offer CSV downloads for scraping.

•

Token Terminal: TokenTerminal aggregates protocol financials (revenue, fees, TVL) via its API. It

tracks Aave’s TVL and revenue

51

, and likely Pendle’s fee revenue, etc. A developer can use

TokenTerminal’s API to pull time-series data on, say, Aave’s fee revenue or Pendle’s trading fees,

to gauge sustainability of yields.

•

Chaos Labs Risk Dashboards: For risk monitoring, Chaos Labs (and Gauntlet) have public

dashboards for Aave and others. These often list current asset utilization, borrow caps, and

value-at-risk. While primarily visual, some data (like recommended risk parameter changes or

live health of Aave markets) might be accessible via their APIs or via scraping the JSON behind

the charts.

•

DeFiLlama Yields & Rankings: Aside from APIs, DefiLlama’s website provides a “Yield” section

aggregating top pools by APY across DeFi

52

. One can scrape this periodically to see where

Ethena/Aave/Pendle stand among all yield opportunities. DeFiLlama also shows historical

charts for TVL and APY which can be downloaded.

•

Other Aggregators: Platforms like Messari Governor (for governance updates) and Boardroom

can be scraped for governance proposals affecting these protocols. For example, Aave’s

governance forum or Pendle’s snapshot votes might signal upcoming changes in yields or caps.

Likewise, Llama.science and EigenLayer dashboards might provide data on staking yields

3

relevant to Ethena’s underlying strategy (if Ethena uses ETH staking rewards, tracking Beacon

chain APY is useful).

Social & Community Sources

•

Blogs & Research Platforms: A wealth of qualitative insight comes from DeFi-focused

publications:

•

Bankless: The Bankless newsletter frequently analyzes Ethena, Pendle, and similar strategies. For

example, Bankless noted that Ethena’s synthetic dollars came to dominate crypto credit

markets in 2024 due to attractive yield economics

53

. Articles like “The Year Ethena Took Over”

or “DeFi Rides the Ethena Wave” provide context on how leveraged yield loops with Pendle boosted

Ethena’s growth. These long-form posts (usually on Substack) can be scraped via RSS or the

webpage to extract insights on risk and market sentiment.

•

Messari Research: Messari’s analyst reports and intel feed cover protocol metrics and milestones.

There are Messari posts on, e.g., Ethena’s $12B supply surge fueled by leveraged yield loops

on Pendle/Aave

54

, or on new point-farming strategies (like Ethena’s shard campaign and

Pendle’s role

55

). Messari’s API (if you have API access) can pull profiles for these assets (e.g.

profile info for PENDLE token

56

). Even without an API key, Messari’s free news feed is scrapable

for headlines and summaries of major events.

•

Medium and Mirror: Official project blogs often live on Medium. Pendle’s Medium publishes

updates (e.g. “Pendle 2025: Zenith” reflecting on its TVL growth

57

), and Ethena Labs has

posted deep-dives (some teams use Mirror.xyz for more technical essays). These blogs yield

insights into protocol upgrades or new yield products. They can be scraped via Medium’s RSS or
by crawling the Medium publication pages (e.g.  pendle.medium.com ). Similarly, independent

analysts on Mirror often write strategy breakdowns – for instance, a Mirror article might dissect

Ethena’s basis-yield mechanism or Pendle’s fixed-rate markets.

•

Delphi Digital: As a research firm, Delphi often releases reports on novel DeFi mechanisms. If

Delphi (or Bankless Premium, etc.) have reports on Ethena or yield maximization, those may not

be fully public, but summaries or excerpts often get shared on Twitter or newsletters. Delphi’s

public blog or podcast transcripts could be sources of qualitative insights (scraping would

involve parsing their site or Substack).

•

The Defiant: Camila Russo’s The Defiant is another blog covering daily DeFi news. They have

reported on Ethena’s growth and any controversies (e.g. depeg incidents or point farming

mania). The Defiant articles can be scraped from their website; for example, they recently noted

Ethena’s on-chain stablecoin crossing multiple billions and the yield strategies around it

58

.

•

Miscellaneous   Analysis:  Other   sources   include  Mirror   posts   by   independent   analysts,

community newsletters (e.g.  Ignas’ DeFi Alpha  on Substack), and protocol-specific newsletters

(some teams have weekly updates on Medium). These provide commentary on risks (like peg

stability, governance changes) which pure data might miss.

•

Reddit Communities: Several subreddits serve as forums for discussion and real-time feedback:

•

r/ethfinance – A general Ethereum finance subreddit where Ethena’s strategy and Pendle yields

are often discussed in daily threads. Users share concerns (for example, discussions on “Is Ethena

legit?” where the consensus was that its ~20% yield is “legitimate (coming from perp funding

rates and native ETH yield)”

59

). Such threads are a goldmine for sentiment and crowd-

sourced risk analysis; they can be scraped via Reddit’s API (e.g. searching mentions of “Ethena”

or “Pendle”).

•

r/DeFi – A broader DeFi subreddit for news and questions. One can find posts about yield

farming strategies, including Ethena’s loops or Pendle’s APYs. Community Q&A (e.g. “Ethena Rate

4

of Return explanation” posts) often break down complex strategies in plain language
Reddit’s JSON endpoints (e.g.  .json  on post URLs) allows extraction of these discussions.

60

. Using

•

r/Ethena (or r/Ethena_protocol): A dedicated subreddit for Ethena Labs. This is a hub for

protocol announcements, community guides, and issue discussions. It can be scraped to track

community concerns (e.g. threads on USDe peg fluctuations or ENA tokenomics changes). For

instance, a community post might analyze an insurance fund parameter change or share yield

optimization tips.

•

r/pendlefi: Pendle’s community subreddit, where users discuss new yield markets, PENDLE

token news, and strategies (like how to leverage Pendle YT for Ethena points). Monitoring this

can provide early warnings of any UI or contract issues and gauge user adoption of new

integrations (such as Pendle on Plasma).

•

r/aavegotchi: While Aavegotchi is a game, it’s rooted in Aave’s yields (using Aave interest to

power NFTs). The mention of Aavegotchi suggests watching how gamified yield is perceived. In

practice, r/Aavegotchi discussions might not directly impact Ethena/Pendle, but they reflect retail

yield sentiment and creative uses of yield (which could inspire Ethena reward gamification). This

sub’s content is scrapable via Reddit API if needed.

•

(Also worth noting: Aave’s own subreddit r/aave is community-run now

61

, and broader subs like

r/CryptoCurrency   sometimes   have   high-level   discussions   on   Ethena’s   legitimacy   or   yield

sustainability

62

).

•

Discord Servers: Real-time community sentiment and support queries appear on Discord. Each

protocol’s official Discord can be joined via public invite:

•

Ethena Discord – used by Ethena Labs for announcements and user support. Monitoring

channels here (e.g. #general or #support) can alert to any peg instability or user confusion in
real time. (Public invite likely found on ethena.fi – e.g.  discord.gg/ethena ).

•

Pendle Discord – Pendle’s community Discord (invite: see link on pendle.finance or their Linktree

63

) has channels like #developers and #strategy where yield strategies are discussed. Scraping

message history requires a bot or API integration (Discord’s API), focusing on key channels for

signal (governance updates, support).

•

Aave Discord – Aave’s Discord (discord.gg/aave) is more developer-focused (for integration help)

but also has risk parameter discussions. For instance, risk parameter changes to Aave that might

affect Ethena’s collateral loops could surface here first.

•

Other Protocol Discords: Similarly, one could monitor Gearbox’s Discord, Morpho’s Discord,

etc., since these yield protocols have overlapping communities. (Ensure to only use publicly

available info – many Discords have public read channels, which can be parsed with appropriate

permissions.)

•

Note:  Discord   content   can   be   unstructured;   a   prudent   approach   is   to   scrape   specific

announcement channels or use Discord’s API to fetch the last N messages periodically. This will

capture   things   like   official   announcements   (e.g.,   Ethena   team   posts   about   new   exchange

integrations or Pendle announcing a new yield market on Plasma).

•

Twitter/X Accounts & Threads:  Crypto Twitter is a crucial source for alpha and analysis, and

many accounts are open for scraping:

•

Protocol Team Accounts: Official Twitter accounts share updates and are easily scrapable. For

example, @ethena_labs (Ethena Labs’ handle) posts about milestones and strategies – e.g.,

threads on sUSDe’s yield mechanics and campaign updates

64

. @pendle_fi tweets yield market

launches, incentives, and has even shared charts (like funding rate trends impacting Pendle)

65

.

5

@aave (the Aave team’s account) posts protocol upgrades and new markets

66

. Following these

gives timely info (like new collateral listings or partnerships among Ethena/Pendle/Plasma).

•

Top DeFi Analysts on X: Many respected analysts and influencers share threads dissecting

protocols:

◦

Ignas (@DefiIgnas) – regularly breaks down complex DeFi strategies in tweet threads

(often covering yield farming and new stablecoin models).

◦

Andrew Kang (@Rewkang) – a prominent DeFi investor known to comment on yield

opportunities and market sentiment. His tweets can indicate where “smart money” is

rotating (he famously highlights high-yield strategies when they emerge).

◦

Camila Russo (@CamiRusso) – founder of The Defiant, often tweets news bits and links to

deeper analysis (useful for quick news scraping).

◦

Ryan Sean Adams & David Hoffman (@RyanSAdams, @TrustlessState) – Bankless founders

who tweet takeaways from Bankless articles/podcasts (e.g. highlighting if a yield loop is

getting too crowded or risky).

◦

Anthony Sassano (@sassal0x) – focuses on Ethereum but often touches on DeFi growth (he

might tweet if something like Ethena significantly impacts Ethereum usage/funding

rates).

◦

Messari & Delphi analysts: e.g. Messari’s account (@MessariCrypto) tweets research

snippets (which can be parsed for key points), and Delphi Digital’s account shares charts

and insights (some might be relevant to Pendle’s fixed rates or global yield trends).

◦

Other notable mentions: @DefiMoon, @TheDeFiEdge, @Route2FI – known for yield

farming tips and strategy threads. These accounts sometimes do long threads on how to

maximize stablecoin yields (which could include Ethena/Pendle combos). Their content

can be scraped by pulling the tweet threads via Twitter API v2.

•

Community Threads: Often, community members or smaller analysts post detailed explainers –

for example, a thread explaining Ethena’s hedge strategy or a deep dive into Pendle’s

veTokenomics. Searching Twitter for keywords (like “Ethena yield Pendle thread”) via API can

surface these. One notable case: a user on X explained Ethena’s ROI coming from staking ETH +

shorting via perps

60

, which distilled the strategy in accessible terms – scraping such organic

discussions is useful for documentation and for identifying pain points or misconceptions.

•

Aggregators on Twitter: Accounts like @DefiLlama and @CoinGecko share charts (TVL

rankings, yield leaderboards) that are quick to scan. Also, @Glassnode or @TheBlock might

share analytics relevant to stablecoin flows or funding rates affecting Ethena. These can be

scraped by monitoring their timelines or specific keywords.

By organizing the above sources into structured categories, we cover both  quantitative data  (APIs,

subgraphs for metrics) and  qualitative context  (social forums, blogs for sentiment and analysis). All

these sources are scrapable via APIs or standard web-scraping, enabling a comprehensive dashboard

for the iterated yield strategy. Leveraging the APIs (for up-to-date metrics like APY, TVL, funding rates)

alongside community chatter (for risk alerts or governance changes) will provide a robust and real-time

view of the Ethena–Aave–Pendle ecosystem

43

59

.

1

Aave Client SDK | Aave Protocol Documentation

https://aave.com/docs/developers/aave-v3/getting-started/graphql

2

3

Aave Market Data | Aave Protocol Documentation

https://aave.com/docs/developers/aave-v3/markets/data

4

22

23

24

GitHub - curvefi/curve-api

https://github.com/curvefi/curve-api

6

5

justmert/Aave-API-Telegram-Bot - GitHub

https://github.com/justmert/Aave-API-Telegram-Bot

6

7

8

Overview | Ethena

https://docs.ethena.fi/api-documentation/overview

9

10

Real-Time Dashboards | Ethena

https://docs.ethena.fi/backing-custody-and-security/real-time-dashboards

11

12

Index Ethena Data with Streams & Subgraphs - Goldsky

https://goldsky.com/chains/ethena

13

14

Pendle Documentation

https://docs.pendle.finance/

15

16

49

Pendle V2 Mainnet Subgraph | Graph Explorer

https://thegraph.com/explorer/subgraphs/ExXGU3ub2nrT5stPk5cH4hSk2qunJcMcP8eX5GAhrZhe?

view=Query&chain=arbitrum-one

17

Case Study: Pendle Finance - How Ormi Fueled a $6 Billion DeFi ...

https://blog.ormilabs.com/how-ormi-powers-pendle-data-infra/

18

Pendle expands DeFi offerings to Plasma with 5 yield markets

https://crypto.news/pendle-expands-defi-offerings-to-plasma-with-5-yield-markets/

19

20

Plasma Docs - Build on Plasma

https://docs.plasma.to/docs/guides/network-configuration/mainnet-details

21

Routescan APIs - Plasma Network (XPL) Blockchain Explorer

https://plasmascan.to/documentation/api/swagger

25

Subgraph Configuration - Grafbase

https://grafbase.com/docs/gateway/configuration/subgraph-configuration

26

Curve Subgraph - Infrastructure Tools - Alchemy

https://www.alchemy.com/dapps/curve-subgraph

27

28

30

Balancer API | Balancer

https://docs.balancer.fi/data-and-analytics/data-and-analytics/balancer-api/balancer-api.html

29

Subgraph - Balancer Docs

https://docs.balancer.fi/data-and-analytics/data-and-analytics/subgraph.html

31

32

Stargate API

https://docs.stargate.finance/developers/api-docs/overview

33

34

35

Stargate Finance by LayerZero Labs | QuickNode

https://www.quicknode.com/builders-guide/tools/stargate-finance?category=blockchain-interoperability

36

Stargate Avalanche | Graph Explorer

https://thegraph.com/explorer/subgraphs/6XypMkQUovcohhVC2XeWgdXeDsBcnL9ynKdLXpXggoHd

37

38

39

40

41

Welcome - deBridge Home

https://docs.debridge.com/

42

43

Binance Earn Enables API Functionality for Simple Earn & ETH Staking | Binance Support

https://www.binance.com/en/support/announcement/detail/c0250022fed440e0be7c3a388b08d9be

44

Earn Rewards On Crypto with Binance Earn | DeFi Staking & Yield ...

https://www.binance.com/en/earn

7

45

46

47

How Developers Use the DefiLlama API to Power DeFi Applications | by Eren Silvar Quade |

Medium

https://medium.com/@ErenSilvarQuade/how-developers-use-the-defillama-api-to-power-defi-applications-e4158f049bc9

48

Subscribe - DefiLlama

https://defillama.com/subscription

50

How to Manage API keys | Docs - The Graph

https://thegraph.com/docs/en/subgraphs/querying/managing-api-keys/

51

Aave Total value locked - Token Terminal

https://tokenterminal.com/explorer/projects/aave/metrics/tvl

52

Yield Rankings - DefiLlama

https://defillama.com/yields

53

The Year Ethena Took Over - Bankless

https://www.bankless.com/read/the-year-ethena-took-over

54

Ethena's USDe stablecoin surges to $12 billion supply, fueled by ...

https://www.theblock.co/post/368677/ethenas-usde-stablecoin-surges-to-12-billion-supply-fueled-by-leveraged-yield-loops-

on-pendle-and-aave

55

Rumpel: Converting Point Farming into Liquid Yield - Messari

https://messari.io/report/rumpel-converting-point-farming-into-liquid-yield

56

Pendle Price, PENDLE to USD, Research, News & Fundraising

https://messari.io/project/pendle

57

Pendle 2025: Zenith - Medium

https://medium.com/pendle/pendle-2025-zenith-cf1a91e6e23f

58

Ethena Staked USDe | Latest News & AI Summaries | Messari

https://messari.io/project/ethena-staked-usde/news

59

62

Is Ethena Legit? : r/defi - Reddit

https://www.reddit.com/r/defi/comments/1bm1bgp/is_ethena_legit/

60

Ethena RoR : r/defi - Reddit

https://www.reddit.com/r/defi/comments/1f37x5s/ethena_ror/

61

Aave_official subreddit gone? : r/aave

https://www.reddit.com/r/aave/comments/1b4wv3f/aave_official_subreddit_gone/

63

Pendle Finance | Twitter - Linktree

https://linktr.ee/pendle_finance

64

Ethena Labs (@ethena_labs) / Posts / X

https://x.com/ethena_labs

65

Pendle on X: "RT @Jonasoeth: Funding rate is one of the most ...

https://x.com/pendle_fi/status/1970725763491209613

66

Aave (@aave) / Posts / X

https://x.com/aave?lang=en

8

