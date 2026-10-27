import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { rulesApi } from "./api";
import type { RuleFormValues } from "./types";

export const useRules = (cameraId?: string) =>
  useQuery({
    queryKey: ["rules", cameraId ?? "all"],
    queryFn: () => rulesApi.list(cameraId),
  });

export const useCreateRule = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (values: RuleFormValues) => rulesApi.create(values),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["rules"] }),
  });
};

export const useSetRuleEnabled = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ ruleId, enabled }: { ruleId: string; enabled: boolean }) =>
      rulesApi.setEnabled(ruleId, enabled),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["rules"] }),
  });
};

export const useDeleteRule = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (ruleId: string) => rulesApi.remove(ruleId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["rules"] }),
  });
};
