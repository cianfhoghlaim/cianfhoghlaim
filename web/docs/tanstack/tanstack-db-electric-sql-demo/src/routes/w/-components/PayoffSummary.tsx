import { Card, CardContent } from '@/components/ui/card';
import { PayoffScheduleResult } from '@/lib/universal/payoff';
import { Temporal } from '@js-temporal/polyfill';
import {
  Area,
  AreaChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { DollarSign } from 'lucide-react';

interface PayoffSummaryProps {
  payoffSchedule: PayoffScheduleResult;
}

export function PayoffSummary({ payoffSchedule }: PayoffSummaryProps) {
  let previousPaidOffDebts = new Set<string>();

  const data = payoffSchedule.months.map((m) => {
    const currentPaidOffDebts = new Set(
      m.payments.filter((p) => p.newBalance.eq(0)).map((p) => p.debtId),
    );

    const newlyPaidOffDebts = [...currentPaidOffDebts].filter(
      (id) => !previousPaidOffDebts.has(id),
    );

    previousPaidOffDebts = currentPaidOffDebts;

    return {
      date: m.date,
      balance: m.remainingBalance.toNumber(),
      displayDate: Temporal.PlainYearMonth.from(m.date)
        .toPlainDate({ day: 1 })
        .toLocaleString('en-US', { month: 'short', year: '2-digit' }),
      fullDisplayDate: Temporal.PlainYearMonth.from(m.date)
        .toPlainDate({ day: 1 })
        .toLocaleString('en-US', { month: 'long', year: 'numeric' }),
      isStartOfYear: m.date.endsWith('-01'),
      newlyPaidOffCount: newlyPaidOffDebts.length,
      totalPaidOffCount: currentPaidOffDebts.size,
    };
  });

  const startOfYearDates = data
    .filter((d) => d.isStartOfYear)
    .map((d) => d.date);

  const CustomDot = (props: any) => {
    const { cx, cy, payload } = props;

    if (!payload.newlyPaidOffCount) return null;

    return (
      <g transform={`translate(${cx - 10},${cy - 10})`}>
        <circle
          cx="10"
          cy="10"
          r="10"
          fill="oklch(72.3% 0.219 149.579)"
          stroke="white"
          strokeWidth="2"
        />
        <text
          x="10"
          y="10"
          dy="0.35em"
          textAnchor="middle"
          fill="white"
          fontSize="12px"
          fontWeight="bold"
          style={{ pointerEvents: 'none' }}
        >
          $
        </text>
      </g>
    );
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      {/* Debt Free Date */}
      <Card className="border-0 bg-gradient-to-br from-green-500 to-green-700 text-white rounded-2xl overflow-hidden relative">
        <div className="absolute top-0 right-0 -mt-4 -mr-4 w-24 h-24 bg-white/10 rounded-full blur-2xl"></div>
        <div className="absolute bottom-0 left-0 -mb-4 -ml-4 w-20 h-20 bg-black/10 rounded-full blur-xl"></div>
        <CardContent className="px-6 py-3 relative z-10">
          <div className="text-teal-100 text-sm font-medium mb-1">
            Debt Free By
          </div>
          <div className="text-3xl font-bold tracking-tight">
            {Temporal.PlainYearMonth.from(payoffSchedule.debtFreeDate)
              .toPlainDate({ day: 1 })
              .toLocaleString('en-US', {
                month: 'short',
                year: 'numeric',
              })}
          </div>
          <div className="mt-1 text-teal-200 text-sm font-medium">
            Pay off in{' '}
            {payoffSchedule.monthsToPayoff > 24
              ? `${(payoffSchedule.monthsToPayoff / 12).toFixed(1)} years`
              : `${payoffSchedule.monthsToPayoff} ${
                  payoffSchedule.monthsToPayoff === 1 ? 'month' : 'months'
                }`}
          </div>
        </CardContent>
      </Card>

      {/* Total Interest */}
      <Card className="border border-border shadow-none bg-card rounded-2xl overflow-hidden">
        <CardContent className="px-6 py-3">
          <div className="text-muted-foreground text-sm font-medium mb-1">
            Total Interest
          </div>
          <div className="text-3xl font-bold text-foreground tracking-tight">
            {payoffSchedule.totalInterestPaid
              .toNumber()
              .toLocaleString('en-US', {
                style: 'currency',
                currency: 'USD',
                maximumFractionDigits: 0,
              })}
          </div>
          <div className="mt-1 text-muted-foreground text-sm font-medium">
            Estimated cost
          </div>
        </CardContent>
      </Card>

      {/* Payoff Graph */}
      <Card className="border border-border shadow-none bg-card rounded-2xl overflow-hidden flex flex-col">
        <CardContent className="px-6 pt-3 pb-0 flex-1 min-h-[60px] flex flex-col">
          <div className="text-muted-foreground text-sm font-medium">
            Payoff Timeline
          </div>
          <div className="flex-1 -ml-4 min-h-[60px]">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart
                data={data}
                margin={{ top: 15, right: 20, left: 20, bottom: 10 }}
              >
                <defs>
                  <linearGradient id="colorBalance" x1="0" y1="0" x2="0" y2="1">
                    <stop
                      offset="5%"
                      stopColor="oklch(72.3% 0.219 149.579)"
                      stopOpacity={0.2}
                    />
                    <stop
                      offset="95%"
                      stopColor="oklch(72.3% 0.219 149.579)"
                      stopOpacity={0}
                    />
                  </linearGradient>
                </defs>
                <XAxis dataKey="date" hide axisLine={false} tickLine={false} />
                <YAxis hide domain={['auto', 'auto']} />
                <Tooltip
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      const dataPoint = payload[0].payload;
                      return (
                        <div className="bg-popover border border-border shadow-lg rounded-lg p-2 text-xs">
                          <p className="font-medium text-foreground mb-1">
                            {dataPoint.fullDisplayDate}
                          </p>
                          <p className="text-muted-foreground">
                            Balance:{' '}
                            <span className="font-mono font-medium text-foreground">
                              {dataPoint.balance.toLocaleString('en-US', {
                                style: 'currency',
                                currency: 'USD',
                                maximumFractionDigits: 0,
                              })}
                            </span>
                          </p>
                          {dataPoint.newlyPaidOffCount > 0 && (
                            <p className="text-green-600 font-medium mt-1 flex items-center gap-1">
                              <DollarSign className="w-3 h-3" />
                              {dataPoint.totalPaidOffCount} debt
                              {dataPoint.totalPaidOffCount !== 1
                                ? 's'
                                : ''}{' '}
                              paid off!
                            </p>
                          )}
                        </div>
                      );
                    }
                    return null;
                  }}
                />
                <ReferenceLine
                  y={0}
                  stroke="currentColor"
                  strokeOpacity={0.1}
                />
                {startOfYearDates.map((date) => (
                  <ReferenceLine
                    key={date}
                    x={date}
                    stroke="currentColor"
                    strokeOpacity={0.1}
                    strokeDasharray="3 3"
                  />
                ))}
                <Area
                  type="monotone"
                  dataKey="balance"
                  stroke="oklch(72.3% 0.219 149.579)"
                  strokeWidth={2}
                  fillOpacity={1}
                  fill="url(#colorBalance)"
                  isAnimationActive={false}
                  dot={<CustomDot />}
                  activeDot={{ r: 6, strokeWidth: 0 }}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
