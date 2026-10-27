"use client";

import dynamic from "next/dynamic";
import { use } from "react";
import { toast } from "sonner";

import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useCamera } from "@/features/sources/hooks";
import { useCreateZone, useDeleteZone, useReferenceFrameUrl, useZones } from "@/features/zones/hooks";

const ZoneCanvas = dynamic(
  () => import("@/features/zones/components/zone-canvas").then((m) => m.ZoneCanvas),
  { ssr: false, loading: () => <Skeleton className="h-96 w-full" /> },
);

export default function ZoneEditorPage({
  params,
}: {
  params: Promise<{ cameraId: string }>;
}) {
  const { cameraId } = use(params);
  const { data: camera } = useCamera(cameraId);
  const { data: referenceFrame, isLoading: loadingFrame, isError: frameError } =
    useReferenceFrameUrl(cameraId);
  const { data: zones } = useZones(cameraId);
  const createZone = useCreateZone(cameraId);
  const deleteZone = useDeleteZone(cameraId);

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Zones — {camera?.name ?? "Camera"}</h1>

      {loadingFrame && <Skeleton className="h-96 w-full" />}

      {frameError && (
        <Card>
          <CardContent className="py-8 text-center text-muted-foreground">
            No reference frame yet. This camera needs to process at least one frame (upload a
            video, start live streaming, or start a screen share) before zones can be drawn.
          </CardContent>
        </Card>
      )}

      {referenceFrame && (
        <ZoneCanvas
          imageUrl={referenceFrame.url}
          zones={zones ?? []}
          onCreateZone={(name, points) =>
            createZone.mutate(
              { name, points },
              {
                onSuccess: () => toast.success(`Zone "${name}" saved`),
                onError: (error) =>
                  toast.error(error instanceof Error ? error.message : "Could not save zone"),
              },
            )
          }
          onDeleteZone={(zoneId) =>
            deleteZone.mutate(zoneId, {
              onSuccess: () => toast.success("Zone deleted"),
            })
          }
        />
      )}
    </div>
  );
}
