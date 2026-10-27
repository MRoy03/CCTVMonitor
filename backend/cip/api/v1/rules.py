import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from cip.api.deps import get_current_user
from cip.db.session import get_db
from cip.models.camera import Camera
from cip.models.rule import Rule
from cip.models.user import User
from cip.schemas.rule import RuleCreate, RuleResponse, RuleUpdate

router = APIRouter(prefix="/rules", tags=["rules"])


def _camera_in_org(db: Session, camera_id: str, organization_id) -> Camera:
    camera = db.get(Camera, uuid.UUID(camera_id))
    if camera is None or camera.location.organization_id != organization_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Camera not found")
    return camera


def _rule_in_org(db: Session, rule_id: str, organization_id) -> Rule:
    rule = db.get(Rule, uuid.UUID(rule_id))
    if rule is None or rule.organization_id != organization_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rule not found")
    return rule


@router.post("", response_model=RuleResponse)
def create_rule(
    payload: RuleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Rule:
    _camera_in_org(db, payload.camera_id, current_user.organization_id)

    rule = Rule(
        organization_id=current_user.organization_id,
        camera_id=uuid.UUID(payload.camera_id),
        name=payload.name,
        conditions=payload.conditions,
        actions=payload.actions,
        enabled=payload.enabled,
        cooldown_seconds=payload.cooldown_seconds,
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


@router.get("", response_model=list[RuleResponse])
def list_rules(
    camera_id: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Rule]:
    query = db.query(Rule).filter(Rule.organization_id == current_user.organization_id)
    if camera_id:
        query = query.filter(Rule.camera_id == uuid.UUID(camera_id))
    return query.all()


@router.get("/{rule_id}", response_model=RuleResponse)
def get_rule(
    rule_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Rule:
    return _rule_in_org(db, rule_id, current_user.organization_id)


@router.patch("/{rule_id}", response_model=RuleResponse)
def update_rule(
    rule_id: str,
    payload: RuleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Rule:
    rule = _rule_in_org(db, rule_id, current_user.organization_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(rule, field, value)
    db.commit()
    db.refresh(rule)
    return rule


@router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rule(
    rule_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    rule = _rule_in_org(db, rule_id, current_user.organization_id)
    db.delete(rule)
    db.commit()
