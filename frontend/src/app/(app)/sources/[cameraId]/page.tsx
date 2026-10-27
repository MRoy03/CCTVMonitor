"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { use, useMemo, useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { BoundingBoxOverlay } from "@/features/video/components/bounding-box-overlay";
import { VideoPlayer } from "@/features/video/components/video-player";
import { FeedbackControls } from "@/features/feedback/components/feedback-controls";
import { MissedEventDialog } from "@/features/feedback/components/missed-event-dialog";
import { useFeedbackStats } from "@/features/feedback/hooks";
import type { ActivityEvent, Camera, DetectionEvent } from "@/features/sources/types";
import {
  useActivityEvents,
  useCamera,
  useCameraDetections,
  useDetections,
  useVideoSession,
  useVideoSessions,
  useVideoUrl,
} from "@/features/sources/hooks";

const SEVERITY_VARIANT: Record<ActivityEvent["severity"], "outline" | "secondary" | "destructive"> = {
  INFO: "outline",
  WARNING: "secondary",
  CRITICAL: "destructive",
};

const STATUS_VARIANT: Record<string, "default" | "secondary" | "destructive" | "outline"> = {
  DONE: "default",
  PROCESSING: "secondary",
  QUEUED: "outline",
  FAILED: "destructive",
  ONLINE: "default",
  OFFLINE: "destructive",
  UNKNOWN: "outline",
};

export default function CameraDetailPage({
  params,
}: {
  params: Promise<{ cameraId: string }>;
}) {
  const { cameraId } = use(params);
  const { data: camera } = useCamera(cameraId);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <h1 className="text-2xl font-semibold">{camera?.name ?? "Camera"}</h1>
          {camera && <Badge variant={STATUS_VARIANT[camera.status]}>{camera.status}</Badge>}
        </div>
        <div className="flex gap-2">
          <MissedEventDialog cameraId={cameraId} />
          <Button variant="outline" size="sm" asChild>
            <Link href={`/zones/${cameraId}/editor`}>Zones</Link>
          </Button>
          <Button variant="outline" size="sm" asChild>
            <Link href={`/rules?camera_id=${cameraId}`}>Rules</Link>
          </Button>
        </div>
      </div>

      <FeedbackStatsBadge cameraId={cameraId} />
      <IncidentsCard cameraId={cameraId} />

      {camera?.source_type === "RTSP" || camera?.source_type === "SCREEN_CAPTURE" ? (
        <LiveCameraView cameraId={cameraId} camera={camera} />
      ) : (
        <UploadCameraView cameraId={cameraId} />
      )}
    </div>
  );
}

function FeedbackStatsBadge({ cameraId }: { cameraId: string }) {
  const { data: stats } = useFeedbackStats(cameraId);
  if (!stats || stats.accuracy === null) return null;

  return (
    <p className="text-sm text-muted-foreground">
      Feedback accuracy: {Math.round(stats.accuracy * 100)}% ({stats.correct} correct,{" "}
      {stats.incorrect} incorrect, {stats.missed_event} missed — {stats.total} total)
    </p>
  );
}

function IncidentsCard({ cameraId }: { cameraId: string }) {
  const { data: events } = useActivityEvents(cameraId, true);
  if (!events || events.length === 0) return null;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Incidents &amp; observations</CardTitle>
      </CardHeader>
      <CardContent className="space-y-2">
        {events.slice(0, 10).map((event) => (
          <div key={event.id} className="flex items-center justify-between text-sm">
            <div className="flex items-center gap-2">
              <Badge variant={SEVERITY_VARIANT[event.severity]}>{event.severity}</Badge>
              <span>{event.description}</span>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-muted-foreground">
                {new Date(event.start_time).toLocaleTimeString()}
              </span>
              <FeedbackControls cameraId={cameraId} activityEventId={event.id} />
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}

function LiveCameraView({ cameraId, camera }: { cameraId: string; camera: Camera }) {
  const isOnline = camera.status === "ONLINE";
  const { data: detections } = useCameraDetections(cameraId, true);

  const classCounts = useMemo(() => countByType(detections), [detections]);

  return (
    <div className="space-y-4">
      <Card>
        <CardContent className="space-y-1 py-4 text-sm text-muted-foreground">
          <p>
            {camera.source_type === "RTSP"
              ? "Live browser video preview for RTSP isn't built yet (it needs RTSP-to-HLS/WebRTC transcoding — a separate piece of work). "
              : "Live video preview is only visible in the browser tab actively sharing its screen. "}
            Detections below are real and update automatically every few seconds.
          </p>
          {camera.last_seen_at && (
            <p>Last frame seen: {new Date(camera.last_seen_at).toLocaleTimeString()}</p>
          )}
          {!isOnline && <p className="text-destructive">Camera is not currently reachable.</p>}
        </CardContent>
      </Card>

      <div className="grid gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="text-base">Recent detections</CardTitle>
          </CardHeader>
          <CardContent>
            {!detections || detections.length === 0 ? (
              <p className="text-sm text-muted-foreground">No detections yet.</p>
            ) : (
              <div className="space-y-1">
                {detections.slice(0, 15).map((d) => (
                  <div key={d.id} className="flex items-center justify-between text-sm">
                    <span className="capitalize">
                      {d.object_type} {d.track_id !== null ? `#${d.track_id}` : ""}
                    </span>
                    <div className="flex items-center gap-3">
                      <span className="text-muted-foreground">
                        {new Date(d.timestamp).toLocaleTimeString()}
                      </span>
                      <FeedbackControls cameraId={cameraId} detectionEventId={d.id} />
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Detection summary</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {Object.entries(classCounts).length === 0 && (
              <p className="text-sm text-muted-foreground">No objects detected.</p>
            )}
            {Object.entries(classCounts).map(([type, count]) => (
              <div key={type} className="flex items-center justify-between text-sm">
                <span className="capitalize">{type}</span>
                <Badge variant="secondary">{count}</Badge>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function UploadCameraView({ cameraId }: { cameraId: string }) {
  const searchParams = useSearchParams();
  const sessionFromUrl = searchParams.get("session");

  const { data: sessions } = useVideoSessions(cameraId);
  const sessionId = sessionFromUrl ?? sessions?.[0]?.id ?? null;

  const { data: session } = useVideoSession(sessionId);
  const isDone = session?.status === "DONE";
  const { data: videoUrlResponse } = useVideoUrl(sessionId, isDone);
  const { data: detections } = useDetections(sessionId, isDone);

  const [currentTime, setCurrentTime] = useState(0);
  const classCounts = useMemo(() => countByType(detections), [detections]);

  return (
    <>
      {!sessionId && (
        <Card>
          <CardContent className="py-8 text-center text-muted-foreground">
            No video sessions yet for this camera.
          </CardContent>
        </Card>
      )}

      {sessionId && !isDone && (
        <Card>
          <CardContent className="space-y-3 py-8 text-center text-muted-foreground">
            <p>
              {session?.status === "FAILED"
                ? `Processing failed: ${session.error_message}`
                : "Processing video — this page updates automatically."}
            </p>
            {session?.status !== "FAILED" && <Skeleton className="mx-auto h-48 w-full max-w-xl" />}
          </CardContent>
        </Card>
      )}

      {isDone && videoUrlResponse && (
        <div className="grid gap-6 lg:grid-cols-3">
          <div className="lg:col-span-2">
            <VideoPlayer
              src={videoUrlResponse.url}
              onTimeUpdate={setCurrentTime}
              overlay={
                <BoundingBoxOverlay
                  detections={(detections ?? []).filter(
                    (d) => Math.abs(secondsSinceStart(d.timestamp, session) - currentTime) < 1,
                  )}
                />
              }
            />
          </div>
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Detection summary</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {Object.entries(classCounts).length === 0 && (
                <p className="text-sm text-muted-foreground">No objects detected.</p>
              )}
              {Object.entries(classCounts).map(([type, count]) => (
                <div key={type} className="flex items-center justify-between text-sm">
                  <span className="capitalize">{type}</span>
                  <Badge variant="secondary">{count}</Badge>
                </div>
              ))}
            </CardContent>
          </Card>
        </div>
      )}
    </>
  );
}

function countByType(detections: DetectionEvent[] | undefined): Record<string, number> {
  if (!detections) return {};
  return detections.reduce<Record<string, number>>((acc, d) => {
    acc[d.object_type] = (acc[d.object_type] ?? 0) + 1;
    return acc;
  }, {});
}

function secondsSinceStart(
  timestamp: string,
  session: { start_time: string | null } | undefined,
): number {
  if (!session?.start_time) return 0;
  return (new Date(timestamp).getTime() - new Date(session.start_time).getTime()) / 1000;
}
