import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import google.generativeai as genai

# ---------- Config ----------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY not set")

genai.configure(api_key=GEMINI_API_KEY)
MODEL_NAME = "gemini-1.5-flash"

app = FastAPI()

# CORS so your frontend can call the API (same origin or others)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # you can restrict later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Static files ----------
# Assumes index.html, script.js, styles.css are in ./static/
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def serve_index():
    """Serve the main frontend page."""
    return FileResponse("static/index.html")


# ---------- API model ----------

@app.post("/api/ask")
async def ask_icse_question(payload: dict):
    """
    Expected JSON body:
    {
      "subject": "Math",
      "chapter": "Quadratic Equations",
      "question": "Solve x^2-5x+6=0"
    }
    """
    subject = (payload.get("subject") or "General").strip()
    chapter = (payload.get("chapter") or "General").strip()
    question = (payload.get("question") or "").strip()

    if not question:
        raise HTTPException(status_code=400, detail="Question is required")

    prompt = f"""
You are an expert ICSE Class 10 tutor.

Subject: {subject}
Chapter: {chapter}

Student Question:
\"\"\"{question}\"\"\"

Instructions:
- Explain step by step in simple language.
- Show working where relevant (math/physics/chemistry).
- Keep the style similar to ICSE board exam solutions.
- If important, mention common mistakes students make.
"""

    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt)
        answer = response.text or "I could not generate an answer."
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini error: {e}")

    return {"answer": answer}


# Optional simple health check
@app.get("/health")
async def health():
    return {"status": "ok"}
