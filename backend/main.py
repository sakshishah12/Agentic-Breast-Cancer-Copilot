from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agents.agent import run_agent

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
    ],
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
