import { useState, useEffect, useCallback } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { ArrowLeft, Download, Copy, Share2, RefreshCw, Edit3, Trash2 } from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import JSZip from "jszip";
import { getSpec, updateSpec, deleteSpec, regenerateSpec } from "../services/specApi";
import type { Spec } from "../services/specApi";
import LoadingSpinner from "../components/common/LoadingSpinner";

const TABS = ["prd", "architecture", "rules", "plan"] as const;

export default function SpecDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [spec, setSpec] = useState<Spec | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<(typeof TABS)[number]>("prd");
  const [editMode, setEditMode] = useState(false);
  const [editContent, setEditContent] = useState("");
  const [saving, setSaving] = useState(false);
  const [regenerating, setRegenerating] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [toast, setToast] = useState<string | null>(null);

  const showToast = useCallback((msg: string) => {
    setToast(msg);
    setTimeout(() => setToast(null), 2000);
  }, []);

  const fetchSpec = useCallback(() => {
    if (!id) return;
    setLoading(true);
    getSpec(id)
      .then(setSpec)
      .catch(() => setSpec(null))
      .finally(() => setLoading(false));
  }, [id]);

  useEffect(() => {
    fetchSpec();
  }, [fetchSpec]);

  useEffect(() => {
    if (spec) {
      const key = activeTab === "prd" ? "prd" : activeTab;
      setEditContent(spec[key] ?? "");
    }
  }, [spec, activeTab]);

  if (!id) {
    navigate("/specs");
    return null;
  }

  if (loading || !spec) {
    return (
      <div className="p-8">
        {loading ? <LoadingSpinner /> : <p className="text-gray-500">Spec not found</p>}
      </div>
    );
  }

  const currentContent = (spec as unknown as Record<string, string>)[activeTab] ?? "";
  const displayContent = editMode ? editContent : currentContent;

  const generatedByLabel = spec.generated_by_name
    ? `Context Engine (${spec.generated_by_name})`
    : "Context Engine";

  const dataFreshness = spec.data_freshness_date
    ? `Based on feedback through ${new Date(spec.data_freshness_date).toLocaleDateString()}`
    : null;

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(displayContent);
      showToast("Copied to clipboard");
    } catch {
      showToast("Copy failed");
    }
  };

  const handleShare = async () => {
    const url = window.location.href;
    try {
      await navigator.clipboard.writeText(url);
      showToast("Link copied to clipboard");
    } catch {
      showToast("Copy failed");
    }
  };

  const handleDownloadTab = () => {
    const filename = `${activeTab}.md`;
    const blob = new Blob([displayContent], { type: "text/markdown" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = filename;
    a.click();
    URL.revokeObjectURL(a.href);
    showToast(`Downloaded ${filename}`);
  };

  const handleDownloadAll = async () => {
    const zip = new JSZip();
    zip.file("prd.md", spec.prd ?? "");
    zip.file("architecture.md", spec.architecture ?? "");
    zip.file("rules.md", spec.rules ?? "");
    zip.file("plan.md", spec.plan ?? "");
    const blob = await zip.generateAsync({ type: "blob" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = `spec-${spec.title.replace(/\s+/g, "-")}.zip`;
    a.click();
    URL.revokeObjectURL(a.href);
    showToast("Downloaded all as zip");
  };

  const handleSaveEdit = async () => {
    if (!editMode || spec.status !== "draft") return;
    setSaving(true);
    try {
      const key = activeTab === "prd" ? "prd" : activeTab;
      const updated = await updateSpec(id, { [key]: editContent });
      setSpec(updated);
      setEditMode(false);
      showToast("Saved");
    } catch {
      showToast("Save failed");
    } finally {
      setSaving(false);
    }
  };

  const handleRegenerate = async () => {
    setRegenerating(true);
    try {
      const updated = await regenerateSpec(id);
      setSpec(updated);
      setEditContent((updated as unknown as Record<string, string>)[activeTab] ?? "");
      showToast("Regenerated");
    } catch (e: unknown) {
      const msg =
        e && typeof e === "object" && "response" in e
          ? (e as { response?: { data?: { detail?: string } } }).response?.data?.detail
          : "Regenerate failed";
      showToast(String(msg));
    } finally {
      setRegenerating(false);
    }
  };

  const handleDelete = async () => {
    if (!showDeleteConfirm) {
      setShowDeleteConfirm(true);
      return;
    }
    setDeleting(true);
    try {
      await deleteSpec(id);
      navigate("/specs");
    } catch {
      showToast("Delete failed");
      setDeleting(false);
    }
  };

  return (
    <div className="p-8 flex gap-8">
      {/* Main content */}
      <div className="flex-1 min-w-0">
        <div className="mb-4">
          <button
            onClick={() => navigate("/specs")}
            className="flex items-center gap-2 text-gray-400 hover:text-gray-200 mb-2"
          >
            <ArrowLeft className="w-4 h-4" /> Back to Specs
          </button>
          <h1 className="text-2xl font-semibold text-gray-100">{spec.title}</h1>
        </div>

        <div className="flex gap-2 border-b border-gray-700 mb-4 overflow-x-auto">
          {TABS.map((tab) => (
            <button
              key={tab}
              onClick={() => {
                setEditMode(false);
                setActiveTab(tab);
              }}
              className={`px-4 py-2 text-sm font-medium capitalize border-b-2 -mb-px transition-colors ${
                activeTab === tab
                  ? "border-blue-500 text-blue-400"
                  : "border-transparent text-gray-400 hover:text-gray-200"
              }`}
            >
              {tab === "prd" ? "PRD" : tab}
            </button>
          ))}
        </div>

        <div className="flex gap-2 flex-wrap mb-4">
          <button
            onClick={handleDownloadAll}
            className="flex items-center gap-2 px-3 py-1.5 text-sm bg-gray-700 hover:bg-gray-600 rounded text-gray-200"
          >
            <Download className="w-4 h-4" /> Download All
          </button>
          <button
            onClick={handleDownloadTab}
            className="flex items-center gap-2 px-3 py-1.5 text-sm bg-gray-700 hover:bg-gray-600 rounded text-gray-200"
          >
            <Download className="w-4 h-4" /> Download Tab
          </button>
          <button
            onClick={handleCopy}
            className="flex items-center gap-2 px-3 py-1.5 text-sm bg-gray-700 hover:bg-gray-600 rounded text-gray-200"
          >
            <Copy className="w-4 h-4" /> Copy
          </button>
          <button
            onClick={handleShare}
            className="flex items-center gap-2 px-3 py-1.5 text-sm bg-gray-700 hover:bg-gray-600 rounded text-gray-200"
          >
            <Share2 className="w-4 h-4" /> Share
          </button>
          <button
            onClick={handleRegenerate}
            disabled={regenerating}
            className="flex items-center gap-2 px-3 py-1.5 text-sm bg-gray-700 hover:bg-gray-600 disabled:opacity-50 rounded text-gray-200"
          >
            <RefreshCw className={`w-4 h-4 ${regenerating ? "animate-spin" : ""}`} /> Regenerate
          </button>
          {spec.status === "draft" && (
            <>
              {editMode ? (
                <button
                  onClick={handleSaveEdit}
                  disabled={saving}
                  className="flex items-center gap-2 px-3 py-1.5 text-sm bg-blue-600 hover:bg-blue-500 disabled:opacity-50 rounded text-white"
                >
                  {saving ? "Saving…" : "Save"}
                </button>
              ) : (
                <button
                  onClick={() => setEditMode(true)}
                  className="flex items-center gap-2 px-3 py-1.5 text-sm bg-gray-700 hover:bg-gray-600 rounded text-gray-200"
                >
                  <Edit3 className="w-4 h-4" /> Edit
                </button>
              )}
            </>
          )}
          <select
            value={spec.status}
            onChange={async (e) => {
              const v = e.target.value;
              try {
                const updated = await updateSpec(id, { status: v });
                setSpec(updated);
              } catch {}
            }}
            className="px-3 py-1.5 text-sm rounded border border-gray-600 bg-gray-800 text-gray-200"
          >
            <option value="draft">Draft</option>
            <option value="final">Final</option>
            <option value="shared">Shared</option>
          </select>
          <button
            onClick={handleDelete}
            disabled={deleting}
            className="flex items-center gap-2 px-3 py-1.5 text-sm bg-red-900/50 hover:bg-red-800/50 disabled:opacity-50 rounded text-red-300"
          >
            <Trash2 className="w-4 h-4" /> Delete
          </button>
        </div>

        {showDeleteConfirm && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
            <div className="bg-gray-900 border border-gray-700 rounded-lg p-6 max-w-md">
              <p className="text-gray-100 mb-4">
                Delete this spec? This cannot be undone.
              </p>
              <div className="flex justify-end gap-2">
                <button
                  onClick={() => setShowDeleteConfirm(false)}
                  className="px-4 py-2 text-gray-300 hover:text-gray-100"
                >
                  Cancel
                </button>
                <button
                  onClick={handleDelete}
                  disabled={deleting}
                  className="px-4 py-2 bg-red-600 hover:bg-red-500 text-white rounded disabled:opacity-50"
                >
                  {deleting ? "Deleting…" : "Delete"}
                </button>
              </div>
            </div>
          </div>
        )}

        <div className="max-w-none text-gray-100 [&_h1]:text-xl [&_h1]:font-bold [&_h2]:text-lg [&_h2]:font-semibold [&_h2]:mt-6 [&_h3]:text-base [&_h3]:font-semibold [&_h3]:mt-4 [&_p]:text-gray-200 [&_p]:my-2 [&_li]:text-gray-200 [&_ul]:list-disc [&_ul]:pl-6 [&_ol]:list-decimal [&_ol]:pl-6 [&_td]:text-gray-200 [&_th]:text-gray-300 [&_th]:font-medium [&_table]:border-gray-600 [&_th]:border [&_td]:border [&_code]:text-gray-300 [&_code]:bg-gray-800 [&_code]:px-1 [&_code]:rounded [&_pre]:bg-gray-800 [&_pre]:text-gray-200 [&_pre]:p-4 [&_pre]:rounded [&_blockquote]:border-l-4 [&_blockquote]:border-gray-500 [&_blockquote]:pl-4 [&_blockquote]:text-gray-300">
          {editMode ? (
            <textarea
              value={editContent}
              onChange={(e) => setEditContent(e.target.value)}
              className="w-full min-h-[400px] rounded border border-gray-600 bg-gray-800 text-gray-100 p-4 font-mono text-sm"
            />
          ) : (
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={{
                a: ({ href, children, ...props }) => {
                  if (href && (href.startsWith("/feedback") || href.startsWith("/customers"))) {
                    return (
                      <Link to={href} className="text-indigo-400 hover:text-indigo-300" {...props}>
                        {children}
                      </Link>
                    );
                  }
                  return (
                    <a href={href} target="_blank" rel="noopener noreferrer" className="text-indigo-400 hover:text-indigo-300" {...props}>
                      {children}
                    </a>
                  );
                },
              }}
            >
              {displayContent}
            </ReactMarkdown>
          )}
        </div>
      </div>

      {/* Sidebar metadata */}
      <aside className="w-64 shrink-0 space-y-4">
        <div className="rounded-lg border border-gray-700 bg-gray-900/50 p-4 space-y-2 text-sm">
          <p><span className="text-gray-500">Generated by:</span> {generatedByLabel}</p>
          <p><span className="text-gray-500">Date:</span> {new Date(spec.created_at).toLocaleDateString()}</p>
          <p><span className="text-gray-500">Feedback items:</span> {spec.feedback_count}</p>
          <p><span className="text-gray-500">Customers cited:</span> {spec.customer_count}</p>
          {spec.product_area && (
            <p><span className="text-gray-500">Product area:</span> {spec.product_area}</p>
          )}
          {dataFreshness && (
            <p className="text-gray-400">{dataFreshness}</p>
          )}
          {spec.linked_goal_id && (
            <p><span className="text-gray-500">Linked goal:</span> {spec.linked_goal_id}</p>
          )}
        </div>
      </aside>

      {toast && (
        <div className="fixed bottom-6 right-6 px-4 py-2 rounded bg-gray-800 border border-gray-600 text-gray-100 shadow-lg z-50">
          {toast}
        </div>
      )}
    </div>
  );
}
