import { useNavigate } from "react-router-dom";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
import type { VolumeResponse } from "../../services/analyticsApi";

interface VolumeChartProps {
  data: VolumeResponse | null;
  loading: boolean;
}

export function VolumeChart({ data, loading }: VolumeChartProps) {
  const navigate = useNavigate();
  if (loading) {
    return <div className="rounded-lg border border-gray-600 bg-gray-800/50 h-64 animate-pulse" />;
  }
  const periods = data?.periods ?? [];
  const chartData = periods.map((p) => ({ date: p.date, count: p.count }));

  const handleClick = (e: { activePayload?: { payload: { date: string; count: number } }[] }) => {
    const payload = e?.activePayload?.[0]?.payload;
    if (payload?.date) {
      navigate(`/feedback?date_from=${payload.date}&date_to=${payload.date}`);
    }
  };

  return (
    <div className="rounded-lg border border-gray-600 bg-gray-800/50 p-4 relative">
      <h3 className="text-sm font-medium text-gray-300">Feedback Volume Over Time</h3>
      <p className="text-xs text-gray-400 mt-0.5 mb-2">Shows how many feedback items you received each day. Click a point to filter feedback by that date.</p>
      <div className="rounded border border-gray-600 bg-gray-900/80 px-2 py-1.5 text-xs mb-2 inline-block">
        <span className="flex items-center gap-1.5 text-gray-200"><span className="w-4 h-0.5 rounded bg-indigo-500 shrink-0" /> Purple line = feedback count per day</span>
      </div>
      {chartData.length === 0 ? (
        <p className="text-gray-500 text-sm py-8">No data for this period</p>
      ) : (
        <ResponsiveContainer width="100%" height={240}>
          <LineChart data={chartData} onClick={handleClick} margin={{ top: 5, right: 5, left: 0, bottom: 0 }}>
            <XAxis dataKey="date" stroke="#6b7280" tick={{ fontSize: 11 }} />
            <YAxis stroke="#6b7280" tick={{ fontSize: 11 }} allowDecimals={false} />
            <Tooltip
              contentStyle={{ backgroundColor: "#1f2937", border: "1px solid #4b5563" }}
              labelStyle={{ color: "#d1d5db" }}
              formatter={(value: number) => [value, "Count"]}
              labelFormatter={(label) => `Date: ${label}`}
            />
            <Line type="monotone" dataKey="count" stroke="#6366f1" strokeWidth={2} dot={{ r: 3 }} />
          </LineChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
