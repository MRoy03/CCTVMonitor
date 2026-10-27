import type { ConditionType } from "./types";

export const CONDITION_VOCABULARY: Record<
  ConditionType,
  {
    label: string;
    needsZone: true;
    needsDuration: boolean;
    needsCount: boolean;
    describe: (zoneName: string, objectType: string, value: number) => string;
  }
> = {
  zone_dwell_duration: {
    label: "Object remains in a zone",
    needsZone: true,
    needsDuration: true,
    needsCount: false,
    describe: (zone, type, seconds) =>
      `a ${type} remains inside "${zone}" for ${seconds} seconds or more`,
  },
  zone_absence_duration: {
    label: "Zone has been empty",
    needsZone: true,
    needsDuration: true,
    needsCount: false,
    describe: (zone, type, seconds) =>
      `"${zone}" has had no ${type} for ${seconds} seconds or more`,
  },
  object_count_in_zone: {
    label: "Too many objects in a zone",
    needsZone: true,
    needsDuration: false,
    needsCount: true,
    describe: (zone, type, count) =>
      `${count} or more ${type}s are present in "${zone}" at once`,
  },
};

// A practical subset of the COCO classes our YOLO nano model can detect.
export const OBJECT_TYPES = [
  "person",
  "bicycle",
  "car",
  "motorcycle",
  "bus",
  "truck",
  "backpack",
  "handbag",
  "suitcase",
  "dog",
  "cat",
];

export const ACTION_LABELS: Record<string, string> = {
  create_incident: "Create an incident",
  create_observation: "Create an observation",
};

export const SEVERITY_LABELS: Record<string, string> = {
  info: "Info",
  warning: "Warning",
  critical: "Critical",
};
