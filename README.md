# 🧬 Agentic Cancer Screening Copilot

An **agentic AI system** that assists in cancer screening decisions by combining machine learning, clinical heuristics, and LLM-based reasoning with a human-in-the-loop safety layer.

---

## 🚀 Live Demo

* https://cancer-copilot-web-5qpx.onrender.com/


---

## 🧠 Overview

This project simulates a **clinical decision-support system** for cancer screening.

Given patient data, the system:

* predicts risk using a trained ML model
* applies screening guidelines
* uses an LLM agent to reason and decide next steps
* flags uncertain cases for human review

> The focus is not just prediction, but **how AI systems make safe, explainable decisions in real-world workflows**.

---

## ⚙️ Architecture

```
Patient Input
      ↓
LLM Agent (Gemini)
      ↓
Tool Calls
 ├── Risk Model (ML)
 ├── Screening Guidelines
 ├── Missing Data Check
 └── Human Review Flag
      ↓
Final Decision + Explanation
```

---

## 🤖 Key Features

### 🔹 Agentic AI System

* LLM dynamically decides which tools to call
* Multi-step reasoning loop
* Structured JSON outputs

---

### 🔹 Machine Learning Integration

* Model trained on real clinical dataset (Breast Cancer - sklearn)
* Predicts probability of malignancy
* Used as a **signal**, not the final decision

---

### 🔹 Feature Mapping Layer

* Converts patient-level inputs → dataset feature space
* Uses statistical alignment (mean + variance)
* Ensures realistic model inputs

---

### 🔹 Human-in-the-Loop Safety

* Flags:

  * incomplete data
  * low confidence
* Prevents unsafe automation

---

### 🔹 Explainability (Agent Trace)

* Logs every step:

  * tool calls
  * intermediate outputs
  * final reasoning

---

## 📊 Example Output

```json
{
  "risk_score": 0.72,
  "recommendations": ["Low-dose CT scan"],
  "urgency": "medium",
  "needs_review": false,
  "explanation": "...",
  "agent_trace": [
    {
      "tool": "compute_risk",
      "output": 0.72
    }
  ]
}
```

---

## 🧱 Tech Stack

### Backend

* FastAPI
* Python
* Gemini (LLM agent)
* Scikit-learn (ML model)

### Frontend

* React (Vite)
* Tailwind CSS
* Pinterest-style masonry UI

### Deployment

* Vercel / Railway

---

## 🧪 Model Details

* Dataset: Breast Cancer Dataset (sklearn)
* Model: Logistic Regression
* Input: Tumor-level features
* Output: Probability of malignancy

> Patient inputs are mapped into feature space using a statistical transformation.

---

## 📁 Project Structure

```
project/
├── backend/
│   ├── main.py
│   ├── agents/
│   ├── models/
│   └── tools/
├── frontend/
├── api/            # Vercel serverless entry
├── requirements.txt
└── vercel.json
```

---

## ▶️ Running Locally

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

---

## 🌍 Deployment Notes

* Model is dynamically generated if not found
* LLM initialized lazily to support serverless environments
* Environment variable required:

```
GEMINI_API_KEY=your_key
```

---

## ⚠️ Disclaimer

This project is for **demonstration purposes only** and is not intended for clinical use.

---

## 💡 Key Takeaways

* ML is just one component of real-world AI systems
* Agent-based architectures enable flexible decision-making
* Safety and explainability are critical in healthcare AI

---

## 🙌 Inspiration

Inspired by modern AI-driven healthcare systems like those built by organizations such as Color Health.

---
