import { useState, useEffect, useCallback } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { SearchBar } from "../components/feedback/SearchBar";
import { getCustomersList } from "../services/customerApi";
import type { Customer } from "../types/customer";
import EmptyState from "../components/common/EmptyState";
import LoadingSpinner from "../components/common/LoadingSpinner";
import CustomerUpload from "../components/upload/CustomerUpload";
import { AlertCircle } from "lucide-react";

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

export default function CustomersPage() {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const [items, setItems] = useState<Customer[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const pageSize = 20;
  const [loading, setLoading] = useState(true);
  const [showUpload, setShowUpload] = useState(false);

  const search = searchParams.get("q") ?? "";
  const segment = searchParams.get("segment") ?? "";
  const healthMin = searchParams.get("health_min") ?? "";
  const healthMax = searchParams.get("health_max") ?? "";
  const renewalWithin = searchParams.get("renewal") ?? "";
  const hasNegative = searchParams.get("has_negative") ?? "";
  const arrMin = searchParams.get("arr_min") ?? "";
  const arrMax = searchParams.get("arr_max") ?? "";
  const sortBy = searchParams.get("sort") ?? "company_name";

  const doFetch = useCallback(() => {
    setLoading(true);
    getCustomersList({
      page,
      page_size: pageSize,
      search: search || undefined,
      segment: segment || undefined,
      health_min: healthMin ? parseFloat(healthMin) : undefined,
      health_max: healthMax ? parseFloat(healthMax) : undefined,
      renewal_within: renewalWithin ? parseInt(renewalWithin, 10) : undefined,
      has_negative_feedback: hasNegative === "1" ? true : hasNegative === "0" ? false : undefined,
      arr_min: arrMin ? parseFloat(arrMin) : undefined,
      arr_max: arrMax ? parseFloat(arrMax) : undefined,
      include_feedback_stats: true,
      sort_by: sortBy,
      sort_order: "asc",
    })
      .then((res) => {
        setItems(res.data);
        setTotal(res.pagination.total);
      })
      .finally(() => setLoading(false));
  }, [page, pageSize, search, segment, healthMin, healthMax, renewalWithin, hasNegative, arrMin, arrMax, sortBy]);

  useEffect(() => {
    doFetch();
  }, [doFetch]);

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

  if (showUpload) {
    return (
      <div className="p-8">
        <button
          type="button"
          onClick={() => setShowUpload(false)}
          className="text-blue-400 hover:text-blue-300 mb-4"
        >
          ← Back to Customers
        </button>
        <CustomerUpload />
      </div>
    );
  }

  if (items.length === 0 && total === 0 && !loading) {
    return (
      <div className="p-8">
        <h2 className="text-xl font-semibold text-gray-100 mb-4">Customers</h2>
        <EmptyState
          message="No customers yet. Upload data to connect feedback to revenue."
          cta={{ label: "Upload Customers", onClick: () => setShowUpload(true) }}
        />
      </div>
    );
  }

  const totalPages = Math.ceil(total / pageSize) || 1;

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-4 flex-wrap gap-3">
        <h2 className="text-xl font-semibold text-gray-100">Customers</h2>
        <button
          onClick={() => setShowUpload(true)}
          className="px-3 py-1.5 text-sm bg-blue-500 hover:bg-blue-600 text-white rounded-lg"
        >
          Upload Customers
        </button>
      </div>
      <div className="mb-4">
        <SearchBar
          value={search}
          onChange={(v) => { updateUrl({ q: v || undefined }); setPage(1); }}
          placeholder="Search by company, manager, industry..."
        />
      </div>
      <div className="mb-4 flex flex-wrap gap-3 items-center text-sm">
        <select
          value={segment}
          onChange={(e) => { updateUrl({ segment: e.target.value || undefined }); setPage(1); }}
          className="rounded border border-gray-600 bg-gray-800 text-gray-200 py-1.5 px-3"
        >
          <option value="">All segments</option>
          <option value="enterprise">Enterprise</option>
          <option value="smb">SMB</option>
          <option value="trial">Trial</option>
        </select>
        <input
          type="number"
          min={0}
          max={100}
          placeholder="Health min"
          value={healthMin}
          onChange={(e) => { updateUrl({ health_min: e.target.value || undefined }); setPage(1); }}
          className="rounded border border-gray-600 bg-gray-800 text-gray-200 py-1.5 px-3 w-24"
          title="Minimum health score (0-100)"
        />
        <input
          type="number"
          min={0}
          max={100}
          placeholder="Health max"
          value={healthMax}
          onChange={(e) => { updateUrl({ health_max: e.target.value || undefined }); setPage(1); }}
          className="rounded border border-gray-600 bg-gray-800 text-gray-200 py-1.5 px-3 w-24"
          title="Maximum health score (0-100)"
        />
        <select
          value={renewalWithin}
          onChange={(e) => { updateUrl({ renewal: e.target.value || undefined }); setPage(1); }}
          className="rounded border border-gray-600 bg-gray-800 text-gray-200 py-1.5 px-3"
        >
          <option value="">Renewal: All</option>
          <option value="30">Within 30d</option>
          <option value="60">Within 60d</option>
          <option value="90">Within 90d</option>
        </select>
        <select
          value={hasNegative}
          onChange={(e) => { updateUrl({ has_negative: e.target.value || undefined }); setPage(1); }}
          className="rounded border border-gray-600 bg-gray-800 text-gray-200 py-1.5 px-3"
        >
          <option value="">Has negative: All</option>
          <option value="1">Yes</option>
          <option value="0">No</option>
        </select>
        <input
          type="number"
          placeholder="ARR min"
          value={arrMin}
          onChange={(e) => { updateUrl({ arr_min: e.target.value || undefined }); setPage(1); }}
          className="rounded border border-gray-600 bg-gray-800 text-gray-200 py-1.5 px-3 w-24"
        />
        <input
          type="number"
          placeholder="ARR max"
          value={arrMax}
          onChange={(e) => { updateUrl({ arr_max: e.target.value || undefined }); setPage(1); }}
          className="rounded border border-gray-600 bg-gray-800 text-gray-200 py-1.5 px-3 w-24"
        />
      </div>
      <div className="overflow-x-auto rounded-lg border border-gray-700">
        <table className="w-full text-sm">
          <thead className="bg-gray-800/50">
            <tr className="text-left text-gray-400">
              <th className="px-4 py-3">Company</th>
              <th className="px-4 py-3">Segment</th>
              <th className="px-4 py-3">MRR</th>
              <th className="px-4 py-3">ARR</th>
              <th className="px-4 py-3">Health</th>
              <th className="px-4 py-3">Feedback</th>
              <th className="px-4 py-3">Renewal</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={7} className="px-4 py-8 text-center text-gray-400">
                  <LoadingSpinner />
                </td>
              </tr>
            ) : (
              items.map((c) => {
                const days = daysToRenewal(c.renewal_date);
                const renewalSoon = days != null && days >= 0 && days <= 60;
                return (
                  <tr
                    key={c.id}
                    onClick={() => navigate(`/customers/${c.id}`, { state: { from: "customers", searchParams: searchParams.toString() } })}
                    className="border-t border-gray-800 hover:bg-gray-800/50 cursor-pointer"
                  >
                    <td className="px-4 py-3 text-gray-100 font-medium">{c.company_name}</td>
                    <td className="px-4 py-3 text-gray-400">{c.segment ?? "—"}</td>
                    <td className="px-4 py-3 text-gray-400">{formatCurrency(c.mrr)}</td>
                    <td className="px-4 py-3 text-gray-400">{formatCurrency(c.arr)}</td>
                    <td className="px-4 py-3">
                      <span className={healthColor(c.health_score)}>
                        {c.health_score != null ? c.health_score : "—"}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-gray-400">
                      {c.feedback_count != null ? (
                        <>
                          {c.feedback_count}
                          {c.negative_feedback_count != null && c.negative_feedback_count > 0 && (
                            <span className="text-red-400 ml-1">({c.negative_feedback_count} negative)</span>
                          )}
                        </>
                      ) : (
                        "—"
                      )}
                    </td>
                    <td className="px-4 py-3">
                      {c.renewal_date ? (
                        <span className={renewalSoon ? "text-amber-400 flex items-center gap-1" : "text-gray-400"}>
                          {new Date(c.renewal_date).toLocaleDateString()}
                          {renewalSoon && <AlertCircle className="h-4 w-4" aria-label="Renewal soon" />}
                        </span>
                      ) : (
                        "—"
                      )}
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
      {totalPages > 1 && (
        <div className="flex justify-between items-center mt-4">
          <p className="text-gray-400 text-sm">
            Page {page} of {totalPages} ({total} total)
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
  );
}
