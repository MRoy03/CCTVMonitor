from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class Detection:
    object_type: str
    confidence: float
    bounding_box: dict  # normalized {x1,y1,x2,y2} in 0-1 image space


@dataclass
class VLMResult:
    caption: str
    flags: dict  # e.g. {"ppe_missing": true}


class InferenceProvider(ABC):
    """One interface for every AI task. Swapping the concrete implementation
    (stub for dev/CI, the HF Space for deployed envs, a future paid vendor)
    is a config choice (AI_PROVIDER_MODE) — business logic never changes.
    """

    @abstractmethod
    async def detect_objects(
        self, image_bytes: bytes, classes: list[str] | None = None
    ) -> list[Detection]: ...

    @abstractmethod
    async def caption_scene(self, image_bytes: bytes, prompt: str) -> VLMResult: ...

    @abstractmethod
    async def generate_text(self, messages: list[dict], max_tokens: int = 1024) -> str: ...
