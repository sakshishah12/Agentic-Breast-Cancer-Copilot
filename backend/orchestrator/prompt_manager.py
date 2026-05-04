"""Prompt loading and A/B selection utilities."""

from __future__ import annotations

import random
from pathlib import Path

from orchestrator.schemas import GuidelineDecision, PatientInput, RiskAssessment


PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"


class PromptManager:
    """Load prompt templates from disk and choose a version for a run."""

    def __init__(self, prompts_dir: Path | None = None) -> None:
        self.prompts_dir = prompts_dir or PROMPTS_DIR
        self.prompt_paths = sorted(self.prompts_dir.glob("prompt_*.txt"))
        if not self.prompt_paths:
            raise FileNotFoundError(f"No prompt templates found in {self.prompts_dir}")

    def list_versions(self) -> list[str]:
        return [path.stem for path in self.prompt_paths]

    def select_version(self, requested_version: str | None = None) -> str:
        if requested_version:
            prompt_path = self.prompts_dir / f"{requested_version}.txt"
            if not prompt_path.exists():
                raise ValueError(f"Prompt version '{requested_version}' does not exist")
            return requested_version
        return random.choice(self.list_versions())

    def render(
        self,
        *,
        patient: PatientInput,
        risk: RiskAssessment,
        guideline: GuidelineDecision,
        prompt_version: str | None = None,
    ) -> tuple[str, str]:
        version = self.select_version(prompt_version)
        template = (self.prompts_dir / f"{version}.txt").read_text(encoding="utf-8")
        rendered = template.format(
            patient_json=patient.model_dump_json(indent=2),
            risk_json=risk.model_dump_json(indent=2),
            guideline_json=guideline.model_dump_json(indent=2),
        )
        return version, rendered
