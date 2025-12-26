# api/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
import os

# ---- config / env ----
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY not set")

ALLOWED_CLASSES = ["10"]
ALLOWED_SUBJECTS = ["Maths", "Physics"]
CHAPTERS = {
    "Maths": [
        "Commercial Mathematics",
        "Algebra",
        "Geometry",
        "Mensuration",
        "Trigonometry",
    ],
    "Physics": [
        "Force, Work, Power and Energy",
        "Light",
        "Sound",
        "Electricity and Magnetism",
        "Heat",
        "Modern Physics",
    ],
}

GEMINI_MODEL_NAME = "gemini-2.5-flash-lite"  # or model with free quota


def build_prompt(class_level: str, subject: str, chapter: str, question: str) -> str:
    system_part = f"""
You are an expert ICSE tutor for Classes 9 and 10.
Board: ICSE.
Subjects: Mathematics, Physics, Chemistry, Biology.

Rules:
1. Stay within ICSE syllabus for the given class, subject and chapter.
2. Explain like a Class 11 topper, simple and step-by-step.
3. For numericals, always show working and final answer.
4. For theory, keep 4–8 exam-focused lines unless student asks for more.
5. If question is outside ICSE 9–10, say so politely and redirect.
"""
    user_part = f"""
Class: {class_level}
Subject: {subject}
Chapter: {chapter}

Student's question:
{question}
"""
    return system_part.strip() + "\n\n" + user_part.strip()


client = genai.Client(api_key=GEMINI_API_KEY)

app = FastAPI(title="ICSE AI Tutor (Vercel)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AskRequest(BaseModel):
    class_level: str
    subject: str
    chapter: str
    question: str


class AskResponse(BaseModel):
    answer: str
    meta: dict


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/ask", response_model=AskResponse)
async def ask_icse_ai(payload: AskRequest):
    if payload.class_level not in ALLOWED_CLASSES:
        raise HTTPException(400, "Only Class 10 supported in v1.")
    if payload.subject not in ALLOWED_SUBJECTS:
        raise HTTPException(400, "Subject not supported in v1.")
    if payload.chapter not in CHAPTERS.get(payload.subject, []):
        raise HTTPException(400, "Chapter not supported for this subject.")
    if not payload.question.strip():
        raise HTTPException(400, "Question cannot be empty.")

    prompt = build_prompt(
        class_level=payload.class_level,
        subject=payload.subject,
        chapter=payload.chapter,
        question=payload.question,
    )

    try:
        resp = client.models.generate_content(
            model=GEMINI_MODEL_NAME,
            contents=prompt,
        )
        answer = (resp.text or "").strip()
        if not answer:
            raise HTTPException(500, "Empty response from Gemini.")
    except Exception as e:
        raise HTTPException(500, f"Gemini error: {str(e)}")

    return AskResponse(
        answer=answer,
        meta={
            "class_level": payload.class_level,
            "subject": payload.subject,
            "chapter": payload.chapter,
        },
    )
