/** Feedback item from API. */
export interface Feedback {
  id: string;
  org_id?: string;
  text: string;
  source?: string;
  sentiment?: string;
  sentiment_score?: number;
  rating?: number;
  product_area?: string;
  customer_id?: string;
  customer_name?: string;
  customer_segment?: string;
  author_name?: string;
  author_email?: string;
  tags?: string[];
  source_file?: string;
  ingestion_method?: string;
  created_at?: string;
  ingested_at?: string;
  metadata?: Record<string, unknown>;
}

/** Feedback source types for display (id, label, color). */
export const FEEDBACK_SOURCES: { id: string; label: string; color: string }[] = [
  { id: "app_store_review", label: "App Store Review", color: "blue" },
  { id: "g2_capterra", label: "G2 / Capterra", color: "indigo" },
  { id: "support_ticket", label: "Support Ticket", color: "orange" },
  { id: "nps_csat", label: "NPS / CSAT Survey", color: "green" },
  { id: "customer_email", label: "Customer Email", color: "teal" },
  { id: "sales_call_note", label: "Sales Call Note", color: "purple" },
  { id: "slack_message", label: "Slack Message", color: "pink" },
  { id: "internal_team_feedback", label: "Internal Team Feedback", color: "gray" },
  { id: "user_interview", label: "User Interview / Research", color: "cyan" },
  { id: "bug_report", label: "Bug Report (Jira/Linear)", color: "red" },
  { id: "community_forum", label: "Community Forum / Discord", color: "yellow" },
];

/** CSV upload init response. */
export interface FeedbackUploadInit {
  upload_id: string;
  columns: string[];
  suggested_mapping: Record<string, string | null>;
  total_rows: number;
  preview_sample?: Record<string, string>[];
}

/** CSV confirm request. */
export interface FeedbackUploadConfirm {
  column_mapping: Record<string, string | null>;
  default_source?: string;
  use_today_for_date?: boolean;
  auto_detect_areas?: boolean;
  auto_analyze_sentiment?: boolean;
}

/** Detected area from import. */
export interface DetectedArea {
  name: string;
  count: number;
  is_new: boolean;
}

/** CSV import result. */
export interface FeedbackUploadImport {
  upload_id: string;
  total_rows: number;
  imported_rows: number;
  failed_rows: number;
  detected_areas?: DetectedArea[];
}
