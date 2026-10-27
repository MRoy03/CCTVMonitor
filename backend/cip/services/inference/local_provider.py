"""Runs object detection in-process using an Ultralytics YOLO nano model
(CPU). This is what actually satisfies the project's two real constraints:
$0 cost and running on cloud compute (wherever the backend is deployed —
Fly.io's free VM, not the developer's own machine) rather than a separate
hosted inference product.

Model weights are pulled once from the HuggingFace/Ultralytics Hub on first
use (plain free file download, unrelated to HF's paid Spaces/Inference
Providers compute) and cached on disk by `ultralytics` itself.

VLM captioning and the report-writing LLM are not implemented here yet —
Phase 5 needs its own (still-unverified) free text/vision API; don't assume
any specific provider works until it's actually tested, the way YOLO's
cloud-hosting path turned out not to (HF Spaces/Inference Providers both
now require payment).
"""

from functools import lru_cache

import numpy as np
from ultralytics import YOLO

from cip.services.inference.base import Detection, InferenceProvider, VLMResult


@lru_cache
def _get_model() -> YOLO:
    return YOLO("yolo11n.pt")  # nano weights: small enough to run acceptably on CPU


class LocalInferenceProvider(InferenceProvider):
    async def detect_objects(
        self, image_bytes: bytes, classes: list[str] | None = None
    ) -> list[Detection]:
        import cv2

        array = np.frombuffer(image_bytes, dtype=np.uint8)
        image = cv2.imdecode(array, cv2.IMREAD_COLOR)
        height, width = image.shape[:2]

        model = _get_model()
        wanted_classes = set(classes) if classes else None
        results = model.predict(image, verbose=False)[0]
        names = results.names

        detections = []
        for box in results.boxes:
            label = names[int(box.cls[0])]
            if wanted_classes and label not in wanted_classes:
                continue
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            detections.append(
                Detection(
                    object_type=label,
                    confidence=float(box.conf[0]),
                    bounding_box={
                        "x1": x1 / width,
                        "y1": y1 / height,
                        "x2": x2 / width,
                        "y2": y2 / height,
                    },
                )
            )
        return detections

    async def caption_scene(self, image_bytes: bytes, prompt: str) -> VLMResult:
        raise NotImplementedError(
            "VLM captioning is deferred to Phase 5 — no free hosted/in-process "
            "option has been verified yet."
        )

    async def generate_text(self, messages: list[dict], max_tokens: int = 1024) -> str:
        raise NotImplementedError(
            "Report-writing LLM calls are deferred to Phase 5 — verify Groq's "
            "free tier actually works before wiring this up, given HF's "
            "compute pricing changed since this plan was written."
        )
