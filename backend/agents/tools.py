import random
import os
import pickle
from models.feature_mapper import map_patient_to_features

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "..", "models", "risk_model.pkl")

def load_model():
    if not os.path.exists(MODEL_PATH):
        print("⚠️ Model not found. Training new model...")

        from models.train_model import train_model
        train_model()

    with open(MODEL_PATH, "rb") as f:
        return pickle.load(f)


model = load_model()


def compute_risk(patient):
    features = map_patient_to_features(patient)
    risk = model.predict_proba(features)[0][1]
    return float(risk)


def get_screening_guidelines(patient):
    recommendations = []

    if patient["age"] > 50:
        recommendations.append("Colonoscopy")

    if patient["smoker"] and patient["age"] > 40:
        recommendations.append("Low-dose CT scan (lung cancer)")

    if patient["gender"].lower() == "female" and patient["age"] > 40:
        recommendations.append("Mammogram")

    return recommendations


def check_missing_data(patient):
    missing = []
    for key, value in patient.items():
        if value is None or value == "":
            missing.append(key)
    return missing


def flag_for_review(risk_score, missing):
    if risk_score < 0.2 or len(missing) > 0:
        return True
    return False
