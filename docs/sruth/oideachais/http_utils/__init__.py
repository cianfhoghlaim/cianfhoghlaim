"""
HTTP Client utilities for oideachais pipeline.

Provides shared HTTP client factory with circuit breaker,
rate limiting, and retry logic for DLT sources.
"""

from .client_factory import (
    HttpClientFactory,
    AuthStrategy,
    BearerTokenAuth,
    ApiKeyAuth,
    BasicAuth,
    create_client,
    # Pre-configured clients - Crypto/DeFi (primarily for crypteolas)
    defillama_client,
    defillama_yields_client,
    defillama_stablecoins_client,
    coingecko_client,
    github_client,
    binance_spot_client,
    binance_futures_client,
    okx_client,
    bybit_client,
    beaconchain_client,
    thegraph_client,
    # Pre-configured clients - Irish Education & Celtic Language
    logainm_client,
    tearma_client,
    ainm_client,
    duchas_client,
    doras_client,
    cso_pxstat_client,
    data_gov_ie_client,
    ncca_client,
    curriculum_online_client,
    sec_ie_client,
    # Pre-configured clients - Pan-Celtic (tuath)
    stats_wales_client,
    scotland_stats_client,
    osi_client,
    stats_wales_odata_client,
    # Pre-configured clients - UK Education
    dfe_explore_client,
    nisra_client,
    get_info_schools_client,
    # Pre-configured clients - Geospatial
    arcgis_geohive_client,
    met_eireann_client,
    met_office_uk_client,
    met_office_datahub_client,
    met_office_climate_client,
    # Pre-configured clients - Celtic Language & Pronunciation
    canuint_client,
    gaois_client,
)

__all__ = [
    "HttpClientFactory",
    "AuthStrategy",
    "BearerTokenAuth",
    "ApiKeyAuth",
    "BasicAuth",
    "create_client",
    # Crypto/DeFi clients
    "defillama_client",
    "defillama_yields_client",
    "defillama_stablecoins_client",
    "coingecko_client",
    "github_client",
    "binance_spot_client",
    "binance_futures_client",
    "okx_client",
    "bybit_client",
    "beaconchain_client",
    "thegraph_client",
    # Irish Education & Celtic Language clients
    "logainm_client",
    "tearma_client",
    "ainm_client",
    "duchas_client",
    "doras_client",
    "cso_pxstat_client",
    "data_gov_ie_client",
    "ncca_client",
    "curriculum_online_client",
    "sec_ie_client",
    # Pan-Celtic clients
    "stats_wales_client",
    "scotland_stats_client",
    "osi_client",
    "stats_wales_odata_client",
    # UK Education clients
    "dfe_explore_client",
    "nisra_client",
    "get_info_schools_client",
    # Geospatial clients
    "arcgis_geohive_client",
    "met_eireann_client",
    "met_office_uk_client",
    "met_office_datahub_client",
    "met_office_climate_client",
    # Celtic Language & Pronunciation clients
    "canuint_client",
    "gaois_client",
]
