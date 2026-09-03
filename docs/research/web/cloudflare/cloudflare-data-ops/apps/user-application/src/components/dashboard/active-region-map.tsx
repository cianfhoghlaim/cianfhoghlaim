import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Globe, ChevronDown } from "lucide-react";
import {
  ComposableMap,
  Geographies,
  Geography,
  Marker,
} from "react-simple-maps";
import { useState, useMemo } from "react";
import countries from "world-countries";
import { useGeoClickStore } from "@/hooks/geo-clicks-store";
import { groupClicksByMile } from "@/lib/utils";

type Region = {
  id: string;
  name: string;
  projection: {
    scale: number;
    center: [number, number];
  };
};

export function ActiveRegionMap() {
  const { clicks } = useGeoClickStore();

  // Create a map of country codes to regions
  const countryToRegion = useMemo(() => {
    const map = new Map<string, string>();
    countries.forEach((country) => {
      map.set(country.cca2, country.region);
    });
    return map;
  }, []);

  const regions: Region[] = [
    {
      id: "Americas",
      name: "Americas",
      projection: { scale: 250, center: [-80, 0] },
    },
    {
      id: "Europe",
      name: "Europe",
      projection: { scale: 350, center: [30, 54] },
    },
    {
      id: "Africa",
      name: "Africa",
      projection: { scale: 400, center: [20, 0] },
    },
    {
      id: "Asia",
      name: "Asia",
      projection: { scale: 300, center: [100, 30] },
    },
    {
      id: "Oceania",
      name: "Oceania",
      projection: { scale: 500, center: [140, -25] },
    },
  ];

  const [selectedRegion, setSelectedRegion] = useState<string>("Americas");

  const currentRegion =
    regions.find((r) => r.id === selectedRegion) || regions[0];

  // Filter clicks by selected region and group them
  const regionClicks = useMemo(() => {
    const filtered = clicks.filter((click) => {
      const region = countryToRegion.get(click.country);
      return region === selectedRegion;
    });
    return groupClicksByMile(filtered);
  }, [clicks, selectedRegion, countryToRegion]);

  return (
    <Card className="lg:col-span-1 hover:shadow-md transition-all duration-200 ">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Globe className="h-5 w-5" />
            {currentRegion.name}
          </CardTitle>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" size="sm">
                {currentRegion.name}
                <ChevronDown className="h-4 w-4 ml-1" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent>
              {regions.map((region) => (
                <DropdownMenuItem
                  key={region.id}
                  onClick={() => setSelectedRegion(region.id)}
                >
                  {region.name}
                </DropdownMenuItem>
              ))}
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </CardHeader>
      <CardContent>
        <div className="h-96 bg-muted/30 rounded-lg border border-border relative overflow-hidden">
          <ComposableMap
            projection="geoMercator"
            projectionConfig={{
              scale: currentRegion.projection.scale,
              center: currentRegion.projection.center,
            }}
            width={800}
            height={400}
            className="w-full h-full"
          >
            <Geographies geography="https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json">
              {({ geographies }) =>
                geographies.map((geo) => (
                  <Geography
                    key={geo.rsmKey}
                    geography={geo}
                    fill="#d1d5db"
                    stroke="#9ca3af"
                    strokeWidth={0.2}
                    style={{
                      default: { outline: "none" },
                      hover: { outline: "none" },
                      pressed: { outline: "none" },
                    }}
                  />
                ))
              }
            </Geographies>
            {regionClicks.map((group, index) => {
              const baseRadius = Math.min(2 + group.count * 0.5, 8);
              const maxRadius = Math.min(5 + group.count * 2, 50);
              const secondMaxRadius = Math.min(4 + group.count * 1.5, 25);

              return (
                <Marker
                  key={index}
                  coordinates={[group.longitude, group.latitude]}
                >
                  <g>
                    <circle
                      r={maxRadius}
                      fill="none"
                      stroke="#ef4444"
                      strokeWidth="1"
                      opacity="0"
                    >
                      <animate
                        attributeName="r"
                        from={baseRadius}
                        to={maxRadius}
                        dur="1.5s"
                        repeatCount="indefinite"
                      />
                      <animate
                        attributeName="opacity"
                        from="0.8"
                        to="0"
                        dur="1.5s"
                        repeatCount="indefinite"
                      />
                    </circle>
                    <circle
                      r={secondMaxRadius}
                      fill="none"
                      stroke="#ef4444"
                      strokeWidth="0.5"
                      opacity="0"
                    >
                      <animate
                        attributeName="r"
                        from={baseRadius}
                        to={secondMaxRadius}
                        dur="1.5s"
                        begin="0.5s"
                        repeatCount="indefinite"
                      />
                      <animate
                        attributeName="opacity"
                        from="0.6"
                        to="0"
                        dur="1.5s"
                        begin="0.5s"
                        repeatCount="indefinite"
                      />
                    </circle>
                    <circle r={baseRadius} fill="#ef4444" />
                  </g>
                </Marker>
              );
            })}
          </ComposableMap>

          {/* Legend */}
          <div className="absolute bottom-2 left-2 text-xs text-muted-foreground">
            <div className="flex items-center gap-1">
              <div className="w-2 h-2 rounded-full bg-red-500"></div>
              <span>Active Users</span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
