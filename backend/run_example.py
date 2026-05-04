"""Simple local smoke test for the multi-agent pipeline."""

from __future__ import annotations

import json
import os
from pathlib import Path

from orchestrator.agent_controller import run_screening_pipeline
from orchestrator.schemas import PatientInput


def main() -> None:
    os.environ.setdefault("EXPLANATION_PROVIDER", "fallback")
    sample_path = Path(__file__).resolve().parent / "sample_patient.json"
    patient = PatientInput.model_validate_json(sample_path.read_text(encoding="utf-8"))
    result = run_screening_pipeline(patient, debug=True)
    print(json.dumps(result.model_dump(mode="json"), indent=2))


if __name__ == "__main__":
    main()
