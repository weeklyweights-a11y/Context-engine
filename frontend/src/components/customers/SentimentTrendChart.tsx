import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

interface DataPoint {
  date: string;
  customer: number;
  product: number;
}

interface SentimentTrendChartProps {
  periods?: { date: string; avg_sentiment: number; count: number }[];
  productAverage?: { date: string; avg_sentiment: number }[];
}

export function SentimentTrendChart({ periods = [], productAverage = [] }: SentimentTrendChartProps) {
  const productMap = new Map((productAverage ?? []).map((p) => [p.date, p.avg_sentiment]));
  const data: DataPoint[] = (periods ?? []).map((p) => ({
    date: p.date,
    customer: p.avg_sentiment,
    product: productMap.get(p.date) ?? 0,
  }));

  if (data.length === 0) {
    return (
      <div className="rounded-lg border border-gray-600 bg-gray-800/50 p-6 h-64 flex items-center justify-center text-gray-500">
        No sentiment data yet
      </div>
    );
  }

  return (
    <div className="rounded-lg border border-gray-600 bg-gray-800/50 p-4 h-64">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
          <XAxis dataKey="date" stroke="#9ca3af" fontSize={12} />
          <YAxis stroke="#9ca3af" fontSize={12} domain={[-1, 1]} />
          <Tooltip
            contentStyle={{ backgroundColor: "#1f2937", border: "1px solid #4b5563" }}
            labelStyle={{ color: "#d1d5db" }}
            formatter={(value: number) => [value.toFixed(2), ""]}
            labelFormatter={(label) => `Period: ${label}`}
          />
          <Legend />
          <Line
            type="monotone"
            dataKey="customer"
            name="Customer"
            stroke="#818cf8"
            strokeWidth={2}
            dot={{ fill: "#818cf8" }}
          />
          <Line
            type="monotone"
            dataKey="product"
            name="Product average"
            stroke="#6b7280"
            strokeWidth={1}
            strokeDasharray="5 5"
            dot={{ fill: "#6b7280" }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
