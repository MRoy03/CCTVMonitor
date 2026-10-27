import pytest

from cip.services.inference.stub_provider import StubInferenceProvider


@pytest.mark.asyncio
async def test_stub_detect_objects_returns_detection():
    provider = StubInferenceProvider()
    detections = await provider.detect_objects(b"fake-jpeg-bytes")

    assert len(detections) == 1
    assert detections[0].object_type == "person"
    assert 0.0 <= detections[0].confidence <= 1.0
    for key in ("x1", "y1", "x2", "y2"):
        assert 0.0 <= detections[0].bounding_box[key] <= 1.0


@pytest.mark.asyncio
async def test_stub_caption_scene_returns_text():
    provider = StubInferenceProvider()
    result = await provider.caption_scene(b"fake-jpeg-bytes", prompt="describe")

    assert isinstance(result.caption, str) and result.caption


@pytest.mark.asyncio
async def test_stub_generate_text_returns_string():
    provider = StubInferenceProvider()
    text = await provider.generate_text([{"role": "user", "content": "summarize"}])

    assert isinstance(text, str) and text
