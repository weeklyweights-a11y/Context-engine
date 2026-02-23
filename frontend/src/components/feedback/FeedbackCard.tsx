import { Link } from "react-router-dom";
import type { Feedback } from "../../types/feedback";
import { SourceBadge } from "../common/SourceBadge";
import { SentimentBadge } from "../common/SentimentBadge";

function formatRelativeDate(iso: string | undefined): string {
  if (!iso) return "";
  const d = new Date(iso);
  const now = new Date();
  const diffMs = now.getTime() - d.getTime();
  const diffDays = Math.floor(diffMs / (24 * 60 * 60 * 1000));
  if (diffDays === 0) return "Today";
  if (diffDays === 1) return "Yesterday";
  if (diffDays < 7) return `${diffDays} days ago`;
  if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`;
  return d.toLocaleDateString();
}

function truncateText(text: string, maxLines = 2): string {
  const lines = text.split(/\n/);
  const first = lines.slice(0, maxLines).join("\n");
  if (lines.length > maxLines || first.length < text.length) {
    return first.trimEnd() + (first.length < text.length ? "..." : "");
  }
  return first;
}

interface FeedbackCardProps {
  item: Feedback;
  onClick?: () => void;
}

export function FeedbackCard({ item, onClick }: FeedbackCardProps) {
  const text = truncateText(item.text ?? "", 2);

  return (
    <div
      role="button"
      tabIndex={0}
      onClick={onClick}
      onKeyDown={(e) => (e.key === "Enter" || e.key === " ") && onClick?.()}
      className="rounded-lg border border-gray-600 bg-gray-800/50 p-4 transition hover:border-gray-500 hover:bg-gray-800 cursor-pointer text-left"
    >
      <p className="text-gray-200 text-sm leading-relaxed mb-2 line-clamp-2">{text}</p>
      <div className="flex flex-wrap items-center gap-2 text-xs">
        <SourceBadge source={item.source} />
        <SentimentBadge sentiment={item.sentiment} score={item.sentiment_score} showScore />
        {item.product_area && (
          <span className="rounded bg-gray-700 px-2 py-0.5 text-gray-400">{item.product_area}</span>
        )}
        {item.customer_id && item.customer_name && (
          <Link
            to={`/customers/${item.customer_id}`}
            onClick={(e) => e.stopPropagation()}
            className="text-indigo-400 hover:text-indigo-300 hover:underline"
          >
            {item.customer_name}
          </Link>
        )}
        <span className="text-gray-500 ml-auto">{formatRelativeDate(item.created_at)}</span>
      </div>
    </div>
  );
}
