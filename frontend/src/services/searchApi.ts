import { api } from "./api";
import type { ApiResponse } from "../types/common";
import type { Feedback } from "../types/feedback";

const PREFIX = "/search";
const FEEDBACK_PREFIX = "/feedback";

export interface SearchFeedbackFilters {
  product_area?: string[];
  source?: string[];
  sentiment?: string[];
  customer_segment?: string[];
  date_from?: string;
  date_to?: string;
  customer_id?: string;
  has_customer?: boolean;
}

export interface SearchFeedbackParams {
  query?: string;
  filters?: SearchFeedbackFilters;
  sort_by?: string;
  page?: number;
  page_size?: number;
}

/** Hybrid semantic + keyword search on feedback. */
export async function searchFeedback(params: SearchFeedbackParams): Promise<{
  data: Feedback[];
  pagination: { page: number; page_size: number; total: number };
  query: string;
}> {
  const { data } = await api.post<{
    data: Feedback[];
    pagination: { page: number; page_size: number; total: number };
    query: string;
  }>(`${PREFIX}/feedback`, {
    query: params.query ?? "",
    filters: params.filters ?? null,
    sort_by: params.sort_by ?? "relevance",
    page: params.page ?? 1,
    page_size: params.page_size ?? 20,
  });
  return data;
}

/** Get similar feedback items. */
export async function getSimilarFeedback(id: string): Promise<Feedback[]> {
  const { data } = await api.get<ApiResponse<Feedback[]>>(`${FEEDBACK_PREFIX}/${id}/similar`);
  return data.data;
}
