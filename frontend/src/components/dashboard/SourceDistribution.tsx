import { useNavigate } from "react-router-dom";
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from "recharts";
import { FEEDBACK_SOURCES } from "../../types/feedback";
import type { SourceBreakdownResponse } from "../../services/analyticsApi";

interface SourceDistributionProps {
  data: SourceBreakdownResponse | null;
  loading: boolean;
}

const SOURCE_COLORS: Record<string, string> = {
  blue: "#3b82f6",
  indigo: "#6366f1",
  orange: "#f97316",
  green: "#22c55e",
  teal: "#14b8a6",
  purple: "#a855f7",
  pink: "#ec4899",
  gray: "#6b7280",
  cyan: "#06b6d4",
  red: "#ef4444",
  yellow: "#eab308",
};

export function SourceDistribution({ data, loading }: SourceDistributionProps) {
  const navigate = useNavigate();
  if (loading) {
    return <div className="rounded-lg border border-gray-600 bg-gray-800/50 h-64 animate-pulse" />;
  }
  const breakdown = data?.breakdown ?? [];
  const chartData = breakdown.map((b) => {
    const def = FEEDBACK_SOURCES.find((s) => s.id === b.source);
    return { name: def?.label ?? b.source, value: b.count, source: b.source, percentage: b.percentage };
  });

  const handleClick = (entry: { source: string }) => {
    if (entry.source) navigate(`/feedback?source=${encodeURIComponent(entry.source)}`);
  };

  return (
    <div className="rounded-lg border border-gray-600 bg-gray-800/50 p-4 relative">
      <h3 className="text-sm font-medium text-gray-300">Source Distribution</h3>
      <p className="text-xs text-gray-400 mt-0.5 mb-2">Shows where feedback comes from: App Store, support, NPS surveys, etc. Each slice = one channel. Click to filter.</p>
      {chartData.length === 0 ? (
        <p className="text-gray-500 text-sm py-8">No data for this period</p>
      ) : (
        <>
        <div className="rounded border border-gray-600 bg-gray-900/80 px-2 py-1.5 text-xs mb-2 max-h-24 overflow-y-auto">
          <p className="font-medium text-gray-300 mb-1">Color = Source:</p>
          <div className="flex flex-wrap gap-x-3 gap-y-0.5">
            {chartData.map((d) => (
              <span key={d.source} className="flex items-center gap-1.5 text-gray-200">
                <span
                  className="w-2.5 h-2.5 rounded shrink-0"
                  style={{ backgroundColor: SOURCE_COLORS[FEEDBACK_SOURCES.find((s) => s.id === d.source)?.color ?? "gray"] ?? "#6b7280" }}
                />
                {d.name}
              </span>
            ))}
          </div>
        </div>
        <ResponsiveContainer width="100%" height={220}>
          <PieChart>
            <Pie
              data={chartData}
              cx="50%"
              cy="50%"
              innerRadius={50}
              outerRadius={80}
              dataKey="value"
              nameKey="name"
              onClick={(e) => handleClick(e)}
              cursor="pointer"
            >
              {chartData.map((d, i) => (
                <Cell
                  key={i}
                  fill={SOURCE_COLORS[FEEDBACK_SOURCES.find((s) => s.id === d.source)?.color ?? "gray"] ?? "#6b7280"}
                />
              ))}
            </Pie>
            <Tooltip
              contentStyle={{ backgroundColor: "#1f2937", border: "1px solid #4b5563" }}
              formatter={(value: number, _name: string, props: { payload: { percentage: number } }) => [
                `${value} (${props.payload.percentage}%)`,
                "Count",
              ]}
            />
          </PieChart>
        </ResponsiveContainer>
        </>
      )}
    </div>
  );
}
