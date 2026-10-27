"""Exports collected Feedback as JSONL — one labeled example per row, joining
the snapshot prediction with the user's correction. This is the dataset Phase
9's custom training works from; no retraining happens here (per the plan's
"supervised learning first, no RLHF" instruction — this script is purely
collection/export, not training).

Run with: python -m scripts.export_feedback_dataset [output_path]
"""

import json
import sys

from cip.db.session import SessionLocal
from cip.models.feedback import Feedback

DEFAULT_OUTPUT = "feedback_dataset.jsonl"


def main() -> None:
    output_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_OUTPUT

    db = SessionLocal()
    try:
        rows = db.query(Feedback).order_by(Feedback.created_at).all()
        with open(output_path, "w", encoding="utf-8") as f:
            for row in rows:
                record = {
                    "id": str(row.id),
                    "camera_id": str(row.camera_id),
                    "verdict": row.verdict.value,
                    "prediction": row.prediction,
                    "actual_correction": row.actual_correction,
                    "notes": row.notes,
                    "created_at": row.created_at.isoformat(),
                }
                f.write(json.dumps(record) + "\n")
        print(f"Exported {len(rows)} feedback records to {output_path}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
