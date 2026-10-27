"use client";

import type { DetectionEvent } from "@/features/sources/types";

const TRACK_COLORS = [
  "#f87171",
  "#60a5fa",
  "#34d399",
  "#fbbf24",
  "#a78bfa",
  "#f472b6",
];

function colorForTrack(trackId: number | null) {
  if (trackId === null) return TRACK_COLORS[0];
  return TRACK_COLORS[trackId % TRACK_COLORS.length];
}

export function BoundingBoxOverlay({ detections }: { detections: DetectionEvent[] }) {
  return (
    <svg
      className="pointer-events-none absolute inset-0 h-full w-full"
      viewBox="0 0 100 100"
      preserveAspectRatio="none"
    >
      {detections.map((detection) => {
        const { x1, y1, x2, y2 } = detection.bounding_box;
        const color = colorForTrack(detection.track_id);
        return (
          <g key={detection.id}>
            <rect
              x={x1 * 100}
              y={y1 * 100}
              width={(x2 - x1) * 100}
              height={(y2 - y1) * 100}
              fill="none"
              stroke={color}
              strokeWidth={0.4}
              vectorEffect="non-scaling-stroke"
            />
            <text
              x={x1 * 100}
              y={Math.max(0, y1 * 100 - 1)}
              fill={color}
              fontSize={3}
              fontWeight={600}
            >
              {detection.object_type}
              {detection.track_id !== null ? ` #${detection.track_id}` : ""}
            </text>
          </g>
        );
      })}
    </svg>
  );
}
