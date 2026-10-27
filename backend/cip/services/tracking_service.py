"""Lightweight in-process, CPU-only multi-object tracker (IOU-matching).

Stands in for full ByteTrack for Phase 1 scaffolding — same role (assign a
stable track_id to a detection across consecutive sampled frames) and same
placement in the pipeline (in-process, never delegated to the HF Space),
so swapping in real ByteTrack later only touches this module.
"""

import itertools
from dataclasses import dataclass, field

from cip.services.inference.base import Detection


def _iou(box_a: dict, box_b: dict) -> float:
    ax1, ay1, ax2, ay2 = box_a["x1"], box_a["y1"], box_a["x2"], box_a["y2"]
    bx1, by1, bx2, by2 = box_b["x1"], box_b["y1"], box_b["x2"], box_b["y2"]

    inter_x1, inter_y1 = max(ax1, bx1), max(ay1, by1)
    inter_x2, inter_y2 = min(ax2, bx2), min(ay2, by2)
    inter_area = max(0.0, inter_x2 - inter_x1) * max(0.0, inter_y2 - inter_y1)
    if inter_area <= 0:
        return 0.0

    area_a = (ax2 - ax1) * (ay2 - ay1)
    area_b = (bx2 - bx1) * (by2 - by1)
    return inter_area / (area_a + area_b - inter_area)


@dataclass
class _Track:
    track_id: int
    object_type: str
    last_box: dict
    missed_frames: int = 0


@dataclass
class SessionTracker:
    """One tracker instance per video_session / camera stream."""

    iou_threshold: float = 0.3
    max_missed_frames: int = 5
    _tracks: list[_Track] = field(default_factory=list)
    _id_counter: itertools.count = field(default_factory=lambda: itertools.count(1))

    def update(self, detections: list[Detection]) -> list[tuple[Detection, int]]:
        assigned: list[tuple[Detection, int]] = []
        unmatched_tracks = list(self._tracks)

        for detection in detections:
            best_track, best_iou = None, 0.0
            for track in unmatched_tracks:
                if track.object_type != detection.object_type:
                    continue
                score = _iou(track.last_box, detection.bounding_box)
                if score > best_iou:
                    best_track, best_iou = track, score

            if best_track and best_iou >= self.iou_threshold:
                best_track.last_box = detection.bounding_box
                best_track.missed_frames = 0
                unmatched_tracks.remove(best_track)
                assigned.append((detection, best_track.track_id))
            else:
                new_track = _Track(
                    track_id=next(self._id_counter),
                    object_type=detection.object_type,
                    last_box=detection.bounding_box,
                )
                self._tracks.append(new_track)
                assigned.append((detection, new_track.track_id))

        for track in unmatched_tracks:
            track.missed_frames += 1
        self._tracks = [t for t in self._tracks if t.missed_frames <= self.max_missed_frames]

        return assigned
