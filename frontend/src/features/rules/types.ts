export type ConditionType = "zone_dwell_duration" | "zone_absence_duration" | "object_count_in_zone";
export type ActionType = "create_incident" | "create_observation";
export type Severity = "info" | "warning" | "critical";

export interface Rule {
  id: string;
  organization_id: string;
  camera_id: string | null;
  name: string;
  conditions: {
    type: ConditionType;
    params: Record<string, string | number>;
  };
  actions: {
    type: ActionType;
    params: Record<string, string>;
  }[];
  enabled: boolean;
  cooldown_seconds: number;
}

export interface RuleFormValues {
  camera_id: string;
  name: string;
  condition_type: ConditionType;
  zone_id: string;
  object_type: string;
  duration_seconds: number; // used by dwell/absence
  min_count: number; // used by object_count_in_zone
  action_type: ActionType;
  severity: Severity;
  description: string;
  cooldown_seconds: number;
}
