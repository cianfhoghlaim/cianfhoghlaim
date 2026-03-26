export interface GeoDestination {
  id: string;
  countryCode: string;
  url: string;
}

export interface LinkData {
  name: string;
  defaultUrl: string;
  isGeoRouted: boolean;
  geoDestinations: GeoDestination[];
}
