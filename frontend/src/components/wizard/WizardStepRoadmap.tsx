import { useState, useEffect } from "react";
import type {
  ExistingFeature,
  PlannedFeature,
  ProductRoadmap,
} from "../../types/product";

interface WizardStepRoadmapProps {
  initialData?: Partial<ProductRoadmap> | null;
  onSave: (data: ProductRoadmap) => Promise<void>;
  saving?: boolean;
}

const inputClass =
  "w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-transparent";
const labelClass = "block text-sm text-gray-400 mb-1";

function emptyExisting(): ExistingFeature {
  return { name: "", status: "live" };
}

function emptyPlanned(): PlannedFeature {
  return { name: "", status: "planned" };
}

export default function WizardStepRoadmap({
  initialData,
  onSave,
  saving = false,
}: WizardStepRoadmapProps) {
  const [existingFeatures, setExistingFeatures] = useState<ExistingFeature[]>([
    emptyExisting(),
  ]);
  const [plannedFeatures, setPlannedFeatures] = useState<PlannedFeature[]>([
    emptyPlanned(),
  ]);

  useEffect(() => {
    if (initialData) {
      if (initialData.existing_features?.length) {
        setExistingFeatures(
          initialData.existing_features.map((f) => ({
            ...f,
            name: f.name ?? "",
          }))
        );
      }
      if (initialData.planned_features?.length) {
        setPlannedFeatures(
          initialData.planned_features.map((f) => ({
            ...f,
            name: f.name ?? "",
          }))
        );
      }
    }
  }, [initialData]);

  const updateExisting = (
    i: number,
    field: keyof ExistingFeature,
    value: string
  ) => {
    setExistingFeatures((prev) => {
      const next = [...prev];
      next[i] = { ...next[i], [field]: value };
      return next;
    });
  };

  const updatePlanned = (
    i: number,
    field: keyof PlannedFeature,
    value: string
  ) => {
    setPlannedFeatures((prev) => {
      const next = [...prev];
      next[i] = { ...next[i], [field]: value };
      return next;
    });
  };

  const addExisting = () =>
    setExistingFeatures((prev) => [...prev, emptyExisting()]);
  const removeExisting = (i: number) =>
    setExistingFeatures((prev) => prev.filter((_, idx) => idx !== i));

  const addPlanned = () =>
    setPlannedFeatures((prev) => [...prev, emptyPlanned()]);
  const removePlanned = (i: number) =>
    setPlannedFeatures((prev) => prev.filter((_, idx) => idx !== i));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const validExisting = existingFeatures.filter((f) => f.name.trim());
    const validPlanned = plannedFeatures.filter((f) => f.name.trim());
    await onSave({
      existing_features: validExisting,
      planned_features: validPlanned,
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <h4 className="text-gray-100 font-medium mb-3">Existing features</h4>
        {existingFeatures.map((f, i) => (
          <div key={i} className="p-4 bg-gray-800/50 rounded-lg space-y-2 mb-3">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-400">Feature {i + 1}</span>
              {existingFeatures.length > 1 && (
                <button
                  type="button"
                  onClick={() => removeExisting(i)}
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
                value={f.name}
                onChange={(e) => updateExisting(i, "name", e.target.value)}
                className={inputClass}
                placeholder="e.g. User dashboard"
              />
            </div>
            <div>
              <label className={labelClass}>Status</label>
              <select
                value={f.status ?? "live"}
                onChange={(e) => {
                  const v: string = e.target.value ?? "live";
                  updateExisting(i, "status", v);
                }}
                className={inputClass}
              >
                <option value="live">Live</option>
                <option value="beta">Beta</option>
                <option value="deprecated">Deprecated</option>
              </select>
            </div>
          </div>
        ))}
        <button
          type="button"
          onClick={addExisting}
          className="text-blue-400 hover:text-blue-300 text-sm"
        >
          + Add existing feature
        </button>
      </div>

      <div>
        <h4 className="text-gray-100 font-medium mb-3">Planned features</h4>
        {plannedFeatures.map((f, i) => (
          <div key={i} className="p-4 bg-gray-800/50 rounded-lg space-y-2 mb-3">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-400">Feature {i + 1}</span>
              {plannedFeatures.length > 1 && (
                <button
                  type="button"
                  onClick={() => removePlanned(i)}
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
                value={f.name}
                onChange={(e) => updatePlanned(i, "name", e.target.value)}
                className={inputClass}
                placeholder="e.g. API v2"
              />
            </div>
            <div>
              <label className={labelClass}>Status</label>
              <select
                value={f.status ?? "planned"}
                onChange={(e) => {
                  const v: string = e.target.value ?? "planned";
                  updatePlanned(i, "status", v);
                }}
                className={inputClass}
              >
                <option value="planned">Planned</option>
                <option value="in_progress">In progress</option>
                <option value="blocked">Blocked</option>
              </select>
            </div>
            <div>
              <label className={labelClass}>Target date</label>
              <input
                type="text"
                value={f.target_date ?? ""}
                onChange={(e) => updatePlanned(i, "target_date", e.target.value)}
                className={inputClass}
                placeholder="e.g. Q2 2025"
              />
            </div>
          </div>
        ))}
        <button
          type="button"
          onClick={addPlanned}
          className="text-blue-400 hover:text-blue-300 text-sm"
        >
          + Add planned feature
        </button>
      </div>

      <button
        type="submit"
        disabled={saving}
        className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50"
      >
        {saving ? "Saving..." : "Save"}
      </button>
    </form>
  );
}
