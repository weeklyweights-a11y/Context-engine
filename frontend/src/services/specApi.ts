import { api } from "./api";
import type { ApiResponse, PaginatedResponse } from "../types/common";

const PREFIX = "/specs";

export interface Spec {
  id: string;
  org_id: string;
  title: string;
  topic: string;
  product_area?: string | null;
  status: string;
  prd?: string;
  architecture?: string;
  rules?: string;
  plan?: string;
  feedback_count: number;
  customer_count: number;
  total_arr: number;
  feedback_ids?: string[];
  customer_ids?: string[];
  linked_goal_id?: string | null;
  generated_by?: string | null;
  generated_by_name?: string | null;
  data_freshness_date?: string | null;
  created_at: string;
  updated_at: string;
}

export interface GenerateSpecResponse {
  id: string;
  title: string;
  status: string;
  feedback_count: number;
  customer_count: number;
  total_arr: number;
  created_at: string;
}

/** Generate specs for a topic. */
export async function generateSpecs(body: {
  topic: string;
  product_area?: string;
}): Promise<GenerateSpecResponse> {
  const { data } = await api.post<ApiResponse<GenerateSpecResponse>>(
    `${PREFIX}/generate`,
    body
  );
  return data.data;
}

/** List specs with pagination and filters. */
export async function getSpecs(params?: {
  page?: number;
  page_size?: number;
  product_area?: string;
  status?: string;
  date_from?: string;
  date_to?: string;
  customer_id?: string;
}): Promise<{ data: Spec[]; pagination: { page: number; page_size: number; total: number } }> {
  const searchParams = new URLSearchParams();
  if (params?.page != null) searchParams.set("page", String(params.page));
  if (params?.page_size != null) searchParams.set("page_size", String(params.page_size));
  if (params?.product_area) searchParams.set("product_area", params.product_area);
  if (params?.status) searchParams.set("status", params.status);
  if (params?.date_from) searchParams.set("date_from", params.date_from);
  if (params?.date_to) searchParams.set("date_to", params.date_to);
  if (params?.customer_id) searchParams.set("customer_id", params.customer_id);
  const qs = searchParams.toString();
  const url = qs ? `${PREFIX}?${qs}` : PREFIX;
  const { data } = await api.get<PaginatedResponse<Spec>>(url);
  return data;
}

/** Get single spec with full 4 docs. */
export async function getSpec(id: string): Promise<Spec> {
  const { data } = await api.get<ApiResponse<Spec>>(`${PREFIX}/${id}`);
  return data.data;
}

/** Update spec status or content. */
export async function updateSpec(
  id: string,
  body: {
    status?: string;
    prd?: string;
    architecture?: string;
    rules?: string;
    plan?: string;
    title?: string;
  }
): Promise<Spec> {
  const { data } = await api.put<ApiResponse<Spec>>(`${PREFIX}/${id}`, body);
  return data.data;
}

/** Delete spec. */
export async function deleteSpec(id: string): Promise<void> {
  await api.delete(`${PREFIX}/${id}`);
}

/** Regenerate 4 docs from saved data_brief. */
export async function regenerateSpec(id: string): Promise<Spec> {
  const { data } = await api.post<ApiResponse<Spec>>(`${PREFIX}/${id}/regenerate`);
  return data.data;
}
