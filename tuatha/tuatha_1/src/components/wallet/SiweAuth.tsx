/**
 * SIWE (Sign In With Ethereum) Authentication Component
 *
 * Combines wagmi wallet connection with Better Auth SIWE plugin
 * for secure Ethereum-based authentication following ERC-4361
 */

import { useState, useCallback, useEffect } from "react";
import {
  useAccount,
  useConnect,
  useDisconnect,
  useSignMessage,
  useChainId,
} from "wagmi";
import { SiweMessage } from "siwe";
import { authClient } from "../../lib/auth/client";
import { cn } from "../../lib/utils";

interface SiweAuthProps {
  className?: string;
  onAuthSuccess?: (user: unknown) => void;
  onAuthError?: (error: Error) => void;
}

type AuthStatus = "idle" | "connecting" | "signing" | "verifying" | "authenticated" | "error";

export function SiweAuth({
  className,
  onAuthSuccess,
  onAuthError,
}: SiweAuthProps) {
  const [authStatus, setAuthStatus] = useState<AuthStatus>("idle");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [session, setSession] = useState<unknown>(null);

  const { address, isConnected } = useAccount();
  const chainId = useChainId();
  const { connectors, connect, isPending: isConnecting } = useConnect();
  const { disconnect } = useDisconnect();
  const { signMessageAsync } = useSignMessage();

  // Check for existing session on mount
  useEffect(() => {
    async function checkSession() {
      try {
        const { data } = await authClient.getSession();
        if (data?.session) {
          setSession(data);
          setAuthStatus("authenticated");
        }
      } catch (error) {
        console.error("Session check failed:", error);
      }
    }
    checkSession();
  }, []);

  // Perform SIWE authentication after wallet connection
  const performSiweAuth = useCallback(async () => {
    if (!address || !chainId) return;

    try {
      setAuthStatus("signing");
      setErrorMessage(null);

      // 1. Get nonce from server
      const { data: nonceData, error: nonceError } = await authClient.siwe.nonce({
        walletAddress: address,
        chainId,
      });

      if (nonceError || !nonceData?.nonce) {
        throw new Error(nonceError?.message || "Failed to get nonce");
      }

      // 2. Create SIWE message
      const siweMessage = new SiweMessage({
        domain: window.location.host,
        address,
        statement: "Sign in to Crypto Analytics Platform",
        uri: window.location.origin,
        version: "1",
        chainId,
        nonce: nonceData.nonce,
      });

      const message = siweMessage.prepareMessage();

      // 3. Request signature from wallet
      const signature = await signMessageAsync({ message });

      // 4. Verify signature with server
      setAuthStatus("verifying");

      const { data: verifyData, error: verifyError } = await authClient.siwe.verify({
        message,
        signature,
        walletAddress: address,
        chainId,
      });

      if (verifyError) {
        throw new Error(verifyError.message || "Verification failed");
      }

      // 5. Success!
      setSession(verifyData);
      setAuthStatus("authenticated");
      onAuthSuccess?.(verifyData?.user);
    } catch (error) {
      console.error("SIWE authentication failed:", error);
      const errorMsg = error instanceof Error ? error.message : "Authentication failed";
      setErrorMessage(errorMsg);
      setAuthStatus("error");
      onAuthError?.(error instanceof Error ? error : new Error(errorMsg));
    }
  }, [address, chainId, signMessageAsync, onAuthSuccess, onAuthError]);

  // Auto-trigger SIWE auth when wallet connects
  useEffect(() => {
    if (isConnected && address && authStatus === "idle") {
      performSiweAuth();
    }
  }, [isConnected, address, authStatus, performSiweAuth]);

  // Handle wallet connection
  const handleConnect = useCallback(
    async (connectorId: string) => {
      setAuthStatus("connecting");
      const connector = connectors.find((c) => c.uid === connectorId);
      if (connector) {
        connect({ connector });
      }
    },
    [connectors, connect]
  );

  // Handle sign out
  const handleSignOut = useCallback(async () => {
    try {
      await authClient.signOut();
      disconnect();
      setSession(null);
      setAuthStatus("idle");
    } catch (error) {
      console.error("Sign out failed:", error);
    }
  }, [disconnect]);

  // Format address for display
  const formatAddress = (addr: string) =>
    `${addr.slice(0, 6)}...${addr.slice(-4)}`;

  // Render authenticated state
  if (authStatus === "authenticated" && session && address) {
    return (
      <div className={cn("flex items-center gap-3", className)}>
        <div className="flex items-center gap-2 rounded-lg border bg-card px-3 py-2">
          <span className="h-2 w-2 rounded-full bg-green-500" />
          <span className="text-sm font-mono">{formatAddress(address)}</span>
        </div>
        <button
          onClick={handleSignOut}
          className="rounded-lg border px-3 py-2 text-sm hover:bg-destructive hover:text-destructive-foreground"
        >
          Sign Out
        </button>
      </div>
    );
  }

  // Render loading states
  if (authStatus === "connecting" || isConnecting) {
    return (
      <div className={cn("flex items-center gap-2", className)}>
        <div className="h-4 w-4 animate-spin rounded-full border-2 border-primary border-t-transparent" />
        <span className="text-sm text-muted-foreground">Connecting wallet...</span>
      </div>
    );
  }

  if (authStatus === "signing") {
    return (
      <div className={cn("flex items-center gap-2", className)}>
        <div className="h-4 w-4 animate-spin rounded-full border-2 border-primary border-t-transparent" />
        <span className="text-sm text-muted-foreground">Sign message in wallet...</span>
      </div>
    );
  }

  if (authStatus === "verifying") {
    return (
      <div className={cn("flex items-center gap-2", className)}>
        <div className="h-4 w-4 animate-spin rounded-full border-2 border-primary border-t-transparent" />
        <span className="text-sm text-muted-foreground">Verifying signature...</span>
      </div>
    );
  }

  // Render error state
  if (authStatus === "error") {
    return (
      <div className={cn("flex flex-col gap-2", className)}>
        <div className="text-sm text-destructive">{errorMessage}</div>
        <button
          onClick={() => setAuthStatus("idle")}
          className="rounded-lg bg-primary px-4 py-2 text-sm text-primary-foreground hover:bg-primary/90"
        >
          Try Again
        </button>
      </div>
    );
  }

  // Render connect buttons
  return (
    <div className={cn("flex flex-wrap gap-2", className)}>
      {connectors.map((connector) => (
        <button
          key={connector.uid}
          onClick={() => handleConnect(connector.uid)}
          className="flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90"
        >
          <WalletIcon name={connector.name} />
          {connector.name}
        </button>
      ))}
    </div>
  );
}

// Wallet icon component
function WalletIcon({ name }: { name: string }) {
  const iconMap: Record<string, string> = {
    MetaMask: "🦊",
    "Coinbase Wallet": "🔵",
    WalletConnect: "🔗",
    Injected: "💉",
  };

  return <span>{iconMap[name] || "👛"}</span>;
}

// Compact version for headers
export function SiweButton({ className }: { className?: string }) {
  const { address, isConnected } = useAccount();
  const { connectors, connect, isPending } = useConnect();
  const { disconnect } = useDisconnect();

  const formatAddress = (addr: string) =>
    `${addr.slice(0, 6)}...${addr.slice(-4)}`;

  if (isConnected && address) {
    return (
      <button
        onClick={() => disconnect()}
        className={cn(
          "flex items-center gap-2 rounded-lg border bg-card px-3 py-2 text-sm hover:bg-muted",
          className
        )}
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
      className={cn(
        "rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50",
        className
      )}
    >
      {isPending ? "..." : "Connect Wallet"}
    </button>
  );
}

export default SiweAuth;
