import { api } from "./api";
import type { ApiResponse, PaginatedResponse } from "../types/common";
import type {
  Feedback,
  FeedbackUploadInit,
  FeedbackUploadConfirm,
  FeedbackUploadImport,
} from "../types/feedback";

const PREFIX = "/feedback";

/** List feedback with pagination and filters. */
export async function getFeedbackList(params?: {
  page?: number;
  page_size?: number;
  source_type?: string;
  product_area?: string;
  sentiment?: string;
  sort_by?: string;
  sort_order?: string;
}): Promise<{ data: Feedback[]; pagination: { page: number; page_size: number; total: number } }> {
  const searchParams = new URLSearchParams();
  if (params?.page) searchParams.set("page", String(params.page));
  if (params?.page_size) searchParams.set("page_size", String(params.page_size));
  if (params?.source_type) searchParams.set("source_type", params.source_type);
  if (params?.product_area) searchParams.set("product_area", params.product_area);
  if (params?.sentiment) searchParams.set("sentiment", params.sentiment);
  if (params?.sort_by) searchParams.set("sort_by", params.sort_by);
  if (params?.sort_order) searchParams.set("sort_order", params.sort_order);
  const qs = searchParams.toString();
  const url = qs ? `${PREFIX}?${qs}` : PREFIX;
  const { data } = await api.get<PaginatedResponse<Feedback>>(url);
  return data;
}

/** Get feedback count. */
export async function getFeedbackCount(): Promise<number> {
  const { data } = await api.get<ApiResponse<{ count: number }>>(`${PREFIX}/count`);
  return data.data.count;
}

/** Get single feedback. */
export async function getFeedback(id: string): Promise<Feedback> {
  const { data } = await api.get<ApiResponse<Feedback>>(`${PREFIX}/${id}`);
  return data.data;
}

/** Create feedback manually. */
export async function createFeedbackManual(body: {
  text: string;
  source?: string;
  product_area?: string;
  customer_id?: string;
  customer_name?: string;
  author_name?: string;
  author_email?: string;
  rating?: number;
  created_at?: string;
}): Promise<Feedback> {
  const { data } = await api.post<ApiResponse<Feedback>>(`${PREFIX}/manual`, body);
  return data.data;
}

/** Upload CSV (step 1). Returns upload_id, columns, suggested_mapping, total_rows. */
export async function uploadFeedbackCsv(file: File): Promise<FeedbackUploadInit> {
  const formData = new FormData();
  formData.append("file", file);
  const { data } = await api.post<ApiResponse<FeedbackUploadInit>>(
    `${PREFIX}/upload-csv`,
    formData,
    {
      headers: { "Content-Type": "multipart/form-data" },
    }
  );
  return data.data;
}

/** Confirm CSV mapping (step 2). */
export async function confirmFeedbackMapping(
  uploadId: string,
  body: FeedbackUploadConfirm
): Promise<{ upload_id: string; status: string }> {
  const { data } = await api.post<ApiResponse<{ upload_id: string; status: string }>>(
    `${PREFIX}/upload-csv/${uploadId}/confirm`,
    body
  );
  return data.data;
}

/** Get similar feedback items. */
export async function getSimilarFeedback(id: string): Promise<Feedback[]> {
  const { data } = await api.get<ApiResponse<Feedback[]>>(`${PREFIX}/${id}/similar`);
  return data.data;
}

/** Run import (step 3). */
export async function importFeedbackCsv(uploadId: string): Promise<FeedbackUploadImport> {
  const { data } = await api.post<ApiResponse<FeedbackUploadImport>>(
    `${PREFIX}/upload-csv/${uploadId}/import`
  );
  return data.data;
}
