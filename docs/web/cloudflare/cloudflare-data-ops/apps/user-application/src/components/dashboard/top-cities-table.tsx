import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { MapPin } from "lucide-react";

interface City {
  city: string;
  country: string;
  clicks: number;
}

interface TopCitiesTableProps {
  cities: City[];
}
export function TopCitiesTable({ cities }: TopCitiesTableProps) {
  return (
    <Card className="hover:shadow-md transition-all duration-200">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <MapPin className="h-5 w-5" />
          Top Cities
        </CardTitle>
      </CardHeader>
      <CardContent className="overflow-x-auto">
        <div className="min-w-full">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>City</TableHead>
                <TableHead>Country</TableHead>
                <TableHead className="text-right">Clicks</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {cities.map((city, index) => (
                <TableRow key={index}>
                  <TableCell className="font-medium">{city.city}</TableCell>
                  <TableCell className="text-muted-foreground">
                    {city.country}
                  </TableCell>
                  <TableCell className="text-right font-semibold">
                    {city.clicks}
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
