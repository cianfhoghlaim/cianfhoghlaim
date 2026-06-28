//! Premium API Routes
//!
//! Routes protected by x402 micropayments. Each route requires USDC payment
//! on supported networks (Base, Polygon, Solana).

use axum::{
    Router,
    routing::{get, post},
    Json,
    extract::Path,
};
use serde::{Deserialize, Serialize};
use x402_axum::{X402Middleware, IntoPriceTag};
use x402_rs::network::{Network, USDCDeployment};
use x402_rs::types::EvmAddress;

use crate::config::{Config, prices};

/// Create the premium routes router with x402 payment protection
pub fn router(config: &Config) -> anyhow::Result<Router> {
    // Parse the pay-to address (EVM address format: 0x...)
    let pay_to: EvmAddress = config.evm_pay_to.parse()
        .map_err(|e| anyhow::anyhow!("Invalid EVM_PAY_TO address '{}': {}", config.evm_pay_to, e))?;

    // Create x402 middleware
    let x402 = X402Middleware::try_from(config.facilitator_url.clone())?
        .with_base_url(url::Url::parse(&config.base_url)?);

    // USDC deployments for multi-chain support
    let usdc_base = USDCDeployment::by_network(Network::Base).pay_to(pay_to);
    let usdc_polygon = USDCDeployment::by_network(Network::Polygon).pay_to(pay_to);

    // Testnet deployments for development
    let usdc_base_sepolia = USDCDeployment::by_network(Network::BaseSepolia).pay_to(pay_to);
    let usdc_polygon_amoy = USDCDeployment::by_network(Network::PolygonAmoy).pay_to(pay_to);

    let router = Router::new()
        // Premium Quest Access - $0.05
        .route(
            "/api/premium/quest/:quest_id",
            get(get_premium_quest).layer(
                x402.with_description("Premium Quest Content - Celtic Mythology")
                    .with_mime_type("application/json")
                    .with_input_schema(serde_json::json!({
                        "type": "http",
                        "method": "GET",
                        "discoverable": true,
                        "description": "Access premium quest content with Celtic mythology stories and language exercises"
                    }))
                    .with_output_schema(serde_json::json!({
                        "type": "object",
                        "properties": {
                            "quest": { "type": "object" },
                            "story": { "type": "string" },
                            "vocabulary": { "type": "array" },
                            "exercises": { "type": "array" }
                        }
                    }))
                    // Mainnet
                    .with_price_tag(usdc_base.amount(prices::PREMIUM_QUEST).unwrap())
                    .or_price_tag(usdc_polygon.amount(prices::PREMIUM_QUEST).unwrap())
                    // Testnet
                    .or_price_tag(usdc_base_sepolia.amount(prices::PREMIUM_QUEST).unwrap())
                    .or_price_tag(usdc_polygon_amoy.amount(prices::PREMIUM_QUEST).unwrap()),
            ),
        )
        // Celtic Knowledge Search - $0.02
        .route(
            "/api/knowledge/search",
            post(search_knowledge).layer(
                x402.with_description("Celtic Mythology & Language Knowledge Search")
                    .with_mime_type("application/json")
                    .with_input_schema(serde_json::json!({
                        "type": "http",
                        "method": "POST",
                        "discoverable": true,
                        "description": "Search Celtic mythology, language, and cultural knowledge using RAG"
                    }))
                    .with_output_schema(serde_json::json!({
                        "type": "object",
                        "properties": {
                            "results": { "type": "array" },
                            "sources": { "type": "array" },
                            "answer": { "type": "string" }
                        }
                    }))
                    .with_price_tag(usdc_base.amount(prices::KNOWLEDGE_SEARCH).unwrap())
                    .or_price_tag(usdc_polygon.amount(prices::KNOWLEDGE_SEARCH).unwrap())
                    .or_price_tag(usdc_base_sepolia.amount(prices::KNOWLEDGE_SEARCH).unwrap())
                    .or_price_tag(usdc_polygon_amoy.amount(prices::KNOWLEDGE_SEARCH).unwrap()),
            ),
        )
        // Extended AI Agent Conversation - $0.10
        .route(
            "/api/agent/extended",
            post(agent_extended).layer(
                x402.with_description("Extended AI Agent Conversation - Celtic Tutor")
                    .with_mime_type("application/json")
                    .with_input_schema(serde_json::json!({
                        "type": "http",
                        "method": "POST",
                        "discoverable": true,
                        "description": "Extended conversation with the Celtic Tutor AI for language learning and mythology exploration"
                    }))
                    .with_output_schema(serde_json::json!({
                        "type": "object",
                        "properties": {
                            "response": { "type": "string" },
                            "vocabulary_learned": { "type": "array" },
                            "pronunciation_tips": { "type": "array" },
                            "cultural_context": { "type": "string" }
                        }
                    }))
                    .with_price_tag(usdc_base.amount(prices::AGENT_EXTENDED).unwrap())
                    .or_price_tag(usdc_polygon.amount(prices::AGENT_EXTENDED).unwrap())
                    .or_price_tag(usdc_base_sepolia.amount(prices::AGENT_EXTENDED).unwrap())
                    .or_price_tag(usdc_polygon_amoy.amount(prices::AGENT_EXTENDED).unwrap()),
            ),
        )
        // Daily XP Boost - $0.25
        .route(
            "/api/premium/xp-boost",
            post(activate_xp_boost).layer(
                x402.with_description("24-Hour XP Boost - 2x Experience Gain")
                    .with_mime_type("application/json")
                    .with_input_schema(serde_json::json!({
                        "type": "http",
                        "method": "POST",
                        "discoverable": true,
                        "description": "Activate a 24-hour 2x XP boost for accelerated learning"
                    }))
                    .with_output_schema(serde_json::json!({
                        "type": "object",
                        "properties": {
                            "activated": { "type": "boolean" },
                            "expires_at": { "type": "string" },
                            "multiplier": { "type": "number" }
                        }
                    }))
                    .with_price_tag(usdc_base.amount(prices::XP_BOOST_DAILY).unwrap())
                    .or_price_tag(usdc_polygon.amount(prices::XP_BOOST_DAILY).unwrap())
                    .or_price_tag(usdc_base_sepolia.amount(prices::XP_BOOST_DAILY).unwrap())
                    .or_price_tag(usdc_polygon_amoy.amount(prices::XP_BOOST_DAILY).unwrap()),
            ),
        )
        // Premium Clan Treasury Features - $0.15
        .route(
            "/api/premium/clan/treasury/:clan_id",
            get(get_clan_treasury).layer(
                x402.with_description("Premium Clan Treasury Analytics & Governance")
                    .with_mime_type("application/json")
                    .with_input_schema(serde_json::json!({
                        "type": "http",
                        "method": "GET",
                        "discoverable": true,
                        "description": "Access premium clan treasury features including analytics and governance tools"
                    }))
                    .with_output_schema(serde_json::json!({
                        "type": "object",
                        "properties": {
                            "balance": { "type": "object" },
                            "transactions": { "type": "array" },
                            "analytics": { "type": "object" },
                            "proposals": { "type": "array" }
                        }
                    }))
                    .with_price_tag(usdc_base.amount(prices::CLAN_TREASURY).unwrap())
                    .or_price_tag(usdc_polygon.amount(prices::CLAN_TREASURY).unwrap())
                    .or_price_tag(usdc_base_sepolia.amount(prices::CLAN_TREASURY).unwrap())
                    .or_price_tag(usdc_polygon_amoy.amount(prices::CLAN_TREASURY).unwrap()),
            ),
        );

    Ok(router)
}

// ============================================================================
// Handler Implementations
// ============================================================================

/// Premium quest content
#[derive(Serialize)]
struct PremiumQuestResponse {
    quest: QuestDetails,
    story: String,
    vocabulary: Vec<VocabularyWord>,
    exercises: Vec<LanguageExercise>,
}

#[derive(Serialize)]
struct QuestDetails {
    id: String,
    title: String,
    irish_title: String,
    description: String,
    mythology_theme: String,
    difficulty: String,
    rewards: QuestRewards,
}

#[derive(Serialize)]
struct QuestRewards {
    xp: u32,
    gold: u32,
    vocabulary_words: u32,
}

#[derive(Serialize)]
struct VocabularyWord {
    irish: String,
    english: String,
    pronunciation: String,
    audio_url: Option<String>,
    example_sentence: String,
}

#[derive(Serialize)]
struct LanguageExercise {
    exercise_type: String,
    prompt: String,
    correct_answer: String,
    hints: Vec<String>,
}

async fn get_premium_quest(Path(quest_id): Path<String>) -> Json<PremiumQuestResponse> {
    // In production, this would fetch from SpacetimeDB and the knowledge graph
    Json(PremiumQuestResponse {
        quest: QuestDetails {
            id: quest_id.clone(),
            title: "The Salmon of Knowledge".to_string(),
            irish_title: "Bradán Feasa".to_string(),
            description: "Follow in the footsteps of young Fionn mac Cumhaill as he discovers the Salmon of Knowledge by the River Boyne.".to_string(),
            mythology_theme: "Fenian Cycle".to_string(),
            difficulty: "intermediate".to_string(),
            rewards: QuestRewards {
                xp: 500,
                gold: 100,
                vocabulary_words: 15,
            },
        },
        story: "Ar bhruach na Bóinne, bhí an file Finnegas ina chónaí. Bhí sé ag iarraidh an Bradán Feasa a ghabháil le seacht mbliana...".to_string(),
        vocabulary: vec![
            VocabularyWord {
                irish: "bradán".to_string(),
                english: "salmon".to_string(),
                pronunciation: "/ˈbɾˠəd̪ˠaːn̪ˠ/".to_string(),
                audio_url: Some("/audio/bradan.mp3".to_string()),
                example_sentence: "Tá an bradán ag snámh san abhainn.".to_string(),
            },
            VocabularyWord {
                irish: "fios".to_string(),
                english: "knowledge".to_string(),
                pronunciation: "/fʲɪsˠ/".to_string(),
                audio_url: Some("/audio/fios.mp3".to_string()),
                example_sentence: "Fuair sé fios an domhain ar fad.".to_string(),
            },
            VocabularyWord {
                irish: "abhainn".to_string(),
                english: "river".to_string(),
                pronunciation: "/ˈau̯ɪn̠ʲ/".to_string(),
                audio_url: Some("/audio/abhainn.mp3".to_string()),
                example_sentence: "Tá an Bhóinn ina habhainn naofa.".to_string(),
            },
        ],
        exercises: vec![
            LanguageExercise {
                exercise_type: "translation".to_string(),
                prompt: "Translate: 'The salmon swims in the river'".to_string(),
                correct_answer: "Snámhann an bradán san abhainn".to_string(),
                hints: vec!["snámh = swim".to_string(), "san = in the".to_string()],
            },
            LanguageExercise {
                exercise_type: "fill_blank".to_string(),
                prompt: "Fuair Fionn _____ nuair a d'ith sé an bradán.".to_string(),
                correct_answer: "fios".to_string(),
                hints: vec!["knowledge".to_string()],
            },
        ],
    })
}

/// Knowledge search request/response
#[derive(Deserialize)]
struct KnowledgeSearchRequest {
    query: String,
    language: Option<String>,
    category: Option<String>,
    limit: Option<usize>,
}

#[derive(Serialize)]
struct KnowledgeSearchResponse {
    results: Vec<KnowledgeResult>,
    sources: Vec<String>,
    answer: String,
}

#[derive(Serialize)]
struct KnowledgeResult {
    title: String,
    content: String,
    category: String,
    relevance_score: f32,
}

async fn search_knowledge(Json(request): Json<KnowledgeSearchRequest>) -> Json<KnowledgeSearchResponse> {
    // In production, this would use RAG with the Celtic knowledge graph
    Json(KnowledgeSearchResponse {
        results: vec![
            KnowledgeResult {
                title: "Tuatha Dé Danann".to_string(),
                content: "The Tuatha Dé Danann ('peoples of the goddess Danu') were a supernatural race in Irish mythology. They were skilled in magic, arts, and sciences.".to_string(),
                category: "mythology".to_string(),
                relevance_score: 0.95,
            },
        ],
        sources: vec![
            "Lebor Gabála Érenn".to_string(),
            "Cath Maige Tuired".to_string(),
        ],
        answer: format!("Based on your query '{}', here is what the ancient texts tell us...", request.query),
    })
}

/// Extended AI agent conversation
#[derive(Deserialize)]
struct AgentRequest {
    message: String,
    context: Option<String>,
    learning_goals: Option<Vec<String>>,
}

#[derive(Serialize)]
struct AgentResponse {
    response: String,
    vocabulary_learned: Vec<VocabularyWord>,
    pronunciation_tips: Vec<String>,
    cultural_context: String,
}

async fn agent_extended(Json(request): Json<AgentRequest>) -> Json<AgentResponse> {
    // In production, this would call the ADK Celtic Tutor agent
    Json(AgentResponse {
        response: format!("Dia duit! Let me help you with: {}. In Irish mythology and language...", request.message),
        vocabulary_learned: vec![
            VocabularyWord {
                irish: "Dia duit".to_string(),
                english: "Hello (God be with you)".to_string(),
                pronunciation: "/ˈdʲiə ɡɪt̪ˠ/".to_string(),
                audio_url: None,
                example_sentence: "Dia duit, a chara!".to_string(),
            },
        ],
        pronunciation_tips: vec![
            "In Irish, 'dh' at the start of a word is often silent before a slender vowel".to_string(),
        ],
        cultural_context: "The Irish greeting 'Dia duit' reflects the deep connection between Irish culture and spirituality. It literally means 'God be with you'.".to_string(),
    })
}

/// XP Boost activation
#[derive(Serialize)]
struct XpBoostResponse {
    activated: bool,
    expires_at: String,
    multiplier: f32,
}

async fn activate_xp_boost() -> Json<XpBoostResponse> {
    // In production, this would update the player state in SpacetimeDB
    let expires_at = chrono::Utc::now() + chrono::Duration::hours(24);
    Json(XpBoostResponse {
        activated: true,
        expires_at: expires_at.to_rfc3339(),
        multiplier: 2.0,
    })
}

/// Clan treasury premium features
#[derive(Serialize)]
struct ClanTreasuryResponse {
    balance: TreasuryBalance,
    transactions: Vec<TreasuryTransaction>,
    analytics: TreasuryAnalytics,
    proposals: Vec<GovernanceProposal>,
}

#[derive(Serialize)]
struct TreasuryBalance {
    gold: u64,
    usdc_base: f64,
    usdc_polygon: f64,
    nfts: u32,
}

#[derive(Serialize)]
struct TreasuryTransaction {
    id: String,
    transaction_type: String,
    amount: String,
    from: String,
    timestamp: String,
}

#[derive(Serialize)]
struct TreasuryAnalytics {
    total_inflow_30d: f64,
    total_outflow_30d: f64,
    member_contributions: Vec<MemberContribution>,
    spending_categories: Vec<SpendingCategory>,
}

#[derive(Serialize)]
struct MemberContribution {
    member_id: String,
    member_name: String,
    contribution: f64,
}

#[derive(Serialize)]
struct SpendingCategory {
    category: String,
    amount: f64,
    percentage: f32,
}

#[derive(Serialize)]
struct GovernanceProposal {
    id: String,
    title: String,
    proposer: String,
    status: String,
    votes_for: u32,
    votes_against: u32,
    ends_at: String,
}

async fn get_clan_treasury(Path(clan_id): Path<String>) -> Json<ClanTreasuryResponse> {
    // In production, this would fetch from SpacetimeDB and on-chain data
    Json(ClanTreasuryResponse {
        balance: TreasuryBalance {
            gold: 50000,
            usdc_base: 125.50,
            usdc_polygon: 75.25,
            nfts: 12,
        },
        transactions: vec![
            TreasuryTransaction {
                id: "tx_001".to_string(),
                transaction_type: "deposit".to_string(),
                amount: "10.00 USDC".to_string(),
                from: "member_fionn".to_string(),
                timestamp: "2024-12-28T10:00:00Z".to_string(),
            },
        ],
        analytics: TreasuryAnalytics {
            total_inflow_30d: 250.75,
            total_outflow_30d: 125.00,
            member_contributions: vec![
                MemberContribution {
                    member_id: "member_fionn".to_string(),
                    member_name: "Fionn mac Cumhaill".to_string(),
                    contribution: 75.00,
                },
            ],
            spending_categories: vec![
                SpendingCategory {
                    category: "Quest Rewards".to_string(),
                    amount: 75.00,
                    percentage: 60.0,
                },
                SpendingCategory {
                    category: "Territory Defense".to_string(),
                    amount: 50.00,
                    percentage: 40.0,
                },
            ],
        },
        proposals: vec![
            GovernanceProposal {
                id: "prop_001".to_string(),
                title: "Expand clan territory to Tír na nÓg".to_string(),
                proposer: "member_nuada".to_string(),
                status: "active".to_string(),
                votes_for: 15,
                votes_against: 3,
                ends_at: "2024-12-30T00:00:00Z".to_string(),
            },
        ],
    })
}
