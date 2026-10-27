import Link from "next/link";
import { MonitorUp, Upload, Video } from "lucide-react";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

const MODES = [
  {
    href: "/sources/new/upload",
    icon: Upload,
    title: "Upload a recording",
    description: "MP4, AVI, MOV, MKV, WEBM",
    enabled: true,
  },
  {
    href: "/sources/new/live",
    icon: Video,
    title: "Live camera",
    description: "RTSP stream URL",
    enabled: true,
  },
  {
    href: "/sources/new/screen-share",
    icon: MonitorUp,
    title: "Screen share",
    description: "Monitor a DVR/NVR viewer or any window",
    enabled: true,
  },
];

export default function NewSourcePage() {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Add a source</h1>
      <div className="grid gap-4 md:grid-cols-3">
        {MODES.map((mode) => {
          const Icon = mode.icon;
          const card = (
            <Card className={mode.enabled ? "h-full transition-colors hover:bg-muted/50" : "h-full opacity-50"}>
              <CardHeader>
                <Icon className="mb-2 h-6 w-6" />
                <CardTitle className="text-base">{mode.title}</CardTitle>
                <CardDescription>{mode.description}</CardDescription>
              </CardHeader>
              <CardContent />
            </Card>
          );
          return mode.enabled ? (
            <Link key={mode.title} href={mode.href}>
              {card}
            </Link>
          ) : (
            <div key={mode.title}>{card}</div>
          );
        })}
      </div>
    </div>
  );
}
