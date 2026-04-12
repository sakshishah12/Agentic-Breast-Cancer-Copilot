import numpy as np
from sklearn.datasets import load_breast_cancer

# Load dataset stats
data = load_breast_cancer()
X = data.data

MEAN = X.mean(axis=0)
STD = X.std(axis=0)


def map_patient_to_features(patient):
    """
    Map patient data → realistic feature vector
    """

    features = MEAN.copy()

    # Normalize signals (0 → low risk, 1 → high risk)
    age_factor = min(patient["age"] / 100, 1.0)
    smoker_factor = int(patient["smoker"])
    family_factor = int(patient["family_history"])
    symptom_factor = min(len(patient["symptoms"]) / 5, 1.0)

    risk_signal = (
        0.4 * age_factor +
        0.3 * smoker_factor +
        0.2 * family_factor +
        0.1 * symptom_factor
    )

    # Apply shift across important feature indices
    important_indices = list(range(10))  # top features

    for i in important_indices:
        features[i] = MEAN[i] + risk_signal * STD[i]

    return features.reshape(1, -1)