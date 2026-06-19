from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
import json
import time

load_dotenv()

MODEL_CANDIDATES = [
    "gemma-3-4b-it",
    "gemini-3.1-flash-lite",
    "gemini-2.5-flash-lite",
    "gemini-3.5-flash",
]

def call_model_with_fallback(prompt):
    last_error = None

    for model_name in MODEL_CANDIDATES:
        for attempt in range(3):
            try:
                client = ChatGoogleGenerativeAI(
                    model=model_name,
                    temperature=0.3,
                    max_retries=1
                )

                response = client.invoke(prompt)
                return response, model_name

            except Exception as e:
                last_error = e
                error_text = str(e).lower()

                if "429" in error_text or "resource exhausted" in error_text or "quota" in error_text:
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
                    continue
                else:
                    break

    raise Exception(f"All models failed. Last error: {last_error}")

def extract_text_from_response(response):
    content = response.content

    if isinstance(content, str):
        return content.strip()

    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                if "text" in item:
                    parts.append(item["text"])
            else:
                text = getattr(item, "text", None)
                if text:
                    parts.append(text)
        return "\n".join(parts).strip()

    return str(content).strip()

def analyze_resume(resume_text, user_goal):
    prompt = f"""
You are a strict hiring manager and software engineer.
Evaluate the resume based on the user's target role.

User goal: "{user_goal}"

Rules:
- Extract only relevant skills for this role.
- Ignore unrelated tools.
- Identify genuine missing skills.
- Create roadmap only for missing areas.
- Tailor output to the user's goal.

Return only valid JSON in this format:
{{
  "skills": [],
  "missing_skills": [],
  "roadmap": [],
  "interview_questions": []
}}

Resume:
{resume_text}
"""

    try:
        response, used_model = call_model_with_fallback(prompt)
        content = extract_text_from_response(response)

        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]

        result = json.loads(content.strip())
        result["model_used"] = used_model
        return result

    except Exception as e:
        return {
            "skills": [],
            "missing_skills": [],
            "roadmap": [],
            "interview_questions": [],
            "error": str(e)
        }