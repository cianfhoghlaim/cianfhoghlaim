import * as cloudflare from "@pulumi/cloudflare";
import * as pulumi from "@pulumi/pulumi";

const config = new pulumi.Config();
const zoneId = config.requireSecret("cloudflareZoneId");

// The user wants to block access to these domains unless from permitted regions.
// We will apply this to the overarching zone, assuming these domains share the same zone 
// or implement a filter based on the hostnames.

const allowedCountries = [
    "IE", // Republic of Ireland
    "GB", // United Kingdom (includes Northern Ireland)
    // European Union (Except Hungary HU and Serbia RS)
    "AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR", "DE", "GR", "IT", "LV", "LT", "LU", "MT", "NL", "PL", "PT", "RO", "SK", "SI", "ES", "SE",
    // Note: 'British Isles' and 'Commonwealth' are vast and not all map neatly to Cloudflare 2-letter country codes cleanly without exhaustive lists.
    // For now, representing core EU, UK, Ireland, plus specified Asian nations and US.
    "US", // United States of America
    "CN", // China
    "JP", // Japan
    "KR", // South Korea
    "TW", // Taiwan
    "NP", // Nepal
    // Tibet is CN
];

const blockWafRule = new cloudflare.Ruleset("geo-restriction-rule", {
    kind: "zone",
    name: "Restrict access to permitted regions",
    description: "Blocks access to cianlyons.co.uk, ciandeacy.co.uk, cianfhoghlaim.ie, crypteolas.ie from unauthorized regions",
    phase: "http_request_firewall_custom",
    zoneId: zoneId,
    rules: [
        {
            action: "block",
            expression: `(http.host in {"cianlyons.co.uk" "ciandeacy.co.uk" "cianfhoghlaim.ie" "crypteolas.ie"}) and not (ip.geoip.country in {${allowedCountries.map(c => `"${c}"`).join(" ")}})`,
            description: "Block unpermitted regions",
            enabled: true,
        },
    ],
});

export const wafRuleId = blockWafRule.id;
