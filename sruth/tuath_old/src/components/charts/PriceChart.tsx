import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";
import { useMemo } from "react";

interface PriceChartProps {
  symbol: string;
  timeframe: "1h" | "1d" | "1w" | "1m";
}

// Mock data - in production, this would come from TanStack Query + API
function generateMockData(points: number = 100) {
  const data = [];
  let price = 3400;

  for (let i = 0; i < points; i++) {
    price = price + (Math.random() - 0.48) * 50;
    data.push({
      timestamp: Date.now() - (points - i) * 3600000,
      price: Math.max(3200, Math.min(3600, price)),
    });
  }

  return data;
}

export function PriceChart({ symbol, timeframe }: PriceChartProps) {
  const data = useMemo(() => generateMockData(100), []);

  const formatXAxis = (timestamp: number) => {
    const date = new Date(timestamp);
    if (timeframe === "1h") {
      return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    }
    return date.toLocaleDateString([], { month: "short", day: "numeric" });
  };

  const formatPrice = (price: number) => `$${price.toLocaleString()}`;

  return (
    <ResponsiveContainer width="100%" height="100%">
      <LineChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#333" />
        <XAxis
          dataKey="timestamp"
          tickFormatter={formatXAxis}
          stroke="#888"
          fontSize={12}
        />
        <YAxis
          domain={["auto", "auto"]}
          tickFormatter={formatPrice}
          stroke="#888"
          fontSize={12}
        />
        <Tooltip
          content={({ active, payload }) => {
            if (active && payload && payload.length) {
              const data = payload[0].payload;
              return (
                <div className="rounded border bg-card p-2 shadow-lg">
                  <p className="text-sm font-medium">
                    {formatPrice(data.price)}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {new Date(data.timestamp).toLocaleString()}
                  </p>
                </div>
              );
            }
            return null;
          }}
        />
        <Line
          type="monotone"
          dataKey="price"
          stroke="#10b981"
          strokeWidth={2}
          dot={false}
          activeDot={{ r: 4, fill: "#10b981" }}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
