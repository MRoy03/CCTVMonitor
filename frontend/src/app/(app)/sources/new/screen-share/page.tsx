"use client";

import { useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { sourcesApi } from "@/features/sources/api";
import { useLocations } from "@/features/sources/hooks";

const FRAME_INTERVAL_MS = 2000;

type CaptureState = "idle" | "previewing" | "capturing" | "stopped";

export default function ScreenShareSourcePage() {
  const router = useRouter();
  const { data: locations } = useLocations();

  const [name, setName] = useState("");
  const [state, setState] = useState<CaptureState>("idle");
  const [cameraId, setCameraId] = useState<string | null>(null);

  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    return () => stopEverything();
     
  }, []);

  function stopEverything() {
    if (intervalRef.current) clearInterval(intervalRef.current);
    streamRef.current?.getTracks().forEach((track) => track.stop());
    streamRef.current = null;
  }

  async function handleStartPreview() {
    if (!name.trim()) {
      toast.error("Name this source first");
      return;
    }
    try {
      const stream = await navigator.mediaDevices.getDisplayMedia({
        video: { frameRate: { ideal: 2 } },
        audio: false,
      });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
      stream.getVideoTracks()[0].addEventListener("ended", () => {
        toast.info("Screen sharing stopped");
        setState("stopped");
        stopEverything();
      });
      setState("previewing");
    } catch {
      toast.error("Screen share permission was denied or cancelled");
    }
  }

  async function handleConfirm() {
    try {
      let locationId = locations?.[0]?.id;
      if (!locationId) {
        const location = await sourcesApi.createLocation("Default Location");
        locationId = location.id;
      }

      const camera = await sourcesApi.createCamera({
        location_id: locationId,
        name,
        source_type: "SCREEN_CAPTURE",
      });
      setCameraId(camera.id);
      setState("capturing");

      intervalRef.current = setInterval(captureAndSendFrame(camera.id), FRAME_INTERVAL_MS);
      toast.success("Capture started — analyzing this screen");
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Could not start capture");
    }
  }

  function captureAndSendFrame(id: string) {
    return () => {
      const video = videoRef.current;
      const canvas = canvasRef.current;
      if (!video || !canvas || video.videoWidth === 0) return;

      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      const ctx = canvas.getContext("2d");
      ctx?.drawImage(video, 0, 0, canvas.width, canvas.height);
      canvas.toBlob(
        (blob) => {
          if (blob) sourcesApi.postFrame(id, blob).catch(() => {});
        },
        "image/jpeg",
        0.8,
      );
    };
  }

  function handleStop() {
    stopEverything();
    setState("stopped");
    if (cameraId) router.push(`/sources/${cameraId}`);
  }

  return (
    <div className="mx-auto max-w-lg space-y-6">
      <h1 className="text-2xl font-semibold">Monitor a screen share</h1>
      <Card>
        <CardHeader>
          <CardTitle>Screen / window capture</CardTitle>
          <CardDescription>
            Open your DVR/NVR viewer or any application in another window, then start capture and
            select that window. Frames are sent for analysis every {FRAME_INTERVAL_MS / 1000}{" "}
            seconds for as long as this tab stays open and sharing.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="name">Camera name</Label>
            <Input
              id="name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. Front Gate DVR"
              disabled={state !== "idle"}
            />
          </div>

          <video
            ref={videoRef}
            autoPlay
            muted
            className="w-full rounded-md border bg-muted"
            style={{ display: state === "idle" ? "none" : "block" }}
          />
          <canvas ref={canvasRef} className="hidden" />

          {state === "idle" && (
            <Button className="w-full" onClick={handleStartPreview}>
              Start capture
            </Button>
          )}
          {state === "previewing" && (
            <div className="flex gap-2">
              <Button className="flex-1" onClick={handleConfirm}>
                This is correct — analyze it
              </Button>
              <Button variant="outline" onClick={handleStop}>
                Cancel
              </Button>
            </div>
          )}
          {state === "capturing" && (
            <Button variant="destructive" className="w-full" onClick={handleStop}>
              Stop capture
            </Button>
          )}
          {state === "stopped" && (
            <p className="text-center text-sm text-muted-foreground">Capture stopped.</p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
