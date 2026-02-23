import { useState, useEffect } from "react";
import type { Goal, ProductGoals } from "../../types/product";

interface WizardStepGoalsProps {
  initialData?: Partial<ProductGoals> | null;
  onSave: (data: ProductGoals) => Promise<void>;
  saving?: boolean;
}

const inputClass =
  "w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-transparent";
const labelClass = "block text-sm text-gray-400 mb-1";

function emptyGoal(): Goal {
  return { title: "" };
}

export default function WizardStepGoals({
  initialData,
  onSave,
  saving = false,
}: WizardStepGoalsProps) {
  const [goals, setGoals] = useState<Goal[]>([emptyGoal()]);

  useEffect(() => {
    if (initialData?.goals?.length) {
      setGoals(
        initialData.goals.map((g) => ({
          ...g,
          title: g.title ?? "",
          description: g.description ?? "",
          time_period: g.time_period ?? "",
        }))
      );
    }
  }, [initialData]);

  const updateGoal = (i: number, field: keyof Goal, value: string) => {
    setGoals((prev) => {
      const next = [...prev];
      next[i] = { ...next[i], [field]: value };
      return next;
    });
  };

  const addGoal = () => setGoals((prev) => [...prev, emptyGoal()]);
  const removeGoal = (i: number) =>
    setGoals((prev) => prev.filter((_, idx) => idx !== i));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const valid = goals.filter((g) => g.title.trim());
    await onSave({ goals: valid });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {goals.map((goal, i) => (
        <div key={i} className="p-4 bg-gray-800/50 rounded-lg space-y-2">
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-400">Goal {i + 1}</span>
            {goals.length > 1 && (
              <button
                type="button"
                onClick={() => removeGoal(i)}
                className="text-red-400 hover:text-red-300 text-sm"
              >
                Remove
              </button>
            )}
          </div>
          <div>
            <label className={labelClass}>Title *</label>
            <input
              type="text"
              value={goal.title}
              onChange={(e) => updateGoal(i, "title", e.target.value)}
              className={inputClass}
              placeholder="e.g. Improve conversion"
            />
          </div>
          <div>
            <label className={labelClass}>Description</label>
            <input
              type="text"
              value={goal.description ?? ""}
              onChange={(e) => updateGoal(i, "description", e.target.value)}
              className={inputClass}
            />
          </div>
          <div>
            <label className={labelClass}>Time period</label>
            <input
              type="text"
              value={goal.time_period ?? ""}
              onChange={(e) => updateGoal(i, "time_period", e.target.value)}
              className={inputClass}
              placeholder="e.g. Q1 2025"
            />
          </div>
        </div>
      ))}
      <button
        type="button"
        onClick={addGoal}
        className="text-blue-400 hover:text-blue-300 text-sm"
      >
        + Add goal
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
