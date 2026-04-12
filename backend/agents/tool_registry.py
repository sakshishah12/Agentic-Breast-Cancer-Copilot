import json
from .tools import compute_risk, get_screening_guidelines, check_missing_data, flag_for_review

TOOLS = {
    "compute_risk": compute_risk,
    "get_screening_guidelines": get_screening_guidelines,
    "check_missing_data": check_missing_data,
    "flag_for_review": flag_for_review,
}

TOOL_DESCRIPTIONS = [
    {
        "name": "compute_risk",
        "description": "Compute cancer risk score from patient data",
        "parameters": ["patient"]
    },
    {
        "name": "get_screening_guidelines",
        "description": "Return recommended screenings based on patient data",
        "parameters": ["patient"]
    },
    {
        "name": "check_missing_data",
        "description": "Check for missing patient fields",
        "parameters": ["patient"]
    },
    {
        "name": "flag_for_review",
        "description": "Determine if case needs human review",
        "parameters": ["risk_score", "missing"]
    }
]