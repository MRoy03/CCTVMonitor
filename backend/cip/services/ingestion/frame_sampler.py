"""Decodes a video file and yields sampled frames as JPEG bytes at a fixed
interval (default from settings.frame_sample_interval_seconds). Same sampler
is reused for uploaded video (Phase 1), RTSP (Phase 2), and screen-capture
(Phase 3) once frames reach this stage.
"""

from collections.abc import Iterator

import cv2
import numpy as np

from cip.settings import get_settings


def sample_frames_from_file(video_path: str) -> Iterator[tuple[float, bytes]]:
    settings = get_settings()
    capture = cv2.VideoCapture(video_path)
    fps = capture.get(cv2.CAP_PROP_FPS) or 25.0
    frame_interval = max(1, round(fps * settings.frame_sample_interval_seconds))

    frame_index = 0
    try:
        while True:
            ok, frame = capture.read()
            if not ok:
                break
            if frame_index % frame_interval == 0:
                timestamp_seconds = frame_index / fps
                ok_encode, buffer = cv2.imencode(".jpg", frame)
                if ok_encode:
                    yield timestamp_seconds, buffer.tobytes()
            frame_index += 1
    finally:
        capture.release()


def frame_dimensions(image_bytes: bytes) -> tuple[int, int]:
    array = np.frombuffer(image_bytes, dtype=np.uint8)
    image = cv2.imdecode(array, cv2.IMREAD_COLOR)
    height, width = image.shape[:2]
    return width, height
