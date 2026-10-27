import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { reportsApi } from "./api";
import type { ReportType } from "./types";

export const useReports = (cameraId: string) =>
  useQuery({
    queryKey: ["cameras", cameraId, "reports"],
    queryFn: () => reportsApi.list(cameraId),
    enabled: !!cameraId,
  });

export const useReport = (reportId: string) =>
  useQuery({
    queryKey: ["reports", reportId],
    queryFn: () => reportsApi.get(reportId),
    enabled: !!reportId,
  });

export const useCreateReport = (cameraId: string) => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: { report_type: ReportType; period_start: string; period_end: string }) =>
      reportsApi.create(cameraId, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["cameras", cameraId, "reports"] });
    },
  });
};
