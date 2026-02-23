import { useNavigate } from "react-router-dom";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from "recharts";
import type { SegmentBreakdownResponse } from "../../services/analyticsApi";

interface SegmentBreakdownProps {
  data: SegmentBreakdownResponse | null;
  loading: boolean;
}

const SEGMENT_COLORS = ["#6366f1", "#8b5cf6", "#ec4899", "#f59e0b"];

export function SegmentBreakdown({ data, loading }: SegmentBreakdownProps) {
  const navigate = useNavigate();
  if (loading) {
    return <div className="rounded-lg border border-gray-600 bg-gray-800/50 h-64 animate-pulse" />;
  }
  const segments = data?.segments ?? [];
  const chartData = segments.map((s) => ({ segment: s.segment, count: s.count }));

  const handleClick = (entry: { segment: string }) => {
    navigate(`/feedback?segment=${encodeURIComponent(entry.segment)}`);
  };

  return (
    <div className="rounded-lg border border-gray-600 bg-gray-800/50 p-4 relative">
      <h3 className="text-sm font-medium text-gray-300">Feedback by Segment</h3>
      <p className="text-xs text-gray-400 mt-0.5 mb-2">Shows feedback count per customer segment (e.g. Enterprise, SMB). Each bar = one segment.</p>
      {chartData.length === 0 ? (
        <p className="text-gray-500 text-sm py-8">No data for this period</p>
      ) : (
        <>
        <div className="rounded border border-gray-600 bg-gray-900/80 px-2 py-1.5 text-xs mb-2">
          <p className="font-medium text-gray-300 mb-1">Bar color = Segment:</p>
          <div className="flex flex-wrap gap-x-3 gap-y-0.5">
            {chartData.map((d, i) => (
              <span key={d.segment} className="flex items-center gap-1.5 text-gray-200">
                <span className="w-2.5 h-2.5 rounded shrink-0" style={{ backgroundColor: SEGMENT_COLORS[i % SEGMENT_COLORS.length] }} />
                {d.segment}
              </span>
            ))}
          </div>
        </div>
        <ResponsiveContainer width="100%" height={220}>
          <BarChart data={chartData} margin={{ top: 5, right: 5, left: 0, bottom: 5 }}>
            <XAxis dataKey="segment" stroke="#6b7280" tick={{ fontSize: 11 }} />
            <YAxis stroke="#6b7280" tick={{ fontSize: 11 }} allowDecimals={false} />
            <Tooltip
              contentStyle={{ backgroundColor: "#1f2937", border: "1px solid #4b5563" }}
              formatter={(value: number) => [value, "Count"]}
            />
            <Bar dataKey="count" radius={[4, 4, 0, 0]} onClick={(e: { segment: string }) => handleClick(e)} cursor="pointer">
              {chartData.map((_, i) => (
                <Cell key={i} fill={SEGMENT_COLORS[i % SEGMENT_COLORS.length]} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
        </>
      )}
    </div>
  );
}
