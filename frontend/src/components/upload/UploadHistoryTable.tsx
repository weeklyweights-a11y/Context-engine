import { useState, useEffect } from "react";
import { deleteUpload, getUploads } from "../../services/uploadApi";
import type { UploadRecord } from "../../services/uploadApi";
import LoadingSpinner from "../common/LoadingSpinner";

function formatDate(iso: string | undefined): string {
  if (!iso) return "—";
  try {
    const d = new Date(iso);
    return d.toLocaleDateString(undefined, {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return iso;
  }
}

function statusBadge(status: string) {
  const classes: Record<string, string> = {
    completed: "bg-green-900/40 text-green-400",
    failed: "bg-red-900/40 text-red-400",
    processing: "bg-yellow-900/40 text-yellow-400",
    pending: "bg-gray-700 text-gray-400",
  };
  const c = classes[status] ?? "bg-gray-700 text-gray-400";
  return <span className={`px-2 py-0.5 rounded text-xs ${c}`}>{status}</span>;
}

export default function UploadHistoryTable() {
  const [uploads, setUploads] = useState<UploadRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const loadUploads = () => {
    setLoading(true);
    getUploads()
      .then(setUploads)
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load"))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadUploads();
  }, []);

  const handleDelete = async (id: string) => {
    if (deletingId) return;
    setDeletingId(id);
    try {
      await deleteUpload(id);
      setUploads((prev) => prev.filter((u) => u.id !== id));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete");
    } finally {
      setDeletingId(null);
    }
  };

  if (loading) return <LoadingSpinner />;
  if (error) return <p className="text-red-400">{error}</p>;

  if (uploads.length === 0) {
    return (
      <p className="text-gray-400 py-8">No uploads yet. Upload feedback or customers to see history.</p>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="text-left text-gray-400 border-b border-gray-700">
            <th className="pb-2 pr-4">Date</th>
            <th className="pb-2 pr-4">Type</th>
            <th className="pb-2 pr-4">Filename</th>
            <th className="pb-2 pr-4">Items Imported</th>
            <th className="pb-2 pr-4">Status</th>
            <th className="pb-2 w-12"></th>
          </tr>
        </thead>
        <tbody>
          {uploads.map((u) => (
            <tr key={u.id} className="border-b border-gray-800">
              <td className="py-3 pr-4 text-gray-300">{formatDate(u.created_at)}</td>
              <td className="py-3 pr-4 text-gray-300 capitalize">{u.upload_type}</td>
              <td className="py-3 pr-4 text-gray-300">{u.filename ?? "—"}</td>
              <td className="py-3 pr-4 text-gray-300">{u.imported_rows ?? 0}</td>
              <td className="py-3 pr-4">{statusBadge(u.status)}</td>
              <td className="py-3">
                <button
                  type="button"
                  onClick={() => handleDelete(u.id)}
                  disabled={deletingId === u.id}
                  className="text-gray-500 hover:text-red-400 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  title="Delete"
                  aria-label="Delete upload"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
