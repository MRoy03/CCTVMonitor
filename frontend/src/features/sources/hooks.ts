import { useQuery } from "@tanstack/react-query";

import { sourcesApi } from "./api";

export const useLocations = () =>
  useQuery({ queryKey: ["locations"], queryFn: sourcesApi.listLocations });

export const useCameras = () =>
  useQuery({ queryKey: ["cameras"], queryFn: sourcesApi.listCameras });

export const useCamera = (cameraId: string) =>
  useQuery({
    queryKey: ["cameras", cameraId],
    queryFn: () => sourcesApi.getCamera(cameraId),
    enabled: !!cameraId,
    refetchInterval: 5000, // keep RTSP camera status/last_seen_at fresh
  });

export const useVideoSession = (sessionId: string | null) =>
  useQuery({
    queryKey: ["video-sessions", sessionId],
    queryFn: () => sourcesApi.getVideoSession(sessionId as string),
    enabled: !!sessionId,
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      return status === "DONE" || status === "FAILED" ? false : 2000;
    },
  });

export const useVideoSessions = (cameraId: string) =>
  useQuery({
    queryKey: ["cameras", cameraId, "video-sessions"],
    queryFn: () => sourcesApi.listVideoSessions(cameraId),
    enabled: !!cameraId,
  });

export const useDetections = (sessionId: string | null, enabled: boolean) =>
  useQuery({
    queryKey: ["video-sessions", sessionId, "detections"],
    queryFn: () => sourcesApi.listDetections(sessionId as string),
    enabled: !!sessionId && enabled,
  });

export const useVideoUrl = (sessionId: string | null, enabled: boolean) =>
  useQuery({
    queryKey: ["video-sessions", sessionId, "video-url"],
    queryFn: () => sourcesApi.getVideoUrl(sessionId as string),
    enabled: !!sessionId && enabled,
  });

export const useCameraDetections = (cameraId: string, enabled: boolean) =>
  useQuery({
    queryKey: ["cameras", cameraId, "detections"],
    queryFn: () => sourcesApi.listCameraDetections(cameraId),
    enabled: !!cameraId && enabled,
    refetchInterval: 3000,
  });

export const useActivityEvents = (cameraId: string, enabled: boolean) =>
  useQuery({
    queryKey: ["cameras", cameraId, "activity-events"],
    queryFn: () => sourcesApi.listActivityEvents(cameraId),
    enabled: !!cameraId && enabled,
    refetchInterval: 5000,
  });
