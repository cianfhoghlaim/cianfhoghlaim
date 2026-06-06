import type { IncomingRequestCfProperties } from "@cloudflare/workers-types";

/**
 * Geolocation data extracted from Cloudflare request context
 */
export interface GeolocationData {
  timezone?: string;
  city?: string;
  country?: string;
  region?: string;
  regionCode?: string;
  colo?: string;
  latitude?: string;
  longitude?: string;
  postalCode?: string;
  metroCode?: string;
  continent?: string;
}

/**
 * Extract geolocation data from Cloudflare request context
 *
 * @param cf - Cloudflare request properties
 * @returns Extracted geolocation data
 */
export function extractGeolocation(cf?: IncomingRequestCfProperties): GeolocationData {
  if (!cf || typeof cf !== "object") {
    return {};
  }

  return {
    timezone: cf.timezone || undefined,
    city: cf.city || undefined,
    country: cf.country || undefined,
    region: cf.region || undefined,
    regionCode: cf.regionCode || undefined,
    colo: cf.colo || undefined,
    latitude: cf.latitude || undefined,
    longitude: cf.longitude || undefined,
    postalCode: cf.postalCode || undefined,
    metroCode: cf.metroCode || undefined,
    continent: cf.continent || undefined,
  };
}

/**
 * Get formatted location string from geolocation data
 *
 * @param geo - Geolocation data
 * @returns Formatted location string (e.g., "San Francisco, CA, United States")
 */
export function formatLocation(geo: GeolocationData): string {
  const parts: string[] = [];

  if (geo.city) parts.push(geo.city);
  if (geo.regionCode) parts.push(geo.regionCode);
  if (geo.country) parts.push(geo.country);

  return parts.join(", ") || "Unknown";
}

/**
 * Get coordinates from geolocation data
 *
 * @param geo - Geolocation data
 * @returns Coordinates object or null if not available
 */
export function getCoordinates(geo: GeolocationData): { lat: number; lon: number } | null {
  if (!geo.latitude || !geo.longitude) {
    return null;
  }

  const lat = parseFloat(geo.latitude);
  const lon = parseFloat(geo.longitude);

  if (isNaN(lat) || isNaN(lon)) {
    return null;
  }

  return { lat, lon };
}

/**
 * Check if request is from a specific country
 *
 * @param cf - Cloudflare request properties
 * @param countryCode - ISO 3166-1 alpha-2 country code (e.g., "US", "GB")
 * @returns True if request is from the specified country
 */
export function isFromCountry(cf?: IncomingRequestCfProperties, countryCode?: string): boolean {
  if (!cf || !countryCode) return false;
  return cf.country === countryCode.toUpperCase();
}

/**
 * Check if request is from a specific region/continent
 *
 * @param cf - Cloudflare request properties
 * @param continent - Continent code (e.g., "NA", "EU", "AS")
 * @returns True if request is from the specified continent
 */
export function isFromContinent(cf?: IncomingRequestCfProperties, continent?: string): boolean {
  if (!cf || !continent) return false;
  return cf.continent === continent.toUpperCase();
}

/**
 * Get distance between two coordinates (Haversine formula)
 *
 * @param lat1 - Latitude of first point
 * @param lon1 - Longitude of first point
 * @param lat2 - Latitude of second point
 * @param lon2 - Longitude of second point
 * @returns Distance in kilometers
 */
export function getDistance(lat1: number, lon1: number, lat2: number, lon2: number): number {
  const R = 6371; // Earth's radius in kilometers
  const dLat = toRad(lat2 - lat1);
  const dLon = toRad(lon2 - lon1);

  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) *
    Math.sin(dLon / 2) * Math.sin(dLon / 2);

  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  const distance = R * c;

  return distance;
}

function toRad(degrees: number): number {
  return degrees * (Math.PI / 180);
}
