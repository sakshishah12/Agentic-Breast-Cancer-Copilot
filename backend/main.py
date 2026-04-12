from fastapi import FastAPI
from pydantic import BaseModel
from agents.agent import run_agent

app = FastAPI()

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
