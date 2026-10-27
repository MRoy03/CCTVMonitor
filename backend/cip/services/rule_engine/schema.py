"""The no-code rule vocabulary. Adding a new condition/action within this
registry is pure configuration from the frontend's perspective — it's only
"new code" the first time a given type is introduced here.

Phase 4 ships the three condition types that directly match the plan's
worked examples (restricted-area dwell, empty-desk absence, crowd count),
plus `and`/`or` composites. `zone_entry`/`zone_exit`/`object_state`/
`ppe_missing`/`custom_vlm_flag` are intentionally not implemented yet — the
first three need event-transition tracking this phase doesn't build, and the
last two need Phase 5's VLM, which doesn't have a provider chosen yet.
"""

LEAF_CONDITION_TYPES = {"zone_dwell_duration", "zone_absence_duration", "object_count_in_zone"}
COMPOSITE_CONDITION_TYPES = {"and", "or"}
CONDITION_TYPES = LEAF_CONDITION_TYPES | COMPOSITE_CONDITION_TYPES

ACTION_TYPES = {"create_incident", "create_observation"}

LEAF_CONDITION_REQUIRED_PARAMS = {
    "zone_dwell_duration": {"zone_id", "object_type", "min_duration_seconds"},
    "zone_absence_duration": {"zone_id", "object_type", "min_duration_seconds"},
    "object_count_in_zone": {"zone_id", "object_type", "min_count"},
}


def validate_condition(condition: dict) -> None:
    ctype = condition.get("type")
    if ctype in COMPOSITE_CONDITION_TYPES:
        children = condition.get("children")
        if not isinstance(children, list) or len(children) < 1:
            raise ValueError(f"'{ctype}' condition needs a non-empty 'children' list")
        for child in children:
            validate_condition(child)
        return

    if ctype not in LEAF_CONDITION_TYPES:
        raise ValueError(f"Unknown condition type: {ctype!r}")

    params = condition.get("params", {})
    required = LEAF_CONDITION_REQUIRED_PARAMS[ctype]
    missing = required - params.keys()
    if missing:
        raise ValueError(f"Condition '{ctype}' is missing params: {sorted(missing)}")


def validate_actions(actions: list) -> None:
    if not isinstance(actions, list) or len(actions) < 1:
        raise ValueError("At least one action is required")
    for action in actions:
        if action.get("type") not in ACTION_TYPES:
            raise ValueError(f"Unknown action type: {action.get('type')!r}")
