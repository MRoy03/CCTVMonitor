"""Report-writing text generation via Groq's free tier. Separate from the
detection InferenceProvider (which is a different vendor/axis entirely) —
this class only implements generate_text; detect_objects/caption_scene are
not this provider's job and raise if called.

Unverified until tested with a real API key — per the lesson from Phase 1
(HuggingFace's "free" compute turned out to require payment), don't assume
this works until a real request succeeds. See docs/PHASES.md.
"""

import httpx

from cip.services.inference.base import Detection, InferenceProvider, VLMResult
from cip.settings import get_settings


class GroqReportProvider(InferenceProvider):
    async def detect_objects(
        self, image_bytes: bytes, classes: list[str] | None = None
    ) -> list[Detection]:
        raise NotImplementedError("GroqReportProvider only implements generate_text")

    async def caption_scene(self, image_bytes: bytes, prompt: str) -> VLMResult:
        raise NotImplementedError("GroqReportProvider only implements generate_text")

    async def generate_text(self, messages: list[dict], max_tokens: int = 1024) -> str:
        settings = get_settings()
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                json={
                    "model": settings.groq_model,
                    "messages": messages,
                    "max_tokens": max_tokens,
                },
                headers={"Authorization": f"Bearer {settings.groq_api_key}"},
            )
            response.raise_for_status()
            payload = response.json()
        return payload["choices"][0]["message"]["content"]
