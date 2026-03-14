/**
 * Data Table Component
 *
 * Displays tabular data from agent responses.
 * Rendered by agents via AG-UI GenerativeUI events.
 */

import { cn } from "../../../lib/utils";
import type { AgentComponentProps } from "../ComponentRegistry";

interface Column {
  key: string;
  label: string;
  width?: string;
}

interface DataTableProps extends AgentComponentProps {
  title?: string;
  columns: Column[];
  rows: Record<string, unknown>[];
  emptyMessage?: string;
}

export default function DataTable({
  title,
  columns,
  rows,
  emptyMessage = "No data available",
}: DataTableProps) {
  if (!rows || rows.length === 0) {
    return (
      <div className="rounded-lg border bg-muted/50 p-8 text-center">
        <p className="text-sm text-muted-foreground">{emptyMessage}</p>
      </div>
    );
  }

  return (
    <div className="rounded-lg border overflow-hidden">
      {title && (
        <div className="bg-muted px-4 py-2 border-b">
          <h3 className="font-medium text-sm">{title}</h3>
        </div>
      )}
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-muted/50">
            <tr>
              {columns.map((col) => (
                <th
                  key={col.key}
                  className={cn(
                    "px-4 py-2 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider",
                    col.width && `w-[${col.width}]`
                  )}
                >
                  {col.label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y">
            {rows.map((row, rowIndex) => (
              <tr key={rowIndex} className="hover:bg-muted/50">
                {columns.map((col) => (
                  <td
                    key={col.key}
                    className="px-4 py-3 text-sm whitespace-nowrap"
                  >
                    {String(row[col.key] ?? "-")}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="bg-muted/30 px-4 py-2 border-t">
        <p className="text-xs text-muted-foreground">
          Showing {rows.length} {rows.length === 1 ? "row" : "rows"}
        </p>
      </div>
    </div>
  );
}
