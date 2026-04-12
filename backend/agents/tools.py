import random
import pickle
from models.feature_mapper import map_patient_to_features

# Load model once
with open("models/risk_model.pkl", "rb") as f:
    model = pickle.load(f)


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