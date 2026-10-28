"use client";

import { Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { toast } from "sonner";

import { RuleBuilder } from "@/features/rules/components/rule-builder";
import { useCreateRule } from "@/features/rules/hooks";

function NewRuleForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const cameraId = searchParams.get("camera_id") ?? undefined;
  const createRule = useCreateRule();

  return (
    <RuleBuilder
      initialCameraId={cameraId}
      submitting={createRule.isPending}
      onSubmit={(values) =>
        createRule.mutate(values, {
          onSuccess: () => {
            toast.success("Rule created");
            router.push("/rules");
          },
          onError: (error) =>
            toast.error(error instanceof Error ? error.message : "Could not create rule"),
        })
      }
    />
  );
}

export default function NewRulePage() {
  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <h1 className="text-2xl font-semibold">New rule</h1>
      <Suspense fallback={null}>
        <NewRuleForm />
      </Suspense>
    </div>
  );
}
