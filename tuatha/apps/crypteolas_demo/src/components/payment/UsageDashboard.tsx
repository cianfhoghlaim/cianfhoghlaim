/**
 * Usage Dashboard Component
 *
 * Shows current usage, remaining free tier, and payment history.
 */

import { useUsageStore, useDailyUsage, usePayments, useTotalSpent } from "../../stores/usage";
import { useX402 } from "../../lib/x402/provider";
import {
  FEATURE_PRICING,
  getFeaturesByCategory,
  atomicToUsd,
} from "../../lib/x402/pricing";
import {
  MessageSquare,
  Search,
  BarChart3,
  Cpu,
  ExternalLink,
  Clock,
} from "lucide-react";

const categoryIcons = {
  chat: MessageSquare,
  knowledge: Search,
  analytics: BarChart3,
  models: Cpu,
};

const categoryLabels = {
  chat: "Chat",
  knowledge: "Knowledge Graph",
  analytics: "Analytics",
  models: "AI Models",
};

interface UsageBarProps {
  used: number;
  limit: number;
  label: string;
}

function UsageBar({ used, limit, label }: UsageBarProps) {
  const percentage = limit > 0 ? Math.min((used / limit) * 100, 100) : 100;
  const remaining = Math.max(0, limit - used);
  const isUnlimited = limit === 0;

  return (
    <div className="space-y-1">
      <div className="flex justify-between text-xs">
        <span className="text-muted-foreground">{label}</span>
        <span className="font-medium">
          {isUnlimited ? (
            <span className="text-yellow-500">Pay per use</span>
          ) : (
            <>
              {remaining} / {limit} free
            </>
          )}
        </span>
      </div>
      <div className="h-2 rounded-full bg-muted">
        <div
          className={`h-full rounded-full transition-all ${
            percentage >= 100
              ? "bg-red-500"
              : percentage >= 80
                ? "bg-yellow-500"
                : "bg-green-500"
          }`}
          style={{ width: isUnlimited ? "100%" : `${percentage}%` }}
        />
      </div>
    </div>
  );
}

export function UsageDashboard() {
  const { network } = useX402();
  const dailyUsage = useDailyUsage();
  const payments = usePayments();
  const totalSpent = useTotalSpent();
  const { getRemainingFree: _getRemainingFree } = useUsageStore();

  const categories = ["chat", "knowledge", "analytics", "models"] as const;

  // Get recent payments (last 5)
  const recentPayments = payments.slice(-5).reverse();

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-lg font-semibold">Usage & Billing</h2>
        <p className="text-sm text-muted-foreground">
          Track your daily usage and payment history
        </p>
      </div>

      {/* Network info */}
      <div className="rounded-lg border bg-muted/50 p-3">
        <div className="flex items-center justify-between">
          <span className="text-sm text-muted-foreground">Payment Network</span>
          <span className="font-medium">{network.displayName}</span>
        </div>
      </div>

      {/* Usage by category */}
      <div className="space-y-4">
        <h3 className="text-sm font-medium">Today's Usage</h3>

        {categories.map((category) => {
          const Icon = categoryIcons[category];
          const features = getFeaturesByCategory(category);

          return (
            <div key={category} className="rounded-lg border p-4">
              <div className="mb-3 flex items-center gap-2">
                <Icon className="h-4 w-4 text-muted-foreground" />
                <span className="font-medium">{categoryLabels[category]}</span>
              </div>

              <div className="space-y-3">
                {features.map((feature) => (
                  <UsageBar
                    key={feature.id}
                    used={dailyUsage[feature.id] || 0}
                    limit={feature.freeLimit}
                    label={feature.name}
                  />
                ))}
              </div>
            </div>
          );
        })}
      </div>

      {/* Pricing reference */}
      <div className="space-y-3">
        <h3 className="text-sm font-medium">Pricing</h3>
        <div className="rounded-lg border">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b">
                <th className="px-4 py-2 text-left font-medium">Feature</th>
                <th className="px-4 py-2 text-right font-medium">Price</th>
              </tr>
            </thead>
            <tbody>
              {Object.values(FEATURE_PRICING).map((feature) => (
                <tr key={feature.id} className="border-b last:border-0">
                  <td className="px-4 py-2">
                    <div>{feature.name}</div>
                    {feature.freeLimit > 0 && (
                      <div className="text-xs text-muted-foreground">
                        {feature.freeLimit} free/day
                      </div>
                    )}
                  </td>
                  <td className="px-4 py-2 text-right font-mono">
                    {feature.priceUsd}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Total spent */}
      <div className="rounded-lg border bg-primary/5 p-4">
        <div className="flex items-center justify-between">
          <span className="text-sm text-muted-foreground">Total Spent</span>
          <span className="text-xl font-bold">{atomicToUsd(totalSpent)}</span>
        </div>
        <div className="mt-1 text-xs text-muted-foreground">
          {payments.length} transactions
        </div>
      </div>

      {/* Recent payments */}
      {recentPayments.length > 0 && (
        <div className="space-y-3">
          <h3 className="text-sm font-medium">Recent Payments</h3>
          <div className="space-y-2">
            {recentPayments.map((payment, i) => {
              const feature = FEATURE_PRICING[payment.featureId];
              return (
                <div
                  key={`${payment.txHash}-${i}`}
                  className="flex items-center justify-between rounded-lg border p-3"
                >
                  <div className="flex items-center gap-3">
                    <Clock className="h-4 w-4 text-muted-foreground" />
                    <div>
                      <div className="text-sm font-medium">
                        {feature?.name || payment.featureId}
                      </div>
                      <div className="text-xs text-muted-foreground">
                        {new Date(payment.timestamp).toLocaleString()}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-sm">
                      {atomicToUsd(BigInt(payment.amount))}
                    </span>
                    {payment.txHash && (
                      <a
                        href={`${network.explorerUrl}/tx/${payment.txHash}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-muted-foreground hover:text-foreground"
                      >
                        <ExternalLink className="h-3 w-3" />
                      </a>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}

// Compact version for sidebar
export function UsageSummary() {
  const { getRemainingFree } = useUsageStore();
  const totalSpent = useTotalSpent();

  const chatRemaining = getRemainingFree("chat_message");
  const searchRemaining = getRemainingFree("knowledge_search");

  return (
    <div className="space-y-3 rounded-lg border p-3">
      <div className="text-xs font-medium text-muted-foreground">
        Free Tier Today
      </div>

      <div className="space-y-2 text-sm">
        <div className="flex justify-between">
          <span className="flex items-center gap-1">
            <MessageSquare className="h-3 w-3" />
            Chat
          </span>
          <span
            className={
              chatRemaining === 0 ? "text-red-500" : "text-green-500"
            }
          >
            {chatRemaining} left
          </span>
        </div>

        <div className="flex justify-between">
          <span className="flex items-center gap-1">
            <Search className="h-3 w-3" />
            Search
          </span>
          <span
            className={
              searchRemaining === 0 ? "text-red-500" : "text-green-500"
            }
          >
            {searchRemaining} left
          </span>
        </div>
      </div>

      <div className="border-t pt-2">
        <div className="flex justify-between text-xs">
          <span className="text-muted-foreground">Spent today</span>
          <span className="font-mono">{atomicToUsd(totalSpent)}</span>
        </div>
      </div>
    </div>
  );
}
