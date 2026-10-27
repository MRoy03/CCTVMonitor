from cip.services.inference.base import Detection
from cip.services.tracking_service import SessionTracker


def _box(x1: float, y1: float, x2: float, y2: float) -> dict:
    return {"x1": x1, "y1": y1, "x2": x2, "y2": y2}


def test_same_object_keeps_track_id_across_frames():
    tracker = SessionTracker()

    frame1 = [Detection("person", 0.9, _box(0.1, 0.1, 0.3, 0.5))]
    frame2 = [Detection("person", 0.9, _box(0.12, 0.1, 0.32, 0.5))]  # small shift, high overlap

    (_, track_id_1), = tracker.update(frame1)
    (_, track_id_2), = tracker.update(frame2)

    assert track_id_1 == track_id_2


def test_different_object_types_never_share_a_track():
    tracker = SessionTracker()

    frame1 = [Detection("person", 0.9, _box(0.1, 0.1, 0.3, 0.5))]
    frame2 = [Detection("vehicle", 0.9, _box(0.1, 0.1, 0.3, 0.5))]  # identical box, different class

    (_, track_id_1), = tracker.update(frame1)
    (_, track_id_2), = tracker.update(frame2)

    assert track_id_1 != track_id_2


def test_track_dropped_after_too_many_missed_frames():
    tracker = SessionTracker(max_missed_frames=2)

    (_, original_id), = tracker.update([Detection("person", 0.9, _box(0.1, 0.1, 0.3, 0.5))])

    for _ in range(3):
        tracker.update([])  # object leaves frame

    (_, new_id), = tracker.update([Detection("person", 0.9, _box(0.1, 0.1, 0.3, 0.5))])

    assert new_id != original_id


def test_two_simultaneous_objects_get_distinct_tracks():
    tracker = SessionTracker()

    detections = [
        Detection("person", 0.9, _box(0.0, 0.0, 0.2, 0.2)),
        Detection("person", 0.9, _box(0.6, 0.6, 0.8, 0.8)),
    ]
    assigned = tracker.update(detections)

    track_ids = {track_id for _, track_id in assigned}
    assert len(track_ids) == 2
