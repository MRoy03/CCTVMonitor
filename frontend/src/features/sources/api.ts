import { apiClient } from "@/lib/api/client";
import type { ActivityEvent, Camera, DetectionEvent, Location, VideoSession } from "./types";

export const sourcesApi = {
  listLocations: () => apiClient.get<Location[]>("/locations"),
  createLocation: (name: string) => apiClient.post<Location>("/locations", { name }),

  listCameras: () => apiClient.get<Camera[]>("/cameras"),
  getCamera: (cameraId: string) => apiClient.get<Camera>(`/cameras/${cameraId}`),
  createCamera: (payload: {
    location_id: string;
    name: string;
    source_type: Camera["source_type"];
    stream_url?: string;
  }) => apiClient.post<Camera>("/cameras", payload),

  listVideoSessions: (cameraId: string) =>
    apiClient.get<VideoSession[]>(`/cameras/${cameraId}/video-sessions`),

  uploadVideo: (cameraId: string, file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    return apiClient.upload<VideoSession>(`/cameras/${cameraId}/video-sessions`, formData);
  },

  getVideoSession: (sessionId: string) =>
    apiClient.get<VideoSession>(`/video-sessions/${sessionId}`),

  getVideoUrl: (sessionId: string) =>
    apiClient.get<{ url: string }>(`/video-sessions/${sessionId}/video-url`),

  listDetections: (sessionId: string) =>
    apiClient.get<DetectionEvent[]>(`/video-sessions/${sessionId}/detections`),

  listCameraDetections: (cameraId: string, limit = 50) =>
    apiClient.get<DetectionEvent[]>(`/cameras/${cameraId}/detections?limit=${limit}`),

  listActivityEvents: (cameraId: string, limit = 50) =>
    apiClient.get<ActivityEvent[]>(`/cameras/${cameraId}/activity-events?limit=${limit}`),

  postFrame: (cameraId: string, blob: Blob) => {
    const formData = new FormData();
    formData.append("file", blob, "frame.jpg");
    return apiClient.upload<{ ok: boolean }>(`/cameras/${cameraId}/frames`, formData);
  },
};
