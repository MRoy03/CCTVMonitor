import { apiClient } from "@/lib/api/client";
import type { Rule, RuleFormValues } from "./types";
import { toApiPayload } from "./serializer";

export const rulesApi = {
  list: (cameraId?: string) =>
    apiClient.get<Rule[]>(cameraId ? `/rules?camera_id=${cameraId}` : "/rules"),
  get: (ruleId: string) => apiClient.get<Rule>(`/rules/${ruleId}`),
  create: (values: RuleFormValues) => apiClient.post<Rule>("/rules", toApiPayload(values)),
  update: (ruleId: string, values: Partial<RuleFormValues> & { enabled?: boolean }) =>
    apiClient.patch<Rule>(`/rules/${ruleId}`, values),
  setEnabled: (ruleId: string, enabled: boolean) =>
    apiClient.patch<Rule>(`/rules/${ruleId}`, { enabled }),
  remove: (ruleId: string) => apiClient.delete<void>(`/rules/${ruleId}`),
};
