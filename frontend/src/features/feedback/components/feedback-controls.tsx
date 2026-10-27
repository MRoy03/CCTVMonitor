"use client";

import { useState } from "react";
import { Check, EyeOff, ThumbsDown, ThumbsUp } from "lucide-react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { useSubmitFeedback } from "@/features/feedback/hooks";
import type { FeedbackVerdict } from "@/features/feedback/types";

export function FeedbackControls({
  cameraId,
  detectionEventId,
  activityEventId,
}: {
  cameraId: string;
  detectionEventId?: string;
  activityEventId?: string;
}) {
  const [submitted, setSubmitted] = useState<FeedbackVerdict | null>(null);
  const submitFeedback = useSubmitFeedback(cameraId);

  function submit(verdict: FeedbackVerdict) {
    submitFeedback.mutate(
      { detection_event_id: detectionEventId, activity_event_id: activityEventId, verdict },
      {
        onSuccess: () => setSubmitted(verdict),
        onError: (error) =>
          toast.error(error instanceof Error ? error.message : "Could not submit feedback"),
      },
    );
  }

  if (submitted) {
    return (
      <span className="flex items-center gap-1 text-xs text-muted-foreground">
        <Check className="h-3 w-3" /> {submitted === "CORRECT" ? "Correct" : submitted === "INCORRECT" ? "Incorrect" : "Ignored"}
      </span>
    );
  }

  return (
    <div className="flex items-center gap-1">
      <Tooltip>
        <TooltipTrigger asChild>
          <Button
            variant="ghost"
            size="icon"
            className="h-6 w-6"
            onClick={() => submit("CORRECT")}
          >
            <ThumbsUp className="h-3.5 w-3.5" />
          </Button>
        </TooltipTrigger>
        <TooltipContent>Correct</TooltipContent>
      </Tooltip>
      <Tooltip>
        <TooltipTrigger asChild>
          <Button
            variant="ghost"
            size="icon"
            className="h-6 w-6"
            onClick={() => submit("INCORRECT")}
          >
            <ThumbsDown className="h-3.5 w-3.5" />
          </Button>
        </TooltipTrigger>
        <TooltipContent>Incorrect</TooltipContent>
      </Tooltip>
      <Tooltip>
        <TooltipTrigger asChild>
          <Button variant="ghost" size="icon" className="h-6 w-6" onClick={() => submit("IGNORED")}>
            <EyeOff className="h-3.5 w-3.5" />
          </Button>
        </TooltipTrigger>
        <TooltipContent>Ignore</TooltipContent>
      </Tooltip>
    </div>
  );
}
