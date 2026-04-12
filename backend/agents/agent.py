
import re
import google.generativeai as genai
import json
from .tool_registry import TOOLS, TOOL_DESCRIPTIONS
from .prompts import SYSTEM_PROMPT
import os 

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel(GEMINI_MODEL)  


def run_agent(patient):
    trace = []

    messages = [
        {"role": "user", "parts": [f"Patient data: {json.dumps(patient)}"]}
    ]

    for _ in range(5):  # max steps
        response = model.generate_content(
            contents=[SYSTEM_PROMPT] + [m["parts"][0] for m in messages]
        )

        
        raw_text = response.text.strip()# Extract JSON inside ```json ... ```
        match = re.search(r"\{.*\}", raw_text, re.DOTALL)

        if match:
            try:
                action_json = json.loads(match.group(0))
            except json.JSONDecodeError:
                return {"error": "JSON parsing failed", "raw": raw_text}
        else:
            return {"error": "No valid JSON found", "raw": raw_text}

        action = action_json.get("action")

        # FINAL OUTPUT
        if action == "final":
            output = action_json["output"]
            output["agent_trace"] = trace
            return output

        # TOOL CALL
        if action in TOOLS:
            tool_fn = TOOLS[action]
            tool_input = action_json.get("input", {})

            result = tool_fn(**tool_input)

            trace.append({
                "tool": action,
                "input": tool_input,
                "output": result
            })

            messages.append({
                "role": "user",
                "parts": [f"Tool {action} returned: {result}"]
            })

        else:
            return {"error": "Unknown action", "raw": action_json}

    return {"error": "Max steps reached", "trace": trace}


