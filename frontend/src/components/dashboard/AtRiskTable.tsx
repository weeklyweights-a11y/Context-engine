import { Link, useNavigate } from "react-router-dom";
import type { AtRiskResponse } from "../../services/analyticsApi";
import { AlertTriangle } from "lucide-react";

interface AtRiskTableProps {
  data: AtRiskResponse | null;
  loading: boolean;
}

function formatCurrency(n: number | undefined): string {
  if (n == null) return "—";
  if (n >= 1_000_000) return `$${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `$${(n / 1_000).toFixed(1)}K`;
  return `$${n.toLocaleString()}`;
}

function healthColor(score: number | undefined): string {
  if (score == null) return "text-gray-400";
  if (score >= 70) return "text-green-400";
  if (score >= 40) return "text-amber-400";
  return "text-red-400";
}

function daysToRenewal(renewalDate: string | undefined): number | null {
  if (!renewalDate) return null;
  const r = new Date(renewalDate);
  const now = new Date();
  now.setHours(0, 0, 0, 0);
  r.setHours(0, 0, 0, 0);
  return Math.ceil((r.getTime() - now.getTime()) / (24 * 60 * 60 * 1000));
}

export function AtRiskTable({ data, loading }: AtRiskTableProps) {
  const navigate = useNavigate();
  if (loading) {
    return <div className="rounded-lg border border-gray-600 bg-gray-800/50 h-48 animate-pulse" />;
  }
  const customers = data?.customers ?? [];

  return (
    <div className="rounded-lg border border-gray-600 bg-gray-800/50 p-4 relative">
      <div className="flex justify-between items-center mb-2">
        <h3 className="text-sm font-medium text-gray-300">At-Risk Customers</h3>
        <Link
          to="/customers?health_max=50"
          className="text-xs text-indigo-400 hover:text-indigo-300"
        >
          View all
        </Link>
      </div>
      <p className="text-xs text-gray-400 mb-2">Customers with health score below 50 or high negative feedback. Click a row to open customer profile.</p>
      <div className="rounded border border-gray-600 bg-gray-900/80 px-2 py-1.5 text-xs mb-3 inline-block">
        <p className="font-medium text-gray-300 mb-1">Health score colors:</p>
        <div className="flex flex-wrap gap-x-3 gap-y-0.5">
          <span className="flex items-center gap-1.5 text-gray-200"><span className="text-green-400">●</span> Green = 70+ (healthy)</span>
          <span className="flex items-center gap-1.5 text-gray-200"><span className="text-amber-400">●</span> Amber = 40–69 (watch)</span>
          <span className="flex items-center gap-1.5 text-gray-200"><span className="text-red-400">●</span> Red = &lt;40 (at-risk)</span>
        </div>
      </div>
      {customers.length === 0 ? (
        <p className="text-gray-500 text-sm py-4">No at-risk customers in this period</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-gray-400 border-b border-gray-600">
                <th className="py-2 pr-2">Company</th>
                <th className="py-2 pr-2">ARR</th>
                <th className="py-2 pr-2">Neg. Feedback</th>
                <th className="py-2 pr-2">Renewal</th>
                <th className="py-2">Health</th>
              </tr>
            </thead>
            <tbody>
              {customers.map((c) => {
                const days = daysToRenewal(c.renewal_date);
                const renewalWarning = days != null && days >= 0 && days <= 60;
                return (
                  <tr
                    key={c.id}
                    className="border-b border-gray-700/50 hover:bg-gray-700/30 cursor-pointer"
                    onClick={() => navigate(`/customers/${c.id}`)}
                  >
                    <td className="py-2 pr-2 text-gray-200">{c.company_name}</td>
                    <td className="py-2 pr-2 text-gray-300">{formatCurrency(c.arr)}</td>
                    <td className="py-2 pr-2 text-gray-300">{c.negative_feedback_count}</td>
                    <td className="py-2 pr-2">
                      <span className={renewalWarning ? "text-amber-400 flex items-center gap-1" : "text-gray-300"}>
                        {renewalWarning && <AlertTriangle size={12} />}
                        {c.renewal_date ? new Date(c.renewal_date).toLocaleDateString() : "—"}
                      </span>
                    </td>
                    <td className={`py-2 font-medium ${healthColor(c.health_score)}`}>
                      {c.health_score ?? "—"}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
