from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from llm import chat_llm, generate_quiz_llm
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------
# LOAD TOPICS FROM LOCAL JSON FILES
# ---------------------------------------
def load_topics(subject: str):
    try:
        with open(f"{subject}.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        return list(data.keys())
    except:
        return []


# ---------------------------------------
# TOPICS API
# ---------------------------------------
@app.get("/topics/{subject}")
def get_topics(subject: str):
    subject = subject.lower()
    topics = load_topics(subject)
    return {"topics": topics}


# ---------------------------------------
# QUIZ GENERATOR API
# ---------------------------------------
@app.get("/quiz")
def generate_quiz(subject: str, topic: str, difficulty: str):
    try:
        questions = generate_quiz_llm(subject, topic, difficulty)
        return {"questions": questions}
    except Exception as e:
        return {"error": str(e), "questions": []}


# ---------------------------------------
# CHAT API
# ---------------------------------------
@app.post("/api/chat")
def chat(payload: dict):
    user_message = payload.get("message", "")
    history = payload.get("history", [])

    if not user_message:
        return {"reply": "Please type something."}

    messages = [{
    "role": "system",
    "content": """
    You are NEETly AI Tutor.
    Follow these rules strictly:
    - Use short paragraphs
    - Use bullet points where possible
    - Add headings like: Answer:, Explanation:
    - Avoid long continuous text
    - Separate steps clearly
    """
    }]


    for h in history[-10:]:
        messages.append({"role": h["role"], "content": h["text"]})

    messages.append({"role": "user", "content": user_message})

    try:
        reply = chat_llm(user_message)
        return {"reply": reply}
    except Exception as e:
        return {"reply": f"Groq error: {str(e)}"}


@app.get("/")
def home():
    return {"msg": "Groq backend running 🚀"}


