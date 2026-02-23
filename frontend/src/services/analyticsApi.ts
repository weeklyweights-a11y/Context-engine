import { api } from "./api";

const PREFIX = "/analytics";

export interface SummaryResponse {
  total_feedback: number;
  total_feedback_trend: number | null;
  avg_sentiment: number;
  avg_sentiment_trend: number | null;
  active_issues: number;
  active_issues_trend: number | null;
  at_risk_customers: number;
}

export interface VolumeResponse {
  periods: { date: string; count: number; by_area?: Record<string, number> }[];
}

export interface SentimentResponse {
  breakdown: { sentiment: string; count: number; percentage: number }[];
  total: number;
}

export interface TopIssue {
  product_area: string;
  issue_name: string;
  feedback_count: number;
  growth_rate: number | null;
  severity: string;
  affected_customers: number;
  avg_sentiment: number;
}

export interface TopIssuesResponse {
  issues: TopIssue[];
}

export interface AreaBreakdownItem {
  product_area: string;
  count: number;
  avg_sentiment: number;
}

export interface AreaBreakdownResponse {
  areas: AreaBreakdownItem[];
}

export interface AtRiskCustomer {
  id: string;
  company_name: string;
  arr?: number;
  renewal_date?: string;
  health_score?: number;
  negative_feedback_count: number;
}

export interface AtRiskResponse {
  customers: AtRiskCustomer[];
}

export interface SourceBreakdownItem {
  source: string;
  count: number;
  percentage: number;
}

export interface SourceBreakdownResponse {
  breakdown: SourceBreakdownItem[];
  total: number;
}

export interface SegmentBreakdownItem {
  segment: string;
  count: number;
  by_area: { product_area: string; count: number }[];
}

export interface SegmentBreakdownResponse {
  segments: SegmentBreakdownItem[];
}

export interface DashboardPreferences {
  visible_widgets: string[];
  default_period: string;
}

export interface ConfigResponse {
  kibana_url: string;
}

function buildParams(period: string, from?: string, to?: string): string {
  const params = new URLSearchParams();
  params.set("period", period);
  if (period === "custom" && from && to) {
    params.set("from", from);
    params.set("to", to);
  }
  return params.toString();
}

export async function getSummary(
  period = "30d",
  from?: string,
  to?: string
): Promise<SummaryResponse> {
  const { data } = await api.get<SummaryResponse>(
    `${PREFIX}/summary?${buildParams(period, from, to)}`
  );
  return data;
}

export async function getVolume(
  period = "30d",
  from?: string,
  to?: string,
  areas?: string[]
): Promise<VolumeResponse> {
  let url = `${PREFIX}/volume?${buildParams(period, from, to)}`;
  if (areas?.length) url += `&areas=${areas.join(",")}`;
  const { data } = await api.get<VolumeResponse>(url);
  return data;
}

export async function getSentiment(
  period = "30d",
  from?: string,
  to?: string
): Promise<SentimentResponse> {
  const { data } = await api.get<SentimentResponse>(
    `${PREFIX}/sentiment?${buildParams(period, from, to)}`
  );
  return data;
}

export async function getTopIssues(
  period = "30d",
  from?: string,
  to?: string,
  limit = 5
): Promise<TopIssuesResponse> {
  const { data } = await api.get<TopIssuesResponse>(
    `${PREFIX}/top-issues?${buildParams(period, from, to)}&limit=${limit}`
  );
  return data;
}

export async function getAreaBreakdown(
  period = "30d",
  from?: string,
  to?: string
): Promise<AreaBreakdownResponse> {
  const { data } = await api.get<AreaBreakdownResponse>(
    `${PREFIX}/areas?${buildParams(period, from, to)}`
  );
  return data;
}

export async function getAtRisk(
  period = "30d",
  from?: string,
  to?: string,
  limit = 5
): Promise<AtRiskResponse> {
  const { data } = await api.get<AtRiskResponse>(
    `${PREFIX}/at-risk?${buildParams(period, from, to)}&limit=${limit}`
  );
  return data;
}

export async function getSourceDistribution(
  period = "30d",
  from?: string,
  to?: string
): Promise<SourceBreakdownResponse> {
  const { data } = await api.get<SourceBreakdownResponse>(
    `${PREFIX}/sources?${buildParams(period, from, to)}`
  );
  return data;
}

export async function getSegmentBreakdown(
  period = "30d",
  from?: string,
  to?: string
): Promise<SegmentBreakdownResponse> {
  const { data } = await api.get<SegmentBreakdownResponse>(
    `${PREFIX}/segments?${buildParams(period, from, to)}`
  );
  return data;
}

export async function getUserPreferences(): Promise<{
  dashboard_preferences: DashboardPreferences;
}> {
  const { data } = await api.get<{ dashboard_preferences: DashboardPreferences }>(
    "/user/preferences"
  );
  return data;
}

export async function putUserPreferences(body: {
  dashboard_preferences?: Partial<DashboardPreferences>;
}): Promise<{ dashboard_preferences: DashboardPreferences }> {
  const { data } = await api.put<{
    dashboard_preferences: DashboardPreferences;
  }>("/user/preferences", body);
  return data;
}

export async function getConfig(): Promise<ConfigResponse> {
  const { data } = await api.get<ConfigResponse>("/config");
  return data;
}
