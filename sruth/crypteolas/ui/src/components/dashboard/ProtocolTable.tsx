import React from "react";
import { cn } from "@/lib/utils";
import { ChevronDown, ChevronUp, ArrowRight } from "lucide-react";

export interface Protocol {
  id: string;
  name: string;
  icon?: string;
  tvl: string;
  change24h: number;
  chains: string[];
  category: string;
  status: "active" | "warning" | "risk";
}

interface ProtocolTableProps {
  data: Protocol[];
  onRowClick?: (id: string) => void;
  className?: string;
}

export function ProtocolTable({
  data,
  onRowClick,
  className,
}: ProtocolTableProps) {
  const [sortCol, setSortCol] = React.useState<keyof Protocol>("tvl");
  const [sortDir, setSortDir] = React.useState<"asc" | "desc">("desc");

  const handleSort = (col: keyof Protocol) => {
    if (sortCol === col) {
      setSortDir(sortDir === "asc" ? "desc" : "asc");
    } else {
      setSortCol(col);
      setSortDir("desc");
    }
  };

  const statusColors = {
    active: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
    warning: "bg-yellow-500/10 text-yellow-400 border-yellow-500/20",
    risk: "bg-rose-500/10 text-rose-400 border-rose-500/20",
  };

  return (
    <div
      className={cn(
        "overflow-hidden rounded-xl border border-slate-700 bg-slate-800/50",
        className,
      )}
    >
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead>
            <tr className="border-b border-slate-700 bg-slate-800/80">
              <th className="p-4 font-medium text-slate-400">Protocol</th>
              <th
                className="p-4 font-medium text-slate-400 cursor-pointer hover:text-white transition-colors"
                onClick={() => handleSort("category")}
              >
                Category
              </th>
              <th
                className="p-4 font-medium text-slate-400 cursor-pointer hover:text-white transition-colors text-right"
                onClick={() => handleSort("tvl")}
              >
                <div className="flex items-center justify-end gap-1">
                  TVL
                  {sortCol === "tvl" &&
                    (sortDir === "desc" ? (
                      <ChevronDown className="h-4 w-4" />
                    ) : (
                      <ChevronUp className="h-4 w-4" />
                    ))}
                </div>
              </th>
              <th
                className="p-4 font-medium text-slate-400 cursor-pointer hover:text-white transition-colors text-right"
                onClick={() => handleSort("change24h")}
              >
                <div className="flex items-center justify-end gap-1">
                  24h Change
                  {sortCol === "change24h" &&
                    (sortDir === "desc" ? (
                      <ChevronDown className="h-4 w-4" />
                    ) : (
                      <ChevronUp className="h-4 w-4" />
                    ))}
                </div>
              </th>
              <th className="p-4 font-medium text-slate-400 text-right">
                Status
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-700/50">
            {data.map((row) => (
              <tr
                key={row.id}
                onClick={() => onRowClick?.(row.id)}
                className="group cursor-pointer transition-colors hover:bg-slate-700/30"
              >
                <td className="p-4">
                  <div className="flex items-center gap-3">
                    <div className="h-8 w-8 rounded-full bg-slate-700 flex items-center justify-center text-xs font-bold">
                      {row.name.substring(0, 2)}
                    </div>
                    <div>
                      <div className="font-medium text-white group-hover:text-indigo-300 transition-colors">
                        {row.name}
                      </div>
                      <div className="flex gap-1 mt-0.5">
                        {row.chains.map((chain) => (
                          <span
                            key={chain}
                            className="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700"
                          >
                            {chain}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                </td>
                <td className="p-4 text-slate-300">{row.category}</td>
                <td className="p-4 text-right font-mono text-white">
                  {row.tvl}
                </td>
                <td className="p-4 text-right">
                  <div
                    className={cn(
                      "inline-flex items-center gap-1 font-medium",
                      row.change24h >= 0 ? "text-emerald-400" : "text-rose-400",
                    )}
                  >
                    {row.change24h > 0 ? "+" : ""}
                    {row.change24h}%
                  </div>
                </td>
                <td className="p-4 text-right">
                  <span
                    className={cn(
                      "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
                      statusColors[row.status],
                    )}
                  >
                    {row.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="bg-slate-800/80 p-3 border-t border-slate-700 flex justify-center">
        <button className="text-xs text-slate-400 hover:text-white flex items-center gap-1 transition-colors">
          View all protocols <ArrowRight className="h-3 w-3" />
        </button>
      </div>
    </div>
  );
}
