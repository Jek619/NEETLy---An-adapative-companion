from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os, json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# ✅ CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

class NoteRequest(BaseModel):
    subject: str
    topic: str

@app.post("/generate-notes")
def generate_notes(data: NoteRequest):
    return {
        "full": [
            f"{data.topic} is an important chapter in {data.subject}.",
            "This is a TEST response from backend."
        ],
        "key_points": ["Test point 1", "Test point 2"],
        "definitions": ["Test definition"],
        "pyqs": ["Test PYQ"],
        "revision": ["Test revision"]
    }
