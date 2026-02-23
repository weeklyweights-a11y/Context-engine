import { useState, useEffect } from "react";
import type { ProductArea, ProductAreas } from "../../types/product";

interface WizardStepAreasProps {
  initialData?: Partial<ProductAreas> | null;
  onSave: (data: ProductAreas) => Promise<void>;
  saving?: boolean;
  submitLabel?: "Save" | "Continue";
}

const inputClass =
  "w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-transparent";
const labelClass = "block text-sm text-gray-400 mb-1";

function emptyArea(): ProductArea {
  return { name: "", description: "" };
}

export default function WizardStepAreas({
  initialData,
  onSave,
  saving = false,
  submitLabel = "Save",
}: WizardStepAreasProps) {
  const [areas, setAreas] = useState<ProductArea[]>([emptyArea()]);

  useEffect(() => {
    if (initialData?.areas?.length) {
      setAreas(
        initialData.areas.map((a) => ({
          ...a,
          name: a.name ?? "",
          description: a.description ?? "",
        }))
      );
    }
  }, [initialData]);

  const updateArea = (i: number, field: keyof ProductArea, value: string | number) => {
    setAreas((prev) => {
      const next = [...prev];
      next[i] = { ...next[i], [field]: value };
      return next;
    });
  };

  const addArea = () => setAreas((prev) => [...prev, emptyArea()]);
  const removeArea = (i: number) =>
    setAreas((prev) => prev.filter((_, idx) => idx !== i));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const valid = areas.filter((a) => a.name.trim());
    await onSave({ areas: valid });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {areas.map((area, i) => (
        <div key={i} className="p-4 bg-gray-800/50 rounded-lg space-y-2">
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-400">Area {i + 1}</span>
            {areas.length > 1 && (
              <button
                type="button"
                onClick={() => removeArea(i)}
                className="text-red-400 hover:text-red-300 text-sm"
                aria-label="Remove area"
              >
                ✕
              </button>
            )}
          </div>
          <div>
            <label className={labelClass}>Name *</label>
            <input
              type="text"
              value={area.name}
              onChange={(e) => updateArea(i, "name", e.target.value)}
              className={inputClass}
              placeholder="e.g. Dashboard"
            />
          </div>
          <div>
            <label className={labelClass}>Description</label>
            <input
              type="text"
              value={area.description ?? ""}
              onChange={(e) => updateArea(i, "description", e.target.value)}
              className={inputClass}
            />
          </div>
        </div>
      ))}
      <button
        type="button"
        onClick={addArea}
        className="text-blue-400 hover:text-blue-300 text-sm"
      >
        + Add area
      </button>
      <p className="text-sm text-gray-500">
        Product areas help auto-detect feedback topics. You can refine these later.
      </p>
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
