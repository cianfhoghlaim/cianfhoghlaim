import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Globe } from "lucide-react";
import {
  ComposableMap,
  Geographies,
  Geography,
  Marker,
} from "react-simple-maps";
import { useGeoClickStore } from "@/hooks/geo-clicks-store";
import { groupClicksByMile } from "@/lib/utils";

export function ActiveAreasMap() {
  const { clicks } = useGeoClickStore();

  const groupedClicks = groupClicksByMile(clicks);

  return (
    <Card className="lg:col-span-1 hover:shadow-md transition-all duration-200">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Globe className="h-5 w-5" />
          Active Areas
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-96 bg-muted/30 rounded-lg border border-border relative overflow-hidden">
          <ComposableMap
            projection="geoMercator"
            projectionConfig={{
              scale: 100,
              center: [0, 20],
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
            {groupedClicks.map((group, index) => {
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
