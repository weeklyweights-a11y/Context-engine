import { useState, useEffect } from "react";
import type { TechItem, ProductTechStack } from "../../types/product";

interface WizardStepTechStackProps {
  initialData?: Partial<ProductTechStack> | null;
  onSave: (data: ProductTechStack) => Promise<void>;
  saving?: boolean;
}

const inputClass =
  "w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-transparent";
const labelClass = "block text-sm text-gray-400 mb-1";

const CATEGORIES = [
  "Frontend",
  "Backend",
  "Database",
  "Infrastructure",
  "Monitoring",
  "Other",
] as const;

function emptyTech(): TechItem {
  return { technology: "", category: "Other" };
}

export default function WizardStepTechStack({
  initialData,
  onSave,
  saving = false,
}: WizardStepTechStackProps) {
  const [technologies, setTechnologies] = useState<TechItem[]>([emptyTech()]);

  useEffect(() => {
    if (initialData?.technologies?.length) {
      setTechnologies(
        initialData.technologies.map((t) => ({
          ...t,
          technology: t.technology ?? "",
          category: t.category ?? "Other",
        }))
      );
    }
  }, [initialData]);

  const updateTech = (
    i: number,
    field: keyof TechItem,
    value: string
  ) => {
    setTechnologies((prev) => {
      const next = [...prev];
      next[i] = { ...next[i], [field]: value };
      return next;
    });
  };

  const addTech = () => setTechnologies((prev) => [...prev, emptyTech()]);
  const removeTech = (i: number) =>
    setTechnologies((prev) => prev.filter((_, idx) => idx !== i));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const valid = technologies.filter((t) => t.technology.trim());
    await onSave({ technologies: valid });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {technologies.map((tech, i) => (
        <div key={i} className="p-4 bg-gray-800/50 rounded-lg space-y-2">
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-400">Technology {i + 1}</span>
            {technologies.length > 1 && (
              <button
                type="button"
                onClick={() => removeTech(i)}
                className="text-red-400 hover:text-red-300 text-sm"
              >
                Remove
              </button>
            )}
          </div>
          <div>
            <label className={labelClass}>Technology *</label>
            <input
              type="text"
              value={tech.technology}
              onChange={(e) => updateTech(i, "technology", e.target.value)}
              className={inputClass}
              placeholder="e.g. React"
            />
          </div>
          <div>
            <label className={labelClass}>Category</label>
            <select
              value={tech.category ?? "Other"}
              onChange={(e) => {
                const v: string = e.target.value ?? "Other";
                updateTech(i, "category", v);
              }}
              className={inputClass}
            >
              {CATEGORIES.map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className={labelClass}>Notes</label>
            <input
              type="text"
              value={tech.notes ?? ""}
              onChange={(e) => updateTech(i, "notes", e.target.value)}
              className={inputClass}
            />
          </div>
        </div>
      ))}
      <button
        type="button"
        onClick={addTech}
        className="text-blue-400 hover:text-blue-300 text-sm"
      >
        + Add technology
      </button>
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
