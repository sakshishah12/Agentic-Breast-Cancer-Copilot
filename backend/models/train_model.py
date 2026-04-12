import pickle
import os
from sklearn.datasets import load_breast_cancer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "risk_model.pkl")


def train_model():
    data = load_breast_cancer()
    X = data.data
    y = data.target

    X_train, _, y_train, _ = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = LogisticRegression(max_iter=5000)
    model.fit(X_train, y_train)

    os.makedirs(BASE_DIR, exist_ok=True)

    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)

    print(f"Model trained and saved as {MODEL_PATH}")
    return model


if __name__ == "__main__":
    train_model()

