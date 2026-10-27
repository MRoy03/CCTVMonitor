"""Evaluates a camera's enabled Rules against current DetectionEvent history
and fires actions (writes ActivityEvents) for conditions that are met,
respecting each rule's cooldown.

Two triggers call this same function (per the plan): event-driven, right
after process_frame persists new DetectionEvents (this module), and a
periodic Celery Beat sweep (cip.workers.tasks_rules) that catches
duration-based conditions with no new detections — e.g. "desk empty for 15
minutes" has no new DetectionEvents to react to; only a periodic sweep can
notice time has simply passed.

Dwell/presence is computed on demand from DetectionEvents history rather
than a separate Redis-backed tracker (the plan's original idea) — simpler,
one data store, and fast enough at this project's scale (a handful of
cameras, 1-2fps). RuleState persists only what can't be derived from
history: cooldown (last_triggered_at).
"""

import logging
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from cip.models.activity_event import ActivityEvent, Severity
from cip.models.detection_event import DetectionEvent
from cip.models.rule import Rule
from cip.models.rule_state import RuleState
from cip.models.zone import Zone

logger = logging.getLogger(__name__)

# A track/zone pairing counts as "currently present" if detected within this
# window — must be a few multiples of the frame sample interval so a single
# missed/skipped frame doesn't look like the object left.
RECENT_PRESENCE_SECONDS = 10
# Consecutive detections more than this far apart don't count as one
# continuous dwell period (the object likely left and came back).
CONTINUITY_GAP_SECONDS = 15


def evaluate_rules_for_camera(db: Session, camera_id: uuid.UUID) -> None:
    now = datetime.now(timezone.utc)
    rules = db.query(Rule).filter(Rule.camera_id == camera_id, Rule.enabled.is_(True)).all()

    for rule in rules:
        try:
            matched_entities = _evaluate_condition(db, camera_id, rule.conditions, now)
        except Exception:
            logger.exception("Error evaluating rule %s (%s)", rule.id, rule.name)
            continue

        zone_id = _extract_zone_id(rule.conditions)

        for entity_key in matched_entities:
            state = _get_or_create_state(db, rule.id, entity_key)
            if state.last_triggered_at is not None:
                elapsed = (now - state.last_triggered_at).total_seconds()
                if elapsed < rule.cooldown_seconds:
                    continue

            track_id = _track_id_from_entity_key(entity_key)
            _execute_actions(db, rule, camera_id, zone_id, track_id, now)
            state.last_triggered_at = now

    db.commit()


def _extract_zone_id(condition: dict) -> uuid.UUID | None:
    """Best-effort zone attribution for the resulting ActivityEvent — all
    three leaf condition types take a zone_id. A composite (and/or) rule
    spanning multiple zones just reports the first one found; that's a
    reasonable simplification until composite rules are actually common.
    """
    if condition["type"] in ("and", "or"):
        for child in condition["children"]:
            zone_id = _extract_zone_id(child)
            if zone_id is not None:
                return zone_id
        return None

    zone_id = condition.get("params", {}).get("zone_id")
    return uuid.UUID(zone_id) if zone_id else None


def _evaluate_condition(
    db: Session, camera_id: uuid.UUID, condition: dict, now: datetime
) -> list[str]:
    ctype = condition["type"]

    if ctype == "and":
        results = [
            set(_evaluate_condition(db, camera_id, child, now))
            for child in condition["children"]
        ]
        return sorted(set.intersection(*results)) if results else []

    if ctype == "or":
        matched: set[str] = set()
        for child in condition["children"]:
            matched |= set(_evaluate_condition(db, camera_id, child, now))
        return sorted(matched)

    params = condition.get("params", {})
    if ctype == "zone_dwell_duration":
        return _eval_zone_dwell_duration(db, camera_id, params, now)
    if ctype == "zone_absence_duration":
        return _eval_zone_absence_duration(db, camera_id, params, now)
    if ctype == "object_count_in_zone":
        return _eval_object_count_in_zone(db, camera_id, params, now)

    raise ValueError(f"Unknown condition type: {ctype!r}")


def _zone_name(db: Session, camera_id: uuid.UUID, zone_id: str) -> str | None:
    zone = db.get(Zone, uuid.UUID(zone_id))
    if zone is None or zone.camera_id != camera_id:
        return None
    return zone.name


def _eval_zone_dwell_duration(
    db: Session, camera_id: uuid.UUID, params: dict, now: datetime
) -> list[str]:
    zone_name = _zone_name(db, camera_id, params["zone_id"])
    if zone_name is None:
        return []
    min_duration = params["min_duration_seconds"]
    object_type = params["object_type"]

    recent_cutoff = now - timedelta(seconds=RECENT_PRESENCE_SECONDS)
    present_tracks = (
        db.query(DetectionEvent.track_id)
        .filter(
            DetectionEvent.camera_id == camera_id,
            DetectionEvent.zone == zone_name,
            DetectionEvent.object_type == object_type,
            DetectionEvent.track_id.isnot(None),
            DetectionEvent.timestamp >= recent_cutoff,
        )
        .distinct()
        .all()
    )

    matched = []
    gap_tolerance = timedelta(seconds=CONTINUITY_GAP_SECONDS)
    for (track_id,) in present_tracks:
        timestamps = [
            row[0]
            for row in db.query(DetectionEvent.timestamp)
            .filter(
                DetectionEvent.camera_id == camera_id,
                DetectionEvent.zone == zone_name,
                DetectionEvent.object_type == object_type,
                DetectionEvent.track_id == track_id,
            )
            .order_by(DetectionEvent.timestamp.desc())
            .limit(500)
            .all()
        ]
        if not timestamps:
            continue

        continuous_start = timestamps[0]
        prev = timestamps[0]
        for ts in timestamps[1:]:
            if prev - ts > gap_tolerance:
                break
            continuous_start = ts
            prev = ts

        dwell_seconds = (now - continuous_start).total_seconds()
        if dwell_seconds >= min_duration:
            matched.append(f"track:{track_id}")

    return matched


def _eval_zone_absence_duration(
    db: Session, camera_id: uuid.UUID, params: dict, now: datetime
) -> list[str]:
    zone_name = _zone_name(db, camera_id, params["zone_id"])
    if zone_name is None:
        return []
    min_duration = params["min_duration_seconds"]
    object_type = params["object_type"]

    last_seen = (
        db.query(func.max(DetectionEvent.timestamp))
        .filter(
            DetectionEvent.camera_id == camera_id,
            DetectionEvent.zone == zone_name,
            DetectionEvent.object_type == object_type,
        )
        .scalar()
    )

    if last_seen is not None:
        absence_seconds = (now - last_seen).total_seconds()
    else:
        # Never seen in this zone. Only treat as "absent" if the camera has
        # actually been monitored for a while — otherwise a brand-new camera
        # would immediately fire every absence rule.
        first_seen = (
            db.query(func.min(DetectionEvent.timestamp))
            .filter(DetectionEvent.camera_id == camera_id)
            .scalar()
        )
        if first_seen is None:
            return []
        absence_seconds = (now - first_seen).total_seconds()

    return ["zone"] if absence_seconds >= min_duration else []


def _eval_object_count_in_zone(
    db: Session, camera_id: uuid.UUID, params: dict, now: datetime
) -> list[str]:
    zone_name = _zone_name(db, camera_id, params["zone_id"])
    if zone_name is None:
        return []
    min_count = params["min_count"]
    object_type = params["object_type"]

    recent_cutoff = now - timedelta(seconds=RECENT_PRESENCE_SECONDS)
    count = (
        db.query(DetectionEvent.track_id)
        .filter(
            DetectionEvent.camera_id == camera_id,
            DetectionEvent.zone == zone_name,
            DetectionEvent.object_type == object_type,
            DetectionEvent.track_id.isnot(None),
            DetectionEvent.timestamp >= recent_cutoff,
        )
        .distinct()
        .count()
    )
    return ["zone"] if count >= min_count else []


def _track_id_from_entity_key(entity_key: str) -> int | None:
    if entity_key.startswith("track:"):
        return int(entity_key.removeprefix("track:"))
    return None


def _get_or_create_state(db: Session, rule_id: uuid.UUID, entity_key: str) -> RuleState:
    state = (
        db.query(RuleState)
        .filter(RuleState.rule_id == rule_id, RuleState.entity_key == entity_key)
        .first()
    )
    if state is None:
        state = RuleState(rule_id=rule_id, entity_key=entity_key, state={})
        db.add(state)
        db.flush()
    return state


def _execute_actions(
    db: Session,
    rule: Rule,
    camera_id: uuid.UUID,
    zone_id: uuid.UUID | None,
    track_id: int | None,
    now: datetime,
) -> None:
    for action in rule.actions:
        action_type = action.get("type")
        params = action.get("params", {})

        if action_type not in ("create_incident", "create_observation"):
            logger.warning(
                "Rule %s: unsupported action type %r (e.g. generate_alert needs Phase 8)",
                rule.id,
                action_type,
            )
            continue

        severity = Severity(params.get("severity", "INFO").upper())
        event_type = params.get("event_type") or (
            "incident" if action_type == "create_incident" else "observation"
        )
        description = params.get("description") or f"Rule '{rule.name}' triggered"

        db.add(
            ActivityEvent(
                camera_id=camera_id,
                zone_id=zone_id,
                rule_id=rule.id,
                track_id=track_id,
                start_time=now,
                event_type=event_type,
                severity=severity,
                description=description,
            )
        )
