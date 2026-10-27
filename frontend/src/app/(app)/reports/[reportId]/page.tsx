"use client";

import { use } from "react";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useReport } from "@/features/reports/hooks";

export default function ReportDetailPage({
  params,
}: {
  params: Promise<{ reportId: string }>;
}) {
  const { reportId } = use(params);
  const { data: report, isLoading } = useReport(reportId);

  if (isLoading || !report) {
    return <Skeleton className="h-96 w-full" />;
  }

  const { structured_data } = report;

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div className="flex items-center gap-3">
        <h1 className="text-2xl font-semibold">{structured_data.camera_name}</h1>
        <Badge variant="outline">{report.report_type}</Badge>
      </div>
      <p className="text-sm text-muted-foreground">
        {new Date(structured_data.period_start).toLocaleString()} —{" "}
        {new Date(structured_data.period_end).toLocaleString()}
      </p>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Summary</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="whitespace-pre-wrap text-sm">{report.report_text}</p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Objects seen</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-wrap gap-2">
          {Object.entries(structured_data.detection_summary).length === 0 && (
            <p className="text-sm text-muted-foreground">No objects detected in this period.</p>
          )}
          {Object.entries(structured_data.detection_summary).map(([type, count]) => (
            <Badge key={type} variant="secondary" className="capitalize">
              {type}: {count}
            </Badge>
          ))}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Incidents &amp; observations</CardTitle>
        </CardHeader>
        <CardContent>
          {structured_data.rows.length === 0 ? (
            <p className="text-sm text-muted-foreground">None in this period.</p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Time</TableHead>
                  <TableHead>Event</TableHead>
                  <TableHead>Zone</TableHead>
                  <TableHead>Severity</TableHead>
                  <TableHead>Observation</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {structured_data.rows.map((row, i) => (
                  <TableRow key={i}>
                    <TableCell>{new Date(row.timestamp).toLocaleTimeString()}</TableCell>
                    <TableCell className="capitalize">{row.event}</TableCell>
                    <TableCell>{row.zone ?? "—"}</TableCell>
                    <TableCell>{row.severity}</TableCell>
                    <TableCell>{row.observation}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
