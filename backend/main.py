import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from orchestrator.agent_controller import run_screening_pipeline
from orchestrator.schemas import PatientInput, PredictionResponse

app = FastAPI()


def get_allowed_origins():
    frontend_url = os.getenv("FRONTEND_URL", "").strip()
    configured = os.getenv("CORS_ORIGINS", "").strip()

    origins = {
        "http://127.0.0.1:5173",
        "http://localhost:5173",
    }

    if frontend_url:
        origins.add(frontend_url.rstrip("/"))

    if configured:
        origins.update(origin.strip().rstrip("/") for origin in configured.split(",") if origin.strip())

    return sorted(origins)


app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "Agentic Cancer Screening Copilot API", "version": "multi-agent"}


@app.post("/predict", response_model=PredictionResponse)
def predict(patient: PatientInput, debug: bool = False, prompt_version: str | None = None):
    try:
        return run_screening_pipeline(patient, debug=debug, prompt_version=prompt_version)
    except Exception as exc:  # pragma: no cover - FastAPI boundary handling
        raise HTTPException(status_code=500, detail=f"Prediction pipeline failed: {exc}") from exc


@app.post("/analyze", response_model=PredictionResponse)
def analyze(patient: PatientInput, debug: bool = False, prompt_version: str | None = None):
    return predict(patient, debug=debug, prompt_version=prompt_version)
