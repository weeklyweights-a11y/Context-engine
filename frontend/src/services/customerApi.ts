import { api } from "./api";
import type { ApiResponse, PaginatedResponse } from "../types/common";
import type {
  Customer,
  CustomerUploadInit,
  CustomerUploadConfirm,
  CustomerUploadImport,
} from "../types/customer";

const PREFIX = "/customers";

/** List customers with pagination and filters. */
export async function getCustomersList(params?: {
  page?: number;
  page_size?: number;
  search?: string;
  segment?: string;
  health_min?: number;
  health_max?: number;
  renewal_within?: number;
  arr_min?: number;
  arr_max?: number;
  has_negative_feedback?: boolean;
  include_feedback_stats?: boolean;
  sort_by?: string;
  sort_order?: string;
}): Promise<{ data: Customer[]; pagination: { page: number; page_size: number; total: number } }> {
  const searchParams = new URLSearchParams();
  if (params?.page) searchParams.set("page", String(params.page));
  if (params?.page_size) searchParams.set("page_size", String(params.page_size));
  if (params?.search) searchParams.set("search", params.search);
  if (params?.segment) searchParams.set("segment", params.segment);
  if (params?.health_min != null) searchParams.set("health_min", String(params.health_min));
  if (params?.health_max != null) searchParams.set("health_max", String(params.health_max));
  if (params?.renewal_within != null) searchParams.set("renewal_within", String(params.renewal_within));
  if (params?.arr_min != null) searchParams.set("arr_min", String(params.arr_min));
  if (params?.arr_max != null) searchParams.set("arr_max", String(params.arr_max));
  if (params?.has_negative_feedback != null) searchParams.set("has_negative_feedback", String(params.has_negative_feedback));
  if (params?.include_feedback_stats) searchParams.set("include_feedback_stats", "true");
  if (params?.sort_by) searchParams.set("sort_by", params.sort_by);
  if (params?.sort_order) searchParams.set("sort_order", params.sort_order);
  const qs = searchParams.toString();
  const url = qs ? `${PREFIX}?${qs}` : PREFIX;
  const { data } = await api.get<PaginatedResponse<Customer>>(url);
  return data;
}

/** Search customers for autocomplete. */
export async function searchCustomers(q: string): Promise<{ id: string; company_name: string; segment?: string }[]> {
  if (!q?.trim()) return [];
  const { data } = await api.get<ApiResponse<{ id: string; company_name: string; segment?: string }[]>>(
    `${PREFIX}/search?q=${encodeURIComponent(q.trim())}`
  );
  return data.data;
}

/** Get customer feedback with pagination. */
export async function getCustomerFeedback(
  id: string,
  params?: { page?: number; page_size?: number }
): Promise<{ data: import("../types/feedback").Feedback[]; pagination: { page: number; page_size: number; total: number } }> {
  const searchParams = new URLSearchParams();
  if (params?.page) searchParams.set("page", String(params.page));
  if (params?.page_size) searchParams.set("page_size", String(params.page_size));
  const qs = searchParams.toString();
  const url = qs ? `${PREFIX}/${id}/feedback?${qs}` : `${PREFIX}/${id}/feedback`;
  const { data } = await api.get(url);
  return data;
}

/** Get customer sentiment trend. */
export async function getCustomerSentimentTrend(id: string): Promise<{
  periods: { date: string; avg_sentiment: number; count: number }[];
  product_average: { date: string; avg_sentiment: number }[];
}> {
  const { data } = await api.get<ApiResponse<{
    periods: { date: string; avg_sentiment: number; count: number }[];
    product_average: { date: string; avg_sentiment: number }[];
  }>>(`${PREFIX}/${id}/sentiment-trend`);
  return data.data;
}

/** Get customer count. */
export async function getCustomerCount(): Promise<number> {
  const { data } = await api.get<ApiResponse<{ count: number }>>(`${PREFIX}/count`);
  return data.data.count;
}

/** Get single customer. */
export async function getCustomer(id: string): Promise<Customer> {
  const { data } = await api.get<ApiResponse<Customer>>(`${PREFIX}/${id}`);
  return data.data;
}

/** Create customer manually. */
export async function createCustomerManual(body: {
  company_name: string;
  customer_id_external?: string;
  segment?: string;
  plan?: string;
  mrr?: number;
  arr?: number;
  account_manager?: string;
  renewal_date?: string;
  health_score?: number;
  industry?: string;
  employee_count?: number;
}): Promise<Customer> {
  const { data } = await api.post<ApiResponse<Customer>>(`${PREFIX}/manual`, body);
  return data.data;
}

/** Upload CSV (step 1). */
export async function uploadCustomersCsv(file: File): Promise<CustomerUploadInit> {
  const formData = new FormData();
  formData.append("file", file);
  const { data } = await api.post<ApiResponse<CustomerUploadInit>>(
    `${PREFIX}/upload-csv`,
    formData,
    {
      headers: { "Content-Type": "multipart/form-data" },
    }
  );
  return data.data;
}

/** Confirm CSV mapping (step 2). */
export async function confirmCustomerMapping(
  uploadId: string,
  body: CustomerUploadConfirm
): Promise<{ upload_id: string; status: string }> {
  const { data } = await api.post<ApiResponse<{ upload_id: string; status: string }>>(
    `${PREFIX}/upload-csv/${uploadId}/confirm`,
    body
  );
  return data.data;
}

/** Run import (step 3). */
export async function importCustomersCsv(uploadId: string): Promise<CustomerUploadImport> {
  const { data } = await api.post<ApiResponse<CustomerUploadImport>>(
    `${PREFIX}/upload-csv/${uploadId}/import`
  );
  return data.data;
}
