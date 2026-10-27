import { apiClient } from "@/lib/api/client";
import type { Report, ReportSummary, ReportType } from "./types";

export const reportsApi = {
  list: (cameraId: string) => apiClient.get<ReportSummary[]>(`/cameras/${cameraId}/reports`),
  get: (reportId: string) => apiClient.get<Report>(`/reports/${reportId}`),
  create: (
    cameraId: string,
    payload: { report_type: ReportType; period_start: string; period_end: string },
  ) => apiClient.post<Report>(`/cameras/${cameraId}/reports`, payload),
};
