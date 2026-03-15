import { useState } from "react";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Edit3, Check } from "lucide-react";
import { DestinationsSchemaType } from "@repo/data-ops/zod-schema/links";
import { trpc } from "@/router";
import { useMutation } from "@tanstack/react-query";

interface DefaultUrlEditorProps {
  destinations: DestinationsSchemaType;
  linkId: string;
  label?: string;
  description?: string;
  onSave?: (url: string) => void;
}

export function DefaultUrlEditor({
  destinations,
  linkId,
  label = "Default URL",
  description = "This URL will be used for visitors from countries not listed below",
  onSave,
}: DefaultUrlEditorProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [url, setUrl] = useState(destinations.default);

  const updateDestinationMutation = useMutation(
    trpc.links.updateLinkDestinations.mutationOptions({
      onSettled: () => {},
    }),
  );

  const handleSave = () => {
    setIsEditing(false);
    updateDestinationMutation.mutate({
      linkId,
      destinations: {
        ...destinations,
        default: url,
      },
    });
    onSave?.(url);
    console.log("Saving default URL...");
  };

  return (
    <div className="space-y-3">
      <Label htmlFor="defaultUrl" className="text-sm font-medium">
        {label}
      </Label>
      {description && (
        <p className="text-sm text-muted-foreground">{description}</p>
      )}
      {isEditing ? (
        <div className="flex items-center gap-2">
          <Input
            id="defaultUrl"
            type="url"
            placeholder="https://example.com"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            className="h-12 text-base flex-1"
          />
          <Button onClick={handleSave} size="sm" className="h-12 px-3">
            <Check className="w-4 h-4" />
          </Button>
        </div>
      ) : (
        <div className="flex items-center gap-3 p-4 rounded-lg border bg-muted/30">
          <code className="text-sm text-muted-foreground flex-1">{url}</code>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsEditing(true)}
            className="h-8 w-8 p-0"
          >
            <Edit3 className="w-4 h-4" />
          </Button>
        </div>
      )}
    </div>
  );
}
