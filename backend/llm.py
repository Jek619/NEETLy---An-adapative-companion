import os
import json
from dotenv import load_dotenv
from groq import Groq

# Load .env (backup loading)
load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


# -----------------------------------------------------
# CHAT FUNCTION
# -----------------------------------------------------
def chat_llm(user_message: str):
    try:
        messages = [
            {
                "role": "system",
                "content": """
You are NEETly AI Tutor.

STRICT RESPONSE FORMAT RULES:
- Use clear headings like: Answer:, Explanation:
- Use bullet points where applicable
- Keep paragraphs short (max 2 lines)
- If explaining a concept, use steps
- If giving facts, use numbered points
- NO emojis
- NO markdown
- Plain text only, but well structured
"""
            },
            {
                "role": "user",
                "content": user_message
            }
        ]

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            temperature=0.4,   # lower = cleaner answers
            max_tokens=700
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print("GROQ CHAT ERROR:", e)
        raise e



# -----------------------------------------------------
# QUIZ GENERATOR (MCQs with explanation)
# -----------------------------------------------------
def generate_quiz_llm(subject, topic, difficulty):
    prompt = f"""
Generate a clean JSON array of **10 NEET-level MCQs**.
Subject: {subject}
Topic: {topic}
Difficulty: {difficulty}

Each MCQ must follow this EXACT JSON format:

{{
  "question": "string",
  "options": ["A", "B", "C", "D"],
  "answer": "Correct option text EXACTLY as in the options array",
  "explanation": "Short NEET-level explanation"
}}

Important rules:
- STRICTLY return ONLY valid JSON array.
- NO markdown.
- NO text before or after the JSON.
- Every question must be unique.
- Options must be full text, not letters.
- Answer MUST match one of the option strings exactly.
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
        )

        raw = response.choices[0].message.content.strip()
        print("RAW QUIZ OUTPUT:", raw)

        # Extract JSON only
        json_text = raw[raw.index("[") : raw.rindex("]") + 1]

        return json.loads(json_text)

    except Exception as e:
        print("GROQ QUIZ GENERATION ERROR:", e)
        return []
