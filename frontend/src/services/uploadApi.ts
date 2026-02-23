import { api } from "./api";
import type { ApiResponse } from "../types/common";

const PREFIX = "/uploads";

export interface UploadRecord {
  id: string;
  org_id?: string;
  upload_type: string;
  filename?: string;
  total_rows?: number;
  imported_rows?: number;
  failed_rows?: number;
  status: string;
  column_mapping?: Record<string, unknown>;
  error_message?: string | null;
  created_at?: string;
  completed_at?: string;
}

/** List upload history. */
export async function getUploads(): Promise<UploadRecord[]> {
  const { data } = await api.get<ApiResponse<UploadRecord[]>>(PREFIX);
  return data.data;
}

/** Get single upload. */
export async function getUpload(id: string): Promise<UploadRecord> {
  const { data } = await api.get<ApiResponse<UploadRecord>>(`${PREFIX}/${id}`);
  return data.data;
}

/** Delete upload from history. */
export async function deleteUpload(id: string): Promise<void> {
  await api.delete(`${PREFIX}/${id}`);
}
