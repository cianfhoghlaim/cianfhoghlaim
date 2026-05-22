// Crypteolas Knowledge Graph Schema
// For use with FalkorDB (Graphiti) and Memgraph (Cognee)

// ============================================
// NODE LABELS
// ============================================

// Protocol - DeFi protocols, exchanges, bridges
// CREATE CONSTRAINT protocol_name IF NOT EXISTS FOR (p:Protocol) REQUIRE p.name IS UNIQUE;

// Token - Cryptocurrency tokens
// CREATE CONSTRAINT token_symbol IF NOT EXISTS FOR (t:Token) REQUIRE t.symbol IS UNIQUE;

// Chain - Blockchain networks
// CREATE CONSTRAINT chain_id IF NOT EXISTS FOR (c:Chain) REQUIRE c.chain_id IS UNIQUE;

// Developer - Individual developers
// CREATE CONSTRAINT developer_github IF NOT EXISTS FOR (d:Developer) REQUIRE d.github_username IS UNIQUE;

// Organization - Teams, companies, DAOs
// CREATE CONSTRAINT org_name IF NOT EXISTS FOR (o:Organization) REQUIRE o.name IS UNIQUE;

// Auditor - Security audit firms
// CREATE CONSTRAINT auditor_name IF NOT EXISTS FOR (a:Auditor) REQUIRE a.name IS UNIQUE;

// Vulnerability - Security vulnerabilities
// Properties: cve_id, severity, type, description

// Proposal - Governance proposals
// Properties: proposal_id, title, status, votes_for, votes_against

// Repository - GitHub repositories
// CREATE CONSTRAINT repo_fullname IF NOT EXISTS FOR (r:Repository) REQUIRE r.full_name IS UNIQUE;

// ============================================
// RELATIONSHIP TYPES
// ============================================

// Protocol relationships
// (Protocol)-[:DEPLOYED_ON {deployed_at: datetime}]->(Chain)
// (Protocol)-[:HAS_TOKEN {is_governance: boolean}]->(Token)
// (Protocol)-[:FORKED_FROM {fork_date: datetime}]->(Protocol)
// (Protocol)-[:INTEGRATED_WITH {integration_type: string}]->(Protocol)
// (Protocol)-[:MIGRATED_TO {migration_date: datetime, version: string}]->(Protocol)

// Team relationships
// (Protocol)-[:FOUNDED_BY {founded_date: datetime}]->(Organization)
// (Protocol)-[:DEVELOPED_BY]->(Developer)
// (Developer)-[:MEMBER_OF {role: string, since: datetime}]->(Organization)
// (Developer)-[:CONTRIBUTED_TO {commits: int, first_commit: datetime}]->(Repository)

// Investment relationships
// (Organization)-[:INVESTED_IN {amount_usd: float, round: string, date: datetime}]->(Protocol)

// Security relationships
// (Protocol)-[:AUDITED_BY {audit_date: datetime, report_url: string}]->(Auditor)
// (Vulnerability)-[:AFFECTS {discovered_date: datetime}]->(Protocol)
// (Vulnerability)-[:FOUND_BY]->(Auditor)
// (Vulnerability)-[:PATCHED_IN {patch_date: datetime}]->(Protocol)

// Governance relationships
// (Proposal)-[:PROPOSED_FOR]->(Protocol)
// (Proposal)-[:PROPOSED_BY]->(Developer|Organization)
// (Token)-[:USED_FOR_VOTING]->(Protocol)

// Repository relationships
// (Protocol)-[:HAS_REPO]->(Repository)
// (Repository)-[:DEPENDS_ON]->(Repository)

// ============================================
// TEMPORAL PROPERTIES (for Graphiti)
// ============================================

// All relationships can have temporal properties:
// - valid_from: datetime - when the relationship became valid
// - valid_to: datetime - when the relationship was invalidated (null if current)
// - source: string - data source (defillama, github, manual)
// - confidence: float - confidence score 0-1

// Example temporal queries:

// Get protocol TVL history
// MATCH (p:Protocol {name: 'Uniswap'})-[r:HAS_TVL]->(m:Metric)
// WHERE r.valid_from >= datetime('2024-01-01')
// RETURN r.valid_from, m.value
// ORDER BY r.valid_from

// Get team changes over time
// MATCH (p:Protocol {name: 'Aave'})<-[r:DEVELOPED_BY]-(d:Developer)
// RETURN d.name, r.valid_from, r.valid_to
// ORDER BY r.valid_from

// ============================================
// SAMPLE DATA INSERTION
// ============================================

// Create sample protocol
// CREATE (p:Protocol {
//     name: 'Uniswap',
//     slug: 'uniswap',
//     category: 'DEX',
//     website: 'https://uniswap.org',
//     description: 'Decentralized exchange protocol',
//     created_at: datetime('2018-11-02')
// });

// Create sample chain
// CREATE (c:Chain {
//     name: 'Ethereum',
//     chain_id: 1,
//     symbol: 'ETH',
//     type: 'L1'
// });

// Create sample token
// CREATE (t:Token {
//     symbol: 'UNI',
//     name: 'Uniswap',
//     decimals: 18,
//     contract_address: '0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984'
// });

// Create relationships
// MATCH (p:Protocol {name: 'Uniswap'}), (c:Chain {chain_id: 1})
// CREATE (p)-[:DEPLOYED_ON {deployed_at: datetime('2018-11-02')}]->(c);

// MATCH (p:Protocol {name: 'Uniswap'}), (t:Token {symbol: 'UNI'})
// CREATE (p)-[:HAS_TOKEN {is_governance: true}]->(t);

// ============================================
// USEFUL QUERIES
// ============================================

// Find all protocols on a chain
// MATCH (p:Protocol)-[:DEPLOYED_ON]->(c:Chain {name: 'Ethereum'})
// RETURN p.name, p.category;

// Find protocol dependencies (forks and integrations)
// MATCH path = (p:Protocol {name: 'Compound'})-[:FORKED_FROM|INTEGRATED_WITH*1..3]-(related:Protocol)
// RETURN path;

// Find common auditors between protocols
// MATCH (p1:Protocol {name: 'Aave'})-[:AUDITED_BY]->(a:Auditor)<-[:AUDITED_BY]-(p2:Protocol)
// WHERE p1 <> p2
// RETURN p2.name, a.name;

// Find all vulnerabilities by severity
// MATCH (v:Vulnerability)-[:AFFECTS]->(p:Protocol)
// WHERE v.severity = 'critical'
// RETURN p.name, v.type, v.description;

// Get developer contribution network
// MATCH (d:Developer)-[:CONTRIBUTED_TO]->(r:Repository)<-[:HAS_REPO]-(p:Protocol)
// RETURN d.name, collect(DISTINCT p.name) as protocols;
