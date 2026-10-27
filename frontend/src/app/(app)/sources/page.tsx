"use client";

import Link from "next/link";
import { Plus, Video } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useCameras } from "@/features/sources/hooks";

const STATUS_VARIANT: Record<string, "default" | "secondary" | "destructive" | "outline"> = {
  ONLINE: "default",
  PROCESSING: "secondary",
  OFFLINE: "destructive",
  UNKNOWN: "outline",
};

export default function SourcesPage() {
  const { data: cameras, isLoading } = useCameras();

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Sources</h1>
        <Button asChild>
          <Link href="/sources/new/upload">
            <Plus className="mr-2 h-4 w-4" /> Add source
          </Link>
        </Button>
      </div>

      {isLoading && (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} className="h-32" />
          ))}
        </div>
      )}

      {!isLoading && cameras?.length === 0 && (
        <Card>
          <CardContent className="flex flex-col items-center gap-3 py-12 text-center text-muted-foreground">
            <Video className="h-8 w-8" />
            <p>No cameras yet. Upload a recording to get started.</p>
            <Button asChild>
              <Link href="/sources/new/upload">Upload a video</Link>
            </Button>
          </CardContent>
        </Card>
      )}

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {cameras?.map((camera) => (
          <Link key={camera.id} href={`/sources/${camera.id}`}>
            <Card className="h-full transition-colors hover:bg-muted/50">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="text-base">{camera.name}</CardTitle>
                  <Badge variant={STATUS_VARIANT[camera.status]}>{camera.status}</Badge>
                </div>
                <CardDescription>{camera.source_type}</CardDescription>
              </CardHeader>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  );
}
