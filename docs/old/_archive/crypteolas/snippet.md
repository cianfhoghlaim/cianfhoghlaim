## Portfolio Allocation Proposal
- 40% Plasma Liquid Leverage (high APY, incentives)
- 30% Aave Looping (stable leverage, points)
- 20% Pendle PT-USDe (fixed yield security)
- 10% Binance Earn (low-risk baseline)

Justification: Balances 22%+ APY in Plasma with liquidation risks via diversification; fixed yields hedge volatility; Binance adds stability. Risk/reward: High-yield leveraged (Plasma/Aave) offset by conservative fixed/earn allocations.

## Detailed Strategy Execution Plan

### Plasma Liquid Leverage
1. Bridge USDe/sUSDe to Plasma via Stargate or Plasma UI (5-10 min, ~$1-5 gas).
2. Deposit 50% USDe/50% sUSDe on Aave Plasma.
3. Borrow USDT at ~2-3% rate.
4. Swap borrowed USDT to USDe on Curve/Balancer.
5. Redeposit for 10x loop (target 22%+ APY).
Gas: ~$10-20 total.

### Aave Looping
1. Deposit 50% USDe/50% sUSDe on Aave Ethereum.
2. Enable e-mode, borrow USDC/USDT at 2% rate.
3. Swap to USDe, redeposit for 5-7x leverage (~12% APY).
Gas: ~$50-100.

### Pendle PT-USDe
1. Buy PT-USDe on Pendle (e.g., Nov 2025 maturity at 8-11% fixed APY).
2. Hold to maturity or sell if yields drop.
Gas: ~$20-30.

### Binance Earn
1. Deposit USDe on Binance.
2. Hold for 12% APR (until Oct 21, 2025; then 8%).
No gas; CEX.

## Risk Management Protocol

### Liquidation Risk
LTV: 92% Plasma, 80% Aave. Monitor health factor >1.2 via Zerion alerts. Emergency: Unloop by repaying borrows, withdraw.

### Smart Contract Risk
Ethena/Aave/Plasma audited (Zellic, Trail of Bits). High reputation; diversify protocols.

### Yield Volatility
Factors: Funding rates, borrow demand. Mitigate: Rebalance if APY <10%.

### Peg Risk
USDe overcollateralized (101%), delta-neutral stable historically. No major depegs in 2025.

## Monitoring and Exit Strategy
Metrics: Daily APY, health factor, cap utilization via DeFi Llama/Dune. Tools: Zapper/Zerion, protocol dashboards.
Triggers: APY drop >20%, health <1.1, better yields elsewhere.
Exit: Unloop by repay/swap/withdraw; bridge back via Stargate; sell Pendle PT/YT.

## Yield Analysis

### Stablecoin Yield
Base sUSDe: 5.5-8% minus borrow costs (2-3%) = net 3-6%. Looped: 12-22%.

### Volatile Asset Yield
Ethena points (ENA airdrop est. 5-10% value), XPL tokens (~5% APY), liquid but volatile; sell on DEX for USDe.
