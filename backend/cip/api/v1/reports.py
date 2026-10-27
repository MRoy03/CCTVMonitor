import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from cip.api.deps import get_current_user
from cip.db.session import get_db
from cip.models.camera import Camera
from cip.models.report import Report
from cip.models.user import User
from cip.schemas.report import ReportCreate, ReportResponse, ReportSummary
from cip.services.report_engine.generator import generate_report

router = APIRouter(tags=["reports"])


def _camera_in_org(db: Session, camera_id: str, organization_id) -> Camera:
    camera = db.get(Camera, uuid.UUID(camera_id))
    if camera is None or camera.location.organization_id != organization_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Camera not found")
    return camera


@router.post("/cameras/{camera_id}/reports", response_model=ReportResponse)
async def create_report(
    camera_id: str,
    payload: ReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Report:
    camera = _camera_in_org(db, camera_id, current_user.organization_id)
    return await generate_report(
        db, camera, payload.report_type, payload.period_start, payload.period_end
    )


@router.get("/cameras/{camera_id}/reports", response_model=list[ReportSummary])
def list_reports(
    camera_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Report]:
    camera = _camera_in_org(db, camera_id, current_user.organization_id)
    return (
        db.query(Report)
        .filter(Report.camera_id == camera.id)
        .order_by(Report.period_end.desc())
        .all()
    )


@router.get("/reports/{report_id}", response_model=ReportResponse)
def get_report(
    report_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Report:
    report = db.get(Report, uuid.UUID(report_id))
    if report is None or report.camera.location.organization_id != current_user.organization_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    return report
