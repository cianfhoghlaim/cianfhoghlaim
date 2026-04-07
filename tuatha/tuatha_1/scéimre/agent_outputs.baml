// agent_outputs.baml
// BAML schemas for structured agent responses

// ============================================================================
// MARKET ANALYSIS OUTPUTS
// ============================================================================

enum TrendDirection {
  StrongBullish @description("Clear upward momentum with volume confirmation")
  Bullish @description("Positive price action")
  Neutral @description("Sideways consolidation")
  Bearish @description("Negative price action")
  StrongBearish @description("Clear downward momentum with volume confirmation")
}

enum TimeHorizon {
  ShortTerm @description("Hours to days")
  MediumTerm @description("Days to weeks")
  LongTerm @description("Weeks to months")
}

class PriceLevel {
  level float
  significance string        // "support", "resistance", "pivot"
  strength string            // "weak", "moderate", "strong"
  notes string?
}

class MarketAnalysis {
  symbol string
  current_price float
  analysis_timestamp string

  trend TrendDirection
  trend_timeframe TimeHorizon

  key_levels PriceLevel[]

  bullish_factors string[]
  bearish_factors string[]

  volume_assessment string?
  sentiment_assessment string?

  short_term_outlook string
  medium_term_outlook string?

  risk_reward_ratio float?
  confidence_level string      // "low", "medium", "high"
}

function AnalyzeMarket(
  symbol: string,
  price_data: string,
  market_context: string
) -> MarketAnalysis {
  client Claude
  prompt #"
    Provide a structured market analysis for {{ symbol }}.

    Price Data:
    {{ price_data }}

    Market Context:
    {{ market_context }}

    Analyze:
    1. Current trend and direction
    2. Key support and resistance levels
    3. Bullish and bearish factors
    4. Volume and sentiment
    5. Short and medium-term outlook

    Be specific with price levels and provide reasoning.

    {{ ctx.output_format }}
  "#
}

// ============================================================================
// DEFI STRATEGY OUTPUTS
// ============================================================================

enum RiskLevel {
  Conservative @description("Capital preservation focus, low APY")
  Moderate @description("Balanced risk/reward")
  Aggressive @description("Higher yield, higher risk")
  Degen @description("Maximum risk exposure")
}

enum StrategyType {
  Staking @description("Single-asset staking")
  LiquidityProvision @description("LP positions")
  Lending @description("Supply assets for yield")
  Borrowing @description("Leverage strategies")
  YieldFarming @description("Multi-protocol farming")
  Arbitrage @description("Cross-venue arbitrage")
  DeltaNeutral @description("Hedged positions")
}

class ProtocolAllocation {
  protocol string
  chain string
  allocation_percent float
  expected_apy float
  strategy_type StrategyType

  entry_instructions string[]
  exit_instructions string[]

  risks string[]
  dependencies string[]        // Other protocols/positions this depends on
}

class DeFiStrategy {
  strategy_name string
  risk_level RiskLevel

  target_apy float
  apy_range_low float
  apy_range_high float

  capital_required string
  recommended_timeframe TimeHorizon

  strategy_description string

  allocations ProtocolAllocation[]

  total_gas_estimate string?
  rebalancing_frequency string?

  key_risks string[]
  risk_mitigation string[]

  monitoring_checklist string[]
  exit_triggers string[]
}

function GenerateDeFiStrategy(
  capital_amount: string,
  risk_tolerance: string,
  preferred_chains: string,
  goals: string
) -> DeFiStrategy {
  client Claude
  prompt #"
    Generate a DeFi yield strategy based on these parameters:

    Capital: {{ capital_amount }}
    Risk Tolerance: {{ risk_tolerance }}
    Preferred Chains: {{ preferred_chains }}
    Goals: {{ goals }}

    Create a comprehensive strategy with:
    1. Protocol allocations with specific percentages
    2. Step-by-step entry and exit instructions
    3. Expected APY ranges (be realistic)
    4. Risk assessment and mitigation
    5. Monitoring and exit triggers

    Focus on battle-tested protocols. Include gas estimates.

    {{ ctx.output_format }}
  "#
}

// ============================================================================
// PORTFOLIO ANALYSIS OUTPUTS
// ============================================================================

class PositionAnalysis {
  asset string
  current_value string
  portfolio_weight float

  unrealized_pnl string?
  unrealized_pnl_percent float?

  risk_contribution string     // "low", "medium", "high"
  correlation_note string?

  recommendation string        // "hold", "increase", "decrease", "exit"
  reasoning string
}

class PortfolioMetrics {
  total_value string
  total_pnl string
  total_pnl_percent float

  diversification_score float  // 0-100
  risk_score float             // 0-100

  largest_position string
  largest_position_weight float

  chain_exposure map<string, float>
  sector_exposure map<string, float>
}

class PortfolioAnalysis {
  analysis_date string

  metrics PortfolioMetrics
  positions PositionAnalysis[]

  strengths string[]
  weaknesses string[]

  rebalancing_suggestions string[]

  risk_warnings string[]
  opportunities string[]

  overall_assessment string
}

function AnalyzePortfolio(
  holdings: string,
  market_conditions: string
) -> PortfolioAnalysis {
  client Claude
  prompt #"
    Analyze this cryptocurrency portfolio:

    Holdings:
    {{ holdings }}

    Current Market Conditions:
    {{ market_conditions }}

    Provide:
    1. Portfolio metrics (diversification, risk scores)
    2. Per-position analysis with recommendations
    3. Strengths and weaknesses
    4. Rebalancing suggestions
    5. Risk warnings and opportunities

    Be specific and actionable in recommendations.

    {{ ctx.output_format }}
  "#
}

// ============================================================================
// SMART CONTRACT REVIEW OUTPUTS
// ============================================================================

enum CodeQuality {
  Excellent @description("Well-structured, documented, follows best practices")
  Good @description("Minor improvements possible")
  Acceptable @description("Functional but could be improved")
  Poor @description("Significant issues present")
  Critical @description("Should not be deployed")
}

class SecurityIssue {
  title string
  severity string              // "Critical", "High", "Medium", "Low", "Info"
  location string?
  description string
  recommendation string
  code_snippet string?
}

class GasOptimization {
  location string
  current_pattern string
  suggested_pattern string
  estimated_savings string
}

class ContractReview {
  contract_name string
  contract_type string         // "ERC20", "ERC721", "DEX", "Lending", etc.

  code_quality CodeQuality

  functionality_summary string

  security_issues SecurityIssue[]
  gas_optimizations GasOptimization[]

  external_dependencies string[]
  upgrade_pattern string?      // "Immutable", "Proxy", "Diamond", etc.

  access_control_assessment string
  reentrancy_assessment string
  oracle_dependency_assessment string?

  overall_risk_assessment string
  deployment_recommendation string
}

function ReviewSmartContract(
  contract_code: string,
  contract_context: string?
) -> ContractReview {
  client Claude
  prompt #"
    Review this smart contract for security and quality:

    Code:
    {{ contract_code }}

    {% if contract_context %}
    Context:
    {{ contract_context }}
    {% endif %}

    Analyze:
    1. Security vulnerabilities (reentrancy, overflow, access control)
    2. Gas optimization opportunities
    3. Code quality and best practices
    4. External dependencies and risks
    5. Overall risk assessment

    Provide specific line references where possible.

    {{ ctx.output_format }}
  "#
}

// ============================================================================
// RESEARCH SUMMARY OUTPUTS
// ============================================================================

class ResearchSource {
  title string
  url string?
  type string                  // "whitepaper", "blog", "twitter", "docs", "audit"
  relevance string             // "primary", "supporting", "background"
}

class KeyInsight {
  insight string
  confidence string            // "high", "medium", "low"
  source string?
  implications string?
}

class ResearchSummary {
  topic string
  research_date string

  executive_summary string     // 2-3 paragraphs

  key_insights KeyInsight[]

  bullish_thesis string?
  bearish_thesis string?

  key_metrics map<string, string>

  risks_and_concerns string[]
  catalysts string[]

  comparable_projects string[]
  competitive_position string?

  sources ResearchSource[]

  investment_thesis string?
  recommendation string?
}

function GenerateResearchSummary(
  topic: string,
  research_materials: string
) -> ResearchSummary {
  client Claude
  prompt #"
    Generate a comprehensive research summary on: {{ topic }}

    Research Materials:
    {{ research_materials }}

    Create a structured summary including:
    1. Executive summary (2-3 paragraphs)
    2. Key insights with confidence levels
    3. Bull and bear cases
    4. Key metrics
    5. Risks and catalysts
    6. Competitive analysis
    7. Investment thesis

    Cite sources where applicable. Be objective.

    {{ ctx.output_format }}
  "#
}

// ============================================================================
// TRADE EXECUTION OUTPUTS
// ============================================================================

enum TradeAction {
  Buy @description("Enter long position")
  Sell @description("Exit position or short")
  Swap @description("Exchange one asset for another")
  AddLiquidity @description("Provide LP")
  RemoveLiquidity @description("Withdraw LP")
}

class TradeExecution {
  action TradeAction

  input_token string
  input_amount string

  output_token string
  expected_output string
  minimum_output string        // With slippage

  slippage_tolerance float

  route_description string     // "ETH -> USDC via Uniswap V3"

  estimated_gas string
  estimated_gas_usd string?

  price_impact float?

  execution_deadline string?

  warnings string[]
  confirmations_required string[]
}

function PlanTradeExecution(
  intent: string,
  portfolio_context: string,
  market_conditions: string
) -> TradeExecution {
  client Claude
  prompt #"
    Plan a trade execution based on this intent:

    Intent: {{ intent }}

    Portfolio Context:
    {{ portfolio_context }}

    Market Conditions:
    {{ market_conditions }}

    Provide:
    1. Specific action and amounts
    2. Optimal route with reasoning
    3. Slippage and gas estimates
    4. Price impact assessment
    5. Warnings and required confirmations

    Be conservative with slippage. Flag any concerns.

    {{ ctx.output_format }}
  "#
}
