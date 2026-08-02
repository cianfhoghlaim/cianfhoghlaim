import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import { Button } from '@/components/ui/button';
import { cn, formatNumber, parseNumericInput } from '@/lib/client/utils';
import { PayoffStrategyType } from '@/lib/universal/types';
import Decimal from 'decimal.js';
import {
  ArrowDownNarrowWide,
  ArrowUpNarrowWide,
  Info,
  MinusCircle,
  PlusCircle,
} from 'lucide-react';
import { useEffect, useState } from 'react';

interface PayoffStrategyProps {
  strategy: PayoffStrategyType;
  onStrategyChange: (strategy: PayoffStrategyType) => void;
  totalMonthlyPayment: Decimal;
  onTotalMonthlyPaymentChange: (value: Decimal) => void;
  totalMinPayment: Decimal;
}

export function PayoffStrategy({
  strategy,
  onStrategyChange,
  totalMonthlyPayment,
  onTotalMonthlyPaymentChange,
  totalMinPayment,
}: PayoffStrategyProps) {
  // Local state to allow free typing without interference
  const [localValue, setLocalValue] = useState(totalMonthlyPayment.toNumber());
  const [isFocused, setIsFocused] = useState(false);

  // Sync local value when prop changes (but not while user is typing)
  useEffect(() => {
    if (!isFocused) {
      setLocalValue(totalMonthlyPayment.toNumber());
    }
  }, [totalMonthlyPayment, isFocused]);

  // Display formatted value when not focused, raw value when focused
  const displayValue = isFocused
    ? String(localValue ?? '')
    : formatNumber(localValue) || String(localValue ?? '');

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value.replace(/[^\d.-]/g, '');
    setLocalValue(newValue as any);
    // Update parent immediately for real-time calculations
    const numValue = newValue === '' ? 0 : parseNumericInput(newValue);
    onTotalMonthlyPaymentChange(new Decimal(numValue));
  };

  const handleFocus = () => {
    setIsFocused(true);
    const num = parseNumericInput(localValue);
    setLocalValue(isNaN(num) ? localValue : num);
  };

  const handleBlur = () => {
    setIsFocused(false);
    // Ensure value is properly formatted on blur
    const numValue = parseNumericInput(localValue);
    if (isNaN(numValue) || numValue < 0) {
      setLocalValue(totalMonthlyPayment.toNumber());
      onTotalMonthlyPaymentChange(totalMonthlyPayment);
    } else {
      setLocalValue(numValue);
      onTotalMonthlyPaymentChange(new Decimal(numValue));
    }
  };

  const handleAdjustment = (amount: number) => {
    const current = parseNumericInput(localValue);
    const safeCurrent = isNaN(current)
      ? totalMonthlyPayment.toNumber()
      : current;
    const next = safeCurrent + amount;
    const constrained = Math.max(next, totalMinPayment.toNumber());

    setLocalValue(constrained);
    onTotalMonthlyPaymentChange(new Decimal(constrained));
  };

  const handleSetToMin = () => {
    const minValue = totalMinPayment.toNumber();
    setLocalValue(minValue);
    onTotalMonthlyPaymentChange(totalMinPayment);
  };

  return (
    <div className="bg-card rounded-2xl p-4 border border-border mt-3">
      <div className="flex items-start gap-4">
        {/* Monthly Budget Input - Left Side */}
        <div className="flex-1 min-w-0">
          <label
            htmlFor="monthly-payment"
            className="text-sm font-medium text-muted-foreground block mb-2"
          >
            Monthly Budget
          </label>
          <div className="flex items-center gap-2 mb-2">
            <div className="relative group flex-1">
              <div className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground font-medium group-focus-within:text-primary transition-colors text-sm">
                $
              </div>
              <input
                id="monthly-payment"
                type="text"
                value={displayValue}
                onChange={handleChange}
                onFocus={handleFocus}
                onBlur={handleBlur}
                className="w-full pl-6 pr-3 py-2 bg-muted/30 border-0 rounded-lg text-base font-semibold text-foreground focus:ring-2 focus:ring-primary/10 focus:bg-muted/50 transition-all outline-none placeholder:text-muted-foreground/50"
              />
            </div>
            <div className="flex items-center gap-0.5">
              <Button
                variant="ghost"
                size="icon"
                onClick={() => handleAdjustment(-50)}
                disabled={
                  parseNumericInput(localValue) <= totalMinPayment.toNumber()
                }
                className="h-8 w-8 rounded-full text-muted-foreground hover:text-foreground"
              >
                <MinusCircle className="h-5 w-5" />
              </Button>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => handleAdjustment(50)}
                className="h-8 w-8 rounded-full text-muted-foreground hover:text-foreground"
              >
                <PlusCircle className="h-5 w-5" />
              </Button>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={handleSetToMin}
              className="text-xs text-muted-foreground font-medium hover:text-foreground transition-colors cursor-pointer"
            >
              Min: ${formatNumber(totalMinPayment)}
            </button>
            {totalMonthlyPayment.gt(0) &&
              totalMonthlyPayment.lt(totalMinPayment) && (
                <p className="text-[10px] text-destructive font-bold bg-destructive/10 px-1.5 py-0.5 rounded-full whitespace-nowrap">
                  Too low
                </p>
              )}
          </div>
        </div>

        {/* Strategy Selector - Right Side */}
        <div className="w-[140px] flex-none">
          <div className="flex items-center gap-1 mb-2">
            <span className="text-sm font-medium text-muted-foreground">
              Strategy
            </span>
            <TooltipProvider>
              <Tooltip delayDuration={300}>
                <TooltipTrigger asChild>
                  <Info className="h-3.5 w-3.5 text-muted-foreground/50 hover:text-muted-foreground cursor-help transition-colors" />
                </TooltipTrigger>
                <TooltipContent
                  side="top"
                  className="max-w-[200px] text-xs p-3"
                >
                  {strategy === PayoffStrategyType.Avalanche
                    ? 'Avalanche focuses on highest interest rates first to save the most money on interest.'
                    : 'Snowball focuses on smallest balances first to build momentum with quick wins.'}
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          </div>

          <div className="flex flex-col gap-2">
            <button
              onClick={() => onStrategyChange(PayoffStrategyType.Avalanche)}
              className={cn(
                'flex items-center gap-2 px-3 py-2 rounded-lg border text-xs font-medium transition-all w-full text-left',
                strategy === PayoffStrategyType.Avalanche
                  ? 'bg-indigo-50 border-indigo-200 text-indigo-700 shadow-none'
                  : 'bg-transparent border-transparent text-muted-foreground hover:bg-muted/50 hover:text-foreground',
              )}
            >
              <ArrowDownNarrowWide
                className={cn(
                  'h-3.5 w-3.5',
                  strategy === PayoffStrategyType.Avalanche
                    ? 'text-indigo-600'
                    : 'text-muted-foreground/70',
                )}
              />
              Avalanche
            </button>
            <button
              onClick={() => onStrategyChange(PayoffStrategyType.Snowball)}
              className={cn(
                'flex items-center gap-2 px-3 py-2 rounded-lg border text-xs font-medium transition-all w-full text-left',
                strategy === PayoffStrategyType.Snowball
                  ? 'bg-indigo-50 border-indigo-200 text-indigo-700 shadow-none'
                  : 'bg-transparent border-transparent text-muted-foreground hover:bg-muted/50 hover:text-foreground',
              )}
            >
              <ArrowUpNarrowWide
                className={cn(
                  'h-3.5 w-3.5',
                  strategy === PayoffStrategyType.Snowball
                    ? 'text-indigo-600'
                    : 'text-muted-foreground/70',
                )}
              />
              Snowball
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
