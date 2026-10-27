"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { sourcesApi } from "@/features/sources/api";
import { useLocations } from "@/features/sources/hooks";

export default function LiveSourcePage() {
  const router = useRouter();
  const { data: locations, isLoading: loadingLocations } = useLocations();
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(formData: FormData) {
    const name = String(formData.get("name"));
    const streamUrl = String(formData.get("stream_url"));
    if (!streamUrl.startsWith("rtsp://")) {
      toast.error("Stream URL must start with rtsp://");
      return;
    }

    setSubmitting(true);
    try {
      let locationId = locations?.[0]?.id;
      if (!locationId) {
        const location = await sourcesApi.createLocation("Default Location");
        locationId = location.id;
      }

      const camera = await sourcesApi.createCamera({
        location_id: locationId,
        name,
        source_type: "RTSP",
        stream_url: streamUrl,
      });

      toast.success("Camera added — connecting…");
      router.push(`/sources/${camera.id}`);
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Could not add camera");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="mx-auto max-w-lg space-y-6">
      <h1 className="text-2xl font-semibold">Add a live camera</h1>
      <Card>
        <CardHeader>
          <CardTitle>RTSP camera</CardTitle>
          <CardDescription>
            Enter the camera&apos;s RTSP stream URL (e.g. rtsp://192.168.1.50:554/stream). It can
            take a few seconds to connect after adding.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form action={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="name">Camera name</Label>
              <Input id="name" name="name" placeholder="e.g. Main Gate" required />
            </div>
            <div className="space-y-2">
              <Label htmlFor="stream_url">RTSP URL</Label>
              <Input
                id="stream_url"
                name="stream_url"
                placeholder="rtsp://..."
                required
              />
            </div>
            <Button type="submit" className="w-full" disabled={submitting || loadingLocations}>
              {submitting ? "Adding…" : "Add camera"}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
