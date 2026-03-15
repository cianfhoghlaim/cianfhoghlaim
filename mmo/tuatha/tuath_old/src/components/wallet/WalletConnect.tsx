import { useAccount, useConnect, useDisconnect, useBalance } from "wagmi";
import { cn } from "../../lib/utils";

interface WalletConnectProps {
  className?: string;
  variant?: "default" | "compact";
}

export function WalletConnect({
  className,
  variant = "default",
}: WalletConnectProps) {
  const { address, isConnected, chain } = useAccount();
  const { connectors, connect, isPending } = useConnect();
  const { disconnect } = useDisconnect();
  const { data: balance } = useBalance({ address });

  const formatAddress = (addr: string) =>
    `${addr.slice(0, 6)}...${addr.slice(-4)}`;

  const formatBalance = (value: bigint | undefined, decimals: number = 18) => {
    if (!value) return "0";
    const num = Number(value) / Math.pow(10, decimals);
    return num.toFixed(4);
  };

  if (isConnected && address) {
    return (
      <div
        className={cn(
          "flex items-center gap-3 rounded-lg border bg-card p-2",
          className
        )}
      >
        {variant === "default" && (
          <div className="flex items-center gap-2">
            <div className="h-2 w-2 rounded-full bg-green-500" />
            <span className="text-sm text-muted-foreground">
              {chain?.name || "Unknown"}
            </span>
          </div>
        )}

        <div className="flex items-center gap-2">
          {balance && (
            <span className="text-sm font-medium">
              {formatBalance(balance.value)} {balance.symbol}
            </span>
          )}
          <button
            onClick={() => navigator.clipboard.writeText(address)}
            className="rounded bg-muted px-2 py-1 text-sm font-mono hover:bg-muted/80"
            title="Click to copy address"
          >
            {formatAddress(address)}
          </button>
        </div>

        <button
          onClick={() => disconnect()}
          className="rounded-lg border px-3 py-1 text-sm hover:bg-destructive hover:text-destructive-foreground"
        >
          Disconnect
        </button>
      </div>
    );
  }

  return (
    <div className={cn("flex gap-2", className)}>
      {connectors.map((connector) => (
        <button
          key={connector.uid}
          onClick={() => connect({ connector })}
          disabled={isPending}
          className={cn(
            "rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50",
            isPending && "cursor-wait"
          )}
        >
          {isPending ? "Connecting..." : `Connect ${connector.name}`}
        </button>
      ))}
    </div>
  );
}

// Alternative compact button for headers
export function WalletButton() {
  const { address, isConnected } = useAccount();
  const { connectors, connect, isPending } = useConnect();
  const { disconnect } = useDisconnect();

  const formatAddress = (addr: string) =>
    `${addr.slice(0, 6)}...${addr.slice(-4)}`;

  if (isConnected && address) {
    return (
      <button
        onClick={() => disconnect()}
        className="flex items-center gap-2 rounded-lg border bg-card px-3 py-2 text-sm hover:bg-muted"
      >
        <span className="h-2 w-2 rounded-full bg-green-500" />
        <span className="font-mono">{formatAddress(address)}</span>
      </button>
    );
  }

  return (
    <button
      onClick={() => {
        const connector = connectors[0];
        if (connector) connect({ connector });
      }}
      disabled={isPending}
      className="rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
    >
      {isPending ? "..." : "Connect Wallet"}
    </button>
  );
}
