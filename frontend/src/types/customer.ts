/** Customer profile from API. */
export interface Customer {
  id: string;
  org_id?: string;
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
  created_at?: string;
  updated_at?: string;
  metadata?: Record<string, unknown>;
  /** From include_feedback_stats */
  feedback_count?: number;
  negative_feedback_count?: number;
}

/** CSV upload init response. */
export interface CustomerUploadInit {
  upload_id: string;
  columns: string[];
  suggested_mapping: Record<string, string | null>;
  total_rows: number;
  preview_sample?: Record<string, string>[];
}

/** CSV confirm request. */
export interface CustomerUploadConfirm {
  column_mapping: Record<string, string | null>;
}

/** CSV import result. */
export interface CustomerUploadImport {
  upload_id: string;
  total_rows: number;
  imported_rows: number;
  failed_rows: number;
}
