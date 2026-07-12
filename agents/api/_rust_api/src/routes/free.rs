//! Free API Routes
//!
//! Routes that do not require payment - basic game data and health checks.

use axum::{
    Router,
    routing::get,
    Json,
};
use serde::Serialize;
// Note: These types are used for documentation reference
// use cianfhoghlaim_shared_types::{CelticLanguage, GameZone, ClanId};

/// Create the free routes router
pub fn router() -> Router {
    Router::new()
        .route("/", get(root))
        .route("/health", get(health))
        .route("/api/zones", get(list_zones))
        .route("/api/languages", get(list_languages))
        .route("/api/clans", get(list_clans))
}

/// Root endpoint
async fn root() -> &'static str {
    "Tuath Celtic MMO API - Fáilte!"
}

/// Health check endpoint
#[derive(Serialize)]
struct HealthResponse {
    status: &'static str,
    version: &'static str,
    service: &'static str,
}

async fn health() -> Json<HealthResponse> {
    Json(HealthResponse {
        status: "healthy",
        version: env!("CARGO_PKG_VERSION"),
        service: "tuath-api",
    })
}

/// List available game zones
#[derive(Serialize)]
struct ZoneInfo {
    id: &'static str,
    name: &'static str,
    region: &'static str,
    language: &'static str,
    description: &'static str,
}

async fn list_zones() -> Json<Vec<ZoneInfo>> {
    Json(vec![
        // Irish Gaeltacht regions
        ZoneInfo {
            id: "connemara",
            name: "Conamara",
            region: "Ireland",
            language: "ga",
            description: "The wild Atlantic coast of Connacht, home to ancient mysteries",
        },
        ZoneInfo {
            id: "donegal",
            name: "Dún na nGall",
            region: "Ireland",
            language: "ga",
            description: "The rugged northwest, where Ulster traditions thrive",
        },
        ZoneInfo {
            id: "kerry",
            name: "Ciarraí",
            region: "Ireland",
            language: "ga",
            description: "The Kingdom of Kerry, land of poets and warriors",
        },
        ZoneInfo {
            id: "clear_island",
            name: "Oileán Chléire",
            region: "Ireland",
            language: "ga",
            description: "The sacred island at the edge of the world",
        },
        ZoneInfo {
            id: "aran_islands",
            name: "Oileáin Árann",
            region: "Ireland",
            language: "ga",
            description: "The limestone islands where ancient traditions endure",
        },
        // Scottish regions
        ZoneInfo {
            id: "skye_island",
            name: "An t-Eilean Sgitheanach",
            region: "Scotland",
            language: "gd",
            description: "The Isle of Mist, realm of the fairy folk",
        },
        ZoneInfo {
            id: "highlands",
            name: "A' Ghàidhealtachd",
            region: "Scotland",
            language: "gd",
            description: "The Scottish Highlands, land of clan battles and ancient magic",
        },
        ZoneInfo {
            id: "outer_hebrides",
            name: "Na h-Eileanan Siar",
            region: "Scotland",
            language: "gd",
            description: "The Western Isles, where the old ways persist",
        },
        // Welsh regions
        ZoneInfo {
            id: "dyfed",
            name: "Dyfed",
            region: "Wales",
            language: "cy",
            description: "The ancient kingdom of the Mabinogi",
        },
        ZoneInfo {
            id: "gwynedd",
            name: "Gwynedd",
            region: "Wales",
            language: "cy",
            description: "The mountainous heart of Welsh language and culture",
        },
        ZoneInfo {
            id: "anglesey",
            name: "Môn",
            region: "Wales",
            language: "cy",
            description: "The sacred island of the druids",
        },
        // Mythological realms
        ZoneInfo {
            id: "tir_na_nog",
            name: "Tír na nÓg",
            region: "Otherworld",
            language: "ga",
            description: "The Land of the Young, where time stands still",
        },
        ZoneInfo {
            id: "tech_duinn",
            name: "Tech Duinn",
            region: "Otherworld",
            language: "ga",
            description: "The House of Donn, gathering place of the dead",
        },
        ZoneInfo {
            id: "mag_mell",
            name: "Mag Mell",
            region: "Otherworld",
            language: "ga",
            description: "The Plain of Joy, realm of eternal feasting",
        },
        ZoneInfo {
            id: "annwn",
            name: "Annwn",
            region: "Otherworld",
            language: "cy",
            description: "The Welsh otherworld, ruled by Arawn",
        },
    ])
}

/// List supported Celtic languages
#[derive(Serialize)]
struct LanguageInfo {
    code: &'static str,
    name: &'static str,
    native_name: &'static str,
    speakers: &'static str,
    status: &'static str,
}

async fn list_languages() -> Json<Vec<LanguageInfo>> {
    Json(vec![
        LanguageInfo {
            code: "ga",
            name: "Irish",
            native_name: "Gaeilge",
            speakers: "~1.7 million",
            status: "Official EU language",
        },
        LanguageInfo {
            code: "gd",
            name: "Scottish Gaelic",
            native_name: "Gàidhlig",
            speakers: "~57,000 native",
            status: "Recognized in Scotland",
        },
        LanguageInfo {
            code: "cy",
            name: "Welsh",
            native_name: "Cymraeg",
            speakers: "~880,000",
            status: "Official in Wales",
        },
        LanguageInfo {
            code: "gv",
            name: "Manx",
            native_name: "Gaelg",
            speakers: "~2,000 fluent",
            status: "Revitalized",
        },
        LanguageInfo {
            code: "kw",
            name: "Cornish",
            native_name: "Kernewek",
            speakers: "~3,000 fluent",
            status: "Revived",
        },
        LanguageInfo {
            code: "br",
            name: "Breton",
            native_name: "Brezhoneg",
            speakers: "~200,000",
            status: "Regional language in France",
        },
    ])
}

/// List playable clans
#[derive(Serialize)]
struct ClanInfo {
    id: &'static str,
    name: &'static str,
    irish_name: &'static str,
    description: &'static str,
    bonus: &'static str,
}

async fn list_clans() -> Json<Vec<ClanInfo>> {
    Json(vec![
        ClanInfo {
            id: "tuatha_de_danann",
            name: "Tuatha Dé Danann",
            irish_name: "Tuatha Dé Danann",
            description: "The children of the goddess Danu, masters of magic and the arts",
            bonus: "+20% Language Learning XP, +10% Magic Power",
        },
        ClanInfo {
            id: "fir_bolg",
            name: "Fir Bolg",
            irish_name: "Fir Bolg",
            description: "The Men of Bags, steadfast warriors and farmers",
            bonus: "+20% Combat XP, +10% Crafting Speed",
        },
        ClanInfo {
            id: "fomorians",
            name: "Fomorians",
            irish_name: "Fomhóraigh",
            description: "The sea giants of chaos, masters of the dark waters",
            bonus: "+20% Trading Profits, +10% Sea Travel Speed",
        },
        ClanInfo {
            id: "milesians",
            name: "Milesians",
            irish_name: "Clann Mhíle",
            description: "The children of Míl Espáine, ancestors of the Gaels",
            bonus: "+20% Exploration XP, +10% All Stats",
        },
    ])
}
