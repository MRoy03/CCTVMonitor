"""Deterministic, no-network provider used for local dev and CI (AI_PROVIDER_MODE=stub).

Returns fixture-shaped responses so the ingestion pipeline, zone/rule engine,
and frontend can all be built and tested without calling the HF Space or
burning any free-tier quota.
"""

from cip.services.inference.base import Detection, InferenceProvider, VLMResult


class StubInferenceProvider(InferenceProvider):
    async def detect_objects(
        self, image_bytes: bytes, classes: list[str] | None = None
    ) -> list[Detection]:
        return [
            Detection(
                object_type="person",
                confidence=0.91,
                bounding_box={"x1": 0.30, "y1": 0.20, "x2": 0.55, "y2": 0.90},
            )
        ]

    async def caption_scene(self, image_bytes: bytes, prompt: str) -> VLMResult:
        return VLMResult(caption="A person is visible in the frame.", flags={})

    async def generate_text(self, messages: list[dict], max_tokens: int = 1024) -> str:
        return "Stub report: no notable activity detected in this period."
