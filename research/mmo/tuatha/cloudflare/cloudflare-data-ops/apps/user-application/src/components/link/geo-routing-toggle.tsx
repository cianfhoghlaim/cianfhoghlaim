import { useState } from "react";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { DestinationsSchemaType } from "@repo/data-ops/zod-schema/links";
import { Globe } from "lucide-react";
import { useMutation } from "@tanstack/react-query";
import { queryClient, trpc } from "@/router";
import { toast } from "sonner";

interface GeoRoutingToggleProps {
  destinations: DestinationsSchemaType;
  linkId: string;
  setGeoToggle: React.Dispatch<React.SetStateAction<boolean>>;
  geoToggle: boolean;
}

export function GeoRoutingToggle({
  destinations,
  linkId,
  setGeoToggle,
  geoToggle,
}: GeoRoutingToggleProps) {
  const [showConfirmDialog, setShowConfirmDialog] = useState(false);

  const updateDestinationMutation = useMutation(
    trpc.links.updateLinkDestinations.mutationOptions({
      onSuccess: () => {
        queryClient.invalidateQueries({
          queryKey: trpc.links.getLink.queryKey({
            linkId,
          }),
        });
        toast.success("Geo routing updated successfully");
      },
      onError: () => {
        toast.error("Failed to update geo routing");
      },
    }),
  );

  const handleUpdateDestination = (
    updatedDestinations: DestinationsSchemaType,
  ) => {
    updateDestinationMutation.mutate({
      linkId: linkId,
      destinations: updatedDestinations,
    });
  };

  const handleToggle = (checked: boolean) => {
    console.log("hi", checked);
    if (checked) {
      // Enable geo routing
      setGeoToggle(true);
    } else {
      // If turning off geo routing and there are multiple destinations, show confirmation
      if (Object.keys(destinations).length > 1) {
        setShowConfirmDialog(true);
      } else {
        setGeoToggle(false);
      }
    }
  };
  const handleConfirmDisable = () => {
    // Purge all destinations except default
    const defaultOnlyDestinations: DestinationsSchemaType = {
      default: destinations.default,
    };
    handleUpdateDestination(defaultOnlyDestinations);
    setShowConfirmDialog(false);
    setGeoToggle(false);
  };

  return (
    <>
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="space-y-1">
            <Label className="text-sm font-medium flex items-center gap-2">
              <Globe className="w-4 h-4" />
              Geo Routing
            </Label>
            <p className="text-sm text-muted-foreground">
              Route users to different destinations based on their location
            </p>
          </div>
          <Switch checked={geoToggle} onCheckedChange={handleToggle} />
        </div>
      </div>

      <AlertDialog open={showConfirmDialog} onOpenChange={setShowConfirmDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Disable Geo Routing?</AlertDialogTitle>
            <AlertDialogDescription>
              Geo destination links will be removed and only the default
              destination will remain. This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={handleConfirmDisable}>
              Disable Geo Routing
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  );
}
