import cv2
import numpy as np

from cip.services.ingestion.frame_sampler import frame_dimensions, sample_frames_from_file


def _write_synthetic_video(path: str, fps: int = 10, seconds: int = 3, size=(64, 48)) -> None:
    width, height = size
    writer = cv2.VideoWriter(path, cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height))
    for i in range(fps * seconds):
        frame = np.full((height, width, 3), fill_value=i % 256, dtype=np.uint8)
        writer.write(frame)
    writer.release()


def test_sample_frames_at_configured_interval(tmp_path, monkeypatch):
    from cip.settings import get_settings

    get_settings.cache_clear()
    monkeypatch.setenv("FRAME_SAMPLE_INTERVAL_SECONDS", "1.0")

    video_path = tmp_path / "synthetic.mp4"
    _write_synthetic_video(str(video_path), fps=10, seconds=3)

    sampled = list(sample_frames_from_file(str(video_path)))

    # 3 seconds at 1 sample/sec -> roughly 3 frames (allow off-by-one from fps rounding)
    assert 2 <= len(sampled) <= 4
    for offset_seconds, frame_bytes in sampled:
        assert isinstance(offset_seconds, float)
        assert isinstance(frame_bytes, bytes)
        assert len(frame_bytes) > 0

    get_settings.cache_clear()


def test_frame_dimensions_reads_encoded_jpeg(tmp_path):
    video_path = tmp_path / "synthetic.mp4"
    _write_synthetic_video(str(video_path), fps=5, seconds=1, size=(64, 48))

    _, frame_bytes = next(sample_frames_from_file(str(video_path)))
    width, height = frame_dimensions(frame_bytes)

    assert (width, height) == (64, 48)
