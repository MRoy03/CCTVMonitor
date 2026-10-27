"use client";

import Link from "next/link";
import { Plus } from "lucide-react";
import { toast } from "sonner";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Switch } from "@/components/ui/switch";
import { useCameras } from "@/features/sources/hooks";
import { useDeleteRule, useRules, useSetRuleEnabled } from "@/features/rules/hooks";
import { CONDITION_VOCABULARY } from "@/features/rules/vocabulary";

export default function RulesPage() {
  const { data: rules, isLoading } = useRules();
  const { data: cameras } = useCameras();
  const setEnabled = useSetRuleEnabled();
  const deleteRule = useDeleteRule();

  const cameraName = (id: string | null) =>
    cameras?.find((c) => c.id === id)?.name ?? "Unknown camera";

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Rules</h1>
        <Button asChild>
          <Link href="/rules/new">
            <Plus className="mr-2 h-4 w-4" /> New rule
          </Link>
        </Button>
      </div>

      {!isLoading && rules?.length === 0 && (
        <Card>
          <CardContent className="py-12 text-center text-muted-foreground">
            No rules yet. Draw a zone on a camera, then create a rule for it.
          </CardContent>
        </Card>
      )}

      <div className="space-y-3">
        {rules?.map((rule) => {
          const vocab = CONDITION_VOCABULARY[rule.conditions.type];
          return (
            <Card key={rule.id}>
              <CardContent className="flex items-center justify-between py-4">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-medium">{rule.name}</span>
                    <Badge variant="outline">{cameraName(rule.camera_id)}</Badge>
                  </div>
                  <p className="text-sm text-muted-foreground">{vocab?.label}</p>
                </div>
                <div className="flex items-center gap-3">
                  <Switch
                    checked={rule.enabled}
                    onCheckedChange={(checked) =>
                      setEnabled.mutate({ ruleId: rule.id, enabled: checked })
                    }
                  />
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() =>
                      deleteRule.mutate(rule.id, {
                        onSuccess: () => toast.success("Rule deleted"),
                      })
                    }
                  >
                    Delete
                  </Button>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
