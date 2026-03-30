// Code Pattern Detection Schema for Crypteolas
// Detects common crypto/DeFi code patterns and potential issues

enum RiskLevel {
    CRITICAL
    HIGH
    MEDIUM
    LOW
    INFO
}

enum PatternCategory {
    SECURITY
    PERFORMANCE
    BEST_PRACTICE
    ANTI_PATTERN
    GAS_OPTIMIZATION
}

class CodeLocation {
    file_path string @description("Path to the source file")
    start_line int @description("Starting line number")
    end_line int @description("Ending line number")
    code_snippet string @description("The relevant code snippet")
}

class CodePattern {
    pattern_type string @description("Type of pattern detected: reentrancy, flash_loan, access_control, etc.")
    pattern_name string @description("Human-readable pattern name")
    category PatternCategory @description("Pattern category")
    severity RiskLevel @description("Severity level of the pattern")
    description string @description("Detailed description of the pattern")
    location CodeLocation @description("Where the pattern was found")
    recommendation string @description("Recommended action or fix")
    confidence float @description("Confidence score 0-1")
}

class PatternDetectionResult {
    patterns CodePattern[] @description("List of detected patterns")
    summary string @description("Brief summary of findings")
    total_patterns int @description("Total number of patterns found")
    highest_severity RiskLevel @description("Highest severity found")
}

// Common Solidity/DeFi patterns to detect
enum SolidityPattern {
    REENTRANCY @description("Reentrancy vulnerability pattern")
    FLASH_LOAN_ATTACK @description("Flash loan attack vector")
    ACCESS_CONTROL @description("Missing or weak access control")
    UNCHECKED_RETURN @description("Unchecked external call return value")
    INTEGER_OVERFLOW @description("Potential integer overflow")
    FRONT_RUNNING @description("MEV/front-running vulnerability")
    ORACLE_MANIPULATION @description("Price oracle manipulation risk")
    SIGNATURE_REPLAY @description("Signature replay attack vector")
    DELEGATE_CALL @description("Dangerous delegatecall usage")
    SELFDESTRUCT @description("Selfdestruct usage")
    TX_ORIGIN @description("tx.origin authentication")
    BLOCK_TIMESTAMP @description("Block timestamp dependency")
    GAS_GRIEFING @description("Gas griefing vulnerability")
    DOS_LOOP @description("DoS via unbounded loop")
    UNINITIALIZED_STORAGE @description("Uninitialized storage pointer")
}

// Function to detect patterns in Solidity code
function DetectSolidityPatterns(
    code: string @description("Solidity source code"),
    contract_name: string? @description("Optional contract name for context")
) -> PatternDetectionResult {
    client "openai/gpt-4o"
    prompt #"
        Analyze the following Solidity code for security patterns and vulnerabilities.

        Contract: {{ contract_name ?? "Unknown" }}

        Code:
        ```solidity
        {{ code }}
        ```

        Detect the following pattern types:
        - Reentrancy vulnerabilities
        - Flash loan attack vectors
        - Access control issues
        - Unchecked external calls
        - Integer overflow/underflow risks
        - Front-running vulnerabilities
        - Oracle manipulation risks
        - Signature replay attacks
        - Dangerous delegatecall usage
        - Block timestamp dependencies
        - Gas griefing vectors
        - DoS via unbounded loops

        For each pattern found, provide:
        1. Pattern type and name
        2. Severity level (CRITICAL, HIGH, MEDIUM, LOW, INFO)
        3. Exact location in the code
        4. Clear description
        5. Recommended fix
        6. Confidence score

        Return the analysis in the specified format.
    "#
}

// Function to detect patterns in Python code
function DetectPythonPatterns(
    code: string @description("Python source code"),
    context: string? @description("Optional context about the code purpose")
) -> PatternDetectionResult {
    client "openai/gpt-4o"
    prompt #"
        Analyze the following Python code for patterns and potential issues.

        Context: {{ context ?? "General Python code" }}

        Code:
        ```python
        {{ code }}
        ```

        Look for:
        - Security issues (injection, unsafe deserialization)
        - Performance anti-patterns
        - Concurrency issues
        - Resource leaks
        - Error handling gaps
        - Type safety issues
        - API misuse

        For each pattern found, provide detailed analysis with severity,
        location, description, and recommendations.
    "#
}

// Function to detect patterns in TypeScript/JavaScript
function DetectTypeScriptPatterns(
    code: string @description("TypeScript/JavaScript source code"),
    is_frontend: bool @description("Whether this is frontend code")
) -> PatternDetectionResult {
    client "openai/gpt-4o"
    prompt #"
        Analyze the following {{ is_frontend ? "frontend" : "backend" }} TypeScript/JavaScript code.

        Code:
        ```typescript
        {{ code }}
        ```

        Look for:
        {{ is_frontend ? "- XSS vulnerabilities\n- CSRF issues\n- Unsafe DOM manipulation\n- Sensitive data exposure" : "- Injection vulnerabilities\n- Authentication bypasses\n- Insecure dependencies" }}
        - Type safety issues
        - Memory leaks
        - Performance anti-patterns
        - Error handling gaps
        - Async/await issues

        Provide detailed pattern analysis with severity and recommendations.
    "#
}

// Function to detect Rust-specific patterns
function DetectRustPatterns(
    code: string @description("Rust source code"),
    is_unsafe: bool @description("Whether the code contains unsafe blocks")
) -> PatternDetectionResult {
    client "openai/gpt-4o"
    prompt #"
        Analyze the following Rust code for patterns and potential issues.
        {{ is_unsafe ? "This code contains unsafe blocks - pay special attention to memory safety." : "" }}

        Code:
        ```rust
        {{ code }}
        ```

        Look for:
        - Memory safety issues (especially in unsafe blocks)
        - Data race conditions
        - Panic paths in library code
        - Error handling gaps (unwrap misuse)
        - Lifetime annotation issues
        - Performance anti-patterns
        - Idiomatic Rust violations

        Provide detailed pattern analysis.
    "#
}

// Cross-language pattern detection
function DetectCodePatterns(
    code: string @description("Source code to analyze"),
    language: string @description("Programming language: solidity, python, typescript, rust, go"),
    context: string? @description("Optional context about the code")
) -> PatternDetectionResult {
    client "openai/gpt-4o"
    prompt #"
        Analyze the following {{ language }} code for patterns, vulnerabilities, and issues.

        Context: {{ context ?? "Code analysis" }}

        Code:
        ```{{ language }}
        {{ code }}
        ```

        Perform comprehensive pattern detection including:
        1. Security vulnerabilities
        2. Performance issues
        3. Best practice violations
        4. Anti-patterns
        5. Language-specific idiom violations

        For each finding, provide:
        - Pattern type and name
        - Category (SECURITY, PERFORMANCE, BEST_PRACTICE, ANTI_PATTERN, GAS_OPTIMIZATION)
        - Severity (CRITICAL, HIGH, MEDIUM, LOW, INFO)
        - Exact code location
        - Clear description
        - Recommended fix
        - Confidence score (0-1)

        Return comprehensive analysis.
    "#
}
