import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import iso31661 from "iso-3166-1";

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { trpc } from "@/router";
import { useSuspenseQuery } from "@tanstack/react-query";
import { Flag } from "lucide-react";

export function TopCountriesTable() {
  const { data: clicksByCountry } = useSuspenseQuery(
    trpc.links.clicksByCountry.queryOptions(),
  );

  const totalClicks = clicksByCountry.reduce(
    (sum, item) => sum + item.count,
    0,
  );

  return (
    <Card className="hover:shadow-md transition-all duration-200 h-64 flex flex-col">
      <CardHeader className="flex-shrink-0">
        <CardTitle className="flex items-center gap-2">
          <Flag className="h-5 w-5" />
          Top Countries
        </CardTitle>
      </CardHeader>
      <CardContent className="flex-1 overflow-hidden">
        <div className="overflow-auto h-full">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Country</TableHead>
                <TableHead className="text-right">Clicks</TableHead>
                <TableHead className="text-right">%</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {clicksByCountry.map((country, index) => (
                <TableRow key={index}>
                  <TableCell className="font-medium">
                    {country.country
                      ? iso31661.whereAlpha2(country.country)?.country ||
                        country.country
                      : "Unknown"}
                  </TableCell>
                  <TableCell className="text-right font-semibold">
                    {country.count}
                  </TableCell>
                  <TableCell className="text-right text-muted-foreground">
                    {totalClicks > 0
                      ? Math.round((country.count / totalClicks) * 100)
                      : 0}
                    %
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
}
