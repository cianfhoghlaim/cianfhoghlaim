/**
 * TVLChart - Total Value Locked chart component
 *
 * Uses Recharts for data visualization
 */

import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';

interface TVLDataPoint {
  date: string;
  tvl: number;
  change?: number;
}

interface TVLChartProps {
  data: TVLDataPoint[];
  height?: number;
  showChange?: boolean;
  title?: string;
}

export function TVLChart({
  data,
  height = 300,
  showChange = false,
  title,
}: TVLChartProps) {
  const formatTVL = (value: number) => {
    if (value >= 1_000_000_000) {
      return `$${(value / 1_000_000_000).toFixed(1)}B`;
    }
    if (value >= 1_000_000) {
      return `$${(value / 1_000_000).toFixed(1)}M`;
    }
    return `$${value.toLocaleString()}`;
  };

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (!active || !payload?.length) return null;

    return (
      <div className="bg-slate-800 border border-slate-700 rounded-lg p-3 shadow-xl">
        <p className="text-slate-400 text-sm mb-1">{label}</p>
        <p className="text-white font-mono font-medium">
          {formatTVL(payload[0].value)}
        </p>
        {showChange && payload[1] && (
          <p
            className={`text-sm ${
              payload[1].value >= 0 ? 'text-emerald-400' : 'text-red-400'
            }`}
          >
            {payload[1].value >= 0 ? '+' : ''}
            {payload[1].value.toFixed(2)}%
          </p>
        )}
      </div>
    );
  };

  return (
    <div className="w-full">
      {title && (
        <h3 className="text-lg font-semibold text-indigo-300 mb-4">{title}</h3>
      )}
      <ResponsiveContainer width="100%" height={height}>
        <AreaChart
          data={data}
          margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
        >
          <defs>
            <linearGradient id="tvlGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
          <XAxis
            dataKey="date"
            stroke="#64748b"
            fontSize={12}
            tickLine={false}
          />
          <YAxis
            stroke="#64748b"
            fontSize={12}
            tickLine={false}
            tickFormatter={formatTVL}
          />
          <Tooltip content={<CustomTooltip />} />
          <Area
            type="monotone"
            dataKey="tvl"
            stroke="#6366f1"
            strokeWidth={2}
            fillOpacity={1}
            fill="url(#tvlGradient)"
          />
          {showChange && (
            <Legend
              wrapperStyle={{ paddingTop: '20px' }}
              formatter={(value) => (
                <span className="text-slate-400 text-sm">{value}</span>
              )}
            />
          )}
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}

// Multi-protocol TVL comparison chart
interface MultiProtocolData {
  date: string;
  [protocol: string]: string | number;
}

interface MultiProtocolChartProps {
  data: MultiProtocolData[];
  protocols: { name: string; color: string }[];
  height?: number;
  title?: string;
}

export function MultiProtocolTVLChart({
  data,
  protocols,
  height = 400,
  title,
}: MultiProtocolChartProps) {
  const formatTVL = (value: number) => {
    if (value >= 1_000_000_000) {
      return `$${(value / 1_000_000_000).toFixed(1)}B`;
    }
    if (value >= 1_000_000) {
      return `$${(value / 1_000_000).toFixed(1)}M`;
    }
    return `$${value.toLocaleString()}`;
  };

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (!active || !payload?.length) return null;

    return (
      <div className="bg-slate-800 border border-slate-700 rounded-lg p-3 shadow-xl">
        <p className="text-slate-400 text-sm mb-2">{label}</p>
        {payload.map((entry: any, i: number) => (
          <div key={i} className="flex justify-between gap-4 text-sm">
            <span style={{ color: entry.color }}>{entry.name}</span>
            <span className="font-mono text-white">
              {formatTVL(entry.value)}
            </span>
          </div>
        ))}
      </div>
    );
  };

  return (
    <div className="w-full">
      {title && (
        <h3 className="text-lg font-semibold text-indigo-300 mb-4">{title}</h3>
      )}
      <ResponsiveContainer width="100%" height={height}>
        <AreaChart
          data={data}
          margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
        >
          <defs>
            {protocols.map((p) => (
              <linearGradient
                key={p.name}
                id={`gradient-${p.name}`}
                x1="0"
                y1="0"
                x2="0"
                y2="1"
              >
                <stop offset="5%" stopColor={p.color} stopOpacity={0.3} />
                <stop offset="95%" stopColor={p.color} stopOpacity={0} />
              </linearGradient>
            ))}
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
          <XAxis
            dataKey="date"
            stroke="#64748b"
            fontSize={12}
            tickLine={false}
          />
          <YAxis
            stroke="#64748b"
            fontSize={12}
            tickLine={false}
            tickFormatter={formatTVL}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend
            wrapperStyle={{ paddingTop: '20px' }}
            formatter={(value) => (
              <span className="text-slate-300 text-sm">{value}</span>
            )}
          />
          {protocols.map((p) => (
            <Area
              key={p.name}
              type="monotone"
              dataKey={p.name}
              stroke={p.color}
              strokeWidth={2}
              fillOpacity={1}
              fill={`url(#gradient-${p.name})`}
              stackId="1"
            />
          ))}
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}

// Simple sparkline for inline display
interface SparklineProps {
  data: number[];
  width?: number;
  height?: number;
  color?: string;
  showChange?: boolean;
}

export function TVLSparkline({
  data,
  width = 100,
  height = 30,
  color = '#6366f1',
  showChange = true,
}: SparklineProps) {
  if (data.length === 0) return null;

  const max = Math.max(...data);
  const min = Math.min(...data);
  const range = max - min || 1;

  const points = data
    .map((value, i) => {
      const x = (i / (data.length - 1)) * width;
      const y = height - ((value - min) / range) * height;
      return `${x},${y}`;
    })
    .join(' ');

  const change = ((data[data.length - 1] - data[0]) / data[0]) * 100;
  const changeColor = change >= 0 ? '#22c55e' : '#ef4444';

  return (
    <div className="flex items-center gap-2">
      <svg width={width} height={height} className="overflow-visible">
        <polyline
          fill="none"
          stroke={color}
          strokeWidth="2"
          points={points}
        />
      </svg>
      {showChange && (
        <span
          className="text-xs font-medium"
          style={{ color: changeColor }}
        >
          {change >= 0 ? '+' : ''}
          {change.toFixed(1)}%
        </span>
      )}
    </div>
  );
}

export default TVLChart;
