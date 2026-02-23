import { FEEDBACK_SOURCES } from "../../types/feedback";

const colorMap: Record<string, string> = {
  blue: "bg-blue-500/20 text-blue-300 border-blue-500/40",
  indigo: "bg-indigo-500/20 text-indigo-300 border-indigo-500/40",
  orange: "bg-orange-500/20 text-orange-300 border-orange-500/40",
  green: "bg-green-500/20 text-green-300 border-green-500/40",
  teal: "bg-teal-500/20 text-teal-300 border-teal-500/40",
  purple: "bg-purple-500/20 text-purple-300 border-purple-500/40",
  pink: "bg-pink-500/20 text-pink-300 border-pink-500/40",
  gray: "bg-gray-500/20 text-gray-300 border-gray-500/40",
  cyan: "bg-cyan-500/20 text-cyan-300 border-cyan-500/40",
  red: "bg-red-500/20 text-red-300 border-red-500/40",
  yellow: "bg-amber-500/20 text-amber-300 border-amber-500/40",
};

interface SourceBadgeProps {
  source?: string | null;
  className?: string;
}

export function SourceBadge({ source, className = "" }: SourceBadgeProps) {
  if (!source) return null;
  const def = FEEDBACK_SOURCES.find((s) => s.id === source);
  const label = def?.label ?? source;
  const colorClass = colorMap[def?.color ?? "gray"] ?? colorMap.gray;
  return (
    <span
      className={`inline-flex items-center rounded-full border px-2 py-0.5 text-xs font-medium ${colorClass} ${className}`}
      title={label}
    >
      {label}
    </span>
  );
}
