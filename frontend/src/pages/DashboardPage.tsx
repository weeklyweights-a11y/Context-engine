import { useState, useEffect, useCallback } from "react";
import EmptyState from "../components/common/EmptyState";
import { useAgentChat } from "../hooks/useAgentChat";
import {
  getSummary,
  getVolume,
  getSentiment,
  getTopIssues,
  getAreaBreakdown,
  getAtRisk,
  getSourceDistribution,
  getSegmentBreakdown,
  getUserPreferences,
  putUserPreferences,
  type SummaryResponse,
  type VolumeResponse,
  type SentimentResponse,
  type TopIssuesResponse,
  type AreaBreakdownResponse,
  type AtRiskResponse,
  type SourceBreakdownResponse,
  type SegmentBreakdownResponse,
} from "../services/analyticsApi";
import { SummaryCards } from "../components/dashboard/SummaryCards";
import { VolumeChart } from "../components/dashboard/VolumeChart";
import { SentimentDonut } from "../components/dashboard/SentimentDonut";
import { TopIssuesWidget } from "../components/dashboard/TopIssuesWidget";
import { AreaBreakdown } from "../components/dashboard/AreaBreakdown";
import { AtRiskTable } from "../components/dashboard/AtRiskTable";
import { RecentFeedback } from "../components/dashboard/RecentFeedback";
import { SourceDistribution } from "../components/dashboard/SourceDistribution";
import { SegmentBreakdown } from "../components/dashboard/SegmentBreakdown";
import { CustomizeDashboard } from "../components/dashboard/CustomizeDashboard";
import { RefreshCw } from "lucide-react";

const DEFAULT_WIDGETS = [
  "summary",
  "volume",
  "sentiment",
  "top_issues",
  "areas",
  "at_risk",
  "recent",
  "sources",
  "segments",
];

function toISO(date: Date): string {
  return date.toISOString().split("T")[0];
}

function periodToDates(period: string): { from: string; to: string } {
  const to = new Date();
  const from = new Date();
  if (period === "7d") from.setDate(to.getDate() - 7);
  else if (period === "30d") from.setDate(to.getDate() - 30);
  else if (period === "90d") from.setDate(to.getDate() - 90);
  else {
    from.setDate(to.getDate() - 30);
  }
  return { from: toISO(from), to: toISO(to) };
}

export default function DashboardPage() {
  const { openWithMessage } = useAgentChat();
  const [period, setPeriod] = useState("30d");
  const [dateFrom, setDateFrom] = useState<string>("");
  const [dateTo, setDateTo] = useState<string>("");
  const [visibleWidgets, setVisibleWidgets] = useState<string[]>(DEFAULT_WIDGETS);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [totalFeedback, setTotalFeedback] = useState<number | null>(null);
  const [summary, setSummary] = useState<SummaryResponse | null>(null);
  const [volume, setVolume] = useState<VolumeResponse | null>(null);
  const [sentiment, setSentiment] = useState<SentimentResponse | null>(null);
  const [topIssues, setTopIssues] = useState<TopIssuesResponse | null>(null);
  const [areas, setAreas] = useState<AreaBreakdownResponse | null>(null);
  const [atRisk, setAtRisk] = useState<AtRiskResponse | null>(null);
  const [sources, setSources] = useState<SourceBreakdownResponse | null>(null);
  const [segments, setSegments] = useState<SegmentBreakdownResponse | null>(null);

  const { from, to } = period === "custom" && dateFrom && dateTo
    ? { from: dateFrom, to: dateTo }
    : periodToDates(period);

  const fetchAll = useCallback(async (showRefresh = false) => {
    if (showRefresh) setRefreshing(true);
    else setLoading(true);

    const p = period === "custom" ? "custom" : period;
    const fromParam = p === "custom" ? from : undefined;
    const toParam = p === "custom" ? to : undefined;

    try {
      const [s, v, sent, ti, ar, arisk, src, seg] = await Promise.all([
        getSummary(p, fromParam, toParam),
        getVolume(p, fromParam, toParam),
        getSentiment(p, fromParam, toParam),
        getTopIssues(p, fromParam, toParam),
        getAreaBreakdown(p, fromParam, toParam),
        getAtRisk(p, fromParam, toParam),
        getSourceDistribution(p, fromParam, toParam),
        getSegmentBreakdown(p, fromParam, toParam),
      ]);
      setSummary(s);
      setTotalFeedback(s.total_feedback);
      setVolume(v);
      setSentiment(sent);
      setTopIssues(ti);
      setAreas(ar);
      setAtRisk(arisk);
      setSources(src);
      setSegments(seg);
    } catch (e) {
      setTotalFeedback(0);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [period, from, to]);

  useEffect(() => {
    getUserPreferences()
      .then((r) => {
        const w = r.dashboard_preferences?.visible_widgets;
        if (w?.length) setVisibleWidgets(w);
      })
      .catch(() => {});
  }, []);

  useEffect(() => {
    fetchAll();
  }, [fetchAll]);

  const handleRefresh = () => fetchAll(true);

  const handleSavePreferences = (visible: string[]) => {
    setVisibleWidgets(visible);
    putUserPreferences({
      dashboard_preferences: { visible_widgets: visible },
    }).catch(() => {});
  };

  const isEmpty = totalFeedback === 0 && !loading;

  if (loading && !refreshing) {
    return (
      <div className="p-8">
        <h2 className="text-xl font-semibold text-gray-100 mb-4">Dashboard</h2>
        <div className="h-96 rounded-lg border border-gray-600 bg-gray-800/30 animate-pulse" />
      </div>
    );
  }

  if (isEmpty) {
    return (
      <div className="p-8">
        <h2 className="text-xl font-semibold text-gray-100 mb-4">Dashboard</h2>
        <EmptyState message="No data yet. Set up your product and upload feedback." />
        <div className="mt-4 flex flex-wrap gap-3">
          <button
            type="button"
            onClick={() => openWithMessage("What should we prioritize?")}
            className="px-4 py-2 text-sm bg-indigo-600 hover:bg-indigo-500 rounded text-white"
          >
            What should we prioritize?
          </button>
          <button
            type="button"
            onClick={() => openWithMessage("Investigate top issues")}
            className="px-4 py-2 text-sm bg-indigo-600 hover:bg-indigo-500 rounded text-white"
          >
            Investigate
          </button>
          <button
            type="button"
            onClick={() => openWithMessage("Generate specs for the top issue")}
            className="px-4 py-2 text-sm bg-gray-700 hover:bg-gray-600 rounded text-white"
          >
            Generate Spec
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8">
      <div className="flex flex-wrap items-center justify-between gap-4 mb-6">
        <h2 className="text-xl font-semibold text-gray-100">Dashboard</h2>
        <div className="flex items-center gap-2 flex-wrap">
          <select
            value={period}
            onChange={(e) => {
              const v = e.target.value;
              setPeriod(v);
              const d = periodToDates(v === "custom" ? "30d" : v);
              setDateFrom(d.from);
              setDateTo(d.to);
            }}
            className="px-3 py-1.5 rounded-lg border border-gray-600 bg-gray-800 text-gray-200 text-sm"
          >
            <option value="7d">Last 7 days</option>
            <option value="30d">Last 30 days</option>
            <option value="90d">Last 90 days</option>
            <option value="custom">Custom</option>
          </select>
          {period === "custom" && (
            <>
              <input
                type="date"
                value={dateFrom}
                onChange={(e) => setDateFrom(e.target.value)}
                className="px-3 py-1.5 rounded-lg border border-gray-600 bg-gray-800 text-gray-200 text-sm"
              />
              <input
                type="date"
                value={dateTo}
                onChange={(e) => setDateTo(e.target.value)}
                className="px-3 py-1.5 rounded-lg border border-gray-600 bg-gray-800 text-gray-200 text-sm"
              />
            </>
          )}
          <button
            type="button"
            onClick={handleRefresh}
            disabled={refreshing}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-gray-600 bg-gray-800 text-gray-300 hover:bg-gray-700 disabled:opacity-50"
          >
            <RefreshCw size={16} className={refreshing ? "animate-spin" : ""} />
            Refresh
          </button>
          <CustomizeDashboard visibleWidgets={visibleWidgets} onSave={handleSavePreferences} />
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {visibleWidgets.includes("summary") && (
          <div className="lg:col-span-2">
            <SummaryCards data={summary} loading={refreshing} />
          </div>
        )}
        {visibleWidgets.includes("volume") && (
          <VolumeChart data={volume} loading={refreshing} />
        )}
        {visibleWidgets.includes("sentiment") && (
          <SentimentDonut data={sentiment} loading={refreshing} />
        )}
        {visibleWidgets.includes("top_issues") && (
          <TopIssuesWidget data={topIssues} loading={refreshing} />
        )}
        {visibleWidgets.includes("areas") && (
          <AreaBreakdown data={areas} loading={refreshing} />
        )}
        {visibleWidgets.includes("at_risk") && (
          <AtRiskTable data={atRisk} loading={refreshing} />
        )}
        {visibleWidgets.includes("recent") && (
          <RecentFeedback dateFrom={from} dateTo={to} />
        )}
        {visibleWidgets.includes("sources") && (
          <SourceDistribution data={sources} loading={refreshing} />
        )}
        {visibleWidgets.includes("segments") && (
          <SegmentBreakdown data={segments} loading={refreshing} />
        )}
      </div>
    </div>
  );
}
