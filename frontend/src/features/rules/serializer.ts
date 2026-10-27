import type { Rule, RuleFormValues } from "./types";

/** UI form state -> the backend's Rules.conditions/actions JSON shape. The
 * one place that needs to stay in sync with cip/services/rule_engine/schema.py.
 */
export function toApiPayload(values: RuleFormValues) {
  const conditionParams: Record<string, string | number> = {
    zone_id: values.zone_id,
    object_type: values.object_type,
  };
  if (values.condition_type === "object_count_in_zone") {
    conditionParams.min_count = values.min_count;
  } else {
    conditionParams.min_duration_seconds = values.duration_seconds;
  }

  return {
    camera_id: values.camera_id,
    name: values.name,
    conditions: { type: values.condition_type, params: conditionParams },
    actions: [
      {
        type: values.action_type,
        params: { severity: values.severity, description: values.description },
      },
    ],
    enabled: true,
    cooldown_seconds: values.cooldown_seconds,
  };
}

export function fromRule(rule: Rule): RuleFormValues {
  const params = rule.conditions.params;
  const action = rule.actions[0];
  return {
    camera_id: rule.camera_id ?? "",
    name: rule.name,
    condition_type: rule.conditions.type,
    zone_id: String(params.zone_id ?? ""),
    object_type: String(params.object_type ?? "person"),
    duration_seconds: Number(params.min_duration_seconds ?? 300),
    min_count: Number(params.min_count ?? 2),
    action_type: action?.type ?? "create_incident",
    severity: (action?.params.severity as RuleFormValues["severity"]) ?? "info",
    description: action?.params.description ?? "",
    cooldown_seconds: rule.cooldown_seconds,
  };
}
