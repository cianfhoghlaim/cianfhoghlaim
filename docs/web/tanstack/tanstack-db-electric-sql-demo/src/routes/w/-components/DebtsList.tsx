import { sortBy } from 'es-toolkit';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  cn,
  formatNumber,
  parseNumericInput,
  toNumericValue,
} from '@/lib/client/utils';
import { DebtType } from '@/lib/universal/types';
import Decimal from 'decimal.js';
import { AnimatePresence, Reorder } from 'framer-motion';
import {
  Car,
  CreditCard,
  GraduationCap,
  Home,
  MoreHorizontal,
  Plus,
  Sparkles,
  Trash2,
  User,
  Wallet,
} from 'lucide-react';
import React, { useEffect, useState } from 'react';

export interface WorkbookDebt {
  id: string;
  name: string;
  type: string;
  rate: Decimal;
  balance: Decimal;
  minPayment: Decimal;
}

interface DebtTypeOption {
  value: DebtType;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
}

const debtTypeOptions: DebtTypeOption[] = [
  { value: DebtType.Auto, label: 'Auto', icon: Car },
  { value: DebtType.Home, label: 'Home', icon: Home },
  { value: DebtType.Credit, label: 'Credit', icon: CreditCard },
  { value: DebtType.School, label: 'School', icon: GraduationCap },
  { value: DebtType.Personal, label: 'Personal', icon: User },
  { value: DebtType.Other, label: 'Other', icon: Wallet },
];

interface DebtsListProps {
  debts: WorkbookDebt[];
  newDebtId?: string | null;
  onNewDebtFocused?: () => void;
  onPopulateDemoDebts: () => void;
  onAddDebt: () => void;
  onTypeChange: (debtId: string, newType: DebtType) => void;
  onUpdateDebt: (
    debtId: string,
    field: 'name' | 'balance' | 'minPayment' | 'rate',
    value: string | number,
  ) => void;
  onDeleteDebt: (debtId: string) => void;
}

const EditableCell = ({
  value,
  onSave,
  type = 'text',
  prefix,
  suffix,
  className = '',
  shouldFocus,
  onFocus,
}: {
  value: string | number | Decimal;
  onSave: (val: string | number) => void;
  type?: 'text' | 'number';
  prefix?: string;
  suffix?: string;
  className?: string;
  shouldFocus?: boolean;
  onFocus?: () => void;
}) => {
  const [localValue, setLocalValue] = useState<string | number>(
    toNumericValue(value),
  );
  const [isFocused, setIsFocused] = useState(false);
  const inputRef = React.useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (shouldFocus && inputRef.current) {
      inputRef.current.focus();
      inputRef.current.select();
    }
  }, [shouldFocus]);

  useEffect(() => {
    setLocalValue(toNumericValue(value));
  }, [value]);

  const displayValue = isFocused
    ? String(localValue ?? '')
    : type === 'number'
      ? formatNumber(localValue) || String(localValue ?? '')
      : String(localValue ?? '');

  const handleFocus = () => {
    setIsFocused(true);
    if (onFocus) {
      onFocus();
    }
    if (type === 'number') {
      const num = parseNumericInput(localValue);
      setLocalValue(isNaN(num) ? localValue : num);
    }
  };

  const handleBlur = () => {
    setIsFocused(false);
    const cleanValue =
      type === 'number' ? parseNumericInput(localValue) : localValue;
    const originalValue = toNumericValue(value);

    if (cleanValue !== originalValue) {
      onSave(type === 'number' ? Number(cleanValue) : cleanValue);
    } else {
      setLocalValue(originalValue);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue =
      type === 'number'
        ? e.target.value.replace(/[^\d.-]/g, '')
        : e.target.value;
    setLocalValue(newValue);
  };

  const isRightAligned = className.includes('justify-end');
  const showBackground = type === 'number';

  return (
    <div className={cn('flex items-center group', className)}>
      <div
        className={cn(
          'flex items-center border border-transparent rounded px-1.5 py-0.5 hover:border-border/30 focus-within:border-border/60 transition-colors w-full',
          showBackground && 'bg-muted/30 focus-within:bg-background',
          isRightAligned && 'justify-end',
        )}
      >
        {prefix && (
          <span className="text-muted-foreground text-xs mr-1 select-none">
            {prefix}
          </span>
        )}
        <input
          ref={inputRef}
          type="text"
          value={displayValue}
          onChange={handleChange}
          onFocus={handleFocus}
          onBlur={handleBlur}
          className={cn(
            'bg-transparent border-none p-0 h-auto focus:ring-0 flex-1 text-sm font-medium text-foreground placeholder:text-muted-foreground/50 focus:outline-none min-w-[20px]',
            isRightAligned && 'text-right',
          )}
        />
        {suffix && (
          <span className="text-muted-foreground text-xs ml-1.5 select-none">
            {suffix}
          </span>
        )}
      </div>
    </div>
  );
};

const DebtField = ({
  label,
  value,
  onSave,
  prefix,
  suffix,
}: {
  label: string;
  value: number;
  onSave: (val: number) => void;
  prefix?: string;
  suffix?: string;
}) => (
  <div>
    <EditableCell
      value={value}
      type="number"
      prefix={prefix}
      suffix={suffix}
      onSave={(val) => onSave(val as number)}
      className="text-sm text-foreground/80"
    />
    <div className="text-[10px] font-semibold text-muted-foreground mt-0.5 text-left pl-1.5">
      {label}
    </div>
  </div>
);

const TotalDisplay = ({ label, amount }: { label: string; amount: number }) => (
  <div className="text-right">
    <span className="block font-bold text-foreground">
      {amount.toLocaleString('en-US', {
        style: 'currency',
        currency: 'USD',
        maximumFractionDigits: 0,
      })}
    </span>
    <span className="block text-[10px] font-semibold text-muted-foreground mt-0.5">
      {label}
    </span>
  </div>
);

const RateDisplay = ({ label, rate }: { label: string; rate: number }) => (
  <div className="text-right">
    <span className="block font-bold text-foreground">{rate.toFixed(2)}%</span>
    <span className="block text-[10px] font-semibold text-muted-foreground mt-0.5">
      {label}
    </span>
  </div>
);

export function DebtsList({
  debts,
  newDebtId,
  onNewDebtFocused,
  onPopulateDemoDebts,
  onAddDebt,
  onTypeChange,
  onUpdateDebt,
  onDeleteDebt,
}: DebtsListProps) {
  const sortedDebts = sortBy(debts, [
    (debt) => debt.balance.toNumber() * -1,
    'name',
  ]);

  const totalBalance = debts.reduce(
    (sum, debt) => sum.add(debt.balance),
    new Decimal(0),
  );
  const totalMinPayment = debts.reduce(
    (sum, debt) => sum.add(debt.minPayment),
    new Decimal(0),
  );

  // Calculate weighted average rate
  const weightedRateSum = debts.reduce(
    (sum, debt) => sum.add(debt.rate.mul(debt.balance)),
    new Decimal(0),
  );
  const avgRate = totalBalance.greaterThan(0)
    ? weightedRateSum.div(totalBalance).toNumber()
    : 0;

  const getDebtIcon = (debtType: string) => {
    return (
      debtTypeOptions.find((opt) => opt.value === debtType)?.icon || Wallet
    );
  };

  return (
    <div className="h-full flex flex-col bg-card rounded-2xl border border-border mb-1">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-2 border-b border-border">
        <h2 className="text-base font-semibold text-foreground">Debts</h2>
        <div className="flex gap-2">
          {debts.length === 0 && (
            <Button
              onClick={onPopulateDemoDebts}
              variant="outline"
              size="sm"
              className="h-8 text-xs"
            >
              <Sparkles className="h-3.5 w-3.5 mr-1 text-muted-foreground" />
              Populate Demo
            </Button>
          )}
          <Button
            onClick={onAddDebt}
            variant="ghost"
            size="sm"
            className="h-8 text-xs"
          >
            <Plus className="h-3.5 w-3.5 mr-1" />
            Add Debt
          </Button>
        </div>
      </div>

      {/* Debts List */}
      <div className="flex-1 overflow-y-auto p-0 relative">
        {debts.length === 0 ? (
          <div className="flex flex-col items-center justify-center text-center p-8 text-muted-foreground">
            <p className="text-sm">No debts added yet</p>
          </div>
        ) : (
          <Reorder.Group
            axis="y"
            values={debts}
            onReorder={() => {}} // Read-only reordering for now since order is determined by balance
            className="flex flex-col"
          >
            <AnimatePresence initial={false} mode="popLayout">
              {sortedDebts.map((debt, index) => {
                const Icon = getDebtIcon(debt.type);
                const isLastDebt = index === sortedDebts.length - 1;

                return (
                  <Reorder.Item
                    key={debt.id}
                    value={debt}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    transition={{ duration: 0.2 }}
                    dragListener={false} // Disable manual drag sorting
                    className={cn(
                      'group relative bg-card py-2 px-4 transition-shadow',
                      !isLastDebt && 'border-b border-border',
                    )}
                  >
                    {/* Top Row: Icon, Name, Actions */}
                    <div className="flex items-center gap-3 mb-1">
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <button
                            className="h-8 w-8 rounded-lg bg-muted/30 flex items-center justify-center text-muted-foreground hover:bg-muted hover:text-foreground transition-colors focus:outline-none"
                            title={
                              debtTypeOptions.find(
                                (opt) => opt.value === debt.type,
                              )?.label
                            }
                          >
                            <Icon className="h-4 w-4" />
                          </button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent
                          align="start"
                          className="rounded-xl border-border shadow-lg"
                        >
                          {debtTypeOptions.map((option) => (
                            <DropdownMenuItem
                              key={option.value}
                              onClick={() =>
                                onTypeChange(debt.id, option.value)
                              }
                            >
                              <option.icon className="h-4 w-4 mr-2 text-muted-foreground" />
                              {option.label}
                            </DropdownMenuItem>
                          ))}
                        </DropdownMenuContent>
                      </DropdownMenu>

                      <div className="flex-1 min-w-0">
                        <EditableCell
                          value={debt.name}
                          shouldFocus={debt.id === newDebtId}
                          onFocus={
                            debt.id === newDebtId ? onNewDebtFocused : undefined
                          }
                          onSave={(val) =>
                            onUpdateDebt(debt.id, 'name', val as string)
                          }
                          className="text-sm font-medium text-foreground"
                        />
                      </div>

                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <button className="p-1.5 rounded-md text-muted-foreground hover:bg-muted hover:text-foreground transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 opacity-0 group-hover:opacity-100 focus:opacity-100 data-[state=open]:opacity-100">
                            <MoreHorizontal className="h-4 w-4" />
                          </button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent
                          align="end"
                          className="rounded-xl border-border shadow-lg"
                        >
                          <DropdownMenuItem
                            onClick={() => onDeleteDebt(debt.id)}
                            className="text-destructive focus:text-destructive focus:bg-destructive/10"
                          >
                            <Trash2 className="h-4 w-4 mr-2 text-destructive" />
                            Delete Debt
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </div>

                    {/* Bottom Row: Values */}
                    <div className="grid grid-cols-[minmax(0,1fr)_minmax(0,1fr)_minmax(0,1.4fr)] gap-2 pl-11">
                      <DebtField
                        label="Rate"
                        value={debt.rate.toNumber()}
                        suffix="%"
                        onSave={(val) => onUpdateDebt(debt.id, 'rate', val)}
                      />
                      <DebtField
                        label="Min Payment"
                        value={debt.minPayment.toNumber()}
                        prefix="$"
                        onSave={(val) =>
                          onUpdateDebt(debt.id, 'minPayment', val)
                        }
                      />
                      <DebtField
                        label="Balance"
                        value={debt.balance.toNumber()}
                        prefix="$"
                        onSave={(val) => onUpdateDebt(debt.id, 'balance', val)}
                      />
                    </div>
                  </Reorder.Item>
                );
              })}
            </AnimatePresence>
          </Reorder.Group>
        )}
      </div>

      {/* Totals Footer */}
      {debts.length > 0 && (
        <div className="bg-card border-t border-border p-4 rounded-b-2xl">
          <div className="flex justify-between items-center text-sm">
            <span className="font-medium text-muted-foreground">Total</span>
            <div className="flex gap-6">
              <RateDisplay label="Avg Rate" rate={avgRate} />
              <TotalDisplay
                label="Min Payment"
                amount={totalMinPayment.toNumber()}
              />
              <TotalDisplay label="Balance" amount={totalBalance.toNumber()} />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
