import { useState, useEffect } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import {
  getCustomer,
  getCustomerFeedback,
  getCustomerSentimentTrend,
} from "../services/customerApi";
import { getSpecs } from "../services/specApi";
import { useAgentChat } from "../hooks/useAgentChat";
import type { Customer } from "../types/customer";
import type { Feedback } from "../types/feedback";
import LoadingSpinner from "../components/common/LoadingSpinner";
import { SentimentTrendChart } from "../components/customers/SentimentTrendChart";
import { FeedbackCard } from "../components/feedback/FeedbackCard";
import { FeedbackDetailPanel } from "../components/feedback/FeedbackDetailPanel";

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

export default function CustomerProfilePage() {
  const { id } = useParams<{ id: string }>();
  const { openWithMessage } = useAgentChat();
  const navigate = useNavigate();
  const [customer, setCustomer] = useState<Customer | null>(null);
  const [trend, setTrend] = useState<{
    periods: { date: string; avg_sentiment: number; count: number }[];
    product_average: { date: string; avg_sentiment: number }[];
  } | null>(null);
  const [feedback, setFeedback] = useState<Feedback[]>([]);
  const [feedbackTotal, setFeedbackTotal] = useState(0);
  const [specsMentioningCustomer, setSpecsMentioningCustomer] = useState<{ id: string; title: string }[]>([]);
  const [loading, setLoading] = useState(true);
  const [detailFeedback, setDetailFeedback] = useState<Feedback | null>(null);

  useEffect(() => {
    if (!id) return;
    setLoading(true);
    Promise.all([
      getCustomer(id),
      getCustomerSentimentTrend(id).catch(() => ({ periods: [], product_average: [] })),
      getCustomerFeedback(id, { page: 1, page_size: 20 }),
    ])
      .then((res) => {
        const [c, t, f] = res;
        setCustomer(c);
        setTrend(t);
        type FbRes = { data: Feedback[]; pagination: { total: number } };
        const fb = f as FbRes;
        setFeedback(Array.isArray(fb?.data) ? fb.data.filter(Boolean) : []);
        setFeedbackTotal(fb?.pagination?.total ?? 0);
      })
      .catch(() => setCustomer(null))
      .finally(() => setLoading(false));
  }, [id]);

  useEffect(() => {
    if (!id) return;
    getSpecs({ customer_id: id })
      .then((res) =>
        setSpecsMentioningCustomer(res.data.map((s) => ({ id: s.id, title: s.title })))
      )
      .catch(() => setSpecsMentioningCustomer([]));
  }, [id]);

  if (loading) return <LoadingSpinner />;
  if (!customer) {
    return (
      <div className="p-8">
        <p className="text-gray-400">Customer not found</p>
        <button
          type="button"
          onClick={() => navigate("/customers")}
          className="mt-4 text-indigo-400 hover:text-indigo-300"
        >
          ← Back to Customers
        </button>
      </div>
    );
  }

  const days = daysToRenewal(customer.renewal_date);
  const avgSentiment =
    trend?.periods?.length &&
    trend.periods.reduce((s, p) => s + p.avg_sentiment, 0) / trend.periods.length;

  return (
    <div className="p-8 max-w-4xl">
      <button
        type="button"
        onClick={() => navigate("/customers")}
        className="text-indigo-400 hover:text-indigo-300 mb-6"
      >
        ← Back to Customers
      </button>
      <div className="mb-8">
        <h1 className="text-2xl font-semibold text-gray-100">{customer.company_name}</h1>
        <div className="flex flex-wrap gap-2 mt-2">
          {customer.segment && (
            <span className="rounded bg-gray-700 px-2 py-0.5 text-gray-300 text-sm">
              {customer.segment}
            </span>
          )}
          {customer.plan && (
            <span className="rounded bg-gray-700 px-2 py-0.5 text-gray-300 text-sm">
              {customer.plan}
            </span>
          )}
          {customer.industry && (
            <span className="rounded bg-gray-700 px-2 py-0.5 text-gray-300 text-sm">
              {customer.industry}
            </span>
          )}
        </div>
      </div>
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-8">
        <div className="rounded-lg border border-gray-600 bg-gray-800/50 p-4">
          <p className="text-gray-500 text-xs uppercase">MRR</p>
          <p className="text-gray-100 font-medium">{formatCurrency(customer.mrr)}</p>
        </div>
        <div className="rounded-lg border border-gray-600 bg-gray-800/50 p-4">
          <p className="text-gray-500 text-xs uppercase">ARR</p>
          <p className="text-gray-100 font-medium">{formatCurrency(customer.arr)}</p>
        </div>
        <div className="rounded-lg border border-gray-600 bg-gray-800/50 p-4">
          <p className="text-gray-500 text-xs uppercase">Health Score</p>
          <p className={`font-medium ${healthColor(customer.health_score)}`}>
            {customer.health_score ?? "—"}
          </p>
        </div>
        <div className="rounded-lg border border-gray-600 bg-gray-800/50 p-4">
          <p className="text-gray-500 text-xs uppercase">Total Feedback</p>
          <p className="text-gray-100 font-medium">{feedbackTotal}</p>
        </div>
        <div className="rounded-lg border border-gray-600 bg-gray-800/50 p-4">
          <p className="text-gray-500 text-xs uppercase">Avg Sentiment</p>
          <p className="text-gray-100 font-medium">
            {avgSentiment != null ? avgSentiment.toFixed(2) : "—"}
          </p>
        </div>
        <div className="rounded-lg border border-gray-600 bg-gray-800/50 p-4">
          <p className="text-gray-500 text-xs uppercase">Days to Renewal</p>
          <p className="text-gray-100 font-medium">
            {days != null ? days : "—"}
          </p>
        </div>
      </div>
      <section className="mb-8">
        <h2 className="text-lg font-medium text-gray-100 mb-3">Account Details</h2>
        <div className="rounded-lg border border-gray-600 bg-gray-800/50 p-4 space-y-2 text-sm text-gray-300">
          {customer.account_manager && <p>Account manager: {customer.account_manager}</p>}
          {customer.employee_count != null && <p>Employee count: {customer.employee_count}</p>}
          {customer.created_at && (
            <p>Created: {new Date(customer.created_at).toLocaleDateString()}</p>
          )}
          {customer.renewal_date && (
            <p>Renewal: {new Date(customer.renewal_date).toLocaleDateString()}</p>
          )}
          {customer.plan && <p>Plan: {customer.plan}</p>}
          {customer.customer_id_external && (
            <p>External ID: {customer.customer_id_external}</p>
          )}
        </div>
      </section>
      {trend && (
        <section className="mb-8">
          <h2 className="text-lg font-medium text-gray-100 mb-3">Sentiment Trend</h2>
          <SentimentTrendChart periods={trend.periods} productAverage={trend.product_average} />
        </section>
      )}
      <section className="mb-8">
        <div className="flex justify-between items-center mb-3">
          <h2 className="text-lg font-medium text-gray-100">Feedback History</h2>
          <Link
            to={`/feedback?customer=${id}`}
            className="text-indigo-400 hover:text-indigo-300 text-sm"
          >
            View all feedback →
          </Link>
        </div>
        {feedback.length === 0 ? (
          <p className="text-gray-500">No feedback yet</p>
        ) : (
          <div className="space-y-3">
            {feedback.map((f) => (
              <FeedbackCard key={f.id} item={f} onClick={() => setDetailFeedback(f)} />
            ))}
          </div>
        )}
      </section>
      <section className="mb-8">
        <h2 className="text-lg font-medium text-gray-100 mb-3">Specs Mentioning This Customer</h2>
        {specsMentioningCustomer.length === 0 ? (
          <p className="text-gray-500 text-sm">No specs mention this customer yet</p>
        ) : (
          <ul className="space-y-2">
            {specsMentioningCustomer.map((s) => (
              <li key={s.id}>
                <Link
                  to={`/specs/${s.id}`}
                  className="text-indigo-400 hover:text-indigo-300"
                >
                  {s.title}
                </Link>
              </li>
            ))}
          </ul>
        )}
      </section>
      <div className="flex gap-3">
        <button
          type="button"
          onClick={() => openWithMessage(`What's the situation with ${customer.company_name}?`)}
          className="px-3 py-1.5 text-sm bg-indigo-600 hover:bg-indigo-500 rounded text-white"
        >
          Ask agent about this customer
        </button>
        <Link
          to={`/feedback?customer=${id}`}
          className="px-3 py-1.5 text-sm bg-indigo-600 hover:bg-indigo-500 rounded text-white"
        >
          View all feedback
        </Link>
        <button
          type="button"
          className="px-3 py-1.5 text-sm bg-gray-700 hover:bg-gray-600 rounded text-gray-200"
          disabled
          title="Coming in Phase 7"
        >
          View in Kibana
        </button>
      </div>
      {detailFeedback && (
        <FeedbackDetailPanel
          feedback={detailFeedback}
          onClose={() => setDetailFeedback(null)}
          onSelectSimilar={(f) => setDetailFeedback(f)}
        />
      )}
    </div>
  );
}
