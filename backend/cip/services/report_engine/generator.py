import logging
from datetime import datetime

from sqlalchemy.orm import Session

from cip.models.camera import Camera
from cip.models.report import Report, ReportType
from cip.services.inference.provider_registry import get_report_provider
from cip.services.report_engine.aggregator import aggregate_report_data
from cip.services.report_engine.templates import build_messages

logger = logging.getLogger(__name__)


async def generate_report(
    db: Session,
    camera: Camera,
    report_type: ReportType,
    period_start: datetime,
    period_end: datetime,
) -> Report:
    structured_data = aggregate_report_data(db, camera, period_start, period_end)
    messages = build_messages(report_type, structured_data)

    provider = get_report_provider()
    try:
        report_text = await provider.generate_text(messages)
    except Exception:
        # Narrative generation failing (quota, network, bad key) must not
        # lose the structured facts — those are stored either way.
        logger.exception("Report narrative generation failed for camera %s", camera.id)
        report_text = (
            "(Narrative generation failed — the structured data below is still accurate.)"
        )

    report = Report(
        camera_id=camera.id,
        report_type=report_type,
        period_start=period_start,
        period_end=period_end,
        report_text=report_text,
        structured_data=structured_data,
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report
