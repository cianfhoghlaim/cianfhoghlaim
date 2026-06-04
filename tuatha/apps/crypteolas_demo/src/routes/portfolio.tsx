import { createFileRoute } from "@tanstack/react-router";
import { usePortfolioStore } from "../stores/portfolio";
import { MetricCard } from "../components/ui/MetricCard";
import { PriceChart } from "../components/charts/PriceChart";
import { cn } from "../lib/utils";

export const Route = createFileRoute("/portfolio")({
  component: PortfolioPage,
});

function PortfolioPage() {
  const { assets, totalValue, selectedAsset, selectAsset, refreshPrices } =
    usePortfolioStore();

  const formatCurrency = (value: number) =>
    new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
      minimumFractionDigits: 2,
    }).format(value);

  const formatNumber = (value: number, decimals = 4) =>
    new Intl.NumberFormat("en-US", {
      minimumFractionDigits: 0,
      maximumFractionDigits: decimals,
    }).format(value);

  const calculateAllocation = (asset: (typeof assets)[0]) => {
    const assetValue = asset.balance * asset.price;
    return totalValue > 0 ? (assetValue / totalValue) * 100 : 0;
  };

  const selectedAssetData = assets.find((a) => a.symbol === selectedAsset);

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Portfolio</h1>
          <p className="text-muted-foreground">
            Track your crypto holdings and performance
          </p>
        </div>
        <button
          onClick={refreshPrices}
          className="rounded-lg border px-4 py-2 hover:bg-muted"
        >
          Refresh Prices
        </button>
      </div>

      {/* Portfolio Summary */}
      <div className="grid gap-4 md:grid-cols-4">
        <MetricCard
          title="Total Value"
          value={formatCurrency(totalValue)}
          change={2.4}
          changeLabel="24h"
        />
        <MetricCard
          title="Total Assets"
          value={assets.length.toString()}
        />
        <MetricCard
          title="Best Performer"
          value="sUSDe"
          change={4.2}
          changeLabel="24h"
        />
        <MetricCard
          title="Worst Performer"
          value="ETH"
          change={-1.3}
          changeLabel="24h"
        />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Asset List */}
        <div className="rounded-lg border bg-card">
          <div className="border-b p-4">
            <h2 className="font-semibold">Holdings</h2>
          </div>
          <div className="divide-y">
            {assets.map((asset) => {
              const value = asset.balance * asset.price;
              const allocation = calculateAllocation(asset);

              return (
                <div
                  key={asset.symbol}
                  onClick={() => selectAsset(asset.symbol)}
                  className={cn(
                    "flex items-center justify-between p-4 cursor-pointer hover:bg-muted/50 transition-colors",
                    selectedAsset === asset.symbol && "bg-muted"
                  )}
                >
                  <div className="flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary/10 text-sm font-bold">
                      {asset.symbol.slice(0, 2)}
                    </div>
                    <div>
                      <p className="font-medium">{asset.name}</p>
                      <p className="text-sm text-muted-foreground">
                        {formatNumber(asset.balance)} {asset.symbol}
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="font-medium">{formatCurrency(value)}</p>
                    <p className="text-sm text-muted-foreground">
                      {allocation.toFixed(1)}% of portfolio
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Selected Asset Details / Chart */}
        <div className="rounded-lg border bg-card">
          {selectedAssetData ? (
            <>
              <div className="border-b p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="font-semibold">{selectedAssetData.name}</h2>
                    <p className="text-sm text-muted-foreground">
                      {selectedAssetData.symbol} on {selectedAssetData.chain}
                    </p>
                  </div>
                  <button
                    onClick={() => selectAsset(null)}
                    className="text-muted-foreground hover:text-foreground"
                  >
                    ✕
                  </button>
                </div>
              </div>
              <div className="p-4 space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-muted-foreground">Balance</p>
                    <p className="text-lg font-semibold">
                      {formatNumber(selectedAssetData.balance)}{" "}
                      {selectedAssetData.symbol}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Value</p>
                    <p className="text-lg font-semibold">
                      {formatCurrency(
                        selectedAssetData.balance * selectedAssetData.price
                      )}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Price</p>
                    <p className="text-lg font-semibold">
                      {formatCurrency(selectedAssetData.price)}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Allocation</p>
                    <p className="text-lg font-semibold">
                      {calculateAllocation(selectedAssetData).toFixed(1)}%
                    </p>
                  </div>
                </div>
                <PriceChart symbol={selectedAssetData.symbol} height={200} />
              </div>
            </>
          ) : (
            <div className="flex h-full items-center justify-center p-8 text-center text-muted-foreground">
              <div>
                <p className="text-lg font-medium">Select an asset</p>
                <p className="text-sm">
                  Click on any holding to view details and price chart
                </p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Allocation Chart */}
      <div className="rounded-lg border bg-card p-4">
        <h2 className="mb-4 font-semibold">Allocation</h2>
        <div className="flex h-8 overflow-hidden rounded-lg">
          {assets.map((asset, index) => {
            const allocation = calculateAllocation(asset);
            const colors = [
              "bg-blue-500",
              "bg-green-500",
              "bg-amber-500",
              "bg-purple-500",
              "bg-pink-500",
            ];
            return (
              <div
                key={asset.symbol}
                className={cn(colors[index % colors.length], "relative")}
                style={{ width: `${allocation}%` }}
                title={`${asset.symbol}: ${allocation.toFixed(1)}%`}
              />
            );
          })}
        </div>
        <div className="mt-4 flex flex-wrap gap-4">
          {assets.map((asset, index) => {
            const colors = [
              "bg-blue-500",
              "bg-green-500",
              "bg-amber-500",
              "bg-purple-500",
              "bg-pink-500",
            ];
            return (
              <div key={asset.symbol} className="flex items-center gap-2">
                <div
                  className={cn("h-3 w-3 rounded-full", colors[index % colors.length])}
                />
                <span className="text-sm">
                  {asset.symbol}: {calculateAllocation(asset).toFixed(1)}%
                </span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
