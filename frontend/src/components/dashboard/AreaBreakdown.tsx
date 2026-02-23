import { useNavigate } from "react-router-dom";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from "recharts";
import type { AreaBreakdownResponse } from "../../services/analyticsApi";

interface AreaBreakdownProps {
  data: AreaBreakdownResponse | null;
  loading: boolean;
}

function sentimentToColor(avg: number): string {
  if (avg >= 0.3) return "#22c55e";
  if (avg >= -0.3) return "#eab308";
  return "#ef4444";
}

export function AreaBreakdown({ data, loading }: AreaBreakdownProps) {
  const navigate = useNavigate();
  if (loading) {
    return <div className="rounded-lg border border-gray-600 bg-gray-800/50 h-64 animate-pulse" />;
  }
  const areas = data?.areas ?? [];

  const handleClick = (entry: { product_area: string }) => {
    navigate(`/feedback?area=${encodeURIComponent(entry.product_area)}`);
  };

  return (
    <div className="rounded-lg border border-gray-600 bg-gray-800/50 p-4 relative">
      <h3 className="text-sm font-medium text-gray-300">Product Area Breakdown</h3>
      <p className="text-xs text-gray-400 mt-0.5 mb-2">Shows how many feedback items each product area (feature) received. Bar color = average customer sentiment for that area.</p>
      <div className="rounded border border-gray-600 bg-gray-900/80 px-2 py-1.5 text-xs text-gray-200 mb-2 inline-block">
        <p className="font-medium text-gray-300 mb-1">Bar colors:</p>
        <div className="flex flex-wrap gap-x-3 gap-y-0.5">
          <span className="flex items-center gap-1.5 text-gray-200"><span className="w-2.5 h-2.5 rounded bg-green-500 shrink-0" /> Green = Positive</span>
          <span className="flex items-center gap-1.5 text-gray-200"><span className="w-2.5 h-2.5 rounded bg-amber-500 shrink-0" /> Amber = Neutral</span>
          <span className="flex items-center gap-1.5 text-gray-200"><span className="w-2.5 h-2.5 rounded bg-red-500 shrink-0" /> Red = Negative</span>
        </div>
      </div>
      {areas.length === 0 ? (
        <p className="text-gray-500 text-sm py-8">No data for this period</p>
      ) : (
        <ResponsiveContainer width="100%" height={Math.max(200, areas.length * 32)}>
          <BarChart data={areas} layout="vertical" margin={{ top: 5, right: 30, left: 80, bottom: 5 }}>
            <XAxis type="number" stroke="#6b7280" tick={{ fontSize: 11 }} allowDecimals={false} />
            <YAxis type="category" dataKey="product_area" stroke="#6b7280" tick={{ fontSize: 11 }} width={70} />
            <Tooltip
              contentStyle={{ backgroundColor: "#1f2937", border: "1px solid #4b5563" }}
              formatter={(value: number, _name: string, props: { payload: { avg_sentiment: number } }) => [
                `${value} (avg sentiment: ${props.payload.avg_sentiment.toFixed(2)})`,
                "Count",
              ]}
            />
            <Bar dataKey="count" radius={[0, 4, 4, 0]} onClick={(e: { product_area: string }) => handleClick(e)} cursor="pointer">
              {areas.map((a, i) => (
                <Cell key={i} fill={sentimentToColor(a.avg_sentiment)} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
