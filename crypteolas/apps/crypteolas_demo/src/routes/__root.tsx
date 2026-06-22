import { Outlet, createRootRoute, Link } from "@tanstack/react-router";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { WagmiProvider } from "wagmi";
import { CopilotKit } from "@copilotkit/react-core";
import { wagmiConfig } from "../lib/web3";
import { SiweAuth } from "../components/wallet/SiweAuth";
import { X402Provider } from "../lib/x402/provider";
import { PaymentModal } from "../components/payment/PaymentModal";
import { UsageSummary } from "../components/payment/UsageDashboard";
import "../styles/globals.css";

const queryClient = new QueryClient();

export const Route = createRootRoute({
  component: RootLayout,
});

function RootLayout() {
  return (
    <QueryClientProvider client={queryClient}>
      <WagmiProvider config={wagmiConfig}>
        <X402Provider>
          <CopilotKit runtimeUrl="/api/copilot">
            <div className="min-h-screen bg-background">
              <Header />
              <main className="flex">
                <Sidebar />
                <div className="flex-1 p-6">
                  <Outlet />
                </div>
              </main>
              {/* Payment Modal - renders when payment is requested */}
              <PaymentModal />
            </div>
          </CopilotKit>
        </X402Provider>
      </WagmiProvider>
    </QueryClientProvider>
  );
}

function Header() {
  return (
    <header className="border-b bg-card">
      <div className="flex h-16 items-center px-6">
        <div className="flex items-center gap-2">
          <span className="text-xl font-bold">Crypto Analytics</span>
        </div>
        <nav className="ml-8 flex items-center gap-6">
          <Link to="/" className="text-sm font-medium hover:text-primary [&.active]:text-primary">
            Dashboard
          </Link>
          <Link to="/portfolio" className="text-sm font-medium hover:text-primary [&.active]:text-primary">
            Portfolio
          </Link>
          <Link to="/analytics" className="text-sm font-medium hover:text-primary [&.active]:text-primary">
            Analytics
          </Link>
          <Link to="/knowledge" className="text-sm font-medium hover:text-primary [&.active]:text-primary">
            Knowledge
          </Link>
          <Link to="/chat" className="text-sm font-medium hover:text-primary [&.active]:text-primary">
            Chat
          </Link>
        </nav>
        <div className="ml-auto">
          <WalletConnect />
        </div>
      </div>
    </header>
  );
}

function Sidebar() {
  return (
    <aside className="w-64 border-r bg-card p-4">
      <div className="space-y-4">
        {/* Usage Summary - shows free tier remaining */}
        <UsageSummary />

        <div>
          <h3 className="mb-2 text-sm font-semibold">Sessions</h3>
          <div className="space-y-1">
            <button className="w-full rounded-md bg-primary px-3 py-2 text-sm text-primary-foreground">
              + New Chat
            </button>
          </div>
        </div>
        <div>
          <h3 className="mb-2 text-sm font-semibold">Quick Links</h3>
          <div className="space-y-1 text-sm">
            <a href="#" className="block hover:text-primary">
              Ethena (USDe)
            </a>
            <a href="#" className="block hover:text-primary">
              Aave v3
            </a>
            <a href="#" className="block hover:text-primary">
              Pendle
            </a>
          </div>
        </div>
      </div>
    </aside>
  );
}

function WalletConnect() {
  return <SiweAuth />;
}
