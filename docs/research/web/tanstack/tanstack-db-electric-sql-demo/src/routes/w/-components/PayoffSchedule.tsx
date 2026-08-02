import { Button } from '@/components/ui/button';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { cn } from '@/lib/client/utils';
import { PayoffScheduleResult } from '@/lib/universal/payoff';
import { Temporal } from '@js-temporal/polyfill';
import { WorkbookDebt } from './DebtsList';

interface PayoffScheduleProps {
  payoffSchedule: PayoffScheduleResult;
  debts: WorkbookDebt[];
  showAllMonths: boolean;
  onShowAllMonthsChange: (show: boolean) => void;
}

export function PayoffSchedule({
  payoffSchedule,
  debts,
  showAllMonths,
  onShowAllMonthsChange,
}: PayoffScheduleProps) {
  const visibleMonths = showAllMonths
    ? payoffSchedule.months
    : payoffSchedule.months.slice(0, 24);

  const debtMap = new Map(debts.map((debt) => [debt.id, debt]));
  const orderedDebts = payoffSchedule.sortedDebts
    .map((sortedDebt) => debtMap.get(sortedDebt.id))
    .filter((debt): debt is WorkbookDebt => debt !== undefined);

  return (
    <div className="bg-card rounded-2xl overflow-hidden border border-border">
      <div className="px-6 py-4 border-b border-border">
        <h3 className="text-base font-semibold text-foreground">
          Payoff Schedule
        </h3>
      </div>
      <div className="overflow-x-auto">
        <Table>
          <TableHeader>
            <TableRow className="hover:bg-transparent border-b-border">
              <TableHead className="w-32 pl-6 py-3 text-xs font-medium text-muted-foreground">
                Month
              </TableHead>
              {orderedDebts.map((debt) => (
                <TableHead
                  key={debt.id}
                  className="text-center min-w-[120px] py-3 text-xs font-medium text-muted-foreground"
                >
                  {debt.name}
                </TableHead>
              ))}
              <TableHead className="text-center min-w-[120px] bg-muted/30 py-3 text-xs font-bold text-muted-foreground">
                Total
              </TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {visibleMonths.map((month) => {
              const monthDate = Temporal.PlainYearMonth.from(month.date);
              const isJanuary = monthDate.month === 1 && month.month > 0;
              return (
                <TableRow
                  key={month.month}
                  className={cn(
                    'hover:bg-muted/30 border-b-border',
                    isJanuary && 'border-t-2 border-t-foreground/40',
                  )}
                >
                  <TableCell className="font-medium text-sm text-foreground/80 pl-6 py-3">
                    {monthDate.toPlainDate({ day: 1 }).toLocaleString('en-US', {
                      month: 'short',
                      year: 'numeric',
                    })}
                  </TableCell>
                  {orderedDebts.map((debt) => {
                    const payment = month.payments.find(
                      (p) => p.debtId === debt.id,
                    );
                    if (
                      !payment ||
                      (payment.newBalance.eq(0) && payment.payment.eq(0))
                    ) {
                      return (
                        <TableCell key={debt.id} className="text-center py-3">
                          <div className="inline-flex items-center justify-center w-5 h-5 rounded-full bg-green-50 text-green-500">
                            <svg
                              className="w-3 h-3"
                              fill="none"
                              stroke="currentColor"
                              viewBox="0 0 24 24"
                              xmlns="http://www.w3.org/2000/svg"
                            >
                              <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={3}
                                d="M5 13l4 4L19 7"
                              />
                            </svg>
                          </div>
                        </TableCell>
                      );
                    }
                    return (
                      <TableCell key={debt.id} className="text-center py-3">
                        <div className="flex flex-col items-center gap-0.5">
                          <div
                            className={cn(
                              'text-[10px] font-medium px-1.5 py-px rounded-full',
                              payment.isMinimum
                                ? 'bg-muted text-muted-foreground'
                                : 'bg-green-50 text-green-700',
                            )}
                          >
                            {payment.isMinimum
                              ? 'Min'
                              : payment.payment
                                  .toNumber()
                                  .toLocaleString('en-US', {
                                    style: 'currency',
                                    currency: 'USD',
                                    minimumFractionDigits: 0,
                                    maximumFractionDigits: 0,
                                  })}
                          </div>
                          <div className="text-xs font-medium text-foreground">
                            {payment.newBalance
                              .toNumber()
                              .toLocaleString('en-US', {
                                style: 'currency',
                                currency: 'USD',
                                minimumFractionDigits: 0,
                                maximumFractionDigits: 0,
                              })}
                          </div>
                        </div>
                      </TableCell>
                    );
                  })}
                  <TableCell className="text-center bg-muted/30 py-3">
                    <div className="text-sm font-bold text-foreground">
                      {month.remainingBalance
                        .toNumber()
                        .toLocaleString('en-US', {
                          style: 'currency',
                          currency: 'USD',
                          minimumFractionDigits: 0,
                          maximumFractionDigits: 0,
                        })}
                    </div>
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </div>

      {/* Show More/Less Button */}
      {payoffSchedule.months.length > 24 && (
        <div className="p-4 text-center border-t border-border bg-muted/10">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => onShowAllMonthsChange(!showAllMonths)}
            className="rounded-full text-xs font-medium text-muted-foreground hover:text-foreground hover:bg-muted h-8"
          >
            {showAllMonths
              ? 'Show Less'
              : `Show All ${payoffSchedule.months.length} Months`}
          </Button>
        </div>
      )}
    </div>
  );
}
