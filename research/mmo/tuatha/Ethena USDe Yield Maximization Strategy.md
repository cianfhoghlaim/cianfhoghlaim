

# **Comprehensive Yield Maximization and Risk Management Strategy for a $1M USDe Portfolio in the Ethena Ecosystem**

## **I. Executive Summary**

Ethena has rapidly emerged as a foundational primitive within Decentralized Finance (DeFi), moving beyond the traditional stablecoin model to introduce what can be best described as a crypto-native "Internet Bond." By tokenizing a delta-neutral cash-and-carry trade, Ethena's synthetic dollar, USDe, provides a scalable, censorship-resistant, and, most notably, yield-bearing alternative to fiat-backed stablecoins. The protocol's swift growth to a supply exceeding $10 billion underscores the significant market appetite for such an instrument.1 This report provides a comprehensive, institutional-grade analysis for deploying a $1 million USDe portfolio to maximize risk-adjusted returns by leveraging the full spectrum of opportunities within the Ethena ecosystem and its key integrations.

The strategies analyzed are categorized by increasing complexity and risk, beginning with the foundational layer and extending to the frontiers of the ecosystem:

1. **Native Staking (sUSDe):** The baseline strategy involves staking USDe for its yield-bearing counterpart, sUSDe, to capture the protocol's organic yield derived from staked Ether (ETH) and perpetual futures funding rates. This represents the lowest-risk, on-chain method for earning yield directly from the protocol.  
2. **Leveraged Lending (Aave):** This intermediate strategy utilizes the "Liquid Leverage" framework on the Aave V3 money market. By supplying a combination of USDe and sUSDe, an investor can borrow stablecoins to create a leveraged, or "looped," position, amplifying exposure to the underlying yields and promotional rewards. This is analyzed on both Ethereum Mainnet and the nascent Plasma Layer 1\.  
3. **Yield Tokenization (Pendle Finance):** These advanced strategies involve using Pendle to split the yield-bearing sUSDe into its Principal Token (PT) and Yield Token (YT). This allows for either locking in a fixed-rate return until a future maturity date (a lower-risk approach) or gaining highly leveraged exposure to future variable yields and incentive points (a higher-risk approach).  
4. **Ecosystem Expansion (Plasma & Emerging Protocols):** This involves deploying capital into newer environments where Ethena is a foundational asset. The primary focus is the Plasma L1, which offers enhanced yields on leveraged strategies due to subsidized borrow rates and additional token incentives, albeit with increased technical and security risks.

The core finding of this analysis is that a static, single-strategy allocation is suboptimal. The dynamic and variable nature of Ethena's yield sources, combined with the diverse risk profiles of its integrated protocols, necessitates a blended, multi-strategy approach. This report culminates in three distinct, actionable allocation models for the $1 million portfolio, tailored to conservative, balanced, and aggressive risk appetites. These models provide a clear framework for navigating the opportunities and risks inherent in the Ethena ecosystem, moving beyond simple APY comparisons to construct a robust, strategic, and quantitatively-backed investment plan.

## **II. Foundational Layer: sUSDe Staking and Native Yield**

The most direct and fundamental method for generating yield within the Ethena ecosystem is by staking the USDe synthetic dollar to receive sUSDe (staked USDe). This process grants the holder a proportional claim on the protocol's generated revenue. Understanding the mechanics, yield composition, and associated incentives of this foundational layer is critical before exploring more complex strategies.

### **2.1. The sUSDe Staking Mechanism**

The transformation of USDe into sUSDe is governed by the StakedUSDe smart contract, which adheres to the ERC4626 Token Vault standard. This adherence is a crucial feature, as ERC4626 is a widely adopted standard for yield-bearing vaults on Ethereum, ensuring seamless composability and integration with a broad range of other DeFi protocols.3

The reward accrual mechanism does not involve rebasing or increasing the holder's quantity of sUSDe tokens. Instead, the protocol periodically transfers the generated yield, in the form of USDe, directly into the StakedUSDe contract. This inflow of USDe increases the total amount of USDe backing the fixed supply of sUSDe, causing the intrinsic value of each sUSDe token to appreciate over time relative to USDe. When a user unstakes, their sUSDe is burned, and they receive a proportionally larger amount of USDe than they initially staked, reflecting their share of the accrued rewards.3 To prevent arbitrage opportunities like "sandwich attacks," where informed actors could stake just before a large yield distribution and unstake immediately after, rewards are dripped into the contract every 8 hours and vest linearly over that same period, ensuring a smooth appreciation of sUSDe's value.3

A primary consideration for this strategy is the **7-day unstaking cooldown period**. To redeem sUSDe for USDe through the protocol, a user must first initiate an unstake request. The assets are then held in a separate USDeSilo smart contract for seven days, after which they become available for withdrawal. During this cooldown, the assets do not earn yield.3 This mechanism introduces a significant liquidity constraint. However, for investors seeking immediate liquidity, secondary markets for sUSDe exist on decentralized exchanges (DEXs) such as Uniswap and Curve. These markets allow users to swap sUSDe for other assets like USDT or USDe directly, bypassing the cooldown. It is important to note that executing large trades on these secondary markets can incur significant price impact or slippage, and during periods of market stress, sUSDe may trade at a discount to its underlying redeemable value as investors pay a premium for instant liquidity.6

### **2.2. Deconstructing the sUSDe Yield**

The yield distributed to sUSDe holders is not derived from inflationary token emissions but from two sustainable, exogenous revenue streams generated by the protocol's backing assets.7

1. **Staked ETH/LST Yield:** A portion of USDe's collateral is held in the form of staked Ethereum, typically via liquid staking tokens (LSTs) like stETH. These assets generate a baseline yield from Ethereum's consensus-layer rewards (a combination of issuance and transaction fees). This source of yield is relatively stable and is currently in the range of 3-4% APY.8  
2. **Funding and Basis Spread:** This is the primary and most volatile component of the yield. To maintain the delta-neutral peg of USDe, for every $1 of spot crypto collateral (e.g., ETH, BTC) held long, the protocol opens an equivalent $1 short position in the perpetual futures market. In most market conditions, particularly during bullish periods, there is a higher demand for long leverage. This imbalance results in a "funding rate," a periodic payment made from long position holders to short position holders. As Ethena holds the short side of this trade, it is a net recipient of these funding payments.3 Historically, the open-interest-weighted annualized funding rate has been significantly positive, averaging around 6-9% over the last three years.8

The combination of these two sources creates the total protocol yield, a portion of which is distributed to sUSDe stakers. The remainder is allocated to Ethena's reserve fund to act as a buffer during adverse conditions.3 The resulting sUSDe APY is therefore highly variable, reflecting the prevailing conditions in the derivatives markets. Historical data shows this variability clearly, with an average APY of 19% throughout 2024, but a more recent 30-day average of 4.1%.1 This pro-cyclical nature is a defining characteristic; the highest yields are generated during periods of bullish market sentiment and high speculative activity, which drive funding rates positive. Conversely, in bear markets, funding rates can turn negative, compressing or even eliminating this yield source.7

### **2.3. Incentive Overlay: The "Sats" Campaign (Season 3\)**

Layered on top of the native cash yield is a temporary incentive program. Following the "Shard Campaign" (Season 1), Ethena is currently in its "Sats Campaign" (Season 3), which is scheduled to run for six months, concluding on March 23, 2025\.12 These campaigns are designed to bootstrap growth and align users with the protocol's long-term success by rewarding on-chain activities with points ("Sats"), which represent a claim on a future airdrop of the ENA governance token.13

Within the current campaign, the simple act of staking USDe to hold sUSDe provides a **2x multiplier** on Sats earned per dollar, per day.12 This multiplier is notably lower than those offered for more complex or higher-risk activities in previous seasons, such as the 20x multiplier for providing liquidity on Curve during Season 1\.14 This strategic shift suggests a maturation of the protocol's incentive design, moving from aggressive acquisition of total value locked (TVL) towards encouraging more sustainable, long-term holding of its core yield-bearing asset.

It is crucial to recognize that the return from Sats is not a cash yield but a speculative one. Its value is entirely dependent on the future valuation of the ENA token at the time of the airdrop and is subject to potential vesting schedules and market volatility. Therefore, while it contributes to the total potential return, it must be heavily discounted for its speculative nature and illiquidity.

## **III. Capital Efficiency and Leverage on Aave**

While sUSDe staking provides a foundational yield, more advanced strategies within the Ethena ecosystem focus on enhancing capital efficiency through leverage. The primary venue for this is the Aave V3 money market, which has integrated both USDe and sUSDe, enabling a powerful strategy known as "Liquid Leverage." This approach allows investors to amplify their exposure to Ethena's yield streams, but it also introduces new layers of complexity and risk, most notably the risk of liquidation.

### **3.1. The "Liquid Leverage" Strategy Explained**

The Liquid Leverage strategy is a form of recursive lending, or "looping," specifically tailored for Ethena's assets on Aave. The process involves several steps:

1. **Initial Deposit:** The user supplies a roughly equal-value split of USDe and sUSDe as collateral into the Aave V3 protocol. This 50/50 split is a requirement to be eligible for certain promotional rewards offered by Ethena.1  
2. **Borrowing:** With the collateral deposited, the user borrows a different stablecoin, typically USDT or USDC, against their position. Aave's risk parameters determine the maximum amount that can be borrowed.15  
3. **Looping:** The borrowed USDT or USDC is then used to acquire more USDe (via a swap on a DEX). This newly acquired USDe is, in turn, partially staked into sUSDe and then both are deposited back into Aave as additional collateral.  
4. **Iteration:** This process of borrowing and re-depositing can be repeated multiple times to build a leveraged position. Each "loop" increases the total collateral supplied and the total debt, thereby magnifying the exposure to the yield generated by the sUSDe portion of the collateral.16

This strategy offers a key benefit beyond yield amplification: it provides a solution to the 7-day sUSDe unstaking cooldown. By maintaining a significant portion of the position in the liquid USDe token, the user retains the ability to unwind part of their position without being subject to the lock-up period, offering greater flexibility.15 Tools like DeFi Saver have even created automated "zaps" that can execute this entire multi-step looping process in a single transaction, improving gas efficiency and simplifying execution for users.15

### **3.2. Quantitative Yield Analysis (Ethereum Mainnet)**

The net Annual Percentage Yield (APY) of the Liquid Leverage strategy is a composite calculation, reflecting multiple income streams offset by the cost of borrowing.

**Yield Sources:**

1. **sUSDe Native Yield:** The foundational yield generated by the Ethena protocol on all sUSDe held as collateral. This has averaged 19% in 2024 but is highly variable.1  
2. **Aave Supply APY:** Aave pays a variable interest rate to suppliers of assets. On the Ethereum V3 market, the supply APR for USDe has recently been around 4.97%, while the rate for sUSDe has been 0.00% as it is not a borrowable asset.17  
3. **Promotional Rewards:** To incentivize this specific strategy, Ethena offers additional rewards. These have been cited at approximately 12% APY, applied to the USDe portion of the supplied collateral.1  
4. **Ethena "Sats":** The entire collateral base (both USDe and sUSDe) continues to earn Sats from Ethena's incentive campaign, amplified by the leverage.

**Cost Component:**

* **Borrow APR:** The primary cost is the variable interest rate paid on the borrowed stablecoins. On Aave V3 Ethereum, recent variable borrow APRs have been approximately 5.90% for USDT and 5.66% for USDC.19 These rates are algorithmic and increase as the utilization of the lending pool rises, meaning they can become more expensive as the strategy grows in popularity.20

The net APY can be modeled with the following formula, where $L$ is the leverage ratio (e.g., $L=3$ for 3x leverage):

$$\\text{Net APY} \= L \\times (\\text{Blended Supply APY}) \- (L-1) \\times (\\text{Borrow APR})$$  
The "Blended Supply APY" is the weighted average of all yield sources across the 50/50 USDe/sUSDe collateral. The profitability of the strategy is dictated by the spread between this blended yield and the cost of borrowing.

### **3.3. Risk Parameters and Liquidation Analysis**

Leverage inherently introduces liquidation risk. A position on Aave becomes eligible for liquidation if its Health Factor drops below 1.0. The Health Factor is a representation of the safety of the position, calculated as the collateral-value-weighted liquidation threshold divided by the total value of the debt.22

$$\\text{Health Factor} \= \\frac{\\sum (\\text{Collateral Value}\_i \\times \\text{Liquidation Threshold}\_i)}{\\text{Total Borrow Value}}$$  
Understanding Aave's specific risk parameters for Ethena's assets is therefore paramount.

| Asset | Max LTV | Liquidation Threshold (LT) | Liquidation Penalty | E-Mode (Stablecoins) LT |
| :---- | :---- | :---- | :---- | :---- |
| **sUSDe** | 72.00% | 75.00% | 8.50% | 92.00% |
| **USDe** | 72.00% | 75.00% | 8.50% | 92.00% |

(Data sourced from 24)

The **Loan-to-Value (LTV)** ratio determines the maximum amount that can be borrowed against a given collateral. The **Liquidation Threshold (LT)** is the percentage at which liquidation is triggered. For example, with a 75% LT, if the value of debt exceeds 75% of the collateral value, the position is at risk. The **Liquidation Penalty** is a fee paid by the borrower from their collateral to the liquidator. Aave's "E-Mode" (High Efficiency Mode) for correlated assets like stablecoins allows for much higher capital efficiency, increasing the LT to 92% when borrowing and lending assets within the same category.24

While a strategy involving only stablecoins appears safe from the volatility of assets like ETH or BTC, the primary risk here is a **de-peg event**. If the market value of the collateral (USDe/sUSDe) deviates downwards from the value of the debt (USDT/USDC), the Health Factor will decrease. Aave governance analysis has indicated that a mere 5% price deviation in USDe could render approximately $300 million of positions eligible for liquidation.28 This highlights the critical dependence on the stability of USDe's peg and the reliability of the price oracles that feed this data to Aave. In recognition of this risk, a proposal was passed to modify the sUSDe oracle to use Chainlink's USDT/USD price feed as its base, effectively pegging its on-chain valuation for lending purposes to USDT to prevent liquidations from transient, minor de-pegs.28

## **IV. Advanced Yield Structuring with Pendle Finance**

For investors seeking more sophisticated methods of managing and speculating on yield, Pendle Finance offers a powerful suite of tools. As the largest crypto yield trading platform, Pendle enables the tokenization of future yield, allowing users to split a yield-bearing asset like sUSDe into its principal and yield components. This separation creates distinct investment strategies: one focused on securing a fixed, predictable return, and another designed for leveraged speculation on future yields and incentive points.

### **4.1. Introduction to Pendle's Yield Tokenization**

Pendle's core innovation is the ability to take a yield-bearing token, such as sUSDe, and mint two new, distinct tokens: a Principal Token (PT) and a Yield Token (YT). These tokens have a fixed maturity date, at which point the system resolves.29

* **Principal Token (PT-sUSDe):** This token represents the underlying principal of the sUSDe. At the maturity date, one PT-sUSDe can be redeemed for one sUSDe. Because it does not accrue any of the yield generated by the underlying asset, it trades on the open market at a discount to the price of sUSDe. The size of this discount is determined by the market's expectation of future yields. This structure is analogous to a zero-coupon bond in traditional finance.30  
* **Yield Token (YT-sUSDe):** This token represents the right to claim all the variable yield generated by the underlying sUSDe from the time of minting until the maturity date. The YT holder can claim this accrued yield at any time. The value of a YT is highest at the beginning of its term and decays over time, approaching zero as it nears the maturity date, by which point all future yield has been realized.32

This mechanism unbundles the price exposure of the principal from the volatility of its yield, allowing each to be traded and managed independently.

### **4.2. Strategy 1: Fixed-Yield with Principal Tokens (PT-sUSDe)**

The most straightforward strategy on Pendle is to purchase PT-sUSDe on its secondary market. By buying the token at a discount to its face value and holding it until maturity, an investor effectively locks in a fixed rate of return. The profit is the difference between the purchase price and the redemption value (which will be one sUSDe).

This strategy is particularly attractive for several reasons:

* **Yield Certainty:** It converts the volatile, unpredictable yield of sUSDe into a known, fixed APY. This is ideal for investors with a lower risk tolerance or those who believe that the current market-implied yield is higher than what Ethena will actually deliver in the future.  
* **Hedging:** It can be used to hedge a portfolio against a potential decline in DeFi yields. If an investor anticipates that funding rates will compress, locking in a fixed yield via PTs can protect returns.  
* **Simplicity:** The strategy is passive. Once the PT is purchased, the investor simply holds it until maturity to realize the fixed yield.

The fixed yield available is determined by the market price of the PT. For example, recent market data on Pendle has shown fixed yields for PT-USDe (which is derived from sUSDe) at **6.65% APY** for a 32-day maturity (26 Nov 2025\) and **6.46% APY** for an 81-day maturity (14 Jan 2026).34

### **4.3. Strategy 2: Leveraged Yield & Points with Yield Tokens (YT-sUSDe)**

Purchasing YT-sUSDe is a significantly higher-risk, higher-reward strategy designed for speculating on future yields and, more importantly, maximizing exposure to point-based incentive programs.

The leverage in this strategy is implicit. Because a YT can be purchased for a small fraction of the price of the underlying sUSDe, an investor can control the rights to the yield of a large sUSDe position with a relatively small capital outlay. For instance, if a YT costs $0.0161, an investment of $1 could purchase approximately 62 YT, granting the investor the yield and points equivalent to holding 62 sUSDe.35

While the holder of YT-sUSDe does receive the cash yield from the underlying sUSDe, the primary driver of this strategy's profitability is often the magnified accumulation of incentive points. For example, one analysis of the YT-sUSDe strategy during the "Sats" campaign calculated a potential APY of **393%** based on the expected value of the Ethena airdrop alone, after accounting for the cost of the YT and the expected cash yield.35

However, this strategy carries substantial risks:

* **Yield Volatility:** The profitability of holding a YT is directly tied to the performance of the underlying sUSDe yield. If the actual APY generated by Ethena is lower than the "Implied APY" priced in by the market when the YT was purchased, the investment will underperform expectations.31  
* **Time Decay:** The value of a YT is inherently time-sensitive and will decay to zero at maturity. If the accrued yield and points do not outweigh the initial cost of the YT by the maturity date, the position will result in a net loss.  
* **Speculative Nature of Points:** The high projected returns are almost entirely dependent on the future value of an airdropped token (ENA). This introduces significant speculative risk, as the value of the points can be volatile and is not guaranteed. Hedging strategies, such as shorting ENA futures or selling points on over-the-counter (OTC) markets, can mitigate this but add complexity.35  
* **Underlying Protocol Risk:** The value of YT-sUSDe is entirely dependent on the continued operation and yield generation of the Ethena protocol. Any failure or disruption at the Ethena layer would render the YT worthless.31

In essence, purchasing YT-sUSDe is less of a traditional yield farming strategy and more of a leveraged, speculative bet on the future performance of Ethena's yield and the success of its incentive programs.

## **V. The New Frontier: The Plasma L1 Ecosystem**

While the strategies on Ethereum Mainnet offer robust and relatively battle-tested opportunities, the Ethena ecosystem is expanding to new frontiers. The most significant of these is its integration as a foundational component of Plasma, a new Layer 1 (L1) blockchain. Plasma is purpose-built and optimized for stablecoin finance, aiming to become a primary settlement layer by offering features like zero-fee USDT transfers.36 For a USDe investor, the Plasma ecosystem represents a higher-risk, higher-reward environment where familiar strategies like Liquid Leverage can be executed with potentially greater efficiency and enhanced incentives.

### **5.1. Strategic Overview of Plasma**

Plasma launched its mainnet beta in September 2025 with a clear strategic focus: to capture a significant share of global stablecoin flows. It differentiates itself from general-purpose L1s by optimizing its architecture—from its PlasmaBFT consensus mechanism to its fee structure—for high-frequency, low-cost stablecoin transactions.38

Crucially, Plasma's launch was not an isolated event but a carefully orchestrated ecosystem deployment. It went live with over 100 DeFi protocol integrations, including cornerstones like Aave and Pendle, with Ethena's USDe and sUSDe serving as core assets from day one.38 This deep integration was facilitated by a successful pre-launch deposit campaign that bootstrapped the chain with over $2 billion in TVL, a significant portion of which was Ethena-related assets, demonstrating strong market conviction and a well-executed go-to-market strategy.36

### **5.2. Enhanced Liquid Leverage on Aave Plasma**

The Aave V3 "Liquid Leverage" strategy, detailed for Ethereum Mainnet, is also available on Aave's Plasma deployment. However, the Plasma environment offers two key advantages that significantly alter the profitability calculation.

1. **Lower Borrow Costs:** The most direct enhancement to the strategy's profitability comes from a lower cost of leverage. On Aave Plasma, USDT borrow rates have been observed to be around **4%**, which is substantially lower than the \~5.6-5.9% rates typically seen on Ethereum Mainnet.19 This wider spread between the gross yield earned on the USDe/sUSDe collateral and the cost of borrowing directly translates to a higher net APY for any given level of leverage. This favorable rate environment is likely sustained by large, strategic liquidity provisions, such as a $1 billion commitment to a Binance Earn product on Plasma, which artificially suppresses borrowing demand relative to supply.36  
2. **Additional XPL Token Incentives:** To accelerate adoption and attract liquidity, the Plasma ecosystem is being heavily incentivized with its native token, XPL. DeFi protocols on the chain are running reward campaigns, such as Pendle's "Plasma Parade," which offered up to 1.14 million XPL for yield and liquidity position holders.45 It is highly probable that similar XPL reward programs are, or will be, directed at users of the Aave protocol, particularly those engaging in high-volume strategies like Liquid Leverage. These XPL rewards represent an additional layer of yield stacked on top of the sUSDe native yield, Aave supply APY, and Ethena's promotional rewards.

A comparative analysis shows that the combination of reduced borrowing costs and supplementary XPL incentives makes the Liquid Leverage strategy on Plasma significantly more lucrative than its Ethereum counterpart, assuming the investor is willing to accept the associated risks.

### **5.3. Bridging and Execution**

Accessing the Plasma L1 requires moving assets from an existing network like Ethereum. This is accomplished via a cross-chain bridge.

* **Recommended Bridges:** The most reliable and widely used bridges for transferring assets to Plasma are **deBridge** and **Stargate Finance**.48 deBridge, for example, supports over 25 networks and has a strong security track record, offering near-instant settlement for assets like USDT and ETH into Plasma.48  
* **Process:** The bridging process is straightforward:  
  1. Connect a source wallet (e.g., MetaMask on Ethereum) and a Plasma-compatible destination wallet to the bridge's user interface.  
  2. Select the source chain (e.g., Ethereum) and Plasma as the destination.  
  3. Choose the asset to bridge (e.g., USDT or ETH).  
  4. Approve the token transfer and confirm the bridge transaction in the wallet.  
  5. The assets typically arrive on Plasma within seconds, appearing as the native equivalent (e.g., USD₮0 or XPL).48  
* **Costs and Risks:** The cost of bridging is generally low, consisting of a flat fee charged by the bridge (e.g., deBridge charges 0.01 XPL) plus the standard gas fee on the source network.48 However, this step introduces a critical new risk vector: **bridge risk**. Cross-chain bridges are complex systems of smart contracts that have historically been prime targets for exploits. While reputable bridges undergo extensive audits, they remain a significant potential point of failure. Additional risks include transaction delays due to network congestion and the potential for insufficient liquidity on the bridge, which could impede large transfers.48 Deploying capital to Plasma is therefore not just a bet on Ethena and Aave, but also on the security and liveness of the chosen bridge and the nascent Plasma L1 itself.

## **VI. Comprehensive Risk Assessment**

A sophisticated yield strategy is defined not only by its potential returns but also by a thorough understanding and mitigation of its associated risks. The Ethena ecosystem, while innovative, presents a complex, multi-layered risk profile that spans from the core protocol design to the various applications it integrates with. This section provides a detailed analysis of these risks.

### **6.1. Protocol-Level & Sustainability Risks**

These risks pertain to the fundamental design and economic model of Ethena itself.

* **Negative Funding Rates:** This is the most significant and widely discussed risk to Ethena's sustainability. The protocol's primary yield source is positive funding payments from perpetual futures markets. During severe or prolonged bear markets, market sentiment can shift, causing funding rates to turn negative. In this scenario, Ethena, holding the short positions, would be required to make payments, draining revenue instead of generating it.10 To counter this, Ethena maintains a **Reserve Fund**, capitalized by a portion of the yield generated during positive funding periods. This fund acts as a buffer to cover payments during negative rate environments, ensuring that sUSDe holders do not experience negative yield.3 The adequacy of this fund relative to the total USDe supply is a critical variable; some analysts have suggested that a "keep rate" (the percentage of revenue directed to the fund) of over 32% would be necessary to withstand a bear market at a $10 billion market cap.10  
* **USDtb Integration as a Mitigant:** Recognizing the pro-cyclical nature of funding-rate-dependent yield, Ethena has strategically introduced USDtb as a backing asset. USDtb is a stablecoin backed by tokenized U.S. Treasury bills.51 The protocol's risk committee has approved a plan to reallocate USDe's backing from the delta-neutral position into USDtb during periods of negative funding. This allows Ethena to close its costly short hedges and instead earn a more stable, albeit lower, yield from the underlying T-bills, effectively diversifying its revenue sources and providing a crucial defense mechanism against adverse market conditions.51

### **6.2. Market & Collateral Risks**

These risks relate to the market dynamics of the assets Ethena uses and issues.

* **Collateral De-peg Risk:** Ethena uses liquid staking tokens like Lido's stETH as a primary form of collateral. While stETH is designed to trade closely to the price of ETH, it is not a perfect peg. During periods of extreme market stress, such as the collapse of Terra/Luna, the stETH/ETH peg has deviated significantly.7 A severe de-peg could compromise the value of Ethena's collateral, potentially leading to forced liquidations of its hedging positions if margin requirements are not met.7  
* **USDe Peg Stability:** While USDe is designed to be stable, it has experienced several de-pegging events where it traded materially below its $1 target, particularly during market-wide routs.10 The stability mechanism relies on arbitrageurs who can mint or redeem USDe with the protocol to bring the market price back in line. However, this mechanism is constrained by redemption limits (e.g., a cap of $10 million per block at one point) and a withdrawal buffer that, while robustly managed, could be temporarily drained under extreme demand.10 The successful handling of a $100 million redemption stress test demonstrates resilience, but the risk of temporary de-pegs under duress remains.28

### **6.3. Counterparty & Custody Risks**

As Ethena interacts with centralized entities, it inherits their counterparty risks.

* **Exchange Counterparty Risk:** Ethena's delta-neutral hedges (short perpetual futures) are held on centralized derivatives exchanges. To mitigate the risk of holding assets directly on these exchanges (as exemplified by the FTX collapse), Ethena utilizes off-exchange settlement (OES) providers. This allows assets to be held with an independent custodian while being available for trading on the exchange.8 However, incidents like the Bybit hack in early 2025 revealed that OES does not eliminate risk but rather transfers it. While Ethena's collateral may be safe, the exchange itself still bears the counterparty risk of Ethena's large, concentrated positions, creating a potential systemic vulnerability.10  
* **Custodian Risk:** The protocol's assets are held with regulated custodians and MPC wallet providers, including prominent names like Coinbase.8 While these are institutional-grade partners, they still represent a centralized point of failure. Any security breach, operational failure, human error, or bankruptcy at the custodian level could result in a loss of protocol assets.54

### **6.4. Smart Contract & Technical Risks**

These are risks inherent to operating on decentralized, code-based infrastructure.

* **Ethena's Security Posture:** Ethena has demonstrated a strong commitment to security, undertaking a multi-phased audit program with numerous reputable firms, including Zellic, Quantstamp, Spearbit, Pashov, and Chaos Labs. No critical or high-severity vulnerabilities were found in the initial audits.56 Furthermore, the protocol maintains an active public bug bounty program with Immunefi to incentivize the responsible disclosure of any potential vulnerabilities.56  
* **Composite Risk:** When engaging in strategies that involve multiple protocols, the smart contract risk becomes cumulative. A strategy utilizing Ethena, Aave, and Pendle is exposed to the smart contract risk of all three protocols simultaneously. An exploit or bug in any single protocol in the chain could lead to a cascading failure and a potential loss of all funds committed to the strategy. This "composability risk" is one of the most significant technical threats in advanced DeFi.

### **Table: Comparative Risk Assessment Matrix**

The following matrix provides a summarized assessment of the key risks across the primary strategies discussed in this report.

| Strategy | Smart Contract Risk | Negative Funding Risk | Collateral De-peg Risk | Liquidation Risk | Counterparty Risk | Bridge/L1 Risk |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| **sUSDe Staking** | Low | Medium | Low | None | Medium | None |
| **Aave Liquid Leverage (ETH)** | Medium | Medium | Medium | Medium | Medium | None |
| **Aave Liquid Leverage (Plasma)** | High | Medium | Medium | Medium | Medium | High |
| **Pendle PT-sUSDe** | Medium | Low | Low | None | Medium | None |
| **Pendle YT-sUSDe** | Medium | High | High | None | Medium | None |

**Justification for Ratings:**

* **Smart Contract Risk:** Increases with the number of protocols involved. "Low" for single-protocol interaction (Ethena), "Medium" for two (Ethena+Aave/Pendle), and "High" when adding a nascent L1 and bridge (Plasma).  
* **Negative Funding Risk:** Affects all strategies deriving yield from sUSDe. It is "Medium" for leveraged positions as it compresses the profitable spread, and "High" for YT as it can rapidly erode the token's value. It is "Low" for PT, as the fixed yield is already locked in.  
* **Collateral De-peg Risk:** Primarily affects leveraged positions where a de-peg could trigger liquidation. It is "High" for YT as a de-peg would also crush the underlying yield, making the YT worthless.  
* **Liquidation Risk:** Only applicable to leveraged borrowing strategies on Aave.  
* **Counterparty Risk:** A baseline "Medium" risk inherent to Ethena's model that affects all strategies.  
* **Bridge/L1 Risk:** Only applicable to strategies executed on the Plasma network.

## **VII. Strategic Allocation Models & Implementation**

Synthesizing the analysis of yield opportunities and their corresponding risk profiles, this section presents three distinct allocation models for a $1 million USDe portfolio. These models are designed to cater to different risk appetites, from conservative capital preservation to aggressive pursuit of maximum returns. Each model is accompanied by a clear rationale and a high-level implementation roadmap.

### **7.1. Model 1: Conservative Yield**

* **Target APY Range:** 15-25%  
* **Risk Profile:** Low  
* **Allocation:**  
  * **70% ($700,000):** sUSDe Staking  
  * **30% ($300,000):** Pendle PT-sUSDe (laddered across available maturities)  
* **Rationale:** This model prioritizes simplicity, security, and predictable returns while avoiding leverage and complex protocol interactions. The majority of the capital is allocated to the foundational sUSDe staking strategy, capturing the native Ethena yield and the 2x "Sats" multiplier. The allocation to Pendle Principal Tokens serves two purposes: it locks in a portion of the portfolio's return at a known, fixed rate, providing a hedge against the volatility of Ethena's funding-rate-driven yield. By laddering purchases across different maturities (e.g., 30-day, 90-day), the portfolio maintains a rolling liquidity profile. This strategy completely eliminates liquidation risk and minimizes smart contract risk by limiting exposure primarily to the heavily audited Ethena and Pendle protocols.

### **7.2. Model 2: Balanced Growth**

* **Target APY Range:** 25-45%  
* **Risk Profile:** Medium  
* **Allocation:**  
  * **40% ($400,000):** sUSDe Staking  
  * **40% ($400,000):** Aave Liquid Leverage on Ethereum Mainnet (target 2-3x leverage)  
  * **20% ($200,000):** Pendle PT-sUSDe  
* **Rationale:** This model introduces leverage in a measured way to enhance capital efficiency and boost returns. The Aave Liquid Leverage position is executed on Ethereum Mainnet, which is considered a more battle-tested and secure environment than newer L1s. A moderate leverage target of 2-3x balances the potential for amplified yield against the risk of liquidation. The significant allocation to direct sUSDe staking and Pendle PTs provides a stable, non-leveraged yield base that anchors the portfolio's overall risk profile. This balanced approach seeks to capture the upside from leveraged Ethena yields while maintaining a substantial defensive allocation.

### **7.3. Model 3: Aggressive Alpha**

* **Target APY Range:** 45%+  
* **Risk Profile:** High to Very High  
* **Allocation:**  
  * **60% ($600,000):** Aave Liquid Leverage on Plasma L1 (target 3-4x leverage)  
  * **30% ($300,000):** Aave Liquid Leverage on Ethereum Mainnet (target 2-3x leverage)  
  * **10% ($100,000):** Pendle YT-sUSDe  
* **Rationale:** This model is designed for maximum yield and fully embraces complexity and risk. The majority of capital is deployed into the Aave Liquid Leverage strategy on the Plasma L1 to capitalize on the significantly lower stablecoin borrow rates and the additional XPL token incentives. A higher leverage target is employed to maximize this advantage. The allocation to the same strategy on Ethereum provides a degree of diversification across environments. The tactical 10% allocation to Pendle Yield Tokens is a high-conviction, speculative play on the Ethena "Sats" airdrop, seeking to generate outsized returns through leveraged points farming. This portfolio accepts substantial L1 risk, bridge risk, and liquidation risk across multiple positions in its pursuit of the highest possible yield from the Ethena ecosystem.

### **7.4. Implementation Roadmap & Operational Security**

Executing these strategies requires careful planning and adherence to security best practices.

1. **Acquire USDe:** The initial $1 million in capital must be held as USDe. This can be acquired on major DEXs or, for whitelisted institutional users, minted directly through the Ethena dApp.  
2. **Wallet Security:** All operations should be conducted from a hardware wallet (e.g., Ledger, Trezor) to protect private keys. For managing multiple complex positions, consider using a dedicated wallet for each strategy to isolate risk.  
3. **Bridging (for Plasma Strategies):** For Model 3, a portion of the assets must be bridged to the Plasma network. Use a reputable bridge like deBridge. Always perform a small test transaction first to verify the process and wallet connectivity before bridging a large sum.  
4. **Platform Interaction:**  
   * **sUSDe Staking:** Use the official Ethena dApp (ethena.fi).  
   * **Aave Liquid Leverage:** Interact directly with the Aave V3 interface (app.aave.com). For simplified looping, consider using a trusted DeFi management tool like DeFi Saver, which can automate the recursive borrow-and-deposit steps in a single transaction.  
   * **Pendle:** Use the Pendle Finance app (app.pendle.finance) to purchase PT or YT tokens.  
5. **Position Monitoring:** This is the most critical ongoing task for any leveraged strategy.  
   * **Health Factor:** Constantly monitor the Health Factor of all Aave positions. A safe threshold is typically considered to be above 1.2, but this should be adjusted based on the volatility of the underlying assets. Set up alerts using on-chain monitoring tools to be notified if the Health Factor drops below a predefined level.  
   * **Yield & Rate Spreads:** Track the sUSDe native APY and the borrow rates on Aave. If the spread compresses significantly, the profitability of the leveraged strategy will decline, and deleveraging may be necessary.  
   * **Pendle Dynamics:** For YT positions, monitor the Underlying APY versus the Implied APY. For PT positions, be aware of the maturity date to ensure timely redemption.  
6. **Unwinding Positions:** Plan the exit strategy in advance. For leveraged positions, unwinding involves repaying the debt and withdrawing the collateral, which may require multiple transactions. Be mindful of the 7-day sUSDe unstaking cooldown and use secondary markets only if the potential slippage is acceptable.

#### **Works cited**

1. Ethena, accessed October 25, 2025, [https://ethena.fi/](https://ethena.fi/)  
2. Ethena USDe price today, USDe to USD live price, marketcap and chart | CoinMarketCap, accessed October 25, 2025, [https://coinmarketcap.com/currencies/ethena-usde/](https://coinmarketcap.com/currencies/ethena-usde/)  
3. Staking USDe | Ethena, accessed October 25, 2025, [https://docs.ethena.fi/solution-design/staking-usde](https://docs.ethena.fi/solution-design/staking-usde)  
4. How to Stake ENA \- Ethena Docs, accessed October 25, 2025, [https://docs.ethena.fi/video-guides/how-to-stake-ena](https://docs.ethena.fi/video-guides/how-to-stake-ena)  
5. sUSDe Rewards Mechanism \- Ethena Overview, accessed October 25, 2025, [https://docs.ethena.fi/solution-overview/protocol-revenue-explanation/susde-rewards-mechanism](https://docs.ethena.fi/solution-overview/protocol-revenue-explanation/susde-rewards-mechanism)  
6. Ethena Staked USDe price SUSDe \#13 \- CoinMarketCap, accessed October 25, 2025, [https://coinmarketcap.com/currencies/ethena-staked-usde/](https://coinmarketcap.com/currencies/ethena-staked-usde/)  
7. Ethena's USDe Explained: No Terra-Luna, but Major Risks Exist \- Medium, accessed October 25, 2025, [https://medium.com/thecapital/ethenas-usde-explained-no-terra-luna-but-major-risks-exist-1ca01e67da86](https://medium.com/thecapital/ethenas-usde-explained-no-terra-luna-but-major-risks-exist-1ca01e67da86)  
8. FAQ \- Ethena Docs, accessed October 25, 2025, [https://docs.ethena.fi/resources/faq](https://docs.ethena.fi/resources/faq)  
9. ethena-labs/bbp-public-assets \- GitHub, accessed October 25, 2025, [https://github.com/ethena-labs/bbp-public-assets](https://github.com/ethena-labs/bbp-public-assets)  
10. Risks for Synthetic Stablecoins Ethena Labs USDe Case Study ..., accessed October 25, 2025, [https://www.chainargos.com/risks-for-synthetic-stablecoins-ethena-labs-usde-case-study/](https://www.chainargos.com/risks-for-synthetic-stablecoins-ethena-labs-usde-case-study/)  
11. Ethena and USDe: Revolutionizing the Stablecoin Landscape? \- CryptoEQ, accessed October 25, 2025, [https://www.cryptoeq.io/articles/ethena-usde](https://www.cryptoeq.io/articles/ethena-usde)  
12. Ethena Labs: Improving Potential Airdrop Eligibility Through Shards ..., accessed October 25, 2025, [https://www.coingecko.com/learn/ethena-labs-airdrop-shard-campaign](https://www.coingecko.com/learn/ethena-labs-airdrop-shard-campaign)  
13. What is the Ethena Shard Campaign? How can I earn Shards? \- BitKan.com, accessed October 25, 2025, [https://bitkan.com/learn/what-is-the-ethena-shard-campaign-how-can-i-earn-shards-24253](https://bitkan.com/learn/what-is-the-ethena-shard-campaign-how-can-i-earn-shards-24253)  
14. Ethena Season 1 Airdrop: Case Study \- One Click Labs, accessed October 25, 2025, [https://www.oneclick.fi/blog/ethena-season-1-airdrop-case-study](https://www.oneclick.fi/blog/ethena-season-1-airdrop-case-study)  
15. Ethena Liquid Leveraging on Aave in one transaction | DeFi Saver Knowledge Base, accessed October 25, 2025, [https://help.defisaver.com/protocols/aave/ethena-liquid-leveraging-on-aave-in-one-transaction](https://help.defisaver.com/protocols/aave/ethena-liquid-leveraging-on-aave-in-one-transaction)  
16. What Is Ethena Liquid Leverage? How Do You Use It? \- BitKan.com, accessed October 25, 2025, [https://bitkan.com/learn/what-is-ethena-liquid-leverage-how-do-you-use-it-61621](https://bitkan.com/learn/what-is-ethena-liquid-leverage-how-do-you-use-it-61621)  
17. USDe on Ethereum V3 | Aavescan, accessed October 25, 2025, [https://aavescan.com/ethereum-v3/usde](https://aavescan.com/ethereum-v3/usde)  
18. sUSDe on Ethereum V3 | Aavescan, accessed October 25, 2025, [https://aavescan.com/ethereum-v3/susde](https://aavescan.com/ethereum-v3/susde)  
19. Aave \- Open Source Liquidity Protocol, accessed October 25, 2025, [https://app.aave.com/](https://app.aave.com/)  
20. Interest rates in decentralised finance \- Banque de France, accessed October 25, 2025, [https://www.banque-france.fr/system/files/2024-04/Billet\_352\_EN.pdf](https://www.banque-france.fr/system/files/2024-04/Billet_352_EN.pdf)  
21. Aave Interest Rate Model Explained \- Krayon, accessed October 25, 2025, [https://www.krayondigital.com/blog/aave-interest-rate-model-explained](https://www.krayondigital.com/blog/aave-interest-rate-model-explained)  
22. Liquidity \- | Aave Protocol Documentation, accessed October 25, 2025, [https://aave.com/docs/developers/liquidations](https://aave.com/docs/developers/liquidations)  
23. Health Factor & Liquidations \- Aave, accessed October 25, 2025, [https://aave.com/help/borrowing/liquidations](https://aave.com/help/borrowing/liquidations)  
24. Open Source Liquidity Protocol \- Aave, accessed October 25, 2025, [https://app.aave.com/reserve-overview/?underlyingAsset=0x9d39a5de30e57443bff2a8307a4256c8797a3497\&marketName=proto\_mainnet\_v3](https://app.aave.com/reserve-overview/?underlyingAsset=0x9d39a5de30e57443bff2a8307a4256c8797a3497&marketName=proto_mainnet_v3)  
25. Aave Protocol Parameter Dashboard, accessed October 25, 2025, [https://aave.com/docs/resources/parameters](https://aave.com/docs/resources/parameters)  
26. Onboard USDe Aave V3 Ethereum, accessed October 25, 2025, [https://app.aave.com/governance/v3/proposal/?proposalId=113](https://app.aave.com/governance/v3/proposal/?proposalId=113)  
27. Efficiency Mode (E-mode) \- Aave, accessed October 25, 2025, [https://aave.com/help/borrowing/e-mode](https://aave.com/help/borrowing/e-mode)  
28. sUSDe and USDe Price Feed Update \- Aave, accessed October 25, 2025, [https://app.aave.com/governance/v3/proposal/?proposalId=262](https://app.aave.com/governance/v3/proposal/?proposalId=262)  
29. Pendle Settles $69.8 Billion in Yield Bridging the $140T Fixed Income Market to Crypto, accessed October 25, 2025, [https://www.tradingview.com/news/chainwire:7cf90ef16094b:0-pendle-settles-69-8-billion-in-yield-bridging-the-140t-fixed-income-market-to-crypto/](https://www.tradingview.com/news/chainwire:7cf90ef16094b:0-pendle-settles-69-8-billion-in-yield-bridging-the-140t-fixed-income-market-to-crypto/)  
30. What is Pendle Finance? Yield Tokenization Explained & How to Earn | Nansen, accessed October 25, 2025, [https://www.nansen.ai/post/what-is-pendle-finance-yield-tokenization-explained-how-to-earn](https://www.nansen.ai/post/what-is-pendle-finance-yield-tokenization-explained-how-to-earn)  
31. PENDLE — A Comprehensive Crypto Yield Market Analysis \- DataDrivenInvestor, accessed October 25, 2025, [https://medium.datadriveninvestor.com/pendle-a-comprehensive-crypto-yield-market-analysis-83311b5be8e6](https://medium.datadriveninvestor.com/pendle-a-comprehensive-crypto-yield-market-analysis-83311b5be8e6)  
32. Glossary | Pendle Documentation, accessed October 25, 2025, [https://docs.pendle.finance/ProtocolMechanics/Glossary/](https://docs.pendle.finance/ProtocolMechanics/Glossary/)  
33. What is Pendle Finance and How Does It Work? | by Slobodzeanb | Satoshi Club \- Medium, accessed October 25, 2025, [https://medium.com/realsatoshiclub/what-is-pendle-finance-and-how-does-it-work-98c16d80cf14](https://medium.com/realsatoshiclub/what-is-pendle-finance-and-how-does-it-work-98c16d80cf14)  
34. Pendle \- Liberating Yield, accessed October 25, 2025, [https://www.pendle.finance/](https://www.pendle.finance/)  
35. Pendle YT Leverage Points Strategy: High Returns and Risk An | 陈小艺 on Binance Square, accessed October 25, 2025, [https://www.binance.com/en/square/post/24757307371234](https://www.binance.com/en/square/post/24757307371234)  
36. Plasma: Taking Aim at a Trillion Dollar Opportunity \- Delphi Digital, accessed October 25, 2025, [https://members.delphidigital.io/reports/plasma-taking-aim-at-a-trillion-dollar-opportunity](https://members.delphidigital.io/reports/plasma-taking-aim-at-a-trillion-dollar-opportunity)  
37. Delphi Digital Research Report: Plasma, Targeting Trillion-Dollar Market Opportunities | Bitget News, accessed October 25, 2025, [https://www.bitget.com/news/detail/12560604984675](https://www.bitget.com/news/detail/12560604984675)  
38. What is Plasma (XPL)| How To Get & Use Plasma | Bitget, accessed October 25, 2025, [https://www.bitget.com/price/plasma/what-is](https://www.bitget.com/price/plasma/what-is)  
39. What Is Plasma (XPL) And How Does It Work? \- CoinMarketCap, accessed October 25, 2025, [https://coinmarketcap.com/cmc-ai/plasma-xpl/what-is/](https://coinmarketcap.com/cmc-ai/plasma-xpl/what-is/)  
40. Revolutionizing Global Finance: How Plasma is Set to Unleash the True Power of Stablecoins | Aesthetic\_Meow on Binance Square, accessed October 25, 2025, [https://www.binance.com/en/square/post/30196757215289](https://www.binance.com/en/square/post/30196757215289)  
41. Plasma Mainnet Beta Launches with Ethena at Its Core \- CoinCentral, accessed October 25, 2025, [https://coincentral.com/plasma-mainnet-beta-launches-with-ethena-at-its-core/](https://coincentral.com/plasma-mainnet-beta-launches-with-ethena-at-its-core/)  
42. $2B TVL and No Backlash \- How Plasma Defied the Odds, accessed October 25, 2025, [https://thedefiant.io/newsletter/defi-daily/2b-tvl-and-no-backlash-how-plasma-defied-the-odds](https://thedefiant.io/newsletter/defi-daily/2b-tvl-and-no-backlash-how-plasma-defied-the-odds)  
43. Ethena Labs' USDe and sUSDe PT Tokens Listed on Aave Plasma with $200M Supply Each, accessed October 25, 2025, [https://www.kucoin.com/news/flash/ethena-labs-usde-and-susde-pt-tokens-listed-on-aave-plasma-with-200m-supply-each](https://www.kucoin.com/news/flash/ethena-labs-usde-and-susde-pt-tokens-listed-on-aave-plasma-with-200m-supply-each)  
44. Ethena Labs Lists USDe and sUSDe PT Tokens on Aave Plasma | Phemex News, accessed October 25, 2025, [https://phemex.com/news/article/ethena-labs-lists-usde-and-susde-pt-tokens-on-aave-plasma-28283](https://phemex.com/news/article/ethena-labs-lists-usde-and-susde-pt-tokens-on-aave-plasma-28283)  
45. Pendle Finance Launches 'Plasma Parade' with 600,000 XPL Rew | Phemex News, accessed October 25, 2025, [https://phemex.com/news/article/pendle-finance-unveils-plasma-parade-with-600000-xpl-rewards-25344](https://phemex.com/news/article/pendle-finance-unveils-plasma-parade-with-600000-xpl-rewards-25344)  
46. $PENDLE Finance launches the exclusive reward event "Plasma | Crypto阿贵链讯 on Binance Square, accessed October 25, 2025, [https://www.binance.com/en/square/post/30810080453513](https://www.binance.com/en/square/post/30810080453513)  
47. Pendle Finance Launches Two-Week 'Plasma Parade' Reward Campaign with Up to 600,000 XPL Tokens \- KuCoin, accessed October 25, 2025, [https://www.kucoin.com/news/flash/pendle-finance-launches-two-week-plasma-parade-reward-campaign-with-up-to-600-000-xpl-tokens](https://www.kucoin.com/news/flash/pendle-finance-launches-two-week-plasma-parade-reward-campaign-with-up-to-600-000-xpl-tokens)  
48. How to Bridge to Plasma Chain \- Datawallet, accessed October 25, 2025, [https://www.datawallet.com/crypto/bridge-to-plasma](https://www.datawallet.com/crypto/bridge-to-plasma)  
49. Bridge to Plasma Network in 7 Minutes\! | Zero-Fee USDT Transfers Explained \- YouTube, accessed October 25, 2025, [https://www.youtube.com/watch?v=J9RxG8SsZ8s](https://www.youtube.com/watch?v=J9RxG8SsZ8s)  
50. Ethena's USDe, a breakthrough or a potential risk ? \- Smart-Chain, accessed October 25, 2025, [https://blog.smart-chain.fr/articles/ethenas-usde-a-breakthrough-or-a-potential-risk](https://blog.smart-chain.fr/articles/ethenas-usde-a-breakthrough-or-a-potential-risk)  
51. Custody You Can Trust: Securely Supporting USDtb, accessed October 25, 2025, [https://zodia-custody.com/custody-you-can-trust-securely-supporting-usdtb/](https://zodia-custody.com/custody-you-can-trust-securely-supporting-usdtb/)  
52. Ethena (ENA): A Deep Dive into the Ecosystem | OAK Research, accessed October 25, 2025, [https://oakresearch.io/en/analyses/fundamentals/ethena-ena-deep-dive-into-ecosystem](https://oakresearch.io/en/analyses/fundamentals/ethena-ena-deep-dive-into-ecosystem)  
53. Ethena selects Coinbase Prime for multi-product agreement, accessed October 25, 2025, [https://www.coinbase.com/blog/coinbase-prime-multi-product-agreement](https://www.coinbase.com/blog/coinbase-prime-multi-product-agreement)  
54. What Are the Main Custody Risks in Crypto Investing \- Safeheron, accessed October 25, 2025, [https://safeheron.com/blog/main-custody-risk-crypto-investing-key-risks-protection/](https://safeheron.com/blog/main-custody-risk-crypto-investing-key-risks-protection/)  
55. Digital asset risk disclosure \- Zodia Custody, accessed October 25, 2025, [https://zodia-custody.com/digital-asset-risk-disclosures/](https://zodia-custody.com/digital-asset-risk-disclosures/)  
56. Audits | Ethena, accessed October 25, 2025, [https://docs.ethena.fi/resources/audits](https://docs.ethena.fi/resources/audits)  
57. Ethena Bug Bounties | Immunefi, accessed October 25, 2025, [https://immunefi.com/bug-bounty/ethena/](https://immunefi.com/bug-bounty/ethena/)