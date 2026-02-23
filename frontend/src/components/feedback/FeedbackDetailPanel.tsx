import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { X, Copy, Star } from "lucide-react";
import type { Feedback } from "../../types/feedback";
import { getSimilarFeedback } from "../../services/feedbackApi";
import { getCustomer } from "../../services/customerApi";
import { SourceBadge } from "../common/SourceBadge";
import { SentimentBadge } from "../common/SentimentBadge";
import { CustomerCard } from "./CustomerCard";
import { useAgentChat } from "../../hooks/useAgentChat";
import type { Customer } from "../../types/customer";

const STARRED_KEY = "feedback-starred";

function getStarred(): Set<string> {
  try {
    const s = localStorage.getItem(STARRED_KEY);
    return new Set(s ? JSON.parse(s) : []);
  } catch {
    return new Set();
  }
}

function toggleStarred(id: string): Set<string> {
  const set = getStarred();
  if (set.has(id)) set.delete(id);
  else set.add(id);
  localStorage.setItem(STARRED_KEY, JSON.stringify([...set]));
  return set;
}

interface FeedbackDetailPanelProps {
  feedback: Feedback | null;
  onClose: () => void;
  onSelectSimilar: (f: Feedback) => void;
}

export function FeedbackDetailPanel({ feedback, onClose, onSelectSimilar }: FeedbackDetailPanelProps) {
  const navigate = useNavigate();
  const [similar, setSimilar] = useState<Feedback[]>([]);
  const [customer, setCustomer] = useState<Customer | null>(null);
  const [starred, setStarred] = useState<Set<string>>(getStarred);
  const { openWithMessage } = useAgentChat();

  useEffect(() => {
    if (!feedback) {
      setSimilar([]);
      setCustomer(null);
      return;
    }
    getSimilarFeedback(feedback.id).then(setSimilar).catch(() => setSimilar([]));
    if (feedback.customer_id) {
      getCustomer(feedback.customer_id).then(setCustomer).catch(() => setCustomer(null));
    } else {
      setCustomer(null);
    }
  }, [feedback?.id, feedback?.customer_id]);

  useEffect(() => {
    const h = (e: KeyboardEvent) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", h);
    return () => window.removeEventListener("keydown", h);
  }, [onClose]);

  if (!feedback) return null;

  const ingestionText =
    feedback.ingestion_method === "csv_upload" && feedback.source_file
      ? `Imported via CSV (${feedback.source_file})`
      : feedback.ingestion_method === "manual_entry"
        ? "Added manually"
        : feedback.ingested_at
          ? `Imported on ${new Date(feedback.ingested_at).toLocaleDateString()}`
          : null;

  const isStarred = starred.has(feedback.id);
  const handleStar = () => setStarred(toggleStarred(feedback.id));

  return (
    <div className="fixed inset-0 z-40 flex justify-end" role="dialog" aria-modal aria-labelledby="feedback-detail-title">
      <div className="absolute inset-0 bg-black/50" onClick={onClose} aria-hidden />
      <div className="relative w-full max-w-md lg:max-w-lg bg-gray-900 border-l border-gray-700 shadow-xl overflow-y-auto flex flex-col">
        <div className="sticky top-0 bg-gray-900 border-b border-gray-700 p-4 flex items-start justify-between gap-4 z-10">
          <div className="flex items-center gap-2 flex-wrap">
            <SourceBadge source={feedback.source} className="text-sm" />
            <span className="text-gray-400 text-sm">
              {feedback.created_at ? new Date(feedback.created_at).toLocaleDateString() : ""}
            </span>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="p-1 rounded text-gray-400 hover:bg-gray-800 hover:text-gray-200"
            aria-label="Close"
          >
            <X className="h-5 w-5" />
          </button>
        </div>
        <div className="p-4 space-y-4 flex-1">
          <h2 id="feedback-detail-title" className="sr-only">Feedback detail</h2>
          <p className="text-gray-200 whitespace-pre-wrap">{feedback.text}</p>
          <div className="flex flex-wrap gap-2">
            <SentimentBadge sentiment={feedback.sentiment} score={feedback.sentiment_score} showScore />
            {feedback.product_area && (
              <span className="rounded bg-gray-700 px-2 py-0.5 text-gray-400 text-sm">{feedback.product_area}</span>
            )}
            {feedback.rating != null && (
              <span className="text-gray-400 text-sm">Rating: {feedback.rating}/5</span>
            )}
          </div>
          {(feedback.author_name || feedback.author_email) && (
            <p className="text-sm text-gray-400">
              Author: {feedback.author_name ?? ""} {feedback.author_email ? `<${feedback.author_email}>` : ""}
            </p>
          )}
          {ingestionText && <p className="text-sm text-gray-400">{ingestionText}</p>}
          {customer && <CustomerCard customer={customer} />}
          {similar.length > 0 && (
            <div>
              <h3 className="font-medium text-gray-100 mb-2">{similar.length} similar items</h3>
              <ul className="space-y-2">
                {similar.map((s) => (
                  <li key={s.id}>
                    <button
                      type="button"
                      onClick={() => onSelectSimilar(s)}
                      className="w-full text-left rounded border border-gray-600 bg-gray-800/50 p-2 text-sm text-gray-200 hover:border-gray-500"
                    >
                      <p className="line-clamp-1">{s.text}</p>
                      <div className="flex items-center gap-2 mt-1">
                        <SentimentBadge sentiment={s.sentiment} />
                        <span className="text-gray-500 text-xs">
                          {s.created_at ? new Date(s.created_at).toLocaleDateString() : ""}
                        </span>
                      </div>
                    </button>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
        <div className="sticky bottom-0 border-t border-gray-700 p-4 flex flex-wrap gap-2 bg-gray-900">
          <button
            type="button"
            onClick={() => openWithMessage(`Analyze this feedback: ${feedback.text.slice(0, 200)}${feedback.text.length > 200 ? "..." : ""}`)}
            className="px-3 py-1.5 text-sm bg-indigo-600 hover:bg-indigo-500 rounded text-gray-200"
          >
            Ask agent
          </button>
          <button
            type="button"
            onClick={() => {
              const topic = feedback.text.slice(0, 80).replace(/\s+/g, " ").trim() + (feedback.text.length > 80 ? "..." : "");
              onClose();
              navigate(`/specs?topic=${encodeURIComponent(topic)}`);
            }}
            className="px-3 py-1.5 text-sm bg-indigo-600 hover:bg-indigo-500 rounded text-gray-200"
          >
            Generate spec
          </button>
          <button
            type="button"
            onClick={() => navigator.clipboard.writeText(feedback.text)}
            className="px-3 py-1.5 text-sm bg-gray-700 hover:bg-gray-600 rounded text-gray-200 flex items-center gap-1"
          >
            <Copy className="h-4 w-4" /> Copy text
          </button>
          <button
            type="button"
            onClick={handleStar}
            className={`px-3 py-1.5 text-sm rounded flex items-center gap-1 ${
              isStarred ? "bg-amber-600 text-white" : "bg-gray-700 hover:bg-gray-600 text-gray-200"
            }`}
            title={isStarred ? "Unstar" : "Star"}
          >
            <Star className={`h-4 w-4 ${isStarred ? "fill-current" : ""}`} /> Star
          </button>
        </div>
      </div>
    </div>
  );
}
