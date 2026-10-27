"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useCameras } from "@/features/sources/hooks";

function Widget({
  title,
  value,
  loading,
}: {
  title: string;
  value: React.ReactNode;
  loading?: boolean;
}) {
  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        {loading ? <Skeleton className="h-8 w-16" /> : <div className="text-3xl font-semibold">{value}</div>}
      </CardContent>
    </Card>
  );
}

export default function DashboardPage() {
  const { data: cameras, isLoading } = useCameras();
  const activeCount = cameras?.filter((c) => c.status !== "OFFLINE").length ?? 0;
  const offlineCount = cameras?.filter((c) => c.status === "OFFLINE").length ?? 0;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Dashboard</h1>
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-3">
        <Widget title="Active Cameras" value={activeCount} loading={isLoading} />
        <Widget title="Offline Cameras" value={offlineCount} loading={isLoading} />
        <Widget title="Incidents Today" value="—" />
        <Widget title="Open Alerts" value="—" />
        <Widget title="Recent Events" value="—" />
        <Widget title="AI Summary" value="Coming in Phase 5" />
      </div>
      <p className="text-sm text-muted-foreground">
        Incidents, alerts, and AI summaries come online as the Rule Engine (Phase 4), Alerts
        (Phase 8), and Reports (Phase 5) are built.
      </p>
    </div>
  );
}
