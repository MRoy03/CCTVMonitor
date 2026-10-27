export type FeedbackVerdict = "CORRECT" | "INCORRECT" | "IGNORED" | "MISSED_EVENT";

export interface Feedback {
  id: string;
  camera_id: string;
  detection_event_id: string | null;
  activity_event_id: string | null;
  verdict: FeedbackVerdict;
  prediction: Record<string, unknown>;
  actual_correction: Record<string, unknown> | null;
  notes: string | null;
  created_at: string;
}

export interface FeedbackStats {
  total: number;
  correct: number;
  incorrect: number;
  ignored: number;
  missed_event: number;
  accuracy: number | null;
}
