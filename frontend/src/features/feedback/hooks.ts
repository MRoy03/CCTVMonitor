import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { feedbackApi } from "./api";
import type { FeedbackVerdict } from "./types";

export const useFeedbackStats = (cameraId: string) =>
  useQuery({
    queryKey: ["cameras", cameraId, "feedback-stats"],
    queryFn: () => feedbackApi.stats(cameraId),
    enabled: !!cameraId,
  });

export const useSubmitFeedback = (cameraId: string) => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: {
      detection_event_id?: string;
      activity_event_id?: string;
      verdict: FeedbackVerdict;
      notes?: string;
    }) => feedbackApi.create({ camera_id: cameraId, ...payload }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["cameras", cameraId, "feedback-stats"] });
    },
  });
};
