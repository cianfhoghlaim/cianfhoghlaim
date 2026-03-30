// Crypto Document Extraction Schemas
// Extract structured data from whitepapers, audits, and documentation

// ============================================================
// Enums
// ============================================================

enum Blockchain {
  ETHEREUM
  SOLANA
  POLYGON
  ARBITRUM
  BASE
  OPTIMISM
  AVALANCHE
  BSC
  BITCOIN
  COSMOS
  NEAR
  SUI
  APTOS
}

enum TokenType {
  NATIVE @description("Chain native token (ETH, SOL)")
  ERC20
  BEP20
  SPL
  GOVERNANCE @description("Protocol governance token")
  STABLECOIN
  WRAPPED @description("Wrapped version of another token")
  SYNTHETIC @description("Synthetic/derivative token")
  LP_TOKEN @description("Liquidity pool share token")
  NFT
}

enum ProtocolCategory {
  DEX @description("Decentralized exchange")
  LENDING @description("Lending and borrowing")
  DERIVATIVES @description("Futures, options, perps")
  STABLECOIN @description("Stablecoin issuance")
  YIELD @description("Yield aggregator/optimizer")
  BRIDGE @description("Cross-chain bridge")
  ORACLE @description("Price oracle provider")
  LIQUID_STAKING @description("Liquid staking derivatives")
  CDP @description("Collateralized debt position")
  INSURANCE @description("DeFi insurance")
  NFT_MARKETPLACE
  GAMING
  INFRASTRUCTURE
  RWA @description("Real-world assets")
}

enum DocumentType {
  WHITEPAPER
  AUDIT_REPORT
  RESEARCH_REPORT
  GOVERNANCE_PROPOSAL
  RISK_ASSESSMENT
  TECHNICAL_DOCS
  TOKENOMICS
  LITEPAPER
}

enum RiskSeverity {
  CRITICAL @description("Immediate threat to funds")
  HIGH @description("Significant vulnerability")
  MEDIUM @description("Moderate concern")
  LOW @description("Minor issue")
  INFORMATIONAL @description("Best practice suggestion")
}

// ============================================================
// Token Extraction
// ============================================================

class TokenInfo {
  symbol string @description("Token ticker symbol")
  name string @description("Full token name")
  contract_address string? @description("Contract address if applicable")
  blockchain Blockchain
  token_type TokenType
  decimals int?

  total_supply string? @description("Total supply as string to handle large numbers")
  initial_supply string?
  max_supply string?

  utility string[] @description("Token use cases")
  mechanisms string[] @description("Economic mechanisms (burning, rebasing, etc.)")
}

class TokenDistribution {
  category string @description("Team, treasury, investors, community, etc.")
  percentage float
  vesting_period string? @description("Vesting schedule if applicable")
  cliff string?
  notes string?
}

class Tokenomics {
  token TokenInfo
  distribution TokenDistribution[]
  emission_schedule string? @description("How new tokens enter circulation")
  fee_structure FeeStructure?
  governance_mechanism string?
  staking_rewards string?
  burn_mechanisms string[]
  inflation_rate string?
}

class FeeStructure {
  fee_types FeeType[]
  fee_distribution FeeDistribution[]
}

class FeeType {
  name string @description("swap_fee, borrow_rate, etc.")
  rate string @description("Percentage or basis points")
  conditions string?
}

class FeeDistribution {
  recipient string @description("Protocol treasury, stakers, LP, etc.")
  percentage float
}

// ============================================================
// Protocol Extraction
// ============================================================

class ProtocolOverview {
  name string
  category ProtocolCategory
  subcategories ProtocolCategory[]
  description string @description("Concise protocol description")

  chains Blockchain[]
  governance_token string?
  launch_date string?

  key_features string[]
  differentiators string[] @description("What makes this protocol unique")
  competitors string[]

  team TeamInfo?
  investors string[]

  urls ProtocolUrls
}

class TeamInfo {
  founders Founder[]
  team_size string?
  anonymous bool @description("Is team anonymous/pseudonymous")
  doxxed bool @description("Are founders publicly known")
  relevant_experience string[]
}

class Founder {
  name string @description("Name or pseudonym")
  role string
  background string?
  twitter string?
  linkedin string?
}

class ProtocolUrls {
  website string?
  documentation string?
  github string?
  discord string?
  twitter string?
  governance_forum string?
}

// ============================================================
// Audit Extraction
// ============================================================

class AuditReport {
  auditor string @description("Auditing firm name")
  protocol string
  audit_date string
  report_url string?

  scope AuditScope
  findings AuditFinding[]
  summary AuditSummary

  recommendations string[]
  response_by_team string?
}

class AuditScope {
  contracts_reviewed string[]
  commit_hash string?
  lines_of_code int?
  duration string?
  methodology string[]
}

class AuditFinding {
  id string @description("Finding identifier")
  title string
  severity RiskSeverity
  category string @description("Reentrancy, Access Control, Logic Error, etc.")
  description string
  impact string
  recommendation string
  status string @description("Fixed, Acknowledged, Disputed, etc.")
  location string? @description("File and line number")
}

class AuditSummary {
  critical_count int
  high_count int
  medium_count int
  low_count int
  informational_count int

  overall_assessment string
  key_concerns string[]
  strengths string[]
}

// ============================================================
// Risk Extraction
// ============================================================

class RiskFactor {
  category string @description("Smart Contract, Economic, Governance, Oracle, etc.")
  severity RiskSeverity
  description string
  likelihood string @description("High, Medium, Low")
  potential_impact string
  mitigations string[]
}

class RiskProfile {
  protocol string
  overall_risk_score float @description("0-100 scale")

  smart_contract_risks RiskFactor[]
  economic_risks RiskFactor[]
  governance_risks RiskFactor[]
  operational_risks RiskFactor[]
  external_dependency_risks RiskFactor[]

  insurance_coverage string?
  bug_bounty string?

  risk_summary string
}

// ============================================================
// Extraction Functions
// ============================================================

function ExtractTokenomics(text: string) -> Tokenomics {
  client DocumentAnalysis
  prompt #"
    Extract detailed tokenomics information from this crypto document.

    Document:
    {{ text }}

    Focus on:
    - Token details (symbol, supply, type)
    - Distribution percentages with vesting schedules
    - Fee structures and where fees go
    - Emission schedules and inflation
    - Governance and staking mechanisms
    - Any burn or deflationary mechanisms

    Be precise with numbers and percentages.

    {{ ctx.output_format }}
  "#
}

function ExtractProtocolOverview(text: string, doc_type: DocumentType) -> ProtocolOverview {
  client FastExtraction
  prompt #"
    Extract protocol overview information from this {{ doc_type }} document.

    Document:
    {{ text }}

    Capture:
    - Protocol name and category
    - Supported chains
    - Key features and differentiators
    - Team information (if available)
    - Investors and backers
    - All relevant URLs

    {{ ctx.output_format }}
  "#
}

function ExtractAuditFindings(audit_text: string) -> AuditReport {
  client Claude
  prompt #"
    Extract structured audit findings from this security audit report.

    Audit Report:
    {{ audit_text }}

    For each finding, capture:
    - Severity level (Critical, High, Medium, Low, Informational)
    - Category (Reentrancy, Access Control, etc.)
    - Description and impact
    - Recommendation and resolution status

    Provide accurate counts in the summary.

    {{ ctx.output_format }}
  "#
}

function ExtractRiskProfile(text: string, protocol_name: string) -> RiskProfile {
  client RiskAssessment
  prompt #"
    Analyze this document and extract risk factors for {{ protocol_name }}.

    Document:
    {{ text }}

    Categorize risks into:
    - Smart Contract: Code vulnerabilities, upgrade risks
    - Economic: Tokenomics flaws, manipulation risks
    - Governance: Centralization, voting attacks
    - Operational: Team risks, key person dependencies
    - External: Oracle, bridge, integration risks

    Assign severity and likelihood to each risk.
    Calculate an overall risk score (0-100, lower is better).

    {{ ctx.output_format }}
  "#
}

function ExtractTokenFromWhitepaper(whitepaper: string) -> TokenInfo {
  client FastExtraction
  prompt #"
    Extract token information from this whitepaper.

    Whitepaper:
    {{ whitepaper }}

    Find:
    - Token symbol and name
    - Blockchain deployment
    - Token type (governance, utility, etc.)
    - Supply details
    - Token utility and mechanisms

    {{ ctx.output_format }}
  "#
}

// Batch extraction for multiple documents
function ExtractProtocolKnowledge(
  documents: string[],
  protocol_name: string
) -> ProtocolKnowledge {
  client DocumentAnalysis
  prompt #"
    Synthesize knowledge about {{ protocol_name }} from these documents.

    Documents:
    {% for doc in documents %}
    --- Document {{ loop.index }} ---
    {{ doc }}
    {% endfor %}

    Create a comprehensive profile including:
    - Protocol mechanics and innovations
    - Token economics
    - Risk factors from audits
    - Competitive positioning

    {{ ctx.output_format }}
  "#
}

class ProtocolKnowledge {
  name string
  category ProtocolCategory
  overview ProtocolOverview
  tokenomics Tokenomics?
  risks RiskProfile?
  audit_history AuditReport[]
  key_innovations string[]
  competitive_advantages string[]
  concerns string[]
  data_freshness string @description("Date of most recent source")
}
