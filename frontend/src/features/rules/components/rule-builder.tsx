"use client";

import { useMemo, useState } from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { useCameras } from "@/features/sources/hooks";
import { useZones } from "@/features/zones/hooks";
import type { ConditionType, RuleFormValues, Severity } from "../types";
import { ACTION_LABELS, CONDITION_VOCABULARY, OBJECT_TYPES, SEVERITY_LABELS } from "../vocabulary";

const DEFAULT_VALUES: RuleFormValues = {
  camera_id: "",
  name: "",
  condition_type: "zone_dwell_duration",
  zone_id: "",
  object_type: "person",
  duration_seconds: 300,
  min_count: 2,
  action_type: "create_incident",
  severity: "warning",
  description: "",
  cooldown_seconds: 300,
};

export function RuleBuilder({
  initialCameraId,
  onSubmit,
  submitting,
}: {
  initialCameraId?: string;
  onSubmit: (values: RuleFormValues) => void;
  submitting?: boolean;
}) {
  const [values, setValues] = useState<RuleFormValues>({
    ...DEFAULT_VALUES,
    camera_id: initialCameraId ?? "",
  });

  const { data: cameras } = useCameras();
  const { data: zones } = useZones(values.camera_id);

  const vocab = CONDITION_VOCABULARY[values.condition_type];
  const selectedZoneName = zones?.find((z) => z.id === values.zone_id)?.name ?? "the zone";

  const previewSentence = useMemo(() => {
    const value = vocab.needsCount ? values.min_count : values.duration_seconds;
    return `If ${vocab.describe(selectedZoneName, values.object_type, value)}, then ${ACTION_LABELS[values.action_type].toLowerCase()} (${SEVERITY_LABELS[values.severity].toLowerCase()} severity).`;
  }, [vocab, selectedZoneName, values]);

  function update<K extends keyof RuleFormValues>(key: K, value: RuleFormValues[K]) {
    setValues((prev) => ({ ...prev, [key]: value }));
  }

  const isValid = values.camera_id && values.name.trim() && values.zone_id;

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Rule name</CardTitle>
        </CardHeader>
        <CardContent>
          <Input
            value={values.name}
            onChange={(e) => update("name", e.target.value)}
            placeholder="e.g. Restricted area watch"
          />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Camera</CardTitle>
        </CardHeader>
        <CardContent>
          <Select
            value={values.camera_id}
            onValueChange={(value) => update("camera_id", value)}
            disabled={!!initialCameraId}
          >
            <SelectTrigger>
              <SelectValue placeholder="Choose a camera" />
            </SelectTrigger>
            <SelectContent>
              {cameras?.map((camera) => (
                <SelectItem key={camera.id} value={camera.id}>
                  {camera.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">IF — condition</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label>What should trigger this rule?</Label>
            <Select
              value={values.condition_type}
              onValueChange={(value) => update("condition_type", value as ConditionType)}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {Object.entries(CONDITION_VOCABULARY).map(([key, meta]) => (
                  <SelectItem key={key} value={key}>
                    {meta.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-2">
              <Label>Zone</Label>
              <Select
                value={values.zone_id}
                onValueChange={(value) => update("zone_id", value)}
                disabled={!values.camera_id}
              >
                <SelectTrigger>
                  <SelectValue
                    placeholder={values.camera_id ? "Choose a zone" : "Pick a camera first"}
                  />
                </SelectTrigger>
                <SelectContent>
                  {zones?.map((zone) => (
                    <SelectItem key={zone.id} value={zone.id}>
                      {zone.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {values.camera_id && zones?.length === 0 && (
                <p className="text-xs text-muted-foreground">
                  No zones drawn yet for this camera — draw one from the camera&apos;s page first.
                </p>
              )}
            </div>

            <div className="space-y-2">
              <Label>Object type</Label>
              <Select
                value={values.object_type}
                onValueChange={(value) => update("object_type", value)}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {OBJECT_TYPES.map((type) => (
                    <SelectItem key={type} value={type}>
                      {type}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          {vocab.needsDuration && (
            <div className="space-y-2">
              <Label>Duration (seconds)</Label>
              <Input
                type="number"
                min={1}
                value={values.duration_seconds}
                onChange={(e) => update("duration_seconds", Number(e.target.value))}
              />
            </div>
          )}
          {vocab.needsCount && (
            <div className="space-y-2">
              <Label>Minimum count</Label>
              <Input
                type="number"
                min={1}
                value={values.min_count}
                onChange={(e) => update("min_count", Number(e.target.value))}
              />
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">THEN — action</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-2">
              <Label>Action</Label>
              <Select
                value={values.action_type}
                onValueChange={(value) => update("action_type", value as RuleFormValues["action_type"])}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {Object.entries(ACTION_LABELS).map(([key, label]) => (
                    <SelectItem key={key} value={key}>
                      {label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label>Severity</Label>
              <Select
                value={values.severity}
                onValueChange={(value) => update("severity", value as Severity)}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {Object.entries(SEVERITY_LABELS).map(([key, label]) => (
                    <SelectItem key={key} value={key}>
                      {label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="space-y-2">
            <Label>Description (optional)</Label>
            <Textarea
              value={values.description}
              onChange={(e) => update("description", e.target.value)}
              placeholder="Shown on the resulting incident/observation"
            />
          </div>

          <div className="space-y-2">
            <Label>Cooldown — don&apos;t re-trigger for (seconds)</Label>
            <Input
              type="number"
              min={0}
              value={values.cooldown_seconds}
              onChange={(e) => update("cooldown_seconds", Number(e.target.value))}
            />
          </div>
        </CardContent>
      </Card>

      <Card className="border-primary/40 bg-primary/5">
        <CardContent className="py-4 text-sm font-medium">{previewSentence}</CardContent>
      </Card>

      <Button disabled={!isValid || submitting} onClick={() => onSubmit(values)}>
        {submitting ? "Saving…" : "Save rule"}
      </Button>
    </div>
  );
}
