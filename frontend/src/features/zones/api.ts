import { apiClient } from "@/lib/api/client";
import type { Zone } from "./types";

export const zonesApi = {
  list: (cameraId: string) => apiClient.get<Zone[]>(`/cameras/${cameraId}/zones`),
  create: (cameraId: string, name: string, polygon_coordinates: [number, number][]) =>
    apiClient.post<Zone>(`/cameras/${cameraId}/zones`, { name, polygon_coordinates }),
  remove: (zoneId: string) => apiClient.delete<void>(`/zones/${zoneId}`),
  getReferenceFrameUrl: (cameraId: string) =>
    apiClient.get<{ url: string }>(`/cameras/${cameraId}/reference-frame-url`),
};
