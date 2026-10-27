import uuid
from datetime import datetime

from pydantic import BaseModel

from cip.models.report import ReportType


class ReportCreate(BaseModel):
    report_type: ReportType
    period_start: datetime
    period_end: datetime


class ReportResponse(BaseModel):
    id: uuid.UUID
    camera_id: uuid.UUID
    report_type: ReportType
    period_start: datetime
    period_end: datetime
    report_text: str
    structured_data: dict

    model_config = {"from_attributes": True}


class ReportSummary(BaseModel):
    """Lighter shape for list views — skips report_text/structured_data."""

    id: uuid.UUID
    camera_id: uuid.UUID
    report_type: ReportType
    period_start: datetime
    period_end: datetime

    model_config = {"from_attributes": True}
