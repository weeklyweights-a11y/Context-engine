import { useState, useEffect, useCallback } from "react";
import { useSearchParams, useLocation } from "react-router-dom";
import { searchFeedback } from "../services/searchApi";
import { getFeedback } from "../services/feedbackApi";
import type { Feedback } from "../types/feedback";
import type { SearchFeedbackFilters } from "../services/searchApi";
import type { FeedbackFilters } from "../components/feedback/FilterBar";
import EmptyState from "../components/common/EmptyState";
import LoadingSpinner from "../components/common/LoadingSpinner";
import FeedbackUpload from "../components/upload/FeedbackUpload";
import UploadHistoryTable from "../components/upload/UploadHistoryTable";
import { SearchBar } from "../components/feedback/SearchBar";
import { FilterBar } from "../components/feedback/FilterBar";
import { FeedbackCard } from "../components/feedback/FeedbackCard";
import { FeedbackDetailPanel } from "../components/feedback/FeedbackDetailPanel";

function filtersToApi(f: FeedbackFilters): SearchFeedbackFilters | undefined {
  const has =
    (f.product_area?.length ?? 0) > 0 ||
    (f.source?.length ?? 0) > 0 ||
    (f.sentiment?.length ?? 0) > 0 ||
    (f.customer_segment?.length ?? 0) > 0 ||
    f.date_from ||
    f.date_to ||
    f.customer_id ||
    f.has_customer != null;
  if (!has) return undefined;
  return {
    product_area: f.product_area?.length ? f.product_area : undefined,
    source: f.source?.length ? f.source : undefined,
    sentiment: f.sentiment?.length ? f.sentiment : undefined,
    customer_segment: f.customer_segment?.length ? f.customer_segment : undefined,
    date_from: f.date_from,
    date_to: f.date_to,
    customer_id: f.customer_id,
    has_customer: f.has_customer,
  };
}

function defaultFilters(): FeedbackFilters {
  return {
    product_area: [],
    source: [],
    sentiment: [],
    customer_segment: [],
  };
}

export default function FeedbackPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const { pathname } = useLocation();
  const [items, setItems] = useState<Feedback[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const pageSize = 20;
  const [loading, setLoading] = useState(true);
  const [showUpload, setShowUpload] = useState(false);
  const [showManual, setShowManual] = useState(false);
  const [detailFeedback, setDetailFeedback] = useState<Feedback | null>(null);

  const q = searchParams.get("q") ?? "";
  const sortBy = searchParams.get("sort") ?? "relevance";
  const area = searchParams.get("area") ?? "";
  const sentiment = searchParams.get("sentiment") ?? "";
  const sourceParam = searchParams.get("source") ?? "";
  const segmentParam = searchParams.get("segment") ?? "";
  const dateFromParam = searchParams.get("date_from") ?? "";
  const dateToParam = searchParams.get("date_to") ?? "";
  const range = searchParams.get("range") ?? "";
  const customerId = searchParams.get("customer") ?? "";

  const [filters, setFilters] = useState<FeedbackFilters>(() => {
    const f = defaultFilters();
    if (area) f.product_area = area.split(",").filter(Boolean);
    if (sentiment) f.sentiment = sentiment.split(",").filter(Boolean);
    if (sourceParam) f.source = sourceParam.split(",").filter(Boolean);
    if (segmentParam) f.customer_segment = segmentParam.split(",").filter(Boolean);
    if (dateFromParam) f.date_from = dateFromParam;
    if (dateToParam) f.date_to = dateToParam;
    if (!dateFromParam && !dateToParam && range) {
      const days = parseInt(range, 10) || 30;
      const to = new Date();
      const from = new Date();
      from.setDate(from.getDate() - days);
      f.date_from = from.toISOString().split("T")[0];
      f.date_to = to.toISOString().split("T")[0];
    }
    if (customerId) f.customer_id = customerId;
    return f;
  });

  const doSearch = useCallback(() => {
    setLoading(true);
    searchFeedback({
      query: q,
      filters: filtersToApi(filters),
      sort_by: sortBy,
      page,
      page_size: pageSize,
    })
      .then((res) => {
        setItems(res.data);
        setTotal(res.pagination.total);
      })
      .finally(() => setLoading(false));
  }, [q, filters, sortBy, page, pageSize]);

  useEffect(() => {
    doSearch();
  }, [doSearch]);

  useEffect(() => {
    setFilters((prev) => {
      const f = { ...prev };
      if (area) f.product_area = area.split(",").filter(Boolean);
      else if (!area && prev.product_area?.length) f.product_area = [];
      if (sentiment) f.sentiment = sentiment.split(",").filter(Boolean);
      else if (!sentiment && prev.sentiment?.length) f.sentiment = [];
      if (sourceParam) f.source = sourceParam.split(",").filter(Boolean);
      else if (!sourceParam && prev.source?.length) f.source = [];
      if (segmentParam) f.customer_segment = segmentParam.split(",").filter(Boolean);
      else if (!segmentParam && prev.customer_segment?.length) f.customer_segment = [];
      f.date_from = dateFromParam || undefined;
      f.date_to = dateToParam || undefined;
      if (!dateFromParam && !dateToParam && range) {
        const days = parseInt(range, 10) || 30;
        const to = new Date();
        const from = new Date();
        from.setDate(from.getDate() - days);
        f.date_from = from.toISOString().split("T")[0];
        f.date_to = to.toISOString().split("T")[0];
      }
      f.customer_id = customerId || undefined;
      return f;
    });
  }, [area, sentiment, sourceParam, segmentParam, dateFromParam, dateToParam, range, customerId]);

  useEffect(() => {
    setDetailFeedback(null);
  }, [pathname]);

  const feedbackIdFromUrl = searchParams.get("id");
  useEffect(() => {
    if (feedbackIdFromUrl) {
      getFeedback(feedbackIdFromUrl)
        .then(setDetailFeedback)
        .catch(() => setDetailFeedback(null));
    }
  }, [feedbackIdFromUrl]);


  if (showUpload || showManual) {
    return (
      <div className="p-8 space-y-8">
        <button
          type="button"
          onClick={() => {
            setShowUpload(false);
            setShowManual(false);
          }}
          className="text-blue-400 hover:text-blue-300"
        >
          ← Back to Feedback
        </button>
        <section>
          <h3 className="font-medium text-gray-100 mb-4">Upload Feedback</h3>
          <FeedbackUpload />
        </section>
        <section>
          <h3 className="font-medium text-gray-100 mb-4">Upload History</h3>
          <UploadHistoryTable />
        </section>
      </div>
    );
  }

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
  }, [setSearchParams]);

  const handleQueryChange = (value: string) => {
    updateUrl({ q: value || undefined });
    setPage(1);
  };

  const handleFiltersChange = (f: FeedbackFilters) => {
    setFilters(f);
    updateUrl({
      area: f.product_area?.length ? f.product_area.join(",") : undefined,
      sentiment: f.sentiment?.length ? f.sentiment.join(",") : undefined,
      source: f.source?.length ? f.source.join(",") : undefined,
      segment: f.customer_segment?.length ? f.customer_segment.join(",") : undefined,
      date_from: f.date_from ?? undefined,
      date_to: f.date_to ?? undefined,
      customer: f.customer_id ?? undefined,
    });
    setPage(1);
  };

  const isFilteredByCustomer = Boolean(customerId || filters.customer_id);
  const showGenericEmpty = items.length === 0 && total === 0 && !loading && !isFilteredByCustomer;

  if (showGenericEmpty) {
    return (
      <div className="p-8">
        <h2 className="text-xl font-semibold text-gray-100 mb-4">Feedback</h2>
        <EmptyState
          message="No feedback yet. Import data to start analyzing."
          actions={
            <div className="flex gap-3">
              <button
                onClick={() => setShowUpload(true)}
                className="px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg"
              >
                Upload CSV
              </button>
              <button
                onClick={() => setShowManual(true)}
                className="px-4 py-2 bg-gray-600 hover:bg-gray-500 text-white rounded-lg"
              >
                Add Manually
              </button>
            </div>
          }
        />
      </div>
    );
  }

  const totalPages = Math.ceil(total / pageSize) || 1;

  return (
    <div className="p-8 flex gap-6">
      <div className="flex-1 min-w-0">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold text-gray-100">Feedback</h2>
          <div className="flex gap-2">
            <button
              onClick={() => setShowUpload(true)}
              className="px-3 py-1.5 text-sm bg-blue-500 hover:bg-blue-600 text-white rounded-lg"
            >
              Upload CSV
            </button>
            <button
              onClick={() => setShowManual(true)}
              className="px-3 py-1.5 text-sm bg-gray-600 hover:bg-gray-500 text-white rounded-lg"
            >
              Add Manually
            </button>
          </div>
        </div>
        <div className="mb-4">
          <SearchBar value={q} onChange={handleQueryChange} />
        </div>
        <div className="mb-4">
          <FilterBar filters={filters} onChange={handleFiltersChange} />
        </div>
        <div className="flex items-center justify-between mb-3">
          <p className="text-gray-400 text-sm">Showing {total} results</p>
          <select
            value={sortBy}
            onChange={(e) => {
              updateUrl({ sort: e.target.value });
              setPage(1);
            }}
            className="rounded border border-gray-600 bg-gray-800 text-gray-200 py-1 px-2 text-sm"
          >
            <option value="relevance">Relevance</option>
            <option value="date">Date (newest)</option>
            <option value="sentiment">Sentiment (most negative)</option>
          </select>
        </div>
        {loading ? (
          <LoadingSpinner />
        ) : items.length === 0 ? (
          <p className="text-gray-500 py-8">
            {isFilteredByCustomer
              ? "No feedback for this customer."
              : "No feedback matches your search."}
          </p>
        ) : (
          <div className="space-y-3">
            {items.map((item) => (
              <FeedbackCard key={item.id} item={item} onClick={() => setDetailFeedback(item)} />
            ))}
          </div>
        )}
        {totalPages > 1 && (
          <div className="flex justify-between items-center mt-4">
            <p className="text-gray-400 text-sm">
              Page {page} of {totalPages}
            </p>
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
