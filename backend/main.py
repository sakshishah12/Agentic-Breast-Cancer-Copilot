import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agents.agent import run_agent

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

class PatientData(BaseModel):
    age: int
    gender: str
    smoker: bool
    family_history: bool
    symptoms: list[str] = []

@app.get("/")
def home():
    return {"message": "Agentic Cancer Screening Copilot API"}

@app.post("/analyze")
def analyze(patient: PatientData):
    result = run_agent(patient.dict())
    return result
