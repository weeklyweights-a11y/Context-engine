import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { X } from "lucide-react";
import { generateSpecs } from "../../services/specApi";

interface GenerateSpecModalProps {
  onClose: () => void;
  prefilledTopic?: string;
  prefilledProductArea?: string;
}

export default function GenerateSpecModal({
  onClose,
  prefilledTopic = "",
  prefilledProductArea = "",
}: GenerateSpecModalProps) {
  const navigate = useNavigate();
  const [topic, setTopic] = useState(prefilledTopic);
  const [productArea, setProductArea] = useState(prefilledProductArea);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!topic.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const res = await generateSpecs({
        topic: topic.trim(),
        product_area: productArea.trim() || undefined,
      });
      onClose();
      navigate(`/specs/${res.id}`);
    } catch (err: unknown) {
      const msg =
        err && typeof err === "object" && "response" in err
          ? (err as { response?: { data?: { detail?: string } } }).response?.data?.detail
          : "Failed to generate specs";
      setError(String(msg));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="w-full max-w-md rounded-lg bg-gray-900 border border-gray-700 shadow-xl p-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold text-gray-100">Generate New Spec</h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-200 p-1"
            disabled={loading}
          >
            <X className="w-5 h-5" />
          </button>
        </div>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="topic" className="block text-sm font-medium text-gray-300 mb-1">
              Topic *
            </label>
            <input
              id="topic"
              type="text"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="e.g. checkout form state loss"
              required
              className="w-full rounded border border-gray-600 bg-gray-800 text-gray-100 px-3 py-2"
              disabled={loading}
            />
          </div>
          <div>
            <label htmlFor="productArea" className="block text-sm font-medium text-gray-300 mb-1">
              Product area (optional)
            </label>
            <input
              id="productArea"
              type="text"
              value={productArea}
              onChange={(e) => setProductArea(e.target.value)}
              placeholder="e.g. checkout"
              className="w-full rounded border border-gray-600 bg-gray-800 text-gray-100 px-3 py-2"
              disabled={loading}
            />
          </div>
          {error && <p className="text-sm text-red-400">{error}</p>}
          {loading && (
            <p className="text-sm text-gray-400">
              Generating specs… this may take up to 60 seconds
            </p>
          )}
          <div className="flex justify-end gap-2 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-300 hover:text-gray-100"
              disabled={loading}
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading || !topic.trim()}
              className="px-4 py-2 bg-blue-500 hover:bg-blue-600 disabled:opacity-50 text-white rounded"
            >
              {loading ? "Generating…" : "Generate"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
