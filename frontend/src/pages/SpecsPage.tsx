import { useState, useEffect, useCallback } from "react";
import { useSearchParams } from "react-router-dom";
import { Link } from "react-router-dom";
import { Plus } from "lucide-react";
import { getSpecs } from "../services/specApi";
import { useAgentChat } from "../hooks/useAgentChat";
import type { Spec } from "../services/specApi";
import EmptyState from "../components/common/EmptyState";
import LoadingSpinner from "../components/common/LoadingSpinner";
import GenerateSpecModal from "../components/specs/GenerateSpecModal";

function formatRelativeDate(iso: string): string {
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

function firstPrdParagraph(prd: string | undefined): string {
  if (!prd) return "";
  const match = prd.match(/^#+.+\n\n(.+?)(?:\n\n|$)/s);
  if (match) return match[1].slice(0, 200) + (match[1].length > 200 ? "…" : "");
  return prd.slice(0, 200) + (prd.length > 200 ? "…" : "");
}

function StatusBadge({ status }: { status: string }) {
  const styles: Record<string, string> = {
    draft: "bg-gray-600 text-gray-200",
    final: "bg-green-600/80 text-green-100",
    shared: "bg-blue-600/80 text-blue-100",
  };
  return (
    <span
      className={`px-2 py-0.5 text-xs font-medium rounded ${
        styles[status] ?? "bg-gray-600 text-gray-200"
      }`}
    >
      {status}
    </span>
  );
}

export default function SpecsPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const { openWithMessage } = useAgentChat();
  const [items, setItems] = useState<Spec[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);

  const productArea = searchParams.get("product_area") ?? "";
  const statusFilter = searchParams.get("status") ?? "";
  const dateFrom = searchParams.get("date_from") ?? "";
  const dateTo = searchParams.get("date_to") ?? "";
  const topicPrefill = searchParams.get("topic") ?? "";

  const fetchSpecs = useCallback(() => {
    setLoading(true);
    getSpecs({
      page,
      page_size: 20,
      product_area: productArea || undefined,
      status: statusFilter || undefined,
      date_from: dateFrom || undefined,
      date_to: dateTo || undefined,
    })
      .then((res) => {
        setItems(res.data);
        setTotal(res.pagination.total);
      })
      .finally(() => setLoading(false));
  }, [page, productArea, statusFilter, dateFrom, dateTo]);

  useEffect(() => {
    fetchSpecs();
  }, [fetchSpecs]);

  useEffect(() => {
    if (topicPrefill && showModal === false) {
      setShowModal(true);
    }
  }, [topicPrefill]);

  const updateUrl = useCallback((updates: Record<string, string | undefined>) => {
    setSearchParams((p) => {
      const next = new URLSearchParams(p);
      Object.entries(updates).forEach(([k, v]) => {
        if (v) next.set(k, v);
        else next.delete(k);
      });
      next.delete("page");
      return next;
    });
    setPage(1);
  }, [setSearchParams]);

  const totalPages = Math.ceil(total / 20) || 1;

  if (items.length === 0 && !loading && total === 0) {
    return (
      <div className="p-8">
        <h2 className="text-xl font-semibold text-gray-100 mb-4">Specs</h2>
        <EmptyState
          message="No specs yet. Ask the agent to create your first spec."
          actions={
            <div className="flex gap-3">
              <button
                onClick={() => setShowModal(true)}
                className="px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg flex items-center gap-2"
              >
                <Plus className="w-4 h-4" />
                Generate New Spec
              </button>
              <button
                onClick={() => openWithMessage("Help me generate specs from feedback")}
                className="px-4 py-2 bg-gray-600 hover:bg-gray-500 text-white rounded-lg"
              >
                Open Agent Chat
              </button>
            </div>
          }
        />
        {showModal && (
          <GenerateSpecModal
            onClose={() => {
              setShowModal(false);
              fetchSpecs();
            }}
            prefilledTopic={topicPrefill}
          />
        )}
      </div>
    );
  }

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold text-gray-100">Specs</h2>
        <button
          onClick={() => setShowModal(true)}
          className="flex items-center gap-2 px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg"
        >
          <Plus className="w-4 h-4" />
          Generate New Spec
        </button>
      </div>

      <div className="flex flex-wrap gap-3 mb-4">
        <select
          value={productArea}
          onChange={(e) => updateUrl({ product_area: e.target.value || undefined })}
          className="rounded border border-gray-600 bg-gray-800 text-gray-200 py-1.5 px-2 text-sm"
        >
          <option value="">All product areas</option>
          <option value="checkout">checkout</option>
          <option value="billing">billing</option>
          <option value="dashboard">dashboard</option>
          <option value="onboarding">onboarding</option>
        </select>
        <select
          value={statusFilter}
          onChange={(e) => updateUrl({ status: e.target.value || undefined })}
          className="rounded border border-gray-600 bg-gray-800 text-gray-200 py-1.5 px-2 text-sm"
        >
          <option value="">All statuses</option>
          <option value="draft">Draft</option>
          <option value="final">Final</option>
          <option value="shared">Shared</option>
        </select>
        <input
          type="date"
          value={dateFrom}
          onChange={(e) => updateUrl({ date_from: e.target.value || undefined })}
          className="rounded border border-gray-600 bg-gray-800 text-gray-200 py-1.5 px-2 text-sm"
          placeholder="From"
        />
        <input
          type="date"
          value={dateTo}
          onChange={(e) => updateUrl({ date_to: e.target.value || undefined })}
          className="rounded border border-gray-600 bg-gray-800 text-gray-200 py-1.5 px-2 text-sm"
          placeholder="To"
        />
      </div>

      {loading ? (
        <LoadingSpinner />
      ) : (
        <div className="space-y-4">
          {items.map((spec) => (
            <Link
              key={spec.id}
              to={`/specs/${spec.id}`}
              className="block p-4 rounded-lg border border-gray-700 bg-gray-900/50 hover:border-gray-600 transition-colors"
            >
              <div className="flex justify-between items-start gap-4">
                <div className="min-w-0 flex-1">
                  <h3 className="font-medium text-gray-100 truncate">{spec.title}</h3>
                  <div className="flex flex-wrap gap-2 mt-1 text-sm text-gray-400">
                    {spec.product_area && (
                      <span className="px-2 py-0.5 rounded bg-gray-700">
                        {spec.product_area}
                      </span>
                    )}
                    <span>{formatRelativeDate(spec.created_at)}</span>
                    <span>
                      {spec.feedback_count} feedback · {spec.customer_count} customers
                    </span>
                  </div>
                  <p className="mt-2 text-sm text-gray-500 line-clamp-2">
                    {firstPrdParagraph(spec.prd)}
                  </p>
                </div>
                <StatusBadge status={spec.status} />
              </div>
            </Link>
          ))}
        </div>
      )}

      {totalPages > 1 && (
        <div className="flex justify-between items-center mt-4">
          <p className="text-gray-400 text-sm">Page {page} of {totalPages}</p>
          <div className="flex gap-2">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page <= 1}
              className="px-3 py-1 bg-gray-700 rounded disabled:opacity-50 text-gray-200"
            >
              Previous
            </button>
            <button
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page >= totalPages}
              className="px-3 py-1 bg-gray-700 rounded disabled:opacity-50 text-gray-200"
            >
              Next
            </button>
          </div>
        </div>
      )}

      {showModal && (
        <GenerateSpecModal
          onClose={() => {
            setShowModal(false);
            fetchSpecs();
          }}
          prefilledTopic={topicPrefill}
        />
      )}
    </div>
  );
}
