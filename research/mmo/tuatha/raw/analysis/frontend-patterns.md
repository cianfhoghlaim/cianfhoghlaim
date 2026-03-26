# Frontend Patterns for TanStack Start + shadcn

## Executive Summary

Analysis of `/examples/frontend/` reveals reusable patterns from Web3 UI libraries that can be adapted for TanStack Start with shadcn/ui styling. This document provides component specifications and implementation patterns.

---

## 1. Source Examples Analyzed

| Example | Focus | Key Patterns |
|---------|-------|--------------|
| `ant-design-web3/` | Comprehensive Web3 UI | Multi-chain adapters, wallet connect |
| `web3uikit/` | Moralis Web3 components | Copy button, NFT displays |
| `crypto-charts/` | Price visualization | Recharts, Jotai state |
| `cryptocurrency-dashboard/` | Full dashboard | Layout patterns |
| `cryptodashe/` | Real-time portfolio | Socket.io, Zustand |
| `cds/` | Design system | Headless patterns, Tailwind |

---

## 2. Component Specifications for shadcn

### 2.1 WalletConnect Button

**Source Pattern** (ant-design-web3):
- Profile modal integration
- Balance display with coverage options
- Sign-in state management
- Avatar support with fallbacks
- Menu items for copy address and disconnect

**shadcn Implementation:**
```tsx
// components/crypto/wallet-connect.tsx
"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { useWallet } from "@/hooks/use-wallet"
import { Copy, LogOut, Wallet } from "lucide-react"
import { toast } from "sonner"

interface WalletConnectProps {
  onConnect?: () => void
  onDisconnect?: () => void
}

export function WalletConnect({ onConnect, onDisconnect }: WalletConnectProps) {
  const { address, isConnected, balance, connect, disconnect } = useWallet()
  const [isConnecting, setIsConnecting] = useState(false)

  const handleConnect = async () => {
    setIsConnecting(true)
    try {
      await connect()
      onConnect?.()
    } finally {
      setIsConnecting(false)
    }
  }

  const handleCopy = () => {
    navigator.clipboard.writeText(address ?? "")
    toast.success("Address copied to clipboard")
  }

  const truncateAddress = (addr: string) =>
    `${addr.slice(0, 6)}...${addr.slice(-4)}`

  if (!isConnected) {
    return (
      <Button onClick={handleConnect} disabled={isConnecting}>
        <Wallet className="mr-2 h-4 w-4" />
        {isConnecting ? "Connecting..." : "Connect Wallet"}
      </Button>
    )
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" className="gap-2">
          <Avatar className="h-6 w-6">
            <AvatarImage src={`https://effigy.im/a/${address}.svg`} />
            <AvatarFallback>{address?.slice(2, 4)}</AvatarFallback>
          </Avatar>
          <span className="hidden sm:inline">{truncateAddress(address!)}</span>
          <span className="text-muted-foreground">
            {balance?.toFixed(4)} ETH
          </span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuItem onClick={handleCopy}>
          <Copy className="mr-2 h-4 w-4" />
          Copy Address
        </DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem onClick={() => { disconnect(); onDisconnect?.() }}>
          <LogOut className="mr-2 h-4 w-4" />
          Disconnect
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
```

### 2.2 Chain Selector

**Source Pattern** (ant-design-web3 + cds):
- Context-based chain management
- Responsive behavior (Modal on mobile, Popover on desktop)
- Chain info display with icons

**shadcn Implementation:**
```tsx
// components/crypto/chain-selector.tsx
"use client"

import { useState } from "react"
import { Check, ChevronDown } from "lucide-react"
import { Button } from "@/components/ui/button"
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/components/ui/command"
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover"
import { useMediaQuery } from "@/hooks/use-media-query"
import {
  Drawer,
  DrawerContent,
  DrawerTrigger,
} from "@/components/ui/drawer"
import { cn } from "@/lib/utils"

interface Chain {
  id: number
  name: string
  icon: string
  rpcUrl: string
}

const chains: Chain[] = [
  { id: 1, name: "Ethereum", icon: "/chains/ethereum.svg", rpcUrl: "..." },
  { id: 137, name: "Polygon", icon: "/chains/polygon.svg", rpcUrl: "..." },
  { id: 42161, name: "Arbitrum", icon: "/chains/arbitrum.svg", rpcUrl: "..." },
  { id: 10, name: "Optimism", icon: "/chains/optimism.svg", rpcUrl: "..." },
  { id: 8453, name: "Base", icon: "/chains/base.svg", rpcUrl: "..." },
  // Solana handled separately via adapter pattern
]

interface ChainSelectorProps {
  value?: number
  onSelect?: (chain: Chain) => void
}

export function ChainSelector({ value, onSelect }: ChainSelectorProps) {
  const [open, setOpen] = useState(false)
  const isDesktop = useMediaQuery("(min-width: 768px)")
  const selectedChain = chains.find((c) => c.id === value)

  const ChainList = () => (
    <Command>
      <CommandInput placeholder="Search chain..." />
      <CommandList>
        <CommandEmpty>No chain found.</CommandEmpty>
        <CommandGroup>
          {chains.map((chain) => (
            <CommandItem
              key={chain.id}
              value={chain.name}
              onSelect={() => {
                onSelect?.(chain)
                setOpen(false)
              }}
            >
              <img
                src={chain.icon}
                alt={chain.name}
                className="mr-2 h-4 w-4"
              />
              {chain.name}
              <Check
                className={cn(
                  "ml-auto h-4 w-4",
                  value === chain.id ? "opacity-100" : "opacity-0"
                )}
              />
            </CommandItem>
          ))}
        </CommandGroup>
      </CommandList>
    </Command>
  )

  if (!isDesktop) {
    return (
      <Drawer open={open} onOpenChange={setOpen}>
        <DrawerTrigger asChild>
          <Button variant="outline" className="w-[150px] justify-between">
            {selectedChain ? (
              <>
                <img src={selectedChain.icon} className="mr-2 h-4 w-4" />
                {selectedChain.name}
              </>
            ) : (
              "Select chain"
            )}
            <ChevronDown className="ml-2 h-4 w-4 opacity-50" />
          </Button>
        </DrawerTrigger>
        <DrawerContent>
          <div className="mt-4 border-t">
            <ChainList />
          </div>
        </DrawerContent>
      </Drawer>
    )
  }

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button variant="outline" className="w-[150px] justify-between">
          {selectedChain ? (
            <>
              <img src={selectedChain.icon} className="mr-2 h-4 w-4" />
              {selectedChain.name}
            </>
          ) : (
            "Select chain"
          )}
          <ChevronDown className="ml-2 h-4 w-4 opacity-50" />
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-[200px] p-0" align="start">
        <ChainList />
      </PopoverContent>
    </Popover>
  )
}
```

### 2.3 Token Search Command

**Source Pattern** (crypto-charts):
- Desktop vs mobile responsive rendering
- Command dialog with keyboard shortcuts (Cmd+K)
- Drawer component for mobile
- Filter-based token search

**shadcn Implementation:**
```tsx
// components/crypto/token-command.tsx
"use client"

import { useEffect, useState } from "react"
import { useRouter } from "@tanstack/react-router"
import {
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/components/ui/command"
import { useMediaQuery } from "@/hooks/use-media-query"
import { Drawer, DrawerContent, DrawerTrigger } from "@/components/ui/drawer"
import { Button } from "@/components/ui/button"
import { Search } from "lucide-react"

interface Token {
  symbol: string
  name: string
  icon: string
  price: number
  change24h: number
}

interface TokenCommandProps {
  tokens: Token[]
}

export function TokenCommand({ tokens }: TokenCommandProps) {
  const [open, setOpen] = useState(false)
  const router = useRouter()
  const isDesktop = useMediaQuery("(min-width: 768px)")

  // Keyboard shortcut
  useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.key === "k" && (e.metaKey || e.ctrlKey)) {
        e.preventDefault()
        setOpen((open) => !open)
      }
    }
    document.addEventListener("keydown", down)
    return () => document.removeEventListener("keydown", down)
  }, [])

  const handleSelect = (symbol: string) => {
    setOpen(false)
    router.navigate({ to: "/token/$symbol", params: { symbol } })
  }

  const TokenList = () => (
    <>
      <CommandInput placeholder="Search tokens..." />
      <CommandList>
        <CommandEmpty>No tokens found.</CommandEmpty>
        <CommandGroup heading="Tokens">
          {tokens.map((token) => (
            <CommandItem
              key={token.symbol}
              value={`${token.symbol} ${token.name}`}
              onSelect={() => handleSelect(token.symbol)}
            >
              <img src={token.icon} className="mr-2 h-5 w-5 rounded-full" />
              <div className="flex flex-1 items-center justify-between">
                <div>
                  <span className="font-medium">{token.symbol}</span>
                  <span className="ml-2 text-muted-foreground">{token.name}</span>
                </div>
                <div className="text-right">
                  <div>${token.price.toLocaleString()}</div>
                  <div className={token.change24h >= 0 ? "text-green-500" : "text-red-500"}>
                    {token.change24h >= 0 ? "+" : ""}{token.change24h.toFixed(2)}%
                  </div>
                </div>
              </div>
            </CommandItem>
          ))}
        </CommandGroup>
      </CommandList>
    </>
  )

  if (!isDesktop) {
    return (
      <Drawer open={open} onOpenChange={setOpen}>
        <DrawerTrigger asChild>
          <Button variant="outline" size="icon">
            <Search className="h-4 w-4" />
          </Button>
        </DrawerTrigger>
        <DrawerContent>
          <div className="mt-4">
            <TokenList />
          </div>
        </DrawerContent>
      </Drawer>
    )
  }

  return (
    <>
      <Button
        variant="outline"
        className="w-[200px] justify-start text-muted-foreground"
        onClick={() => setOpen(true)}
      >
        <Search className="mr-2 h-4 w-4" />
        Search tokens...
        <kbd className="ml-auto pointer-events-none hidden h-5 select-none items-center gap-1 rounded border bg-muted px-1.5 font-mono text-[10px] font-medium opacity-100 sm:flex">
          <span className="text-xs">⌘</span>K
        </kbd>
      </Button>
      <CommandDialog open={open} onOpenChange={setOpen}>
        <TokenList />
      </CommandDialog>
    </>
  )
}
```

### 2.4 Price Chart

**Source Pattern** (crypto-charts pyth-chart):
- Server-side data resolution
- Recharts with custom axis ticks
- Jotai atom-based state for tooltip
- Animated axis labels with Framer Motion
- Split color gradient for price trends

**shadcn Implementation:**
```tsx
// components/crypto/price-chart.tsx
"use client"

import { useMemo, useState } from "react"
import {
  Area,
  AreaChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { cn } from "@/lib/utils"

interface PricePoint {
  timestamp: number
  price: number
}

interface PriceChartProps {
  symbol: string
  data: PricePoint[]
  className?: string
}

type TimeRange = "1H" | "1D" | "1W" | "1M" | "1Y"

export function PriceChart({ symbol, data, className }: PriceChartProps) {
  const [range, setRange] = useState<TimeRange>("1D")
  const [hoveredPrice, setHoveredPrice] = useState<number | null>(null)

  const filteredData = useMemo(() => {
    const now = Date.now()
    const ranges: Record<TimeRange, number> = {
      "1H": 60 * 60 * 1000,
      "1D": 24 * 60 * 60 * 1000,
      "1W": 7 * 24 * 60 * 60 * 1000,
      "1M": 30 * 24 * 60 * 60 * 1000,
      "1Y": 365 * 24 * 60 * 60 * 1000,
    }
    const cutoff = now - ranges[range]
    return data.filter((d) => d.timestamp >= cutoff)
  }, [data, range])

  const { minPrice, maxPrice, priceChange, priceChangePercent } = useMemo(() => {
    if (filteredData.length === 0) return { minPrice: 0, maxPrice: 0, priceChange: 0, priceChangePercent: 0 }

    const prices = filteredData.map((d) => d.price)
    const min = Math.min(...prices)
    const max = Math.max(...prices)
    const first = filteredData[0].price
    const last = filteredData[filteredData.length - 1].price
    const change = last - first
    const changePercent = (change / first) * 100

    return { minPrice: min, maxPrice: max, priceChange: change, priceChangePercent: changePercent }
  }, [filteredData])

  const currentPrice = hoveredPrice ?? filteredData[filteredData.length - 1]?.price ?? 0
  const isPositive = priceChange >= 0

  return (
    <Card className={cn("w-full", className)}>
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <div>
          <CardTitle className="text-2xl font-bold">{symbol}</CardTitle>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-bold">
              ${currentPrice.toLocaleString(undefined, { maximumFractionDigits: 2 })}
            </span>
            <span className={cn(
              "text-sm font-medium",
              isPositive ? "text-green-500" : "text-red-500"
            )}>
              {isPositive ? "+" : ""}{priceChangePercent.toFixed(2)}%
            </span>
          </div>
        </div>
        <Tabs value={range} onValueChange={(v) => setRange(v as TimeRange)}>
          <TabsList>
            <TabsTrigger value="1H">1H</TabsTrigger>
            <TabsTrigger value="1D">1D</TabsTrigger>
            <TabsTrigger value="1W">1W</TabsTrigger>
            <TabsTrigger value="1M">1M</TabsTrigger>
            <TabsTrigger value="1Y">1Y</TabsTrigger>
          </TabsList>
        </Tabs>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart
            data={filteredData}
            onMouseMove={(e) => {
              if (e.activePayload?.[0]) {
                setHoveredPrice(e.activePayload[0].payload.price)
              }
            }}
            onMouseLeave={() => setHoveredPrice(null)}
          >
            <defs>
              <linearGradient id="priceGradient" x1="0" y1="0" x2="0" y2="1">
                <stop
                  offset="0%"
                  stopColor={isPositive ? "#22c55e" : "#ef4444"}
                  stopOpacity={0.3}
                />
                <stop
                  offset="100%"
                  stopColor={isPositive ? "#22c55e" : "#ef4444"}
                  stopOpacity={0}
                />
              </linearGradient>
            </defs>
            <XAxis
              dataKey="timestamp"
              tickFormatter={(ts) => {
                const date = new Date(ts)
                if (range === "1H" || range === "1D") {
                  return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
                }
                return date.toLocaleDateString([], { month: "short", day: "numeric" })
              }}
              stroke="#888888"
              fontSize={12}
              tickLine={false}
              axisLine={false}
            />
            <YAxis
              domain={[minPrice * 0.99, maxPrice * 1.01]}
              tickFormatter={(val) => `$${val.toLocaleString()}`}
              stroke="#888888"
              fontSize={12}
              tickLine={false}
              axisLine={false}
              width={80}
            />
            <Tooltip
              content={({ payload }) => {
                if (!payload?.[0]) return null
                const { timestamp, price } = payload[0].payload
                return (
                  <div className="rounded-lg border bg-background p-2 shadow-sm">
                    <div className="text-sm text-muted-foreground">
                      {new Date(timestamp).toLocaleString()}
                    </div>
                    <div className="font-bold">
                      ${price.toLocaleString(undefined, { maximumFractionDigits: 2 })}
                    </div>
                  </div>
                )
              }}
            />
            <Area
              type="monotone"
              dataKey="price"
              stroke={isPositive ? "#22c55e" : "#ef4444"}
              strokeWidth={2}
              fill="url(#priceGradient)"
            />
          </AreaChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}
```

### 2.5 Portfolio Card

**Source Pattern** (cryptodashe):
- Real-time value updates via Socket.io
- Zustand store for portfolio state
- USD value calculation from holdings

**shadcn Implementation:**
```tsx
// components/crypto/portfolio-card.tsx
"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import { ArrowDownIcon, ArrowUpIcon, TrendingUp } from "lucide-react"
import { cn } from "@/lib/utils"

interface Position {
  symbol: string
  amount: number
  valueUsd: number
  change24h: number
  icon: string
}

interface PortfolioCardProps {
  positions: Position[]
  totalValueUsd: number
  change24hUsd: number
  change24hPercent: number
  isLoading?: boolean
}

export function PortfolioCard({
  positions,
  totalValueUsd,
  change24hUsd,
  change24hPercent,
  isLoading,
}: PortfolioCardProps) {
  const isPositive = change24hUsd >= 0

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <Skeleton className="h-6 w-24" />
        </CardHeader>
        <CardContent className="space-y-4">
          <Skeleton className="h-10 w-32" />
          <Skeleton className="h-4 w-20" />
          <div className="space-y-2">
            {[1, 2, 3].map((i) => (
              <Skeleton key={i} className="h-12 w-full" />
            ))}
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle className="flex items-center gap-2">
          <TrendingUp className="h-5 w-5" />
          Portfolio
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="mb-4">
          <div className="text-3xl font-bold">
            ${totalValueUsd.toLocaleString(undefined, { maximumFractionDigits: 2 })}
          </div>
          <div className={cn(
            "flex items-center text-sm",
            isPositive ? "text-green-500" : "text-red-500"
          )}>
            {isPositive ? (
              <ArrowUpIcon className="mr-1 h-4 w-4" />
            ) : (
              <ArrowDownIcon className="mr-1 h-4 w-4" />
            )}
            ${Math.abs(change24hUsd).toLocaleString()} ({change24hPercent.toFixed(2)}%)
            <span className="ml-1 text-muted-foreground">24h</span>
          </div>
        </div>

        <div className="space-y-2">
          {positions.map((position) => (
            <div
              key={position.symbol}
              className="flex items-center justify-between rounded-lg border p-3"
            >
              <div className="flex items-center gap-3">
                <img
                  src={position.icon}
                  alt={position.symbol}
                  className="h-8 w-8 rounded-full"
                />
                <div>
                  <div className="font-medium">{position.symbol}</div>
                  <div className="text-sm text-muted-foreground">
                    {position.amount.toLocaleString()} {position.symbol}
                  </div>
                </div>
              </div>
              <div className="text-right">
                <div className="font-medium">
                  ${position.valueUsd.toLocaleString(undefined, { maximumFractionDigits: 2 })}
                </div>
                <div className={cn(
                  "text-sm",
                  position.change24h >= 0 ? "text-green-500" : "text-red-500"
                )}>
                  {position.change24h >= 0 ? "+" : ""}{position.change24h.toFixed(2)}%
                </div>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
```

---

## 3. Multi-Chain Architecture

### Adapter Pattern (from ant-design-web3)

```tsx
// lib/wallet/adapters.ts

// Base adapter interface
interface WalletAdapter {
  name: string
  connect(): Promise<string>  // Returns address
  disconnect(): Promise<void>
  signMessage(message: string): Promise<string>
  getBalance(): Promise<number>
}

// EVM adapter (wagmi-based)
class EVMWalletAdapter implements WalletAdapter {
  name = "evm"

  async connect() {
    // Uses wagmi connect
    const { address } = await connectAsync({ connector: injected() })
    return address
  }

  async getBalance() {
    const balance = await getBalance({ address })
    return parseFloat(formatEther(balance.value))
  }
}

// Solana adapter
class SolanaWalletAdapter implements WalletAdapter {
  name = "solana"

  async connect() {
    // Uses @solana/wallet-adapter-react
    const { publicKey } = useWallet()
    return publicKey?.toBase58() ?? ""
  }

  async getBalance() {
    const connection = new Connection(clusterApiUrl("mainnet-beta"))
    const balance = await connection.getBalance(publicKey)
    return balance / LAMPORTS_PER_SOL
  }
}

// Context for multi-chain support
interface WalletContextValue {
  adapter: WalletAdapter | null
  chain: "evm" | "solana"
  setChain: (chain: "evm" | "solana") => void
  address: string | null
  balance: number
  connect: () => Promise<void>
  disconnect: () => Promise<void>
}

export const WalletContext = createContext<WalletContextValue | null>(null)

export function WalletProvider({ children }: { children: React.ReactNode }) {
  const [chain, setChain] = useState<"evm" | "solana">("evm")
  const [adapter, setAdapter] = useState<WalletAdapter | null>(null)

  useEffect(() => {
    setAdapter(chain === "evm" ? new EVMWalletAdapter() : new SolanaWalletAdapter())
  }, [chain])

  // ... rest of implementation
}
```

---

## 4. Real-Time Data Patterns

### TanStack Query + WebSocket

```tsx
// hooks/use-price-feed.ts
import { useQuery, useQueryClient } from "@tanstack/react-query"
import { useEffect } from "react"

export function usePriceFeed(symbol: string) {
  const queryClient = useQueryClient()

  // Initial fetch
  const query = useQuery({
    queryKey: ["price", symbol],
    queryFn: () => fetchPrice(symbol),
    refetchInterval: 60000, // Fallback polling
  })

  // WebSocket for real-time updates
  useEffect(() => {
    const ws = new WebSocket(`wss://api.example.com/prices/${symbol}`)

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      queryClient.setQueryData(["price", symbol], data)
    }

    return () => ws.close()
  }, [symbol, queryClient])

  return query
}
```

### Restate Integration for Agent Streaming

```tsx
// hooks/use-agent-response.ts
import { useState, useCallback } from "react"

export function useAgentResponse() {
  const [response, setResponse] = useState<string>("")
  const [isStreaming, setIsStreaming] = useState(false)

  const streamResponse = useCallback(async (prompt: string) => {
    setIsStreaming(true)
    setResponse("")

    const eventSource = new EventSource(
      `/api/restate/agent/stream?prompt=${encodeURIComponent(prompt)}`
    )

    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data)
      if (data.type === "partial") {
        setResponse((prev) => prev + data.content)
      } else if (data.type === "final") {
        setResponse(data.content)
        setIsStreaming(false)
        eventSource.close()
      }
    }

    eventSource.onerror = () => {
      setIsStreaming(false)
      eventSource.close()
    }
  }, [])

  return { response, isStreaming, streamResponse }
}
```

---

## 5. TanStack Start Route Patterns

### Route with Chain-Aware Data Loading

```tsx
// routes/dashboard/$chain.tsx
import { createFileRoute } from "@tanstack/react-router"
import { DashboardLayout } from "@/components/layouts/dashboard"
import { fetchPortfolio, fetchPrices } from "@/lib/api"

export const Route = createFileRoute("/dashboard/$chain")({
  component: DashboardPage,
  loader: async ({ params }) => {
    const [portfolio, prices] = await Promise.all([
      fetchPortfolio(params.chain),
      fetchPrices(params.chain),
    ])
    return { portfolio, prices }
  },
})

function DashboardPage() {
  const { chain } = Route.useParams()
  const { portfolio, prices } = Route.useLoaderData()

  return (
    <DashboardLayout>
      <ChainSelector value={chain} />
      <PortfolioCard {...portfolio} />
      <PriceChart data={prices} />
    </DashboardLayout>
  )
}
```

### Server Functions for Wallet Operations

```tsx
// lib/server-functions.ts
import { createServerFn } from "@tanstack/start"

export const fetchPortfolio = createServerFn("GET", async (userId: string) => {
  // Server-side: fetch from database/API
  const portfolio = await db.portfolio.findUnique({ where: { userId } })
  return portfolio
})

export const executeSwap = createServerFn("POST", async (params: SwapParams) => {
  // Server-side: validate and execute
  const result = await restateClient.call("swap", params)
  return result
})
```

---

## 6. Component File Structure

```
web/src/components/crypto/
├── wallet-connect.tsx      # Wallet connection button
├── chain-selector.tsx      # Multi-chain selector
├── token-command.tsx       # Token search command palette
├── price-chart.tsx         # Price visualization
├── portfolio-card.tsx      # Portfolio summary
├── transaction-history.tsx # Transaction list
├── token-balance.tsx       # Single token display
├── swap-form.tsx           # Token swap interface
└── hooks/
    ├── use-wallet.ts       # Wallet state hook
    ├── use-price-feed.ts   # Real-time price hook
    └── use-agent-response.ts # Agent streaming hook
```

---

## 7. Dependencies

```json
{
  "dependencies": {
    "@tanstack/react-query": "^5.x",
    "@tanstack/react-router": "^1.x",
    "recharts": "^2.x",
    "jotai": "^2.x",
    "wagmi": "^2.x",
    "viem": "^2.x",
    "@solana/web3.js": "^1.x",
    "@solana/wallet-adapter-react": "^0.x"
  }
}
```

---

## References

- `/examples/frontend/ant-design-web3/packages/web3/src/connect-button/`
- `/examples/frontend/crypto-charts/components/pyth-chart.tsx`
- `/examples/frontend/cds/packages/web/src/dropdown/`
- `/examples/frontend/cryptodashe/client/src/`
