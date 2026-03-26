import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { X, Search } from "lucide-react";
import iso31661 from "iso-3166-1";
import { DestinationsSchemaType } from "@repo/data-ops/zod-schema/links";
import { queryClient, trpc } from "@/router";
import { useMutation } from "@tanstack/react-query";
import { toast } from "sonner";
import { useState, useMemo } from "react";
import { AnimatePresence, motion } from "framer-motion";

interface GeographicDestinationsListProps {
  linkId: string;
  destinations: DestinationsSchemaType;
}

export function GeographicDestinationsList({
  linkId,
  destinations,
}: GeographicDestinationsListProps) {
  const [searchQuery, setSearchQuery] = useState("");

  const updateDestinationMutation = useMutation(
    trpc.links.updateLinkDestinations.mutationOptions({
      onSuccess: () => {
        queryClient.invalidateQueries({
          queryKey: trpc.links.getLink.queryKey({
            linkId,
          }),
        });
        toast.success("Removed destination successfully");
      },
      onError: () => {
        toast.error("Failed to remove destination");
      },
    }),
  );

  const removeDestination = (countryCode: string) => {
    const updatedDestinations = { ...destinations };
    delete updatedDestinations[countryCode];

    updateDestinationMutation.mutate({
      linkId,
      destinations: updatedDestinations,
    });
  };

  const countries = iso31661.all();

  const getCountryNameByCode = (code: string) => {
    const country = countries.find((c) => c.alpha2 === code);
    return country?.country || code;
  };

  // Get all country codes except 'default' and sort by country name
  const sortedCountryEntries = useMemo(() => {
    const countryEntries = Object.entries(destinations).filter(
      ([key]) => key !== "default",
    );

    return countryEntries.sort(([codeA], [codeB]) => {
      const nameA = getCountryNameByCode(codeA);
      const nameB = getCountryNameByCode(codeB);
      return nameA.localeCompare(nameB);
    });
  }, [destinations]);

  // Filter by search query
  const filteredCountryEntries = useMemo(() => {
    if (!searchQuery) return sortedCountryEntries;

    return sortedCountryEntries.filter(([countryCode]) => {
      const countryName = getCountryNameByCode(countryCode);
      return countryName.toLowerCase().includes(searchQuery.toLowerCase());
    });
  }, [sortedCountryEntries, searchQuery]);

  const showSearch = sortedCountryEntries.length > 5;

  return (
    <div className="space-y-3">
      <Label className="text-sm font-medium">Country-Specific Routes</Label>
      {showSearch && (
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
          <Input
            placeholder="Search countries..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10"
          />
        </div>
      )}
      <AnimatePresence mode="popLayout">
        {filteredCountryEntries.map(([countryCode, url]) => (
          <motion.div
            key={countryCode}
            layout
            initial={{ opacity: 0, height: 0, marginBottom: 0 }}
            animate={{ opacity: 1, height: "auto", marginBottom: 12 }}
            exit={{ opacity: 0, height: 0, marginBottom: 0 }}
            transition={{
              duration: 0.3,
              ease: "easeInOut",
              layout: { duration: 0.2 },
            }}
            className="flex items-center gap-3 p-4 rounded-lg border bg-muted/50 overflow-hidden"
          >
            <Badge variant="secondary">
              {getCountryNameByCode(countryCode)}
            </Badge>
            <div className="flex-1 font-mono text-sm text-muted-foreground  px-3 py-2 rounded border">
              {url}
            </div>
            <Button
              variant="ghost"
              size="sm"
              disabled={updateDestinationMutation.isPending}
              onClick={() => removeDestination(countryCode)}
              className="text-destructive hover:text-destructive hover:bg-destructive/10"
            >
              <X className="w-4 h-4" />
            </Button>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
}
