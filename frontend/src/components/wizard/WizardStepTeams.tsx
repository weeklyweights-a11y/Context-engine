import { useState, useEffect } from "react";
import type { Team, ProductTeams } from "../../types/product";

interface WizardStepTeamsProps {
  initialData?: Partial<ProductTeams> | null;
  onSave: (data: ProductTeams) => Promise<void>;
  saving?: boolean;
}

const inputClass =
  "w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-transparent";
const labelClass = "block text-sm text-gray-400 mb-1";

function emptyTeam(): Team {
  return { name: "" };
}

export default function WizardStepTeams({
  initialData,
  onSave,
  saving = false,
}: WizardStepTeamsProps) {
  const [teams, setTeams] = useState<Team[]>([emptyTeam()]);

  useEffect(() => {
    if (initialData?.teams?.length) {
      setTeams(
        initialData.teams.map((t) => ({
          ...t,
          name: t.name ?? "",
          lead: t.lead ?? "",
        }))
      );
    }
  }, [initialData]);

  const updateTeam = (i: number, field: keyof Team, value: string | number) => {
    setTeams((prev) => {
      const next = [...prev];
      next[i] = { ...next[i], [field]: value };
      return next;
    });
  };

  const addTeam = () => setTeams((prev) => [...prev, emptyTeam()]);
  const removeTeam = (i: number) =>
    setTeams((prev) => prev.filter((_, idx) => idx !== i));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const valid = teams.filter((t) => t.name.trim());
    await onSave({ teams: valid });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {teams.map((team, i) => (
        <div key={i} className="p-4 bg-gray-800/50 rounded-lg space-y-2">
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-400">Team {i + 1}</span>
            {teams.length > 1 && (
              <button
                type="button"
                onClick={() => removeTeam(i)}
                className="text-red-400 hover:text-red-300 text-sm"
              >
                Remove
              </button>
            )}
          </div>
          <div>
            <label className={labelClass}>Team name *</label>
            <input
              type="text"
              value={team.name}
              onChange={(e) => updateTeam(i, "name", e.target.value)}
              className={inputClass}
              placeholder="e.g. Platform"
            />
          </div>
          <div>
            <label className={labelClass}>Lead</label>
            <input
              type="text"
              value={team.lead ?? ""}
              onChange={(e) => updateTeam(i, "lead", e.target.value)}
              className={inputClass}
            />
          </div>
          <div>
            <label className={labelClass}>Size</label>
            <input
              type="number"
              value={team.size ?? ""}
              onChange={(e) =>
                updateTeam(i, "size", parseInt(e.target.value, 10) || 0)
              }
              className={inputClass}
            />
          </div>
          <div>
            <label className={labelClass}>Slack channel</label>
            <input
              type="text"
              value={team.slack_channel ?? ""}
              onChange={(e) => updateTeam(i, "slack_channel", e.target.value)}
              className={inputClass}
            />
          </div>
        </div>
      ))}
      <button
        type="button"
        onClick={addTeam}
        className="text-blue-400 hover:text-blue-300 text-sm"
      >
        + Add team
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
