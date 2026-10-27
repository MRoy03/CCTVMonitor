import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { zonesApi } from "./api";

export const useZones = (cameraId: string) =>
  useQuery({
    queryKey: ["cameras", cameraId, "zones"],
    queryFn: () => zonesApi.list(cameraId),
    enabled: !!cameraId,
  });

export const useReferenceFrameUrl = (cameraId: string) =>
  useQuery({
    queryKey: ["cameras", cameraId, "reference-frame-url"],
    queryFn: () => zonesApi.getReferenceFrameUrl(cameraId),
    enabled: !!cameraId,
    retry: false,
  });

export const useCreateZone = (cameraId: string) => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ name, points }: { name: string; points: [number, number][] }) =>
      zonesApi.create(cameraId, name, points),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["cameras", cameraId, "zones"] });
    },
  });
};

export const useDeleteZone = (cameraId: string) => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (zoneId: string) => zonesApi.remove(zoneId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["cameras", cameraId, "zones"] });
    },
  });
};
