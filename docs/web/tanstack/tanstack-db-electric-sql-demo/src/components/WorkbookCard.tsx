import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { debtsCollection, workbooksCollection } from '@/lib/client/collections';
import { eq, useLiveQuery } from '@tanstack/react-db';
import { Link } from '@tanstack/react-router';
import Decimal from 'decimal.js';
import { BookOpen, MoreHorizontal, Trash2 } from 'lucide-react';
import React from 'react';

interface WorkbookCardProps {
  workbook: {
    id: string;
    name: string;
    updatedAt: string;
  };
}

export function WorkbookCard({ workbook }: WorkbookCardProps) {
  // Query debts for this specific workbook
  const { data: debts } = useLiveQuery((q) =>
    q
      .from({ debt: debtsCollection })
      .where(({ debt }) => eq(debt.workbookId, workbook.id)),
  );

  // Calculate total balance from all debts
  const totalBalance = debts.reduce(
    (sum, debt) => sum.add(debt.balance),
    new Decimal(0),
  );

  const handleDelete = (e: React.MouseEvent) => {
    // Stop propagation to prevent the link from navigating
    e.preventDefault();
    e.stopPropagation();

    if (window.confirm('Are you sure you want to delete this workbook?')) {
      workbooksCollection.delete(workbook.id);
    }
  };

  return (
    <Link to="/w/$id" params={{ id: workbook.id }}>
      <Card className="cursor-pointer hover:shadow-lg transition-shadow group bg-white">
        <CardHeader>
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-100 rounded-lg">
                <BookOpen className="h-6 w-6 text-blue-600" />
              </div>
              <div>
                <CardTitle className="text-xl">{workbook.name}</CardTitle>
                <CardDescription className="text-xs mt-1">
                  Updated{' '}
                  {new Date(workbook.updatedAt).toLocaleDateString('en-US', {
                    month: 'short',
                    day: 'numeric',
                    year: 'numeric',
                  })}
                </CardDescription>
              </div>
            </div>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <button
                  onClick={(e) => {
                    e.preventDefault();
                    e.stopPropagation();
                  }}
                  className="p-1.5 rounded-md text-muted-foreground/50 hover:bg-muted hover:text-foreground transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
                >
                  <MoreHorizontal className="h-5 w-5" />
                </button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem
                  onClick={handleDelete}
                  className="text-destructive focus:text-destructive focus:bg-destructive/10"
                >
                  <Trash2 className="h-4 w-4 mr-2 text-destructive" />
                  Delete
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">Debts</span>
              <span className="font-medium">{debts.length}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">Total Balance</span>
              <span className="font-medium">
                {totalBalance.toNumber().toLocaleString('en-US', {
                  style: 'currency',
                  currency: 'USD',
                })}
              </span>
            </div>
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}
