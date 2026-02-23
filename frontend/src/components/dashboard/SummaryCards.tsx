import { Link } from "react-router-dom";
import type { SummaryResponse } from "../../services/analyticsApi";
import { TrendingUp, TrendingDown } from "lucide-react";

interface SummaryCardsProps {
  data: SummaryResponse | null;
  loading: boolean;
}

function formatTrend(trend: number | null): { text: string; up: boolean } | null {
  if (trend == null) return null;
  return { text: `${trend > 0 ? "+" : ""}${trend}%`, up: trend >= 0 };
}

export function SummaryCards({ data, loading }: SummaryCardsProps) {
  if (loading || !data) {
    return (
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="rounded-lg border border-gray-600 bg-gray-800/50 h-24 animate-pulse" />
        ))}
      </div>
    );
  }
  const totalTrend = formatTrend(data.total_feedback_trend);
  const sentimentTrend = formatTrend(data.avg_sentiment_trend);
  const issuesTrend = formatTrend(data.active_issues_trend);

  return (
    <div>
      <p className="text-xs text-gray-400 mb-3">Key metrics for the selected period. Click a card to drill down.</p>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      <Link
        to="/feedback"
        className="rounded-lg border border-gray-600 bg-gray-800/50 p-4 hover:border-gray-500 transition"
      >
        <p className="text-gray-400 text-sm" title="All feedback items in this period">Total Feedback</p>
        <p className="text-xl font-semibold text-gray-100 mt-1">{data.total_feedback.toLocaleString()}</p>
        {totalTrend && (
          <span className={`inline-flex items-center gap-1 text-xs mt-1 ${totalTrend.up ? "text-green-400" : "text-red-400"}`}>
            {totalTrend.up ? <TrendingUp size={12} /> : <TrendingDown size={12} />}
            {totalTrend.text}
          </span>
        )}
      </Link>
      <Link
        to="/feedback"
        className="rounded-lg border border-gray-600 bg-gray-800/50 p-4 hover:border-gray-500 transition"
      >
        <p className="text-gray-400 text-sm" title="Average sentiment score -1 to 1 (positive = higher)">Avg Sentiment</p>
        <p className="text-xl font-semibold text-gray-100 mt-1">{data.avg_sentiment.toFixed(2)}</p>
        {sentimentTrend && (
          <span className={`inline-flex items-center gap-1 text-xs mt-1 ${sentimentTrend.up ? "text-green-400" : "text-red-400"}`}>
            {sentimentTrend.up ? <TrendingUp size={12} /> : <TrendingDown size={12} />}
            {sentimentTrend.text}
          </span>
        )}
      </Link>
      <Link
        to="/feedback?sentiment=negative"
        className="rounded-lg border border-gray-600 bg-gray-800/50 p-4 hover:border-gray-500 transition"
      >
        <p className="text-gray-400 text-sm" title="Distinct negative feedback themes">Active Issues</p>
        <p className="text-xl font-semibold text-gray-100 mt-1">{data.active_issues}</p>
        {issuesTrend && (
          <span className={`inline-flex items-center gap-1 text-xs mt-1 ${issuesTrend.up ? "text-red-400" : "text-green-400"}`}>
            {issuesTrend.up ? <TrendingUp size={12} /> : <TrendingDown size={12} />}
            {issuesTrend.text}
          </span>
        )}
      </Link>
      <Link
        to="/customers?health_max=50"
        className="rounded-lg border border-gray-600 bg-gray-800/50 p-4 hover:border-gray-500 transition"
      >
        <p className="text-gray-400 text-sm" title="Customers with health score below 50">At-Risk Customers</p>
        <p className="text-xl font-semibold text-gray-100 mt-1">{data.at_risk_customers}</p>
      </Link>
      </div>
    </div>
  );
}
