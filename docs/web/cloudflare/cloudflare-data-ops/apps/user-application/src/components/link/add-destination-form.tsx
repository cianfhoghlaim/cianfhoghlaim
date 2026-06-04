import { useState } from "react";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
} from "@/components/ui/command";
import { Plus, Check, ChevronsUpDown } from "lucide-react";
import { cn } from "@/lib/utils";
import iso31661 from "iso-3166-1";
import { DestinationsSchemaType } from "@repo/data-ops/zod-schema/links";
import { queryClient, trpc } from "@/router";
import { useMutation } from "@tanstack/react-query";
import { toast } from "sonner";

interface AddDestinationFormProps {
  usedCountryCodes: string[];
  linkId: string;
  destinations: DestinationsSchemaType;
}

export function AddDestinationForm({
  usedCountryCodes,
  linkId,
  destinations,
}: AddDestinationFormProps) {
  const [newCountry, setNewCountry] = useState("");
  const [newUrl, setNewUrl] = useState("");
  const [open, setOpen] = useState(false);

  const countries = iso31661.all();
  const availableCountries = countries.filter(
    (country) => !usedCountryCodes.includes(country.alpha2),
  );

  const selectedCountry = availableCountries.find(
    (country) => country.alpha2 === newCountry,
  );

  const updateDestinationMutation = useMutation(
    trpc.links.updateLinkDestinations.mutationOptions({
      onSuccess: () => {
        queryClient.invalidateQueries({
          queryKey: trpc.links.getLink.queryKey({
            linkId,
          }),
        });
        toast.success("Destination added successfully");
      },
      onError: () => {
        toast.error("Failed to add destination");
      },
    }),
  );

  const addGeoDestination = () => {
    if (newCountry && newUrl) {
      const newDest = {
        ...destinations,
        [newCountry]: newUrl,
      };
      updateDestinationMutation.mutate({
        linkId: linkId,
        destinations: newDest,
      });
      setNewCountry("");
      setNewUrl("");
    }
  };

  if (availableCountries.length === 0) {
    return (
      <div className="text-center py-4 text-muted-foreground text-sm">
        All available countries have been assigned destinations
      </div>
    );
  }

  return (
    <Card className="border-dashed border-2 bg-muted/30">
      <CardContent className="pt-6">
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label className="text-sm font-medium">Country</Label>
              <Popover open={open} onOpenChange={setOpen}>
                <PopoverTrigger asChild>
                  <Button
                    variant="outline"
                    role="combobox"
                    aria-expanded={open}
                    className="w-full justify-between h-10"
                  >
                    {selectedCountry
                      ? selectedCountry.country
                      : "Select country..."}
                    <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
                  </Button>
                </PopoverTrigger>
                <PopoverContent className="w-full p-0">
                  <Command>
                    <CommandInput placeholder="Search countries..." />
                    <CommandEmpty>No country found.</CommandEmpty>
                    <CommandGroup className="max-h-64 overflow-auto">
                      {availableCountries.map((country) => (
                        <CommandItem
                          key={country.alpha2}
                          value={country.country}
                          onSelect={() => {
                            setNewCountry(
                              country.alpha2 === newCountry
                                ? ""
                                : country.alpha2,
                            );
                            setOpen(false);
                          }}
                        >
                          <Check
                            className={cn(
                              "mr-2 h-4 w-4",
                              newCountry === country.alpha2
                                ? "opacity-100"
                                : "opacity-0",
                            )}
                          />
                          {country.country}
                        </CommandItem>
                      ))}
                    </CommandGroup>
                  </Command>
                </PopoverContent>
              </Popover>
            </div>
            <div className="space-y-2">
              <Label className="text-sm font-medium">Destination URL</Label>
              <Input
                type="url"
                placeholder="https://example.com"
                value={newUrl}
                onChange={(e) => setNewUrl(e.target.value)}
                className="h-10"
              />
            </div>
          </div>
          <Button
            onClick={addGeoDestination}
            disabled={
              !newCountry || !newUrl || updateDestinationMutation.isPending
            }
            className="w-full h-10"
          >
            <Plus className="w-4 h-4 mr-2" />
            Add Destination
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
