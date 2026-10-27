export type SourceType = "RTSP" | "UPLOAD" | "SCREEN_CAPTURE";
export type CameraStatus = "ONLINE" | "OFFLINE" | "PROCESSING" | "UNKNOWN";
export type VideoSessionStatus = "QUEUED" | "PROCESSING" | "DONE" | "FAILED";

export interface Location {
  id: string;
  organization_id: string;
  name: string;
  address: string | null;
}

export interface Camera {
  id: string;
  location_id: string;
  name: string;
  source_type: SourceType;
  stream_url: string | null;
  status: CameraStatus;
  last_seen_at: string | null;
  monitoring_profile_id: string | null;
}

export interface VideoSession {
  id: string;
  camera_id: string;
  status: VideoSessionStatus;
  start_time: string | null;
  end_time: string | null;
  error_message: string | null;
}

export interface BoundingBox {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
}

export interface DetectionEvent {
  id: string;
  timestamp: string;
  track_id: number | null;
  object_type: string;
  confidence: number;
  bounding_box: BoundingBox;
  zone: string | null;
}

export type Severity = "INFO" | "WARNING" | "CRITICAL";

export interface ActivityEvent {
  id: string;
  camera_id: string;
  zone_id: string | null;
  rule_id: string | null;
  track_id: number | null;
  start_time: string;
  end_time: string | null;
  event_type: string;
  severity: Severity;
  description: string;
}
