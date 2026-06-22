// Code Analysis Schemas for Crypteolas
// Smart contract review, vulnerability detection, and code understanding

// ============================================================
// Enums
// ============================================================

enum ProgrammingLanguage {
  SOLIDITY
  VYPER
  RUST @description("Solana, Cosmos SDK, Substrate")
  MOVE @description("Aptos, Sui")
  CAIRO @description("StarkNet")
  TYPESCRIPT @description("SDK, frontend, tooling")
  PYTHON @description("Scripts, tests, tooling")
  GO @description("Node implementations, tooling")
}

enum ContractType {
  TOKEN @description("ERC20, ERC721, etc.")
  DEX @description("AMM, order book")
  LENDING @description("Lending pool, vault")
  VAULT @description("Yield vault, strategy")
  GOVERNANCE @description("DAO, voting")
  BRIDGE @description("Cross-chain bridge")
  ORACLE @description("Price feed, data provider")
  PROXY @description("Upgradeable proxy")
  FACTORY @description("Contract factory")
  ROUTER @description("Multi-hop routing")
  STAKING @description("Staking, rewards")
  NFT @description("NFT collection, marketplace")
  MULTISIG @description("Multi-signature wallet")
  TIMELOCK @description("Timelock controller")
}

enum VulnerabilityCategory {
  REENTRANCY @description("Reentrancy attacks")
  ACCESS_CONTROL @description("Missing or weak access control")
  ARITHMETIC @description("Overflow, underflow, precision loss")
  ORACLE_MANIPULATION @description("Price oracle attacks")
  FLASH_LOAN @description("Flash loan attack vectors")
  FRONT_RUNNING @description("MEV, sandwich attacks")
  LOGIC_ERROR @description("Business logic flaws")
  INITIALIZATION @description("Uninitialized or re-initializable")
  UPGRADE @description("Unsafe upgrade patterns")
  DOS @description("Denial of service")
  TIMESTAMP @description("Block timestamp manipulation")
  EXTERNAL_CALL @description("Unsafe external calls")
  STORAGE_COLLISION @description("Storage slot collisions")
  SIGNATURE @description("Signature replay, malleability")
  GAS @description("Gas griefing, out of gas")
  INPUT_VALIDATION @description("Missing input validation")
}

enum CodeQuality {
  EXCELLENT @description("Production-ready, well-tested")
  GOOD @description("Minor improvements needed")
  FAIR @description("Several issues to address")
  POOR @description("Significant refactoring needed")
  CRITICAL @description("Not safe for production")
}

// ============================================================
// Code Structure Analysis
// ============================================================

class CodebaseOverview {
  repository string
  primary_language ProgrammingLanguage
  languages_used ProgrammingLanguage[]

  contracts ContractSummary[]
  total_files int
  total_lines int

  architecture_pattern string @description("Upgradeable, Diamond, etc.")
  key_dependencies string[]
  test_coverage string?

  notable_patterns string[]
  concerns string[]
}

class ContractSummary {
  name string
  file_path string
  contract_type ContractType
  lines_of_code int

  inherits string[] @description("Parent contracts/interfaces")
  implements string[] @description("Interfaces implemented")

  key_functions string[]
  state_variables int
  events int
  modifiers string[]

  complexity_score float @description("0-100, higher is more complex")
  risk_indicators string[]
}

class FunctionAnalysis {
  name string
  visibility string @description("public, external, internal, private")
  mutability string @description("view, pure, payable, nonpayable")

  parameters Parameter[]
  return_values string[]

  modifiers string[]
  access_control string?

  description string
  purpose string
  side_effects string[]

  gas_estimate string?
  complexity string @description("Low, Medium, High")

  potential_issues string[]
  recommendations string[]
}

class Parameter {
  name string
  type string
  description string?
  validation string? @description("How is it validated")
}

// ============================================================
// Vulnerability Detection
// ============================================================

class VulnerabilityReport {
  contract string
  file_path string
  analyzed_at string

  vulnerabilities Vulnerability[]
  security_score float @description("0-100, higher is more secure")

  critical_count int
  high_count int
  medium_count int
  low_count int

  summary string
  immediate_actions string[]
  recommendations string[]
}

class Vulnerability {
  id string
  title string
  category VulnerabilityCategory
  severity string @description("Critical, High, Medium, Low, Info")

  location CodeLocation
  description string
  impact string
  likelihood string

  proof_of_concept string? @description("Attack scenario")
  affected_functions string[]

  fix_recommendation string
  fix_complexity string @description("Simple, Moderate, Complex")
  references string[] @description("CWE, SWC IDs, or articles")
}

class CodeLocation {
  file string
  start_line int
  end_line int
  code_snippet string
}

// ============================================================
// Code Review
// ============================================================

class CodeReview {
  file string
  language ProgrammingLanguage

  quality CodeQuality
  maintainability_score float @description("0-100")
  security_score float @description("0-100")

  strengths string[]
  weaknesses string[]

  issues CodeIssue[]
  suggestions CodeSuggestion[]

  documentation_quality string
  test_recommendations string[]
}

class CodeIssue {
  severity string
  category string @description("Security, Performance, Style, Logic")
  location CodeLocation
  description string
  suggested_fix string?
}

class CodeSuggestion {
  type string @description("Optimization, Readability, Security, Gas")
  location CodeLocation?
  current_code string?
  suggested_code string?
  explanation string
  impact string
}

// ============================================================
// GitHub Analysis
// ============================================================

class RepositoryHealth {
  repo_url string
  stars int
  forks int
  open_issues int
  last_commit string

  contributors int
  commit_frequency string
  code_churn string @description("Stability indicator")

  ci_cd_status string
  test_coverage_trend string
  dependency_health DependencyHealth

  community_health CommunityHealth
  risk_indicators string[]
}

class DependencyHealth {
  total_dependencies int
  outdated_count int
  vulnerable_count int
  critical_vulnerabilities Dependency[]
  recommendations string[]
}

class Dependency {
  name string
  current_version string
  latest_version string
  vulnerability string?
  severity string?
}

class CommunityHealth {
  response_time string @description("Average issue response time")
  pr_merge_rate string
  documentation_score float
  contributor_diversity float
  governance_clarity string
}

class PRAnalysis {
  pr_number int
  title string
  author string
  files_changed int
  additions int
  deletions int

  summary string
  key_changes string[]

  risk_assessment string
  security_implications string[]
  breaking_changes bool
  migration_needed bool

  review_recommendations string[]
}

class IssueAnalysis {
  issue_number int
  title string
  labels string[]

  category string @description("Bug, Feature, Security, etc.")
  severity string?
  affected_components string[]

  summary string
  root_cause string?
  proposed_solutions string[]

  related_code string[]
  similar_issues string[]
}

// ============================================================
// Analysis Functions
// ============================================================

function AnalyzeContract(
  code: string,
  language: ProgrammingLanguage,
  contract_name: string
) -> VulnerabilityReport {
  client CrypteolasCodeAnalysis
  prompt #"
    Perform a comprehensive security analysis of this {{ language }} smart contract.

    Contract: {{ contract_name }}

    Code:
    ```
    {{ code }}
    ```

    Check for:
    - Reentrancy vulnerabilities
    - Access control issues
    - Arithmetic bugs (overflow, underflow, precision)
    - Oracle manipulation vectors
    - Flash loan attack surfaces
    - Front-running opportunities
    - Logic errors
    - Unsafe external calls
    - Initialization issues
    - Upgrade vulnerabilities

    For each finding:
    - Specify exact line numbers
    - Explain the attack scenario
    - Provide fix recommendations
    - Rate severity (Critical, High, Medium, Low, Info)

    {{ ctx.output_format }}
  "#
}

function ReviewCodeQuality(
  code: string,
  language: ProgrammingLanguage,
  file_path: string
) -> CodeReview {
  client CrypteolasCodeAnalysis
  prompt #"
    Review this {{ language }} code for quality, maintainability, and best practices.

    File: {{ file_path }}

    Code:
    ```
    {{ code }}
    ```

    Evaluate:
    - Code organization and structure
    - Naming conventions
    - Documentation and comments
    - Error handling
    - Gas efficiency (if applicable)
    - Test coverage needs
    - Security best practices

    Provide specific suggestions with code examples where helpful.

    {{ ctx.output_format }}
  "#
}

function AnalyzeFunction(
  function_code: string,
  contract_context: string,
  language: ProgrammingLanguage
) -> FunctionAnalysis {
  client CrypteolasFastExtraction
  prompt #"
    Analyze this {{ language }} function in detail.

    Function:
    ```
    {{ function_code }}
    ```

    Contract Context:
    {{ contract_context }}

    Explain:
    - What the function does
    - Access control requirements
    - State changes and side effects
    - Potential issues or edge cases
    - Gas considerations

    {{ ctx.output_format }}
  "#
}

function AnalyzePR(
  pr_diff: string,
  pr_title: string,
  pr_description: string
) -> PRAnalysis {
  client CrypteolasCodeAnalysis
  prompt #"
    Review this pull request for a crypto/DeFi codebase.

    Title: {{ pr_title }}
    Description: {{ pr_description }}

    Diff:
    ```
    {{ pr_diff }}
    ```

    Analyze:
    - Summary of changes
    - Security implications
    - Breaking changes
    - Migration requirements
    - Testing recommendations
    - Risk assessment

    {{ ctx.output_format }}
  "#
}

function ExplainCode(
  code: string,
  language: ProgrammingLanguage,
  context: string?
) -> CodeExplanation {
  client CrypteolasFastExtraction
  prompt #"
    Explain this {{ language }} code clearly for someone learning DeFi development.

    Code:
    ```
    {{ code }}
    ```

    {% if context %}
    Context: {{ context }}
    {% endif %}

    Provide:
    - High-level overview
    - Step-by-step explanation
    - Key patterns used
    - Important considerations
    - Common pitfalls

    {{ ctx.output_format }}
  "#
}

class CodeExplanation {
  overview string @description("High-level summary")
  step_by_step string[] @description("Line-by-line or block explanation")
  patterns_used string[] @description("Design patterns identified")
  key_concepts string[] @description("Important DeFi/crypto concepts")
  considerations string[] @description("Things to be aware of")
  common_pitfalls string[] @description("Mistakes to avoid")
  related_code string[] @description("Similar patterns elsewhere")
}

function CompareImplementations(
  code_a: string,
  code_b: string,
  language: ProgrammingLanguage
) -> ImplementationComparison {
  client CrypteolasCodeAnalysis
  prompt #"
    Compare these two {{ language }} implementations.

    Implementation A:
    ```
    {{ code_a }}
    ```

    Implementation B:
    ```
    {{ code_b }}
    ```

    Analyze:
    - Functional differences
    - Security trade-offs
    - Gas efficiency comparison
    - Maintainability comparison
    - Which is recommended and why

    {{ ctx.output_format }}
  "#
}

class ImplementationComparison {
  summary string
  functional_differences string[]
  security_comparison SecurityComparison
  gas_comparison GasComparison
  recommendation string
  rationale string
}

class SecurityComparison {
  a_advantages string[]
  b_advantages string[]
  a_risks string[]
  b_risks string[]
  winner string @description("A, B, or Tie")
}

class GasComparison {
  a_estimated_gas string
  b_estimated_gas string
  difference string
  winner string @description("A, B, or Tie")
  notes string
}
