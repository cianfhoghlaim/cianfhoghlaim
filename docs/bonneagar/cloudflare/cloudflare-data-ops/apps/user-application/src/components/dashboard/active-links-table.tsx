import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { formatRelativeTime } from "@/lib/utils";
import { trpc } from "@/router";
import { useSuspenseQuery } from "@tanstack/react-query";
import { useNavigate } from "@tanstack/react-router";
import { MousePointer } from "lucide-react";

export function ActiveLinksTable() {
  const navigate = useNavigate();

  const { data } = useSuspenseQuery(
    trpc.links.activeLinks.queryOptions(undefined, {
      refetchInterval: 5000,
    }),
  );

  return (
    <Card className="hover:shadow-md transition-all duration-200">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <MousePointer className="h-5 w-5" />
          Active Links
        </CardTitle>
      </CardHeader>
      <CardContent>
        {data.length === 0 ? (
          <div className="text-center py-4 text-muted-foreground">
            No link clicks in the last 60 Minutes
          </div>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Name</TableHead>
                <TableHead className="text-right">Clicks</TableHead>
                <TableHead className="text-right">Last Clicked</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {data.map((link, index) => (
                <TableRow
                  key={index}
                  onClick={() =>
                    navigate({
                      to: "/app/link/$id",
                      params: {
                        id: link.linkId,
                      },
                    })
                  }
                  className="cursor-pointer hover:bg-muted"
                >
                  <TableCell className="font-medium">
                    <div className="max-w-xs truncate">{link.name}</div>
                  </TableCell>
                  <TableCell className="text-right font-semibold">
                    {link.clickCount}
                  </TableCell>
                  <TableCell className="text-right text-muted-foreground">
                    {link.lastClicked
                      ? formatRelativeTime(link.lastClicked)
                      : "-"}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </CardContent>
    </Card>
  );
}
