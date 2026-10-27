"use client";

import { useState } from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { useSubmitFeedback } from "@/features/feedback/hooks";

export function MissedEventDialog({ cameraId }: { cameraId: string }) {
  const [open, setOpen] = useState(false);
  const [notes, setNotes] = useState("");
  const submitFeedback = useSubmitFeedback(cameraId);

  function handleSubmit() {
    submitFeedback.mutate(
      { verdict: "MISSED_EVENT", notes },
      {
        onSuccess: () => {
          toast.success("Missed event recorded");
          setOpen(false);
          setNotes("");
        },
        onError: (error) =>
          toast.error(error instanceof Error ? error.message : "Could not record this"),
      },
    );
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" size="sm">
          Flag missed event
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Flag something the system missed</DialogTitle>
        </DialogHeader>
        <div className="space-y-2">
          <Label htmlFor="missed-notes">What happened that wasn&apos;t detected?</Label>
          <Textarea
            id="missed-notes"
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="e.g. A person entered through the side gate around 2:15pm and wasn't flagged"
            autoFocus
          />
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={() => setOpen(false)}>
            Cancel
          </Button>
          <Button onClick={handleSubmit} disabled={!notes.trim() || submitFeedback.isPending}>
            Submit
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
