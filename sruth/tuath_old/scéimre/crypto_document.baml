// crypto_document.baml
// BAML schemas for extracting structured data from crypto documents

// ============================================================================
// WHITEPAPER EXTRACTION
// ============================================================================

class TeamMember {
  name string
  role string?
  linkedin string?
  twitter string?
  background string?
}

class Tokenomics {
  token_name string?
  token_symbol string?
  total_supply string?
  initial_distribution string?
  vesting_schedule string?
  inflation_rate string?
  burn_mechanism string?
}

class TechnologyStack {
  blockchain string?               // "Ethereum", "Solana", "Custom L1"
  consensus_mechanism string?      // "PoS", "PoW", "DPoS"
  smart_contract_language string?  // "Solidity", "Rust", "Move"
  scaling_solution string?         // "Rollup", "Sidechain", "Sharding"
  key_innovations string[]
}

class WhitepaperExtraction {
  project_name string
  tagline string?
  problem_statement string?
  solution_overview string?

  team TeamMember[]
  tokenomics Tokenomics?
  technology TechnologyStack?

  use_cases string[]
  competitive_advantages string[]
  risks_and_challenges string[]

  roadmap_items string[]
  partnerships string[]

  publication_date string?
  version string?
}

function ExtractWhitepaper(document: pdf) -> WhitepaperExtraction {
  client Claude
  prompt #"
    Extract structured information from this cryptocurrency whitepaper.

    Focus on:
    1. Project fundamentals (name, problem, solution)
    2. Team information (founders, advisors, key members)
    3. Tokenomics (supply, distribution, utility)
    4. Technology (blockchain, consensus, innovations)
    5. Use cases and competitive advantages
    6. Roadmap and partnerships

    Be thorough but concise. Extract actual values, not placeholders.
    If information is not present, omit the field.

    Document:
    {{ document }}

    {{ ctx.output_format }}
  "#
}

// ============================================================================
// AUDIT REPORT EXTRACTION
// ============================================================================

enum Severity {
  Critical @description("Immediate exploitation risk, funds at risk")
  High @description("Significant vulnerability, should fix before launch")
  Medium @description("Notable issue, recommend fixing")
  Low @description("Minor issue, best practice")
  Informational @description("Suggestion or observation")
}

enum FindingStatus {
  Open @description("Not yet addressed")
  Acknowledged @description("Team aware, decision pending")
  Resolved @description("Fixed in code")
  Mitigated @description("Risk reduced but not eliminated")
  WontFix @description("Accepted risk")
}

class AuditFinding {
  id string?
  title string
  severity Severity
  status FindingStatus?

  description string
  location string?              // Contract/function/line
  recommendation string?
  team_response string?
}

class AuditSummary {
  overall_risk string           // "Low", "Medium", "High", "Critical"
  total_findings int
  critical_count int
  high_count int
  medium_count int
  low_count int
  informational_count int
}

class AuditReportExtraction {
  project_name string
  auditor_name string
  audit_date string?
  audit_version string?

  contracts_audited string[]
  scope_description string?
  methodology string?

  summary AuditSummary
  findings AuditFinding[]

  executive_summary string?
  conclusion string?

  is_recommended_for_deployment bool?
}

function ExtractAuditReport(document: pdf) -> AuditReportExtraction {
  client Claude
  prompt #"
    Extract structured information from this smart contract security audit report.

    Focus on:
    1. Audit metadata (project, auditor, date, scope)
    2. Summary statistics (finding counts by severity)
    3. Individual findings (title, severity, description, status)
    4. Overall assessment and recommendation

    For each finding, extract:
    - Severity level (Critical, High, Medium, Low, Informational)
    - Current status if mentioned
    - Location in code if specified
    - Recommendation and team response if available

    Document:
    {{ document }}

    {{ ctx.output_format }}
  "#
}

// ============================================================================
// NEWS ARTICLE EXTRACTION
// ============================================================================

enum SentimentLevel {
  ExtremeFear @description("Panic, capitulation signals")
  Fear @description("Negative outlook, concern")
  Neutral @description("Balanced or factual reporting")
  Greed @description("Positive outlook, optimism")
  ExtremeGreed @description("Euphoria, FOMO signals")
}

enum ArticleType {
  News @description("Breaking news or current events")
  Analysis @description("In-depth analysis or research")
  Opinion @description("Editorial or opinion piece")
  Tutorial @description("Educational or how-to content")
  Announcement @description("Official project announcement")
  Interview @description("Interview or Q&A")
}

class MentionedEntity {
  name string
  type string              // "token", "protocol", "person", "company", "exchange"
  sentiment string?        // "positive", "negative", "neutral"
  context string?
}

class NewsArticleExtraction {
  title string
  publication string?
  author string?
  publish_date string?

  article_type ArticleType
  sentiment SentimentLevel

  summary string           // 2-3 sentence summary
  key_points string[]

  mentioned_entities MentionedEntity[]
  mentioned_tokens string[]
  mentioned_protocols string[]

  price_predictions string[]   // Any specific price targets mentioned
  event_dates string[]         // Any future dates mentioned

  regulatory_implications string?
  market_impact_assessment string?
}

function ExtractNewsArticle(content: string) -> NewsArticleExtraction {
  client Claude
  prompt #"
    Extract structured information from this cryptocurrency news article.

    Analyze:
    1. Article metadata and type
    2. Overall sentiment (Fear/Greed scale)
    3. Key points and summary
    4. Mentioned entities (tokens, protocols, people, companies)
    5. Any price predictions or future event dates
    6. Regulatory or market impact implications

    Be objective in sentiment assessment. Focus on factual extraction.

    Article:
    {{ content }}

    {{ ctx.output_format }}
  "#
}

// ============================================================================
// GOVERNANCE PROPOSAL EXTRACTION
// ============================================================================

enum ProposalStatus {
  Draft @description("Not yet submitted")
  Active @description("Currently voting")
  Passed @description("Approved by governance")
  Rejected @description("Did not reach threshold")
  Executed @description("Implemented on-chain")
  Cancelled @description("Withdrawn by author")
}

class VoteBreakdown {
  for_votes string?
  against_votes string?
  abstain_votes string?
  quorum_reached bool?
  participation_rate string?
}

class GovernanceProposalExtraction {
  proposal_id string?
  title string
  author string?
  protocol string

  status ProposalStatus?
  created_date string?
  voting_start string?
  voting_end string?

  summary string
  motivation string?
  specification string?

  requested_funds string?      // If treasury request
  impact_assessment string?

  vote_breakdown VoteBreakdown?

  discussion_link string?
  snapshot_link string?
}

function ExtractGovernanceProposal(content: string) -> GovernanceProposalExtraction {
  client Claude
  prompt #"
    Extract structured information from this DeFi governance proposal.

    Focus on:
    1. Proposal identification (ID, title, protocol)
    2. Status and timeline
    3. Content (summary, motivation, specification)
    4. Financial impact (requested funds, treasury changes)
    5. Voting results if available

    Content:
    {{ content }}

    {{ ctx.output_format }}
  "#
}

// ============================================================================
// DEFI PROTOCOL DOCUMENTATION
// ============================================================================

class ContractAddress {
  name string
  address string
  chain string
  verified bool?
}

class TokenInfo {
  symbol string
  name string?
  decimals int?
  contract_address string?
  chain string?
}

class RiskFactor {
  category string       // "Smart Contract", "Oracle", "Liquidity", "Governance"
  description string
  severity string       // "Low", "Medium", "High"
  mitigation string?
}

class ProtocolDocExtraction {
  protocol_name string
  protocol_type string           // "DEX", "Lending", "Yield", "Bridge", "Derivative"

  description string
  key_features string[]

  supported_chains string[]
  contracts ContractAddress[]
  tokens TokenInfo[]

  tvl_current string?
  tvl_ath string?

  fees_structure string?
  revenue_model string?

  risk_factors RiskFactor[]

  governance_token string?
  governance_model string?

  audit_status string?
  auditors string[]

  integrations string[]          // Other protocols integrated
  competitors string[]
}

function ExtractProtocolDocs(content: string) -> ProtocolDocExtraction {
  client Claude
  prompt #"
    Extract structured information from this DeFi protocol documentation.

    Focus on:
    1. Protocol basics (name, type, description)
    2. Technical details (contracts, chains, tokens)
    3. Economic model (fees, revenue, TVL)
    4. Risk assessment
    5. Governance structure
    6. Audit and security status

    Content:
    {{ content }}

    {{ ctx.output_format }}
  "#
}
