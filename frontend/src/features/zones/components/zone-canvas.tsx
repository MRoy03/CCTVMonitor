"use client";

import { Fragment, useEffect, useRef, useState } from "react";
import { Circle, Image as KonvaImage, Layer, Line, Stage, Text } from "react-konva";
import useImage from "use-image";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import type { Zone } from "@/features/zones/types";

const ZONE_COLORS = ["#f87171", "#60a5fa", "#34d399", "#fbbf24", "#a78bfa", "#f472b6"];

function colorFor(index: number) {
  return ZONE_COLORS[index % ZONE_COLORS.length];
}

export function ZoneCanvas({
  imageUrl,
  zones,
  onCreateZone,
  onDeleteZone,
}: {
  imageUrl: string;
  zones: Zone[];
  onCreateZone: (name: string, points: [number, number][]) => void;
  onDeleteZone: (zoneId: string) => void;
}) {
  const [image] = useImage(imageUrl, "anonymous");
  const containerRef = useRef<HTMLDivElement>(null);
  const [stageWidth, setStageWidth] = useState(640);

  const [isDrawing, setIsDrawing] = useState(false);
  const [drawingPoints, setDrawingPoints] = useState<[number, number][]>([]);
  const [pendingPoints, setPendingPoints] = useState<[number, number][] | null>(null);
  const [zoneName, setZoneName] = useState("");
  const [selectedZoneId, setSelectedZoneId] = useState<string | null>(null);

  useEffect(() => {
    function updateWidth() {
      if (containerRef.current) setStageWidth(containerRef.current.offsetWidth);
    }
    updateWidth();
    window.addEventListener("resize", updateWidth);
    return () => window.removeEventListener("resize", updateWidth);
  }, []);

  const aspectRatio = image ? image.height / image.width : 0.75;
  const stageHeight = stageWidth * aspectRatio;

  function toNormalized(x: number, y: number): [number, number] {
    return [x / stageWidth, y / stageHeight];
  }
  function toPixels([x, y]: [number, number]): [number, number] {
    return [x * stageWidth, y * stageHeight];
  }

  function handleStageClick(e: { target: { getStage: () => unknown } }) {
    const stage = e.target.getStage() as { getPointerPosition: () => { x: number; y: number } | null } | null;
    const pos = stage?.getPointerPosition();
    if (!pos) return;
    setDrawingPoints((prev) => [...prev, toNormalized(pos.x, pos.y)]);
  }

  function startDrawing() {
    setIsDrawing(true);
    setDrawingPoints([]);
  }

  function finishDrawing() {
    if (drawingPoints.length < 3) return;
    setPendingPoints(drawingPoints);
    setDrawingPoints([]);
    setIsDrawing(false);
  }

  function cancelDrawing() {
    setDrawingPoints([]);
    setIsDrawing(false);
  }

  function confirmZone() {
    if (!pendingPoints || !zoneName.trim()) return;
    onCreateZone(zoneName.trim(), pendingPoints);
    setPendingPoints(null);
    setZoneName("");
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <p className="text-sm text-muted-foreground">
          {isDrawing
            ? `Click to add points (${drawingPoints.length} so far). Finish with at least 3.`
            : "Click “Draw zone”, then click points on the image to outline an area."}
        </p>
        <div className="flex gap-2">
          {isDrawing ? (
            <>
              <Button size="sm" variant="outline" onClick={cancelDrawing}>
                Cancel
              </Button>
              <Button size="sm" onClick={finishDrawing} disabled={drawingPoints.length < 3}>
                Finish shape
              </Button>
            </>
          ) : (
            <Button size="sm" onClick={startDrawing}>
              Draw zone
            </Button>
          )}
        </div>
      </div>

      <div ref={containerRef} className="w-full overflow-hidden rounded-md border">
        <Stage
          width={stageWidth}
          height={stageHeight || 360}
          onClick={isDrawing ? handleStageClick : undefined}
          style={{ cursor: isDrawing ? "crosshair" : "default" }}
        >
          <Layer>
            {image && <KonvaImage image={image} width={stageWidth} height={stageHeight} />}

            {zones.map((zone, index) => {
              const points = zone.polygon_coordinates.flatMap((p) => toPixels(p));
              const color = colorFor(index);
              const [labelX, labelY] = toPixels(zone.polygon_coordinates[0]);
              return (
                <Fragment key={zone.id}>
                  <Line
                    points={points}
                    closed
                    stroke={color}
                    strokeWidth={selectedZoneId === zone.id ? 3 : 2}
                    fill={`${color}33`}
                    onClick={() => setSelectedZoneId(zone.id)}
                    onTap={() => setSelectedZoneId(zone.id)}
                  />
                  <Text
                    x={labelX}
                    y={labelY - 16}
                    text={zone.name}
                    fontSize={14}
                    fill={color}
                    fontStyle="bold"
                  />
                </Fragment>
              );
            })}

            {drawingPoints.length > 0 && (
              <Line
                points={drawingPoints.flatMap((p) => toPixels(p))}
                stroke="#ffffff"
                strokeWidth={2}
                dash={[4, 4]}
              />
            )}
            {drawingPoints.map((p, i) => {
              const [x, y] = toPixels(p);
              return <Circle key={i} x={x} y={y} radius={4} fill="#ffffff" />;
            })}
          </Layer>
        </Stage>
      </div>

      {zones.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {zones.map((zone, index) => (
            <div
              key={zone.id}
              className="flex items-center gap-2 rounded-md border px-2 py-1 text-sm"
              style={{ borderColor: colorFor(index) }}
            >
              <span>{zone.name}</span>
              <button
                className="text-muted-foreground hover:text-destructive"
                onClick={() => onDeleteZone(zone.id)}
              >
                ×
              </button>
            </div>
          ))}
        </div>
      )}

      <Dialog open={!!pendingPoints} onOpenChange={(open) => !open && setPendingPoints(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Name this zone</DialogTitle>
          </DialogHeader>
          <div className="space-y-2">
            <Label htmlFor="zone-name">Zone name</Label>
            <Input
              id="zone-name"
              value={zoneName}
              onChange={(e) => setZoneName(e.target.value)}
              placeholder="e.g. Restricted Area"
              autoFocus
            />
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setPendingPoints(null)}>
              Cancel
            </Button>
            <Button onClick={confirmZone} disabled={!zoneName.trim()}>
              Save zone
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
