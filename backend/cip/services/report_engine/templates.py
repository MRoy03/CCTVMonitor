import json

from cip.models.report import ReportType

REPORT_TYPE_INSTRUCTIONS = {
    ReportType.DAILY: "Write a concise daily monitoring summary for this camera.",
    ReportType.SHIFT: "Write a concise shift-handover summary for this camera.",
    ReportType.EXCEPTION: (
        "Write a report focused only on unusual or notable incidents in this period."
    ),
    ReportType.INCIDENT: "Write a focused incident report describing what happened and when.",
    ReportType.SUMMARY: "Write a brief overview summary of activity in this period.",
}

SYSTEM_PROMPT = (
    "You are a security operations assistant that writes clear, factual CCTV "
    "monitoring reports for non-technical staff. Only describe what is in the "
    "data provided — never invent events, counts, or times that aren't there. "
    "Keep it to 3-6 sentences."
)


def build_messages(report_type: ReportType, structured_data: dict) -> list[dict]:
    instruction = REPORT_TYPE_INSTRUCTIONS[report_type]
    user_content = (
        f"{instruction}\n\n"
        f"Camera: {structured_data['camera_name']}\n"
        f"Period: {structured_data['period_start']} to {structured_data['period_end']}\n\n"
        f"Distinct objects seen (by type): {json.dumps(structured_data['detection_summary'])}\n\n"
        f"Incidents/observations:\n{json.dumps(structured_data['rows'], indent=2)}"
    )
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]
