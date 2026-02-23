interface SentimentBadgeProps {
  sentiment?: string | null;
  score?: number | null;
  showScore?: boolean;
  className?: string;
}

export function SentimentBadge({ sentiment, score, showScore = false, className = "" }: SentimentBadgeProps) {
  if (!sentiment) return null;
  const s = sentiment.toLowerCase();
  let colorClass = "bg-gray-500/20 text-gray-300 border-gray-500/40";
  let dotColor = "bg-gray-400";
  if (s === "positive") {
    colorClass = "bg-green-500/20 text-green-300 border-green-500/40";
    dotColor = "bg-green-400";
  } else if (s === "negative") {
    colorClass = "bg-red-500/20 text-red-300 border-red-500/40";
    dotColor = "bg-red-400";
  }
  const label = sentiment.charAt(0).toUpperCase() + sentiment.slice(1);
  const scoreStr = showScore && score != null ? ` ${score >= 0 ? "+" : ""}${score.toFixed(2)}` : "";
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border px-2 py-0.5 text-xs font-medium ${colorClass} ${className}`}
      title={`${label}${scoreStr}`}
    >
      <span className={`h-1.5 w-1.5 rounded-full ${dotColor}`} aria-hidden />
      {label}
      {scoreStr}
    </span>
  );
}
