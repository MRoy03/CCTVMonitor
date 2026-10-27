import { apiClient } from "@/lib/api/client";
import type { Feedback, FeedbackStats, FeedbackVerdict } from "./types";

export const feedbackApi = {
  create: (payload: {
    camera_id: string;
    detection_event_id?: string;
    activity_event_id?: string;
    verdict: FeedbackVerdict;
    notes?: string;
  }) => apiClient.post<Feedback>("/feedback", payload),
  list: (cameraId: string) => apiClient.get<Feedback[]>(`/cameras/${cameraId}/feedback`),
  stats: (cameraId: string) => apiClient.get<FeedbackStats>(`/cameras/${cameraId}/feedback/stats`),
};
