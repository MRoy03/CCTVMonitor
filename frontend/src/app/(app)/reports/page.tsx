"use client";

import Link from "next/link";
import { useState } from "react";
import { toast } from "sonner";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useCameras } from "@/features/sources/hooks";
import { useCreateReport, useReports } from "@/features/reports/hooks";
import type { ReportType } from "@/features/reports/types";

const REPORT_TYPES: ReportType[] = ["DAILY", "SHIFT", "EXCEPTION", "INCIDENT", "SUMMARY"];

export default function ReportsPage() {
  const { data: cameras } = useCameras();
  const [cameraId, setCameraId] = useState<string>("");
  const [reportType, setReportType] = useState<ReportType>("SUMMARY");

  const { data: reports, isLoading } = useReports(cameraId);
  const createReport = useCreateReport(cameraId);

  function handleGenerate() {
    const periodEnd = new Date();
    const periodStart = new Date(periodEnd.getTime() - 24 * 60 * 60 * 1000); // last 24h
    createReport.mutate(
      {
        report_type: reportType,
        period_start: periodStart.toISOString(),
        period_end: periodEnd.toISOString(),
      },
      {
        onSuccess: () => toast.success("Report generated"),
        onError: (error) =>
          toast.error(error instanceof Error ? error.message : "Could not generate report"),
      },
    );
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Reports</h1>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Generate a report</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-wrap items-end gap-4">
          <div className="space-y-2">
            <label className="text-sm font-medium">Camera</label>
            <Select value={cameraId} onValueChange={setCameraId}>
              <SelectTrigger className="w-56">
                <SelectValue placeholder="Choose a camera" />
              </SelectTrigger>
              <SelectContent>
                {cameras?.map((camera) => (
                  <SelectItem key={camera.id} value={camera.id}>
                    {camera.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium">Type</label>
            <Select value={reportType} onValueChange={(v) => setReportType(v as ReportType)}>
              <SelectTrigger className="w-40">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {REPORT_TYPES.map((type) => (
                  <SelectItem key={type} value={type}>
                    {type}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <Button disabled={!cameraId || createReport.isPending} onClick={handleGenerate}>
            {createReport.isPending ? "Generating…" : "Generate (last 24h)"}
          </Button>
        </CardContent>
      </Card>

      {cameraId && (
        <div className="space-y-3">
          {!isLoading && reports?.length === 0 && (
            <Card>
              <CardContent className="py-8 text-center text-muted-foreground">
                No reports yet for this camera.
              </CardContent>
            </Card>
          )}
          {reports?.map((report) => (
            <Link key={report.id} href={`/reports/${report.id}`}>
              <Card className="transition-colors hover:bg-muted/50">
                <CardContent className="flex items-center justify-between py-4">
                  <div className="flex items-center gap-2">
                    <Badge variant="outline">{report.report_type}</Badge>
                    <span className="text-sm text-muted-foreground">
                      {new Date(report.period_start).toLocaleString()} —{" "}
                      {new Date(report.period_end).toLocaleString()}
                    </span>
                  </div>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
