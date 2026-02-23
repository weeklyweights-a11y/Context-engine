import { useState, useEffect } from "react";
import type {
  Segment,
  PricingTier,
  ProductSegments,
} from "../../types/product";

interface WizardStepSegmentsProps {
  initialData?: Partial<ProductSegments> | null;
  onSave: (data: ProductSegments) => Promise<void>;
  saving?: boolean;
  submitLabel?: "Save" | "Continue";
}

const inputClass =
  "w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-transparent";
const labelClass = "block text-sm text-gray-400 mb-1";

const DEFAULT_SEGMENTS: Segment[] = [
  { name: "Enterprise", description: "" },
  { name: "SMB", description: "" },
  { name: "Consumer", description: "" },
  { name: "Trial", description: "" },
];

function emptySegment(): Segment {
  return { name: "" };
}

function emptyTier(): PricingTier {
  return { name: "" };
}

export default function WizardStepSegments({
  initialData,
  onSave,
  saving = false,
  submitLabel = "Save",
}: WizardStepSegmentsProps) {
  const [segments, setSegments] = useState<Segment[]>(DEFAULT_SEGMENTS);
  const [pricingTiers, setPricingTiers] = useState<PricingTier[]>([
    emptyTier(),
  ]);

  useEffect(() => {
    if (initialData) {
      if (initialData.segments?.length) {
        setSegments(
          initialData.segments.map((s) => ({
            ...s,
            name: s.name ?? "",
            description: s.description ?? "",
          }))
        );
      } else {
        setSegments(DEFAULT_SEGMENTS);
      }
      if (initialData.pricing_tiers?.length) {
        setPricingTiers(
          initialData.pricing_tiers.map((t) => ({
            ...t,
            name: t.name ?? "",
          }))
        );
      }
    }
  }, [initialData]);

  const updateSegment = (i: number, field: keyof Segment, value: string | number) => {
    setSegments((prev) => {
      const next = [...prev];
      next[i] = { ...next[i], [field]: value };
      return next;
    });
  };

  const updateTier = (i: number, field: keyof PricingTier, value: string | number) => {
    setPricingTiers((prev) => {
      const next = [...prev];
      next[i] = { ...next[i], [field]: value };
      return next;
    });
  };

  const addSegment = () => setSegments((prev) => [...prev, emptySegment()]);
  const removeSegment = (i: number) =>
    setSegments((prev) => prev.filter((_, idx) => idx !== i));

  const addTier = () => setPricingTiers((prev) => [...prev, emptyTier()]);
  const removeTier = (i: number) =>
    setPricingTiers((prev) => prev.filter((_, idx) => idx !== i));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const validSegments = segments.filter((s) => s.name.trim());
    const validTiers = pricingTiers.filter((t) => t.name.trim());
    await onSave({
      segments: validSegments,
      pricing_tiers: validTiers,
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <h4 className="text-gray-100 font-medium mb-3">Customer segments</h4>
        {segments.map((seg, i) => (
          <div key={i} className="p-4 bg-gray-800/50 rounded-lg space-y-2 mb-3">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-400">Segment {i + 1}</span>
              {segments.length > 1 && (
                <button
                  type="button"
                  onClick={() => removeSegment(i)}
                  className="text-red-400 hover:text-red-300 text-sm"
                >
                  Remove
                </button>
              )}
            </div>
            <div>
              <label className={labelClass}>Name *</label>
              <input
                type="text"
                value={seg.name}
                onChange={(e) => updateSegment(i, "name", e.target.value)}
                className={inputClass}
                placeholder="e.g. Enterprise"
              />
            </div>
            <div>
              <label className={labelClass}>Description</label>
              <input
                type="text"
                value={seg.description ?? ""}
                onChange={(e) => updateSegment(i, "description", e.target.value)}
                className={inputClass}
              />
            </div>
            <div>
              <label className={labelClass}>Revenue share %</label>
              <input
                type="number"
                min={0}
                max={100}
                value={seg.revenue_share ?? ""}
                onChange={(e) =>
                  updateSegment(i, "revenue_share", parseFloat(e.target.value) || 0)
                }
                className={inputClass}
                placeholder="e.g. 60"
              />
            </div>
          </div>
        ))}
        <button
          type="button"
          onClick={addSegment}
          className="text-blue-400 hover:text-blue-300 text-sm"
        >
          + Add segment
        </button>
      </div>

      <div>
        <h4 className="text-gray-100 font-medium mb-3">Pricing tiers</h4>
        {pricingTiers.map((tier, i) => (
          <div key={i} className="p-4 bg-gray-800/50 rounded-lg space-y-2 mb-3">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-400">Tier {i + 1}</span>
              {pricingTiers.length > 1 && (
                <button
                  type="button"
                  onClick={() => removeTier(i)}
                  className="text-red-400 hover:text-red-300 text-sm"
                >
                  Remove
                </button>
              )}
            </div>
            <div>
              <label className={labelClass}>Name *</label>
              <input
                type="text"
                value={tier.name}
                onChange={(e) => updateTier(i, "name", e.target.value)}
                className={inputClass}
                placeholder="e.g. Pro"
              />
            </div>
            <div>
              <label className={labelClass}>Price</label>
              <input
                type="number"
                value={tier.price ?? ""}
                onChange={(e) =>
                  updateTier(i, "price", parseFloat(e.target.value) || 0)
                }
                className={inputClass}
                placeholder="0"
              />
            </div>
            <div>
              <label className={labelClass}>Period</label>
              <select
                value={tier.price_period ?? "month"}
                onChange={(e) => updateTier(i, "price_period", e.target.value)}
                className={inputClass}
              >
                <option value="month">month</option>
                <option value="year">year</option>
              </select>
            </div>
            <div>
              <label className={labelClass}>Segment</label>
              <select
                value={tier.segment_id ?? ""}
                onChange={(e) => updateTier(i, "segment_id", e.target.value)}
                className={inputClass}
              >
                <option value="">Select segment</option>
                {segments.map((s, idx) => (
                  <option key={idx} value={s.id ?? s.name ?? `seg_${idx}`}>
                    {s.name}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className={labelClass}>Features</label>
              <input
                type="text"
                value={tier.features ?? ""}
                onChange={(e) => updateTier(i, "features", e.target.value)}
                className={inputClass}
                placeholder="e.g. Unlimited users, SSO"
              />
            </div>
          </div>
        ))}
        <button
          type="button"
          onClick={addTier}
          className="text-blue-400 hover:text-blue-300 text-sm"
        >
          + Add pricing tier
        </button>
      </div>

      <button
        type="submit"
        disabled={saving}
        className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50"
      >
        {saving ? "Saving..." : submitLabel}
      </button>
    </form>
  );
}
