import { useState, useEffect, useCallback } from "react";
import { useSearchParams } from "react-router-dom";
import {
  getSummary,
  getVolume,
  getSentiment,
  getTopIssues,
  getAreaBreakdown,
  getAtRisk,
  getSourceDistribution,
  getSegmentBreakdown,
  getConfig,
  type SummaryResponse,
  type VolumeResponse,
  type SentimentResponse,
  type TopIssuesResponse,
  type AreaBreakdownResponse,
  type AtRiskResponse,
  type SourceBreakdownResponse,
  type SegmentBreakdownResponse,
} from "../services/analyticsApi";
import { searchFeedback } from "../services/searchApi";
import { SummaryCards } from "../components/dashboard/SummaryCards";
import { VolumeChart } from "../components/dashboard/VolumeChart";
import { SentimentDonut } from "../components/dashboard/SentimentDonut";
import { TopIssuesWidget } from "../components/dashboard/TopIssuesWidget";
import { AreaBreakdown } from "../components/dashboard/AreaBreakdown";
import { AtRiskTable } from "../components/dashboard/AtRiskTable";
import { SourceDistribution } from "../components/dashboard/SourceDistribution";
import { SegmentBreakdown } from "../components/dashboard/SegmentBreakdown";
import { FeedbackCard } from "../components/feedback/FeedbackCard";
import { ExternalLink } from "lucide-react";
import type { Feedback } from "../types/feedback";

const TABS = [
  { id: "overview", label: "Feedback Overview" },
  { id: "trends", label: "Trends & Alerts" },
  { id: "deepdive", label: "Deep Dive" },
  { id: "custom", label: "Custom" },
] as const;

function toISO(d: Date): string {
  return d.toISOString().split("T")[0];
}

function periodToDates(p: string): { from: string; to: string } {
  const to = new Date();
  const from = new Date();
  if (p === "7d") from.setDate(to.getDate() - 7);
  else if (p === "30d") from.setDate(to.getDate() - 30);
  else if (p === "90d") from.setDate(to.getDate() - 90);
  else from.setDate(to.getDate() - 30);
  return { from: toISO(from), to: toISO(to) };
}

export default function AnalyticsPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const tabParam = searchParams.get("tab") ?? "overview";
  const activeTab = TABS.find((t) => t.id === tabParam)?.id ?? "overview";

  const [period, setPeriod] = useState("30d");
  const { from, to } = periodToDates(period);

  const [summary, setSummary] = useState<SummaryResponse | null>(null);
  const [volume, setVolume] = useState<VolumeResponse | null>(null);
  const [sentiment, setSentiment] = useState<SentimentResponse | null>(null);
  const [topIssues, setTopIssues] = useState<TopIssuesResponse | null>(null);
  const [areas, setAreas] = useState<AreaBreakdownResponse | null>(null);
  const [atRisk, setAtRisk] = useState<AtRiskResponse | null>(null);
  const [sources, setSources] = useState<SourceBreakdownResponse | null>(null);
  const [segments, setSegments] = useState<SegmentBreakdownResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [kibanaUrl, setKibanaUrl] = useState<string>("");

  const [deepFilters, setDeepFilters] = useState({
    area: "",
    source: "",
    sentiment: "",
    segment: "",
  });
  const [deepFeedback, setDeepFeedback] = useState<Feedback[]>([]);
  const [deepLoading, setDeepLoading] = useState(false);

  useEffect(() => {
    getConfig()
      .then((c) => setKibanaUrl(c.kibana_url || ""))
      .catch(() => {});
  }, []);

  const fetchAnalytics = useCallback(async () => {
    setLoading(true);
    const p = period === "custom" ? "30d" : period;
    const { from: f, to: t } = periodToDates(p);
    try {
      const [s, v, sent, ti, ar, arisk, src, seg] = await Promise.all([
        getSummary(p, f, t),
        getVolume(p, f, t),
        getSentiment(p, f, t),
        getTopIssues(p, f, t),
        getAreaBreakdown(p, f, t),
        getAtRisk(p, f, t),
        getSourceDistribution(p, f, t),
        getSegmentBreakdown(p, f, t),
      ]);
      setSummary(s);
      setVolume(v);
      setSentiment(sent);
      setTopIssues(ti);
      setAreas(ar);
      setAtRisk(arisk);
      setSources(src);
      setSegments(seg);
    } finally {
      setLoading(false);
    }
  }, [period]);

  useEffect(() => {
    fetchAnalytics();
  }, [fetchAnalytics]);

  useEffect(() => {
    if (activeTab !== "deepdive") return;
    setDeepLoading(true);
    const filters: { product_area?: string[]; source?: string[]; sentiment?: string[]; customer_segment?: string[] } = {};
    if (deepFilters.area) filters.product_area = [deepFilters.area];
    if (deepFilters.source) filters.source = [deepFilters.source];
    if (deepFilters.sentiment) filters.sentiment = [deepFilters.sentiment];
    if (deepFilters.segment) filters.customer_segment = [deepFilters.segment];
    searchFeedback({
      query: "",
      filters: Object.keys(filters).length ? filters : undefined,
      sort_by: "date",
      page: 1,
      page_size: 50,
    })
      .then((r) => setDeepFeedback(r.data))
      .finally(() => setDeepLoading(false));
  }, [activeTab, deepFilters]);

  const setTab = (id: string) => {
    setSearchParams((p) => {
      const n = new URLSearchParams(p);
      n.set("tab", id);
      return n;
    });
  };

  const totalFeedback = summary?.total_feedback ?? 0;
  const isEmpty = totalFeedback === 0 && !loading;

  return (
    <div className="p-8">
      <div className="flex flex-wrap items-center justify-between gap-4 mb-6">
        <h2 className="text-xl font-semibold text-gray-100">Analytics</h2>
        <div className="flex items-center gap-2">
          <select
            value={period}
            onChange={(e) => setPeriod(e.target.value)}
            className="rounded border border-gray-600 bg-gray-800 text-gray-200 py-1.5 px-3 text-sm"
          >
            <option value="7d">Last 7 days</option>
            <option value="30d">Last 30 days</option>
            <option value="90d">Last 90 days</option>
          </select>
          {kibanaUrl && (
            <a
              href={kibanaUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-gray-600 bg-gray-800 text-gray-300 hover:bg-gray-700 text-sm"
            >
              <ExternalLink size={14} />
              Open in Kibana
            </a>
          )}
        </div>
      </div>

      <div className="flex gap-1 border-b border-gray-600 mb-6">
        {TABS.map((t) => (
          <button
            key={t.id}
            type="button"
            onClick={() => setTab(t.id)}
            className={`px-4 py-2 text-sm font-medium rounded-t ${
              activeTab === t.id
                ? "bg-gray-800 text-gray-100 border border-gray-600 border-b-0 -mb-px"
                : "text-gray-400 hover:text-gray-200"
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {activeTab === "overview" && (
        <>
          {isEmpty ? (
            <p className="text-gray-500 py-8">No feedback data yet. Upload feedback to see analytics.</p>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="lg:col-span-2">
                <SummaryCards data={summary} loading={loading} />
              </div>
              <VolumeChart data={volume} loading={loading} />
              <SentimentDonut data={sentiment} loading={loading} />
              <TopIssuesWidget data={topIssues} loading={loading} />
              <AreaBreakdown data={areas} loading={loading} />
              <AtRiskTable data={atRisk} loading={loading} />
              <SourceDistribution data={sources} loading={loading} />
              <SegmentBreakdown data={segments} loading={loading} />
            </div>
          )}
        </>
      )}

      {activeTab === "trends" && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {isEmpty ? (
            <p className="text-gray-500 py-8 col-span-2">No feedback data yet.</p>
          ) : (
            <>
              <VolumeChart data={volume} loading={loading} />
              <SentimentDonut data={sentiment} loading={loading} />
              <TopIssuesWidget data={topIssues} loading={loading} />
              <AtRiskTable data={atRisk} loading={loading} />
            </>
          )}
        </div>
      )}

      {activeTab === "deepdive" && (
        <div>
          <div className="flex flex-wrap gap-3 mb-4">
            <select
              value={deepFilters.area}
              onChange={(e) => setDeepFilters((f) => ({ ...f, area: e.target.value }))}
              className="rounded border border-gray-600 bg-gray-800 text-gray-200 py-1.5 px-3 text-sm"
            >
              <option value="">All areas</option>
              {areas?.areas?.map((a) => (
                <option key={a.product_area} value={a.product_area}>{a.product_area}</option>
              ))}
            </select>
            <select
              value={deepFilters.source}
              onChange={(e) => setDeepFilters((f) => ({ ...f, source: e.target.value }))}
              className="rounded border border-gray-600 bg-gray-800 text-gray-200 py-1.5 px-3 text-sm"
            >
              <option value="">All sources</option>
              {sources?.breakdown?.map((b) => (
                <option key={b.source} value={b.source}>{b.source}</option>
              ))}
            </select>
            <select
              value={deepFilters.sentiment}
              onChange={(e) => setDeepFilters((f) => ({ ...f, sentiment: e.target.value }))}
              className="rounded border border-gray-600 bg-gray-800 text-gray-200 py-1.5 px-3 text-sm"
            >
              <option value="">All sentiments</option>
              <option value="positive">Positive</option>
              <option value="negative">Negative</option>
              <option value="neutral">Neutral</option>
            </select>
            <select
              value={deepFilters.segment}
              onChange={(e) => setDeepFilters((f) => ({ ...f, segment: e.target.value }))}
              className="rounded border border-gray-600 bg-gray-800 text-gray-200 py-1.5 px-3 text-sm"
            >
              <option value="">All segments</option>
              {segments?.segments?.map((s) => (
                <option key={s.segment} value={s.segment}>{s.segment}</option>
              ))}
            </select>
          </div>
          {deepLoading ? (
            <p className="text-gray-500 py-8">Loading...</p>
          ) : deepFeedback.length === 0 ? (
            <p className="text-gray-500 py-8">No feedback matches the filters.</p>
          ) : (
            <div className="space-y-2">
              {deepFeedback.map((item) => (
                <FeedbackCard key={item.id} item={item} onClick={() => {}} />
              ))}
            </div>
          )}
        </div>
      )}

      {activeTab === "custom" && (
        <div className="rounded-lg border border-gray-600 bg-gray-800/50 p-8 text-center">
          <p className="text-gray-400 mb-4">For custom dashboards and advanced analytics, use Kibana.</p>
          {kibanaUrl ? (
            <a
              href={kibanaUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg"
            >
              <ExternalLink size={16} />
              Open Kibana
            </a>
          ) : (
            <p className="text-gray-500 text-sm">Kibana URL is not configured.</p>
          )}
        </div>
      )}
    </div>
  );
}
