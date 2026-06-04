import { MapPin } from "lucide-react";
import { GeographicDestinationsList } from "./geographic-destinations-list";
import { AddDestinationForm } from "./add-destination-form";

import { DestinationsSchemaType } from "@repo/data-ops/zod-schema/links";

interface GeoRoutingSectionProps {
  destinations: DestinationsSchemaType;
  linkId: string;
  geoToggle: boolean;
}

export function GeoRoutingSection({
  destinations,
  linkId,
  geoToggle,
}: GeoRoutingSectionProps) {
  const usedCountryCodes = Object.keys(destinations);

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2 text-sm font-medium text-foreground">
        <MapPin className="w-4 h-4" />
        Geographic Destinations
      </div>

      {geoToggle && (
        <>
          <AddDestinationForm
            usedCountryCodes={usedCountryCodes}
            linkId={linkId}
            destinations={destinations}
          />
          <GeographicDestinationsList
            destinations={destinations}
            linkId={linkId}
          />
        </>
      )}
    </div>
  );
}
