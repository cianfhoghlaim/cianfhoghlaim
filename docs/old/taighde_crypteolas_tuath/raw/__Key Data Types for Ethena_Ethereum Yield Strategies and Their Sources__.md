Key Data Types for Ethena/Ethereum Yield

Strategies and Their Sources

Price & Peg Metrics

USDe Peg Price (Ethena’s stablecoin): The price of USDe should stay near \$1.00. You can monitor this
via free APIs like CoinGecko (REST endpoint for  ethena-usde ) or CoinMarketCap (requires a free API

key)

1

2

. These provide real-time quotes (updated every few minutes) and historical daily prices for

backtesting. For example, USDe has traded around \$0.999–\$1.000 recently

3

. CoinGecko’s API offers

daily price history (suitable for long-term peg stability analysis) and is free with rate limits. This is ideal

for  live  peg  tracking  and  for  simulating  stress  scenarios  –  e.g.  during  a  market  shock  USDe  briefly

dipped   well   below   \$1   (indicating   peg   risk)

4

.   Alternatively,   on-chain   DEX   price   feeds   (via  Dune

Analytics  or  a  protocol’s  subgraph)  can  be  used  to  verify  the  peg  in  real  time,  but  CoinGecko  is  a

straightforward starting point.

sUSDe Price (Staked USDe value):  sUSDe’s price represents USDe plus accrued yield. Unlike USDe,

sUSDe gradually appreciates above \$1.00 as yield is earned
around \$1.20, up from \$1 a year ago
with   a   free   API   (ID:   ethena-staked-usde )

7

6

. For instance, sUSDe is currently worth
. CoinGecko tracks this under “Ethena Staked USDe (SUSDE)”

5

.   This   data   lets   you   calculate   the  realized   APY  (by

measuring sUSDe’s price change over time). It’s updated live (few-minute intervals) and historical daily

prices   are   available   for   backtesting   the   yield   accrual.   As   an   alternative,   you   can   compute   sUSDe’s

“exchange rate” on-chain (the ratio of total USDe backing vs. sUSDe supply) via Ethena’s smart contract

(ERC4626 vault), but using CoinGecko or DeFi Llama is simpler. DeFi Llama also lists sUSDe under yield-

bearing stablecoins; for example, it shows sUSDe’s current APY ~4.4% with a 30-day average ~4.5%,

based on the price trend

8

. These sources are free and suitable for both live tracking and historical

analysis of the peg and yield performance.

Supply & TVL Metrics

USDe Circulating Supply and TVL: Ethena’s USDe has become a major stablecoin, so tracking its total

supply (market cap) and distribution is critical. DeFi Llama provides an aggregated view: USDe’s supply
.   DeFi   Llama’s   free   API   ( GET   /
is   about   $10+   billion,   making   it   the   3rd–4th   largest   stablecoin
stablecoin/usde )   returns   current   supply   and   even   breakdown   by   chain.   For   example,   it   shows

9

USDe’s allocation across Ethereum vs. other chains (Ethereum ~98% of TVL)

10

. This data updates daily

(sufficient for monitoring growth or contractions) and includes a historical chart (accessible via API or

CSV) for backtesting adoption trends. CoinGecko and CoinMarketCap likewise report USDe’s market cap

(with   historical   snapshots),   so   they   can   be   used   as   alternatives

9

.   Tracking   supply   is   useful   for

modeling strategy capacity and market impact  – e.g., a rapid supply surge of 60% over six weeks

was observed in late 2025

11

, indicating increased adoption and potentially higher yields

12

.

Ethena Protocol TVL (Collateral Backing):  To monitor risk, one may track the total value locked in

Ethena’s contracts (the collateral securing USDe). DeFi Llama reports Ethena’s TVL (about \$9.8B across

. This essentially mirrors the USDe supply (since USDe is
Ethereum and a few million on other chains)
fully collateralized/delta-hedged) and updates daily. Access via DeFi Llama’s protocol API ( /protocol/
ethena ) is free. Historical TVL data (for stress testing) is also available, which is useful to see how the

10

1

collateral pool changed during market volatility. For example, during a flash crash, TVL fluctuations

might indicate collateral outflows or emergency stabilizations

13

14

.

Aave Utilization & Deposits: In leveraged strategies, a portion of USDe/sUSDe is supplied to Aave. It’s

helpful to track Aave pool utilization and total deposits for relevant assets: e.g. amount of USDe and

sUSDe supplied on Aave V3. This can be obtained via Aave’s  subgraph  (free GraphQL API) or  Dune

Analytics queries. These sources can give real-time values of total supplied/borrowed and utilization %

(borrowed/liquidity)  for  USDC,  USDT,  USDe,  etc.  Monitoring  utilization  is  key  –  a  spike  toward  100%

utilization in USDT/USDC pools can foreshadow rising borrow rates and stress

15

16

. For instance,

after Oct 10, utilization in stablecoin pools jumped, so knowing the historical utilization (via subgraph or

tools like Aavescan) helps predict rate spikes. While this data may not come as a simple REST feed, it’s

accessible   via   free   analytics   and   is  vital   for   risk   monitoring  in   your   dashboard   (both   live   and   for

backtesting how past conditions affected Aave liquidity).

Yield & Rate Metrics

Ethena Native Yield (sUSDe APY): Staking USDe into sUSDe  yields a variable return sourced from

Ethereum staking and perp funding. Ethena’s app and docs provide the current sUSDe APY. As of now,

the baseline APY is relatively modest (~4–5% on average recently)

8

, but it has been highly variable –

e.g. ~19% on average through 2024, dropping to ~4% in late 2025

17

. This volatility is because the yield

comes from two components: (1)  ETH staking rewards  (~3–4% APY from consensus, stable) and (2)

perpetual futures funding  (which averaged ~6–9% historically, but swings widely)

18

. For real-time

tracking,   Ethena’s  Market   Data   dashboard  (on   app.ethena.fi)   shows   current   yield   and   even

breakdowns (e.g. average perp funding yield by quarter)

19

. For programmatic access, you can use

DeFi Llama’s yields API – it tracks an “sUSDe staking” pool with current APY (~4.4%) and 30d avg APY

8

. This API is free and provides historical APY data points, which is excellent for backtesting (e.g.

modeling how yield responded to past market conditions). In summary, use Ethena’s own stats or DeFi

Llama for live APY, and historical yield series (to build confidence intervals) can be derived from those or

from sUSDe price history. (Note: Ethena’s yield is pro-cyclical – it spiked above 20% APY in bullish periods

and can shrink or even go  negative net yield  in bear markets

17

20

, so capturing a wide historical

range is important for simulations.)

Perpetual Funding Rates (Off-chain Yield Driver):  Since a major part of sUSDe’s yield comes from

shorting perps, funding rate data is crucial. You can pull ETH perpetual funding rates from exchange
APIs – e.g.  Binance Futures  has a free endpoint for funding history ( GET /fapi/v1/fundingRate

for a given symbol)

21

. This provides an 8-hour funding rate and timestamp, which you can aggregate

to annualized%. Other exchanges like OKX or Bybit offer similar free data. For a more aggregate view,

third-party   sites   like  CoinGlass  (formerly   Bybt)   list   industry-average   funding,   though   their   API   may

require a key. Historical funding rate series (at least back a few years) can be fetched exchange-by-

exchange via these public APIs and then used to simulate Ethena’s yield in different market regimes. For

example, in bullish quarters funding was strongly positive (Ethena cites ~6–9% annualized on average

22

,   and   even   spikes   of   30%+   during   2025’s   rally

23

),   whereas   after   the   Oct   crash   funding   turned

negative (costing yield)

20

.  Use-case:  incorporate this data to build  confidence intervals  for sUSDe

APY – e.g., assume base ~4% from staking plus a distribution of funding that could be +10% in a bull or

–2% in a severe bear. The data is free; for live tracking you might poll the latest funding rate from a

major exchange (Binance provides current funding and even predicted next funding in their API), and

for backtesting, pull historical funding rates to replay how Ethena’s yield would have behaved.

Ethereum Staking Yield:  The other yield component is the ETH staking reward (for collateral held as

staked ETH). While this is relatively steady (~3–4% APY currently

24

), you might still want to track it for

2

completeness.  Beacon chain data sources  like Beaconcha.in or  Staking Rewards API  can give the

current network APR for validators. Many are free (for example, Beaconcha.in has an API for the current

epoch   reward   rate).   This   is   mostly   for   understanding   –   your   dashboard   can   just   treat   ~3-4%   as   a

constant   baseline,   but   if   doing   precise   modeling,   using   an   API   to   update   this   based   on   network

conditions   (e.g.   if   Ethereum   staking   yield   changes   with   participation   or   fee   burns)   can   refine   your

simulation. Historical staking yield (e.g. via Dune queries on validator rewards or via Ethereum metrics

APIs) is available for backtesting, but given its low volatility, a simple average might suffice.

Aave   Supply   Rates   (Depositor   APY):  In   leveraged   strategies,   you   supply   assets   to   Aave   and   earn

interest.  Aave’s   API/Subgraph  provides   real-time   supply   APYs   for   each   asset   in   each   market.   For

example,   on   Aave   v3   Ethereum,   supplying   USDe   currently   earns   ~5%   APY

25

  (this   comes   from

.
borrowers paying interest), whereas supplying sUSDe earns ~0% APY (since no one borrows sUSDe)
You   can   get   these   rates   via   the   Aave  subgraph  (GraphQL   query   for   reserveParameters   or
reserveData   will   return   current   liquidity   rate).   Aave’s  JSON-RPC   contract   call
(e.g.
getReserveData()  on the LendingPool contract) is another free method to fetch the current variable

25

APR. For convenience,  DefiLlama’s  “yields” aggregator  lists Aave pool rates too (e.g.  USDC (Aave V3

Ethereum) – APY 3.55%

26

). It may not yet list USDe, but if USDe is supported on Aave, you can find its

rate on the Aave UI or via the subgraph. These sources are free and update in real time as conditions

change.   For   backtesting,   Aave’s   subgraph   allows   querying   historical   rates   or   utilizing   community

dashboards:   e.g.  Aavescan  provides   historical   lending   rates   charts

27

.   You   might   export   historical

utilization  or  interest  rate  events  to  simulate   how   supply  APYs   moved  during   volatile   periods.   (This

matters   because   during   stress,   borrow   demand   shifts   –   after   Oct   10,   stablecoin   borrow   demand

dropped, so supply APYs fell). In summary, use Aave’s data to feed your dashboard with  live deposit

yields and to analyze past APY spread behavior.

Aave Borrowing Rates: The cost of borrowing stablecoins (USDT, USDC, etc.) on Aave is a key part of

the strategy’s P/L. We need to monitor these to gauge  APY spreads  (sUSDe yield vs. borrow cost)

28

20

. Aave’s subgraph or API similarly provides variable borrow APR for each asset. Recently, Aave v3

Ethereum saw ~5.6%–5.9% variable APR for USDC/USDT loans

29

30

, though these can fluctuate. After

the crash, these rates actually fell to ~1.5–2.0% above sUSDe’s yield (making the trade unprofitable)

31

.

For   live   data,   query   Aave’s   subgraph   or   use   the  Aave   UI’s   JSON   data.   Some   dashboards   (e.g.

DefiLlama’s  borrow   aggregator)   also   surface   current   borrow   rates   across   protocols;   for   example,

DefiLlama might show Aave USDT borrow APY ~X% on Ethereum vs. other venues. The data is free. For

historical   analysis,   you   can   reconstruct   borrow   rate   changes   from   Aave’s   interest   rate   model   and

utilization (or fetch snapshots via Dune). This helps answer “would the loop have worked in previous

conditions?”   by   seeing   periods   where   borrow   was   cheaper   or   more   expensive   than   yield.   Your

dashboard   could   even   display   the  real-time   APY   spread:  sUSDe   APY   minus   USDT   borrow   APR,   which

should be positive for profitability. If that spread inverts (negative carry), it’s a warning sign (as noted by

research firms)

20

15

. In fact, Sentora Research specifically advises tracking this spread closely, since

a sustained negative spread can force unwinding of positions

32

15

.

Pendle Fixed Yields (Principal Tokens): For the Pendle strategy, you’ll want data on PT-USDe yields –

essentially the fixed rate you lock in. Pendle’s official app (pendle.finance) displays the current discount

and implied APY  for each maturity. For example, a November 2025 USDe PT was recently yielding

~6.65% APY fixed

33

. To integrate this, you can use Pendle’s subgraph or API (Pendle has subgraphs on

The Graph for its markets) to fetch the PT price and calculate APY = (RedeemValue/MarketPrice - 1)/

time. Some community dashboards or Dune queries might already compute Pendle yield curves. If you

prefer a ready source, check if Defi Llama lists Pendle pools under “Yield” – they might list something

like “USDe PT (maturity date) – APY X%, TVL Y”. If not, Pendle’s own analytics (they have a dashboard called

Pendle Scan or via their API) would be the way. This data is generally free (Pendle’s subgraph is open).

Granularity:  you can get real-time quotes for the PT price whenever needed (Pendle’s AMM pricing

3

updates with each trade), and historical data by querying price snapshots. For backtesting, you could

simulate if earlier maturities offered better/worse rates – Pendle launched USDe markets more recently,

so   historical   depth   may   be   limited,   but   you   can   see   how,   say,   the   fixed   rate   varied   with   market

conditions.  Including  PT  yield  in  your  dashboard  helps  show  a  baseline  “risk-free”  (fixed)  yield  to

compare against the variable sUSDe yield.

Pendle Yield Tokens (YT) & Leveraged Yield: If you consider more complex strategies (like buying YT-

sUSDe to leverage yields), you’d need data on YT prices and projected APYs. YT gives you the floating

yield of an asset without principal, effectively a leveraged play on future yield plus any incentive points

34

35

. Pendle’s interface can show the current effective APY if you purchase a YT (it depends on how

much yield is expected vs. YT price). While this is advanced, note that  YT-sUSDe also earns Ethena’s

points (since you’re entitled to the yield, you get the Sats points as if you held sUSDe)

36

35

. Tracking

this in real time is complex; you might rely on analyses (e.g. a Binance Square post estimated ~393%

APY from YT-sUSDe when including points rewards in a campaign

35

). If you include this, use Pendle’s

subgraph to get YT prices and perhaps Ethena’s current sUSDe yield to compute what cash yield the YT

represents. This is likely beyond a basic dashboard, but it’s worth noting as a backtest: e.g.,  had one

bought YT in the past, would the realized yield + points have outperformed? – you’d need historical

sUSDe yield and Pendle pricing to simulate that. For now, a simpler approach is to note that Pendle YT is

available and that its returns hinge on the same data (sUSDe yield) plus point multipliers.

Leverage & Risk Metrics

Health Factor & Collateral Ratios: In a leveraged loop, maintaining a safe Health Factor (HF) on Aave

is paramount. HF is calculated from real-time collateral value vs. borrowed value and risk parameters.

To monitor HF, you can fetch your position data via Aave’s subgraph (which lists user reserves, collateral

balances, debt, and health factor). This is a free query. For a given user address, the subgraph (or Aave’s
contract call  getUserAccountData ) will return the current HF. Embedding this in your dashboard lets

you see, for example, “Current Health Factor: 1.8”. If you want system-wide risk, you could even track how

many   accounts   have   HF   <   1.1   (risky   zone)   using   Dune   Analytics   –   though   that’s   more   of   a   one-off

analysis (Sentora noted a rise in positions within 5% of liquidation after the crash

15

). For backtesting,

you can simulate HF over time by feeding in historical prices (USDe, sUSDe) and debt amounts, or use

historical Aave snapshots to see if a given initial position would have liquidated during past volatility.

Risk   parameters  (like   Aave’s   collateral   factors)   are   needed   for   this:   e.g.,   in   Aave’s   “E-Mode”   for

correlated stables, the liquidation threshold is 92%

37

. These parameters are accessible via Aave docs

or API – they’re static values (e.g., USDe in E-Mode: LTV 97%, Liq threshold 92%

38

). Ensuring your

model uses the correct LTV/threshold is crucial. So your dashboard might list “Max Borrow % (LTV): 97%,

Liq Threshold: 92% (E-Mode)”  for reference. These are available on Aave’s  Risk Parameter JSON  or the

subgraph (free). They typically don’t change often (but if Aave governance updates them, you’d catch it

via the same sources).

Utilization Rates: As mentioned, utilization of lending pools is a leading indicator for rate changes and

potential liquidity crunch. It’s useful to display the current utilization% for USDT and USDC on Aave.

This can be calculated from total supplied and total borrowed (data via Aave subgraph). For example, if

USDT pool utilization is 85% and rising, borrow APR will climb steeply (Aave’s rate model has kinks). If it’s

near 100%, additional borrowing becomes impossible and rates max out – a scenario that could force

unwinding loops. After the Oct crash, reports noted utilization spiking, which drove borrow rates ~2%

above sUSDe yield

31

. In your dashboard, a simple gauge of utilization (and perhaps available liquidity

left) for key pools can inform when the strategy’s cost might jump. Historical utilization (from subgraph

snapshots or Dune) can support backtesting – e.g., did utilization ever hit 100% in past DeFi turmoil

(and thus what borrow rate resulted)? All this data is on-chain and free to query with the right tools.

4

Asset Price Volatility & Correlation:  While the strategy is mostly stablecoin-based, consider tracking

ETH price  if only to understand external risks (Ethena’s collateral includes ETH and BTC longs + short

perps

39

). A severe ETH price move could test Ethena’s collateral management (though USDe is delta-

neutral, extreme volatility could cause liquidity issues). Free price APIs (CoinGecko, etc.) can feed ETH/

USD, BTC/USD prices live – largely for context in your dashboard or to stress test the Ethena reserve. For

instance, a module could show “ETH -5% today”, which might hint at lower funding rates (in a big drop,

perp funding can flip negative). Similarly, tracking USDT or USDC prices (usually \$1) is mostly to catch

any rare depeg of those, which would affect collateral on Aave. These are readily available via the same

price APIs. Generally, live tracking of major crypto prices (free via CoinGecko or exchange websockets)

and incorporating their historical volatilities can enrich your backtesting scenarios (e.g., how would the

loop fare if ETH crashed 30% or if a stablecoin depegged briefly).

Liquidation   Alerts:  If   you   want   to   be   comprehensive,   you   could   integrate  liquidation   data  –   e.g.,

number of sUSDe positions liquidated or at risk. Platforms like Dune have community queries that track

Aave liquidations. This data (addresses liquidated, amounts, timestamps) is historical but can show how

often looped positions got wiped out in past volatility. It’s not an easily consumable API for live use

(unless you set up a custom alert via subgraph subscriptions), but for research it’s useful. For example,

if   backtesting   shows   no   liquidations   in   normal   periods   but   a   wave   on   Oct   10,   that   informs   risk

management. This level of detail might be beyond your immediate needs, but is available via on-chain

data if needed.

APY Spreads & Strategy KPIs

Bringing it together, your dashboard should highlight APY spreads between yields and costs, since the

core strategy is a carry trade. Key spread metrics to calculate (using data from above):

•

sUSDe   Yield   –   Stablecoin   Borrow   APR:  This   is   the   net   yield   of   the   looping   strategy   (before

incentives). Positive means profit, negative means bleeding cash. As noted, this turned negative

post-crash (e.g. borrow rates ~2% higher than sUSDe yield)

31

. Use the live sUSDe APY (Ethena

or DeFi Llama) minus Aave’s live borrow rate (subgraph). This can be tracked continuously. For

historical   simulation,   compute   this   spread   over   time   (daily   or   weekly)   to   identify   regimes   of

profitability vs loss. You have all components free: sUSDe APY history from DeFi Llama or by

derivation, and borrow APR history from Aave events – so you can chart, say, the spread over

2024–2025 and see how often it was >0.

•

Pendle Fixed – Floating Yield Spread: If using Pendle, you might show the difference between

current   sUSDe   APY   and   the   fixed   yield   available   on   PT.   This   indicates   the   “yield   curve”

sentiment – e.g., if sUSDe is yielding 5% but you can lock in 7% fixed, the market expects yields

to rise; if fixed is lower than current, market expects yields to fall. This spread can be calculated

from the data above (Pendle APY vs sUSDe APY). For backtests, seeing how that spread moved

can reveal opportunities (e.g., was there a time locking 10% fixed would have beaten the realized

floating yield?).

•

Incentive-Adjusted Yield: During incentive programs, you may want to display an “augmented

APY” including rewards. For example, if Ethena offers a temp 12% APY booster on USDe in Aave

40

, add that to the base yield in the model. Similarly, the value of Sats points (speculative) could

be shown as +X% (with a caveat). Data for these require pulling the incentive rates (explained

below) and, for points, assuming a conversion (perhaps using the ENA token’s market price once

live). This gives a fuller picture of total returns.

5

Incentives & Rewards Programs

Ethena   “Sats”   Points   (Multiplier   Campaigns):  Ethena   periodically   runs   incentive   campaigns   that

award  Sats points  for certain actions. Currently in “Season 3 – Sats Campaign”, simply staking USDe
. (Earlier campaigns had
(holding sUSDe) yields extra points with a 2× multiplier per dollar per day

41

higher multipliers for riskier tasks, e.g. 20× for providing Curve liquidity in Season 1

41

.) These points

will convert to Ethena’s governance token ENA in a future airdrop, effectively boosting your ROI (if ENA

has value). To track this, refer to  Ethena’s documentation/announcements  – the rules (multipliers,

durations) are published there

42

41

. There isn’t a public API for points accrual, but you can calculate

points earned  in your model: e.g., if you have $100k sUSDe, at 2× that’s 200k Sats points per day

(hypothetical units). For estimating value, you could pull ENA’s price (now trading around \$0.46

43

 via

CoinGecko   API)   and   assume   some   conversion   rate   (if   known,   e.g.   1   ENA   per   1000   Sats,   just   as   an

example). This would give a notional APY from points. For instance, analysts calculated the YT-sUSDe

strategy could yield hundreds of % APY when valuing the potential ENA airdrop

35

44

 – highlighting

how   significant   these   incentives   can   be.   In   your   dashboard,   you   can   list   the   current   multipliers   (to

inform users) and perhaps a  “Points APY”  line (with big disclaimers). Since Sats are off-chain,  monitor

Ethena’s official channels for any changes (campaign end on Mar 2025, etc.)

42

. This is all free info,

just not in an API – manual updates are needed.

Aave/Plasma Incentive Programs:  On the  Plasma L1, leveraged yields are sweetened by  XPL token

rewards and subsidized rates

45

46

. For example, Plasma may reimburse part of borrow interest or

distribute XPL for borrowers, resulting in an effective borrow rate ~4% (much lower than normal)

46

. To

incorporate this, check Plasma or Aave’s documentation for any liquidity mining details. Often, Aave

markets   with   incentives   have   a  “reward   APR”  displayed   on   the   UI.   If   XPL   incentives   exist,   Aave’s

subgraph might expose a rewardToken APR for that reserve. Otherwise, Plasma’s team might provide

an   API   or   data   on   how   much   XPL   per   $1   borrowed   per   day.   You   can   also   observe   XPL’s   price   via

CoinGecko   if   needed.   Given   Plasma   is   new,   data   might   be   sparse;   however,   Ethena’s   strategy   docs

indicate substantial XPL incentives on Plasma Aave

45

46

. For your purposes, you might assume a

fixed extra APY (e.g. “+X% APY in XPL incentives”) as stated by Ethena. This is more of a static input

unless you find a direct feed. It’s worth including in a summary table so that the total APY on Plasma =

base yield + XPL rewards – giving the full picture (Ethena noted Plasma offers the highest yields largely

thanks   to   these   subsidies).   All   information   on   this   is   publicly   provided   by   the   protocols,   just   not

aggregated in one API; you may need to periodically update it from blog posts or community forums.

Other Incentives:  Keep an eye on any  centralized promos  like  Binance Earn. In the strategy, $100k

was allocated to Binance for a promotional 12% APR on USDe

47

. Such promotions have fixed terms (in

that case, 12% until Oct 21, 2025, then 8% thereafter

47

). If you include CeFi in your dashboard, you

can note these rates. Sources for these are exchange announcements or listings on aggregator sites

(CoinMarketCap’s   “Earn”   section   or   DeFi   Llama   might   have   a   CeFi   yields   page).   For   example,

CoinMarketCap often lists staking/flexible savings rates for major exchanges (API available for some but

often requires key). In general,  free info via exchange websites  will tell you current promo yields.

These don’t need live updating as frequently (since they’re often fixed-period), but do include them for

completeness when comparing strategy components. For backtesting, you’d treat them as constants or

see if such promotions existed in the past (not usually, they come and go).

Summary   Table   –   Data   Sources   Overview:

(The   table   below   categorizes   each   data   type   with

recommended sources, API access, and usage notes for both live tracking and historical analysis.)

6

Data Type

Primary Source (API/

Data Access &

Free/Paid & Use for

Dashboard)

Granularity

Backtesting vs. Live

Stablecoin

Prices

(USDe,

sUSDe)

CoinGecko API –  coins/
ethena-usde ,
coins/ethena-staked-usde

1

6

; Alt: CMC API (key)

Total Supply

& TVL (USDe

& Ethena)

DeFi Llama API –  /
stablecoins/usde  and  /
protocol/ethena

10

;

CoinGecko/CMC for market cap

Real-time price

updates (couple

min); Historical daily

prices (CoinGecko’s

market_chart

endpoint) for long-

term peg analysis.

Daily (TVL and

supply typically

Free (rate-limited).

Suitable for live peg

monitoring and

historical trend (e.g.,

peg stability, sUSDe

appreciation curve).

Free. Great for

backtesting adoption

(supply growth) and

update every 24h on

tracking current size

aggregators);

(for context in

Historical series

dashboards). Live

downloadable (CSV

changes are slow,

or API).

daily granularity is

usually fine.

sUSDe

Staking

Ethena app/dashboard (current

last distribution and

APY display); DeFi Llama Yields

funding rates); 30d

Updated in near-

real-time (reflects

Yield (APY)

API (pool for sUSDe)

8

avg and potentially

time-series from

DeFi Llama.

Daily or epoch-level

updates (Ethereum

ETH Staking

Beaconcha.in API (network APR);

consensus updates

Rate

StakingRewards API

~ every 6 min

epoch) – changes

are gradual.

Perpetual

Funding

Rates

Exchange APIs (Binance Futures
GET /fapi/v1/fundingRate

Every 8 hours

(funding interval);

historical records

21

, OKX, etc. for ETH perp);

per exchange. Can

CoinGlass (web)

aggregate for

average.

Free. Use live to show

the latest APY.

Historical APY series

can be derived for

backtesting (variability

over time).

Free. Useful for

modeling baseline

yield. Historical data

easy to get (but

relatively stable). Live

use mainly

informational.

Free. Critical for

backtesting different

market conditions

(pull 1–2+ years of

data). For live, update

after each funding

interval – or use

predicted funding if

available.

7

Data Type

Primary Source (API/

Data Access &

Free/Paid & Use for

Dashboard)

Granularity

Backtesting vs. Live

Real-time, changes

with utilization

Aave Supply

APR (USDe,

etc.)

Aave Subgraph (GraphQL) or

(block-by-block, but

Aave JSON-RPC (on-chain call) for
liquidityRate ; DefiLlama

polling every few

minutes is fine).

(lists many Aave pools)

26

Historical via

Aave

Borrow APR

Aave Subgraph or on-chain call
for  variableBorrowRate ;

(USDT,

USDC)

Aave UI/API; DefiLlama borrow

aggregator

subgraph events or

AaveScan.

Real-time variable

APR (updates as

utilization shifts).

Can sample

periodically.

Historical via events

(interest rate model)
or third-party

(Aavescan).

Free. Use live to

display current

deposit yields on

Aave. Historical data

needed if evaluating

past loop yields

(requires some data

wrangling from

subgraphs or Dune).

Free. Essential for live

strategy monitoring

(cost of leverage) and

for backtesting

spread. Historical

reconstruction a bit

complex but doable

with on-chain data.

Aave Risk

Params

(LTV,

Static values (per

reference in

Free. Include for

Aave Docs or Risk Parameter

asset and mode).

dashboards (no

endpoints (e.g. JSON config);

Changes only when

frequent update

Liquidation

threshold, E-

also queryable via subgraph
( reserveConfiguration )

governance updates

needed). Use in

(rare; you’d hear

simulations to apply

Mode)

about it).

Health

Factor

(user-

specific)

Aave Subgraph (user data) or
Aave  getUserAccountData

call per address

Real-time per

account; you’d pull

whenever you want

to update the

dashboard (e.g. on

page load or on

interval).

correct leverage

constraints.

Free. Use live for your

own positions’ safety

monitor. Historical HF

can be computed if

reconstructing a

scenario, but no direct

feed (simulate with

price history).

Free. Good for live

monitoring of liquidity

Utilization

Aave Subgraph (totalSupply/

with lending activity.

utilization can be

Rates (Aave

totalBorrow for asset); Dune

Can compute on the

derived (backtesting

pools)

Analytics for periodic snapshots

fly from up-to-date

when borrow demand

Updates in real-time

stress. Historical

reserve data.

spiked – e.g. to see if

100% utilization ever

occurred).

8

Data Type

Primary Source (API/

Data Access &

Free/Paid & Use for

Dashboard)

Granularity

Backtesting vs. Live

Real-time price-

driven (changes

Free. Use live to

with each trade; in

display current fixed

practice check

yield on offer. For

periodically as it’s

backtesting, simulate

relatively liquid).

if fixed rates at entry

Historical PT prices

would beat floating

Pendle PT

Yield (Fixed

APY)

Pendle Subgraph/API (PT market

price & terms); Pendle app

(frontend shows current APY);

possibly DefiLlama (if integrated)

Pendle YT

Yield

(Floating)

Pendle Subgraph (YT price);

derived APY = current underlying
yield * leverage factor; Pendle

app UI for YT stats

available via

subgraph for

backtesting

performance.

Real-time, but yield

projection depends

on underlying APY

(sUSDe) which is

variable. Could

update alongside

sUSDe APY.

Static rules per

Ethena Sats

Points

(Incentive)

Ethena Docs/Blog (campaign

campaign (e.g. 2x

details: multipliers, duration)

for staking). Update

41

; Ethena SDK/GitHub for

if new campaign

point calculation rules

launches or ends.

Points accrue daily.

Aave’s UI on Plasma (shows any

Plasma XPL

reward APR); Plasma

Rewards

documentation/announcements;

(Incentive)

possibly DefiLlama if tracking

Plasma Aave yields

Likely a semi-static

APR (changes if XPL

price or allocation

changes). Check

weekly or as

announced.

9

(requires historical

price – subgraph

data).

Free. This is advanced

– use live if doing a

“speculative yield”

display. Backtesting

would need
combining sUSDe

actual yields with YT

price changes

(complex, but doable

via subgraph).

Free info. No direct

API – you’ll compute

points earned. For

modeling, assume

future token value;

backtesting not

applicable (past

campaigns differed).

Use in live dashboard

as “bonus yield

(speculative)” indicator.

Free. Include as added

APY on Plasma

strategy. Backtest by

applying it to

historical loops on

Plasma (if Plasma

existed historically –

it’s new, so mainly

forward-looking).

Data Type

Primary Source (API/

Data Access &

Free/Paid & Use for

Dashboard)

Granularity

Backtesting vs. Live

CeFi Earn

Rates (e.g.

Binance

USDe)

Exchange announcements (e.g.

Binance blog for promotions);

CoinMarketCap Earn section;

Exchange API (some have

savings endpoints)

rate. Not

continuously

variable.

Free (info). Use to

Fixed for promo

compare against on-

period, then

chain yields. Not for

changes to standard

complex backtesting

(just note if such

promos existed;

mostly use current

rates).

Free. Use live to

contextualize (market

up/down). Use

historical to simulate

stress on collateral/

funding (e.g. feed an

ETH crash to your

model to see HF
impact).

Major Asset

Prices (ETH,

BTC)

CoinGecko API (e.g.  /coins/
ethereum ); Kraken Websocket/

Real-time (seconds)

and historical

(Coingecko provides

API for real-time OHLC; any free

daily; Kraken can

price feed

provide intraday

OHLC for free).

Each   of   these   sources   is   cost-effective   (mostly   free),   allowing   you   to   build   a   comprehensive   data

pipeline.  For live dashboards, you’ll pull key metrics periodically (some every few minutes, like prices

and   APYs;   others   daily,   like   TVL).  For   backtesting,   you   can   leverage   the   historical   endpoints

(CoinGecko’s   market   charts   for   prices,   subgraph   queries   for   past   rates,   exchange   APIs   for   funding

history, etc.) to gather time-series and run simulations. Combining on-chain data (yields, utilization, TVL)

with off-chain data (funding rates, CeFi rates) will enable you to model strategy performance under

various scenarios and even construct confidence intervals for returns. All the data types listed – from

peg   prices   to   incentive   multipliers   –   feed   into   understanding   the  risk   vs.   reward  of   the   Ethena

strategies and will directly support your engineering of both dashboards and simulation models

28

20

. By organizing the data sources as above, you ensure that your pipeline remains robust,  cost-

efficient, and up-to-date with the evolving DeFi landscape.

Sources:  Key information and figures were obtained from official analytics and documentation: e.g.,

CoinGecko for price and market cap data

1

6

, DeFi Llama for TVL and yield metrics

10

8

, Ethena’s

docs for yield composition and incentives

18

41

, and news analyses (CoinDesk, The Defiant) for recent

real-world scenarios affecting these metrics

20

23

. These ensure that the recommendations on data

sources are grounded in the latest available information.

10

1

2

Ethena USDe Price Chart (USDE) - CoinGecko

https://www.coingecko.com/en/coins/ethena-usde

3

14

15

16

20

28

31

32

DeFi News: sUSDe Loop Trades Worth $1B at Risk

https://www.coindesk.com/markets/2025/10/29/recent-bitcoin-crash-has-put-usd1b-in-susde-loop-trades-at-risk-research-

firm-says

4

Third-Largest Stablecoin Briefly Loses Dollar Peg in Crypto Rout

https://www.bloomberg.com/news/articles/2025-10-11/third-largest-stablecoin-briefly-loses-dollar-peg-in-crypto-rout

5

17

18

22

24

25

30

34

35

36

40

41

42

44

Ethena USDe Yield Maximization Strategy.md

file://file_00000000728861f5ba57b19276d9e4a6

6

7

Ethena Staked USDe Price: SUSDE Live Price Chart, Market Cap & News Today | CoinGecko

https://www.coingecko.com/en/coins/ethena-staked-usde

8

SUSDE (7 days unstaking)(Ethena USDe - Yields - DefiLlama

https://defillama.com/yields/pool/66985a81-9c51-46ca-9977-42b4fe7bc6df

9

11

12

23

Market Cap of Ethena's USDe Stablecoin Surged 60% In Six Weeks - "The Defiant"

https://thedefiant.io/news/defi/market-cap-of-ethena-s-usde-stablecoin-surged-60-in-six-weeks

10

43

Ethena - DefiLlama

https://defillama.com/protocol/ethena

13

39

Ethena and the Mechanics of USDe - Coin Metrics

https://coinmetrics.io/state-of-the-network/ethena-usde/

19

Ethena

https://ethena.fi/

21

Introduction to Binance Futures Funding Rates

https://www.binance.com/en/support/faq/detail/360033525031

26

USDC(Aave V3 - Ethereum) - Yields - DefiLlama

https://defillama.com/yields/pool/aa70268e-4b52-42bf-a116-608b370f9501

27

Aave Markets: Live And Historical Lending Rates | Aavescan

https://aavescan.com/

29

33

37

38

45

46

47

Iterated Yield Maximization Strategy for a $1M USDe Portfolio.md

file://file_00000000d26c620e955fad5342a5256b

11

