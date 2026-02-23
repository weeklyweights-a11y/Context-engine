import { useNavigate } from "react-router-dom";
import { searchFeedback } from "../../services/searchApi";
import { SourceBadge } from "../common/SourceBadge";
import { SentimentBadge } from "../common/SentimentBadge";
import type { Feedback } from "../../types/feedback";
import { useState, useEffect } from "react";

interface RecentFeedbackProps {
  dateFrom?: string;
  dateTo?: string;
}

function formatRelativeDate(iso: string | undefined): string {
  if (!iso) return "";
  const d = new Date(iso);
  const now = new Date();
  const diffMs = now.getTime() - d.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);
  if (diffMins < 1) return "Just now";
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;
  return d.toLocaleDateString();
}

function truncateText(text: string, max = 80): string {
  if (text.length <= max) return text;
  return text.slice(0, max).trim() + "...";
}

export function RecentFeedback({ dateFrom, dateTo }: RecentFeedbackProps) {
  const [items, setItems] = useState<Feedback[]>([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    setLoading(true);
    const filters = dateFrom || dateTo ? { date_from: dateFrom, date_to: dateTo } : undefined;
    searchFeedback({ query: "", filters, sort_by: "date", page: 1, page_size: 10 })
      .then((res) => setItems(res.data))
      .finally(() => setLoading(false));
  }, [dateFrom, dateTo]);

  if (loading) {
    return <div className="rounded-lg border border-gray-600 bg-gray-800/50 h-64 animate-pulse" />;
  }

  return (
    <div className="rounded-lg border border-gray-600 bg-gray-800/50 p-4 relative">
      <h3 className="text-sm font-medium text-gray-300">Recent Feedback</h3>
      <p className="text-xs text-gray-400 mt-0.5 mb-2">Latest feedback items. Badges show source (channel) and sentiment (positive/negative/neutral). Click to open full feedback.</p>
      <div className="rounded border border-gray-600 bg-gray-900/80 px-2 py-1.5 text-xs mb-3">
        <p className="font-medium text-gray-300 mb-1">Badges on each row:</p>
        <div className="flex flex-wrap gap-x-3 gap-y-0.5 text-gray-200">
          <span>• Source = channel (review, support, NPS)</span>
          <span>• Sentiment = tone (green +, red −, gray neutral)</span>
          <span>• Area = product feature</span>
        </div>
      </div>
      {items.length === 0 ? (
        <p className="text-gray-500 text-sm py-4">No feedback in this period</p>
      ) : (
        <div className="space-y-2">
          {items.map((item) => (
            <div
              key={item.id}
              role="button"
              tabIndex={0}
              onClick={() => navigate(`/feedback?id=${item.id}`)}
              onKeyDown={(e) => e.key === "Enter" && navigate(`/feedback?id=${item.id}`)}
              className="rounded border border-gray-600 p-2 hover:border-gray-500 hover:bg-gray-700/30 cursor-pointer text-left"
            >
              <p className="text-gray-200 text-sm line-clamp-2">{truncateText(item.text)}</p>
              <div className="flex flex-wrap items-center gap-2 mt-1.5 text-xs">
                <SourceBadge source={item.source} />
                <SentimentBadge sentiment={item.sentiment} score={item.sentiment_score} />
                {item.product_area && (
                  <span className="rounded bg-gray-700 px-1.5 py-0.5 text-gray-400">{item.product_area}</span>
                )}
                <span className="text-gray-500 ml-auto">{formatRelativeDate(item.created_at)}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
