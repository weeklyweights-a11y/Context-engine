import { useState, useEffect } from "react";
import { FEEDBACK_SOURCES } from "../../types/feedback";
import { getWizardAll } from "../../services/productApi";
import { searchCustomers } from "../../services/customerApi";

export interface FeedbackFilters {
  product_area: string[];
  source: string[];
  sentiment: string[];
  customer_segment: string[];
  date_from?: string;
  date_to?: string;
  customer_id?: string;
  has_customer?: boolean;
}

interface FilterBarProps {
  filters: FeedbackFilters;
  onChange: (f: FeedbackFilters) => void;
}

const DATE_PRESETS: { label: string; days: number }[] = [
  { label: "7d", days: 7 },
  { label: "30d", days: 30 },
  { label: "90d", days: 90 },
];

const SENTIMENTS = ["positive", "negative", "neutral"];

export function FilterBar({ filters, onChange }: FilterBarProps) {
  const [areas, setAreas] = useState<string[]>([]);
  const [segments, setSegments] = useState<string[]>([]);
  const [customerQuery, setCustomerQuery] = useState("");
  const [customerOptions, setCustomerOptions] = useState<{ id: string; company_name: string }[]>([]);
  const [selectedCustomer, setSelectedCustomer] = useState<{ id: string; company_name: string } | null>(null);

  useEffect(() => {
    getWizardAll().then((res) => {
      const sections = res.data as Record<string, { data?: { areas?: { name: string }[]; segments?: { name: string }[] } }>;
      const areaList: string[] = [];
      const segList: string[] = [];
      Object.values(sections).forEach((sec) => {
        const d = sec?.data;
        d?.areas?.forEach((a: { name: string }) => a.name && areaList.push(a.name));
        d?.segments?.forEach((s: { name: string }) => s.name && segList.push(s.name));
      });
      setAreas([...new Set(areaList)]);
      setSegments([...new Set(segList)]);
    });
  }, []);

  useEffect(() => {
    if (!customerQuery.trim()) {
      setCustomerOptions([]);
      return;
    }
    const t = setTimeout(() => {
      searchCustomers(customerQuery).then((list) => setCustomerOptions(list));
    }, 200);
    return () => clearTimeout(t);
  }, [customerQuery]);

  const toggle = <K extends keyof FeedbackFilters>(
    key: K,
    value: FeedbackFilters[K] extends string[] ? string : never
  ) => {
    const arr = (filters[key] as string[]) ?? [];
    const next = arr.includes(value) ? arr.filter((x) => x !== value) : [...arr, value];
    onChange({ ...filters, [key]: next });
  };

  const setDateRange = (days: number) => {
    const to = new Date();
    const from = new Date();
    from.setDate(from.getDate() - days);
    onChange({
      ...filters,
      date_from: from.toISOString().split("T")[0],
      date_to: to.toISOString().split("T")[0],
    });
  };

  const clearAll = () => {
    onChange({
      product_area: [],
      source: [],
      sentiment: [],
      customer_segment: [],
      date_from: undefined,
      date_to: undefined,
      customer_id: undefined,
      has_customer: undefined,
    });
    setSelectedCustomer(null);
    setCustomerQuery("");
  };

  return (
    <div className="flex flex-wrap items-center gap-3 text-sm">
      <span className="text-gray-400">Filters:</span>
      <select
        multiple
        value={filters.product_area}
        onChange={(e) => {
          const v = Array.from(e.target.selectedOptions, (o) => o.value);
          onChange({ ...filters, product_area: v });
        }}
        className="rounded border border-gray-600 bg-gray-800 text-gray-200 py-1 px-2 min-w-[120px] max-h-24"
        title="Product area"
      >
        {areas.map((a) => (
          <option key={a} value={a}>{a}</option>
        ))}
      </select>
      <select
        multiple
        value={filters.source}
        onChange={(e) => {
          const v = Array.from(e.target.selectedOptions, (o) => o.value);
          onChange({ ...filters, source: v });
        }}
        className="rounded border border-gray-600 bg-gray-800 text-gray-200 py-1 px-2 min-w-[140px] max-h-24"
        title="Source"
      >
        {FEEDBACK_SOURCES.map((s) => (
          <option key={s.id} value={s.id}>{s.label}</option>
        ))}
      </select>
      <div className="flex gap-1">
        {SENTIMENTS.map((s) => (
          <button
            key={s}
            type="button"
            onClick={() => toggle("sentiment", s)}
            className={`rounded px-2 py-1 text-xs ${
              filters.sentiment?.includes(s)
                ? "bg-indigo-600 text-white"
                : "bg-gray-700 text-gray-300 hover:bg-gray-600"
            }`}
          >
            {s.charAt(0).toUpperCase() + s.slice(1)}
          </button>
        ))}
      </div>
      <select
        multiple
        value={filters.customer_segment ?? []}
        onChange={(e) => {
          const v = Array.from(e.target.selectedOptions, (o) => o.value);
          onChange({ ...filters, customer_segment: v });
        }}
        className="rounded border border-gray-600 bg-gray-800 text-gray-200 py-1 px-2 min-w-[100px] max-h-24"
        title="Segment"
      >
        {segments.map((s) => (
          <option key={s} value={s}>{s}</option>
        ))}
      </select>
      <div className="flex gap-1">
        {DATE_PRESETS.map(({ label, days }) => (
          <button
            key={label}
            type="button"
            onClick={() => setDateRange(days)}
            className="rounded px-2 py-1 text-xs bg-gray-700 text-gray-300 hover:bg-gray-600"
          >
            {label}
          </button>
        ))}
      </div>
      <div className="relative">
        <input
          type="text"
          value={selectedCustomer?.company_name ?? customerQuery}
          onChange={(e) => {
            setCustomerQuery(e.target.value);
            setSelectedCustomer(null);
          }}
          onFocus={() => customerQuery && setCustomerOptions(customerOptions)}
          placeholder="Customer"
          className="rounded border border-gray-600 bg-gray-800 py-1 px-2 w-40 text-gray-200 placeholder-gray-500"
        />
        {customerOptions.length > 0 && !selectedCustomer && (
          <ul className="absolute top-full left-0 mt-1 w-48 max-h-40 overflow-auto rounded border border-gray-600 bg-gray-800 py-1 z-10">
            {customerOptions.map((c) => (
              <li key={c.id}>
                <button
                  type="button"
                  className="w-full text-left px-3 py-1 text-gray-200 hover:bg-gray-700"
                  onClick={() => {
                    setSelectedCustomer(c);
                    setCustomerQuery("");
                    onChange({ ...filters, customer_id: c.id });
                    setCustomerOptions([]);
                  }}
                >
                  {c.company_name}
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
      <select
        value={filters.has_customer === true ? "linked" : filters.has_customer === false ? "unlinked" : "all"}
        onChange={(e) => {
          const v = e.target.value;
          onChange({
            ...filters,
            has_customer: v === "all" ? undefined : v === "linked",
          });
        }}
        className="rounded border border-gray-600 bg-gray-800 text-gray-200 py-1 px-2"
      >
        <option value="all">All</option>
        <option value="linked">Linked</option>
        <option value="unlinked">Unlinked</option>
      </select>
      <button
        type="button"
        onClick={clearAll}
        className="text-gray-500 hover:text-gray-300 text-xs"
      >
        Clear all
      </button>
    </div>
  );
}
