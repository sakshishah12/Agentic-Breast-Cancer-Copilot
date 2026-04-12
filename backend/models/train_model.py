from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
import pickle
import os

# Load dataset
data = load_breast_cancer()
X = data.data
y = data.target

# Split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Train model
model = LogisticRegression(max_iter=5000)
model.fit(X_train, y_train)

# Create models folder if not exists
os.makedirs("models", exist_ok=True)

# Save model
with open("models/risk_model.pkl", "wb") as f:
    pickle.dump(model, f)

print("Model trained and saved as models/risk_model.pkl")

