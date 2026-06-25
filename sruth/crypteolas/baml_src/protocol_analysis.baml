// Protocol Analysis Schemas for Crypteolas
// DeFi analytics, yield strategies, TVL analysis, and market research

// Import shared types from crypto_extraction
// Note: In production, use BAML imports

// ============================================================
// Enums
// ============================================================

enum MarketCondition {
  BULL @description("Strong upward momentum")
  BEAR @description("Strong downward momentum")
  SIDEWAYS @description("Range-bound trading")
  VOLATILE @description("High volatility, uncertain direction")
  RECOVERY @description("Recovering from downturn")
}

enum YieldStrategy {
  LENDING @description("Supply assets to earn interest")
  LIQUIDITY_PROVISION @description("Provide liquidity to AMMs")
  STAKING @description("Stake tokens for rewards")
  YIELD_FARMING @description("Farm governance tokens")
  DELTA_NEUTRAL @description("Hedge directional exposure")
  ARBITRAGE @description("Cross-platform arbitrage")
  OPTIONS @description("Options-based yield strategies")
  RESTAKING @description("Restake LST/LRT tokens")
  POINTS @description("Farm protocol points for airdrop")
}

enum RiskLevel {
  MINIMAL @description("Blue-chip, battle-tested")
  LOW @description("Established protocols, audited")
  MEDIUM @description("Newer protocols with audits")
  HIGH @description("Experimental, limited audits")
  EXTREME @description("Unaudited, high complexity")
}

enum MetricTimeframe {
  HOUR_1
  HOUR_24
  DAY_7
  DAY_30
  DAY_90
  YEAR_1
  ALL_TIME
}

// ============================================================
// TVL & Protocol Metrics
// ============================================================

class ProtocolMetrics {
  protocol_name string
  category string
  chains string[]

  tvl TVLMetrics
  volume VolumeMetrics?
  users UserMetrics?
  revenue RevenueMetrics?

  token_metrics TokenMetrics?
  yield_opportunities YieldOpportunity[]

  health_score float @description("0-100 composite score")
  trend string @description("Growing, Stable, Declining")
  analysis string
}

class TVLMetrics {
  current_tvl_usd float
  tvl_change_24h float @description("Percentage change")
  tvl_change_7d float
  tvl_change_30d float

  tvl_by_chain ChainTVL[]
  tvl_by_pool PoolTVL[]

  peak_tvl float
  peak_tvl_date string
  tvl_rank int? @description("Rank in category")
}

class ChainTVL {
  chain string
  tvl_usd float
  percentage float
}

class PoolTVL {
  pool_name string
  tvl_usd float
  apy float?
  token_composition string[]
}

class VolumeMetrics {
  volume_24h float
  volume_7d float
  volume_30d float

  volume_change_24h float
  volume_to_tvl_ratio float @description("Efficiency metric")

  top_pairs VolumeByPair[]
}

class VolumeByPair {
  pair string
  volume_24h float
  fee_tier float?
}

class UserMetrics {
  daily_active_users int
  weekly_active_users int
  monthly_active_users int

  new_users_24h int
  returning_user_rate float

  user_growth_trend string
  geographic_distribution string[]?
}

class RevenueMetrics {
  revenue_24h float
  revenue_7d float
  revenue_30d float
  annualized_revenue float

  revenue_to_tvl_ratio float @description("Revenue efficiency")
  fee_sources FeeSource[]

  treasury_value float?
  runway_months float? @description("Treasury / burn rate")
}

class FeeSource {
  source string
  revenue_24h float
  percentage float
}

class TokenMetrics {
  symbol string
  price_usd float
  market_cap float
  fdv float @description("Fully diluted valuation")

  price_change_24h float
  price_change_7d float
  price_change_30d float

  circulating_supply float
  max_supply float?
  inflation_rate float?

  mcap_to_tvl_ratio float
  mcap_to_revenue_ratio float? @description("P/E-like metric")

  holder_count int?
  top_holders_percentage float? @description("Concentration risk")
}

// ============================================================
// Yield Analysis
// ============================================================

class YieldOpportunity {
  name string
  protocol string
  chain string
  strategy YieldStrategy

  base_apy float
  reward_apy float
  total_apy float

  tvl_usd float
  tokens_required string[]

  risk_level RiskLevel
  risk_factors string[]
  lock_period string?
  minimum_deposit float?

  sustainability_score float @description("0-100, how sustainable is yield")
  impermanent_loss_risk string? @description("For LP positions")

  notes string
}

class YieldComparison {
  opportunities YieldOpportunity[]
  best_risk_adjusted YieldOpportunity
  best_absolute_yield YieldOpportunity
  safest_option YieldOpportunity

  analysis string
  recommendations string[]
  warnings string[]
}

class StrategyAnalysis {
  strategy_name string
  description string
  steps StrategyStep[]

  expected_apy float
  risk_level RiskLevel
  capital_required float
  complexity string @description("Simple, Moderate, Complex")

  risks string[]
  mitigations string[]

  gas_estimate string
  monitoring_requirements string[]

  historical_performance string?
  similar_strategies string[]
}

class StrategyStep {
  step_number int
  action string
  protocol string
  chain string
  details string
  risks string[]
}

// ============================================================
// Market Analysis
// ============================================================

class MarketOverview {
  timestamp string
  condition MarketCondition

  total_crypto_mcap float
  total_defi_tvl float
  btc_dominance float
  eth_dominance float

  sector_performance SectorPerformance[]
  trending_narratives string[]
  risk_indicators RiskIndicator[]

  summary string
  outlook string
}

class SectorPerformance {
  sector string
  tvl float
  tvl_change_7d float
  top_protocols string[]
  momentum string @description("Strong, Moderate, Weak, Negative")
}

class RiskIndicator {
  indicator string
  value float
  interpretation string
  action string?
}

class CompetitorAnalysis {
  protocol string
  competitors ProtocolComparison[]

  market_position string
  competitive_advantages string[]
  competitive_weaknesses string[]

  market_share float
  market_share_trend string

  differentiation_score float @description("0-100, how unique")
  moat_strength string @description("Strong, Moderate, Weak, None")

  threats string[]
  opportunities string[]
}

class ProtocolComparison {
  name string
  tvl float
  market_share float
  apy_range string
  unique_features string[]
  weaknesses string[]
}

// ============================================================
// Research Synthesis
// ============================================================

class ResearchReport {
  protocol_name string
  report_date string
  analyst string?

  executive_summary string

  protocol_overview ProtocolSection
  tokenomics_analysis TokenomicsSection
  competitive_landscape CompetitorAnalysis
  risk_assessment RiskSection
  investment_thesis InvestmentThesis?

  appendix Appendix?
}

class ProtocolSection {
  description string
  mechanics string
  innovations string[]
  use_cases string[]
  adoption_metrics string
}

class TokenomicsSection {
  token_utility string
  supply_dynamics string
  value_accrual string
  distribution_analysis string
  concerns string[]
}

class RiskSection {
  overall_risk RiskLevel
  smart_contract_risk string
  economic_risk string
  governance_risk string
  regulatory_risk string
  key_risks string[]
  mitigating_factors string[]
}

class InvestmentThesis {
  recommendation string @description("Strong Buy, Buy, Hold, Sell, Strong Sell")
  conviction string @description("High, Medium, Low")
  time_horizon string
  bull_case string
  base_case string
  bear_case string
  catalysts string[]
  risks string[]
}

class Appendix {
  data_sources string[]
  methodology string
  disclaimers string[]
}

// ============================================================
// Analysis Functions
// ============================================================

function AnalyzeProtocolMetrics(
  protocol_name: string,
  metrics_data: string,
  timeframe: MetricTimeframe
) -> ProtocolMetrics {
  client CrypteolasDocumentAnalysis
  prompt #"
    Analyze the metrics for {{ protocol_name }} over {{ timeframe }}.

    Metrics Data:
    {{ metrics_data }}

    Provide comprehensive analysis including:
    - TVL trends and composition
    - Volume and user activity
    - Revenue and sustainability
    - Token performance
    - Available yield opportunities
    - Overall health assessment

    Calculate a health score (0-100) based on:
    - TVL stability (25%)
    - User growth (25%)
    - Revenue sustainability (25%)
    - Token performance (25%)

    {{ ctx.output_format }}
  "#
}

function CompareYieldOpportunities(
  opportunities: string,
  risk_tolerance: RiskLevel,
  capital_amount: float
) -> YieldComparison {
  client CrypteolasRiskAssessment
  prompt #"
    Compare these yield opportunities for an investor with {{ risk_tolerance }} risk tolerance
    and ${{ capital_amount }} to deploy.

    Opportunities:
    {{ opportunities }}

    Analyze:
    - Risk-adjusted returns for each
    - Sustainability of yields
    - Capital requirements
    - Lock-up periods
    - Hidden risks

    Recommend the best options based on the risk profile.

    {{ ctx.output_format }}
  "#
}

function DesignYieldStrategy(
  available_capital: float,
  risk_tolerance: RiskLevel,
  preferred_chains: string[],
  time_horizon: string
) -> StrategyAnalysis {
  client CrypteolasRiskAssessment
  prompt #"
    Design an optimal yield strategy for:
    - Capital: ${{ available_capital }}
    - Risk tolerance: {{ risk_tolerance }}
    - Chains: {{ preferred_chains }}
    - Time horizon: {{ time_horizon }}

    Create a detailed strategy including:
    - Step-by-step implementation
    - Expected returns
    - All risks and mitigations
    - Gas cost estimates
    - Monitoring requirements

    {{ ctx.output_format }}
  "#
}

function AnalyzeMarketConditions(
  market_data: string,
  focus_sectors: string[]
) -> MarketOverview {
  client CrypteolasDocumentAnalysis
  prompt #"
    Analyze current DeFi market conditions.

    Market Data:
    {{ market_data }}

    Focus Sectors: {{ focus_sectors }}

    Provide:
    - Current market condition classification
    - Sector performance breakdown
    - Key risk indicators
    - Trending narratives
    - Short-term outlook

    {{ ctx.output_format }}
  "#
}

function GenerateResearchReport(
  protocol_name: string,
  documentation: string,
  metrics: string,
  audit_summary: string?
) -> ResearchReport {
  client CrypteolasClaude
  prompt #"
    Generate a comprehensive research report for {{ protocol_name }}.

    Documentation:
    {{ documentation }}

    Metrics:
    {{ metrics }}

    {% if audit_summary %}
    Audit Summary:
    {{ audit_summary }}
    {% endif %}

    Create a professional research report covering:
    - Executive summary
    - Protocol mechanics and innovations
    - Tokenomics analysis
    - Competitive positioning
    - Risk assessment
    - Investment thesis (if applicable)

    Be objective and highlight both opportunities and risks.

    {{ ctx.output_format }}
  "#
}

function AnalyzeOnChainData(
  wallet_data: string,
  protocol: string,
  analysis_type: string
) -> OnChainAnalysis {
  client CrypteolasFastExtraction
  prompt #"
    Analyze this on-chain data for {{ protocol }}.

    Data:
    {{ wallet_data }}

    Analysis Type: {{ analysis_type }}

    Extract insights about:
    - Whale activity patterns
    - Smart money movements
    - Accumulation/distribution signals
    - Unusual activity

    {{ ctx.output_format }}
  "#
}

class OnChainAnalysis {
  protocol string
  analysis_type string
  timeframe string

  key_findings string[]
  whale_activity WhaleSummary
  smart_money_flows string[]
  signals Signal[]

  interpretation string
  recommended_actions string[]
}

class WhaleSummary {
  total_whale_addresses int
  net_flow_24h float @description("Positive = accumulation")
  largest_transactions Transaction[]
  notable_wallets string[]
}

class Transaction {
  hash string
  from_label string?
  to_label string?
  amount float
  token string
  timestamp string
  significance string
}

class Signal {
  signal_type string @description("Bullish, Bearish, Neutral")
  indicator string
  strength string @description("Strong, Moderate, Weak")
  description string
}

function SummarizeProtocolNews(
  news_items: string[],
  protocol: string
) -> NewsSummary {
  client CrypteolasFastExtraction
  prompt #"
    Summarize recent news and developments for {{ protocol }}.

    News Items:
    {% for item in news_items %}
    - {{ item }}
    {% endfor %}

    Provide:
    - Key developments summary
    - Sentiment analysis
    - Potential price impact
    - Action items

    {{ ctx.output_format }}
  "#
}

class NewsSummary {
  protocol string
  period string

  highlights string[]
  sentiment string @description("Positive, Neutral, Negative, Mixed")
  sentiment_score float @description("-1 to 1")

  key_developments Development[]
  potential_catalysts string[]
  concerns string[]

  market_impact string
  recommended_actions string[]
}

class Development {
  title string
  category string @description("Partnership, Product, Governance, etc.")
  significance string @description("High, Medium, Low")
  summary string
  source string
}
