import {
  createColumnHelper,
  flexRender,
  getCoreRowModel,
  useReactTable,
} from "@tanstack/react-table";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { ChevronLeft, ChevronRight, Info } from "lucide-react";
import { trpc } from "@/router";
import { useSuspenseQuery } from "@tanstack/react-query";
import { useNavigate } from "@tanstack/react-router";
import { useState } from "react";

type Evaluation = {
  id: string;
  linkId: string;
  accountId: string;
  destinationUrl: string;
  status: string;
  reason: string;
  createdAt: string;
};

export function EvaluationsTable() {
  const navigate = useNavigate();
  const [createdBefore, setCreatedBefore] = useState<string | undefined>(
    undefined,
  );
  const [paginationHistory, setPaginationHistory] = useState<string[]>([]);

  const { data: evaluationsData } = useSuspenseQuery(
    trpc.evaluations.recentEvaluations.queryOptions({
      createdBefore: createdBefore,
    }),
  );

  const evaluations = evaluationsData.data;
  const columnHelper = createColumnHelper<Evaluation>();

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const getStatusDisplay = (status: string) => {
    const statusConfig = {
      AVAILABLE_PRODUCT: {
        label: "Available",
        classes: "bg-green-100 text-green-800 border-green-200",
      },
      NOT_AVAILABLE_PRODUCT: {
        label: "Not Available",
        classes: "bg-red-100 text-red-800 border-red-200",
      },
      UNKNOWN_STATUS: {
        label: "Unknown",
        classes: "bg-gray-100 text-gray-800 border-gray-200",
      },
    };

    const config = statusConfig[status as keyof typeof statusConfig] || {
      label: status,
      classes: "bg-gray-100 text-gray-800 border-gray-200",
    };

    return config;
  };

  const columns = [
    columnHelper.accessor("createdAt", {
      header: "Created At",
      cell: (info) => (
        <div className="text-sm text-muted-foreground">
          {formatDate(info.getValue())}
        </div>
      ),
    }),
    columnHelper.accessor("status", {
      header: "Status",
      cell: (info) => {
        const status = info.getValue();
        const statusDisplay = getStatusDisplay(status);
        return (
          <span
            className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${statusDisplay.classes}`}
          >
            {statusDisplay.label}
          </span>
        );
      },
    }),
    columnHelper.accessor("reason", {
      header: "Reason",
      cell: (info) => (
        <TooltipProvider>
          <Tooltip>
            <TooltipTrigger>
              <Info className="h-4 w-4 text-muted-foreground hover:text-foreground transition-colors" />
            </TooltipTrigger>
            <TooltipContent>
              <p>{info.getValue()}</p>
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>
      ),
    }),
    columnHelper.accessor("destinationUrl", {
      header: "Destination URL",
      cell: (info) => {
        const url = info.getValue();
        return (
          <div
            className="text-sm font-medium text-ellipsis overflow-hidden max-w-[200px] text-blue-600 hover:text-blue-800 cursor-pointer underline"
            onClick={(e) => {
              e.stopPropagation();
              window.open(url, "_blank");
            }}
          >
            {url}
          </div>
        );
      },
    }),
  ];

  const table = useReactTable({
    data: evaluations,
    columns,
    getCoreRowModel: getCoreRowModel(),
  });

  const handleNextPage = () => {
    if (evaluationsData.oldestCreatedAt) {
      setPaginationHistory((prev) => [...prev, createdBefore || ""]);
      setCreatedBefore(evaluationsData.oldestCreatedAt);
    }
  };

  const handlePreviousPage = () => {
    if (paginationHistory.length > 0) {
      const newHistory = [...paginationHistory];
      const previousCreatedBefore = newHistory.pop();
      setPaginationHistory(newHistory);
      setCreatedBefore(
        previousCreatedBefore === "" ? undefined : previousCreatedBefore,
      );
    }
  };

  return (
    <div className="space-y-4">
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            {table.getHeaderGroups().map((headerGroup) => (
              <TableRow key={headerGroup.id}>
                {headerGroup.headers.map((header) => (
                  <TableHead className="pl-4" key={header.id}>
                    {header.isPlaceholder
                      ? null
                      : flexRender(
                          header.column.columnDef.header,
                          header.getContext(),
                        )}
                  </TableHead>
                ))}
              </TableRow>
            ))}
          </TableHeader>
          <TableBody>
            {table.getRowModel().rows?.length ? (
              table.getRowModel().rows.map((row) => (
                <TableRow
                  key={row.id}
                  data-state={row.getIsSelected() && "selected"}
                  className="cursor-pointer hover:bg-muted/50"
                  onClick={() => {
                    navigate({
                      to: "/app/link/$id",
                      params: { id: row.original.linkId },
                    });
                  }}
                >
                  {row.getVisibleCells().map((cell) => (
                    <TableCell key={cell.id}>
                      {flexRender(
                        cell.column.columnDef.cell,
                        cell.getContext(),
                      )}
                    </TableCell>
                  ))}
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell
                  colSpan={columns.length}
                  className="h-24 text-center"
                >
                  No evaluations found.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>

      <div className="flex items-center justify-between px-2">
        <div className="flex-1 text-sm text-muted-foreground">
          Showing {evaluations.length} entries
        </div>
        <div className="flex items-center space-x-2">
          <Button
            variant="outline"
            size="sm"
            onClick={handlePreviousPage}
            disabled={paginationHistory.length === 0}
          >
            <ChevronLeft className="h-4 w-4" />
            Previous
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={handleNextPage}
            disabled={
              !evaluationsData.oldestCreatedAt || evaluations.length <= 10
            }
          >
            Next
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  );
}
