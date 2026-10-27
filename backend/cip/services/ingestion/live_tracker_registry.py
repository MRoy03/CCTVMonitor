"""Keeps one SessionTracker alive per camera across independent HTTP frame
POSTs (screen-capture ingestion). Unlike the StreamManager's own per-process
tracker, frames here arrive as discrete requests to the API process rather
than from a pull loop, so the tracker has to live somewhere between requests
— an in-process registry is enough at this project's scale (single uvicorn
worker, a handful of cameras); revisit if the API ever runs multiple workers.
"""

import uuid

from cip.services.tracking_service import SessionTracker

_trackers: dict[uuid.UUID, SessionTracker] = {}


def get_tracker(camera_id: uuid.UUID) -> SessionTracker:
    if camera_id not in _trackers:
        _trackers[camera_id] = SessionTracker()
    return _trackers[camera_id]
