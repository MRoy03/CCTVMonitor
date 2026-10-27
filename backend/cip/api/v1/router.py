from fastapi import APIRouter

from cip.api.v1 import (
    auth,
    cameras,
    feedback,
    locations,
    reports,
    rules,
    screen_capture,
    video_sessions,
    zones,
)

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(locations.router)
api_router.include_router(cameras.router)
api_router.include_router(video_sessions.router)
api_router.include_router(zones.router)
api_router.include_router(screen_capture.router)
api_router.include_router(rules.router)
api_router.include_router(reports.router)
api_router.include_router(feedback.router)
