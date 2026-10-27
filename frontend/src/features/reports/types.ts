export type ReportType = "DAILY" | "SHIFT" | "EXCEPTION" | "INCIDENT" | "SUMMARY";

export interface ReportSummary {
  id: string;
  camera_id: string;
  report_type: ReportType;
  period_start: string;
  period_end: string;
}

export interface ReportRow {
  timestamp: string;
  event: string;
  zone: string | null;
  severity: string;
  observation: string;
}

export interface ReportStructuredData {
  camera_name: string;
  period_start: string;
  period_end: string;
  detection_summary: Record<string, number>;
  rows: ReportRow[];
}

export interface Report extends ReportSummary {
  report_text: string;
  structured_data: ReportStructuredData;
}
