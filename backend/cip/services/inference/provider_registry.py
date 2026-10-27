from functools import lru_cache

from cip.services.inference.base import InferenceProvider
from cip.settings import get_settings


@lru_cache
def get_inference_provider() -> InferenceProvider:
    settings = get_settings()
    if settings.ai_provider_mode == "local":
        from cip.services.inference.local_provider import LocalInferenceProvider

        return LocalInferenceProvider()

    from cip.services.inference.stub_provider import StubInferenceProvider

    return StubInferenceProvider()


@lru_cache
def get_report_provider() -> InferenceProvider:
    settings = get_settings()
    if settings.report_provider_mode == "groq":
        from cip.services.inference.groq_provider import GroqReportProvider

        return GroqReportProvider()

    from cip.services.inference.stub_provider import StubInferenceProvider

    return StubInferenceProvider()
