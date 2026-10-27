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

const ACCEPTED = ".mp4,.avi,.mov,.mkv,.webm";

export default function UploadSourcePage() {
  const router = useRouter();
  const { data: locations, isLoading: loadingLocations } = useLocations();
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(formData: FormData) {
    const name = String(formData.get("name"));
    const file = formData.get("file") as File;
    if (!file || file.size === 0) {
      toast.error("Choose a video file to upload");
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
        source_type: "UPLOAD",
      });

      const session = await sourcesApi.uploadVideo(camera.id, file);
      toast.success("Upload started — processing in the background");
      router.push(`/sources/${camera.id}?session=${session.id}`);
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Upload failed");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="mx-auto max-w-lg space-y-6">
      <h1 className="text-2xl font-semibold">Upload a recording</h1>
      <Card>
        <CardHeader>
          <CardTitle>Video upload</CardTitle>
          <CardDescription>
            Supported formats: MP4, AVI, MOV, MKV, WEBM. The video is analyzed in the background
            — detections will appear once processing finishes.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form action={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="name">Camera name</Label>
              <Input id="name" name="name" placeholder="e.g. Main Gate" required />
            </div>
            <div className="space-y-2">
              <Label htmlFor="file">Video file</Label>
              <Input id="file" name="file" type="file" accept={ACCEPTED} required />
            </div>
            <Button type="submit" className="w-full" disabled={submitting || loadingLocations}>
              {submitting ? "Uploading…" : "Upload and analyze"}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
