import { useState, useRef, useEffect } from "react";
import { Settings2 } from "lucide-react";

const WIDGET_IDS = [
  { id: "summary", label: "Summary Cards" },
  { id: "volume", label: "Volume Chart" },
  { id: "sentiment", label: "Sentiment Donut" },
  { id: "top_issues", label: "Top Issues" },
  { id: "areas", label: "Area Breakdown" },
  { id: "at_risk", label: "At-Risk Customers" },
  { id: "recent", label: "Recent Feedback" },
  { id: "sources", label: "Source Distribution" },
  { id: "segments", label: "Segment Breakdown" },
] as const;

interface CustomizeDashboardProps {
  visibleWidgets: string[];
  onSave: (visible: string[]) => void;
}

export function CustomizeDashboard({ visibleWidgets, onSave }: CustomizeDashboardProps) {
  const [open, setOpen] = useState(false);
  const [local, setLocal] = useState<string[]>(visibleWidgets);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setLocal(visibleWidgets);
  }, [visibleWidgets]);

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const toggle = (id: string) => {
    const next = local.includes(id) ? local.filter((w) => w !== id) : [...local, id];
    setLocal(next);
  };

  const handleSave = () => {
    onSave(local);
    setOpen(false);
  };

  return (
    <div className="relative" ref={ref}>
      <button
        type="button"
        onClick={() => setOpen(!open)}
        className="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-gray-600 bg-gray-800 text-gray-300 hover:bg-gray-700"
      >
        <Settings2 size={16} />
        Customize
      </button>
      {open && (
        <div className="absolute right-0 top-full mt-1 z-20 w-56 rounded-lg border border-gray-600 bg-gray-800 shadow-xl p-3">
          <p className="text-sm font-medium text-gray-300 mb-2">Show / Hide Widgets</p>
          <div className="space-y-1.5 max-h-64 overflow-y-auto">
            {WIDGET_IDS.map((w) => (
              <label key={w.id} className="flex items-center gap-2 cursor-pointer text-sm text-gray-200">
                <input
                  type="checkbox"
                  checked={local.includes(w.id)}
                  onChange={() => toggle(w.id)}
                  className="rounded border-gray-500"
                />
                {w.label}
              </label>
            ))}
          </div>
          <button
            type="button"
            onClick={handleSave}
            className="mt-3 w-full px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 rounded text-white text-sm"
          >
            Save
          </button>
        </div>
      )}
    </div>
  );
}
