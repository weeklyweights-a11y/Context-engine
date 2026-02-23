import { useNavigate } from "react-router-dom";
import { useAgentChat } from "../../hooks/useAgentChat";
import type { TopIssuesResponse } from "../../services/analyticsApi";
import { AlertCircle, FileText } from "lucide-react";

interface TopIssuesWidgetProps {
  data: TopIssuesResponse | null;
  loading: boolean;
}

const SEVERITY_COLORS: Record<string, string> = {
  Critical: "bg-red-500/20 text-red-300 border-red-500/40",
  Emerging: "bg-amber-500/20 text-amber-300 border-amber-500/40",
  Stable: "bg-gray-500/20 text-gray-300 border-gray-500/40",
  Improving: "bg-green-500/20 text-green-300 border-green-500/40",
};

export function TopIssuesWidget({ data, loading }: TopIssuesWidgetProps) {
  const { openWithMessage } = useAgentChat();
  const navigate = useNavigate();
  if (loading) {
    return <div className="rounded-lg border border-gray-600 bg-gray-800/50 h-64 animate-pulse" />;
  }
  const issues = data?.issues ?? [];

  const handleInvestigate = (area: string) => {
    openWithMessage(`Tell me more about ${area} issues`);
  };
  const handleGenerateSpec = (area: string) => {
    openWithMessage(`Generate specs for fixing ${area}`);
    navigate("/specs");
  };

  return (
    <div className="rounded-lg border border-gray-600 bg-gray-800/50 p-4 relative">
      <h3 className="text-sm font-medium text-gray-300">Top Issues</h3>
      <p className="text-xs text-gray-400 mt-0.5 mb-2">Most common negative feedback themes. Each badge shows severity of the issue.</p>
      <div className="rounded border border-gray-600 bg-gray-900/80 px-2 py-1.5 text-xs mb-2 inline-block">
        <p className="font-medium text-gray-300 mb-1">Severity badges:</p>
        <div className="flex flex-wrap gap-x-3 gap-y-0.5">
          <span className="flex items-center gap-1.5 text-gray-200"><span className="w-2.5 h-2.5 rounded bg-red-500 shrink-0" /> Critical</span>
          <span className="flex items-center gap-1.5 text-gray-200"><span className="w-2.5 h-2.5 rounded bg-amber-500 shrink-0" /> Emerging</span>
          <span className="flex items-center gap-1.5 text-gray-200"><span className="w-2.5 h-2.5 rounded bg-gray-500 shrink-0" /> Stable</span>
          <span className="flex items-center gap-1.5 text-gray-200"><span className="w-2.5 h-2.5 rounded bg-green-500 shrink-0" /> Improving</span>
        </div>
      </div>
      {issues.length === 0 ? (
        <p className="text-gray-500 text-sm py-4">No negative feedback in this period</p>
      ) : (
        <div className="space-y-3">
          {issues.slice(0, 5).map((issue) => (
            <div key={issue.product_area} className="rounded border border-gray-600 p-3 bg-gray-900/50">
              <div className="flex items-start justify-between gap-2">
                <div>
                  <p className="font-medium text-gray-200">{issue.issue_name}</p>
                  <div className="flex flex-wrap gap-2 mt-1 text-xs">
                    <span className="text-gray-400">{issue.feedback_count} feedback</span>
                    {issue.growth_rate != null && (
                      <span className={issue.growth_rate > 0 ? "text-amber-400" : "text-green-400"}>
                        {issue.growth_rate > 0 ? "+" : ""}{issue.growth_rate}% growth
                      </span>
                    )}
                    <span
                      className={`rounded border px-1.5 py-0.5 ${SEVERITY_COLORS[issue.severity] ?? SEVERITY_COLORS.Stable}`}
                    >
                      {issue.severity}
                    </span>
                  </div>
                  <p className="text-xs text-gray-500 mt-1">
                    {issue.affected_customers} customers affected
                  </p>
                </div>
                <div className="flex gap-1 flex-shrink-0">
                  <button
                    type="button"
                    onClick={() => handleInvestigate(issue.product_area)}
                    className="p-1.5 rounded bg-indigo-600 hover:bg-indigo-500 text-white"
                    title="Investigate"
                  >
                    <AlertCircle size={14} />
                  </button>
                  <button
                    type="button"
                    onClick={() => handleGenerateSpec(issue.product_area)}
                    className="p-1.5 rounded bg-gray-600 hover:bg-gray-500 text-white"
                    title="Generate Spec"
                  >
                    <FileText size={14} />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
